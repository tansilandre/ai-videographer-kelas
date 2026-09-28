"""A video project folder: its plan (Shotlist.json, agent-owned) and its state (project.json, tool-owned).

project.json holds facts only: uploads, generated outputs and their versions, the task ledger with
credits, identities, and approvals. Every write goes through `transaction()`, which locks the file,
re-reads it, and writes it back atomically.
"""
import contextlib
import datetime
import hashlib
import json
import os
import re
import time
from pathlib import Path

from vglib import config
from vglib.errors import UsageError

try:
    import fcntl
except ImportError:  # Windows: no advisory lock, single-process use assumed
    fcntl = None

STATE_VERSION = 1

TARGET_KINDS = ("look", "asset", "storyboard", "first", "last", "clip")
FOLDERS = {
    "look": "2_References",
    "asset": "2_References",
    "storyboard": "3_Storyboard",
    "first": "4_Frames",
    "last": "4_Frames",
    "clip": "5_Clips",
}


def now_iso():
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def parse_target(target):
    if ":" not in target:
        raise UsageError("Target %r needs a kind prefix: %s" % (target, ", ".join(k + ":<id>" for k in TARGET_KINDS)))
    kind, ident = target.split(":", 1)
    if kind not in TARGET_KINDS or not ident:
        raise UsageError("Unknown target %r. Kinds: %s" % (target, ", ".join(TARGET_KINDS)))
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9_-]*$", ident):  # the id becomes a file name
        raise UsageError("Target %r: ids may use only letters, digits, _ and -" % target)
    return kind, ident


def target_filename(target, version, ext):
    kind, ident = parse_target(target)
    stem = {
        "look": ident,
        "asset": ident,
        "storyboard": "SB_" + ident,
        "first": "Frame_%s_First" % ident,
        "last": "Frame_%s_Last" % ident,
        "clip": "Clip_" + ident,
    }[kind]
    return "%s_v%d%s" % (stem, version, ext)


def resolve(project_arg=None):
    """Find the project folder from -p (name or path) or from the current directory."""
    if project_arg:
        def is_project(folder):
            return (folder / "1_Script").is_dir() or (folder / "project.json").is_file()
        for candidate in (Path(project_arg), config.PROJECTS_DIR / project_arg):
            if is_project(candidate):
                return Project(candidate.resolve())
        pattern = re.compile(r"^\d{4}-\d{2}-\d{2}_" + re.escape(project_arg) + "$")
        matches = [p for p in sorted(config.PROJECTS_DIR.glob("*")) if pattern.match(p.name) and is_project(p)] \
            if config.PROJECTS_DIR.is_dir() else []
        if len(matches) > 1:
            raise UsageError("%r matches several projects: %s. Pass the full folder name."
                             % (project_arg, ", ".join(p.name for p in matches)))
        if matches:
            return Project(matches[0].resolve())
        raise UsageError("No project %r under %s" % (project_arg, config.PROJECTS_DIR))
    here = Path.cwd().resolve()
    for folder in [here] + list(here.parents):
        if (folder / "project.json").is_file():
            return Project(folder)
    raise UsageError("No project given. Pass -p <project folder name> (see 5_Projects/).")


class Project:
    def __init__(self, path):
        self.path = Path(path)
        self.name = self.path.name
        self.shotlist_path = self.path / "1_Script" / "Shotlist.json"
        self.state_path = self.path / "project.json"
        self._lock_path = self.path / ".project.lock"

    # ------------------------------------------------------------------ plan

    def shotlist(self):
        if not self.shotlist_path.is_file():
            raise UsageError("Missing %s. Write the shot list first (skill vg-scene)." % self.rel(self.shotlist_path))
        try:
            return json.loads(self.shotlist_path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise UsageError("Shotlist.json is not valid JSON: %s" % exc)

    # ------------------------------------------------------------------ state

    def empty_state(self):
        return {
            "version": STATE_VERSION,
            "project": self.name,
            "created": now_iso(),
            "uploads": {},
            "outputs": {},
            "tasks": [],
            "identities": {},
            "approvals": {"video": {}},  # plus "look" and "visuals" once the human approves them
            "animatics": [],
            "balance": None,
        }

    def read_state(self):
        if not self.state_path.is_file():
            return self.empty_state()
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        base = self.empty_state()
        for key, value in base.items():
            state.setdefault(key, value)
        state["approvals"].setdefault("video", {})
        return state

    def _write_state(self, state):
        tmp = self.state_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(str(tmp), str(self.state_path))

    @contextlib.contextmanager
    def transaction(self):
        handle = open(self._lock_path, "a+")
        try:
            if fcntl:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            state = self.read_state()
            yield state
            self._write_state(state)
        finally:
            if fcntl:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            handle.close()

    # ------------------------------------------------------------------ helpers

    def rel(self, path):
        try:
            return str(Path(path).resolve().relative_to(self.path))
        except ValueError:
            return str(path)

    def abs(self, rel_path):
        return self.path / rel_path

    def selected(self, target, state=None):
        """Path of the selected version of a target, or None."""
        state = state or self.read_state()
        entry = state["outputs"].get(target)
        if not entry:
            return None
        for version in entry["versions"]:
            if version["v"] == entry.get("selected"):
                path = self.abs(version["path"])
                return path if path.is_file() else None
        return None

    def selected_entry(self, target, state=None):
        state = state or self.read_state()
        entry = state["outputs"].get(target)
        if not entry:
            return None
        for version in entry["versions"]:
            if version["v"] == entry.get("selected"):
                return version
        return None

    def next_version(self, target, ext, state):
        entry = state["outputs"].get(target) or {"versions": []}
        version = max([v["v"] for v in entry["versions"]] + [0]) + 1
        kind, _ = parse_target(target)
        folder = self.abs(FOLDERS[kind])
        while (folder / target_filename(target, version, ext)).exists():
            version += 1
        return version

    def output_path(self, target, version, ext):
        kind, _ = parse_target(target)
        folder = self.abs(FOLDERS[kind])
        folder.mkdir(parents=True, exist_ok=True)
        return folder / target_filename(target, version, ext)

    @staticmethod
    def add_output(state, target, version, rel_path, key, task_id=None, sha=None):
        entry = state["outputs"].setdefault(target, {"versions": [], "selected": None})
        entry["versions"].append({
            "v": version, "path": rel_path, "key": key, "task_id": task_id,
            "sha256": sha, "at": now_iso(),
        })
        entry["selected"] = version

    @staticmethod
    def find_task(state, key, states=("success", "pending")):
        for task in reversed(state["tasks"]):
            if task["key"] == key and task["state"] in states:
                return task
        return None

    @staticmethod
    def spent(state):
        """Credits committed: actual where known (also for failed tasks that were charged),
        the estimate for anything still in flight or of unknown outcome."""
        total = 0.0
        for task in state["tasks"]:
            if task["state"] in ("success", "fail"):
                if task.get("credits") is not None:
                    total += float(task["credits"])
                elif task["state"] == "success":
                    total += float(task.get("estimate") or 0)
            elif task["state"] in ("pending", "submitting", "unknown", "abandoned"):
                # abandoned rows stay counted: a released task may still have been charged
                total += float(task.get("estimate") or 0)
        return total

    def cached_upload(self, state, sha, ttl_s):
        entry = state["uploads"].get(sha)
        if entry and time.time() - entry["at"] < ttl_s:
            return entry["url"]
        return None


def slugify(text):
    """Keep the caller's casing (e.g. AI_vs_Asli); only replace separators and odd characters."""
    return re.sub(r"[^A-Za-z0-9]+", "_", text.strip()).strip("_")
