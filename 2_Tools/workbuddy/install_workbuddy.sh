#!/usr/bin/env bash
# Install the AI Videographer expert into WorkBuddy (macOS). Safe to run again.
#   bash 2_Tools/workbuddy/install_workbuddy.sh               expert + workspace skills
#   bash 2_Tools/workbuddy/install_workbuddy.sh --add-models  also add GLM-5.3-Flash and MiniMax-M3.1-Flash-Preview
#                                                             as custom models through your own gateway key (only
#                                                             needed off WorkBuddy's credits: glm-5.3-flash is built in)
#   bash 2_Tools/workbuddy/install_workbuddy.sh --quiet       no closing instructions (setup.sh prints its own)
# Most people run `bash setup.sh` instead, which calls this. Then restart WorkBuddy, open this folder as the
# workspace, pick the expert and the model.
set -euo pipefail
cd "$(dirname "$0")/../.."
ROOT="$(pwd)"
EXPERT="ai-videographer"
SRC="$ROOT/2_Tools/workbuddy/expert/$EXPERT"
APP="/Applications/WorkBuddy AI.app"
CFG="${WORKBUDDY_CONFIG_DIR:-$HOME/.workbuddy-ai}"
MARKET="$CFG/plugins/marketplaces/my-experts"
SCRIPTS="$APP/Contents/Resources/app.asar.unpacked/resources/plugins/workbuddy-builtin/skills/expert-manager/scripts"

echo "== checks"
[ -d "$APP" ] || { echo "WorkBuddy is not installed in /Applications. Get it from https://www.workbuddy.ai"; exit 1; }
[ -d "$CFG" ] || { echo "No WorkBuddy settings folder at $CFG yet: open WorkBuddy once and sign in, then run this again"; exit 1; }
VERSION="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$SRC/.codebuddy-plugin/plugin.json")"
echo "WorkBuddy $(defaults read "$APP/Contents/Info" CFBundleShortVersionString 2>/dev/null || echo '?'), settings $CFG, expert $EXPERT $VERSION"

echo "== workspace (skills, .env)"
bash "$ROOT/install.sh" >/dev/null || true
[ -e "$ROOT/.codebuddy/skills/vg-director/SKILL.md" ] && echo "ok     .codebuddy/skills (WorkBuddy reads the vg skills here)" \
  || { echo "FAIL   .codebuddy/skills is not linked: run bash install.sh"; exit 1; }

echo "== expert"
DEST="$MARKET/plugins/$EXPERT"
CACHED="$CFG/plugins/cache/my-experts/$EXPERT/$VERSION"
if [ -d "$CACHED" ] && ! diff -rq -x .created-by-session "$SRC" "$CACHED" >/dev/null 2>&1; then
  echo "note   WorkBuddy caches experts by version and $VERSION is already cached with other files:"
  echo "       raise \"version\" in $SRC/.codebuddy-plugin/plugin.json, then run this again"
fi
mkdir -p "$MARKET/plugins"
rm -rf "$DEST"
cp -R "$SRC" "$DEST"
echo "copied $DEST"
if [ -f "$SCRIPTS/register_expert.py" ]; then
  WORKBUDDY_CONFIG_DIR="$CFG" python3 "$SCRIPTS/register_expert.py" "$DEST" --marketplace-dir "$MARKET" | tail -3
  WORKBUDDY_CONFIG_DIR="$CFG" python3 "$SCRIPTS/validate_expert.py" "$DEST" | tail -4
else  # the app moved its scripts: register it the way the app does (one entry in marketplace.json)
  python3 - "$MARKET" "$EXPERT" <<'PY'
import json, sys
from pathlib import Path
market, name = Path(sys.argv[1]), sys.argv[2]
path = market / ".codebuddy-plugin" / "marketplace.json"
path.parent.mkdir(parents=True, exist_ok=True)
data = json.loads(path.read_text()) if path.is_file() else {"name": "my-experts", "plugins": []}
meta = json.loads((market / "plugins" / name / ".codebuddy-plugin" / "plugin.json").read_text())
data["plugins"] = [p for p in data.get("plugins", []) if p.get("name") != name]
data["plugins"].append({"name": name, "source": "./plugins/" + name, "description": meta["description"]})
path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
print("registered", name, "in", path)
PY
fi

if [ "${1:-}" = "--quiet" ]; then
  exit 0
fi

if [ "${1:-}" = "--add-models" ]; then
  echo "== models"
  MODELS="$CFG/models.json"
  read -r -p "OpenAI-compatible URL [https://ai.sumopod.com/v1/chat/completions]: " URL
  URL="${URL:-https://ai.sumopod.com/v1/chat/completions}"
  read -r -s -p "API key for that URL (hidden): " KEY; echo
  [ -n "$KEY" ] || { echo "no key given: models not added"; exit 1; }
  [ -f "$MODELS" ] && cp "$MODELS" "$MODELS.bak" && chmod 600 "$MODELS.bak"
  KEY="$KEY" URL="$URL" python3 - "$MODELS" <<'PY'
import json, os, sys
from pathlib import Path
path = Path(sys.argv[1])
data = json.loads(path.read_text()) if path.is_file() else []
models = data["models"] if isinstance(data, dict) else data
for model_id in ("glm-5.3-flash", "MiniMax-M3.1-Flash-Preview"):
    models[:] = [m for m in models if m.get("id") != model_id]
    models.append({"id": model_id, "name": model_id, "vendor": "Custom", "url": os.environ["URL"],
                   "apiKey": os.environ["KEY"], "supportsToolCall": True, "supportsImages": True,
                   "supportsReasoning": True, "useCustomProtocol": False})
    print("added model", model_id)
path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
os.chmod(path, 0o600)
PY
fi

echo "== next"
echo "1. Quit WorkBuddy (Cmd+Q) and open it again."
echo "2. Open this folder as the workspace: $ROOT"
echo "3. Expert Center > My Experts > AI Videographer. Pick the model glm-5.3-flash (built into WorkBuddy)."
echo "4. Paste your API keys on the setup page (it also sets approvals to clicks): python3 2_Tools/vg/vg.py setup"
python3 "$ROOT/2_Tools/vg/vg.py" doctor | /usr/bin/grep -E "approval mode|skills \(WorkBuddy\)|FAIL" || true
