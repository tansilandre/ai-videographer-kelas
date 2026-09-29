"""The visual review gate: before any video, the human approves the look (style frames) and then the
whole reel as images (board filmstrip + animatic). Design: 4_Docs/Specs/2026-09-28_Visual_Review_Gate_Design_v1.0.md

An approval stores `items` (label -> SHA-256 of a file or of text) and `snapshot` = hash of items.
Anything the human saw that changes afterwards (a new selected version, an edited photo, edited
text in the edit plan) changes the snapshot, so the approval is stale and the video gate closes.
"""
import json
import shlex

from vglib import compat, config
from vglib.errors import Refused, UsageError
from vglib.project import now_iso, sha256_file, sha256_json

EDIT_SPEC = "6_Edit/Edit_Spec.json"
LOOK_TEXT = ("world", "light", "grade", "graphics")
SPEC_IGNORED = ("output", "voice", "music", "sfx")  # sound and delivery settings, not what the viewer sees
SEGMENT_AUDIO = ("audio", "clip_volume")
TRANSITIONS = ("cut", "flash", "whip")


def _sha(path):
    return sha256_file(path) if path is not None and path.is_file() else None


def snapshot(items):
    return sha256_json(items)


# ---------------------------------------------------------------------- what the human sees

def look_items(project, sl, state):
    look = sl.look()
    items = {"look text": sha256_json({k: look.get(k, "") for k in LOOK_TEXT})}
    for frame in sl.look_frames():
        items["look frame %s" % frame["id"]] = _sha(project.selected("look:" + frame["id"], state))
    return items


def edit_spec(project):
    """The edit plan, checked for the shapes the renderer and the gate rely on (None if not written)."""
    path = project.path / EDIT_SPEC
    if not path.is_file():
        return None
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise UsageError("%s is not valid JSON: %s" % (EDIT_SPEC, exc))
    if not isinstance(spec, dict) or not isinstance(spec.get("segments"), list):
        raise UsageError("%s: needs an object with a \"segments\" list" % EDIT_SPEC)
    if not isinstance(spec.get("graphics", []), list):
        raise UsageError("%s: \"graphics\" must be a list" % EDIT_SPEC)
    _check_grade(project, spec.get("grade"))
    _check_sound(project, spec)
    for i, seg in enumerate(spec["segments"]):
        where = "%s segments[%d]" % (EDIT_SPEC, i)
        if not isinstance(seg, dict):
            raise UsageError("%s: must be an object" % where)
        if seg.get("transition_in", "cut") not in TRANSITIONS:
            raise UsageError("%s.transition_in: must be one of %s" % (where, ", ".join(TRANSITIONS)))
        if "still" in seg and not isinstance(seg["still"], str):
            raise UsageError("%s.still: must be an image ref such as \"storyboard:S02\" or \"file:0_Source/x.jpg\""
                             % where)
        for key in ("background", "cover"):
            if key in seg and not (isinstance(seg[key], dict) and isinstance(seg[key].get("image"), str)):
                raise UsageError("%s.%s: must be an object with an \"image\" ref" % (where, key))
    return spec


GRADE_NUMBERS = {"contrast": (0.5, 2.0), "brightness": (-0.5, 0.5), "saturation": (0.0, 2.0),
                 "gamma": (0.5, 2.0), "temperature": (2000, 12000), "grain": (0, 40)}


def _check_grade(project, grade):
    """`grade` in the edit plan: one colour treatment over every clip (LUT file and/or numbers)."""
    if grade is None:
        return
    where = "%s grade" % EDIT_SPEC
    if not isinstance(grade, dict):
        raise UsageError("%s: must be an object, e.g. {\"contrast\": 1.05, \"temperature\": 5200}" % where)
    unknown = sorted(set(grade) - set(GRADE_NUMBERS) - {"lut"})
    if unknown:
        raise UsageError("%s: unknown key(s) %s; use lut, %s" % (where, ", ".join(unknown), ", ".join(GRADE_NUMBERS)))
    for key, (low, high) in GRADE_NUMBERS.items():
        value = grade.get(key)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                                  or not low <= value <= high):
            raise UsageError("%s.%s: must be a number from %g to %g" % (where, key, low, high))
    lut = grade.get("lut")
    if lut is not None:
        if not (isinstance(lut, str) and lut.startswith("file:") and lut.endswith(".cube")):
            raise UsageError("%s.lut: must be \"file:<path to a .cube file in the project>\"" % where)
        if resolve_image(project, None, lut) is None:
            raise UsageError("%s.lut: %s not found inside the project" % (where, lut))


def _check_sound(project, spec):
    """`narration` (one voice-over track for the whole reel, captioned from its words) and `sfx`."""
    narration = spec.get("narration")
    if narration is not None:
        where = "%s narration" % EDIT_SPEC
        if not (isinstance(narration, dict) and isinstance(narration.get("file"), str)
                and isinstance(narration.get("text"), str) and narration["text"].strip()):
            raise UsageError("%s: must be {\"file\": \"file:6_Edit/1_Audio/<track>.wav\", \"text\": \"<the words>\"}"
                             % where)
        if resolve_image(project, None, narration["file"]) is None:
            raise UsageError("%s.file: %s not found inside the project" % (where, narration["file"]))
    sfx = spec.get("sfx", [])
    if not isinstance(sfx, list):
        raise UsageError("%s sfx: must be a list of {\"file\", \"at\"}" % EDIT_SPEC)
    for i, fx in enumerate(sfx):
        where = "%s sfx[%d]" % (EDIT_SPEC, i)
        if not (isinstance(fx, dict) and isinstance(fx.get("file"), str)
                and isinstance(fx.get("at"), (int, float)) and not isinstance(fx.get("at"), bool)):
            raise UsageError("%s: must be {\"file\": \"file:...\", \"at\": seconds} (optional \"segment\", \"volume\")"
                             % where)
        if resolve_image(project, None, fx["file"]) is None:
            raise UsageError("%s.file: %s not found inside the project" % (where, fx["file"]))


def edit_images(spec):
    """Every image the edit plan shows directly: stills and background/cover images."""
    refs = []
    for seg in spec.get("segments", []):
        if isinstance(seg.get("still"), str):
            refs.append(seg["still"])
        for key in ("background", "cover"):
            image = (seg.get(key) or {}).get("image")
            if image:
                refs.append(image)
    return list(dict.fromkeys(refs))


def resolve_image(project, state, ref):
    """Same rules as the edit renderer: file:<path inside the project>, kind:id, or a bare shot id."""
    if ref.startswith("file:"):
        root = project.path.resolve()
        path = (root / ref[len("file:"):]).resolve()
        return path if root in path.parents and path.is_file() else None
    return project.selected(ref if ":" in ref else "storyboard:" + ref, state)


def still_target(shot):
    """The picture that stands for a shot before its clip exists (animatic, filmstrip, character anchor):
    its planned first frame, else its storyboard panel."""
    first = shot.get("first_frame") or {}
    return ("first:" if first.get("prompt") or first.get("file") else "storyboard:") + shot["id"]


def segment_image(project, sl, state, seg):
    """The picture a viewer sees for one edit segment, as the animatic shows it (None when it has none)."""
    if seg.get("cover"):
        return resolve_image(project, state, seg["cover"].get("image", ""))
    if seg.get("clip"):
        shot = sl.shots.get(seg["clip"])
        return project.selected(still_target(shot), state) if shot else None
    if isinstance(seg.get("still"), str):
        return resolve_image(project, state, seg["still"])
    image = (seg.get("background") or {}).get("image")
    return resolve_image(project, state, image) if image else None


def reel_beats(project, sl, state, spec):
    """Every beat in timeline order, as the board filmstrip and the review page show it: the edit
    plan's segments when `spec` (from edit_spec) is given, else the shot list. Each beat has id, text
    (on-screen text or voice-over), image (path or None), placeholder (label when there is no image)
    and shot (the AI shot behind it, or None)."""
    beats = []
    if spec:
        texts = {}
        for g in spec.get("graphics", []):
            for key in ("text", "label", "caption", "brand", "cta"):
                if g.get(key):
                    texts.setdefault(g.get("segment"), []).append(str(g[key]).replace("\n", " "))
        for seg in spec.get("segments", []):
            sid = seg.get("id", "?")
            text = seg.get("text") or (seg.get("vo") or {}).get("text") or " · ".join(texts.get(sid, []))
            beats.append({"id": sid, "text": text or "", "image": segment_image(project, sl, state, seg),
                          "placeholder": seg.get("placeholder") or seg.get("card") or "no image",
                          "shot": seg.get("clip") if seg.get("clip") in sl.shots else None})
        return beats
    for shot in sl.data.get("shots", []):
        sid = shot.get("id", "?")
        ai = shot.get("source") == "ai"
        beats.append({"id": sid, "text": shot.get("on_screen_text") or shot.get("summary", ""),
                      "image": project.selected("storyboard:" + sid, state) if ai else None,
                      "placeholder": {"real": "real footage", "mg": "motion graphic"}.get(shot.get("source"),
                                                                                      "not generated"),
                      "shot": sid if ai else None})
    return beats


def shot_inputs(project, sl, shot, state):
    """(label, path or None) for every image a video request for this shot sends. `build_video_job`
    takes its images from here too, so what the human approved and what is sent cannot differ."""
    sid, mode = shot["id"], shot.get("mode")
    out = []
    if mode == "frames":
        first = sl.normalize_ref("first:" + sid)[1]
        out.append(("%s first frame (%s)" % (sid, first), project.selected(first, state)))
        if shot.get("last_frame"):
            out.append(("%s last frame" % sid, project.selected("last:" + sid, state)))
    elif mode == "character":
        anchor = still_target(shot)
        out.append(("%s anchor (%s)" % (sid, anchor), project.selected(anchor, state)))
    elif mode == "lipsync":  # the presenter's picture, then the narration she says (cut in build_video_job)
        anchor = still_target(shot)
        out.append(("%s anchor (%s)" % (sid, anchor), project.selected(anchor, state)))
        audio = (shot.get("lipsync") or {}).get("audio") or ""
        out.append(("%s lipsync audio" % sid, resolve_image(project, state, audio) if audio.startswith("file:")
                    else None))
    if mode in ("character", "text"):
        for ref in shot.get("video_refs") or []:
            kind, value = sl.normalize_ref(ref)
            path = resolve_image(project, state, "file:" + value) if kind == "file" else project.selected(value, state)
            out.append(("%s video ref %s" % (sid, ref), path))
    return out


def shot_frames(sl):
    """(label, target) for every frame an AI shot is planned to have, in timeline order."""
    out = []
    for shot in sl.ai_shots():
        sid = shot["id"]
        if (shot.get("storyboard") or {}).get("prompt"):
            out.append(("%s storyboard" % sid, "storyboard:" + sid))
        first, last = shot.get("first_frame") or {}, shot.get("last_frame") or {}
        if first.get("prompt") or first.get("file"):
            out.append(("%s first frame" % sid, "first:" + sid))
        if last.get("prompt") or last.get("file"):
            out.append(("%s last frame" % sid, "last:" + sid))
    return out


def visual_items(project, sl, state):
    """Everything the human judges in the sequence review, and everything video will be sent."""
    items = {"look": snapshot(look_items(project, sl, state)),
             "shot list": sha256_json([[s.get("id"), s.get("source"), s.get("mode")] for s in sl.data.get("shots", [])])}
    for label, target in shot_frames(sl):
        items[label] = _sha(project.selected(target, state))
    for shot in sl.ai_shots():
        sid = shot["id"]
        items["%s picture (%s)" % (sid, still_target(shot))] = _sha(project.selected(still_target(shot), state))
        for label, path in shot_inputs(project, sl, shot, state):
            items[label] = _sha(path)
        items["%s words" % sid] = sha256_json({k: shot.get(k) for k in ("dialogue", "vo", "on_screen_text", "lipsync")})
        if shot.get("mode") == "character":
            for name in shot.get("characters") or []:
                char = sl.characters.get(name) or {}
                for key in ("portrait", "body"):
                    if char.get(key):
                        items["character %s %s" % (name, key)] = _sha(project.selected("asset:" + char[key], state))
    spec = edit_spec(project)
    if spec is None:
        items["edit plan"] = None
        return items
    plan = {k: v for k, v in spec.items() if k not in SPEC_IGNORED}
    plan["segments"] = [{k: v for k, v in seg.items() if k not in SEGMENT_AUDIO} for seg in spec.get("segments", [])]
    items["edit plan"] = sha256_json(plan)
    for ref in edit_images(spec):
        items["image %s" % ref] = _sha(resolve_image(project, state, ref))
    lut = (spec.get("grade") or {}).get("lut")
    if lut:
        items["grade lut %s" % lut] = _sha(resolve_image(project, state, lut))
    narration = spec.get("narration")
    if narration:  # its pauses time the captions the human sees
        items["narration audio"] = _sha(resolve_image(project, state, narration["file"]))
    return items


# ---------------------------------------------------------------------- gate checks

def _changed(approved, current):
    labels = [k for k in current if approved.get(k) != current[k]]
    return labels + [k for k in approved if k not in current]


def _check(project, name, approval, items):
    if not approval:
        return "%s not approved" % name
    if approval.get("project_path") and approval["project_path"] != str(project.path.resolve()):
        return "%s approval was made in another project folder (copied project); approve again here" % name
    if approval.get("snapshot") != snapshot(items):
        return "%s changed since approval: %s" % (name, ", ".join(_changed(approval.get("items") or {}, items)))
    return None


def look_problem(project, sl, state):
    if not sl.look_frames():
        return "the look is not planned (Shotlist.json has no look.style_frames)"
    return _check(project, "look", state["approvals"].get("look"), look_items(project, sl, state))


def problems(project, sl, state):
    """Why video may not run yet, or [] when both approvals exist and match what is on disk."""
    found = []
    look = look_problem(project, sl, state)
    if look:
        found.append(look)
    visuals = _check(project, "visuals", state["approvals"].get("visuals"), visual_items(project, sl, state))
    if visuals:
        found.append(visuals)
    return found


def gate_message(project, found):
    return ("Visual review gate closed: %s.\nShow the human the board (vg board -p %s) and the animatic "
            "(vg edit animatic -p %s). Only after their explicit 'approved' in chat run vg approve look / "
            "vg approve visuals." % ("; ".join(found), project.name, project.name))


def look_refs(sl, target):
    """Refs to append to an image request once the look is approved: the style frames, for shot
    images and non-character assets, unless the shot or asset sets "look_refs": false."""
    kind, ident = target.split(":", 1)
    if kind in ("storyboard", "first", "last"):
        holder = sl.shots.get(ident) or {}
    elif kind == "asset":
        holder = sl.assets.get(ident) or {}
        if holder.get("kind") == "character":
            return []  # identity anchors stay on their neutral background
        if target in sl.look_asset_deps():
            return []  # a sheet a style frame is built from: a ref back would re-roll the look forever
    else:
        return []
    if holder.get("look_refs", True) is False:
        return []
    return [("target", "look:" + f["id"]) for f in sl.look_frames()]


def gate_status(project, sl, state):
    """One line per gate for `vg status` and the board: (name, ok, text). Never raises: a broken edit
    plan is reported, not thrown, so status and the board always work."""
    look = look_problem(project, sl, state)
    try:
        visuals = _check(project, "visuals", state["approvals"].get("visuals"), visual_items(project, sl, state))
    except UsageError as exc:
        visuals = "cannot check: %s" % exc
    return [("look", not look, look or "approved"), ("visuals", not visuals, visuals or "approved")]


# ---------------------------------------------------------------------- animatic record

def record_animatic(project, path, shown):
    """Remember which visuals snapshot an animatic shows (taken before rendering it), so approval can
    require that the human saw the current one."""
    with project.transaction() as st:
        st.setdefault("animatics", []).append({"path": project.rel(path), "snapshot": shown, "at": now_iso()})


def _latest_animatic(state):
    return (state.get("animatics") or [None])[-1]


# ---------------------------------------------------------------------- approvals

def _command(project, stage):
    return ("cd %s && " + compat.VG + " approve %s -p %s") % (
        shlex.quote(str(config.ROOT)), stage, shlex.quote(project.name))


def animatic_mark(record):
    """What identifies the animatic a human was shown (None when there was none)."""
    return "%s@%s" % (record["path"], record["at"]) if record else None


def approve_look(project, expected=None, via_page=False):
    """`expected`: the look snapshot the human was shown (the review page sends it); anything else on
    disk is refused, so an approval never covers a picture that changed after it was shown."""
    from vglib.generate import _human_confirm_text, load, say  # generate imports this module
    sl = load(project)
    if not sl.look_frames():
        raise UsageError("Shotlist.json has no look.style_frames. Write the look block first (skill vg-scene).")
    state = project.read_state()
    items = look_items(project, sl, state)
    missing = [k for k, v in items.items() if v is None]
    if missing:
        raise UsageError("Generate the style frames first (vg image -p %s --stage look): %s"
                         % (project.name, ", ".join(missing)))
    if expected is not None and expected != snapshot(items):
        raise Refused("The look changed after the review page showed it; nothing was approved. "
                      "Refresh the page, look again, then approve.")
    for frame in sl.look_frames():
        say("look   %-12s %s" % (frame["id"], project.rel(project.selected("look:" + frame["id"], state))))
    _human_confirm_text("Approve the look (%d style frame(s))?" % len(sl.look_frames()), _command(project, "look"),
                        via_page)
    with project.transaction() as st:
        if snapshot(look_items(project, sl, st)) != snapshot(items):
            raise Refused("The look changed while waiting for the code; nothing was approved. Show it again.")
        st["approvals"]["look"] = {"snapshot": snapshot(items), "items": items,
                                   "project_path": str(project.path.resolve()), "at": now_iso()}
    say("approved the look. Changing a style frame or the look text voids it, and with it the visuals approval.")


def approve_visuals(project, expected=None, expected_animatic=None, via_page=False):
    """`expected` / `expected_animatic`: the visuals snapshot and the animatic (animatic_mark) the human
    was shown on the review page; a mismatch is refused."""
    from vglib.generate import _human_confirm_text, load, say
    sl = load(project)
    state = project.read_state()
    look = look_problem(project, sl, state)
    if look:
        raise Refused("Approve the look before the visuals: %s." % look)
    unplanned = [s["id"] for s in sl.ai_shots() if s.get("mode") == "frames" and not s.get("first_frame")]
    if unplanned:
        raise UsageError("Frames-mode shots without a first frame planned: %s (skill vg-storyboard)"
                         % ", ".join(unplanned))
    items = visual_items(project, sl, state)
    if items["edit plan"] is None:
        raise UsageError("Write %s first: the text, map, photos and captions are part of the visual review "
                         "(skill vg-edit)" % EDIT_SPEC)
    missing = [k for k, v in items.items() if v is None]
    if missing:
        raise UsageError("Not generated or not found yet: %s" % ", ".join(missing))
    in_plan = {seg.get("clip") for seg in edit_spec(project)["segments"]}
    absent = [s["id"] for s in sl.ai_shots() if s["id"] not in in_plan]
    if absent:
        raise UsageError("AI shots not in the edit plan, so the human never sees them in the animatic: %s. "
                         "Add a clip segment for each (skill vg-edit)." % ", ".join(absent))
    latest = _latest_animatic(state)
    if latest and not (project.path / latest["path"]).is_file():
        raise Refused("The latest animatic (%s) is missing. Render it again (vg edit animatic -p %s) and show it."
                      % (latest["path"], project.name))
    if not latest or latest.get("snapshot") != snapshot(items):
        raise Refused("The human has not seen the current visuals. Render the animatic (vg edit animatic -p %s), "
                      "show it with the board, and approve only after their explicit 'approved'." % project.name)
    if expected is not None and (expected != snapshot(items) or expected_animatic != animatic_mark(latest)):
        raise Refused("The reel or its animatic changed after the review page showed it; nothing was approved. "
                      "Refresh the page, watch it again, then approve.")
    frames = [label for label, _ in shot_frames(sl)]
    say("visuals: %d AI frame(s), %d edit-plan image(s), animatic %s"
        % (len(frames), len([k for k in items if k.startswith("image ")]), latest["path"]))
    _human_confirm_text("Approve the visuals of the whole reel?", _command(project, "visuals"), via_page)
    with project.transaction() as st:
        if snapshot(visual_items(project, sl, st)) != snapshot(items):
            raise Refused("The visuals changed while waiting for the code; nothing was approved. Show them again.")
        st["approvals"]["visuals"] = {"snapshot": snapshot(items), "items": items, "animatic": latest["path"],
                                      "project_path": str(project.path.resolve()), "at": now_iso()}
    say("approved the visuals. Any change to a frame, photo or the edit plan voids this approval.")
