"""The few things that differ between macOS/Linux and Windows: the Python command, process checks,
and starting a page that outlives the shell call that started it."""
import os
import signal
import subprocess
import sys

WINDOWS = os.name == "nt"

# The command a human or an agent types. python.org's Windows installer has no python3.exe, and the
# python3 that Windows ships is a Microsoft Store shortcut, so Windows uses `python`.
PYTHON = "python" if WINDOWS else "python3"
VG = PYTHON + " 2_Tools/vg/vg.py"

_STILL_ACTIVE = 259
_ERROR_ACCESS_DENIED = 5
_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
_DETACHED_PROCESS = 0x00000008
_CREATE_NEW_PROCESS_GROUP = 0x00000200
_CREATE_BREAKAWAY_FROM_JOB = 0x01000000


def utf8_output():
    """Windows pipes default to the ANSI code page, which cannot print the tool's arrows and dashes."""
    if not WINDOWS:
        return
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def pid_alive(pid):
    """True while process `pid` runs. On Windows os.kill(pid, 0) would terminate it, so ask the kernel."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if WINDOWS:
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.restype = wintypes.HANDLE
        handle = kernel32.OpenProcess(_PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return ctypes.get_last_error() == _ERROR_ACCESS_DENIED
        try:
            code = wintypes.DWORD()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return False
            return code.value == _STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except PermissionError:
        return True
    except (OSError, OverflowError):
        return False
    return True


def stop_pid(pid):
    """Ask process `pid` to end (SIGTERM; on Windows this terminates it)."""
    try:
        os.kill(int(pid), signal.SIGTERM)
    except (OSError, TypeError, ValueError):
        pass


def popen_detached(cmd, **kwargs):
    """Start `cmd` so it keeps running after the calling shell (an agent's tool call) ends."""
    if not WINDOWS:
        return subprocess.Popen(cmd, start_new_session=True, **kwargs)
    flags = _DETACHED_PROCESS | _CREATE_NEW_PROCESS_GROUP
    try:  # leave the agent app's job object too, where the app allows it
        return subprocess.Popen(cmd, creationflags=flags | _CREATE_BREAKAWAY_FROM_JOB, **kwargs)
    except OSError:
        return subprocess.Popen(cmd, creationflags=flags, **kwargs)
