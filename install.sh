#!/usr/bin/env bash
# AI Videographer installer. Safe to run again.
#   bash install.sh            link skills into this workspace for Claude Code, Codex/Cursor, WorkBuddy
#   bash install.sh --global   also link them into your user-level skill folders
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"

echo "== checks"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' \
  || { echo "Python 3.9+ is required"; exit 1; }
echo "python3 $(python3 -c 'import platform; print(platform.python_version())')"
command -v ffmpeg >/dev/null || echo "WARN ffmpeg missing: brew install ffmpeg (needed for the edit stage)"
command -v swiftc >/dev/null || echo "WARN swiftc missing: xcode-select --install (macOS; captions and graphics in the edit)"

echo "== .env"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "created .env from .env.example: the human adds KIE_API_KEY and OPENROUTER_API_KEY (agents never edit .env)"
else
  echo ".env exists (contents left untouched)"
fi
chmod 600 .env

link_dir() {  # link_dir <target folder> <link path>
  local target="$1" link="$2"
  mkdir -p "$(dirname "$link")"
  if [ -L "$link" ] && [ "$(readlink "$link")" = "$target" ]; then echo "ok     $link"; return; fi
  if [ -L "$link" ]; then echo "repoint $link (was $(readlink "$link"))"; rm "$link"; fi
  if [ -e "$link" ]; then echo "skip $link (exists and is not a link)"; return; fi
  ln -s "$target" "$link"
  echo "linked $link"
}

echo "== skills (workspace)"
link_dir "../1_Skills" ".claude/skills"      # Claude Code
link_dir "../1_Skills" ".agents/skills"      # Codex, Cursor, Gemini CLI
link_dir "../1_Skills" ".workbuddy/skills"   # WorkBuddy project skills
link_dir "../1_Skills" ".codebuddy/skills"   # CodeBuddy

if [ "${1:-}" = "--global" ]; then
  echo "== skills (user level)"
  for base in "$HOME/.claude/skills" "$HOME/.agents/skills" "$HOME/.workbuddy/skills" "$HOME/.workbuddy-ai/skills"; do
    case "$base" in
      *workbuddy*) [ -d "$(dirname "$base")" ] || continue ;;
    esac
    mkdir -p "$base"
    for skill in "$ROOT"/1_Skills/vg-*; do
      link_dir "$skill" "$base/$(basename "$skill")"
    done
  done
  echo "Global skills point at this workspace ($ROOT). Restart your agent to load them."
fi

echo "== doctor"
python3 2_Tools/vg/vg.py doctor || true
