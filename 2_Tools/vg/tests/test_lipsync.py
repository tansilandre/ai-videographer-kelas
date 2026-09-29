"""Lip-sync mode: a presenter says the reel's own narration on camera. The shot's picture (first frame, else
its storyboard panel) and a cut of the approved narration go to an audio-driven model (InfiniteTalk on
kie.ai), so the lips match the one voice the whole reel uses. Andre, 2026-09-29: "make her doing the
talking to the audience"."""
import json
import os
import shutil
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_vg import Base, shotlist  # noqa: E402
from vglib import finish, generate, registry, review  # noqa: E402
from vglib.shotlist import Shotlist  # noqa: E402


@unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg")
class LipsyncTests(Base):
    def setUp(self):
        super().setUp()
        audio = self.project.path / "6_Edit" / "1_Audio"
        audio.mkdir(parents=True)
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=220:d=4:sample_rate=48000",
                     str(audio / "Narration.wav")])

    def lipsync(self, **window):
        data = shotlist()
        s01 = data["shots"][0]
        s01.pop("characters", None)
        s01.pop("dialogue", None)
        s01.update({"mode": "lipsync", "model": "infinitalk-from-audio", "resolution": "720p",
                    "video_prompt": "A young woman talks to her phone camera in her car, natural head movement.",
                    "lipsync": dict({"audio": "file:6_Edit/1_Audio/Narration.wav", "start": 0.2, "end": 1.7},
                                    **window)})
        self.write(data)
        return data

    def errors(self):
        return Shotlist(self.project.shotlist(), self.project).validate()[0]

    def test_a_lipsync_shot_needs_a_real_audio_window(self):
        self.lipsync()
        self.assertEqual([e for e in self.errors() if "S01" in e], [])
        for bad in ({"end": 0.1}, {"start": 0.0, "end": 16.0}, {"audio": "file:6_Edit/1_Audio/Missing.wav"},
                    {"audio": None}):
            self.lipsync(**bad)
            self.assertTrue([e for e in self.errors() if "S01.lipsync" in e], bad)

    def test_the_price_is_per_started_second(self):
        self.lipsync()
        self.images_ready()
        sl = Shotlist(self.project.shotlist(), self.project)
        spec = registry.get("infinitalk-from-audio", "video", allow_untested=True)
        job = generate.build_video_job(self.project, sl, sl.shots["S01"], self.project.read_state(), spec)
        self.assertEqual(job["cost"], 24)  # 1.5 s -> 2 started seconds x 12 credits at 720p

    def test_the_request_carries_the_picture_and_the_cut_of_the_narration(self):
        self.lipsync()
        self.images_ready()
        generate.approve_video(self.project, "S01", False, confirm=24, allow_untested=True)
        generate.run_video(self.project, "S01", False, allow_untested=True)
        model, payload = self.fake.created[-1]
        self.assertEqual(model, "infinitalk/from-audio")
        self.assertEqual(sorted(payload), ["audio_url", "image_url", "prompt", "resolution"])
        self.assertIsInstance(payload["image_url"], str)
        self.assertTrue(payload["audio_url"].endswith(".mp3"))
        cut = self.project.path / "6_Edit" / "1_Audio" / "Lipsync_S01.mp3"
        self.assertAlmostEqual(finish._duration(cut), 1.5, delta=0.03)

    def test_moving_the_window_voids_the_visual_approval(self):
        self.lipsync()
        self.images_ready()
        sl = Shotlist(self.project.shotlist(), self.project)
        self.assertEqual(review.problems(self.project, sl, self.project.read_state()), [])
        self.lipsync(start=0.5)
        sl = Shotlist(self.project.shotlist(), self.project)
        self.assertTrue(review.problems(self.project, sl, self.project.read_state()))

    def test_kling_avatar_pro_gets_picture_audio_and_prompt_only(self):
        """Kling AI Avatar Pro on kie.ai (1080p, 16 credits a second): no resolution field, one price."""
        data = self.lipsync()
        data["shots"][0]["model"] = "kling-ai-avatar-pro"
        data["shots"][0].pop("resolution", None)
        self.write(data)
        self.images_ready()
        generate.approve_video(self.project, "S01", False, confirm=32, allow_untested=True)
        generate.run_video(self.project, "S01", False, allow_untested=True)
        model, payload = self.fake.created[-1]
        self.assertEqual(model, "kling/ai-avatar-pro")
        self.assertEqual(sorted(payload), ["audio_url", "image_url", "prompt"])


if __name__ == "__main__":
    unittest.main()
