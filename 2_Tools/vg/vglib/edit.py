"""Local editing with FFmpeg. The rough cut is for timing review, not the final edit."""
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from vglib.errors import UsageError
from vglib.generate import load, say

W, H, FPS = 1080, 1920, 30


def _run(cmd, timeout=600):
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
                                timeout=timeout)
    except subprocess.TimeoutExpired:
        raise UsageError("ffmpeg timed out after %ds: %s" % (timeout, " ".join(cmd[:6])))
    if result.returncode != 0:
        raise UsageError("ffmpeg failed: %s" % result.stderr.strip().splitlines()[-1:])
    return result.stdout


def _slot_seconds(time_label):
    match = re.match(r"\s*([\d.]+)\s*-\s*([\d.]+)", time_label or "")
    if not match:
        return 3.0
    return max(0.5, float(match.group(2)) - float(match.group(1)))


def _has_audio(path):
    out = _run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                "-of", "csv=p=0", str(path)])
    return bool(out.strip())


def roughcut(project):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise UsageError("ffmpeg and ffprobe are required (brew install ffmpeg)")
    sl = load(project, allow_errors=True)
    state = project.read_state()
    vf = ("scale=%d:%d:force_original_aspect_ratio=decrease,pad=%d:%d:(ow-iw)/2:(oh-ih)/2:color=black,"
          "fps=%d,format=yuv420p,setsar=1" % (W, H, W, H, FPS))
    pieces = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for index, shot in enumerate(sl.data.get("shots", [])):
            piece = tmp / ("%03d.mp4" % index)
            clip = project.selected("clip:" + shot["id"], state) if shot.get("source") == "ai" else None
            if clip:
                cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(clip)]
                if _has_audio(clip):
                    cmd += ["-map", "0:v:0", "-map", "0:a:0"]
                else:
                    cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v:0", "-map", "1:a:0",
                            "-shortest"]
                cmd += ["-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-c:a", "aac", "-ar", "48000", "-ac", "2", str(piece)]
                say("clip   %-6s %s" % (shot["id"], project.rel(clip)))
            else:
                seconds = _slot_seconds(shot.get("time"))
                color = {"real": "0x2f4f3a", "mg": "0x3d2f5a"}.get(shot.get("source"), "0x333333")
                panel = project.selected("storyboard:" + shot["id"], state)
                if panel:
                    cmd = ["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", "%.2f" % seconds, "-i", str(panel)]
                else:
                    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-t", "%.2f" % seconds,
                           "-i", "color=c=%s:s=%dx%d:r=%d" % (color, W, H, FPS)]
                cmd += ["-f", "lavfi", "-t", "%.2f" % seconds, "-i", "anullsrc=r=48000:cl=stereo",
                        "-map", "0:v:0", "-map", "1:a:0", "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "20", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest", str(piece)]
                say("gap    %-6s %.1fs %s" % (shot["id"], seconds,
                                              "(panel)" if panel else "(%s placeholder)" % shot.get("source")))
            _run(cmd)
            pieces.append(piece)
        if not pieces:
            raise UsageError("No shots to cut")
        listing = tmp / "list.txt"
        listing.write_text("".join("file '%s'\n" % Path(p).as_posix().replace("'", "'\\''") for p in pieces),
                           encoding="utf-8")
        out_dir = project.path / "6_Edit"
        out_dir.mkdir(exist_ok=True)
        stem = "Roughcut_%s" % (sl.data.get("project") or project.name)
        version = 1
        while (out_dir / ("%s_v%d.mp4" % (stem, version))).exists():
            version += 1
        out = out_dir / ("%s_v%d.mp4" % (stem, version))
        _run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
              "-c", "copy", "-movflags", "+faststart", str(out)])
    duration = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)])
    say("roughcut %s (%.1fs)" % (project.rel(out), float(duration.strip() or 0)))
    return out
