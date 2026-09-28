"""`vg audio`: the sound is made first and the reel is cut to it.

  voice  narration takes, one per voice, through OpenRouter text-to-speech (a few cents per take)
  music  music takes through OpenRouter Lyria (about $0.04 per 30 s clip)
  sfx    four sound effects synthesized locally with FFmpeg (whoosh, tap, ding, tick)
  curve  a track's loudness every half second, and where its drop is (to set `music.at`)

Everything lands in <project>/6_Edit/1_Audio/ with plain version numbers (_v1, _v2 ...); a take is never
overwritten. The key is OPENROUTER_API_KEY (or OPENROUTER) in .env; it is never printed.
"""
import array
import base64
import json
import math
import re
import subprocess
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from vglib import config
from vglib.errors import UsageError
from vglib.finish import _run
from vglib.generate import say

API = "https://openrouter.ai/api/v1"
VOICE_MODEL = "google/gemini-3.8-flash-lite-tts"
MUSIC_MODEL = "google/lyria-3-clip-preview"
VOICES = ("Callirrhoe", "Leda", "Laomedeia", "Aoede", "Zephyr", "Sulafat")

SFX = {  # name: (FFmpeg source, filter)
    "Whoosh": ("anoisesrc=d=0.55:c=pink:a=0.9:r=48000",
               "highpass=f=350,lowpass=f=6500,volume='pow(sin(PI*t/0.55),3)':eval=frame,"
               "equalizer=f=1800:t=q:w=1:g=6"),
    "Tap": ("aevalsrc='0.9*sin(2*PI*(150+90*exp(-60*t))*t)*exp(-40*t)+0.18*(random(0)*2-1)*exp(-260*t)'"
            ":s=48000:d=0.2", "lowpass=f=2800"),
    "Ding": ("aevalsrc='0.5*(sin(2*PI*1046.5*t)+0.5*sin(2*PI*1568*t)+0.2*sin(2*PI*2093*t))*exp(-2.6*t)"
             "*min(1,t*200)':s=48000:d=1.6", "lowpass=f=4500,aecho=0.7:0.5:70:0.2"),
    "Tick": ("aevalsrc='0.45*sin(2*PI*2600*t)*exp(-260*mod(t,0.075))':s=48000:d=1.1", "highpass=f=1200"),
}


def key():
    for name in ("OPENROUTER_API_KEY", "OPENROUTER"):
        value = config.setting(name)
        if value and not value.startswith(("your-", "<")):
            return value
    raise UsageError("OPENROUTER_API_KEY is not set. Make a key at https://openrouter.ai/keys, then open .env "
                     "in the workspace root and set OPENROUTER_API_KEY=<your key>.")


def post(path, body, api_key, stream=False):
    """One OpenRouter call. Returns (bytes, content type), or (list of lines, content type) when streamed."""
    request = urllib.request.Request(API + path, data=json.dumps(body).encode("utf-8"), headers={
        "Authorization": "Bearer " + api_key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            ctype = response.headers.get("Content-Type", "")
            return (list(response) if stream else response.read()), ctype
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise UsageError("OpenRouter refused %s (HTTP %d): %s" % (path, exc.code, detail))
    except urllib.error.URLError as exc:
        raise UsageError("Could not reach OpenRouter: %s" % exc.reason)


def folder(project):
    path = project.path / "6_Edit" / "1_Audio"
    path.mkdir(parents=True, exist_ok=True)
    return path


def next_paths(directory, stem, ext, count=1):
    """`count` new files <stem>_v<N><ext>, numbered after the highest version already there."""
    taken = [int(m.group(1)) for p in directory.glob("%s_v*%s" % (stem, ext))
             for m in [re.match(re.escape(stem) + r"_v(\d+)" + re.escape(ext) + "$", p.name)] if m]
    start = max(taken, default=0) + 1
    return [directory / ("%s_v%d%s" % (stem, n, ext)) for n in range(start, start + count)]


def voice(project, text, voices, style, name="Narration", model=VOICE_MODEL):
    """One narration take per voice. `style` is the direction (who speaks, to whom, pace, mood); the
    text is read as written, so write numbers and names the way they should sound."""
    if not text.strip():
        raise UsageError("The narration text is empty")
    api_key = key()
    directory = folder(project)
    paths = [next_paths(directory, "%s_Take_%s" % (name, v), ".wav")[0] for v in voices]

    def one(item):
        name_, path = item
        body = {"model": model, "input": text, "voice": name_, "response_format": "pcm",
                "provider": {"options": {"google-ai-studio": {"speech_metadata": {"style": style}}}}}
        data, ctype = post("/audio/speech", body, api_key)
        rate = re.search(r"rate=(\d+)", ctype or "")
        channels = re.search(r"channels=(\d+)", ctype or "")
        raw = path.with_suffix(".pcm")
        raw.write_bytes(data)
        try:
            _run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", rate.group(1) if rate else "24000",
                  "-ac", channels.group(1) if channels else "1", "-i", str(raw), str(path)])
        finally:
            raw.unlink()
        return path

    with ThreadPoolExecutor(max(1, min(6, len(paths)))) as pool:
        done = list(pool.map(one, zip(voices, paths)))
    for path in done:
        say("voice  %s" % project.rel(path))
    return done


def stream_audio(lines):
    """The audio bytes from a streamed chat completion (base64 pieces in choices[].delta.audio.data)."""
    pieces = []
    for raw in lines:
        line = raw.decode("utf-8", "replace").strip() if isinstance(raw, bytes) else raw.strip()
        if not line.startswith("data:") or line == "data: [DONE]":
            continue
        event = json.loads(line[len("data:"):])
        for choice in event.get("choices", []):
            data = ((choice.get("delta") or {}).get("audio") or {}).get("data")
            if data:
                pieces.append(data)
    return base64.b64decode("".join(pieces))


def music(project, prompt, label, takes=1, model=MUSIC_MODEL):
    """`takes` music takes from one prompt. Describe the structure with times (quiet under the voice,
    a build, half a beat of silence, the drop), then check each take with `curve`."""
    if not prompt.strip():
        raise UsageError("The music prompt is empty")
    if not re.match(r"^[A-Za-z0-9_]+$", label):
        raise UsageError("--label must be letters, digits and underscores, e.g. Quiz_Pop")
    api_key = key()
    paths = next_paths(folder(project), "Music_Take_%s" % label, ".mp3", takes)

    def one(path):
        body = {"model": model, "stream": True, "modalities": ["audio"], "audio": {"format": "mp3"},
                "messages": [{"role": "user", "content": prompt}]}
        lines, _ = post("/chat/completions", body, api_key, stream=True)
        data = stream_audio(lines)
        if not data:
            raise UsageError("OpenRouter returned no audio for %s" % path.name)
        path.write_bytes(data)
        return path

    with ThreadPoolExecutor(max(1, min(3, len(paths)))) as pool:
        done = list(pool.map(one, paths))
    for path in done:
        say("music  %s" % project.rel(path))
    return done


def sfx(project):
    """Whoosh (under a whip cut), Tap (a title or callout appears), Ding (the reveal), Tick (a counter)."""
    directory = folder(project)
    done = []
    for name, (source, chain) in SFX.items():
        path = next_paths(directory, "Sfx_" + name, ".wav")[0]
        _run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", source, "-af",
              chain + ",aformat=channel_layouts=stereo", str(path)])
        say("sfx    %s" % project.rel(path))
        done.append(path)
    return done


def curve(path, step=0.5):
    """[(seconds, loudness in dB)] every `step` seconds."""
    raw = _run_bytes(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "8000", "-f", "s16le", "-"])
    samples = array.array("h")
    samples.frombytes(raw[:len(raw) // 2 * 2])
    size = max(1, int(8000 * step))
    out = []
    for i in range(0, len(samples) - size + 1, size):
        chunk = samples[i:i + size]
        rms = math.sqrt(sum(x * x for x in chunk) / size)
        out.append((round(i / 8000.0, 3), max(-90.0, 20 * math.log10(rms / 32768.0)) if rms else -90.0))
    return out


def find_drop(points, hold=2.0, before=1.0, min_rise=12.0):
    """Where the music drops: of the points where the `hold` seconds after are at least `min_rise` dB
    louder than the `before` seconds ahead, the one with the loudest stretch after it (the hook).
    A final hit after the ending's silence has no loud stretch after it, a gap between beats has loud
    music before it, and a quiet section after a break is not the loudest, so none of them count."""
    if len(points) < 2:
        return None
    step = points[1][0] - points[0][0]
    ahead, behind = max(1, int(round(hold / step))), max(1, int(round(before / step)))
    scored = []
    for i in range(1, len(points) - ahead + 1):
        after = sum(p[1] for p in points[i:i + ahead]) / ahead
        prior = points[max(0, i - behind):i]
        scored.append((after, after - sum(p[1] for p in prior) / len(prior), points[i][0]))
    if not scored:
        return None
    eligible = [s for s in scored if s[1] >= min_rise]
    if not eligible:
        return max(scored, key=lambda s: s[1])[2]
    loudest = max(eligible)
    # the hook keeps building for a moment: step back to where it starts
    onset = [s for s in eligible if loudest[2] - before <= s[2] <= loudest[2] and s[0] >= loudest[0] - 3.0]
    return min(onset, key=lambda s: s[2])[2]


def _run_bytes(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    if result.returncode != 0:
        raise UsageError("%s failed: %s" % (cmd[0], result.stderr.decode("utf-8", "replace").strip()[-200:]))
    return result.stdout
