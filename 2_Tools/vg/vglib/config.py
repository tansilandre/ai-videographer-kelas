"""Paths and settings. Settings come from the process environment first, then the workspace .env.

The .env file is parsed, never sourced or printed.
"""
import math
import os
from pathlib import Path

from vglib.errors import UsageError

ROOT = Path(__file__).resolve().parents[3]
VG_DIR = ROOT / "2_Tools" / "vg"
MODELS_DIR = VG_DIR / "models"
PROJECTS_DIR = ROOT / "5_Projects"
TEMPLATE_DIR = ROOT / "3_Templates" / "Project"
ENV_FILE = ROOT / ".env"

DEFAULTS = {
    "VG_IMAGE_MODEL": "gpt-image-2",
    "VG_VIDEO_MODEL": "gemini-omni-flash-1-1",
    "VG_BUDGET_PROJECT": "800",
    "VG_MAX_PER_CALL": "250",
    "VG_APPROVAL_MODE": "terminal",
}

# Safety settings come only from .env (or the defaults above). The process environment is ignored
# for them, so a command-line prefix such as `VG_BUDGET_PROJECT=99999 vg ...` cannot override them.
FILE_FIRST = ("VG_BUDGET_PROJECT", "VG_MAX_PER_CALL", "VG_APPROVAL_MODE")

_env_cache = None


def _parse_env_file(path):
    values = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        values[key.strip()] = value
    return values


def env_file_values():
    global _env_cache
    if _env_cache is None:
        _env_cache = _parse_env_file(ENV_FILE)
    return _env_cache


def setting(name, default=None):
    if name in FILE_FIRST:
        return env_file_values().get(name) or DEFAULTS.get(name, default)
    value = os.environ.get(name)
    if value:
        return value
    value = env_file_values().get(name)
    if value:
        return value
    return DEFAULTS.get(name, default)


def number(name):
    raw = setting(name)
    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise UsageError("%s must be a number, got %r" % (name, raw))
    if not math.isfinite(value) or value < 0:
        raise UsageError("%s must be a finite number >= 0, got %r" % (name, raw))
    return value


def api_key(provider):
    name = {"kie": "KIE_API_KEY"}.get(provider, provider.upper() + "_API_KEY")
    key = setting(name)
    if not key or key.startswith("your-") or key.startswith("<"):
        if ENV_FILE.is_file():
            raise UsageError("%s is empty. Open .env in the workspace root and set %s=<your key>." % (name, name))
        raise UsageError("%s is not set. Run `bash install.sh` (it creates .env), then set %s in .env."
                         % (name, name))
    return key
