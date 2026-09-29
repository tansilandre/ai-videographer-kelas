"""Command-line interface. See 1_Skills/vg-director/references/cli.md for the user guide."""
import argparse
import datetime
import json
import os
import platform
import shutil
import subprocess
import sys

from vglib import config, generate, registry
from vglib.errors import ProviderError, Refused, UsageError, VgError
from vglib.project import Project, resolve, slugify
from vglib.shotlist import Shotlist

say = generate.say


class Parser(argparse.ArgumentParser):
    """Usage errors exit 1, so exit code 2 only ever means a safety refusal."""

    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write("error: %s\n" % message)
        sys.exit(1)


def cmd_doctor(args):
    ok = True

    def line(good, label, detail=""):
        nonlocal ok
        ok = ok and good is not False
        mark = {True: "ok  ", False: "FAIL", None: "warn"}[good]
        say("%s %-22s %s" % (mark, label, detail))

    line(sys.version_info >= (3, 9), "python", platform.python_version())
    for tool in ("ffmpeg", "ffprobe"):
        line(bool(shutil.which(tool)), tool, shutil.which(tool) or "missing: brew install ffmpeg")
    if shutil.which("ffmpeg"):
        filters = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, universal_newlines=True).stdout
        has_ass = " subtitles " in filters or " ass " in filters
        line(True if has_ass else None, "ffmpeg libass",
             "yes" if has_ass else "no (only needed for burned-in subtitles; see vg-setup)")
    # captions and graphics: the Swift renderer (CoreGraphics) on macOS, else its Python + Pillow port
    from vglib import finish
    pillow = finish.pillow_version()
    if sys.platform == "darwin":
        swiftc = shutil.which("swiftc")
        line(True if swiftc else None, "swiftc", swiftc or (
            "missing: xcode-select --install (captions and graphics use python + Pillow %s instead)" % pillow
            if pillow else "missing: xcode-select --install, or python3 -m pip install pillow (needed for "
            "captions and graphics in the edit)"))
    else:
        line(True if pillow else None, "overlay renderer", "python + Pillow %s" % pillow if pillow else
             "Pillow missing: python -m pip install pillow (needed for captions and graphics in the edit)")
    try:
        from vglib import audio
        audio.key()
        line(True, "OPENROUTER_API_KEY", "set (value hidden)")
    except UsageError:
        line(None, "OPENROUTER_API_KEY", "missing (only needed for `vg audio voice` and `vg audio music`)")
    line(config.ENV_FILE.is_file() or None, ".env", str(config.ENV_FILE) if config.ENV_FILE.is_file()
         else "missing: cp .env.example .env")
    try:
        config.api_key("kie")
        line(True, "KIE_API_KEY", "set (value hidden)")
        from providers import get_provider
        balance = get_provider("kie").credits()
        line(True, "kie.ai balance", "%g credits" % balance)
    except VgError as exc:
        line(False, "kie.ai", str(exc))
    line(True, "budget", "VG_BUDGET_PROJECT=%s  VG_MAX_PER_CALL=%s"
         % (config.setting("VG_BUDGET_PROJECT"), config.setting("VG_MAX_PER_CALL")))
    for kind in ("image", "video"):
        model_id = config.setting("VG_%s_MODEL" % kind.upper())
        try:
            spec = registry.get(model_id, kind, allow_untested=True)
            line(True, "%s model" % kind, "%s (%s)" % (model_id, spec.get("status")))
        except UsageError as exc:
            line(False, "%s model" % kind, str(exc))
    mode = (config.setting("VG_APPROVAL_MODE") or "terminal").lower()
    line(True if mode in ("page", "terminal") else (None if mode == "chat" else False), "approval mode",
         {"page": "page (the human clicks Approve on the review page)",
          "terminal": "terminal (the human types a code in their own terminal)",
          "chat": "chat: an agent may run `vg approve` itself; for agent apps and small models set "
                  "VG_APPROVAL_MODE=page in .env"}.get(mode, "%r is not terminal, page or chat" % mode))
    for agent, folder in (("Claude Code", ".claude/skills"), ("WorkBuddy", ".codebuddy/skills")):
        skills = config.ROOT / folder
        linked = (skills / "vg-director" / "SKILL.md").is_file()
        fix = "run setup.ps1" if os.name == "nt" else "run install.sh"
        line(True if linked else None, "skills (%s)" % agent, str(skills) if linked else fix)
    if os.name != "nt" and config.ENV_FILE.is_file() and config.ENV_FILE.stat().st_mode & 0o077:
        line(None, ".env permissions", "readable by other users: chmod 600 .env")
    return 0 if ok else 1


def cmd_credits(args):
    from providers import get_provider
    say("%g" % get_provider("kie").credits())
    return 0


def cmd_models(args):
    for model_id, spec in sorted(registry.load_models().items()):
        say("%-24s %-6s %-12s %s" % (model_id, spec["kind"], spec.get("status"), spec.get("provider")))
    return 0


def cmd_new(args):
    slug = slugify(args.slug)
    name = "%s_%s" % (datetime.date.today().isoformat(), slug)
    path = config.PROJECTS_DIR / name
    if path.exists():
        raise UsageError("%s already exists" % path)
    if not config.TEMPLATE_DIR.is_dir():
        raise UsageError("Template missing: %s" % config.TEMPLATE_DIR)
    shutil.copytree(str(config.TEMPLATE_DIR), str(path))
    shotlist = path / "1_Script" / "Shotlist.json"
    data = json.loads(shotlist.read_text(encoding="utf-8"))
    data["project"] = slug
    if args.client:
        data["client"] = args.client
    shotlist.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    project = Project(path)
    with project.transaction():
        pass
    say("created %s" % path.relative_to(config.ROOT))
    return 0


def cmd_validate(args):
    project = resolve(args.project)
    sl = Shotlist(project.shotlist(), project)
    errors, warnings = sl.validate()
    for todo in sl.todos:
        say("todo  %s" % todo)
    for warning in warnings:
        say("warn  %s" % warning)
    for error in errors:
        say("error %s" % error)
    ai = sl.ai_shots()
    say("%s: %d assets, %d shots (%d AI), %d error(s), %d warning(s), %d todo(s)"
        % ("INVALID" if errors else "valid", len(sl.assets), len(sl.shots), len(ai), len(errors), len(warnings),
           len(sl.todos)))
    return 1 if errors else 0


def cmd_status(args):
    generate.status(resolve(args.project))
    return 0


def cmd_estimate(args):
    generate.estimate(resolve(args.project), args.stage)
    return 0


def cmd_setup(args):
    from vglib import setup_page
    if args.stop:
        setup_page.stop_detached()
    elif args.detach:
        setup_page.detach(port=args.port, open_browser=not args.no_open)
    else:
        setup_page.serve(port=args.port, open_browser=not args.no_open)
    return 0


def cmd_next(args):
    from vglib import next_step
    next_step.show(resolve(args.project))
    return 0


def cmd_board(args):
    from vglib import board
    path = board.build(resolve(args.project))
    say("board %s" % path)
    return 0


def cmd_review(args):
    from vglib import review_page
    project = resolve(args.project)
    if args.summary:
        for line in review_page.summary(project):
            say(line)
        return 0
    if args.stop:
        review_page.stop_detached(project)
        return 0
    if args.detach:
        review_page.detach(project, port=args.port, open_browser=not args.no_open)
        return 0
    try:
        review_page.serve(project, port=args.port, open_browser=not args.no_open)
    except KeyboardInterrupt:
        say("\nReview page stopped.")
        for line in review_page.summary(project):
            say(line)
        return 130
    return 0


def cmd_upload(args):
    project = resolve(args.project)
    session = generate.Session(project)
    say(session.upload(project.path / args.file if not os.path.isabs(args.file) else args.file))
    return 0


def cmd_image(args):
    project = resolve(args.project)
    sl = Shotlist(project.shotlist(), project)
    targets = list(args.target or [])
    if args.stage:
        targets += sl.image_targets(args.stage)
    if not targets and args.stage:
        say("Nothing to generate at stage %s (e.g. every first frame reuses its storyboard panel)." % args.stage)
        return 0
    if not targets:
        raise UsageError("Pass --target <kind:id> (repeatable) or --stage look|refs|storyboard|frames|all")
    generate.run_images(project, targets, dry_run=args.dry_run, new_take=args.new_take, model_id=args.model,
                        resolution=args.resolution, allow_untested=args.allow_untested)
    return 0


def cmd_select(args):
    project = resolve(args.project)
    with project.transaction() as st:
        entry = st["outputs"].get(args.target)
        if not entry or args.version not in [v["v"] for v in entry["versions"]]:
            raise UsageError("%s has no version %s" % (args.target, args.version))
        entry["selected"] = args.version
    say("%s -> v%d" % (args.target, args.version))
    return 0


def cmd_character(args):
    generate.create_character(resolve(args.project), args.name, dry_run=args.dry_run)
    return 0


def cmd_approve(args):
    from vglib import review
    if args.stage == "look":
        review.approve_look(resolve(args.project))
    elif args.stage == "visuals":
        review.approve_visuals(resolve(args.project))
    else:
        generate.approve_video(resolve(args.project), args.shots, args.all, args.confirm, new_take=args.new_take,
                               allow_untested=args.allow_untested, resolution=args.resolution)
    return 0


def cmd_video(args):
    generate.run_video(resolve(args.project), args.shots, args.all, dry_run=args.dry_run, new_take=args.new_take,
                       allow_untested=args.allow_untested, resolution=args.resolution)
    return 0


def cmd_release(args):
    generate.release(resolve(args.project), args.target)
    return 0


def cmd_adopt(args):
    generate.adopt(resolve(args.project), args.target, args.task_id)
    return 0


def cmd_resume(args):
    generate.resume(resolve(args.project))
    return 0


def cmd_edit(args):
    if args.action == "final":
        from vglib import finish
        finish.final(resolve(args.project), draft=args.draft)
    elif args.action == "animatic":
        from vglib import finish
        finish.animatic(resolve(args.project))
    else:
        from vglib import edit
        edit.roughcut(resolve(args.project))
    return 0


def cmd_audio(args):
    from vglib import audio
    project = resolve(args.project)
    if args.action == "voice":
        if args.text_file:
            path = project.path / args.text_file
            if not path.is_file():
                raise UsageError("%s not found inside the project" % args.text_file)
            text = path.read_text(encoding="utf-8")
        else:
            text = args.text or ""
        voices = [v.strip() for v in (args.voices or ",".join(audio.VOICES)).split(",") if v.strip()]
        audio.voice(project, text, voices, args.style or "A warm, natural Indonesian voice-over for a short "
                    "social video, conversational, not a newsreader.", args.name)
    elif args.action == "music":
        if args.prompt_file:
            path = project.path / args.prompt_file
            if not path.is_file():
                raise UsageError("%s not found inside the project" % args.prompt_file)
            prompt = path.read_text(encoding="utf-8")
        else:
            prompt = args.prompt or ""
        if not args.label:
            raise UsageError("--label is required, e.g. --label Quiz_Pop")
        audio.music(project, prompt, args.label, max(1, min(3, args.takes)))
    elif args.action == "sfx":
        audio.sfx(project)
    else:
        if not args.file:
            raise UsageError("--file is required, e.g. --file 6_Edit/1_Audio/Music_Take_Quiz_Pop_v1.mp3")
        path = project.path / args.file
        if not path.is_file():
            raise UsageError("%s not found inside the project" % args.file)
        points = audio.curve(path, args.step)
        for t, db in points:
            say("%6.2fs %6.1f dB %s" % (t, db, "#" * max(0, int((db + 60) / 2))))
        drop = audio.find_drop(audio.curve(path, 0.1))
        if drop is None:
            say("drop   none found (the track is too short)")
        else:
            say("drop   at about %.2fs (set music.at = reveal time - this)" % drop)
    return 0


def build_parser():
    parser = Parser(prog="vg", description="AI Videographer tool. Run from the workspace root.")
    sub = parser.add_subparsers(dest="command")

    def add(name, func, help_text, project=True):
        p = sub.add_parser(name, help=help_text, description=help_text)
        if project:
            p.add_argument("-p", "--project", help="project folder name under 5_Projects/ or a path")
        p.set_defaults(func=func)
        return p

    add("doctor", cmd_doctor, "check tools, .env, key and balance", project=False)
    p = add("setup", cmd_setup, "open a local page where the human pastes their API keys into .env (never into "
            "the chat); it checks the kie.ai key and ends after one save", project=False)
    p.add_argument("--port", type=int, default=0)
    p.add_argument("--no-open", action="store_true", help="print the URL instead of opening the browser")
    p.add_argument("--detach", action="store_true", help="start the page in its own process and return at once")
    p.add_argument("--stop", action="store_true", help="stop a page started with --detach")
    add("credits", cmd_credits, "print the kie.ai credit balance", project=False)
    add("models", cmd_models, "list models in the registry", project=False)
    p = add("new", cmd_new, "create a project from the template", project=False)
    p.add_argument("slug", help="e.g. Acme_Launch")
    p.add_argument("--client")
    add("validate", cmd_validate, "check Shotlist.json")
    add("next", cmd_next, "the one next step for this project: the command to run, the file to write, or "
        "what to ask the human (start here)")
    add("status", cmd_status, "show every target, version and spend")
    p = add("estimate", cmd_estimate, "credit cost of what is still missing")
    p.add_argument("--stage", choices=["images", "video", "all"], default="all")
    add("board", cmd_board, "rebuild the HTML review board")
    p = add("review", cmd_review, "open the local review page: the human looks at the look, the sheets and the "
            "reel, switches takes, writes change notes and approves by clicking (blocks until they click Done)")
    p.add_argument("--port", type=int, default=0, help="default: any free port")
    p.add_argument("--no-open", action="store_true", help="print the URL instead of opening the browser")
    p.add_argument("--detach", action="store_true", help="start the page in its own process and return at once "
                   "(agent apps whose commands must end); it runs until the human clicks Done")
    p.add_argument("--summary", action="store_true", help="print the gates, the human's notes and the next "
                   "step without opening the page")
    p.add_argument("--stop", action="store_true", help="stop a page started with --detach")
    p = add("upload", cmd_upload, "upload a file and print its URL")
    p.add_argument("file")

    p = add("image", cmd_image, "generate images (paid, no approval needed)")
    p.add_argument("--target", action="append",
                   help="look:<id> | asset:<id> | storyboard:<shot> | first:<shot> | last:<shot>")
    p.add_argument("--stage", choices=["look", "refs", "storyboard", "frames", "all"])
    p.add_argument("--new-take", action="store_true", help="re-roll as a new version")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--model")
    p.add_argument("--resolution")
    p.add_argument("--allow-untested", action="store_true")

    p = add("select", cmd_select, "choose which version of a target later steps use")
    p.add_argument("--target", required=True)
    p.add_argument("--version", type=int, required=True)

    p = add("character", cmd_character, "create voice + character identity (Gemini Omni; paid, price not "
            "published, measured afterwards; tell the human first)")
    p.add_argument("action", choices=["create"])
    p.add_argument("--name", required=True)
    p.add_argument("--dry-run", action="store_true")

    p = add("approve", cmd_approve, "record the human's approval: look (style frames), visuals (the whole reel "
            "as images, after the animatic), or video (credit spend)")
    p.add_argument("stage", choices=["look", "visuals", "video"])
    p.add_argument("--shots")
    p.add_argument("--all", action="store_true")
    p.add_argument("--confirm", type=float, help="must equal the total credit estimate")
    p.add_argument("--new-take", action="store_true", help="approve re-rolling shots that already have a clip")
    p.add_argument("--resolution")
    p.add_argument("--allow-untested", action="store_true")

    p = add("video", cmd_video, "generate approved video clips (paid, gated)")
    p.add_argument("--shots")
    p.add_argument("--all", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--new-take", action="store_true")
    p.add_argument("--resolution")
    p.add_argument("--allow-untested", action="store_true")

    add("resume", cmd_resume, "poll pending tasks and download finished results")
    p = add("release", cmd_release, "HUMAN ONLY, after checking kie.ai showed nothing was created: "
            "unblock a target stuck in submitting/unknown/pending")
    p.add_argument("--target", required=True)
    p = add("adopt", cmd_adopt, "HUMAN ONLY, after kie.ai showed a task was created: attach its task id "
            "to a submitting/unknown row so `vg resume` downloads it")
    p.add_argument("--target", required=True)
    p.add_argument("--task-id", required=True)
    p = add("audio", cmd_audio, "sound first: narration takes (voice), music takes (music), sound effects "
            "(sfx), or a track's loudness and drop (curve). Voice and music are paid via OpenRouter (cents)")
    p.add_argument("action", choices=["voice", "music", "sfx", "curve"])
    p.add_argument("--text", help="voice: the narration text")
    p.add_argument("--text-file", help="voice: a text file inside the project, e.g. 1_Script/Narration.txt")
    p.add_argument("--voices", help="voice: comma list, default Callirrhoe,Leda,Laomedeia,Aoede,Zephyr,Sulafat")
    p.add_argument("--style", help="voice: the direction (who speaks, to whom, pace, mood), in English")
    p.add_argument("--name", default="Narration", help="voice: file name start, default Narration")
    p.add_argument("--prompt", help="music: the music prompt")
    p.add_argument("--prompt-file", help="music: a text file inside the project with the prompt")
    p.add_argument("--label", help="music: a short name for the take, e.g. Quiz_Pop")
    p.add_argument("--takes", type=int, default=1, help="music: 1 to 3 takes")
    p.add_argument("--file", help="curve: an audio file inside the project")
    p.add_argument("--step", type=float, default=0.5, help="curve: seconds per line")
    p = add("edit", cmd_edit, "local edit steps (animatic: the reel as stills for the visual review)")
    p.add_argument("action", choices=["animatic", "roughcut", "final"])
    p.add_argument("--draft", action="store_true", help="final only: write a numbered draft to 6_Edit/ instead of 99_Output/")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 1
    try:
        return args.func(args) or 0
    except Refused as exc:
        say("REFUSED: %s" % exc)
        return exc.exit_code
    except ProviderError as exc:
        say("PROVIDER ERROR: %s" % exc)
        return exc.exit_code
    except UsageError as exc:
        say("ERROR: %s" % exc)
        return exc.exit_code
    except KeyboardInterrupt:
        say("\nInterrupted. Run `vg status` and `vg resume`; a task marked submitting may or may not "
            "exist on kie.ai, so check the dashboard before releasing it.")
        return 130
