"""`vg next`: the one next step of a project, worked out from Shotlist.json, the ledger and the disk, for
an agent (often a small model in an agent app such as WorkBuddy) to follow without holding the whole
pipeline in mind. It never runs or pays for anything.

Each line starts with a tag:
  STAGE  where the project is and why
  NOTE   a change note the human wrote on the review page
  RUN    the one command to run now (TIME: how long it takes)
  WRITE  a file the agent writes or fixes, and the skill to read first
  DO     something to change before anything else (e.g. act on the human's notes)
  ASK    stop: tell or ask the human this, and wait for their reply
  THEN   what to do after that
  DONE   the reel is finished
"""
import datetime
import os
import shlex

from vglib import config, generate, review, review_page
from vglib.errors import UsageError
from vglib.shotlist import Shotlist

VG = "python3 2_Tools/vg/vg.py"
LONG_S = "give the command a timeout of at least 20 minutes (or run it in the background and wait for it)"
AGAIN = "run `%s next -p %%s` again" % VG


def vg(verb, project, extra=""):
    return "%s %s -p %s%s" % (VG, verb, shlex.quote(project.name), extra)


def _ts(text):
    try:
        return datetime.datetime.fromisoformat(str(text)).timestamp()
    except ValueError:
        return 0.0


def _open_notes(project, state, prefixes, since):
    """Notes the human wrote that nothing was made after yet (`since`: when the last fix was made)."""
    notes = state.get(review_page.NOTES) or {}
    return [(item, entry["note"]) for item, entry in sorted(notes.items())
            if item.startswith(prefixes) and float(entry.get("ts") or _ts(entry.get("at"))) > since]


def _newest_file(project, state, targets):
    newest = 0.0
    for target in targets:
        path = project.selected(target, state)
        if path is not None:
            newest = max(newest, os.path.getmtime(str(path)))
    return newest


def _review_ask(project, stage):
    """How the human approves the look or the reel in the current approval mode."""
    button = "Approve look" if stage == "look" else "Approve reel"
    what = ("the style frames (the look of the whole reel)" if stage == "look"
            else "the whole reel as images: every frame, the text on screen and the animatic")
    mode = generate.approval_mode()
    if mode == "terminal":
        return [("RUN", vg("review", project, " --detach")),
                ("ASK", "Send the human the review link. Ask them to check %s, write a note on anything to change "
                        "and click Done; if it is right, they approve by running this in their own terminal app "
                        "and typing the code it shows: %s" % (what, review._command(project, stage))),
                ("THEN", "when they say they are done, " + AGAIN % project.name)]
    return [("RUN", vg("review", project, " --detach")),
            ("ASK", "Send the human the review link. Ask them to check %s: if it is right, click '%s'; if not, "
                    "write a note on the picture and click 'Done, back to the agent'. Wait for their reply."
                    % (what, button)) if mode == "page" else
            ("ASK", "Send the human the review link and ask them to check %s. Only on their explicit 'approved' in "
                    "chat, run: %s approve %s -p %s" % (what, VG, stage, project.name)),
            ("THEN", "when they say they are done, " + AGAIN % project.name)]


def _video_ask(project, shots, total, pilot, new_take=False):
    names = ", ".join(shots)
    what = ("the pilot clip %s (%g credits)" % (names, total) if pilot
            else "the clips %s (%g credits in total)" % (names, total))
    mode = generate.approval_mode()
    command = "cd %s && %s approve video -p %s --shots %s --confirm %g%s" % (
        shlex.quote(str(config.ROOT)), VG, shlex.quote(project.name), ",".join(shots), total,
        " --new-take" if new_take else "")
    if mode == "page":
        steps = [("RUN", vg("review", project, " --detach")),
                 ("ASK", "Video costs credits, so the human decides. Send them the review link and ask them to "
                         "approve %s in the Video section of the page (one click per clip, then confirm). Wait for "
                         "their reply." % what)]
    elif mode == "terminal":
        steps = [("ASK", "Video costs credits, so the human decides. Show them %s and ask them to run this in "
                         "their own terminal app and type the code it shows: %s" % (what, command))]
    else:
        steps = [("ASK", "Video costs credits, so the human decides. Ask: approve %s? Only on a clear yes, run: %s"
                         % (what, command.split("&& ", 1)[1]))]
    return steps + [("THEN", "when they say it is approved, " + AGAIN % project.name)]


BRIEF_QUESTIONS = ("1. Brand or client name?  2. What is sold, where, and from what price?  3. Three things that "
                   "make it worth it?  4. What should the viewer do at the end (DM, WhatsApp, visit)?  5. Real photos "
                   "of the place? (attach them; without photos every picture is AI)")
NOT_A_BRIEF = ("README.md", ".gitkeep", ".DS_Store")


def _has_brief(project):
    source = project.path / "0_Source"
    return source.is_dir() and any(f.is_file() and f.name not in NOT_A_BRIEF for f in source.rglob("*"))


def steps(project):
    """The next step as (tag, text) pairs."""
    planned = project.shotlist_path.is_file() and (project.shotlist().get("shots") or [])
    if not planned and not _has_brief(project):
        return [("STAGE", "brief: nothing in 0_Source/ yet"),
                ("ASK", "Ask the human these five questions in one message, in their language: " + BRIEF_QUESTIONS),
                ("THEN", "write their answers as 0_Source/Brief.md, copy any photos they attach into 0_Source/, "
                         "then " + AGAIN % project.name)]
    if not project.shotlist_path.is_file():
        return [("STAGE", "plan: there is no shot list yet"),
                ("WRITE", "1_Script/Shotlist.json from the brief in 0_Source/, including the look block; "
                          "read skill vg-scene first"),
                ("THEN", "run `%s` and fix what it reports, then %s" % (vg("validate", project), AGAIN % project.name))]
    sl = Shotlist(project.shotlist(), project)
    errors, _ = sl.validate()
    if errors:
        return ([("STAGE", "plan: Shotlist.json has %d error(s)" % len(errors))]
                + [("NOTE", e) for e in errors[:8]]
                + [("WRITE", "fix these errors in 1_Script/Shotlist.json (skill vg-scene explains every field)"),
                   ("THEN", "run `%s`, then %s" % (vg("validate", project), AGAIN % project.name))])
    if not sl.look_frames():
        return [("STAGE", "plan: the look is not written"),
                ("WRITE", "the look block in 1_Script/Shotlist.json (world, light, grade, graphics, 1-3 "
                          "style_frames); read skill vg-scene, step 7b"),
                ("THEN", AGAIN % project.name)]
    state = project.read_state()

    # 1. the look
    look_targets = sl.image_targets("look")
    if [t for t in look_targets if project.selected(t, state) is None]:
        return [("STAGE", "look: the style frames are not made yet"),
                ("RUN", vg("image", project, " --stage look")),
                ("TIME", "about 1-3 minutes; " + LONG_S),
                ("THEN", "look at every image it made (open the files), then " + AGAIN % project.name)]
    if review.look_problem(project, sl, state):
        notes = _open_notes(project, state, ("look:",), _newest_file(project, state, look_targets))
        if notes:
            return ([("STAGE", "look review: the human left %d note(s)" % len(notes))]
                    + [("NOTE", "%s: %s" % (item, " / ".join(text.splitlines()))) for item, text in notes]
                    + [("DO", "for each note, change that style frame's prompt in 1_Script/Shotlist.json "
                              "look.style_frames (skill vg-image-prompt), then re-make it: %s (one --target per "
                              "noted frame, e.g. %s)" % (vg("image", project, " --target <look:id> --new-take"),
                                                         ", ".join(item for item, _ in notes))),
                       ("THEN", AGAIN % project.name)])
        return [("STAGE", "look review: the human approves the look before any other picture is made")] + \
            _review_ask(project, "look")

    # 2. the rest of the pictures
    unplanned = [s["id"] for s in sl.ai_shots() if s.get("mode") == "frames" and not s.get("first_frame")]
    for stage in ("refs", "storyboard", "frames"):
        missing = [t for t in sl.image_targets(stage) if project.selected(t, state) is None]
        if missing:
            return [("STAGE", "pictures: %d %s image(s) not made yet (%s)" % (len(missing), stage,
                                                                         ", ".join(missing[:6]))),
                    ("RUN", vg("image", project, " --stage " + stage)),
                    ("TIME", "about 1-3 minutes; " + LONG_S),
                    ("THEN", "look at every image it made (open the files); re-make a bad one with --target "
                             "<kind:id> --new-take; then " + AGAIN % project.name)]
    if unplanned:
        return [("STAGE", "pictures: frames-mode shots without a first frame: %s" % ", ".join(unplanned)),
                ("WRITE", "first_frame for those shots in 1_Script/Shotlist.json; read skill vg-storyboard"),
                ("THEN", AGAIN % project.name)]

    # 3. the edit plan and the animatic
    if not (project.path / review.EDIT_SPEC).is_file():
        return [("STAGE", "edit plan: 6_Edit/Edit_Spec.json is not written"),
                ("WRITE", "6_Edit/Edit_Spec.json (timing, text on screen, captions, sound); read skill vg-edit"),
                ("THEN", AGAIN % project.name)]
    try:
        review.edit_spec(project)
    except UsageError as exc:
        return [("STAGE", "edit plan: 6_Edit/Edit_Spec.json has a problem"), ("NOTE", str(exc)),
                ("WRITE", "fix 6_Edit/Edit_Spec.json (skill vg-edit)"), ("THEN", AGAIN % project.name)]
    look_ok, visuals_ok = [ok for _, ok, _ in review.gate_status(project, sl, state)]
    if not visuals_ok:
        latest = review._latest_animatic(state)
        try:
            shown = review.snapshot(review.visual_items(project, sl, state))
        except UsageError as exc:
            return [("STAGE", "reel review: the reel cannot be checked"), ("NOTE", str(exc)),
                    ("WRITE", "fix what the note names (skill vg-edit or vg-storyboard)"), ("THEN", AGAIN % project.name)]
        made = project.path / latest["path"] if latest else None
        notes = _open_notes(project, state, ("beat:", "asset:"),
                            os.path.getmtime(str(made)) if made and made.is_file() else 0.0)
        if notes:
            return ([("STAGE", "reel review: the human left %d note(s)" % len(notes))]
                    + [("NOTE", "%s: %s" % (item, " / ".join(text.splitlines()))) for item, text in notes]
                    + [("DO", "act on each note: re-prompt or re-make that beat's picture (vg image --target "
                              "<kind:id> --new-take) or change 6_Edit/Edit_Spec.json; then render the animatic "
                              "again: " + vg("edit animatic", project)),
                       ("THEN", AGAIN % project.name)])
        if not latest or latest.get("snapshot") != shown or not (project.path / latest["path"]).is_file():
            return [("STAGE", "reel review: the animatic does not show the current pictures"),
                    ("RUN", vg("edit animatic", project)),
                    ("TIME", "about 1-3 minutes; " + LONG_S),
                    ("THEN", "watch it yourself, then " + AGAIN % project.name)]
        return [("STAGE", "reel review: the human approves the whole reel as images before any video")] + \
            _review_ask(project, "visuals")

    # 4. video
    missing_prompts = [s["id"] for s in sl.ai_shots() if not s.get("video_prompt")]
    if missing_prompts:
        return [("STAGE", "video prompts: not written for %s" % ", ".join(missing_prompts)),
                ("WRITE", "video_prompt for those shots in 1_Script/Shotlist.json; read skill vg-video-prompt"),
                ("THEN", "run `%s`, then %s" % (vg("validate", project), AGAIN % project.name))]
    for shot in sl.ai_shots():
        busy = generate._in_flight(state, "clip:" + shot["id"])
        if busy and busy[-1]["state"] != "pending":
            return [("STAGE", "video: clip:%s is stuck in state %r" % (shot["id"], busy[-1]["state"])),
                    ("ASK", "Tell the human: the tool cannot tell whether kie.ai made this task. They check the kie.ai "
                            "dashboard, then run `vg adopt` (a task exists) or `vg release` (nothing was made) "
                            "themselves. Do not run either yourself."),
                    ("THEN", AGAIN % project.name)]
    if any(generate._in_flight(state, "clip:" + s["id"]) for s in sl.ai_shots()):
        return [("STAGE", "video: clips are still being made"),
                ("RUN", vg("resume", project)), ("TIME", "a few minutes; " + LONG_S),
                ("THEN", AGAIN % project.name)]
    rows = review_page.video_data(project, sl, state, True)["rows"]
    broken = [r for r in rows if r["error"]]
    if broken:
        return ([("STAGE", "video: %d clip(s) cannot be priced yet" % len(broken))]
                + [("NOTE", "%s: %s" % (r["shot"], r["error"])) for r in broken]
                + [("DO", "fix what each note names (skill vg-video-prompt or vg-video); a character identity "
                          "(vg character create) is paid at an unknown price: ask the human first"),
                   ("THEN", AGAIN % project.name)])
    approved = [r["shot"] for r in rows if r["status"] == "approved"]
    if approved:
        takes = state["approvals"]["video"]
        new = [s for s in approved if takes[s].get("new_take")]
        batches = [(approved if not new else [s for s in approved if s not in new], ""), (new, " --new-take")]
        run = [vg("video", project, " --shots %s%s" % (",".join(shots), flag)) for shots, flag in batches if shots]
        return [("STAGE", "video: approved and ready to make: %s" % ", ".join(approved)),
                ("RUN", " && ".join(run)),
                ("TIME", "about 3-6 minutes; " + LONG_S),
                ("THEN", "watch every clip it made (open the files), tell the human what you see, then "
                         + AGAIN % project.name)]
    todo = [r for r in rows if r["status"] == "not made"]
    if todo:
        pilot = not any(r["status"].startswith("made") for r in rows)
        pick = todo[:1] if pilot else todo
        total = sum(r["cost"] for r in pick)
        return ([("STAGE", "video: %s" % ("make one pilot clip first, to check the look and the price"
                                          if pilot else "the pilot is made; %d clip(s) to go" % len(todo)))]
                + _video_ask(project, [r["shot"] for r in pick], total, pilot))

    # 5. the final edit
    spec = review.edit_spec(project)
    name = spec.get("output") or "%s_v1.0.mp4" % (sl.data.get("project") or project.name)
    final = project.path / "99_Output" / name
    if not final.is_file():
        return [("STAGE", "edit: every clip is made; the final reel is not rendered"),
                ("RUN", vg("edit final", project)),
                ("TIME", "about 2-5 minutes; " + LONG_S),
                ("THEN", "watch it yourself, then " + AGAIN % project.name)]
    clips = ["clip:" + s["id"] for s in sl.ai_shots()]
    newer = max(_newest_file(project, state, clips), os.path.getmtime(str(project.path / review.EDIT_SPEC)))
    if newer > os.path.getmtime(str(final)):
        return [("STAGE", "edit: clips or the edit plan changed after %s was rendered" % project.rel(final)),
                ("WRITE", "a new `output` name in 6_Edit/Edit_Spec.json (next version, e.g. _v1.1); never "
                          "overwrite a delivered file"),
                ("THEN", AGAIN % project.name)]
    return [("DONE", "the reel is finished: %s" % project.rel(final)),
            ("ASK", "Send the human the file and ask what they think.")]


def show(project):
    for tag, text in steps(project):
        generate.say("%-6s %s" % (tag, text))
