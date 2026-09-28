"""Shot craft tags with validate warnings, and one grade over the whole picture in the edit
(4_Docs/Research/2026-09-28_Higgsfield_Learnings_v1.0.md §11)."""
import json
import os
import shutil
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_vg import Base, shotlist  # noqa: E402
from vglib import review  # noqa: E402
from vglib.errors import UsageError  # noqa: E402
from vglib.shotlist import Shotlist  # noqa: E402


def tagged():
    data = shotlist()
    s01, s02, s03 = data["shots"]
    s01.update(category="hook_talking", camera="handheld", size="mcu", promise="she will check the house herself")
    s02.update(category="aerial_establish", camera="drone_approach", size="ews")
    s03.update(category="graphic", camera="static", size="ws")
    return data


class CraftTagTests(Base):
    def warnings(self, data):
        self.write(data)
        sl = Shotlist(self.project.shotlist(), self.project)
        errors, warnings = sl.validate()
        self.assertEqual(errors, [])
        return "\n".join(warnings)

    def test_unknown_category_camera_and_size_are_named(self):
        data = tagged()
        data["shots"][1].update(category="drone_thing", camera="swoop", size="huge")
        text = self.warnings(data)
        self.assertIn("shots.S02.category: 'drone_thing' is not a known category", text)
        self.assertIn("shots.S02.camera: 'swoop' is not a known camera move", text)
        self.assertIn("shots.S02.size: 'huge' is not a known shot size", text)

    def test_a_promise_nobody_pays_off_is_flagged(self):
        text = self.warnings(tagged())
        self.assertIn("shots.S01.promise: no shot pays it off", text)

    def test_a_paid_off_promise_is_quiet(self):
        data = tagged()
        data["shots"][1]["pays_off"] = "S01"
        self.assertNotIn("pays it off", self.warnings(data))

    def test_pays_off_must_point_at_a_shot_with_a_promise(self):
        data = tagged()
        data["shots"][2]["pays_off"] = "S02"
        self.assertIn("shots.S03.pays_off: S02 has no promise", self.warnings(data))

    def test_product_screen_share_below_target(self):
        data = tagged()
        data["format"]["product_share_min"] = 0.4
        data["shots"][2]["category"] = "room_reveal"  # 5 s of 13 s = 38%
        text = self.warnings(data)
        self.assertIn("the product holds 38% of screen time (target 40%)", text)
        data["shots"][1]["category"] = "room_reveal"  # 10 of 13 s
        self.assertNotIn("screen time", self.warnings(data))

    def test_three_cuts_in_a_row_with_same_size_and_move(self):
        data = tagged()
        for shot in data["shots"]:
            shot.update(camera="push_in", size="ws")
        self.assertIn("S01, S02, S03: three cuts in a row with the same size and camera move (ws, push_in)",
                      self.warnings(data))

    def test_untagged_ai_shots_are_a_todo_not_a_warning(self):
        self.write(shotlist())
        sl = Shotlist(self.project.shotlist(), self.project)
        sl.validate()
        self.assertTrue([t for t in sl.todos if "category" in t])


class GradeTests(Base):
    def spec_with(self, grade):
        spec = {"segments": [{"id": "S03", "card": "#404040", "duration": 1}], "graphics": [], "grade": grade}
        path = self.project.path / "6_Edit" / "Edit_Spec.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(spec), encoding="utf-8")
        return spec

    def test_grade_filter_combines_lut_eq_temperature_and_grain(self):
        from vglib import finish
        lut = self.project.path / "0_Source" / "Look.cube"
        lut.parent.mkdir(exist_ok=True)
        lut.write_text("LUT_3D_SIZE 2\n0 0 0\n1 0 0\n0 1 0\n1 1 0\n0 0 1\n1 0 1\n0 1 1\n1 1 1\n", encoding="utf-8")
        chain = finish.grade_filter(self.project, None, {"lut": "file:0_Source/Look.cube", "contrast": 1.05,
                                                         "saturation": 0.9, "temperature": 5200, "grain": 6})
        self.assertIn("lut3d=file=", chain)
        self.assertIn("eq=contrast=1.05:saturation=0.9", chain)
        self.assertIn("colortemperature=temperature=5200", chain)
        self.assertIn("noise=alls=6:allf=t", chain)
        self.assertIsNone(finish.grade_filter(self.project, None, None))

    def test_bad_grade_is_a_clear_error(self):
        self.spec_with({"lut": "file:0_Source/Missing.cube"})
        with self.assertRaises(UsageError):
            review.edit_spec(self.project)
        self.spec_with({"contrast": "high"})
        with self.assertRaises(UsageError):
            review.edit_spec(self.project)
        self.spec_with({"sparkle": 1})
        with self.assertRaises(UsageError):
            review.edit_spec(self.project)

    def test_a_changed_lut_file_voids_the_visuals(self):
        lut = self.project.path / "0_Source" / "Look.cube"
        lut.parent.mkdir(exist_ok=True)
        lut.write_text("LUT_3D_SIZE 2\n", encoding="utf-8")
        self.images_ready(visuals=False)
        spec = self.write_edit_spec()
        spec["grade"] = {"lut": "file:0_Source/Look.cube"}
        self.write_edit_spec(spec)
        self.visuals_ready()
        lut.write_text("LUT_3D_SIZE 2\n# changed\n", encoding="utf-8")
        found = review.problems(self.project, Shotlist(self.project.shotlist(), self.project),
                                self.project.read_state())
        self.assertIn("grade lut file:0_Source/Look.cube", found[0])

    @unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg")
    def test_grade_changes_the_picture_but_not_the_graphics(self):
        from vglib import finish
        src = self.tmp / "grey.mp4"
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x808080:s=64x64:r=10:d=1",
                     "-pix_fmt", "yuv420p", str(src)])
        out = self.tmp / "graded.mp4"
        chain = finish.grade_filter(self.project, None, {"brightness": 0.2})
        finish._run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", chain, str(out)])
        before = finish._run(["ffmpeg", "-i", str(src), "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG",
                              "-f", "null", "-"])
        after = finish._run(["ffmpeg", "-i", str(out), "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG",
                             "-f", "null", "-"])
        import re
        y0 = float(re.findall(r"YAVG=([\d.]+)", before)[0])
        y1 = float(re.findall(r"YAVG=([\d.]+)", after)[0])
        self.assertGreater(y1, y0 + 20)


if __name__ == "__main__":
    unittest.main()


@unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg")
class RealPhotoFrameTests(Base):
    """A property shot's first frame is the client's real photo, cropped to 9:16, never regenerated."""

    def setUp(self):
        super().setUp()
        from vglib import finish
        photo = self.project.path / "0_Source" / "Facade.png"
        photo.parent.mkdir(exist_ok=True)
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=s=800x450", "-frames:v", "1",
                     str(photo)])
        self.photo = photo
        data = shotlist()
        data["shots"][1]["first_frame"] = {"file": "0_Source/Facade.png", "crop_x": 0.25}
        self.write(data)

    def size(self, path):
        from vglib import finish
        return finish._run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", str(path)]).strip()

    def test_file_frame_is_imported_cropped_without_spend(self):
        from vglib import generate
        sl = Shotlist(self.project.shotlist(), self.project)
        self.assertIn("first:S02", sl.image_targets("frames"))
        generate.run_images(self.project, sl.image_targets("look"))
        review.approve_look(self.project)
        self.fake.created = []
        generate.run_images(self.project, ["first:S02"])
        self.assertEqual(self.fake.created, [], "an imported photo must not call the image model")
        frame = self.project.selected("first:S02")
        self.assertEqual(self.size(frame), "252,450")  # 9:16 window, full height
        generate.run_images(self.project, ["first:S02"])  # same photo, same crop: nothing new
        self.assertEqual(len(self.project.read_state()["outputs"]["first:S02"]["versions"]), 1)

    def test_a_changed_photo_or_crop_makes_a_new_version(self):
        from vglib import generate
        sl = Shotlist(self.project.shotlist(), self.project)
        generate.run_images(self.project, sl.image_targets("look"))
        review.approve_look(self.project)
        generate.run_images(self.project, ["first:S02"])
        data = json.loads(self.project.shotlist_path.read_text())
        data["shots"][1]["first_frame"]["crop_x"] = 0.8
        self.write(data)
        generate.run_images(self.project, ["first:S02"])
        self.assertEqual(len(self.project.read_state()["outputs"]["first:S02"]["versions"]), 2)

    def test_the_real_photo_is_what_the_review_and_the_video_use(self):
        sl = Shotlist(self.project.shotlist(), self.project)
        self.assertEqual(review.still_target(sl.shots["S02"]), "first:S02")
        self.assertIn(("S02 first frame", "first:S02"), review.shot_frames(sl))

    def test_file_frame_validation(self):
        data = json.loads(self.project.shotlist_path.read_text())
        data["shots"][1]["first_frame"] = {"file": "0_Source/Missing.png"}
        self.write(data)
        errors = Shotlist(self.project.shotlist(), self.project).validate()[0]
        self.assertTrue([e for e in errors if "Missing.png" in e])
        data["shots"][1]["first_frame"] = {"file": "0_Source/Facade.png", "crop_x": 1.5}
        self.write(data)
        errors = Shotlist(self.project.shotlist(), self.project).validate()[0]
        self.assertTrue([e for e in errors if "crop_x" in e])
        data["shots"][1]["first_frame"] = {"file": "../outside.png"}
        self.write(data)
        errors = Shotlist(self.project.shotlist(), self.project).validate()[0]
        self.assertTrue([e for e in errors if "inside the project" in e])


class PhotoFrameTodoTests(Base):
    def test_a_real_photo_frame_needs_no_storyboard_panel(self):
        photo = self.project.path / "0_Source" / "Facade.png"
        photo.parent.mkdir(exist_ok=True)
        photo.write_bytes(b"png")
        data = shotlist()
        data["shots"][1]["first_frame"] = {"file": "0_Source/Facade.png"}
        del data["shots"][1]["storyboard"]
        self.write(data)
        sl = Shotlist(self.project.shotlist(), self.project)
        sl.validate()
        self.assertFalse([t for t in sl.todos if t.startswith("shots.S02.storyboard")])


class AudioFirstEditTests(Base):
    """Audio first: one narration track (captioned from its words), sound effects, and cut effects."""

    def write_spec(self, extra):
        spec = {"segments": [{"id": "A", "card": "#404040", "duration": 1},
                             {"id": "B", "card": "#808080", "duration": 1}], "graphics": []}
        spec.update(extra)
        path = self.project.path / "6_Edit" / "Edit_Spec.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(spec), encoding="utf-8")

    def test_bad_narration_sfx_or_transition_is_a_clear_error(self):
        for extra in ({"narration": {"text": "no file"}},
                      {"narration": {"file": "file:6_Edit/Missing.wav", "text": "x"}},
                      {"sfx": [{"file": "file:6_Edit/Missing.wav", "at": 1}]},
                      {"sfx": {"file": "x"}}):
            self.write_spec(extra)
            with self.assertRaises(UsageError, msg=str(extra)):
                review.edit_spec(self.project)
        self.write_spec({})
        spec = json.loads((self.project.path / "6_Edit" / "Edit_Spec.json").read_text())
        spec["segments"][1]["transition_in"] = "spin"
        (self.project.path / "6_Edit" / "Edit_Spec.json").write_text(json.dumps(spec))
        with self.assertRaises(UsageError):
            review.edit_spec(self.project)

    def test_sfx_are_audio_only_but_narration_text_is_part_of_the_visuals(self):
        self.images_ready()
        sl = Shotlist(self.project.shotlist(), self.project)
        spec = json.loads((self.project.path / "6_Edit" / "Edit_Spec.json").read_text())
        wav = self.project.path / "6_Edit" / "Pop.wav"
        wav.write_bytes(b"RIFF")
        spec["sfx"] = [{"file": "file:6_Edit/Pop.wav", "at": 1.0}]
        self.write_edit_spec(spec)
        self.assertEqual(review.problems(self.project, sl, self.project.read_state()), [])
        spec["narration"] = {"file": "file:6_Edit/Pop.wav", "text": "Tebak harga rumah ini."}
        self.write_edit_spec(spec)
        self.assertTrue(review.problems(self.project, sl, self.project.read_state()))

    @unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg")
    def test_narration_words_follow_its_phrases(self):
        from vglib import finish
        wav = self.tmp / "narration.wav"
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                     "aevalsrc='0.5*sin(2*PI*220*t)*(lt(t,1)+between(t,1.6,2.6))':s=48000:d=3", str(wav)])
        words, spans = finish.narration_words(wav, "Satu dua. Tiga empat.", start=10.0)
        self.assertEqual([w["text"] for w in words], ["Satu", "dua.", "Tiga", "empat."])
        self.assertAlmostEqual(words[0]["t0"], 10.0, delta=0.15)
        self.assertAlmostEqual(words[2]["t0"], 11.6, delta=0.2)
        self.assertEqual(len(spans), 2)

    @unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg")
    def test_a_breath_inside_a_phrase_does_not_shift_the_next_phrase(self):
        from vglib import finish
        wav = self.tmp / "breath.wav"
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                     "aevalsrc='0.5*sin(2*PI*220*t)*(lt(t,0.6)+between(t,0.9,1.4)+between(t,2.2,3.0))':s=48000:d=3.3",
                     str(wav)])
        words, spans = finish.narration_words(wav, "Satu dua tiga. Empat lima.", start=10.0)
        self.assertEqual(len(spans), 2)
        self.assertAlmostEqual(words[3]["t0"], 12.2, delta=0.15)  # "Empat" starts after the long pause
        self.assertLess(words[2]["t1"], 11.5)

    @unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg")
    def test_every_photo_piece_has_the_same_pixel_format(self):
        """A JPEG is full range; a slide across it must not come out yuvj420p, or the final render
        re-initialises its filters where the format changes and drops seconds of picture."""
        from vglib import finish
        photo = self.tmp / "photo.jpg"
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=640x360", "-frames:v", "1",
                     str(photo)])
        formats = set()
        for name, pan_x in (("zoom.mp4", None), ("slide.mp4", [0.1, 0.6])):
            finish._image_piece(photo, 0.5, self.tmp / name, [1.0, 1.1], 0, 0, 0, pan_x)
            formats.add(finish._run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                     "stream=pix_fmt,color_range,color_space", "-of", "csv=p=0",
                                     str(self.tmp / name)]).strip())
        # the same tags as every other piece: a change mid-stream re-initialises the render's filters
        self.assertEqual(formats, {"yuv420p,tv,bt709"})

    def test_a_caption_chunk_never_runs_past_a_pause_mark(self):
        """The price must not show before it is said: a chunk ends after . , ? ! : and an ellipsis."""
        from vglib import finish
        words = finish._spread("Harganya… mulai 1,3M-an! Petunjuk 1: seberang MALL sama tol.", [(0.0, 5.0)])
        chunks = [[w["text"] for w in c] for c in finish.caption_chunks(words, 3)]
        self.assertEqual(chunks, [["Harganya…"], ["mulai", "1,3M-an!"], ["Petunjuk", "1:"],
                                  ["seberang", "MALL", "sama"], ["tol."]])

    @unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg")
    def test_flash_starts_white_and_whip_blurs_the_cut(self):
        from vglib import finish
        import re
        a, b = self.tmp / "a.mp4", self.tmp / "b.mp4"
        for path, colour in ((a, "0x303030"), (b, "0x303030")):
            finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=160x284:r=30:d=1",
                         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "1", "-pix_fmt", "yuv420p",
                         "-c:a", "aac", str(path)])
        finish.apply_transition(a, b, "flash", self.tmp)
        stats = finish._run(["ffmpeg", "-i", str(b), "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG",
                             "-frames:v", "1", "-f", "null", "-"])
        self.assertGreater(float(re.findall(r"YAVG=([\d.]+)", stats)[0]), 200)
        self.assertAlmostEqual(finish._duration(b), 1.0, delta=0.1)
        self.assertIn("gblur", finish.transition_filter("whip", "in", 1.0))
        self.assertIn("gblur", finish.transition_filter("whip", "out", 1.0))

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("swiftc"), "needs ffmpeg and swiftc")
    def test_draft_mixes_narration_and_sfx_under_captions(self):
        from vglib import finish
        import re
        audio = self.project.path / "6_Edit" / "1_Audio"
        audio.mkdir(parents=True)
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                     "aevalsrc='0.4*sin(2*PI*200*t)*between(t,0.2,1.2)':s=48000:d=1.5", str(audio / "Narration.wav")])
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                     "aevalsrc='0.6*sin(2*PI*900*t)':s=48000:d=0.2", str(audio / "Pop.wav")])
        self.write_spec({"narration": {"file": "file:6_Edit/1_Audio/Narration.wav", "text": "Tebak harganya."},
                         "sfx": [{"file": "file:6_Edit/1_Audio/Pop.wav", "segment": "B", "at": 0.3}],
                         "output": "Mix_Test_v1.0.mp4"})
        spec = json.loads((self.project.path / "6_Edit" / "Edit_Spec.json").read_text())
        spec["segments"][1]["transition_in"] = "flash"
        (self.project.path / "6_Edit" / "Edit_Spec.json").write_text(json.dumps(spec))
        out = finish.final(self.project, draft=True)
        self.assertAlmostEqual(finish._duration(out), 2.0, delta=0.1)

        def level(start):
            log = finish._run(["ffmpeg", "-ss", str(start), "-t", "0.2", "-i", str(out), "-af", "volumedetect",
                               "-f", "null", "-"])
            return float(re.findall(r"mean_volume: (-?[\d.]+)", log)[0])
        self.assertGreater(level(0.5), -40)   # the narration
        self.assertGreater(level(1.3), -40)   # the pop, 0.3 s into segment B
        self.assertLess(level(1.7), -60)      # nothing after it
        self.assertIn("Tebak", out.with_suffix(".srt").read_text())

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("swiftc"), "needs ffmpeg and swiftc")
    def test_music_can_come_in_late(self):
        from vglib import finish
        import re
        audio = self.project.path / "6_Edit" / "1_Audio"
        audio.mkdir(parents=True)
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=330:d=3:sample_rate=48000",
                     str(audio / "Music.wav")])
        self.write_spec({"music": {"file": "file:6_Edit/1_Audio/Music.wav", "at": 1.2, "volume": 0.5, "fade_in": 0.05,
                                   "fade_out": 0.1}, "output": "Late_Music_v1.0.mp4"})
        out = finish.final(self.project, draft=True)

        def level(start):
            log = finish._run(["ffmpeg", "-ss", str(start), "-t", "0.2", "-i", str(out), "-af", "volumedetect",
                               "-f", "null", "-"])
            return float(re.findall(r"mean_volume: (-?[\d.]+)", log)[0])
        self.assertLess(level(0.6), -60)
        self.assertGreater(level(1.5), -40)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("swiftc"), "needs ffmpeg and swiftc")
    def test_no_picture_is_lost_when_the_sound_is_mixed(self):
        """Every frame must reach the file. Guard only: the Tebak Harga animatic lost 2.5-2.7 s of picture
        (loudnorm in the overlay pass, and a colour-tag change mid-timeline re-initialising the filters),
        a timing race that this small reel does not trigger; the fix was verified on the real reel."""
        from vglib import finish
        audio = self.project.path / "6_Edit" / "1_Audio"
        audio.mkdir(parents=True)
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                     "aevalsrc='0.4*sin(2*PI*200*t)*gt(mod(t,2),0.4)':s=48000:d=26", str(audio / "Voice.wav")])
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=500:d=0.2:sample_rate=48000",
                     str(audio / "Pop.wav")])
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=220:d=30", "-b:a", "128k",
                     str(audio / "Music.mp3")])
        spec = {"segments": [{"id": "S%d" % i, "card": "#%02x%02x80" % (i * 15, 200 - i * 12), "duration": 2}
                             for i in range(14)],
                "graphics": [{"segment": "S%d" % i, "type": "title", "text": "T%d" % i, "at": 0.1} for i in range(14)],
                "grade": {"contrast": 1.04, "saturation": 0.96, "temperature": 5600, "grain": 3},
                "narration": {"file": "file:6_Edit/1_Audio/Voice.wav", "text": "Satu. Dua. Tiga. Empat. Lima."},
                "music": {"file": "file:6_Edit/1_Audio/Music.mp3", "at": 1.5, "volume": 0.3},
                "sfx": [{"file": "file:6_Edit/1_Audio/Pop.wav", "at": 0.5 + 1.8 * k} for k in range(15)],
                "output": "Frames_Test_v1.0.mp4"}
        (self.project.path / "6_Edit" / "Edit_Spec.json").write_text(json.dumps(spec))
        out = finish.final(self.project, draft=True)
        frames = finish._run(["ffprobe", "-v", "error", "-select_streams", "v", "-count_frames", "-show_entries",
                              "stream=nb_read_frames", "-of", "csv=p=0", str(out)]).strip()
        self.assertEqual(int(frames.strip(",")), 840)


@unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg")
class FrameCountTests(unittest.TestCase):
    """Every render is checked: a file with fewer frames than its length needs (a frozen stretch, as in
    the Tebak Harga animatic v3/v4) is refused and removed instead of reaching the human."""

    def test_a_render_missing_frames_is_refused_and_removed(self):
        from vglib import finish
        from vglib.errors import UsageError
        import tempfile
        from pathlib import Path
        tmp = Path(tempfile.mkdtemp())
        clip = tmp / "one_second.mp4"
        finish._run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=160x284:r=30:d=1",
                     "-pix_fmt", "yuv420p", str(clip)])
        finish.check_frames(clip, 1.0)          # 30 of 30 frames: fine
        with self.assertRaises(UsageError):
            finish.check_frames(clip, 2.0)      # a 2 s render with 1 s of frames
        self.assertFalse(clip.exists())
        shutil.rmtree(str(tmp))
