#!/usr/bin/env bash
# Satu perintah untuk menyiapkan AI Videographer di Mac. Aman dijalankan ulang kapan saja.
#   bash setup.sh
# Bisa dijalankan sendiri di Terminal, atau oleh AI di WorkBuddy. Kunci API tidak pernah lewat chat:
# setup membuka halaman lokal (vg setup) tempat kamu menempelnya sendiri.
set -uo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"
ok()   { echo "✓ $1"; }
stop() { echo; echo "→ $1"; echo; echo "Setelah itu, jalankan lagi: bash setup.sh"; exit 1; }

echo "== AI Videographer · setup"
[ "$(uname)" = "Darwin" ] || stop "Butuh Mac: caption dan grafis digambar dengan Swift buatan Apple."

# 1. Xcode Command Line Tools: git, python3, swiftc
if ! xcode-select -p >/dev/null 2>&1; then
  xcode-select --install >/dev/null 2>&1 || true
  stop "Sebuah jendela dari Apple muncul: klik Install dan tunggu sampai selesai (5–15 menit)."
fi
ok "Xcode Command Line Tools"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null \
  || stop "Python 3.9 atau lebih baru dibutuhkan. Buka app Terminal dan jalankan: brew install python"
ok "Python $(python3 -c 'import platform; print(platform.python_version())')"

# 2. FFmpeg (video dan audio), lewat Homebrew
BREW="$(command -v brew || true)"
[ -z "$BREW" ] && [ -x /opt/homebrew/bin/brew ] && BREW=/opt/homebrew/bin/brew
[ -z "$BREW" ] && [ -x /usr/local/bin/brew ] && BREW=/usr/local/bin/brew
if ! command -v ffmpeg >/dev/null 2>&1; then
  if [ -n "$BREW" ]; then
    echo "… memasang FFmpeg (beberapa menit)"
    "$BREW" install ffmpeg >/dev/null || stop "FFmpeg gagal dipasang. Buka app Terminal dan jalankan: brew install ffmpeg"
  else
    stop "Homebrew belum ada, dan pemasangannya butuh password Mac-mu. Buka app Terminal, tempel baris ini, tekan Enter, lalu ketik password (hurufnya memang tidak terlihat):
   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"
   Jalankan juga perintah 'Next steps' yang ditampilkan di akhir."
  fi
fi
ok "FFmpeg"

# 3. Skill, file .env, dan Expert WorkBuddy
if [ -d "/Applications/WorkBuddy AI.app" ] && [ -d "${WORKBUDDY_CONFIG_DIR:-$HOME/.workbuddy-ai}" ]; then
  OUT="$(bash 2_Tools/workbuddy/install_workbuddy.sh --quiet 2>&1)" || { echo "$OUT"; stop "Expert WorkBuddy gagal dipasang: baca pesan di atas."; }
  ok "Expert AI Videographer terpasang di WorkBuddy"
else
  bash install.sh >/dev/null 2>&1 || true
  ok "Skill terpasang (WorkBuddy belum ada: agent lain seperti Claude Code juga bisa dipakai)"
fi
[ -f .env ] || stop "File .env belum ada. Jalankan: bash install.sh"
ok "File .env"

# 4. Kunci API: lewat halaman lokal, tidak pernah lewat chat
if python3 -c 'import sys; sys.path.insert(0, "2_Tools/vg"); from vglib import config; sys.exit(0 if config.api_key("kie") else 1)' >/dev/null 2>&1; then
  ok "Kunci kie.ai sudah ada"
  NEED_KEYS=0
else
  NEED_KEYS=1
  python3 2_Tools/vg/vg.py setup --detach | head -1
fi

echo
echo "== Tinggal ini:"
n=1
if [ "$NEED_KEYS" = 1 ]; then
  echo "$n. Di halaman setup yang terbuka di browser: tempel kunci kie.ai (dan OpenRouter), klik Simpan."; n=$((n+1))
fi
echo "$n. Tutup WorkBuddy (Cmd+Q), lalu buka lagi."; n=$((n+1))
echo "$n. Pilih folder kerja ini: $ROOT"; n=$((n+1))
echo "$n. Pilih Expert 'AI Videographer' dan model glm-5.3-flash, lalu bilang: Buat video baru."
