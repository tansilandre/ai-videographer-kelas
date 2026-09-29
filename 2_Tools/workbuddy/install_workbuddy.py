#!/usr/bin/env python3
"""Install the AI Videographer skills and the WorkBuddy expert. Safe to run again.

    python 2_Tools/workbuddy/install_workbuddy.py [--quiet]

setup.ps1 calls this on Windows (on a Mac, setup.sh uses install_workbuddy.sh). It links 1_Skills into the
workspace skill folders, creates .env from .env.example, copies the expert into WorkBuddy's settings folder
and registers it the way WorkBuddy's own register_expert.py does (one entry in marketplace.json).

Exit codes: 0 done, 1 failed, 3 skills done but no WorkBuddy settings folder (open WorkBuddy once, sign in).
"""
import filecmp
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERT = "ai-videographer"
SRC = ROOT / "2_Tools" / "workbuddy" / "expert" / EXPERT
SKILLS = ROOT / "1_Skills"
SKILL_LINKS = (".claude/skills", ".agents/skills", ".workbuddy/skills", ".codebuddy/skills")
COPY_MARK = ".vg-copy"


def say(message):
    print(message, flush=True)


def config_dir():
    """WorkBuddy's settings folder: the app sets WORKBUDDY_CONFIG_DIR in its agent shell."""
    env = os.environ.get("WORKBUDDY_CONFIG_DIR", "").strip()
    if env and Path(env).is_dir():
        return Path(env)
    for name in (".workbuddy-ai", ".workbuddy"):
        path = Path.home() / name
        if path.is_dir():
            return path
    return None


def _points_at(link, target):
    try:
        os.readlink(str(link))  # a symlink, or a junction on Windows
    except (OSError, ValueError, AttributeError):
        return None
    return os.path.normcase(os.path.realpath(str(link))) == os.path.normcase(os.path.realpath(str(target)))


def _remove_link(link):
    try:
        os.unlink(str(link))
    except OSError:
        os.rmdir(str(link))  # a directory junction


def link_skills(link):
    """Point `link` at 1_Skills: a symlink, else a junction (Windows, no admin needed), else a copy."""
    link.parent.mkdir(parents=True, exist_ok=True)
    state = _points_at(link, SKILLS)
    if state:
        return "ok"
    if state is False:
        _remove_link(link)
    elif link.exists():
        if (link / COPY_MARK).is_file():
            shutil.rmtree(str(link))
        else:
            return "skip (exists and is not a link)"
    try:
        os.symlink(str(SKILLS), str(link), target_is_directory=True)
        return "linked"
    except (OSError, NotImplementedError):
        pass
    if os.name == "nt":
        done = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(SKILLS)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if done.returncode == 0:
            return "linked (junction)"
    shutil.copytree(str(SKILLS), str(link))
    (link / COPY_MARK).write_text("Copied by install_workbuddy.py. Run setup again to refresh it.\n", encoding="utf-8")
    return "copied"


def env_file():
    env = ROOT / ".env"
    if env.exists():
        return ".env exists (contents left untouched)"
    shutil.copyfile(str(ROOT / ".env.example"), str(env))
    try:
        os.chmod(str(env), 0o600)
    except OSError:
        pass
    return "created .env from .env.example (the human pastes the keys on the setup page)"


def _same_tree(a, b):
    cmp = filecmp.dircmp(str(a), str(b), ignore=[".created-by-session", "__pycache__", ".DS_Store"])
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False
    return all(_same_tree(Path(a) / d, Path(b) / d) for d in cmp.common_dirs)


def register(market, dest):
    manifest_path = market / ".codebuddy-plugin" / "marketplace.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {"name": "my-experts", "description": "my-experts marketplace (auto-generated)", "plugins": []}
    meta = json.loads((dest / ".codebuddy-plugin" / "plugin.json").read_text(encoding="utf-8"))
    entry = {"name": meta.get("name", dest.name), "source": "./plugins/" + dest.name,
             "description": meta.get("description", "")}
    plugins = [p for p in manifest.get("plugins", [])
               if p.get("name") != entry["name"] and p.get("source") != entry["source"]]
    manifest["plugins"] = plugins + [entry]
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest_path


def install_expert(cfg):
    version = json.loads((SRC / ".codebuddy-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    market = cfg / "plugins" / "marketplaces" / "my-experts"
    dest = market / "plugins" / EXPERT
    cached = cfg / "plugins" / "cache" / "my-experts" / EXPERT / version
    if cached.is_dir() and not _same_tree(SRC, cached):
        say("note   WorkBuddy caches experts by version and %s is already cached with other files:" % version)
        say("       raise \"version\" in %s, then run this again" % (SRC / ".codebuddy-plugin" / "plugin.json"))
    (market / "plugins").mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(str(dest))
    shutil.copytree(str(SRC), str(dest), ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
    say("copied %s" % dest)
    say("registered %s in %s" % (EXPERT, register(market, dest)))
    return version


def main(argv):
    quiet = "--quiet" in argv
    say("== skills")
    for folder in SKILL_LINKS:
        say("%-18s %s" % (link_skills(ROOT / folder), folder))
    say("== .env")
    say(env_file())
    say("== expert")
    cfg = config_dir()
    if cfg is None:
        say("note   no WorkBuddy settings folder yet: open WorkBuddy once and sign in, then run setup again")
        return 3
    version = install_expert(cfg)
    say("ok     expert %s %s in %s" % (EXPERT, version, cfg))
    if not quiet:
        say("== next")
        say("1. Quit WorkBuddy completely and open it again.")
        say("2. Open this folder as the workspace: %s" % ROOT)
        say("3. Pick the expert AI Videographer and the model glm-5.3-flash.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
