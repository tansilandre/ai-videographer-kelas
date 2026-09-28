"""`vg audio`: narration takes (OpenRouter TTS), music takes (Lyria), synthesized sound effects and a
loudness curve for finding a music drop. No network: the HTTP call is replaced."""
import base64
import json
import os
import shutil
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_vg import Base  # noqa: E402
from vglib import audio, config, finish  # noqa: E402
from vglib.cli import main  # noqa: E402
from vglib.errors import UsageError  # noqa: E402


class FakeOpenRouter:
    """Records every request; answers speech with 0.5 s of PCM and music with a streamed MP3."""

    def __init__(self, tmp):
        self.requests = []
        self.tmp = tmp

    def post(self, path, body, key, stream=False):
        self.requests.append((path, body, key, stream))
        if path == "/audio/speech":
            return b"\x00\x10" * 12000, "audio/pcm;rate=24000;channels=1"
        mp3 = self.tmp / "fake_music.mp3"
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=220:d=1", str(mp3)])
        data = base64.b64encode(mp3.read_bytes()).decode()
        half = len(data) // 2
        return [b": keep-alive", b"",
                ("data: " + json.dumps({"choices": [{"delta": {"audio": {"data": data[:half]}}}]})).encode(),
                ("data: " + json.dumps({"choices": [{"delta": {"audio": {"data": data[half:]}}}]})).encode(),
                ("data: " + json.dumps({"choices": [{"delta": {"content": "<instrumental>"}}]})).encode(),
                b"data: [DONE]"], "text/event-stream"


@unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg")
class AudioTests(Base):
    def setUp(self):
        super().setUp()
        config._env_cache["OPENROUTER_API_KEY"] = "test-key"
        self.fake = FakeOpenRouter(self.tmp)
        self._post = audio.post
        audio.post = self.fake.post

    def tearDown(self):
        audio.post = self._post
        super().tearDown()

    def test_voice_makes_one_take_per_voice_with_the_style_as_direction(self):
        paths = audio.voice(self.project, "Tebak harga rumah ini.", ["Callirrhoe", "Leda"], "playful quiz host")
        self.assertEqual([p.name for p in paths], ["Narration_Take_Callirrhoe_v1.wav", "Narration_Take_Leda_v1.wav"])
        self.assertTrue(all(p.parent == self.project.path / "6_Edit" / "1_Audio" for p in paths))
        self.assertAlmostEqual(finish._duration(paths[0]), 0.5, delta=0.05)
        path, body, key, stream = self.fake.requests[0]
        self.assertEqual((path, key, body["input"], body["response_format"]),
                         ("/audio/speech", "test-key", "Tebak harga rumah ini.", "pcm"))
        self.assertEqual(body["provider"]["options"]["google-ai-studio"]["speech_metadata"]["style"],
                         "playful quiz host")
        again = audio.voice(self.project, "Lagi.", ["Leda"], "calm")
        self.assertEqual(again[0].name, "Narration_Take_Leda_v2.wav")  # never overwrites a take

    def test_music_joins_the_streamed_chunks_into_one_file(self):
        paths = audio.music(self.project, "Playful quiz pop, drop at 0:20", "Quiz_Pop", takes=2)
        self.assertEqual([p.name for p in paths], ["Music_Take_Quiz_Pop_v1.mp3", "Music_Take_Quiz_Pop_v2.mp3"])
        self.assertAlmostEqual(finish._duration(paths[0]), 1.0, delta=0.15)
        path, body, key, stream = self.fake.requests[0]
        self.assertTrue(stream)
        self.assertEqual((path, body["modalities"], body["model"]),
                         ("/chat/completions", ["audio"], audio.MUSIC_MODEL))

    def test_sfx_writes_the_four_effects(self):
        paths = audio.sfx(self.project)
        self.assertEqual(sorted(p.name for p in paths),
                         ["Sfx_Ding_v1.wav", "Sfx_Tap_v1.wav", "Sfx_Tick_v1.wav", "Sfx_Whoosh_v1.wav"])
        for p in paths:
            self.assertGreater(finish._duration(p), 0.1)

    def test_curve_finds_the_drop_not_the_ending_sting(self):
        """A drop is a jump into the loudest stretch. Neither a quieter section after a deep break nor a
        final hit after the ending's silence counts (Lyria's Quiz_Pop take: drop 18.5 s; earlier
        versions of this search said 25.4 s and 30 s)."""
        track = self.tmp / "track.wav"
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                     "aevalsrc='(0.05*lt(t,3)+0.4*between(t,3.5,6)+0.1*between(t,6.5,9)+0.9*gte(t,9.6))"
                     "*sin(2*PI*220*t)':s=48000:d=10",
                     str(track)])
        curve = audio.curve(track, step=0.25)
        self.assertAlmostEqual(audio.find_drop(curve), 3.5, delta=0.26)

    def test_missing_key_is_a_clear_error_and_the_short_name_works(self):
        del config._env_cache["OPENROUTER_API_KEY"]
        with self.assertRaises(UsageError):
            audio.voice(self.project, "x", ["Leda"], "calm")
        config._env_cache["OPENROUTER"] = "short-name-key"
        audio.voice(self.project, "x", ["Leda"], "calm")
        self.assertEqual(self.fake.requests[-1][2], "short-name-key")

    def test_cli_reads_the_script_from_a_file(self):
        script = self.project.path / "1_Script" / "Narration.txt"
        script.write_text("Satu. Dua.", encoding="utf-8")
        code = main(["audio", "voice", "-p", str(self.project.path), "--text-file", "1_Script/Narration.txt",
                     "--voices", "Leda", "--style", "calm"])
        self.assertEqual(code, 0)
        self.assertEqual(self.fake.requests[-1][1]["input"], "Satu. Dua.")
        self.assertEqual(main(["audio", "voice", "-p", str(self.project.path), "--text-file", "1_Script/Missing.txt",
                               "--voices", "Leda", "--style", "calm"]), 1)  # a usage error exits 1


if __name__ == "__main__":
    unittest.main()


class DoctorTests(Base):
    """Setup checks match what the harness really needs: the Swift renderer (macOS), not Node, and the
    OpenRouter key for `vg audio`."""

    def doctor(self):
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["doctor"])
        return out.getvalue()

    def test_doctor_checks_swift_and_the_audio_key_not_node(self):
        text = self.doctor()
        self.assertIn("swiftc", text)
        self.assertNotIn("node", text.lower().replace("anode", ""))
        self.assertRegex(text, r"warn\s+OPENROUTER_API_KEY")
        config._env_cache["OPENROUTER"] = "x"
        self.assertRegex(self.doctor(), r"ok\s+OPENROUTER_API_KEY")
