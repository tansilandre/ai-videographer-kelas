"""Offline tests for the vg tool. No network: a fake provider stands in for kie.ai.

Run from the workspace root:  python3 -m unittest discover -s 2_Tools/vg/tests -v
"""
import errno
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from vglib import config, generate, registry, review  # noqa: E402
from vglib.errors import ProviderError, Refused, UsageError  # noqa: E402
from vglib.project import Project  # noqa: E402
from vglib.shotlist import Shotlist  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 64
LINE = "Rumah Harbor Homes masih ada yang 1,3M-an? Aku cek langsung."
TALK = 'she says "%s". Avoid: morphing' % LINE
TALK_LOCKED = 'she says "%s". handheld. Avoid: morphing' % LINE


class FakeProvider:
    upload_ttl_s = 3600

    def __init__(self):
        self.created = []
        self.balance = 1000.0
        self.counter = 0
        self.finish = True
        self.fail_create = None  # set to a ProviderError to simulate a failed createTask

    def credits(self):
        return self.balance

    def create_task(self, model, payload):
        if self.fail_create:
            error, self.fail_create = self.fail_create, None
            raise error
        self.counter += 1
        self.created.append((model, payload))
        return "task%d" % self.counter

    def get_task(self, task_id):
        if not self.finish:
            return {"state": "generating", "urls": [], "credits": None, "fail_code": "", "fail_msg": ""}
        return {"state": "success", "urls": ["https://fake/%s.bin" % task_id], "credits": 10,
                "fail_code": "", "fail_msg": ""}

    def upload(self, path, upload_path="vg"):
        return "https://fake/upload/" + os.path.basename(path)

    def download(self, url, dest):
        Path(dest).write_bytes(PNG + url.encode())

    def create_voice(self, preset, name, description=None, example=None):
        return "voice123"

    def create_character(self, descriptions, image_urls, audio_ids=None, name=None):
        self.character_args = (descriptions, image_urls, audio_ids, name)
        return "char123"


def shotlist():
    return {
        "project": "Test_Project",
        "format": {"aspect_ratio": "9:16", "language": "id"},
        "style_lock": {"image": "shot on iPhone", "video": "handheld"},
        "look": {"world": "Harbor Homes, one sunny afternoon", "light": "warm sun from the left",
                 "grade": "natural warm", "graphics": "one font, one accent, captions in the lower third",
                 "style_frames": [{"id": "Look_A", "prompt": "Rani on the harbour street, golden light",
                                   "refs": ["Char_Rani_Portrait"]}]},
        "characters": [{
            "name": "Rani", "description": "Young Indonesian woman", "portrait": "Char_Rani_Portrait",
            "voice": {"preset": "sulafat", "name": "Rani voice", "example": "Halo"},
        }],
        "assets": [
            {"id": "Char_Rani_Portrait", "kind": "character", "prompt": "portrait", "aspect_ratio": "3:4"},
            {"id": "Char_Rani_Turnaround", "kind": "character", "prompt": "2x2 grid", "refs": ["Char_Rani_Portrait"],
             "aspect_ratio": "1:1"},
        ],
        "shots": [
            {"id": "S01", "time": "0-3s", "source": "ai", "summary": "hook", "mode": "character",
             "duration": "auto", "characters": ["Rani"],
             "dialogue": LINE,
             "storyboard": {"prompt": "selfie in car", "refs": ["Char_Rani_Portrait"]},
             "first_frame": {"from": "storyboard"}, "video_prompt": TALK},
            {"id": "S02", "time": "3-8s", "source": "ai", "summary": "drone", "mode": "frames", "duration": "4",
             "storyboard": {"prompt": "aerial"}, "first_frame": {"from": "storyboard"},
             "last_frame": {"prompt": "aerial end", "refs": ["first:S02"]}, "video_prompt": "drone glides"},
            {"id": "S03", "time": "8-13s", "source": "mg", "summary": "map"},
        ],
    }


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.project = Project(self.tmp / "2026-01-01_Test_Project")
        (self.project.path / "1_Script").mkdir(parents=True)
        self.write(shotlist())
        self.fake = FakeProvider()
        self._orig = (generate.get_provider, generate.POLL, generate.SUBMIT_GAP_S)
        generate.get_provider = lambda name: self.fake
        generate.POLL = {"image": (0, 5), "video": (0, 5), "mixed": (0, 5)}
        generate.SUBMIT_GAP_S = 0
        # stand-in for the workspace .env (safety settings are read from .env only)
        config._env_cache = {"VG_BUDGET_PROJECT": "1000", "VG_MAX_PER_CALL": "300", "VG_APPROVAL_MODE": "chat"}

    def tearDown(self):
        generate.get_provider, generate.POLL, generate.SUBMIT_GAP_S = self._orig
        config._env_cache = None
        shutil.rmtree(str(self.tmp))

    def write(self, data):
        self.project.shotlist_path.write_text(json.dumps(data), encoding="utf-8")

    def images_ready(self, visuals=True):
        """The workflow up to the video gate: style frames, look approval, every image, and (unless
        visuals=False) an edit plan, an animatic record and the visuals approval."""
        sl = Shotlist(self.project.shotlist(), self.project)
        generate.run_images(self.project, sl.image_targets("look"))
        review.approve_look(self.project)
        generate.run_images(self.project, sl.image_targets("all"))
        if visuals:
            self.visuals_ready()

    def write_edit_spec(self, spec=None):
        """Default: one clip segment per AI shot in the shot list, a card for every other beat."""
        if spec is None:
            segments = []
            for shot in self.project.shotlist()["shots"]:
                if shot["source"] == "ai":
                    segments.append({"id": shot["id"], "clip": shot["id"], "out": "speech+0.4"})
                else:
                    segments.append({"id": shot["id"], "duration": 2, "background": {"image": "storyboard:S02"}})
            spec = {"output": "Test_v1.0.mp4", "segments": segments,
                    "graphics": [{"segment": "S03", "type": "title", "text": "TOL 2 KM"}]}
        path = self.project.path / "6_Edit" / "Edit_Spec.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(spec), encoding="utf-8")
        return spec

    def show_animatic(self):
        """What `vg edit animatic` records after rendering (rendering itself needs ffmpeg and Swift)."""
        sl = Shotlist(self.project.shotlist(), self.project)
        items = review.visual_items(self.project, sl, self.project.read_state())
        out = self.project.path / "6_Edit" / "Animatic_Test_v1.mp4"
        out.parent.mkdir(exist_ok=True)
        out.write_bytes(b"mp4")
        review.record_animatic(self.project, out, review.snapshot(items))

    def visuals_ready(self):
        if not (self.project.path / "6_Edit" / "Edit_Spec.json").is_file():
            self.write_edit_spec()
        self.show_animatic()
        review.approve_visuals(self.project)


class RegistryTests(unittest.TestCase):
    def test_prices(self):
        omni = registry.get("gemini-omni-flash-1-1")
        self.assertEqual(registry.price(omni, {"resolution": "1080p", "duration": "4"}), 63)
        self.assertEqual(registry.price(omni, {"resolution": "720p", "duration": "10"}), 126)
        self.assertEqual(registry.price(omni, {"resolution": "4k", "duration": "6"}), 168)
        image = registry.get("gpt-image-2")
        self.assertEqual(registry.price(image, {"resolution": "2K"}), 10)

    def test_constraints(self):
        image = registry.get("gpt-image-2")
        self.assertTrue(registry.check_params(image, {"resolution": "2K", "aspect_ratio": "4:5"}))
        self.assertFalse(registry.check_params(image, {"resolution": "2K", "aspect_ratio": "9:16"}))

    def test_dialogue_fit(self):
        omni = registry.get("gemini-omni-flash-1-1")
        line = "x" * 58  # needs (58 / 10.5) + 0.7 = 6.2 s
        self.assertEqual(registry.fit_duration(omni, line), 8)
        self.assertEqual(registry.fit_duration(omni, "x" * 34), 4)
        self.assertIsNone(registry.fit_duration(omni, "x" * 200))

    def test_untested_refused(self):
        with self.assertRaises(UsageError):
            registry.get("veo-3-1")
        self.assertEqual(registry.get("veo-3-1", allow_untested=True)["id"], "veo-3-1")


class ShotlistTests(Base):
    def test_valid(self):
        errors, warnings = Shotlist(self.project.shotlist(), self.project).validate()
        self.assertEqual(errors, [])

    def test_catches_problems(self):
        data = shotlist()
        data["shots"][0]["characters"] = []
        data["shots"][1]["storyboard"]["refs"] = ["Nope"]
        data["shots"][1]["duration"] = "4"
        data["shots"][1]["dialogue"] = "x" * 80
        self.write(data)
        errors, _ = Shotlist(self.project.shotlist(), self.project).validate()
        text = "\n".join(errors)
        self.assertIn("character mode needs", text)
        self.assertIn("'Nope' is not an asset id", text)
        self.assertIn("do not fit", text)

    def test_style_lock_goes_before_avoid(self):
        sl = Shotlist(self.project.shotlist(), self.project)
        self.assertEqual(sl.video_prompt(sl.shots["S01"]), TALK_LOCKED)

    def test_first_aliases_storyboard(self):
        sl = Shotlist(self.project.shotlist(), self.project)
        self.assertEqual(sl.normalize_ref("first:S02"), ("target", "storyboard:S02"))


class ImageTests(Base):
    def test_generates_in_dependency_order_and_skips_on_rerun(self):
        self.images_ready()
        models = [m for m, _ in self.fake.created]
        self.assertEqual(len(models), 6)  # 1 style frame + 2 assets + 2 panels + 1 last frame
        self.assertEqual(models[0], "gpt-image-2-text-to-image")
        turnaround = [p for m, p in self.fake.created if p["prompt"] == "2x2 grid"][0]
        self.assertEqual(turnaround["input_urls"], ["https://fake/upload/Char_Rani_Portrait_v1.png"])
        self.assertTrue((self.project.path / "4_Frames" / "Frame_S02_Last_v1.png").is_file())
        self.images_ready(visuals=False)
        self.assertEqual(len(self.fake.created), 6, "second run must not spend")

    def test_prompt_change_makes_new_version(self):
        self.images_ready()
        data = shotlist()
        data["assets"][1]["prompt"] = "2x2 grid, warmer light"
        self.write(data)
        generate.run_images(self.project, ["asset:Char_Rani_Turnaround"])
        self.assertTrue((self.project.path / "2_References" / "Char_Rani_Turnaround_v2.png").is_file())

    def test_pending_task_is_resumed_not_resubmitted(self):
        self.fake.finish = False
        generate.run_images(self.project, ["asset:Char_Rani_Portrait"])
        self.assertEqual(len(self.fake.created), 1)
        self.fake.finish = True
        generate.run_images(self.project, ["asset:Char_Rani_Portrait"])
        self.assertEqual(len(self.fake.created), 1, "pending task must be polled, not re-submitted")
        self.assertIsNotNone(self.project.selected("asset:Char_Rani_Portrait"))

    def test_budget_cap_refuses(self):
        config._env_cache["VG_BUDGET_PROJECT"] = "5"
        with self.assertRaises(Refused):
            generate.run_images(self.project, ["asset:Char_Rani_Portrait"])
        self.assertEqual(self.fake.created, [])

    def test_dry_run_spends_nothing(self):
        sl = Shotlist(self.project.shotlist(), self.project)
        generate.run_images(self.project, sl.image_targets("all"), dry_run=True)
        self.assertEqual(self.fake.created, [])


class VideoGateTests(Base):
    def prepared(self):
        self.images_ready()
        generate.create_character(self.project, "Rani")
        self.fake.created = []

    def test_character_create_binds_voice(self):
        self.images_ready()
        generate.create_character(self.project, "Rani")
        self.assertEqual(self.fake.character_args[2], ["voice123"])

    def test_refuses_without_approval(self):
        self.prepared()
        with self.assertRaises(Refused):
            generate.run_video(self.project, "S01", False)
        self.assertEqual(self.fake.created, [])

    def test_confirm_must_match_estimate(self):
        self.prepared()
        with self.assertRaises(Refused):
            generate.approve_video(self.project, "S01,S02", False, confirm=100)
        generate.approve_video(self.project, "S01,S02", False, confirm=105 + 63)

    def test_approved_run_builds_legal_payloads(self):
        self.prepared()
        generate.approve_video(self.project, None, True, confirm=168)
        generate.run_video(self.project, None, True)
        payloads = {p["prompt"]: p for _, p in self.fake.created}
        talk = payloads[TALK_LOCKED]
        self.assertEqual(talk["duration"], "8")
        self.assertEqual(talk["character_ids"], ["char123"])
        self.assertEqual(talk["audio_ids"], ["voice123"])
        self.assertIn("image_urls", talk)
        self.assertNotIn("first_frame_url", talk)
        drone = payloads["drone glides handheld"]
        self.assertEqual(drone["first_frame_url"], "https://fake/upload/SB_S02_v1.png")
        self.assertEqual(drone["last_frame_url"], "https://fake/upload/Frame_S02_Last_v1.png")
        self.assertNotIn("image_urls", drone)
        self.assertTrue((self.project.path / "5_Clips" / "Clip_S01_v1.mp4").is_file())

    def test_change_after_approval_voids_it(self):
        self.prepared()
        generate.approve_video(self.project, "S02", False, confirm=63)
        data = shotlist()
        data["shots"][1]["video_prompt"] = "drone glides faster"
        self.write(data)
        with self.assertRaises(Refused):
            generate.run_video(self.project, "S02", False)
        self.assertEqual(self.fake.created, [])

    def test_approval_is_single_use(self):
        self.prepared()
        generate.approve_video(self.project, "S02", False, confirm=63)
        generate.run_video(self.project, "S02", False)
        self.assertEqual(len(self.fake.created), 1)
        generate.run_video(self.project, "S02", False)  # already done: skipped, no spend
        self.assertEqual(len(self.fake.created), 1)
        with self.assertRaises(Refused):
            generate.run_video(self.project, "S02", False, new_take=True)
        self.assertEqual(len(self.fake.created), 1)


class RefuterRegressionTests(Base):
    """Each test reproduces an attack found by the adversarial review on 2026-09-24."""

    def prepared(self):
        self.images_ready()
        generate.create_character(self.project, "Rani")
        self.fake.created = []

    def clips(self):
        return [p for m, p in self.fake.created if m.startswith("google/")]

    def test_duplicate_shot_ids_pay_once(self):
        self.prepared()
        generate.approve_video(self.project, "S02", False, confirm=63)
        generate.run_video(self.project, "S02,S02", False)
        self.assertEqual(len(self.clips()), 1)

    def test_network_error_blocks_retry_until_released(self):
        self.prepared()
        generate.approve_video(self.project, "S02", False, confirm=63)
        self.fake.fail_create = ProviderError("timeout", code=None)
        with self.assertRaises(ProviderError):
            generate.run_video(self.project, "S02", False)
        state = self.project.read_state()
        self.assertEqual([t["state"] for t in state["tasks"] if t["target"] == "clip:S02"], ["unknown"])
        self.assertTrue(state["approvals"]["video"]["S02"]["used"])
        with self.assertRaises(Refused):
            generate.run_video(self.project, "S02", False)
        generate.release(self.project, "clip:S02")
        with self.assertRaises(Refused):  # approval was consumed; a human must approve again
            generate.run_video(self.project, "S02", False)
        self.assertEqual(self.clips(), [])

    def test_image_network_error_blocks_resubmission(self):
        self.fake.fail_create = ProviderError("timeout", code=None)
        with self.assertRaises(ProviderError):
            generate.run_images(self.project, ["asset:Char_Rani_Portrait"])
        with self.assertRaises(Refused):
            generate.run_images(self.project, ["asset:Char_Rani_Portrait"])
        self.assertEqual(self.fake.created, [])
        generate.release(self.project, "asset:Char_Rani_Portrait")
        generate.run_images(self.project, ["asset:Char_Rani_Portrait"])
        self.assertEqual(len(self.fake.created), 1)

    def test_definite_rejection_restores_approval(self):
        self.prepared()
        generate.approve_video(self.project, "S02", False, confirm=63)
        self.fake.fail_create = ProviderError("422", code=422)
        with self.assertRaises(ProviderError):
            generate.run_video(self.project, "S02", False)
        self.assertFalse(self.project.read_state()["approvals"]["video"]["S02"]["used"])

    def test_zero_cost_approval_cannot_rearm(self):
        self.prepared()
        generate.approve_video(self.project, "S02", False, confirm=63)
        generate.run_video(self.project, "S02", False)
        generate.approve_video(self.project, "S02", False, confirm=0)  # "already generated": nothing approved
        clip = self.project.selected("clip:S02")
        clip.unlink()
        with self.assertRaises(Refused):
            generate.run_video(self.project, "S02", False)
        self.assertEqual(len(self.clips()), 1)

    def test_new_take_clip_counts_as_done(self):
        self.prepared()
        generate.approve_video(self.project, "S02", False, confirm=63, new_take=True)
        generate.run_video(self.project, "S02", False, new_take=True)
        self.assertEqual(generate.estimate(self.project, "video"), 105)  # only S01 left
        generate.run_video(self.project, "S02", False)  # skipped as done
        self.assertEqual(len(self.clips()), 1)

    def test_stale_identity_is_refused(self):
        self.prepared()
        data = shotlist()
        data["assets"][0]["prompt"] = "portrait, different face"
        self.write(data)
        generate.run_images(self.project, ["asset:Char_Rani_Portrait"])
        with self.assertRaises(Refused):  # the portrait is part of the reviewed visuals
            generate.approve_video(self.project, "S01", False, confirm=105)
        self.visuals_ready()  # the human re-approves the reel with the new face...
        with self.assertRaises(UsageError):  # ...and the identity built from the old one is still stale
            generate.approve_video(self.project, "S01", False, confirm=105)

    def test_dialogue_must_be_in_video_prompt(self):
        data = shotlist()
        data["shots"][0]["video_prompt"] = "she says: \"something much longer than the checked line\""
        self.write(data)
        errors, _ = Shotlist(self.project.shotlist(), self.project).validate()
        self.assertTrue(any("word for word" in e for e in errors))

    def test_terminal_mode_needs_a_human_typed_code(self):
        self.prepared()
        config._env_cache["VG_APPROVAL_MODE"] = "terminal"
        original = generate._open_tty

        def no_tty():
            raise OSError("no terminal")
        generate._open_tty = no_tty
        try:
            with self.assertRaises(Refused):
                generate.approve_video(self.project, "S02", False, confirm=63)
            self.assertEqual(self.project.read_state()["approvals"]["video"], {})

            class FakeTty(io.StringIO):
                def readline(self_inner):
                    return self.code + "\n"
            self.code = "0000"
            generate._open_tty = lambda: FakeTty()
            with self.assertRaises(Refused):  # wrong code
                generate.approve_video(self.project, "S02", False, confirm=63)
            original_random = generate.random.SystemRandom
            generate.random.SystemRandom = lambda: type("R", (), {"randint": lambda s, a, b: 4321})()
            self.code = "4321"
            try:
                generate.approve_video(self.project, "S02", False, confirm=63)
            finally:
                generate.random.SystemRandom = original_random
            self.assertIn("S02", self.project.read_state()["approvals"]["video"])
        finally:
            generate._open_tty = original

    def test_failed_task_credits_count_as_spent(self):
        with self.project.transaction() as st:
            st["tasks"].append({"target": "clip:S01", "state": "fail", "credits": 126, "estimate": 105})
        self.assertEqual(Project.spent(self.project.read_state()), 126)

    def test_env_file_budget_beats_command_prefix(self):
        config._env_cache["VG_BUDGET_PROJECT"] = "5"
        os.environ["VG_BUDGET_PROJECT"] = "999999"
        try:
            with self.assertRaises(Refused):
                generate.run_images(self.project, ["asset:Char_Rani_Portrait"])
        finally:
            del os.environ["VG_BUDGET_PROJECT"]

    def test_process_env_cannot_raise_the_default_budget(self):
        config._env_cache = {"VG_APPROVAL_MODE": "chat"}  # .env without a budget line -> default 800
        os.environ["VG_BUDGET_PROJECT"] = "999999"
        try:
            self.assertEqual(config.number("VG_BUDGET_PROJECT"), 800)
        finally:
            del os.environ["VG_BUDGET_PROJECT"]

    def test_identical_shots_are_tracked_separately(self):
        data = shotlist()
        for sid in ("S04", "S05"):
            data["shots"].append({"id": sid, "time": "13-17s", "source": "ai", "summary": "city", "mode": "text",
                                  "duration": "4", "storyboard": {"prompt": "city"},
                                  "video_prompt": "city skyline at dusk"})
        self.write(data)
        self.prepared()
        generate.approve_video(self.project, "S04", False, confirm=63)
        generate.run_video(self.project, "S04", False)
        self.assertEqual(generate.estimate(self.project, "video"), 105 + 63 + 63)  # S01, S02, S05 still to do


class FinalReviewRegressionTests(Base):
    """Findings of the final multi-agent review on 2026-09-24."""

    def prepared(self):
        self.images_ready()
        generate.create_character(self.project, "Rani")
        self.fake.created = []

    def test_real_tty_prompt_reads_the_typed_code(self):
        import pty
        pid, fd = pty.fork()
        if pid == 0:  # child: the real _open_tty on a real pseudo-terminal
            config._env_cache = {"VG_APPROVAL_MODE": "terminal"}
            generate.random.SystemRandom = lambda: type("R", (), {"randint": lambda s, a, b: 4321})()
            try:
                generate._human_confirm(63, 1, "cmd")
                os._exit(0)
            except Exception:
                os._exit(1)
        import time as _time
        output, sent, deadline = b"", False, _time.time() + 20
        while _time.time() < deadline:
            try:
                chunk = os.read(fd, 1024)
            except OSError:
                break  # child closed the terminal
            if not chunk:
                break
            output += chunk
            if not sent and b"Type 4321" in output:
                os.write(fd, b"4321\n")
                sent = True
        _, status = os.waitpid(pid, 0)
        self.assertTrue(sent, output)
        self.assertEqual(os.WEXITSTATUS(status), 0, output)

    def test_rejection_only_restores_the_approval_it_consumed(self):
        with self.project.transaction() as st:
            st["approvals"]["video"]["S02"] = {"snapshot": "x", "estimate": 63, "used": True, "claimed_row": "new"}
        generate._update_row(self.project, "old", "S02", state="rejected")
        self.assertTrue(self.project.read_state()["approvals"]["video"]["S02"]["used"])
        generate._update_row(self.project, "new", "S02", state="rejected")
        self.assertFalse(self.project.read_state()["approvals"]["video"]["S02"]["used"])

    def test_submit_skips_work_another_run_finished(self):
        self.images_ready()
        self.fake.created = []
        state = self.project.read_state()
        sl = Shotlist(self.project.shotlist(), self.project)
        job = generate.build_image_job(self.project, sl, "asset:Char_Rani_Portrait", state)
        session = generate.Session(self.project)
        self.assertIsNone(generate._submit(self.project, session, job, lambda: {}))
        self.assertEqual(self.fake.created, [])

    def test_file_refs_cannot_leave_the_project(self):
        data = shotlist()
        data["assets"][0]["refs"] = ["file:../../etc/hosts"]
        self.write(data)
        errors, _ = Shotlist(self.project.shotlist(), self.project).validate()
        self.assertTrue(any("outside the project" in e for e in errors))

    def test_one_broken_task_does_not_stop_polling_the_others(self):
        original = self.fake.get_task

        def flaky(task_id):
            if task_id == "task1":
                raise ProviderError("boom", code=500)
            return original(task_id)
        self.fake.get_task = flaky
        data = shotlist()
        data["assets"].append({"id": "Loc_Harbour", "kind": "location", "prompt": "harbour street"})
        self.write(data)
        generate.run_images(self.project, ["asset:Char_Rani_Portrait", "asset:Loc_Harbour"])
        state = self.project.read_state()
        states = {t["target"]: t["state"] for t in state["tasks"]}
        self.assertEqual(states["asset:Char_Rani_Portrait"], "pending")
        self.assertEqual(states["asset:Loc_Harbour"], "success")

    def test_adopt_attaches_an_accepted_task(self):
        self.fake.fail_create = ProviderError("timeout", code=None)
        with self.assertRaises(ProviderError):
            generate.run_images(self.project, ["asset:Char_Rani_Portrait"])
        generate.adopt(self.project, "asset:Char_Rani_Portrait", "task-from-dashboard")
        generate.resume(self.project)
        self.assertIsNotNone(self.project.selected("asset:Char_Rani_Portrait"))
        self.assertEqual(self.fake.created, [])

    def test_seed_reaches_the_payload_and_the_snapshot(self):
        self.prepared()
        data = shotlist()
        data["shots"][1]["seed"] = 123456
        self.write(data)
        generate.approve_video(self.project, "S02", False, confirm=63)
        generate.run_video(self.project, "S02", False)
        self.assertEqual(self.fake.created[-1][1]["seed"], 123456)
        self.assertIsInstance(self.fake.created[-1][1]["seed"], int)

    def test_veo_lite_per_shot_payload_and_price(self):
        self.prepared()
        data = shotlist()
        data["shots"][1]["model"] = "veo-3-1-lite"
        data["video_defaults"] = {"resolution": "720p"}
        data["shots"][1]["duration"] = "auto"
        self.write(data)
        # live-tested since the 2026-09-28 pilot, so no --allow-untested (test_untested_refused covers the guard)
        generate.approve_video(self.project, "S02", False, confirm=30)
        generate.run_video(self.project, "S02", False)
        model, payload = self.fake.created[-1]
        self.assertEqual(model, "veo3_lite")
        self.assertEqual(payload["generationType"], "FIRST_AND_LAST_FRAMES_2_VIDEO")
        self.assertEqual(len(payload["imageUrls"]), 2)  # first + last frame
        self.assertEqual(payload["duration"], 4)
        self.assertIsInstance(payload["duration"], int)
        self.assertEqual(payload["resolution"], "720p")
        self.assertNotIn("first_frame_url", payload)

    def test_veo_provider_maps_status(self):
        from providers.kie_veo import KieVeoProvider
        provider = KieVeoProvider("key")
        replies = {"fail": {"code": 200, "data": {"successFlag": 3, "errorCode": 500, "errorMessage": "upstream"}},
                   "ok": {"code": 200, "data": {"successFlag": 1, "response": {"resultUrls": ["https://x/v.mp4"]}}},
                   "run": {"code": 200, "data": {"successFlag": 0}}}
        for key, reply in replies.items():
            provider._request = lambda method, url, body=None, query=None, reply=reply: (200, reply)
            info = provider.get_task(key)
            expected = {"fail": "fail", "ok": "success", "run": "generating"}[key]
            self.assertEqual(info["state"], expected)
        self.assertEqual(info["state"], "generating")
        sent = {}

        def capture(method, url, body=None, query=None):
            sent.update(url=url, body=body)
            return 200, {"code": 200, "data": {"taskId": "veo_1"}}
        provider._request = capture
        self.assertEqual(provider.create_task("veo3_lite", {"prompt": "p", "imageUrls": ["u"]}), "veo_1")
        self.assertTrue(sent["url"].endswith("/api/v1/veo/generate"))
        self.assertEqual(sent["body"]["model"], "veo3_lite")
        self.assertIs(sent["body"]["enableTranslation"], False)

    def test_confirm_nan_is_refused(self):
        self.prepared()
        with self.assertRaises(Refused):
            generate.approve_video(self.project, "S02", False, confirm=float("nan"))
        self.assertEqual(self.project.read_state()["approvals"]["video"], {})

    def test_nan_budget_is_rejected(self):
        config._env_cache["VG_BUDGET_PROJECT"] = "nan"
        with self.assertRaises(UsageError):
            config.number("VG_BUDGET_PROJECT")

    def test_ambiguous_project_name_is_refused(self):
        from vglib import project as project_module
        original = config.PROJECTS_DIR
        config.PROJECTS_DIR = self.tmp
        try:
            for day in ("2026-01-02", "2026-01-03"):
                (self.tmp / ("%s_Test_Project" % day) / "1_Script").mkdir(parents=True)
            with self.assertRaises(UsageError):
                project_module.resolve("Test_Project")
            self.assertEqual(project_module.resolve("2026-01-02_Test_Project").name, "2026-01-02_Test_Project")
        finally:
            config.PROJECTS_DIR = original

    def test_copied_project_does_not_carry_usable_approvals(self):
        self.prepared()
        generate.approve_video(self.project, "S02", False, confirm=63)
        with self.project.transaction() as st:
            st["approvals"]["video"]["S02"]["project_path"] = "/somewhere/else"
        with self.assertRaises(Refused):
            generate.run_video(self.project, "S02", False)
        self.assertEqual(self.fake.created, [])

    def test_finishing_the_same_task_twice_records_one_version(self):
        generate.run_images(self.project, ["asset:Char_Rani_Portrait"])
        state = self.project.read_state()
        record = [t for t in state["tasks"] if t["target"] == "asset:Char_Rani_Portrait"][0]
        generate._finish(self.project, generate.Session(self.project), record,
                         {"urls": ["https://fake/again"], "credits": 10})
        versions = self.project.read_state()["outputs"]["asset:Char_Rani_Portrait"]["versions"]
        self.assertEqual(len(versions), 1)


class VisualGateTests(Base):
    """The human approves the look, then the whole reel as images, before any video (spec 2026-09-28)."""

    def urls(self, prompt_start):
        return [p.get("input_urls", []) for _, p in self.fake.created if p["prompt"].startswith(prompt_start)][-1]

    def test_look_stage_builds_style_frames_and_their_sheets(self):
        sl = Shotlist(self.project.shotlist(), self.project)
        self.assertEqual(sl.image_targets("look"), ["asset:Char_Rani_Portrait", "look:Look_A"])
        generate.run_images(self.project, sl.image_targets("look"))
        self.assertTrue((self.project.path / "2_References" / "Look_A_v1.png").is_file())

    def test_look_validation(self):
        data = shotlist()
        data["look"]["style_frames"] = [{"id": "A", "prompt": "x", "refs": ["look:A"]}, {"id": "A"},
                                        {"id": "B", "prompt": "y"}, {"id": "C", "prompt": "z"}]
        self.write(data)
        text = "\n".join(Shotlist(self.project.shotlist(), self.project).validate()[0])
        self.assertIn("1-3", text)
        self.assertIn("duplicate id", text)
        self.assertIn("style_frames.A.prompt: missing", text)
        self.assertIn("may not ref another style frame", text)
        del data["look"]
        self.write(data)
        sl = Shotlist(self.project.shotlist(), self.project)
        self.assertEqual(sl.validate()[0], [])
        self.assertTrue([t for t in sl.todos if t.startswith("look:")])

    def test_storyboard_refused_until_look_approved(self):
        with self.assertRaises(Refused):
            generate.run_images(self.project, ["storyboard:S02"])
        self.assertEqual(self.fake.created, [])
        generate.run_images(self.project, ["storyboard:S02"], dry_run=True)  # a dry run reports, never refuses
        sl = Shotlist(self.project.shotlist(), self.project)
        generate.run_images(self.project, sl.image_targets("look"))
        with self.assertRaises(Refused):
            review.approve_visuals(self.project)  # the look comes first
        review.approve_look(self.project)
        generate.run_images(self.project, ["storyboard:S02"])
        self.assertIsNotNone(self.project.selected("storyboard:S02"))

    def test_approve_look_needs_generated_frames(self):
        with self.assertRaises(UsageError):
            review.approve_look(self.project)

    def test_style_frames_become_refs_but_not_for_identity_sheets_or_opted_out_shots(self):
        data = shotlist()
        data["shots"][1]["look_refs"] = False
        self.write(data)
        self.images_ready(visuals=False)
        look_url = "https://fake/upload/Look_A_v1.png"
        self.assertIn(look_url, self.urls("selfie in car"))
        self.assertNotIn(look_url, self.urls("aerial"))
        self.assertNotIn(look_url, self.urls("2x2 grid"))

    def test_visuals_need_an_edit_plan_and_a_current_animatic(self):
        self.images_ready(visuals=False)
        with self.assertRaises(UsageError):
            review.approve_visuals(self.project)  # no Edit_Spec.json yet
        self.write_edit_spec()
        with self.assertRaises(Refused):
            review.approve_visuals(self.project)  # the human has not seen an animatic
        self.show_animatic()
        generate.run_images(self.project, ["storyboard:S02"], new_take=True)
        with self.assertRaises(Refused):
            review.approve_visuals(self.project)  # the animatic shows the old panel
        self.show_animatic()
        review.approve_visuals(self.project)
        self.assertEqual(review.problems(self.project, Shotlist(self.project.shotlist(), self.project),
                                         self.project.read_state()), [])

    def test_video_refused_without_visuals_approval(self):
        self.images_ready(visuals=False)
        generate.create_character(self.project, "Rani")
        self.fake.created = []
        with self.assertRaises(Refused) as ctx:
            generate.approve_video(self.project, "S02", False, confirm=63)
        self.assertIn("visuals not approved", str(ctx.exception))
        with self.assertRaises(Refused):
            generate.run_video(self.project, "S02", False)
        self.assertEqual(self.fake.created, [])

    def test_new_frame_after_approval_closes_the_gate_and_names_it(self):
        self.images_ready()
        generate.create_character(self.project, "Rani")
        generate.approve_video(self.project, "S02", False, confirm=63)
        generate.run_images(self.project, ["last:S02"], new_take=True)
        self.fake.created = []
        with self.assertRaises(Refused) as ctx:
            generate.run_video(self.project, "S02", False)
        self.assertIn("S02 last frame", str(ctx.exception))
        self.assertEqual(self.fake.created, [])

    def test_edit_plan_text_counts_but_audio_does_not(self):
        self.images_ready()
        sl = Shotlist(self.project.shotlist(), self.project)
        spec = json.loads((self.project.path / "6_Edit" / "Edit_Spec.json").read_text())
        spec["segments"][0]["audio"] = "file:6_Edit/1_Voice_Over/S01.wav"
        spec["output"] = "Test_v2.0.mp4"
        self.write_edit_spec(spec)
        self.assertEqual(review.problems(self.project, sl, self.project.read_state()), [])
        spec["graphics"][0]["text"] = "TOL 1,5 KM"
        self.write_edit_spec(spec)
        found = review.problems(self.project, sl, self.project.read_state())
        self.assertEqual(len(found), 1)
        self.assertIn("edit plan", found[0])

    def test_new_style_frame_voids_look_and_visuals(self):
        self.images_ready()
        generate.run_images(self.project, ["look:Look_A"], new_take=True)
        sl = Shotlist(self.project.shotlist(), self.project)
        found = review.problems(self.project, sl, self.project.read_state())
        self.assertIn("look changed since approval: look frame Look_A", found[0])
        self.assertIn("visuals changed since approval: look", found[1])
        with self.assertRaises(Refused):
            generate.run_images(self.project, ["storyboard:S01"], new_take=True)

    def test_gate_is_rechecked_inside_the_submit_transaction(self):
        self.images_ready()
        generate.create_character(self.project, "Rani")
        generate.approve_video(self.project, "S02", False, confirm=63)
        self.fake.created = []
        checks = {"n": 0}
        original = review.problems

        def changes_after_first_check(*args):
            checks["n"] += 1
            return [] if checks["n"] == 1 else ["visuals changed since approval: S02 storyboard"]
        review.problems = changes_after_first_check
        try:
            with self.assertRaises(Refused):
                generate.run_video(self.project, "S02", False)
        finally:
            review.problems = original
        self.assertEqual(self.fake.created, [])
        self.assertFalse(self.project.read_state()["approvals"]["video"]["S02"]["used"])

    def test_replaced_photo_closes_the_gate_and_names_it(self):
        photo = self.project.path / "0_Source" / "Facade.jpg"
        photo.parent.mkdir(exist_ok=True)
        photo.write_bytes(b"one")
        self.images_ready(visuals=False)
        spec = self.write_edit_spec()
        spec["segments"].append({"id": "S06", "still": "file:0_Source/Facade.jpg", "duration": 3})
        self.write_edit_spec(spec)
        self.visuals_ready()
        photo.write_bytes(b"two")
        found = review.problems(self.project, Shotlist(self.project.shotlist(), self.project),
                                self.project.read_state())
        self.assertIn("image file:0_Source/Facade.jpg", found[0])

    def test_old_ledger_reads_as_not_approved(self):
        self.project.state_path.write_text(json.dumps({"version": 1, "outputs": {}, "tasks": [],
                                                       "approvals": {"video": {}}}), encoding="utf-8")
        state = self.project.read_state()
        self.assertEqual(state["animatics"], [])
        found = review.problems(self.project, Shotlist(self.project.shotlist(), self.project), state)
        self.assertEqual(found, ["look not approved", "visuals not approved"])

    def test_terminal_mode_without_a_terminal_hands_the_command_to_the_human(self):
        sl = Shotlist(self.project.shotlist(), self.project)
        generate.run_images(self.project, sl.image_targets("look"))
        config._env_cache["VG_APPROVAL_MODE"] = "terminal"
        original = generate._open_tty

        def no_tty():
            raise OSError(errno.ENXIO, "no tty")
        generate._open_tty = no_tty
        try:
            with self.assertRaises(Refused) as ctx:
                review.approve_look(self.project)
        finally:
            generate._open_tty = original
        self.assertIn("approve look -p", str(ctx.exception))
        self.assertNotIn("look", self.project.read_state()["approvals"])

    def test_broken_edit_plan_is_a_clear_error(self):
        path = self.project.path / "6_Edit" / "Edit_Spec.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text("{not json", encoding="utf-8")
        with self.assertRaises(UsageError) as ctx:
            review.edit_spec(self.project)
        self.assertIn("Edit_Spec.json", str(ctx.exception))

    def test_copied_project_does_not_carry_visual_approvals(self):
        self.images_ready()
        copy = Project(self.tmp / "2026-01-02_Copy")
        shutil.copytree(str(self.project.path), str(copy.path))
        found = review.problems(copy, Shotlist(copy.shotlist(), copy), copy.read_state())
        self.assertEqual(len(found), 2)
        self.assertTrue(all("another project folder" in f for f in found))

    def test_animatic_segments_use_stills_and_edit_timing(self):
        from vglib import finish
        data = shotlist()
        data["shots"][1]["first_frame"] = {"prompt": "aerial start"}
        sl = Shotlist(data, self.project)
        seg, caption_shot = finish._animatic_segment(sl, {"id": "S02", "clip": "S02", "in": 0.4, "out": 4.9})
        self.assertEqual((seg["still"], seg["duration"], seg["clip"], caption_shot), ("first:S02", 4.5, None, "S02"))
        seg, _ = finish._animatic_segment(sl, {"id": "S01", "clip": "S01", "out": "speech+0.4"})
        self.assertEqual(seg["still"], "storyboard:S01")
        self.assertGreaterEqual(seg["duration"], 3.0)
        seg, caption_shot = finish._animatic_segment(sl, {"id": "S03", "clip": "S01", "in": 0, "out": 2.25,
                                                          "text": "Keluar cluster.", "cover": {"image": "storyboard:S02"}})
        self.assertEqual((seg["background"]["image"], seg["vo"]["speak"], caption_shot),
                         ("storyboard:S02", False, None))


class EditImageTests(Base):
    def test_file_ref_resolves_inside_the_project(self):
        from vglib import finish
        photo = self.project.path / "0_Source" / "Facade.jpg"
        photo.parent.mkdir(parents=True)
        photo.write_bytes(b"jpg")
        self.assertEqual(finish._image(self.project, None, "file:0_Source/Facade.jpg", "S06"), photo.resolve())

    def test_file_ref_outside_the_project_is_refused(self):
        from vglib import finish
        (self.tmp / "Elsewhere.jpg").write_bytes(b"jpg")
        with self.assertRaises(UsageError):
            finish._image(self.project, None, "file:../Elsewhere.jpg", "S06")
        with self.assertRaises(UsageError):
            finish._image(self.project, None, "file:0_Source/Missing.jpg", "S06")

    @unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg")
    def test_pan_x_slides_a_portrait_window_across_a_wide_photo(self):
        from vglib import finish
        wide = self.tmp / "wide.png"
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=s=900x300", "-frames:v", "1",
                     str(wide)])
        piece = self.tmp / "piece.mp4"
        finish._image_piece(wide, 1.0, piece, [1.0, 1.0], 0, 0, 0, pan_x=[0.0, 1.0])
        size = finish._run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                            "stream=width,height", "-of", "csv=p=0", str(piece)]).strip()
        self.assertEqual(size, "1080,1920")
        self.assertAlmostEqual(finish._duration(piece), 1.0, delta=0.1)


if __name__ == "__main__":
    unittest.main()
