"""Windows support: the command spelling, process checks and the Python installer for skills and the expert.
These run on any OS; the Windows-only branches are exercised on a real Windows PC."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from vglib import compat, next_step  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]


def load_installer():
    spec = importlib.util.spec_from_file_location("install_workbuddy",
                                                  str(ROOT / "2_Tools" / "workbuddy" / "install_workbuddy.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CompatTests(unittest.TestCase):
    def test_the_command_spelling_matches_the_os(self):
        self.assertEqual(compat.PYTHON, "python" if os.name == "nt" else "python3")
        self.assertEqual(compat.VG, compat.PYTHON + " 2_Tools/vg/vg.py")
        self.assertEqual(next_step.VG, compat.VG)

    def test_pid_alive(self):
        self.assertTrue(compat.pid_alive(os.getpid()))
        self.assertTrue(compat.pid_alive(str(os.getpid())))
        for bad in (None, "x", 0, -5):
            self.assertFalse(compat.pid_alive(bad))

    def test_a_finished_process_is_not_alive(self):
        proc = subprocess.Popen([sys.executable, "-c", "pass"])
        proc.wait()
        self.assertFalse(compat.pid_alive(proc.pid))

    def test_a_detached_process_runs_and_can_be_stopped(self):
        proc = compat.popen_detached([sys.executable, "-c", "import time; time.sleep(30)"],
                                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            self.assertTrue(compat.pid_alive(proc.pid))
            compat.stop_pid(proc.pid)
            proc.wait(timeout=10)
            self.assertFalse(compat.pid_alive(proc.pid))
        finally:
            if proc.poll() is None:
                proc.kill()

    def test_windows_popen_falls_back_when_the_job_forbids_breakaway(self):
        calls = []

        def fake_popen(cmd, **kwargs):
            calls.append(kwargs.get("creationflags"))
            if len(calls) == 1:
                raise PermissionError("access denied")
            return "proc"
        with mock.patch.object(compat, "WINDOWS", True), mock.patch.object(compat.subprocess, "Popen", fake_popen):
            self.assertEqual(compat.popen_detached(["x"]), "proc")
        self.assertTrue(calls[0] & compat._CREATE_BREAKAWAY_FROM_JOB)
        self.assertFalse(calls[1] & compat._CREATE_BREAKAWAY_FROM_JOB)
        self.assertTrue(calls[1] & compat._DETACHED_PROCESS)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.installer = load_installer()
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, str(self.tmp), True)

    def test_register_adds_one_entry_and_keeps_other_experts(self):
        market = self.tmp / "my-experts"
        manifest = market / ".codebuddy-plugin" / "marketplace.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({"name": "my-experts", "plugins": [
            {"name": "other", "source": "./plugins/other", "description": "x"}]}), encoding="utf-8")
        dest = market / "plugins" / "ai-videographer"
        (dest / ".codebuddy-plugin").mkdir(parents=True)
        (dest / ".codebuddy-plugin" / "plugin.json").write_text(
            json.dumps({"name": "ai-videographer", "description": "d"}), encoding="utf-8")
        self.installer.register(market, dest)
        self.installer.register(market, dest)
        plugins = json.loads(manifest.read_text(encoding="utf-8"))["plugins"]
        self.assertEqual([p["name"] for p in plugins], ["other", "ai-videographer"])
        self.assertEqual(plugins[1]["source"], "./plugins/ai-videographer")

    def test_install_expert_copies_and_registers(self):
        cfg = self.tmp / "cfg"
        cfg.mkdir()
        version = self.installer.install_expert(cfg)
        market = cfg / "plugins" / "marketplaces" / "my-experts"
        self.assertTrue((market / "plugins" / "ai-videographer" / "agents" / "ai-videographer.md").is_file())
        manifest = json.loads((market / ".codebuddy-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["plugins"][-1]["name"], "ai-videographer")
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")

    def test_the_playbook_tells_windows_to_type_python(self):
        text = (ROOT / "2_Tools/workbuddy/expert/ai-videographer/agents/ai-videographer.md").read_text(encoding="utf-8")
        self.assertIn("On Windows type `python`", text)
        self.assertIn("setup.ps1", text)
        self.assertNotIn("test -f", text)

    def test_link_skills_links_once_replaces_its_own_copy_and_skips_foreign_folders(self):
        skills = self.tmp / "1_Skills"
        (skills / "vg-director").mkdir(parents=True)
        (skills / "vg-director" / "SKILL.md").write_text("x", encoding="utf-8")
        with mock.patch.object(self.installer, "SKILLS", skills):
            link = self.tmp / "ws" / ".codebuddy" / "skills"
            self.assertIn(self.installer.link_skills(link), ("linked", "linked (junction)", "copied"))
            self.assertTrue((link / "vg-director" / "SKILL.md").is_file())
            self.assertIn(self.installer.link_skills(link), ("ok", "copied"))
            own_copy = self.tmp / "ws" / ".agents" / "skills"
            own_copy.mkdir(parents=True)
            (own_copy / self.installer.COPY_MARK).write_text("", encoding="utf-8")
            self.assertNotEqual(self.installer.link_skills(own_copy), "skip (exists and is not a link)")
            self.assertTrue((own_copy / "vg-director" / "SKILL.md").is_file())
            foreign = self.tmp / "ws" / ".claude" / "skills"
            foreign.mkdir(parents=True)
            self.assertEqual(self.installer.link_skills(foreign), "skip (exists and is not a link)")

    def test_setup_ps1_is_plain_ascii_for_windows_powershell(self):
        data = (ROOT / "setup.ps1").read_bytes()
        self.assertTrue(all(b < 128 for b in data), "Windows PowerShell 5.1 misreads non-ASCII in a BOM-less file")
        text = data.decode("ascii")
        for needed in ("Gyan.FFmpeg", "Python.Python.3.12", "pillow", "install_workbuddy.py", "setup --detach"):
            self.assertIn(needed, text)


if __name__ == "__main__":
    unittest.main()
