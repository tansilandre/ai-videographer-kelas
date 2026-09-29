"""`vg setup`: a local page (127.0.0.1, one-time token) where the human pastes their API keys into .env.

Keys never pass through the chat or the agent: the page writes them straight into .env (mode 600), checks
the kie.ai key against the balance endpoint, and reports only which keys are set. It ends after one save.
The approval mode can be set to page or terminal here, never to chat (that one is typed into .env by hand).
"""
import hashlib
import json
import os
import re
import secrets
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from vglib import config
from vglib.errors import UsageError, VgError
from vglib.generate import say

KEYS = {"kie": "KIE_API_KEY", "openrouter": "OPENROUTER_API_KEY"}
MODES = ("page", "terminal")
KEY_SHAPE = re.compile(r"^[A-Za-z0-9._:-]{8,300}$")
MAX_BODY = 16 * 1024


def _balance():
    """The kie.ai balance with the key now in .env (raises VgError when the key does not work)."""
    from providers import get_provider
    return get_provider("kie").credits()


ALIASES = {"OPENROUTER_API_KEY": ("OPENROUTER",)}  # names `vg audio` also accepts


def _is_set(name):
    values = config.env_file_values()
    for key in (name,) + ALIASES.get(name, ()):
        value = values.get(key) or ""
        if value and not value.startswith(("your-", "<")):
            return True
    return False


def state():
    return {"keys": {name: _is_set(name) for name in KEYS.values()},
            "mode": (config.env_file_values().get("VG_APPROVAL_MODE") or "terminal").lower(),
            "env": str(config.ENV_FILE)}


def write_env(updates):
    """Set KEY=value lines in .env: replace an existing uncommented line, else append. Every other line,
    comment and blank stays as it was. The file ends up readable by its owner only."""
    path = config.ENV_FILE
    lines = path.read_text(encoding="utf-8-sig").splitlines() if path.is_file() else []
    todo = dict(updates)
    for i, line in enumerate(lines):
        bare = line.strip()
        if bare.startswith("export "):
            bare = bare[len("export "):]
        name = bare.split("=", 1)[0].strip() if "=" in bare and not bare.startswith("#") else None
        if name in todo:
            lines[i] = "%s=%s" % (name, todo.pop(name))
    lines += ["%s=%s" % (name, value) for name, value in todo.items()]
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as out:
        out.write("\n".join(lines) + "\n")
    os.chmod(str(path), 0o600)
    config._env_cache = None


def save(body):
    """Check what the human typed, write it, then test the kie.ai key. Returns what the page shows."""
    if not isinstance(body, dict):
        raise UsageError("body must be a JSON object")
    updates = {}
    for field, name in KEYS.items():
        value = str(body.get(field) or "").strip()
        if not value:
            continue
        if not KEY_SHAPE.match(value):
            raise UsageError("Kunci %s tidak terlihat seperti API key: salin lagi tanpa spasi." % name)
        updates[name] = value
    if "KIE_API_KEY" not in updates and not _is_set("KIE_API_KEY"):
        raise UsageError("Kunci kie.ai wajib diisi: tanpa itu tidak ada gambar dan video.")
    mode = str(body.get("mode") or "page").lower()
    if mode not in MODES:
        raise UsageError("Mode persetujuan hanya page atau terminal.")
    updates["VG_APPROVAL_MODE"] = mode
    write_env(updates)
    result = {"ok": True, "keys": state()["keys"], "mode": mode, "kie_balance": None, "kie_error": None}
    try:
        result["kie_balance"] = _balance()
    except VgError as exc:
        result["kie_error"] = str(exc).replace(updates.get("KIE_API_KEY", "\0"), "<key>")
    return result


# ---------------------------------------------------------------------- server

class SetupServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port=0):
        self.token = secrets.token_urlsafe(16)
        self.finished = threading.Event()
        self.result = None
        super().__init__(("127.0.0.1", port), _Handler)

    @property
    def url(self):
        return "http://127.0.0.1:%d/?t=%s" % (self.server_address[1], self.token)


class _Handler(BaseHTTPRequestHandler):
    server_version = "vg-setup"

    def log_message(self, format, *args):
        pass

    def _send(self, status, body, content_type="application/json; charset=utf-8"):
        data = (json.dumps(body, ensure_ascii=False) if isinstance(body, dict) else body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _authorized(self, token):
        return bool(token) and secrets.compare_digest(token, self.server.token)

    def do_GET(self):
        from urllib.parse import parse_qs, urlsplit
        url = urlsplit(self.path)
        token = self.headers.get("X-VG-Token") or (parse_qs(url.query).get("t") or [""])[0]
        if not self._authorized(token):
            return self._send(403, {"ok": False, "error": "bad or missing token"})
        if url.path == "/":
            return self._send(200, PAGE_HTML, "text/html; charset=utf-8")
        if url.path == "/api/state":
            return self._send(200, dict(state(), ok=True))
        return self._send(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            return self._send(413, {"ok": False, "error": "request too large"})
        raw = self.rfile.read(length)
        if not self._authorized(self.headers.get("X-VG-Token")):
            return self._send(403, {"ok": False, "error": "bad or missing token"})
        if self.path != "/api/save":
            return self._send(404, {"ok": False, "error": "not found"})
        try:
            result = save(json.loads(raw.decode("utf-8") or "{}"))
        except ValueError:
            return self._send(400, {"ok": False, "error": "body must be JSON"})
        except VgError as exc:
            return self._send(400, {"ok": False, "error": str(exc)})
        self.server.result = result
        self._send(200, result)
        self.server.finished.set()


def _summary(result):
    keys = result["keys"]
    lines = ["SAVED  KIE_API_KEY %s, OPENROUTER_API_KEY %s, VG_APPROVAL_MODE=%s"
             % ("set" if keys["KIE_API_KEY"] else "missing",
                "set" if keys["OPENROUTER_API_KEY"] else "not set (narration and music need it)", result["mode"])]
    if result["kie_balance"] is not None:
        lines.append("KIE    the key works: %g credits" % result["kie_balance"])
    else:
        lines.append("KIE    the key did not work: %s" % result["kie_error"])
    lines.append("NEXT   run `python3 2_Tools/vg/vg.py doctor`")
    return lines


def serve(port=0, open_browser=True):
    """Run the page until the human saves once; print (and return) what was saved, never the keys."""
    server = SetupServer(port)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        say("Setup page: %s" % server.url)
        say("Waiting for the human to paste their keys and click Simpan (Ctrl-C stops).")
        if open_browser:
            webbrowser.open(server.url)
        server.finished.wait()
    finally:
        server.shutdown()
        server.server_close()
    lines = _summary(server.result)
    for line in lines:
        say(line)
    return lines


# ---------------------------------------------------------------------- detached (agent apps)

def _pid_file():
    tag = hashlib.sha256(str(config.ROOT).encode("utf-8")).hexdigest()[:12]
    return os.path.join(tempfile.gettempdir(), "vg_setup_%s.json" % tag)


def detach(port=0, open_browser=True, timeout=20):
    """Start the page in its own process and return at once with its link."""
    import subprocess
    import sys
    import time
    from vglib.review_page import VG, _alive
    try:
        with open(_pid_file(), encoding="utf-8") as fh:
            info = json.load(fh)
        if _alive(info.get("pid")):
            say("Setup page already open: %s" % info["url"])
            return info["url"]
    except (OSError, ValueError):
        pass
    log = _pid_file().replace(".json", ".log")
    cmd = [sys.executable, str(VG), "setup", "--port", str(port)] + ([] if open_browser else ["--no-open"])
    with open(log, "w", encoding="utf-8") as out:
        proc = subprocess.Popen(cmd, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                cwd=str(config.ROOT), start_new_session=True)
    deadline, url = time.time() + timeout, None
    while time.time() < deadline and not url:
        with open(log, encoding="utf-8", errors="replace") as fh:
            found = re.search(r"Setup page: (http\S+)", fh.read())
        url = found.group(1) if found else None
        if not url:
            if proc.poll() is not None:
                break
            time.sleep(0.1)
    if not url:
        if proc.poll() is None:
            proc.kill()
        raise UsageError("The setup page did not start; see %s" % log)
    with open(_pid_file(), "w", encoding="utf-8") as fh:
        json.dump({"pid": proc.pid, "url": url}, fh)
    say("Setup page: %s" % url)
    say("Send the human this link: they paste their kie.ai key (and OpenRouter key) there and click Simpan. "
        "Never ask for keys in the chat. When they say it is done, run: python3 2_Tools/vg/vg.py doctor")
    return url


def stop_detached():
    import signal
    try:
        with open(_pid_file(), encoding="utf-8") as fh:
            info = json.load(fh)
    except (OSError, ValueError):
        say("No setup page is open.")
        return False
    from vglib.review_page import _alive
    if _alive(info.get("pid")):
        os.kill(int(info["pid"]), signal.SIGTERM)
    os.remove(_pid_file())
    say("Setup page stopped.")
    return True


PAGE_HTML = r"""<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Setup AI Videographer</title>
<style>
:root{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--muted:#6b6a66;--line:#e2e0da;--ok:#15803d;--bad:#b91c1c;--accent:#c2410c}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--card:#1d1d1b;--ink:#ecebe7;--muted:#9c9a94;--line:#2e2d2a;--ok:#6ee7a0;--bad:#fca5a5;--accent:#fb923c}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,system-ui,sans-serif}
main{max-width:560px;margin:0 auto;padding:28px 16px 60px}h1{font-size:24px;margin:0 0 4px}.muted{color:var(--muted);font-size:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:16px 0}
label{display:block;font-weight:600;margin:12px 0 4px}input,select{width:100%;font:inherit;padding:10px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--ink)}
button{font:inherit;font-weight:600;padding:12px 18px;border-radius:10px;border:0;background:var(--accent);color:#fff;cursor:pointer;width:100%;margin-top:16px}
.set{color:var(--ok);font-size:13px;font-weight:400}.err{color:var(--bad);white-space:pre-wrap}.ok{color:var(--ok)}
a{color:var(--accent)}
</style></head><body><main>
<h1>Setup AI Videographer</h1>
<p class="muted">Tempel kuncimu di sini, bukan di chat. Kunci disimpan hanya di file <code>.env</code> di komputermu.</p>
<div class="card" id="form">
<label for="kie">Kunci kie.ai <span class="set" id="kie_set"></span></label>
<input id="kie" type="password" autocomplete="off" placeholder="tempel kunci dari kie.ai/api-key">
<p class="muted">Untuk gambar dan video. Buat di <a href="https://kie.ai/api-key" target="_blank" rel="noopener">kie.ai/api-key</a>, beri batas kredit.</p>
<label for="openrouter">Kunci OpenRouter (opsional) <span class="set" id="openrouter_set"></span></label>
<input id="openrouter" type="password" autocomplete="off" placeholder="tempel kunci dari openrouter.ai/keys">
<p class="muted">Untuk narasi dan musik. Bisa diisi nanti.</p>
<label for="mode">Cara menyetujui</label>
<select id="mode"><option value="page">Klik di halaman review (disarankan)</option><option value="terminal">Ketik kode di Terminal</option></select>
<button id="save">Simpan</button>
<p class="err" id="err"></p>
</div>
<div class="card" id="done" style="display:none"></div>
</main><script>
const T = new URLSearchParams(location.search).get("t");
const $ = id => document.getElementById(id);
fetch("/api/state?t=" + encodeURIComponent(T)).then(r => r.json()).then(s => {
  if (!s.ok) return;
  if (s.keys.KIE_API_KEY) $("kie_set").textContent = "sudah tersimpan (kosongkan kalau tidak diganti)";
  if (s.keys.OPENROUTER_API_KEY) $("openrouter_set").textContent = "sudah tersimpan";
  if (s.mode === "terminal") $("mode").value = "terminal";
});
$("save").addEventListener("click", async () => {
  $("err").textContent = ""; $("save").disabled = true;
  let r;
  try {
    r = await (await fetch("/api/save", {method: "POST", headers: {"X-VG-Token": T, "Content-Type": "application/json"},
      body: JSON.stringify({kie: $("kie").value, openrouter: $("openrouter").value, mode: $("mode").value})})).json();
  } catch (e) { r = {ok: false, error: "Halaman ini sudah ditutup. Minta agent membukanya lagi."}; }
  $("save").disabled = false;
  if (!r.ok) { $("err").textContent = r.error; return; }
  $("kie").value = $("openrouter").value = "";
  $("form").style.display = "none";
  const d = $("done"); d.style.display = "block";
  d.innerHTML = r.kie_balance !== null
    ? "<h2 class='ok'>Tersimpan ✓</h2><p>Kunci kie.ai jalan: saldo " + r.kie_balance + " kredit.</p>"
    : "<h2>Tersimpan, tapi kunci kie.ai belum jalan</h2><p class='err'></p><p>Minta agent membuka halaman ini lagi dan tempel ulang kuncinya.</p>";
  if (r.kie_balance === null) d.querySelector(".err").textContent = r.kie_error;
  d.insertAdjacentHTML("beforeend", "<p>" + (r.keys.OPENROUTER_API_KEY ? "Kunci OpenRouter tersimpan." : "Kunci OpenRouter belum diisi: narasi dan musik menunggu.") +
    "</p><p><b>Kembali ke agent-mu (WorkBuddy atau Claude Code) dan bilang: sudah.</b> Halaman ini boleh ditutup.</p>");
});
</script></body></html>
"""
