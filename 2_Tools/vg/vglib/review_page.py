"""The local review page for the visual review gate (`vg review`). Design:
4_Docs/Specs/2026-09-28_Visual_Review_Page_Design_v1.0.md

The page adds no gate logic: it shows what vglib.review reports, calls its approve functions, and
records the human's notes and take choices through the tool. It never generates or pays for anything.
"""
import json
import mimetypes
import secrets
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from vglib import config, review
from vglib.errors import Refused, UsageError, VgError
from vglib.generate import load, say
from vglib.project import now_iso

NOTES = "review_notes"
TAKE_KINDS = ("look", "asset", "storyboard", "first", "last")
MAX_NOTE = 2000
MAX_BODY = 64 * 1024
DRAIN_LIMIT = 1024 * 1024  # an oversized body is read and dropped up to this, so the client sees the 413


def approval_mode():
    return (config.setting("VG_APPROVAL_MODE") or "terminal").lower()


def _rel(project, path):
    """Project-relative path for a file inside the project. The ledger can hold absolute paths when
    the project folder is reached through a symlink (macOS /var -> /private/var)."""
    path = Path(path)
    full = path if path.is_absolute() else project.path / path
    try:
        return str(full.resolve().relative_to(project.path.resolve()))
    except ValueError:
        return str(path)


def _take(project, state, target, label):
    entry = state["outputs"].get(target) or {"versions": [], "selected": None}
    versions = [{"v": v["v"], "path": _rel(project, v["path"])} for v in entry["versions"]
                if (project.path / v["path"]).is_file()]
    return {"target": target, "label": label, "selected": entry.get("selected"), "versions": versions}


def page_data(project, gates=True):
    """Everything the page shows, read fresh from Shotlist.json, project.json and the disk.
    gates=False skips the gate checks and the reel hashing (serving a file only needs the file list)."""
    sl = load(project, allow_errors=True)
    state = project.read_state()
    look = sl.look()
    frames = [dict(_take(project, state, "look:" + f["id"], f["id"]), item="look:" + f["id"],
                   prompt=f.get("prompt", "")) for f in sl.look_frames()]
    refs = [dict(_take(project, state, "asset:" + aid, aid), item="asset:" + aid, prompt=a.get("prompt", ""))
            for aid, a in sl.assets.items() if aid]
    by_shot = {}
    for label, target in review.shot_frames(sl):
        by_shot.setdefault(target.split(":", 1)[1], []).append(_take(project, state, target, label))
    try:
        spec, edit_error = review.edit_spec(project), None
    except UsageError as exc:  # like the board: report a broken edit plan and show the shot list
        spec, edit_error = None, str(exc)
    reel = [{"item": "beat:" + b["id"], "id": b["id"], "text": b["text"],
             "image": _rel(project, b["image"]) if b["image"] is not None else None,
             "placeholder": b["placeholder"], "frames": by_shot.get(b["shot"], [])}
            for b in review.reel_beats(project, sl, state, spec)]
    visuals_seen = None
    if gates:
        try:
            visuals_seen = review.snapshot(review.visual_items(project, sl, state))
        except UsageError:
            pass
    animatic = None
    latest = (state.get("animatics") or [None])[-1]
    if latest and (project.path / latest["path"]).is_file():
        animatic = {"path": _rel(project, latest["path"]), "at": latest["at"],
                    "current": visuals_seen is not None and latest.get("snapshot") == visuals_seen}
    return {
        "project": project.name,
        "mode": approval_mode(),
        "gates": [{"name": n, "ok": ok, "text": t} for n, ok, t in review.gate_status(project, sl, state)]
                 if gates else [],
        "look": {"text": {k: look.get(k, "") for k in review.LOOK_TEXT}, "frames": frames},
        "refs": refs,
        "reel": reel,
        "edit_error": edit_error,
        "animatic": animatic,
        "notes": state.get(NOTES, {}),
        "commands": {"look": review._command(project, "look"), "visuals": review._command(project, "visuals")},
        # sent back with Approve: the approval must cover exactly what this page showed
        "seen": {"look": review.snapshot(review.look_items(project, sl, state)), "visuals": visuals_seen,
                 "animatic": review.animatic_mark(latest) if animatic else None} if gates else None,
    }


def allowed_files(data):
    """The only files the server may send: images and the animatic that are on the page."""
    paths = set()
    for card in data["look"]["frames"] + data["refs"]:
        paths.update(v["path"] for v in card["versions"])
    for beat in data["reel"]:
        if beat["image"]:
            paths.add(beat["image"])
        for take in beat["frames"]:
            paths.update(v["path"] for v in take["versions"])
    if data["animatic"]:
        paths.add(data["animatic"]["path"])
    return paths


def page_items(data):
    """Everything a note can be attached to."""
    return {card["item"] for card in data["look"]["frames"] + data["refs"] + data["reel"]}


# ---------------------------------------------------------------------- actions

def set_note(project, item, note):
    """Save the human's change note for one card (an empty note removes it)."""
    if item not in page_items(page_data(project)):
        raise UsageError("%s is not on the review page" % item)
    note = str(note or "").strip()[:MAX_NOTE]
    with project.transaction() as st:
        notes = st.setdefault(NOTES, {})
        if note:
            notes[item] = {"note": note, "at": now_iso()}
        else:
            notes.pop(item, None)


def select_take(project, target, version):
    """Same as `vg select`: which version later steps use. The gate's snapshots make any approval
    that included the old take stale."""
    if str(target).split(":", 1)[0] not in TAKE_KINDS:
        raise UsageError("Takes can be switched only for look, asset, storyboard, first and last images")
    try:
        version = int(version)
    except (TypeError, ValueError):
        raise UsageError("version must be a number")
    with project.transaction() as st:
        entry = st["outputs"].get(target)
        if not entry or version not in [v["v"] for v in entry["versions"]]:
            raise UsageError("%s has no version %s" % (target, version))
        entry["selected"] = version


def approve(project, stage, seen):
    """The human clicked Approve on what the page showed (`seen`, from page_data). Chat mode records it
    through the gate, which refuses if anything changed since; terminal mode refuses with the command
    to run in their own terminal, because a click cannot prove a human typed the code."""
    if stage not in ("look", "visuals"):
        raise UsageError("stage must be look or visuals")
    if not isinstance(seen, dict) or not isinstance(seen.get(stage), str):
        raise UsageError("Approve needs what the page showed; refresh the page and try again")
    if approval_mode() != "chat":
        raise Refused("VG_APPROVAL_MODE=%s: approve in your own terminal, where you type the code it shows:\n  %s"
                      % (approval_mode(), review._command(project, stage)))
    if stage == "look":
        review.approve_look(project, expected=seen["look"])
    else:
        review.approve_visuals(project, expected=seen["visuals"], expected_animatic=seen.get("animatic"))
    covered = ("look:",) if stage == "look" else ("beat:", "asset:")
    with project.transaction() as st:
        notes = st.setdefault(NOTES, {})
        for key in [k for k in notes if k.startswith(covered)]:
            del notes[key]


def summary(project):
    """What the agent reads after the human clicks Done."""
    data = page_data(project)
    lines = ["GATE  %s: %s" % (g["name"], g["text"]) for g in data["gates"]]
    for item, entry in sorted(data["notes"].items()):
        lines.append("NOTE  %s  %s" % (item, " / ".join(entry["note"].splitlines())))
    look_ok, visuals_ok = [g["ok"] for g in data["gates"]]
    terminal = data["mode"] != "chat"
    animatic_current = bool(data["animatic"] and data["animatic"]["current"])
    if data["notes"]:
        # the animatic belongs to the reel review; at the look stage there is none to re-render yet
        reel_notes = any(not item.startswith("look:") for item in data["notes"])
        step = "act on the notes (re-roll or re-prompt), %sthen vg review again" % (
            "render the animatic again (vg edit animatic), " if reel_notes else "")
    elif look_ok and visuals_ok:
        step = "both gates approved: write the video prompts, then the video gate"
    elif not look_ok:
        step = ("wait for the human to run the approve look command in their own terminal, then check vg status"
                if terminal else "look not approved and nothing noted: ask the human what to change, then vg review again")
    elif not animatic_current:
        step = ("look approved: continue with the reference sheets, storyboard and frames and the edit plan, "
                "render the animatic (vg edit animatic), then vg review again for the reel")
    else:
        step = ("wait for the human to run the approve visuals command in their own terminal, then check vg status"
                if terminal else "reel not approved and nothing noted: ask the human what to change, then vg review again")
    lines.append("NEXT  " + step)
    return lines


# ---------------------------------------------------------------------- server

class ReviewServer(ThreadingHTTPServer):
    """127.0.0.1 only; every request must carry the per-run token."""
    daemon_threads = True

    def __init__(self, project, port=0):
        self.project = project
        self.token = secrets.token_urlsafe(16)
        self.finished = threading.Event()
        super().__init__(("127.0.0.1", port), _Handler)

    @property
    def url(self):
        return "http://127.0.0.1:%d/?t=%s" % (self.server_address[1], self.token)


class _Handler(BaseHTTPRequestHandler):
    server_version = "vg-review"

    def log_message(self, format, *args):  # keep the agent's output to the summary
        pass

    def _send(self, status, body, content_type="application/json; charset=utf-8", headers=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        headers = dict(headers or {})
        self.send_header("Cache-Control", headers.pop("Cache-Control", "no-store"))
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status, message):
        self._send(status, {"ok": False, "error": message})

    def _authorized(self, query):
        given = self.headers.get("X-VG-Token") or (query.get("t") or [""])[0]
        return bool(given) and secrets.compare_digest(given, self.server.token)

    def _file(self, rel):
        project = self.server.project
        if not rel or rel not in allowed_files(page_data(project, gates=False)):
            return self._error(404, "not on the review page")
        root = project.path.resolve()
        path = (root / rel).resolve()
        if root not in path.parents or not path.is_file():
            return self._error(404, "not found")
        data = path.read_bytes()
        size = len(data)
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        extra = {"Accept-Ranges": "bytes", "Cache-Control": "private, max-age=86400"}  # versioned files never change
        wanted = self.headers.get("Range", "")
        if not wanted.startswith("bytes="):
            return self._send(200, data, ctype, extra)
        first, _, last = wanted[len("bytes="):].split(",")[0].strip().partition("-")
        try:
            if first:
                start, end = int(first), min(int(last), size - 1) if last else size - 1
            else:
                start, end = max(0, size - int(last)), size - 1  # suffix range: the last N bytes
        except ValueError:
            start, end = size, -1
        if start > end or start >= size:
            return self._send(416, b"", ctype, {"Content-Range": "bytes */%d" % size})
        extra["Content-Range"] = "bytes %d-%d/%d" % (start, end, size)
        return self._send(206, data[start:end + 1], ctype, extra)

    def do_GET(self):
        url = urllib.parse.urlsplit(self.path)
        query = urllib.parse.parse_qs(url.query)
        if not self._authorized(query):
            return self._error(403, "bad or missing token")
        try:
            if url.path == "/":
                return self._send(200, page_html(), "text/html; charset=utf-8")
            if url.path == "/api/state":
                return self._send(200, dict(page_data(self.server.project), ok=True))
            if url.path == "/file":
                return self._file((query.get("path") or [""])[0])
        except VgError as exc:
            return self._error(400, str(exc))
        return self._error(404, "not found")

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            remaining = min(length, DRAIN_LIMIT)
            while remaining > 0:
                chunk = self.rfile.read(min(remaining, 65536))
                if not chunk:
                    break
                remaining -= len(chunk)
            return self._error(413, "request too large")
        raw = self.rfile.read(length)
        if not self._authorized({}):  # API calls: header only
            return self._error(403, "bad or missing token")
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except ValueError:
            return self._error(400, "body must be JSON")
        if not isinstance(body, dict):
            return self._error(400, "body must be a JSON object")
        project, path = self.server.project, urllib.parse.urlsplit(self.path).path
        try:
            if path == "/api/note":
                set_note(project, body.get("item"), body.get("note"))
            elif path == "/api/select":
                select_take(project, body.get("target"), body.get("version"))
            elif path == "/api/approve":
                approve(project, body.get("stage"), body.get("seen"))
            elif path == "/api/done":
                notes = body.get("notes") or {}
                if not isinstance(notes, dict):
                    raise UsageError("notes must be an object of item -> note")
                pages = page_items(page_data(project, gates=False))
                unknown = [item for item in notes if item not in pages]
                if unknown:
                    raise UsageError("not on the review page: %s" % ", ".join(sorted(map(str, unknown))))
                for item, note in notes.items():
                    set_note(project, item, note)
                self._send(200, {"ok": True})
                self.server.finished.set()
                return None
            else:
                return self._error(404, "not found")
        except VgError as exc:
            return self._error(400, str(exc))
        return self._send(200, dict(page_data(project), ok=True))


def serve(project, port=0, open_browser=True, ready=None):
    """Run the page until the human clicks Done; return (and print) the summary for the agent."""
    if not allowed_files(page_data(project)):
        say("Nothing to review yet: generate the style frames first (vg image -p %s --stage look)." % project.name)
        return []
    server = ReviewServer(project, port)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        say("Review page: %s" % server.url)
        say("Waiting for the human to click 'Done, back to the agent' (Ctrl-C stops).")
        if ready:
            ready(server)
        if open_browser:
            webbrowser.open(server.url)
        server.finished.wait()
    finally:
        server.shutdown()
        server.server_close()
    lines = summary(project)
    for line in lines:
        say(line)
    return lines


def page_html():
    """The page shell; everything on it is rendered in the browser from /api/state."""
    return PAGE_HTML


PAGE_HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Visual Review</title>
<style>
:root{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--muted:#6b6a66;--line:#e2e0da;--ok:#15803d;--warn:#b45309;
--bad:#b91c1c;--accent:#1d4ed8;--chip:#f0eee9}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--card:#1d1d1b;--ink:#ecebe7;--muted:#9c9a94;--line:#2e2d2a;
--ok:#6ee7a0;--warn:#fbbf24;--bad:#fca5a5;--accent:#93b4ff;--chip:#262523}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 -apple-system,system-ui,sans-serif}
main{max-width:1280px;margin:0 auto;padding:20px 16px 80px}h1{font-size:24px;margin:0}h2{font-size:18px;margin:32px 0 10px}
.muted{color:var(--muted);font-size:13px}.gate{padding:8px 12px;border-radius:8px;border:1px solid var(--warn);color:var(--warn);margin:6px 0}
.gate.ok{border-color:var(--ok);color:var(--ok)}.err{display:none;padding:10px 12px;border:1px solid var(--bad);color:var(--bad);border-radius:8px;white-space:pre-wrap;margin:10px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px;display:flex;flex-direction:column;gap:8px}
.card img,.card video{width:100%;border-radius:8px;display:block;background:var(--chip)}
.ph{aspect-ratio:9/16;background:var(--chip);border-radius:8px;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:13px;text-align:center;padding:8px}
.takes{display:flex;gap:4px;flex-wrap:wrap;align-items:center}.takes button{padding:2px 8px;font-size:12px}
.takes button.on{border-color:var(--accent);color:var(--accent)}
button{font:inherit;padding:6px 12px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--ink);cursor:pointer}
button.primary{border-color:var(--accent);color:var(--accent)}
textarea{width:100%;font:inherit;font-size:13px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--ink);padding:6px}
.note-saved{color:var(--warn);font-size:12px}.frame img{max-width:120px}
dl{margin:0}dt{font-weight:600;font-size:13px}dd{margin:0 0 6px;color:var(--muted);font-size:13px}
code{display:block;white-space:pre-wrap;font-size:12px;background:var(--chip);padding:8px;border-radius:8px}
.bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:12px}
</style></head><body><main>
<h1 id="title">Visual review</h1><p class="muted" id="mode"></p><div id="gates"></div><div class="err" id="err"></div>
<div id="app"><p class="muted">Loading…</p></div>
<div class="bar"><button class="primary" id="done">Done, back to the agent</button><button id="refresh">Refresh</button></div>
</main>
<script>
const T = new URLSearchParams(location.search).get("t");
const $ = (tag, attrs, kids) => { const e = document.createElement(tag); Object.entries(attrs || {}).forEach(([k, v]) => {
  if (k === "text") e.textContent = v; else if (k === "on") e.addEventListener("click", v); else e.setAttribute(k, v); });
  (kids || []).forEach(k => k && e.appendChild(k)); return e; };
const file = p => "/file?t=" + encodeURIComponent(T) + "&path=" + encodeURIComponent(p);
let state = null;
async function api(path, body) {
  const opts = {headers: {"X-VG-Token": T}};
  if (body !== undefined) { opts.method = "POST"; opts.headers["Content-Type"] = "application/json"; opts.body = JSON.stringify(body); }
  const err = document.getElementById("err");
  let data;
  try { data = await (await fetch(path, opts)).json(); } catch (e) { data = {ok: false, error: "The review page server is not answering (did the command stop?)."}; }
  if (!data.ok) { err.textContent = data.error; err.style.display = "block"; return null; }
  err.style.display = "none"; if (data.gates) { state = data; render(); } return data;
}
function takeButtons(take) {
  return $("div", {class: "takes"}, [$("span", {class: "muted", text: "Take"})].concat(take.versions.map(v =>
    $("button", {class: v.v === take.selected ? "on" : "", text: "v" + v.v,
                 on: () => api("/api/select", {target: take.target, version: v.v})}))));
}
function picture(take) {
  const v = take.versions.find(x => x.v === take.selected);
  return v ? $("img", {src: file(v.path), alt: take.label, loading: "lazy"}) : $("div", {class: "ph", text: "not generated yet"});
}
const drafts = {};  // typed but not saved yet: kept across re-renders and sent with Done
function noteBox(item) {
  const saved = (state.notes[item] || {}).note || "";
  const box = $("textarea", {rows: "2", placeholder: "What should change? (empty = fine as is)"});
  box.value = item in drafts ? drafts[item] : saved;
  box.addEventListener("input", () => { drafts[item] = box.value; });
  return $("div", {}, [saved ? $("div", {class: "note-saved", text: "Your note is saved"}) : null,
    item in drafts && drafts[item] !== saved ? $("div", {class: "note-saved", text: "Not saved yet (Done saves it)"}) : null, box,
    $("button", {text: "Save note", on: async () => { if (await api("/api/note", {item: item, note: box.value})) { delete drafts[item]; render(); } }})]);
}
function approveBar(stage, label) {
  const gate = state.gates.find(g => g.name === stage);
  if (stage === "visuals" && !(state.animatic && state.animatic.current))
    return $("p", {class: "muted", text: "Approve reel appears once an animatic of exactly these images is here."});
  if (state.mode === "chat") return $("div", {class: "bar"}, [$("button", {class: "primary", text: label,
    on: () => api("/api/approve", {stage: stage, seen: state.seen})}), $("span", {class: "muted", text: gate && gate.ok ? "approved" : ""})]);
  return $("div", {}, [$("p", {class: "muted", text: "Approval mode is terminal: run this in your own terminal and type the code it shows, then Refresh."}),
    $("code", {text: state.commands[stage]})]);
}
function card(c) { return $("div", {class: "card"}, [$("b", {text: c.label}), picture(c), takeButtons(c), noteBox(c.item)]); }
function render() {
  document.getElementById("title").textContent = "Visual review: " + state.project;
  document.getElementById("mode").textContent = "Approval mode: " + state.mode;
  document.getElementById("gates").replaceChildren(...state.gates.map(g =>
    $("div", {class: "gate" + (g.ok ? " ok" : ""), text: g.name + " review: " + g.text})));
  const app = document.getElementById("app"); app.replaceChildren();
  const text = state.look.text;
  app.appendChild($("h2", {text: "Look"}));
  app.appendChild($("dl", {}, ["world", "light", "grade", "graphics"].flatMap(k => [$("dt", {text: k}), $("dd", {text: text[k] || "not written"})])));
  app.appendChild($("div", {class: "grid"}, state.look.frames.map(card)));
  if (state.look.frames.length) app.appendChild(approveBar("look", "Approve look"));
  if (state.refs.length) { app.appendChild($("h2", {text: "Reference sheets"})); app.appendChild($("div", {class: "grid"}, state.refs.map(card))); }
  app.appendChild($("h2", {text: "Reel"}));
  if (state.edit_error) app.appendChild($("div", {class: "gate", text: "Edit plan cannot be read: " + state.edit_error}));
  app.appendChild($("div", {class: "grid"}, state.reel.map(b => $("div", {class: "card"}, [
    $("b", {text: b.id}), $("span", {class: "muted", text: b.text || ""}),
    b.image ? $("img", {src: file(b.image), alt: b.id, loading: "lazy"}) : $("div", {class: "ph", text: b.placeholder}),
    ...b.frames.map(f => $("div", {class: "frame"}, [$("span", {class: "muted", text: f.label}), picture(f), takeButtons(f)])),
    noteBox(b.item)]))));
  const a = state.animatic;
  app.appendChild($("h2", {text: "Animatic"}));
  app.appendChild(a ? $("div", {class: "card", style: "max-width:320px"}, [
      $("video", {controls: "", preload: "metadata", playsinline: "", src: file(a.path)}),
      $("span", {class: a.current ? "muted" : "note-saved", text: a.current ? a.path : "Out of date: it shows older visuals. Ask the agent to render it again."})])
    : $("p", {class: "muted", text: "No animatic yet. The agent renders it with vg edit animatic before the reel review."}));
  app.appendChild(approveBar("visuals", "Approve reel"));
}
document.getElementById("refresh").addEventListener("click", () => api("/api/state"));
document.getElementById("done").addEventListener("click", async () => {
  const r = await api("/api/done", {notes: drafts});
  if (r) document.querySelector("main").replaceChildren($("h1", {text: "Done"}),
    $("p", {text: "The agent has your notes and approvals. You can close this tab."}));
});
api("/api/state");
</script></body></html>
"""
