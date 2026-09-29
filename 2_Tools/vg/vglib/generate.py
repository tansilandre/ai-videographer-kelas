"""Paid generation: images, identities, video.

Every paid request goes through `_submit` (or `_identity_call` for the synchronous Omni identity
endpoints), which runs this sequence:
  1. under the project lock: refuse if the target already has a task in flight, skip if another run
     already finished the same request, re-check the approval (video), check budget and balance,
     mark the approval used, and write a "submitting" row to the ledger;
  2. upload inputs and call the provider;
  3. record the taskId ("pending"), or "rejected" when the provider definitely refused, or
     "unknown" when the call may or may not have created a task (network error, crash).
An "unknown" or "submitting" row blocks that target until a human checks kie.ai and runs
`vg release` (nothing was created) or `vg adopt` (a task was created). That is what stops a retry
after a timeout from paying twice.
"""
import errno
import io
import math
import os
import random
import shlex
import subprocess
import sys
import time
import uuid

from providers import get_provider
from vglib import config, registry, review
from vglib.errors import ProviderError, Refused, UsageError, VgError
from vglib.project import Project, now_iso, sha256_file, sha256_json
from vglib.shotlist import Shotlist

POLL = {"image": (5, 15 * 60), "video": (10, 25 * 60), "mixed": (10, 25 * 60)}
SUBMIT_GAP_S = 0.6  # kie.ai allows 20 new requests per 10 s
POLL_ERROR_LIMIT = 3
IN_FLIGHT = ("submitting", "pending", "unknown")
DEFINITE_REJECTIONS = (400, 401, 402, 404, 422, 433, 455, 505)


def say(message=""):
    print(message)
    sys.stdout.flush()


def load(project, allow_errors=False):
    sl = Shotlist(project.shotlist(), project)
    errors, _ = sl.validate()
    if errors and not allow_errors:
        raise UsageError("Shotlist.json has %d error(s). Run `vg validate -p %s` and fix them first."
                         % (len(errors), project.name))
    return sl


class Session:
    """One command run: provider, budget guard, uploads."""

    def __init__(self, project, dry_run=False):
        self.project = project
        self.dry_run = dry_run
        self._provider = None
        self.balance = None
        self.budget = config.number("VG_BUDGET_PROJECT")
        self.max_call = config.number("VG_MAX_PER_CALL")

    @property
    def provider(self):
        return self.provider_for("kie")

    def provider_for(self, name):
        """The provider a model's registry entry names (uploads, balance and downloads use "kie")."""
        if not hasattr(self, "_providers"):
            self._providers = {}
        if name not in self._providers:
            self._providers[name] = get_provider(name)
        return self._providers[name]

    def guard(self, st, cost, label):
        """Budget and balance check. `st` is the state inside an open transaction."""
        if cost > self.max_call:
            raise Refused("%s costs %g credits, above VG_MAX_PER_CALL=%g. Ask the human whether to raise the "
                          "cap in .env; do not edit it yourself." % (label, cost, self.max_call))
        spent = Project.spent(st)
        if spent + cost > self.budget:
            raise Refused("%s would bring this project to %g credits, above VG_BUDGET_PROJECT=%g (already "
                          "committed: %g). Ask the human whether to raise the budget in .env; do not edit it "
                          "yourself." % (label, spent + cost, self.budget, spent))
        if self.balance is None:
            self.balance = self.provider.credits()
            st["balance"] = {"credits": self.balance, "at": now_iso()}
        if self.balance < max(cost, 1):
            raise Refused("%s needs %g credits but the balance is %g. Top up at kie.ai." % (label, cost, self.balance))
        self.balance -= cost

    def upload(self, path):
        sha = sha256_file(path)
        state = self.project.read_state()
        url = self.project.cached_upload(state, sha, self.provider.upload_ttl_s)
        if url:
            return url
        url = self.provider.upload(str(path), upload_path="vg/" + self.project.name)
        with self.project.transaction() as st:
            st["uploads"][sha] = {"url": url, "at": time.time(), "file": self.project.rel(path)}
        return url


def video_input(project, path):
    """A light JPEG copy of an image for video models (max 1080 px wide). kie.ai's workers fetch inputs
    from a slow temporary host; 6-8 MB 2K PNGs made Omni tasks fail with a 500 after minutes."""
    import shutil as _shutil
    import subprocess as _subprocess
    if path.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp") or not _shutil.which("ffmpeg"):
        return path
    folder = project.path / ".vg_cache" / "video_inputs"
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / ("%s_%s.jpg" % (path.stem, sha256_file(path)[:12]))
    if not dest.is_file():
        result = _subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vf",
                                  "scale='min(1080,iw)':-2", "-q:v", "3", str(dest)],
                                 stdout=_subprocess.PIPE, stderr=_subprocess.PIPE)
        if result.returncode != 0 or not dest.is_file():
            return path
    return dest


# ---------------------------------------------------------------------- ledger helpers

def _done(project, state, key, target):
    """The successful task that produced this exact request for this target, if its file still exists."""
    for task in reversed(state["tasks"]):
        if (task["target"] == target and task["state"] == "success"
                and key in (task.get("key"), task.get("base_key"))
                and task.get("path") and project.abs(task["path"]).is_file()):
            return task
    return None


def _in_flight(state, target):
    return [t for t in state["tasks"] if t["target"] == target and t["state"] in IN_FLIGHT]


def _resumable(state, key, target):
    for task in _in_flight(state, target):
        if task["state"] == "pending" and key in (task.get("key"), task.get("base_key")):
            return task
    return None


def _busy_message(project, target, tasks):
    task = tasks[-1]
    if task["state"] == "pending":
        return ("%s already has a task running (%s). Run `vg resume -p %s` first."
                % (target, task["task_id"], project.name))
    return ("%s has a task in state %r: the provider may or may not have accepted it. The human must check "
            "the kie.ai dashboard: if a task exists, `vg adopt -p %s --target %s --task-id <id>`; if nothing "
            "was created, `vg release -p %s --target %s`."
            % (target, task["state"], project.name, target, project.name, target))


def _record(job, extra=None):
    record = {
        "row": uuid.uuid4().hex, "key": job["key"], "base_key": job.get("base_key", job["key"]),
        "target": job["target"], "kind": job["kind"], "provider": job["provider"], "model": job["model"],
        "task_id": None, "state": "submitting", "estimate": job["cost"], "credits": None, "ext": job["ext"],
        "created": now_iso(), "path": None, "version": None, "fail": None,
    }
    record.update(extra or {})
    return record


def _update_row(project, row, restore_approval=None, **fields):
    with project.transaction() as st:
        for task in st["tasks"]:
            if task.get("row") == row:
                task.update(fields)
        if restore_approval:
            approval = st["approvals"]["video"].get(restore_approval)
            # only give back the approval this row actually consumed
            if approval and approval.get("claimed_row") == row:
                approval["used"] = False
                approval["claimed_row"] = None


def _submit(project, session, job, build_payload, claim=None, extra=None, approval_shot=None):
    """Claim, record, then call the provider. Returns the ledger record (state pending), or None when
    another run finished the same request in the meantime."""
    record = _record(job, extra)
    with project.transaction() as st:
        busy = _in_flight(st, job["target"])
        if busy:
            raise Refused(_busy_message(project, job["target"], busy))
        if job["key"] == job.get("base_key", job["key"]) and _done(project, st, job["key"], job["target"]):
            say("skip   %-28s finished by another run, no spend" % job["target"])
            return None
        if claim:
            claim(st)
            if approval_shot:
                st["approvals"]["video"][approval_shot]["claimed_row"] = record["row"]
        session.guard(st, job["cost"], job["target"])
        st["tasks"].append(record)
    try:
        payload = build_payload()
    except (VgError, OSError) as exc:
        _update_row(project, record["row"], approval_shot, state="rejected", fail="upload: %s" % exc)
        raise
    try:
        task_id = session.provider_for(job["provider"]).create_task(job["model"], payload)
    except ProviderError as exc:
        if exc.code in DEFINITE_REJECTIONS:
            _update_row(project, record["row"], approval_shot, state="rejected", fail=str(exc))
        else:
            _update_row(project, record["row"], state="unknown", fail=str(exc))
            say("UNKNOWN %-27s the request may have reached kie.ai. The human must check the dashboard "
                "before anything is retried." % job["target"])
        raise
    _update_row(project, record["row"], state="pending", task_id=task_id)
    record.update(state="pending", task_id=task_id)
    say("submit %-28s task %s (%g credits est.)" % (job["target"], task_id, job["cost"]))
    return record


def release(project, target):
    """Human-only escape hatch: the human checked kie.ai and nothing was created (or a pending task can
    never finish). Marks the rows abandoned; they stay counted in the budget at their estimate."""
    with project.transaction() as st:
        rows = [t for t in st["tasks"] if t["target"] == target and t["state"] in IN_FLIGHT]
        if not rows:
            raise UsageError("%s has no submitting, unknown or pending task" % target)
        for task in rows:
            task["released_from"] = task["state"]
            task["state"] = "abandoned"
            task["released"] = now_iso()
    say("released %d row(s) of %s. A new video take needs a new approval." % (len(rows), target))


def adopt(project, target, task_id):
    """Human-only: kie.ai shows a task was created for a submitting/unknown row; attach its id so
    `vg resume` downloads the result instead of anyone paying again."""
    with project.transaction() as st:
        rows = [t for t in st["tasks"] if t["target"] == target and t["state"] in ("submitting", "unknown")]
        if not rows:
            raise UsageError("%s has no submitting or unknown task to adopt" % target)
        rows[-1].update(state="pending", task_id=task_id, adopted=now_iso())
    say("adopted task %s for %s. Run `vg resume -p %s` to collect it." % (task_id, target, project.name))


# ---------------------------------------------------------------------- images

def _ref_path(project, ref, state):
    kind, value = ref
    if kind == "file":
        path = (project.path / value).resolve()
        try:
            path.relative_to(project.path.resolve())
        except ValueError:
            return None  # refs may not point outside the project folder
        return path if path.is_file() else None
    return project.selected(value, state)


def build_image_job(project, sl, target, state, model_id=None, resolution=None, allow_untested=False,
                    enforce_look=True):
    """`enforce_look=False` is for estimates only: storyboard/frame images are otherwise refused until
    the human has approved the look, and then carry the style frames as extra refs."""
    request = sl.image_request(target)
    kind = target.split(":", 1)[0]
    if kind in ("storyboard", "first", "last", "asset"):
        problem = review.look_problem(project, sl, state)
        if problem and enforce_look and kind != "asset":
            raise Refused("%s: %s. Generate the style frames (vg image -p %s --stage look), show them to the human "
                          "with the board, and run `vg approve look` only after their explicit 'approved'."
                          % (target, problem, project.name))
        if not problem:
            request["refs"] += [r for r in review.look_refs(sl, target) if r not in request["refs"]]
    spec = registry.get(model_id or sl.model_id("image"), "image", allow_untested)
    params = {
        "aspect_ratio": registry.cast_param(spec, "aspect_ratio", request["aspect_ratio"]),
        "resolution": registry.cast_param(spec, "resolution", resolution or request["resolution"]),
    }
    problems = registry.check_params(spec, params)
    if len(request["prompt"]) > spec.get("prompt_max", 20000):
        problems.append("prompt is %d characters, limit %d" % (len(request["prompt"]), spec["prompt_max"]))
    files, missing = [], []
    for ref in request["refs"]:
        path = _ref_path(project, ref, state)
        if path is None:
            missing.append(ref[1])
        else:
            files.append(path)
    variant = spec["variants"]["i2i" if request["refs"] else "t2i"]
    if len(request["refs"]) > variant.get("max_refs", 99):
        problems.append("%d refs, limit %d" % (len(request["refs"]), variant["max_refs"]))
    if problems:
        raise UsageError("%s: %s" % (target, "; ".join(problems)))
    key = None
    if not missing:
        key = sha256_json({
            "model": variant["model"], "prompt": request["prompt"], "params": params,
            "refs": [sha256_file(f) for f in files],
        })
    return {
        "kind": "image", "target": target, "provider": spec["provider"], "model": variant["model"],
        "prompt": request["prompt"], "params": params, "files": files, "missing": missing,
        "refs_field": variant.get("refs_field"), "key": key, "base_key": key,
        "cost": registry.price(spec, params), "ext": ".png",
    }


def run_images(project, targets, dry_run=False, new_take=False, model_id=None, resolution=None,
               allow_untested=False):
    sl = load(project)
    session = Session(project, dry_run)
    remaining = list(dict.fromkeys(targets))
    gated = [t for t in remaining if t.split(":", 1)[0] in ("storyboard", "first", "last")]
    look_gate = review.look_problem(project, sl, project.read_state()) if gated else None
    if look_gate and not dry_run:  # refuse before any dependency is paid for
        raise Refused("%s: %s. Generate the style frames (vg image -p %s --stage look), show them to the human "
                      "with the board, and run `vg approve look` only after their explicit 'approved'."
                      % (", ".join(gated), look_gate, project.name))
    planned = set()  # dry-run: targets that would be generated this run
    total = 0.0
    failed, stuck = [], []
    while remaining:
        state = project.read_state()
        ready, waiting = [], []
        for target in remaining:
            deps = [v for k, v in sl.image_request(target)["refs"] if k == "target"]
            if [d for d in deps if d in remaining]:
                waiting.append(target)
                continue
            unmet = [d for d in deps if d not in planned
                     and (project.selected(d, state) is None or _in_flight(state, d))]
            if unmet and dry_run:
                planned.update(unmet)  # show the run as if the earlier stage were done
            elif unmet:
                raise UsageError("%s needs %s generated first (generate them, or use --stage all)."
                                 % (target, ", ".join(unmet)))
            ready.append(target)
        if not ready:
            raise UsageError("Circular refs between: %s" % ", ".join(remaining))

        wave, wave_poll = [], []
        for target in ready:
            request = sl.image_request(target)
            if request.get("file"):  # a real photo: cropped and recorded, never sent to the image model
                _import_frame(project, target, request, state, dry_run, new_take)
                continue
            job = build_image_job(project, sl, target, state, model_id, resolution, allow_untested,
                                  enforce_look=not dry_run)
            if job["key"] and not new_take:
                done = _done(project, state, job["key"], target)
                if done:
                    say("skip   %-28s already done (v%s), no spend" % (target, done.get("version")))
                    continue
                pending = _resumable(state, job["key"], target)
                if pending:
                    say("resume %-28s task %s" % (target, pending["task_id"]))
                    if not dry_run:
                        wave_poll.append(pending)
                    continue
            if job["key"] and new_take:
                job["key"] = sha256_json([job["key"], "take", time.time()])
            if dry_run:
                planned.add(target)
                total += job["cost"]
                _print_image_dry(project, job)
                continue
            wave.append(job)

        try:
            for job in wave:
                def build(job=job):
                    payload = {"prompt": job["prompt"]}
                    payload.update(job["params"])
                    urls = [session.upload(f) for f in job["files"]]
                    if urls:
                        payload[job["refs_field"]] = urls
                    return payload
                record = _submit(project, session, job, build)
                if record:
                    wave_poll.append(record)
                time.sleep(SUBMIT_GAP_S)
        finally:
            if wave_poll:
                outcome = poll(project, session, wave_poll, "image")
                failed += outcome["failed"]
                stuck += outcome["pending"]
        if failed or stuck:
            if waiting:
                say("stop   %d dependent image(s) not built this run: %s"
                    % (len(waiting), ", ".join(waiting)))
            break
        remaining = waiting
    if dry_run:
        say("\nDry run: %d image(s), %g credits. Nothing was sent." % (len(planned), total))
        if look_gate:
            say("Gate: storyboard and frame images are refused until the look is approved (%s)." % look_gate)
    _summary(project)
    _raise_failures(project, failed)


def _import_frame(project, target, request, state, dry_run=False, new_take=False):
    """Record a real photo as a frame: crop a full-height window at the frame's aspect ratio, centred at
    `crop_x` (0 = left edge, 1 = right edge). No credits; a changed photo or crop makes a new version."""
    source = (project.path / request["file"]).resolve()
    if project.path.resolve() not in source.parents or not source.is_file():
        raise UsageError("%s: real photo %s not found inside the project" % (target, request["file"]))
    w, h = (float(x) for x in request["aspect_ratio"].split(":"))
    key = sha256_json({"import": sha256_file(source), "crop_x": request["crop_x"], "aspect": request["aspect_ratio"]})
    if not new_take and _done(project, state, key, target):
        say("skip   %-28s real photo already imported, no spend" % target)
        return
    if dry_run:
        say("would  %-28s import %s (crop_x %g), 0 credits" % (target, request["file"], request["crop_x"]))
        return
    version = project.next_version(target, ".png", state)
    out = project.output_path(target, version, ".png")
    window = "crop='trunc(min(iw,ih*%g/%g)/2)*2':'trunc(min(ih,iw*%g/%g)/2)*2':'(iw-ow)*%g':'(ih-oh)/2'" % (
        w, h, h, w, request["crop_x"])
    import subprocess
    done = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-vf", window, "-frames:v", "1", str(out)],
                          capture_output=True, text=True)
    if done.returncode != 0 or not out.is_file():
        raise UsageError("%s: could not crop %s: %s" % (target, request["file"], done.stderr.strip()[-300:]))
    rel = project.rel(out)
    with project.transaction() as st:
        st["tasks"].append({"row": uuid.uuid4().hex, "key": key, "base_key": key, "target": target, "kind": "image",
                            "provider": "local", "model": "real-photo-import", "task_id": None, "state": "success",
                            "estimate": 0, "credits": 0, "created": now_iso(), "done": now_iso(), "path": rel,
                            "version": version, "fail": None})
        Project.add_output(st, target, version, rel, key, sha=sha256_file(out))
    say("import %-28s %s from %s (crop_x %g), 0 credits" % (target, rel, request["file"], request["crop_x"]))


def _print_image_dry(project, job):
    say("would  %-28s %s %s %s  %g credits" % (
        job["target"], job["model"], job["params"]["aspect_ratio"], job["params"]["resolution"], job["cost"]))
    refs = [project.rel(f) for f in job["files"]] + ["(pending) " + m for m in job["missing"]]
    if refs:
        say("       refs: %s" % ", ".join(refs))
    say("       prompt: %s" % _clip(job["prompt"], 220))


def _clip(text, limit):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit - 3] + "..."


# ---------------------------------------------------------------------- polling

def poll(project, session, records, kind):
    """Poll until done or timeout. Returns {"failed": [...], "pending": [...]} (descriptions)."""
    interval, timeout = POLL[kind]
    start = time.time()
    open_tasks = {r["task_id"]: r for r in records if r.get("task_id")}
    errors = {}
    failed = []
    last_note = 0.0
    while open_tasks and time.time() - start < timeout:
        time.sleep(interval)
        for task_id, record in list(open_tasks.items()):
            try:
                info = session.provider_for(record.get("provider") or "kie").get_task(task_id)
                if info["state"] == "success":
                    _finish(project, session, record, info)
                    del open_tasks[task_id]
                elif info["state"] == "fail":
                    with project.transaction() as st:
                        for task in st["tasks"]:
                            if task["task_id"] == task_id:
                                task["state"] = "fail"
                                task["fail"] = "%s %s" % (info["fail_code"], info["fail_msg"])
                                task["credits"] = info["credits"]
                    say("FAILED %-28s %s %s" % (record["target"], info["fail_code"], info["fail_msg"]))
                    failed.append("%s (%s %s)" % (record["target"], info["fail_code"], info["fail_msg"]))
                    del open_tasks[task_id]
                errors.pop(task_id, None)
            except ProviderError as exc:
                errors[task_id] = errors.get(task_id, 0) + 1
                say("WARN   %-28s could not check or download task %s: %s" % (record["target"], task_id, exc))
                if errors[task_id] >= POLL_ERROR_LIMIT:
                    del open_tasks[task_id]  # stays pending in the ledger; `vg resume` tries again
        if open_tasks and time.time() - last_note > 60:
            last_note = time.time()
            say("...    waiting on %d task(s), %ds elapsed" % (len(open_tasks), int(time.time() - start)))
    state = project.read_state()
    still = [t for t in state["tasks"] if t.get("task_id") in {r.get("task_id") for r in records}
             and t["state"] == "pending"]
    for task in still:
        say("PENDING %-27s task %s not finished yet. Run `vg resume -p %s` later; do not re-submit."
            % (task["target"], task["task_id"], project.name))
    return {"failed": failed, "pending": [t["target"] for t in still]}


def _raise_failures(project, failed):
    if not failed:
        return
    video = [f for f in failed if f.startswith("clip:")]
    hint = ("Failed tasks are not retried automatically; look at the cause, then run the same command "
            "again to retry.")
    if video:
        hint += (" A failed video clip used up its approval: show the human the cost again, get a new yes, "
                 "and approve that shot again before retrying.")
    raise ProviderError("%d task(s) failed at the provider: %s. %s" % (len(failed), "; ".join(failed), hint))


def _finish(project, session, record, info):
    if not info["urls"]:
        raise ProviderError("Task %s succeeded but returned no result URL" % record["task_id"])
    kind_folder = project.output_path(record["target"], 1, record["ext"]).parent
    tmp = kind_folder / (".download-%s%s" % (record["task_id"], record["ext"]))
    session.provider.download(info["urls"][0], tmp)
    with project.transaction() as st:
        row = next((t for t in st["tasks"] if t["task_id"] == record["task_id"]), None)
        if row is not None and row["state"] == "success":
            tmp.unlink()  # another poller already recorded this task
            return
        version = project.next_version(record["target"], record["ext"], st)
        path = project.output_path(record["target"], version, record["ext"])
        os.replace(str(tmp), str(path))
        rel = project.rel(path)
        sha = sha256_file(path)
        if row is not None:
            row.update({"state": "success", "credits": info["credits"], "path": rel,
                        "version": version, "done": now_iso(), "result_url": info["urls"][0]})
        Project.add_output(st, record["target"], version, rel, record["key"], record["task_id"], sha)
    say("done   %-28s %s (%s credits)" % (record["target"], rel, info["credits"]))


def resume(project):
    state = project.read_state()
    stuck = [t for t in state["tasks"] if t["state"] in ("submitting", "unknown")]
    for task in stuck:
        say("CHECK  %-28s state %r since %s: may or may not exist on kie.ai. The human checks the dashboard: "
            "task exists -> `vg adopt -p %s --target %s --task-id <id>`; nothing created -> `vg release -p %s "
            "--target %s`." % (task["target"], task["state"], task["created"], project.name, task["target"],
                               project.name, task["target"]))
    pending = [t for t in state["tasks"] if t["state"] == "pending"]
    if not pending:
        say("No pending tasks.")
        return
    kinds = {t["kind"] for t in pending}
    outcome = poll(project, Session(project), pending, kinds.pop() if len(kinds) == 1 else "mixed")
    _summary(project)
    _raise_failures(project, outcome["failed"])


def _summary(project):
    state = project.read_state()
    say("project spend: %g credits committed (budget %g)" % (Project.spent(state), config.number("VG_BUDGET_PROJECT")))


# ---------------------------------------------------------------------- identity

def _identity_files(project, char, state):
    portrait = project.selected("asset:" + char["portrait"], state)
    if not portrait:
        raise UsageError("Generate asset:%s (the portrait of %s) first" % (char["portrait"], char["name"]))
    files = [portrait]
    if char.get("body"):
        body = project.selected("asset:" + char["body"], state)
        if not body:
            raise UsageError("Generate asset:%s (the body image of %s) first" % (char["body"], char["name"]))
        files.append(body)
    return files


def _voice_key(char):
    return sha256_json({"voice": char.get("voice")})


def _character_key(char, files, voice_id):
    # "input" marks how the images were sent: identities built from full-size PNGs made every
    # character-mode clip time out at kie.ai (2026-09-24); they are now sent as light JPEGs.
    return sha256_json({"description": char["description"], "files": [sha256_file(f) for f in files],
                        "voice": voice_id, "name": char["name"], "input": "jpeg-1080"})


def _current_identity(project, sl, name, state):
    """(character_id, voice_id) if the stored identity still matches the Shotlist and the portrait."""
    char = sl.characters.get(name)
    if not char:
        raise UsageError("No character %r in Shotlist.json" % name)
    stale = ("tell the human (identity creation is paid; kie.ai does not publish the price), then run "
             "`vg character create -p %s --name %s`" % (project.name, name))
    voice_id = None
    if char.get("voice"):
        voice = state["identities"].get("voice:" + name)
        if not voice:
            raise UsageError("%s has no voice identity yet: %s" % (name, stale))
        if voice.get("key") != _voice_key(char):
            raise UsageError("%s's voice changed in Shotlist.json since it was created: %s" % (name, stale))
        voice_id = voice["id"]
    ident = state["identities"].get("character:" + name)
    if not ident:
        raise UsageError("%s has no character identity yet: %s" % (name, stale))
    if ident.get("key") != _character_key(char, _identity_files(project, char, state), voice_id):
        raise UsageError("%s's identity is out of date (portrait, description or voice changed): %s" % (name, stale))
    return ident["id"], voice_id


def _identity_call(project, session, target, key, model, call):
    """Run a synchronous identity request with the same in-flight protection as _submit."""
    row = uuid.uuid4().hex
    with project.transaction() as st:
        busy = _in_flight(st, target)
        if busy:
            raise Refused(_busy_message(project, target, busy))
        session.guard(st, 0, target)
        st["tasks"].append({"row": row, "key": key, "base_key": key, "target": target, "kind": "identity",
                            "provider": "kie", "model": model, "task_id": None, "state": "submitting",
                            "estimate": 0, "credits": None, "created": now_iso(), "path": None,
                            "version": None, "fail": None})
    before = session.provider.credits()
    try:
        result_id = call()
    except ProviderError as exc:
        definite = exc.code in DEFINITE_REJECTIONS
        _update_row(project, row, state="rejected" if definite else "unknown", fail=str(exc))
        raise
    spent = max(0.0, round(before - session.provider.credits(), 2))
    _update_row(project, row, state="success", task_id=result_id, credits=spent, done=now_iso())
    return result_id, spent


def create_character(project, name, dry_run=False):
    sl = load(project)
    char = sl.characters.get(name)
    if not char:
        raise UsageError("No character %r in Shotlist.json" % name)
    spec = registry.get(sl.model_id("video"), "video", allow_untested=True)
    identity = spec.get("identity") or {}
    if not identity.get("character"):
        raise UsageError("%s has no character identity service; use frames mode instead" % spec["id"])
    session = Session(project, dry_run)
    state = project.read_state()
    files = _identity_files(project, char, state)

    voice_id = None
    voice = char.get("voice")
    if voice and identity.get("voice"):
        vkey = _voice_key(char)
        existing = state["identities"].get("voice:" + name)
        if existing and existing.get("key") == vkey:
            voice_id = existing["id"]
            say("skip   voice:%-22s already created (%s)" % (name, voice_id))
        elif dry_run:
            say("would  voice:%s  preset=%s name=%r" % (name, voice["preset"], voice["name"]))
            voice_id = "<new voice id>"
        else:
            voice_id, spent = _identity_call(
                project, session, "voice:" + name, vkey, "omni-audio",
                lambda: session.provider.create_voice(voice["preset"], voice["name"],
                                                      voice.get("description"), voice.get("example")))
            with project.transaction() as st:
                st["identities"]["voice:" + name] = {"id": voice_id, "key": vkey, "at": now_iso()}
            say("done   voice:%-22s %s (%g credits measured)" % (name, voice_id, spent))

    ckey = _character_key(char, files, voice_id)
    existing = state["identities"].get("character:" + name)
    if existing and existing.get("key") == ckey:
        say("skip   character:%-18s already created (%s)" % (name, existing["id"]))
        return
    if dry_run:
        say("would  character:%s  images=%s voice=%s" % (name, [project.rel(f) for f in files], voice_id))
        return
    urls = [session.upload(video_input(project, f)) for f in files]
    character_id, spent = _identity_call(
        project, session, "character:" + name, ckey, "omni-character",
        lambda: session.provider.create_character(char["description"], urls,
                                                  [voice_id] if voice_id else None, name))
    with project.transaction() as st:
        st["identities"]["character:" + name] = {"id": character_id, "key": ckey, "voice": voice_id,
                                                  "at": now_iso()}
    say("done   character:%-18s %s (%g credits measured)" % (name, character_id, spent))


# ---------------------------------------------------------------------- video

def video_params(sl, shot, spec, resolution=None):
    duration = sl.duration(shot, spec)
    params = {
        "aspect_ratio": registry.cast_param(spec, "aspect_ratio", sl.aspect_ratio()),
        "resolution": registry.cast_param(spec, "resolution",
                                          resolution or shot.get("resolution") or sl.video_resolution()),
        "duration": registry.cast_param(spec, "duration", duration),
    }
    # optional seed: per shot, else video_defaults.seed (only for models that accept one)
    seed = shot.get("seed", (sl.data.get("video_defaults") or {}).get("seed"))
    if seed is not None and "seed" in (spec.get("params") or {}):
        params["seed"] = registry.cast_param(spec, "seed", seed)
    return params


def build_video_job(project, sl, shot, state, spec, resolution=None):
    sid = shot["id"]
    mode = shot.get("mode")
    mode_spec = (spec.get("modes") or {}).get(mode)
    if mode_spec is None:
        raise UsageError("%s: %s does not support %s mode" % (sid, spec["id"], mode))
    if not (shot.get("video_prompt") or "").strip():
        raise UsageError("%s: video_prompt is empty; write it first (skill vg-video-prompt)" % sid)
    if mode == "frames" and not shot.get("first_frame"):
        raise UsageError("%s: frames mode needs first_frame in Shotlist.json" % sid)
    params = video_params(sl, shot, spec, resolution)
    problems = registry.check_params(spec, params)
    prompt = sl.video_prompt(shot)
    if len(prompt) > spec.get("prompt_max", 20000):
        problems.append("prompt is %d characters, limit %d" % (len(prompt), spec["prompt_max"]))
    if not registry.dialogue_fits(spec, shot.get("dialogue"), params["duration"]):
        problems.append("dialogue does not fit %ss" % params["duration"])

    # the images come from the same helper the visual review hashes, so they cannot disagree
    inputs = review.shot_inputs(project, sl, shot, state)
    missing = [label for label, path in inputs if path is None]
    if missing:
        raise UsageError("%s: generate these first (or fix the ref): %s" % (sid, ", ".join(missing)))
    paths = [path for _, path in inputs]
    files, ids, singles = {}, {}, set()
    if mode == "frames":
        first = paths[0]
        last = paths[1] if shot.get("last_frame") else None
        if mode_spec.get("first_frame"):
            files[mode_spec["first_frame"]] = [first]
            singles.add(mode_spec["first_frame"])
            if last:
                files[mode_spec["last_frame"]] = [last]
                singles.add(mode_spec["last_frame"])
        elif mode_spec.get("frames_list"):
            files[mode_spec["frames_list"]] = [first] + ([last] if last else [])
    elif mode == "character":
        characters, voices = [], []
        for name in shot.get("characters", []):
            character_id, voice_id = _current_identity(project, sl, name, state)
            characters.append(character_id)
            if voice_id:
                voices.append(voice_id)
        ids[mode_spec["characters"]] = characters
        if voices and mode_spec.get("voices"):
            ids[mode_spec["voices"]] = voices
        if paths and mode_spec.get("refs"):  # the anchor (planned first frame, else panel) + video_refs
            files[mode_spec["refs"]] = paths
    elif mode == "lipsync":  # the picture, and the stretch of the narration the presenter says
        files[mode_spec["image"]] = [paths[0]]
        files[mode_spec["audio"]] = [_lipsync_cut(project, shot, paths[1])]
        singles.update((mode_spec["image"], mode_spec["audio"]))
    elif paths and mode_spec.get("refs"):  # text mode: video_refs only
        files[mode_spec["refs"]] = paths

    sent = {f for f, v in list(files.items()) + list(ids.items()) if v}
    for field, banned in (spec.get("exclusive") or {}).items():
        clash = sent & set(banned) if field in sent else set()
        if clash:
            problems.append("%s cannot be sent with %s" % (field, ", ".join(sorted(clash))))
    for field, needed in (spec.get("requires") or {}).items():
        if field in sent and needed not in sent:
            problems.append("%s requires %s" % (field, needed))
    for field, limit in (spec.get("limits") or {}).items():
        count = len(files.get(field, [])) + len(ids.get(field, []))
        if count > limit:
            problems.append("%s has %d items, limit %d" % (field, count, limit))
    quota = spec.get("media_quota")
    if quota:
        used = sum(w * (len(files.get(f, [])) + len(ids.get(f, []))) for f, w in quota["weights"].items())
        # a character registered with a body image occupies two media slots
        if mode == "character":
            used += sum(1 for name in shot.get("characters", []) if (sl.characters.get(name) or {}).get("body"))
        if used > quota["limit"]:
            problems.append("media quota %d > %d" % (used, quota["limit"]))
    if problems:
        raise UsageError("%s: %s" % (sid, "; ".join(problems)))

    constants = mode_spec.get("set") or {}
    key = sha256_json({
        "model": spec["model"], "prompt": prompt, "params": params, "set": constants,
        "files": {f: [sha256_file(p) for p in paths] for f, paths in files.items()},
        "ids": ids,
    })
    return {
        "kind": "video", "target": "clip:" + sid, "shot": sid, "mode": mode, "provider": spec["provider"],
        "model": spec["model"], "prompt": prompt, "params": params, "files": files, "ids": ids,
        "singles": singles, "set": constants, "key": key, "base_key": key,
        "omit": tuple(spec.get("payload_omit") or ()),
        "cost": registry.price(spec, params), "ext": ".mp4",
    }


def _lipsync_cut(project, shot, source):
    """The narration window a lipsync shot says, as its own file (6_Edit/1_Audio/Lipsync_<shot>.mp3: MP3 at
    44.1 kHz stereo, the most widely accepted input; a 48 kHz mono WAV got a 500 from InfiniteTalk)."""
    window = shot["lipsync"]
    start, end = float(window["start"]), float(window["end"])
    dest = project.path / "6_Edit" / "1_Audio" / ("Lipsync_%s.mp3" % shot["id"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-af",
                             "atrim=start=%.3f:end=%.3f,asetpts=N/SR/TB" % (start, end), "-ar", "44100", "-ac", "2",
                             "-b:a", "192k", str(dest)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0 or not dest.is_file():
        raise UsageError("%s: could not cut the narration %.2f-%.2fs: %s"
                         % (shot["id"], start, end, result.stderr.decode("utf-8", "replace")[-200:]))
    return dest


def _select_shots(sl, shot_ids, all_shots):
    ai = sl.ai_shots()
    if all_shots:
        return ai
    if not shot_ids:
        raise UsageError("Pass --shots S01,S02 or --all")
    wanted = list(dict.fromkeys(s.strip() for s in shot_ids.split(",") if s.strip()))
    by_id = {s["id"]: s for s in ai}
    unknown = [s for s in wanted if s not in by_id]
    if unknown:
        raise UsageError("Not AI shots in Shotlist.json: %s" % ", ".join(unknown))
    return [by_id[s] for s in wanted]


def _gate_problem(project, approval, snapshot, cost, new_take):
    if not approval:
        return "not approved"
    if approval.get("project_path") and approval["project_path"] != str(project.path.resolve()):
        return "approval was made in another project folder (copied project); approve again here"
    if approval["snapshot"] != snapshot:
        return "changed since approval (frames, prompt, mode, duration or identity)"
    if approval.get("used"):
        return "approval already used; a new take needs a new approval"
    if new_take and not approval.get("new_take"):
        return "approval was not for a new take (approve with --new-take)"
    if cost > float(approval.get("estimate") or 0) + 1e-6:
        return "approved for %g credits but this costs %g" % (approval.get("estimate") or 0, cost)
    return None


def _open_tty():
    """The controlling terminal for reading and writing. Text-mode open('/dev/tty', 'r+') fails on a
    real tty (it is not seekable), so build the stream from an unbuffered file descriptor."""
    fd = os.open("/dev/tty", os.O_RDWR | getattr(os, "O_NOCTTY", 0))
    return io.TextIOWrapper(io.FileIO(fd, "r+"), line_buffering=True, write_through=True)


AGENT_SHELL_VARS = ("CODEBUDDY_TOOL_CALL_ID",)  # set in every command WorkBuddy's agent runs


def approval_mode():
    """terminal: the human types a code in their own terminal. page: the human clicks on the review page
    (`vg review`); the command line never approves. chat: the agent approves after the human's yes."""
    return (config.setting("VG_APPROVAL_MODE") or "terminal").lower()


def _human_confirm(total, count, command, via_page=False):
    _human_confirm_text("Approve %g credits for %d video shot(s)?" % (total, count), command, via_page)


def _human_confirm_text(question, command, via_page=False):
    """In terminal mode a human must type a random code; in page mode only a click on the review page
    (via_page) approves. Both are friction against accidental or casual approval, not a wall: an agent
    that drives a terminal or the page itself could do it. The hard limit is a dedicated kie.ai key with
    a total credit cap."""
    mode = approval_mode()
    if mode == "chat":
        return
    words = shlex.split(command.split("&&")[-1])
    project = words[words.index("-p") + 1] if "-p" in words[:-1] else "<project>"
    if mode == "page":
        if via_page:
            return
        raise Refused("VG_APPROVAL_MODE=page: the human approves by clicking on the review page, never on the "
                      "command line. Open it with `python3 2_Tools/vg/vg.py review -p %s --detach`, send the "
                      "human the link, and wait until they say they clicked; then run `vg next -p %s`."
                      % (project, project))
    if via_page:
        raise Refused("VG_APPROVAL_MODE=%s: approve in your own terminal, where you type the code it shows:\n  %s"
                      % (mode, command))
    if any(os.environ.get(var) for var in AGENT_SHELL_VARS):
        raise Refused("Approval must be typed by the human in their own terminal; this shell belongs to an "
                      "agent, so the code would be shown to it. Give the human this command to run in their "
                      "own terminal app:\n  " + command)
    try:
        tty = _open_tty()
    except OSError as exc:
        if exc.errno not in (errno.ENXIO, errno.ENOENT, errno.ENODEV, errno.EACCES, None):
            raise
        raise Refused("Approval must be typed by the human in a terminal (VG_APPROVAL_MODE=terminal). "
                      "Give the human this command to run in their own terminal; they type the code it shows. "
                      "Never run it through script, expect, a pty or any terminal you control:\n  " + command)
    code = "%04d" % random.SystemRandom().randint(0, 9999)
    try:
        tty.write("\n%s Type %s and press Enter to approve: " % (question, code))
        tty.flush()
        answer = tty.readline().strip()
    finally:
        tty.close()
    if answer != code:
        raise Refused("Code did not match. Nothing was approved.")


def shot_spec(sl, shot, allow_untested=False):
    return registry.get(sl.video_model_id(shot), "video", allow_untested)


def approve_video(project, shot_ids, all_shots, confirm, new_take=False, allow_untested=False, resolution=None,
                  via_page=False):
    sl = load(project)
    state = project.read_state()
    blocked = review.problems(project, sl, state)
    if blocked:
        raise Refused(review.gate_message(project, blocked))
    rows, total = [], 0.0
    for shot in _select_shots(sl, shot_ids, all_shots):
        spec = shot_spec(sl, shot, allow_untested)
        job = build_video_job(project, sl, shot, state, spec, resolution)
        if _in_flight(state, job["target"]):
            say("skip   %-6s a task is in flight; nothing to approve" % shot["id"])
            continue
        if _done(project, state, job["key"], job["target"]) and not new_take:
            say("skip   %-6s already generated; use --new-take to approve another take" % shot["id"])
            continue
        rows.append((shot["id"], job))
        total += job["cost"]
    if not rows:
        say("Nothing to approve.")
        return
    say("%-6s %-10s %-9s %s" % ("shot", "mode", "duration", "credits"))
    for sid, job in rows:
        say("%-6s %-10s %-9s %g" % (sid, job["mode"], "%ss" % job["params"]["duration"], job["cost"]))
    say("total  %g credits" % total)
    shots_arg = "--all" if all_shots else "--shots " + ",".join(sid for sid, _ in rows)
    command = "cd %s && python3 2_Tools/vg/vg.py approve video -p %s %s --confirm %g%s%s%s" % (
        shlex.quote(str(config.ROOT)), shlex.quote(project.name), shots_arg, total,
        " --new-take" if new_take else "", " --resolution %s" % resolution if resolution else "",
        " --allow-untested" if allow_untested else "")
    if confirm is None or not math.isfinite(float(confirm)) or abs(float(confirm) - total) > 1e-6:
        raise Refused("Not approved. --confirm must equal the total the human agreed to (%g here). "
                      "If the human agreed to a different number, stop and ask again." % total)
    _human_confirm(total, len(rows), command, via_page)
    before = {sid: state["approvals"]["video"].get(sid) for sid, _ in rows}
    with project.transaction() as st:
        written = 0
        for sid, job in rows:
            if (_in_flight(st, job["target"]) or (_done(project, st, job["key"], job["target"]) and not new_take)
                    or st["approvals"]["video"].get(sid) != before[sid]):
                say("skip   %-6s changed while waiting for the code; not approved" % sid)
                continue
            st["approvals"]["video"][sid] = {"snapshot": job["key"], "estimate": job["cost"], "new_take": new_take,
                                             "used": False, "claimed_row": None,
                                             "project_path": str(project.path.resolve()), "at": now_iso()}
            written += 1
    say("approved %d shot(s) for %g credits. Any change to these shots voids the approval." % (written, total))


def run_video(project, shot_ids, all_shots, dry_run=False, new_take=False, allow_untested=False, resolution=None):
    sl = load(project)
    session = Session(project, dry_run)
    state = project.read_state()
    jobs, refusals, resumes, total = [], [], [], 0.0
    visual_gate = review.problems(project, sl, state)
    for shot in _select_shots(sl, shot_ids, all_shots):
        spec = shot_spec(sl, shot, allow_untested)
        job = build_video_job(project, sl, shot, state, spec, resolution)
        base = job["key"]
        if not new_take:
            done = _done(project, state, base, job["target"])
            if done:
                say("skip   %-28s already done (v%s), no spend" % (job["target"], done.get("version")))
                continue
            pending = _resumable(state, base, job["target"])
            if pending:
                say("resume %-28s task %s" % (job["target"], pending["task_id"]))
                resumes.append(pending)
                continue
        busy = _in_flight(state, job["target"])
        if busy:
            refusals.append(_busy_message(project, job["target"], busy))
        problem = _gate_problem(project, state["approvals"]["video"].get(shot["id"]), base, job["cost"], new_take)
        if problem:
            refusals.append("%s: %s" % (shot["id"], problem))
        if new_take:
            job["key"] = sha256_json([base, "take", time.time()])
        jobs.append(job)
        total += job["cost"]

    if jobs and visual_gate:
        refusals.insert(0, "visual review: " + "; ".join(visual_gate))
    if dry_run:
        for job in jobs:
            _print_video_dry(project, job)
        if refusals:
            say("\nGate: %s" % "; ".join(refusals))
        say("\nDry run: %d clip(s), %g credits. Nothing was sent." % (len(jobs), total))
        return
    if jobs and visual_gate:
        raise Refused(review.gate_message(project, visual_gate))
    if refusals:
        raise Refused("Video gate closed, nothing was sent:\n  " + "\n  ".join(refusals) +
                      "\nShow `vg estimate -p %s --stage video` and the board to the human; only they "
                      "can approve." % project.name)

    records, outcome = [], {"failed": [], "pending": []}
    try:
        for job in jobs:
            def claim(st, job=job):
                blocked = review.problems(project, sl, st)  # images may have changed since the check above
                if blocked:
                    raise Refused(review.gate_message(project, blocked))
                approval = st["approvals"]["video"].get(job["shot"])
                problem = _gate_problem(project, approval, job["base_key"], job["cost"], new_take)
                if problem:
                    raise Refused("%s: %s" % (job["shot"], problem))
                approval["used"] = True

            def build(job=job):
                payload = {"prompt": job["prompt"]}
                payload.update({k: v for k, v in job["params"].items() if k not in job.get("omit", ())})
                payload.update(job["set"])
                for field, paths in job["files"].items():
                    urls = [session.upload(video_input(project, p)) for p in paths]
                    payload[field] = urls[0] if field in job["singles"] else urls
                for field, values in job["ids"].items():
                    payload[field] = values
                return payload

            record = _submit(project, session, job, build, claim,
                             {"shot": job["shot"], "mode": job["mode"]}, approval_shot=job["shot"])
            if record:
                records.append(record)
            time.sleep(SUBMIT_GAP_S)
    finally:
        if resumes or records:
            outcome = poll(project, session, resumes + records, "video")
    _summary(project)
    _raise_failures(project, outcome["failed"])


def _print_video_dry(project, job):
    say("would  %-28s %s mode=%s %s %ss %s  %g credits" % (
        job["target"], job["model"], job["mode"], job["params"]["aspect_ratio"], job["params"]["duration"],
        job["params"]["resolution"], job["cost"]))
    for field, paths in job["files"].items():
        say("       %s: %s" % (field, ", ".join(project.rel(p) for p in paths)))
    for field, values in job["ids"].items():
        say("       %s: %s" % (field, ", ".join(values)))
    say("       prompt: %s" % _clip(job["prompt"], 260))


# ---------------------------------------------------------------------- estimate and status

def estimate(project, stage="all", allow_untested=True):
    sl = load(project, allow_errors=True)
    state = project.read_state()
    lines, total = [], 0.0
    if stage in ("images", "all"):
        spec = registry.get(sl.model_id("image"), "image", allow_untested)
        for target in sl.image_targets("all"):
            if _in_flight(state, target):
                lines.append(("image", target, 0, "in flight (already committed)"))
                continue
            try:
                if sl.image_request(target).get("file"):
                    continue  # a real photo: imported for free
            except UsageError:
                pass
            try:
                job = build_image_job(project, sl, target, state, allow_untested=allow_untested, enforce_look=False)
                needed = not (job["key"] and _done(project, state, job["key"], target))
                cost = job["cost"]
            except UsageError:
                needed, cost = True, registry.price(spec, {"resolution": sl.image_resolution()})
            if needed:
                lines.append(("image", target, cost, ""))
                total += cost
        for shot in sl.ai_shots():
            if not (shot.get("storyboard") or {}).get("prompt"):
                cost = registry.price(spec, {"resolution": sl.image_resolution()})
                lines.append(("image", "storyboard:%s" % shot["id"], cost, "planned (prompt not written yet)"))
                total += cost
    if stage in ("video", "all"):
        needs_identity = set()
        for shot in sl.ai_shots():
            note = ""
            spec = shot_spec(sl, shot, allow_untested)
            if _in_flight(state, "clip:" + shot["id"]):
                lines.append(("video", "clip:%s" % shot["id"], 0, "in flight (already committed)"))
                continue
            try:
                job = build_video_job(project, sl, shot, state, spec)
                needed = not _done(project, state, job["key"], job["target"])
                cost, duration = job["cost"], job["params"]["duration"]
            except UsageError as exc:
                try:
                    params = video_params(sl, shot, spec)
                    cost, duration = registry.price(spec, params), params["duration"]
                except UsageError:
                    cost, duration = 0.0, "?"
                needed, note = True, "not ready: %s" % exc
                if "identity" in str(exc):
                    needs_identity.update(shot.get("characters", []))
            if needed:
                lines.append(("video", "clip:%s (%s, %ss)" % (shot["id"], shot.get("mode"), duration), cost, note))
                total += cost
        for name in sorted(needs_identity):
            lines.append(("ident", "character:%s (+ voice)" % name, 0, "cost unknown until created; tell the human"))
    for kind, label, cost, note in lines:
        say("%-6s %-40s %6g  %s" % (kind, label, cost, note))
    say("total  %g credits still to spend (%s). Committed so far: %g."
        % (total, stage, Project.spent(state)))
    return total


def status(project):
    sl = load(project, allow_errors=True)
    state = project.read_state()
    targets = sl.image_targets("all") + ["clip:" + s["id"] for s in sl.ai_shots()]
    say("%-30s %-10s %-8s %s" % ("target", "state", "credits", "file"))
    for target in targets:
        entry = project.selected_entry(target, state)
        flight = _in_flight(state, target)
        failed = [t for t in state["tasks"] if t["target"] == target and t["state"] == "fail"]
        credits = sum(float(t.get("credits") or 0) for t in state["tasks"]
                      if t["target"] == target and t["state"] in ("success", "fail"))
        if flight:
            label = flight[-1]["state"]
        elif entry:
            label = "v%d" % entry["v"]
        elif failed:
            label = "failed"
        else:
            label = "-"
        say("%-30s %-10s %-8g %s" % (target, label, credits, entry["path"] if entry else ""))
    for key, ident in sorted(state["identities"].items()):
        say("%-30s %-10s %-8s %s" % (key, "created", "", ident["id"]))
    for name, ok, text in review.gate_status(project, sl, state):
        say("%s gate: %s" % (name, text))
    approvals = state["approvals"]["video"]
    if approvals:
        say("video approvals: %s" % ", ".join("%s%s" % (k, " (used)" if v.get("used") else "")
                                                for k, v in sorted(approvals.items())))
    say("committed %g credits of %g budget" % (Project.spent(state), config.number("VG_BUDGET_PROJECT")))
