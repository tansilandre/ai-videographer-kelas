"""`vg edit final`: assemble the finished video from 6_Edit/Edit_Spec.json.

Local and free: FFmpeg for cutting and mixing, macOS `say` for a temporary voice-over, and the
Swift renderer (2_Tools/vg/render/overlay.swift) for animated captions and motion graphics.

Edit_Spec.json (agent-written; see 1_Skills/vg-edit/references/edit-spec.md):
  segments[]  in timeline order. One of:
                {"id", "clip": "<ShotId>", "in": 0, "out": 8 | "speech+0.4"}
                {"id", "card": "#0F1B2D", "duration": 4 | "vo+0.6"}
                {"id", "placeholder": "FOOTAGE ASLI\\n...", "duration": 2}
              optional "vo": {"text", "at": 0.2} (voice-over starting in this segment)
              optional "captions": false (skip captions for this segment's speech)
              clip only: "text" (the words captioned for this part of the clip, instead of the shot's
                dialogue), "cover": {"image", "blur", "dim", "zoom", "pan", "pan_x"} (show that
                image while the clip's sound plays: a cutaway), and "audio": "file:<voice track in
                clip time>" with "clip_volume": 0.15 (replace the clip's voice, keep some ambience)
              images ("still", background/cover "image") can be "file:0_Source/<photo>"; "pan_x":
                [from, to] slides across a wide photo instead of zooming
              optional "transition_in": "flash" (fades up from white) | "whip" (motion blur across
                the cut; pair it with a whoosh in sfx) | "cut" (default)
  narration   {"file": "file:6_Edit/1_Audio/<track>.wav", "text", "start": 0, "volume": 1.0}: one
              voice-over for the whole reel; captions follow its phrases, music and clips duck under it
  music       {"file": "file:0_Source/<track>", "volume": 0.22, "duck": 0.4, "start": 0, "fade_out": 1.5}
              "start" is the offset into the track, "at" the second of the reel where it comes in (land a
              drop on a reveal: at = reveal time - drop time in the track)
  sfx[]       {"file", "at": seconds (into "segment" when given, else into the reel), "volume": 0.8}
  graphics[]  {"segment": id, "type": title|pin|badge|counter|map|callouts|card_text|endcard,
               "at": seconds into the segment, "until": seconds or "end", ...layer fields}
  voice       {"voice": "Damayanti", "rate": 185}
  style       {"caption_y", "caption_size", "caption_chunk", "highlight", "fonts": {...}}
  output      file name inside 99_Output/
"""
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from vglib import config
from vglib.errors import UsageError
from vglib.generate import load, say

W, H, FPS = 1080, 1920, 30
RENDER_DIR = config.VG_DIR / "render"
# every piece of the timeline carries the same colour tags and no ICC profile: a change mid-stream (a
# client JPEG among AI clips) makes ffmpeg re-initialise the render's filters there and drop frames
UNIFORM = ("sidedata=mode=delete:type=ICC_PROFILE,"
           "setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709")


def _run(cmd, timeout=900, input_bytes=None):
    try:
        result = subprocess.run(cmd, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=timeout)
    except subprocess.TimeoutExpired:
        raise UsageError("timed out after %ds: %s" % (timeout, " ".join(map(str, cmd[:6]))))
    if result.returncode != 0:
        tail = result.stderr.decode("utf-8", "replace").strip().splitlines()[-3:]
        raise UsageError("%s failed: %s" % (cmd[0], " | ".join(tail)))
    return result.stdout.decode("utf-8", "replace") + result.stderr.decode("utf-8", "replace")


def _duration(path):
    out = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    return float(out.strip().splitlines()[0])


def check_frames(path, seconds):
    """Refuse a render that lacks frames for its length (a frozen stretch the eye can miss): the file
    is removed so it never reaches the human, and the error says so."""
    out = _run(["ffprobe", "-v", "error", "-select_streams", "v", "-count_frames", "-show_entries",
                "stream=nb_read_frames", "-of", "csv=p=0", str(path)])
    frames = int(out.strip().split(",")[0] or 0)
    expected = int(round(seconds * FPS))
    if frames < expected - 2:
        Path(path).unlink()
        raise UsageError("%s had %d frames for %.2fs (%d expected): a stretch of picture was dropped, so the file was "
                         "removed; render it again" % (Path(path).name, frames, seconds, expected))
    return frames


def _has_audio(path):
    out = _run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                "-of", "csv=p=0", str(path)])
    return bool(out.strip())


def speech_segments(path, min_silence=0.25):
    """Spoken intervals [(start, end), ...] from ffmpeg silencedetect. The threshold adapts to the
    clip: AI clips often carry room tone (car air-conditioning, wind) above -32 dB, which would make
    the whole clip look like speech, so stricter levels are tried until real pauses appear."""
    total = _duration(path)
    if not _has_audio(path):
        return []
    for noise in (-32, -28, -25, -22):
        log = _run(["ffmpeg", "-hide_banner", "-i", str(path), "-af",
                    "silencedetect=noise=%ddB:d=%s" % (noise, min_silence), "-f", "null", "-"])
        starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
        ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
        if not starts:
            continue
        silences = list(zip(starts, ends + [total] * (len(starts) - len(ends))))
        spoken, cursor = [], 0.0
        for a, b in silences:
            if a - cursor > 0.15:
                spoken.append((cursor, a))
            cursor = max(cursor, b)
        if total - cursor > 0.15:
            spoken.append((cursor, total))
        talk = sum(b - a for a, b in spoken)
        if spoken and talk < 0.95 * total:
            return spoken
    return [(0.0, total)]


def speech_span(path):
    """(start, end) of speech, or None when the file has no audio."""
    spoken = speech_segments(path)
    return (spoken[0][0], spoken[-1][1]) if spoken else None


def word_times(text, start, end, segments=None):
    """Words timed to speech. When the line's phrases (split after , . ? ! followed by a space) or
    its sentences match the number of spoken segments one to one, each phrase is placed in its own
    segment; otherwise words are spread over the spoken time so pauses get no words."""
    segments = [(max(a, start), min(b, end)) for a, b in (segments or []) if min(b, end) > max(a, start)]
    if len(segments) > 1:
        for pattern in (r"(?<=[.,?!])\s+", r"(?<=[.?!])\s+"):
            phrases = [p for p in re.split(pattern, text.strip()) if p]
            if len(phrases) == len(segments):
                out = []
                for phrase, (a, b) in zip(phrases, segments):
                    out += _spread(phrase, [(a, b)])
                return out
    return _spread(text, segments or [(start, end)])


def _spread(text, segments):
    """Words weighted by length over the spoken time of `segments`."""
    words = text.split()
    if not words:
        return []
    talk = sum(b - a for a, b in segments)
    weights = [len(w) + (3 if w[-1] in ".,?!" else 1) for w in words]
    total = float(sum(weights))

    def at(position):  # position in speech-time -> absolute time
        for a, b in segments:
            if position <= b - a:
                return a + position
            position -= b - a
        return segments[-1][1]

    out, pos = [], 0.0
    for w, wt in zip(words, weights):
        dur = talk * wt / total
        out.append({"text": w, "t0": round(at(pos), 3), "t1": round(at(pos + dur * 0.92), 3)})
        pos += dur
    return out


def narration_words(path, text, start=0.0, min_silence=0.25):
    """Caption words and spoken intervals for a narration track placed at `start` in the reel. Each
    phrase of `text` (split after . ? ! : and a space; a narrator runs through commas) lands in its own stretch of speech: a narrator
    also pauses inside phrases, so the shortest pauses are joined until there is one stretch per phrase."""
    spans = [(start + a, start + b) for a, b in speech_segments(path, min_silence)]
    if not spans:
        return [], []
    phrases = [p for p in re.split(r"(?<=[.?!:])\s+", text.strip()) if p]
    while len(spans) > max(1, len(phrases)):
        i = min(range(len(spans) - 1), key=lambda k: spans[k + 1][0] - spans[k][1])
        spans[i:i + 2] = [(spans[i][0], spans[i + 1][1])]
    if len(spans) == len(phrases):
        return [w for phrase, span in zip(phrases, spans) for w in _spread(phrase, [span])], spans
    return word_times(text, spans[0][0], spans[-1][1], spans), spans


TRANSITION_LEN = 0.2


def transition_filter(kind, side, dur):
    """The video filter for one side of a cut: `side` "in" is the head of the incoming piece, "out"
    the tail of the outgoing one; `dur` is that piece's length. flash: the incoming shot fades up from
    white. whip: a horizontal motion blur that peaks on the cut."""
    d = TRANSITION_LEN
    if kind == "flash":
        return "fade=t=in:st=0:d=%.3f:color=white" % d if side == "in" else None
    if kind == "whip":
        near = "lte(t,%.3f)" if side == "in" else "gte(t,%.3f)"
        edge = (lambda x: x) if side == "in" else (lambda x: dur - x)
        return ",".join("gblur=sigma=%d:sigmaV=0.6:enable='%s'" % (sigma, near % edge(window))
                        for sigma, window in ((14, d), (40, d / 2)))
    return None


def apply_transition(prev_piece, piece, kind, tmp):
    """Re-render the two pieces around a cut with the transition's filters (sound is copied)."""
    for side, path in (("out", prev_piece), ("in", piece)):
        vf = transition_filter(kind, side, _duration(path))
        if not vf:
            continue
        done = Path(tmp) / ("tx_%s" % Path(path).name)
        _run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vf", vf + ",format=yuv420p," + UNIFORM,
              "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "copy", str(done)])
        shutil.move(str(done), str(path))


def tts(text, voice, rate, dest):
    if not shutil.which("say"):
        raise UsageError("macOS `say` is needed for the temporary voice-over (or provide VO audio files)")
    aiff = dest.with_suffix(".aiff")
    _run(["say", "-v", voice, "-r", str(rate), "-o", str(aiff), text])
    _run(["ffmpeg", "-v", "error", "-y", "-i", str(aiff), "-ar", "48000", "-ac", "2", str(dest)])
    return dest


def reading_time(text, words_per_second=2.6):
    """How long an on-screen line needs when there is no voice to time it."""
    return max(1.2, len(text.split()) / words_per_second)


def _image(project, state, ref, sid):
    if ref.startswith("file:"):  # a client photo, e.g. file:0_Source/Facade.jpg
        root = project.path.resolve()
        image = (root / ref[len("file:"):]).resolve()
        if root not in image.parents or not image.is_file():
            raise UsageError("segment %s: %s is not a file inside the project" % (sid, ref))
        return image
    target = ref if ":" in ref else "storyboard:" + ref
    image = project.selected(target, state)
    if not image:
        raise UsageError("segment %s: %s is not generated yet" % (sid, target))
    return image


def _image_piece(image, dur, piece, zoom, pan, blur, dim, pan_x=None):
    """An image as a moving clip: zoom from zoom[0] to zoom[1], vertical drift `pan` (fraction of the
    frame), optional blur and darkening for backgrounds behind graphics. `pan_x` [from, to] instead
    slides a 9:16 window sideways across a wide photo (0 = left edge, 1 = right edge) at zoom[0]."""
    z0, z1 = zoom
    frames = int(round(dur * FPS))
    # photos are full range (yuvj420p); every piece must match the clips, or the final render
    # re-initialises its filters where the format changes and drops seconds of picture
    extra = ""
    if blur:
        extra += ",boxblur=%d:2" % int(blur)
    if dim:
        extra += ",eq=brightness=%.3f:saturation=0.9" % (-float(dim) * 0.5)
    rate = []
    if pan_x:
        x0, x1 = pan_x
        sw, sh = int(W * 2 * z0) // 2 * 2, int(H * 2 * z0) // 2 * 2
        rate = ["-framerate", str(FPS)]  # one input frame per output frame, so the slide is smooth
        video = ("[0:v]scale=%d:%d:force_original_aspect_ratio=increase,"
                 "crop=%d:%d:x='(iw-ow)*(%.4f+(%.4f)*n/%d)':y='(ih-oh)/2',scale=%d:%d%s,"
                 "scale=out_range=tv:out_color_matrix=bt709,format=yuv420p,setsar=1,%s[v]"
                 % (sw, sh, W * 2, H * 2, x0, x1 - x0, max(1, frames - 1), W, H, extra, UNIFORM))
    else:
        zexpr = "%.4f+(%.4f)*on/%d" % (z0, z1 - z0, max(1, frames - 1))
        yexpr = "ih/2-(ih/zoom/2)+(%.4f)*ih*on/%d" % (pan, max(1, frames - 1))
        video = ("[0:v]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,"
                 "zoompan=z='%s':x='iw/2-(iw/zoom/2)':y='max(0,min(ih-ih/zoom,%s))':d=%d:s=%dx%d:fps=%d%s,"
                 "scale=out_range=tv:out_color_matrix=bt709,format=yuv420p,setsar=1,%s[v]"
                 % (W * 2, H * 2, W * 2, H * 2, zexpr, yexpr, frames, W, H, FPS, extra, UNIFORM))
    _run(["ffmpeg", "-v", "error", "-y"] + rate + ["-loop", "1", "-i", str(image), "-f", "lavfi",
          "-t", "%.3f" % dur, "-i", "anullsrc=r=48000:cl=stereo", "-filter_complex", video,
          "-map", "[v]", "-map", "1:a:0", "-t", "%.3f" % dur, "-c:v", "libx264", "-preset", "veryfast",
          "-crf", "18", "-c:a", "aac", "-ar", "48000", "-ac", "2", str(piece)])


def grade_filter(project, state, grade):
    """The FFmpeg filter chain for the edit plan's `grade` (None when there is none): a LUT, then
    contrast/brightness/saturation/gamma, colour temperature, and grain, in that order."""
    if not grade:
        return None
    from vglib import review
    parts = []
    if grade.get("lut"):
        lut = review.resolve_image(project, state, grade["lut"])
        parts.append("lut3d=file='%s'" % str(lut).replace("\\", "/").replace("'", "\\'"))
    eq = ["%s=%g" % (k, grade[k]) for k in ("contrast", "brightness", "saturation", "gamma") if k in grade]
    if eq:
        parts.append("eq=" + ":".join(eq))
    if "temperature" in grade:
        parts.append("colortemperature=temperature=%g" % grade["temperature"])
    if grade.get("grain"):
        parts.append("noise=alls=%g:allf=t" % grade["grain"])
    return ",".join(parts) or None


def _image_opts(opts):
    """zoom/pan/pan_x from a `background` or `cover` block, with the background defaults."""
    return opts.get("zoom", [1.06, 1.16]), opts.get("pan", 0.04), opts.get("pan_x")


def renderer_binary():
    source = RENDER_DIR / "overlay.swift"
    binary = RENDER_DIR / ".build" / "overlay"
    if not binary.exists() or binary.stat().st_mtime < source.stat().st_mtime:
        if not shutil.which("swiftc"):
            raise UsageError("swiftc (Xcode command line tools) is needed to build the overlay renderer: "
                             "xcode-select --install")
        binary.parent.mkdir(exist_ok=True)
        say("build  overlay renderer (one time)")
        _run(["swiftc", "-O", str(source), "-o", str(binary)])
    return binary


def _srt_time(t):
    ms = int(round(t * 1000))
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


CHUNK_ENDS = ".,?!:\u2026"


def caption_chunks(words, chunk):
    """Words grouped the way captions show them: at most `chunk` words, and a group always ends at a
    pause mark (. , ? ! : …) so the next words, such as a price, never show before they are said."""
    groups, group = [], []
    for w in words:
        group.append(w)
        if len(group) >= chunk or w["text"][-1] in CHUNK_ENDS:
            groups.append(group)
            group = []
    return groups + ([group] if group else [])


def _write_srt(words, path, chunk):
    groups = caption_chunks(words, chunk)
    lines = []
    for n, group in enumerate(groups, 1):
        end = group[-1]["t1"] + 0.2
        if n < len(groups):  # never overlap the next subtitle
            end = min(end, groups[n][0]["t0"] - 0.01)
        lines.append("%d\n%s --> %s\n%s\n" % (n, _srt_time(group[0]["t0"]), _srt_time(end),
                                           " ".join(g["text"] for g in group)))
    path.write_text("\n".join(lines), encoding="utf-8")


def _animatic_duration(seg, shot):
    """How long a clip segment lasts in the animatic: its in/out when numeric, else its fallback
    duration, else long enough to read its line."""
    out = seg.get("out")
    if isinstance(out, (int, float)):
        return max(0.5, float(out) - float(seg.get("in", 0)))
    if seg.get("fallback_duration"):
        return float(seg["fallback_duration"])
    line = seg.get("text") or shot.get("dialogue") or ""
    return max(3.0, reading_time(line) + 0.8) if line else 4.0


def _animatic_segment(sl, seg):
    """A clip segment as the human reviews it before any video exists: the shot's first frame (or its
    cutaway image) held for the segment's timing, with its words as captions. Returns (segment, shot id
    for captions or None)."""
    shot = sl.shots.get(seg["clip"]) or {}
    dur = _animatic_duration(seg, shot)
    line = seg.get("text") or shot.get("dialogue")
    if seg.get("cover"):
        background = dict({"blur": 0, "dim": 0}, **seg["cover"])
        vo = {"text": line, "at": 0.2, "speak": False} if line else None
        return dict(seg, clip=None, background=background, duration=dur, vo=vo), None
    from vglib import review
    still = review.still_target(dict(shot, id=seg["clip"]))
    return dict(seg, clip=None, still=still, duration=dur), seg["clip"]


def animatic(project):
    """`vg edit animatic`: the whole reel as stills at edit timing (captions, graphics, transitions and
    the planned narration, music and sound effects; never clips), recorded with the visuals snapshot it shows so `vg approve visuals` can require it."""
    from vglib import review
    sl = load(project, allow_errors=True)
    state = project.read_state()
    items = review.visual_items(project, sl, state)
    missing = [k for k, v in items.items() if v is None and k != "edit plan"]
    if missing:
        raise UsageError("Not generated or not found yet: %s" % ", ".join(missing))
    out = final(project, animatic=True)
    after = review.visual_items(project, sl, project.read_state())
    if review.snapshot(after) != review.snapshot(items):  # something changed while it rendered
        changed = [k for k in after if after.get(k) != items.get(k)]
        raise UsageError("%s changed while the animatic rendered, so it may not show the current version; "
                         "render it again (not recorded as seen)" % ", ".join(changed))
    review.record_animatic(project, out, review.snapshot(items))
    return out


def final(project, draft=False, animatic=False):
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise UsageError("%s is required (brew install ffmpeg)" % tool)
    from vglib import review
    spec = review.edit_spec(project)  # also checks the shapes the renderer relies on
    if spec is None:
        raise UsageError("Missing 6_Edit/Edit_Spec.json (skill vg-edit explains how to write it)")
    sl = load(project, allow_errors=True)
    state = project.read_state()
    style = spec.get("style") or {}
    voice = spec.get("voice") or {"voice": "Damayanti", "rate": 185}
    chunk = int(style.get("caption_chunk", 3))

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        vf = ("scale=%d:%d:force_original_aspect_ratio=decrease,pad=%d:%d:(ow-iw)/2:(oh-ih)/2:color=black,"
              "fps=%d,format=yuv420p,setsar=1,%s" % (W, H, W, H, FPS, UNIFORM))
        pieces, timeline, words, vos, speech = [], {}, [], [], []
        clock = 0.0
        for index, seg in enumerate(spec.get("segments", [])):
            sid = seg.get("id") or "seg%d" % index
            fallback_shot = None
            if animatic and seg.get("clip"):
                seg, fallback_shot = _animatic_segment(sl, seg)
            elif seg.get("clip") and not project.selected("clip:" + seg["clip"], state) and seg.get("fallback"):
                fallback_shot = seg["clip"]
                seg = dict(seg, still=seg["clip"], duration=seg.get("fallback_duration", 4), clip=None)
                say("note   %-8s clip:%s not generated yet; using its storyboard panel" % (sid, seg["still"]))
            piece = tmp / ("%03d.mp4" % index)
            vo = seg.get("vo")
            vo_file, vo_len = None, 0.0
            if vo and vo.get("speak", True) and not animatic:
                vo_file = tts(vo["text"], voice.get("voice", "Damayanti"), voice.get("rate", 185),
                              tmp / ("vo%03d.wav" % index))
                span = speech_span(vo_file) or (0.0, _duration(vo_file))
                vo_len = span[1]
            elif vo:
                vo_len = reading_time(vo["text"])
            if seg.get("clip"):
                clip = project.selected("clip:" + seg["clip"], state)
                if not clip:
                    raise UsageError("segment %s: clip:%s is not generated yet" % (sid, seg["clip"]))
                cin = float(seg.get("in", 0))
                # `audio`: a replacement voice track in clip time (e.g. a TTS voice aligned to the lips)
                track = _image(project, state, seg["audio"], sid) if seg.get("audio") else None
                spoken = speech_segments(track or clip)
                span = (spoken[0][0], spoken[-1][1]) if spoken else None
                out = seg.get("out", _duration(clip))
                if isinstance(out, str) and out.startswith("speech"):
                    pad = float(out.split("+", 1)[1]) if "+" in out else 0.3
                    out = min(_duration(clip), (span[1] if span else _duration(clip)) + pad)
                out = float(out)
                dur = out - cin
                cmd = ["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % cin, "-to", "%.3f" % out, "-i", str(clip)]
                if track:
                    keep = float(seg.get("clip_volume", 0)) if _has_audio(clip) else 0.0
                    cmd += ["-ss", "%.3f" % cin, "-to", "%.3f" % out, "-i", str(track), "-filter_complex",
                            "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,apad[t];"
                            + ("[0:a]volume=%.3f[c];[t][c]amix=inputs=2:normalize=0:duration=first[a]" % keep
                               if keep else "[t]anull[a]"),
                            "-map", "0:v:0", "-map", "[a]", "-t", "%.3f" % dur]
                elif _has_audio(clip):
                    cmd += ["-map", "0:v:0", "-map", "0:a:0"]
                else:
                    cmd += ["-f", "lavfi", "-t", "%.3f" % dur, "-i", "anullsrc=r=48000:cl=stereo",
                            "-map", "0:v:0", "-map", "1:a:0"]
                cover = seg.get("cover")
                cut = tmp / ("%03d_clip.mp4" % index) if cover else piece
                cmd += ["-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                        "-c:a", "aac", "-ar", "48000", "-ac", "2", str(cut)]
                _run(cmd)
                if cover:  # cutaway: the clip's sound under a picture (a map, a photo), e.g. a J-cut
                    image = _image(project, state, cover.get("image"), sid)
                    zoom, pan, pan_x = _image_opts(cover)
                    still = tmp / ("%03d_cover.mp4" % index)
                    _image_piece(image, dur, still, zoom, pan, cover.get("blur", 0), cover.get("dim", 0), pan_x)
                    _run(["ffmpeg", "-v", "error", "-y", "-i", str(still), "-i", str(cut), "-map", "0:v:0",
                          "-map", "1:a:0", "-c", "copy", "-t", "%.3f" % dur, str(piece)])
                speech += [(clock + max(a, cin) - cin, clock + min(b, out) - cin) for a, b in spoken
                           if min(b, out) > max(a, cin)]
                shot = sl.shots.get(seg["clip"]) or {}
                line = seg.get("text") or shot.get("dialogue")  # `text`: this segment's words, as captioned
                if line and span and seg.get("captions", True):
                    s0, s1 = max(span[0], cin), min(span[1], out)
                    shifted = [(clock + a - cin, clock + b - cin) for a, b in spoken]
                    words += word_times(line, clock + s0 - cin, clock + s1 - cin, shifted)
                say("clip   %-8s %s %.2f-%.2fs%s" % (sid, project.rel(clip), cin, out, " (cutaway)" if cover else ""))
            elif seg.get("still"):
                image = _image(project, state, seg["still"], sid)
                dur = float(seg.get("duration", 3))
                _image_piece(image, dur, piece, seg.get("zoom", [1.0, 1.14]), seg.get("pan", -0.05), 0, 0,
                             seg.get("pan_x"))
                shot = sl.shots.get(fallback_shot or "") or {}
                line = seg.get("text") or shot.get("dialogue")
                if line and seg.get("captions", True):
                    # stand-in for a talking clip: show the line so the edit still reads
                    words += word_times(line, clock + 0.3, clock + max(0.6, dur - 0.3))
                say("still  %-8s %s %.2fs" % (sid, project.rel(image), dur))
            else:
                raw = seg.get("duration", 3)
                if isinstance(raw, str) and raw.startswith("vo"):
                    pad = float(raw.split("+", 1)[1]) if "+" in raw else 0.5
                    raw = float((vo or {}).get("at", 0.2)) + vo_len + pad
                dur = float(raw)
                background = seg.get("background")
                if background:
                    image = _image(project, state, background.get("image"), sid)
                    zoom, pan, pan_x = _image_opts(background)
                    _image_piece(image, dur, piece, zoom, pan, background.get("blur", 18), background.get("dim", 0.35),
                                 pan_x)
                    say("card   %-8s %.2fs over %s" % (sid, dur, project.rel(image)))
                else:
                    bg = seg.get("card") or "#0F1B2D"
                    _run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-t", "%.3f" % dur, "-i",
                          "color=c=%s:s=%dx%d:r=%d" % (bg.replace("#", "0x"), W, H, FPS),
                          "-f", "lavfi", "-t", "%.3f" % dur, "-i", "anullsrc=r=48000:cl=stereo",
                          "-map", "0:v:0", "-map", "1:a:0", "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
                          "-crf", "18", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest", str(piece)])
                    say("card   %-8s %.2fs" % (sid, dur))
            timeline[sid] = (clock, dur, seg)
            if vo and seg.get("captions", True):
                at = clock + float(vo.get("at", 0.2))
                if vo_file:
                    vos.append((vo_file, at, at + vo_len))
                    speech.append((at, at + vo_len))
                    span = speech_span(vo_file) or (0.0, vo_len)
                    words += word_times(vo["text"], at + span[0], at + span[1])
                else:
                    words += word_times(vo["text"], at, at + vo_len)
            pieces.append(piece)
            clock += dur

        for index, seg in enumerate(spec.get("segments", [])):
            if index and seg.get("transition_in", "cut") != "cut":
                apply_transition(pieces[index - 1], pieces[index], seg["transition_in"], tmp)

        narration = spec.get("narration")
        narration_track, narration_spans = None, []
        if narration:  # one voice-over track for the whole reel; its phrases time the captions
            narration_track = _image(project, state, narration["file"], "narration")
            said, narration_spans = narration_words(
                narration_track, narration["text"], float(narration.get("start", 0)),
                float(narration.get("min_silence", 0.25)))
            speech += narration_spans
            if narration.get("captions", True):
                words = sorted(words + said, key=lambda w: w["t0"])
            say("voice  narration %s, %d phrase(s)" % (project.rel(narration_track), len(narration_spans)))

        listing = tmp / "list.txt"
        listing.write_text("".join("file '%s'\n" % p for p in pieces), encoding="utf-8")
        base = tmp / "base.mp4"
        _run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy",
              str(base)])
        total = _duration(base)

        layers = []
        for g in spec.get("graphics", []):
            if g.get("segment") not in timeline:
                raise UsageError("graphic %s: unknown segment %r" % (g.get("type"), g.get("segment")))
            start, dur, _ = timeline[g["segment"]]
            layer = dict(g)
            layer["t0"] = start + float(g.get("at", 0))
            until = g.get("until", "end")
            layer["t1"] = start + (dur if until == "end" else float(until))
            if g.get("through"):  # keep showing until the end of a later segment
                end_start, end_dur, _ = timeline[g["through"]]
                layer["t1"] = end_start + end_dur
            layers.append(layer)
        for seg_id, (start, dur, seg) in timeline.items():
            if seg.get("placeholder"):
                # a small corner tag, not a full-screen notice: the frame should still look designed
                first, _, rest = seg["placeholder"].partition("\n")
                layers.append({"type": "badge", "text": first, "t0": start, "t1": start + dur, "corner": "top-left",
                               "top": 150, "size": 30, "bg": "#000000A6", "border": "#FFD23F"})
                if rest.strip():
                    layers.append({"type": "card_text", "text": rest.strip(), "t0": start, "t1": start + dur,
                                   "y": 0.155, "size": 30, "color": "#FFFFFF", "opacity": 0.85, "font": "bold"})
        if words:
            layers.append({"type": "caption", "words": words, "chunk": chunk,
                           "chunks": [len(group) for group in caption_chunks(words, chunk)],
                           "y": float(style.get("caption_y", 0.74)), "size": float(style.get("caption_size", 76)),
                           "highlight": style.get("highlight", "#FFD23F")})
        overlay_spec = {"width": W, "height": H, "fps": FPS, "duration": total, "layers": layers,
                        "fonts": style.get("fonts", {})}
        spec_file = tmp / "overlay.json"
        spec_file.write_text(json.dumps(overlay_spec), encoding="utf-8")

        # audio, in its own pass: duck the base under voice-over, add the voices, music and effects,
        # normalise loudness. loudnorm holds ~3 s of sound back; in the same pass as the overlay pipe,
        # ffmpeg 8 dropped seconds of picture (Tebak Harga animatic v3/v4 froze for 2.5-2.7 s)
        inputs = ["-i", str(base)]
        for vo_file, _, _ in vos:
            inputs += ["-i", str(vo_file)]
        duck = "+".join("between(t,%.3f,%.3f)" % (a, b)
                        for a, b in [(a, b) for _, a, b in vos] + narration_spans) or "0"
        graded = grade_filter(project, state, spec.get("grade"))  # the picture only; graphics stay exact
        picture = (("[0:v]%s[g];[g][1:v]" % graded if graded else "[0:v][1:v]")
                   + "overlay=0:0:alpha=premultiplied:eof_action=pass[v]")
        chains = ["[0:a]volume=0.3:enable='%s'[bed]" % duck]
        mix = ["[bed]"]
        for i, (_, at, _) in enumerate(vos):
            ms = int(at * 1000)
            chains.append("[%d:a]adelay=%d|%d,volume=1.4[vo%d]" % (i + 1, ms, ms, i))
            mix.append("[vo%d]" % i)
        stereo = "aformat=sample_rates=48000:channel_layouts=stereo"
        n = len(vos) + 1  # next input index
        if narration_track:
            ms = int(float(narration.get("start", 0)) * 1000)
            inputs += ["-i", str(narration_track)]
            chains.append("[%d:a]%s,adelay=%d|%d,volume=%.3f[nar]"
                          % (n, stereo, ms, ms, float(narration.get("volume", 1.0))))
            mix.append("[nar]")
            n += 1
        music = spec.get("music")
        if music:  # a licensed track under everything, ducked while anyone speaks
            track = _image(project, state, music["file"], "music")
            inputs += ["-stream_loop", "-1", "-i", str(track)]
            talk = "+".join("between(t,%.3f,%.3f)" % (a - 0.15, b + 0.25) for a, b in speech) or "0"
            fade_out = float(music.get("fade_out", 1.5))
            at = min(max(0.0, float(music.get("at", 0))), total)  # when the music comes in, e.g. after a cold open
            ms = int(at * 1000)
            chains.append("[%d:a]%s,atrim=%.3f:%.3f,asetpts=N/SR/TB,afade=t=in:d=%.2f,adelay=%d|%d,"
                          "volume=%.3f,volume=%.3f:enable='%s',afade=t=out:st=%.3f:d=%.2f[mus]"
                          % (n, stereo, float(music.get("start", 0)), float(music.get("start", 0)) + total - at,
                             float(music.get("fade_in", 0.3)), ms, ms, float(music.get("volume", 0.22)),
                             float(music.get("duck", 0.4)), talk, max(0.0, total - fade_out), fade_out))
            mix.append("[mus]")
            n += 1
        for i, fx in enumerate(spec.get("sfx", [])):  # sound effects: a whoosh on a whip, a pop on a card
            at = float(fx["at"])
            if fx.get("segment"):
                if fx["segment"] not in timeline:
                    raise UsageError("sfx[%d]: unknown segment %r" % (i, fx["segment"]))
                at += timeline[fx["segment"]][0]
            ms = int(max(0.0, at) * 1000)
            inputs += ["-i", str(_image(project, state, fx["file"], "sfx"))]
            chains.append("[%d:a]%s,adelay=%d|%d,volume=%.3f[fx%d]"
                          % (n, stereo, ms, ms, float(fx.get("volume", 0.8)), i))
            mix.append("[fx%d]" % i)
            n += 1
        chains.append("%samix=inputs=%d:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]"
                      % ("".join(mix), len(mix)))
        name = spec.get("output") or "%s_v1.0.mp4" % (sl.data.get("project") or project.name)
        if animatic:  # tool-made media: plain integer versions
            out_dir = project.path / "6_Edit"
            stem = "Animatic_%s" % (sl.data.get("project") or project.name)
            n = 1
            while (out_dir / ("%s_v%d.mp4" % (stem, n))).exists():
                n += 1
            out = out_dir / ("%s_v%d.mp4" % (stem, n))
        elif draft:
            out_dir = project.path / "6_Edit"
            stem = "Draft_" + Path(name).stem
            n = 1
            while (out_dir / ("%s_d%d.mp4" % (stem, n))).exists():
                n += 1
            out = out_dir / ("%s_d%d.mp4" % (stem, n))
        else:
            out_dir = project.path / "99_Output"
            out = out_dir / name
        out_dir.mkdir(exist_ok=True)
        if out.exists():
            raise UsageError("%s already exists; never overwrite a delivered version, set a new `output` name"
                             % project.rel(out))
        mixed = tmp / "mix.wav"
        _run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(chains), "-map", "[a]",
              "-c:a", "pcm_s16le", "-ar", "48000", "-t", "%.3f" % total, str(mixed)])
        renderer = renderer_binary()
        say("render %d overlay layer(s), %d caption word(s), %.1fs" % (len(layers), len(words), total))
        overlay_proc = subprocess.Popen([str(renderer), str(spec_file)], stdout=subprocess.PIPE)
        # the picture alone (any audio stream in this pass lost frames too), then a stream-copy mux
        pictured = tmp / "picture.mp4"
        ffmpeg = subprocess.run(["ffmpeg", "-v", "error", "-y", "-reinit_filter", "0", "-i", str(base),
                                 "-f", "rawvideo", "-pix_fmt", "rgba",
                                 "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
            "-filter_complex", picture, "-map", "[v]", "-c:v", "libx264", "-preset", "medium",
            "-crf", "18", "-pix_fmt", "yuv420p", "-t", "%.3f" % total, str(pictured)],
            stdin=overlay_proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1800)
        overlay_proc.stdout.close()
        overlay_proc.wait()
        if ffmpeg.returncode != 0:
            raise UsageError("final render failed: %s" % ffmpeg.stderr.decode("utf-8", "replace").strip()[-400:])
        _run(["ffmpeg", "-v", "error", "-y", "-i", str(pictured), "-i", str(mixed), "-map", "0:v", "-map", "1:a",
              "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
              "-t", "%.3f" % total, str(out)])
        check_frames(out, total)
        if words:
            _write_srt(words, out.with_suffix(".srt"), chunk)
    say("final  %s (%.1fs)%s" % (project.rel(out), _duration(out),
                                 " + %s" % project.rel(out.with_suffix(".srt")) if words else ""))
    return out
