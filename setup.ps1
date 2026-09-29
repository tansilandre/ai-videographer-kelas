# Satu perintah untuk menyiapkan AI Videographer di Windows. Aman dijalankan ulang kapan saja.
#   powershell -ExecutionPolicy Bypass -File setup.ps1
# Bisa dijalankan sendiri di PowerShell, atau oleh AI di WorkBuddy. Kunci API tidak pernah lewat chat:
# setup membuka halaman lokal (vg setup) tempat kamu menempelnya sendiri.
# Di Mac, pakai: bash setup.sh
$ErrorActionPreference = 'Continue'
Set-Location -LiteralPath $PSScriptRoot
$Root = (Get-Location).Path

function Ok([string]$Message) { Write-Host "OK  $Message" }

function Stop-Setup([string]$Message) {
    Write-Host ""
    Write-Host "-> $Message"
    Write-Host ""
    Write-Host "Setelah itu, jalankan lagi: powershell -ExecutionPolicy Bypass -File setup.ps1"
    exit 1
}

function Update-SessionPath {
    $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $user = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$machine;$user;$env:LOCALAPPDATA\Microsoft\WinGet\Links"
}

function Find-Python {
    $candidates = @()
    foreach ($name in @('python', 'py')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { $candidates += $cmd.Source }
    }
    $candidates += Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe" -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending | ForEach-Object { $_.FullName }
    foreach ($exe in $candidates) {
        $pyArgs = @('-c', 'import sys; print(sys.executable if sys.version_info >= (3, 9) else "")')
        if ((Split-Path $exe -Leaf) -eq 'py.exe') { $pyArgs = @('-3') + $pyArgs }
        $out = & $exe @pyArgs 2>$null
        if ($LASTEXITCODE -eq 0 -and $out) {
            $path = ("$out" -split "`n")[0].Trim()
            if ($path) { return $path }
        }
    }
    return $null
}

function Test-Winget { return [bool](Get-Command winget -ErrorAction SilentlyContinue) }

function Install-Winget([string]$Id, [string[]]$Extra) {
    & winget install -e --id $Id --source winget --silent --accept-package-agreements --accept-source-agreements @Extra
}

Write-Host "== AI Videographer - setup (Windows)"

# 1. Python 3.9 atau lebih baru
$py = Find-Python
if (-not $py) {
    if (-not (Test-Winget)) {
        Stop-Setup "Python belum ada, dan winget tidak ditemukan. Pasang Python dari https://www.python.org/downloads/ dan centang 'Add python.exe to PATH'."
    }
    Write-Host "... memasang Python 3.12 (beberapa menit)"
    Install-Winget 'Python.Python.3.12' @('--scope', 'user', '--override', '/quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 InstallLauncherAllUsers=0 Include_test=0')
    Update-SessionPath
    $py = Find-Python
    if (-not $py) {
        Install-Winget 'Python.Python.3.12' @()
        Update-SessionPath
        $py = Find-Python
    }
    if (-not $py) {
        Stop-Setup "Python gagal dipasang. Pasang dari https://www.python.org/downloads/ dan centang 'Add python.exe to PATH'."
    }
}
$pyVersion = & $py -c "import platform; print(platform.python_version())"
Ok "Python $pyVersion"

# 2. FFmpeg (video dan audio)
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) { Update-SessionPath }
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    if (-not (Test-Winget)) {
        Stop-Setup "FFmpeg belum ada, dan winget tidak ditemukan. Pasang winget (App Installer) dari Microsoft Store, lalu jalankan setup lagi."
    }
    Write-Host "... memasang FFmpeg (beberapa menit)"
    Install-Winget 'Gyan.FFmpeg' @()
    Update-SessionPath
    if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
        $bin = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter ffmpeg.exe -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($bin) {
            $dir = $bin.DirectoryName
            $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
            if (-not $userPath) { $userPath = '' }
            if ($userPath -notlike "*$dir*") {
                [Environment]::SetEnvironmentVariable('Path', ($userPath.TrimEnd(';') + ';' + $dir), 'User')
            }
            $env:Path += ";$dir"
        }
    }
    if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
        Stop-Setup "FFmpeg gagal dipasang. Buka PowerShell dan jalankan: winget install -e --id Gyan.FFmpeg"
    }
}
Ok "FFmpeg"

# 3. Pillow: menggambar caption dan grafis
& $py -c "import PIL" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "... memasang Pillow"
    & $py -m pip install --user --quiet --disable-pip-version-check pillow
    & $py -c "import PIL" 2>$null
    if ($LASTEXITCODE -ne 0) { Stop-Setup "Pillow gagal dipasang. Jalankan: python -m pip install --user pillow" }
}
Ok "Pillow (caption dan grafis)"

# 4. Skill, file .env, dan Expert WorkBuddy
& $py 2_Tools/workbuddy/install_workbuddy.py --quiet
$code = $LASTEXITCODE
if ($code -eq 3) {
    Ok "Skill terpasang (WorkBuddy belum ditemukan: buka WorkBuddy sekali dan masuk, lalu jalankan setup lagi)"
} elseif ($code -ne 0) {
    Stop-Setup "Expert WorkBuddy gagal dipasang: baca pesan di atas."
} else {
    Ok "Expert AI Videographer terpasang di WorkBuddy"
}
if (-not (Test-Path .env)) { Stop-Setup "File .env belum ada: baca pesan di atas." }
Ok "File .env"

# 5. Kunci API: lewat halaman lokal, tidak pernah lewat chat
& $py -c "import sys; sys.path.insert(0, '2_Tools/vg'); from vglib import config; sys.exit(0 if config.api_key('kie') else 1)" 2>$null
$needKeys = ($LASTEXITCODE -ne 0)
if ($needKeys) {
    & $py 2_Tools/vg/vg.py setup --detach
} else {
    Ok "Kunci kie.ai sudah ada"
}

Write-Host ""
Write-Host "== Tinggal ini:"
$n = 1
if ($needKeys) {
    Write-Host "$n. Di halaman setup yang terbuka di browser: tempel kunci kie.ai (dan OpenRouter), klik Simpan."
    $n++
}
Write-Host "$n. Tutup WorkBuddy sepenuhnya (klik kanan ikonnya di taskbar atau system tray, pilih Quit/Keluar), lalu buka lagi."
$n++
Write-Host "$n. Pilih folder kerja ini: $Root"
$n++
Write-Host "$n. Pilih Expert 'AI Videographer' dan model glm-5.3-flash, lalu bilang: Buat video baru."
