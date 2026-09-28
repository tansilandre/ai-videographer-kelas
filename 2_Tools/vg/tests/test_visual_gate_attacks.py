"""Attacks on the visual review gate from the adversarial review of 2026-09-28 (R01-R11). Each test
states a property the gate must have; all of them failed before the fixes in the same commit.
Nothing here talks to kie.ai: the FakeProvider from test_vg is used.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_vg import Base, shotlist  # noqa: E402
from vglib import generate, review  # noqa: E402
from vglib.errors import ProviderError, Refused, UsageError  # noqa: E402
from vglib.shotlist import Shotlist  # noqa: E402


def sent_files(fake, field="image_urls"):
    """Basenames of the files the fake provider received in the last createTask."""
    payload = fake.created[-1][1]
    value = payload.get(field)
    values = value if isinstance(value, list) else [value]
    return [v.rsplit("/", 1)[-1] for v in values if v]


class R01_LookRefCycle(Base):
    """money-leak: after `vg approve look`, a documented stage run re-rolls the approved style frame."""

    def setUp(self):
        super().setUp()
        data = shotlist()
        data["assets"].append({"id": "Loc_Harbour", "kind": "location", "prompt": "harbour street plate, empty"})
        data["look"]["style_frames"][0]["refs"] = ["Char_Rani_Portrait", "Loc_Harbour"]
        self.write(data)

    def test_stage_all_after_look_approval_keeps_the_approved_style_frame(self):
        sl = Shotlist(self.project.shotlist(), self.project)
        generate.run_images(self.project, sl.image_targets("look"))
        review.approve_look(self.project)
        paid_before = len(self.fake.created)
        refused = None
        try:
            generate.run_images(self.project, sl.image_targets("all"))
        except Refused as exc:
            refused = str(exc).splitlines()[0]
        state = self.project.read_state()
        rerolled = [p["prompt"][:30] for _, p in self.fake.created[paid_before:]]
        self.assertEqual(
            len(state["outputs"]["look:Look_A"]["versions"]), 1,
            "approved style frame re-rolled by `--stage all`; look gate now: %r; mid-run refusal: %r; "
            "images paid in that run: %s" % (review.look_problem(self.project, sl, state), refused, rerolled))

    def test_it_never_settles(self):
        """Approve, run --stage all, re-approve, run --stage all again: every round pays again."""
        sl = Shotlist(self.project.shotlist(), self.project)
        generate.run_images(self.project, sl.image_targets("look"))
        rounds = []
        for _ in range(3):
            review.approve_look(self.project)
            before = len(self.fake.created)
            try:
                generate.run_images(self.project, sl.image_targets("all"))
            except Refused:
                pass
            rounds.append([p["prompt"][:24] for _, p in self.fake.created[before:]])
        self.assertEqual(rounds[2], [], "round 3 still paid for: %s" % rounds[2])


class R02_VideoRefsNotReviewed(Base):
    """human-bypass: an image sent to the video model through video_refs is outside the visuals snapshot."""

    def test_video_ref_image_change_after_visuals_approval_closes_the_gate(self):
        photo = self.project.path / "0_Source" / "Product.jpg"
        photo.parent.mkdir(exist_ok=True)
        photo.write_bytes(b"the product shot the human approved")
        data = shotlist()
        data["shots"].append({"id": "S04", "time": "13-17s", "source": "ai", "summary": "product", "mode": "text",
                              "duration": "4", "storyboard": {"prompt": "product on the table"},
                              "video_prompt": "slow push in on the product",
                              "video_refs": ["file:0_Source/Product.jpg"]})
        self.write(data)
        self.images_ready(visuals=False)
        spec = self.write_edit_spec()
        spec["segments"].append({"id": "S04", "clip": "S04", "out": 4})
        self.write_edit_spec(spec)
        self.visuals_ready()
        photo.write_bytes(b"a different photo nobody reviewed")
        sl = Shotlist(self.project.shotlist(), self.project)
        found = review.problems(self.project, sl, self.project.read_state())
        sent = None
        if not found:
            generate.approve_video(self.project, "S04", False, confirm=63)
            self.fake.created = []
            generate.run_video(self.project, "S04", False)
            sent = sent_files(self.fake)
        self.assertTrue(found, "gate stayed open after the video_ref photo changed; video was sent %s" % sent)


class R03_StaleAnchorNotReviewed(Base):
    """human-bypass: character-mode anchor comes from a first:SID output that is no longer planned, so it is
    not in the visuals snapshot; the animatic/filmstrip show the storyboard panel instead."""

    def test_image_sent_to_character_video_is_the_one_in_the_snapshot(self):
        data = shotlist()
        data["shots"][0]["first_frame"] = {"prompt": "selfie in car, first frame", "refs": ["Char_Rani_Portrait"]}
        self.write(data)
        self.images_ready(visuals=False)
        generate.run_images(self.project, ["first:S01"], new_take=True)  # v2
        del data["shots"][0]["first_frame"]  # plan now anchors S01 on its storyboard panel
        self.write(data)
        self.visuals_ready()  # animatic shows SB_S01 for S01
        generate.create_character(self.project, "Rani")
        with self.project.transaction() as st:  # `vg select --target first:S01 --version 1` after approval
            st["outputs"]["first:S01"]["selected"] = 1
        sl = Shotlist(self.project.shotlist(), self.project)
        found = review.problems(self.project, sl, self.project.read_state())
        state = self.project.read_state()
        job = generate.build_video_job(self.project, sl, sl.shots["S01"], state, generate.shot_spec(sl, sl.shots["S01"]))
        generate.approve_video(self.project, "S01", False, confirm=job["cost"])
        self.fake.created = []
        generate.run_video(self.project, "S01", False)
        sent = sent_files(self.fake)
        self.assertEqual(sent[0], "SB_S01_v1.png",
                         "animatic showed SB_S01_v1.png, video anchor was %s; gate problems: %r" % (sent[0], found))


class R04_StoryboardWithoutPromptNotReviewed(Base):
    """human-bypass: frames shot with first_frame from storyboard whose storyboard prompt was removed after
    generation: the panel is sent as first_frame_url but is not hashed."""

    def test_panel_sent_as_first_frame_is_in_the_snapshot(self):
        self.images_ready(visuals=False)
        generate.run_images(self.project, ["storyboard:S02"], new_take=True)  # v2 selected
        data = shotlist()
        data["shots"][1]["storyboard"] = {"notes": "prompt moved to notes after generation"}
        self.write(data)
        self.write_edit_spec({"segments": [{"id": "S01", "clip": "S01", "out": "speech+0.4"},
                                           {"id": "S02", "clip": "S02"}]})
        self.visuals_ready()  # animatic shows SB_S02_v2 for S02
        with self.project.transaction() as st:
            st["outputs"]["storyboard:S02"]["selected"] = 1
        sl = Shotlist(self.project.shotlist(), self.project)
        found = review.problems(self.project, sl, self.project.read_state())
        self.assertTrue(found, "storyboard:S02 switched to v1 after approval, gate still open (v1 would be sent "
                               "as first_frame_url)")


class R05_NewShotAfterApproval(Base):
    """human-bypass: an AI shot added after `approve visuals` without planned frames leaves the gate open."""

    def test_ai_shot_added_after_approval_closes_the_gate(self):
        self.images_ready()
        data = shotlist()
        data["shots"].append({"id": "S04", "time": "13-17s", "source": "ai", "summary": "crowd", "mode": "text",
                              "duration": "4", "video_prompt": "a crowd cheers on the harbour at night"})
        self.write(data)
        sl = Shotlist(self.project.shotlist(), self.project)
        found = review.problems(self.project, sl, self.project.read_state())
        sent = None
        if not found:
            generate.approve_video(self.project, "S04", False, confirm=63)
            self.fake.created = []
            generate.run_video(self.project, "S04", False)
            sent = len(self.fake.created)
        self.assertTrue(found, "new AI shot S04 (never in the review, not in the edit plan) passed the visual "
                               "gate; %s video task(s) sent" % sent)

    def test_ai_shot_missing_from_edit_plan_is_refused_at_approve_visuals(self):
        self.images_ready(visuals=False)
        self.write_edit_spec({"segments": [{"id": "S01", "clip": "S01", "out": "speech+0.4"}]})  # S02 absent
        self.show_animatic()
        try:
            review.approve_visuals(self.project)
            approved = True
        except (Refused, UsageError):
            approved = False
        self.assertFalse(approved, "visuals approved although AI shot S02 is not in the edit plan/animatic")


class R06_CaptionTextNotHashed(Base):
    """human-bypass (text): captions the animatic shows come from Shotlist dialogue, which is not hashed."""

    def test_dialogue_change_after_approval_closes_the_gate(self):
        self.images_ready()
        data = shotlist()
        new = "Harga rumah di sini mulai 900 juta, cek sekarang juga!"
        data["shots"][0]["dialogue"] = new
        data["shots"][0]["video_prompt"] = 'she says "%s". Avoid: morphing' % new
        self.write(data)
        sl = Shotlist(self.project.shotlist(), self.project)
        self.assertTrue(review.problems(self.project, sl, self.project.read_state()),
                        "S01 caption text (shown in the animatic) changed, visuals approval still current")


class R07_AnimaticSnapshotTakenBeforeRender(Base):
    """human-bypass (race): the animatic records the snapshot computed BEFORE rendering and never re-checks."""

    def test_change_during_render_is_not_recorded_as_seen(self):
        from vglib import finish
        self.images_ready(visuals=False)
        generate.run_images(self.project, ["storyboard:S02"], new_take=True)  # v2 selected
        self.write_edit_spec()
        rendered = {}
        original = finish.final

        def render(project, draft=False, animatic=False):
            with project.transaction() as st:  # a concurrent `vg select ... --version 1` lands mid-render
                st["outputs"]["storyboard:S02"]["selected"] = 1
            rendered["S02"] = project.selected("storyboard:S02").name  # what ffmpeg reads
            out = project.path / "6_Edit" / "Animatic_Test_v1.mp4"
            out.write_bytes(b"mp4")
            return out
        finish.final = render
        try:
            with self.assertRaises(UsageError):  # the change mid-render is detected, nothing recorded
                finish.animatic(self.project)
        finally:
            finish.final = original
        with self.project.transaction() as st:  # and back
            st["outputs"]["storyboard:S02"]["selected"] = 2
        with self.assertRaises(Refused, msg="approved SB_S02_v2 but the animatic rendered %s" % rendered.get("S02")):
            review.approve_visuals(self.project)


class R08_AnimaticMissing(Base):
    """low: approve visuals accepts an animatic record whose file does not exist."""

    def test_approval_needs_the_animatic_file(self):
        self.images_ready(visuals=False)
        self.write_edit_spec()
        sl = Shotlist(self.project.shotlist(), self.project)
        items = review.visual_items(self.project, sl, self.project.read_state())
        missing = self.project.path / "6_Edit" / "Animatic_Test_v1.mp4"
        review.record_animatic(self.project, missing, review.snapshot(items))  # recorded, never written
        self.assertFalse(missing.exists())
        with self.assertRaises((Refused, UsageError)):
            review.approve_visuals(self.project)


class R09_Crashes(Base):
    """crash: shapes an agent can plausibly write take down status/board/video/animatic with a traceback."""

    def run_cli(self, *argv):
        from vglib import cli
        return cli.main(list(argv) + ["-p", str(self.project.path)])

    def test_status_with_background_as_string(self):
        self.images_ready(visuals=False)
        self.write_edit_spec({"segments": [{"id": "X", "duration": 2, "background": "storyboard:S02"}]})
        self.assertIn(self.run_cli("status"), (0, 1, 2))

    def test_board_with_cover_true(self):
        self.images_ready(visuals=False)
        self.write_edit_spec({"segments": [{"id": "S01", "clip": "S01", "out": 3, "cover": True}]})
        self.assertIn(self.run_cli("board"), (0, 1, 2))

    def test_status_with_segments_null(self):
        self.images_ready(visuals=False)
        self.write_edit_spec({"segments": None})
        self.assertIn(self.run_cli("status"), (0, 1, 2))

    def test_animatic_with_cover_without_image(self):
        from vglib import finish
        self.images_ready(visuals=False)
        self.write_edit_spec({"segments": [{"id": "S01", "clip": "S01", "out": 3, "cover": {"blur": 10}}]})
        with self.assertRaises(UsageError):
            finish.animatic(self.project)

    def test_animatic_with_still_as_object(self):
        from vglib import finish
        self.images_ready(visuals=False)
        self.write_edit_spec({"segments": [{"id": "X", "still": {"image": "storyboard:S02"}, "duration": 2}]})
        with self.assertRaises(UsageError):
            finish.animatic(self.project)

    def test_look_graphics_as_object_is_a_validation_error(self):
        data = shotlist()
        data["look"]["graphics"] = {"font": "Inter", "accent": "#FF5A1F"}
        self.write(data)
        self.assertIn(self.run_cli("validate"), (0, 1))

    def test_style_frame_refs_null_is_a_validation_error(self):
        data = shotlist()
        data["look"]["style_frames"][0]["refs"] = None
        self.write(data)
        self.assertIn(self.run_cli("validate"), (0, 1))

    def test_status_with_invalid_edit_plan_still_reports(self):
        """spec: `vg board` never refuses, it reports the gate state."""
        path = self.project.path / "6_Edit" / "Edit_Spec.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text("{oops", encoding="utf-8")
        self.assertEqual(self.run_cli("board"), 0)


class R10_StyleFrameIds(Base):
    """validation gap (new target kind): style frame ids are used as file names unchecked."""

    def test_dotdot_id_writes_outside_the_project(self):
        data = shotlist()
        data["look"]["style_frames"][0]["id"] = "../../Escaped"
        self.write(data)
        errors = Shotlist(self.project.shotlist(), self.project).validate()[0]
        if not errors:
            generate.run_images(self.project, ["asset:Char_Rani_Portrait"])
            generate.run_images(self.project, ["look:../../Escaped"])
        escaped = self.project.path.parent / "Escaped_v1.png"
        self.assertFalse(escaped.exists(), "validate() errors=%r; paid image written outside the project: %s"
                         % (errors, escaped))

    def test_slash_id_leaves_a_paid_task_uncollectable(self):
        data = shotlist()
        data["look"]["style_frames"][0]["id"] = "Look/A"
        self.write(data)
        errors = Shotlist(self.project.shotlist(), self.project).validate()[0]
        fake_download = self.fake.download

        def kie_like_download(url, dest):  # providers/kie.py wraps OSError into ProviderError after retries
            try:
                fake_download(url, dest)
            except OSError as exc:
                raise ProviderError("Download failed for %s: %s" % (url, exc))
        self.fake.download = kie_like_download
        if not errors:
            generate.run_images(self.project, ["asset:Char_Rani_Portrait"])
            try:
                generate.run_images(self.project, ["look:Look/A"])
            except Exception:
                pass
        state = self.project.read_state()
        stuck = [t["state"] for t in state["tasks"] if t["target"] == "look:Look/A"]
        self.assertTrue(errors, "validate() accepted id 'Look/A'; paid task state(s): %s, output: %s"
                        % (stuck, state["outputs"].get("look:Look/A")))


class R02b_AssetVideoRefReRolled(Base):
    """human-bypass, same root cause as R02 via a routine command: re-rolling an asset sheet used as a video_ref."""

    def test_asset_video_ref_reroll_after_visuals_approval_closes_the_gate(self):
        data = shotlist()
        data["assets"].append({"id": "Prod_Box", "kind": "product", "prompt": "product box on white"})
        data["shots"].append({"id": "S04", "time": "13-17s", "source": "ai", "summary": "product", "mode": "text",
                              "duration": "4", "storyboard": {"prompt": "product on the table"},
                              "video_prompt": "slow push in on the product", "video_refs": ["Prod_Box"]})
        self.write(data)
        self.images_ready(visuals=False)
        spec = self.write_edit_spec()
        spec["segments"].append({"id": "S04", "clip": "S04", "out": 4})
        self.write_edit_spec(spec)
        self.visuals_ready()
        generate.run_images(self.project, ["asset:Prod_Box"], new_take=True)  # v2, never reviewed
        sl = Shotlist(self.project.shotlist(), self.project)
        found = review.problems(self.project, sl, self.project.read_state())
        sent = None
        if not found:
            generate.approve_video(self.project, "S04", False, confirm=63)
            self.fake.created = []
            generate.run_video(self.project, "S04", False)
            sent = sent_files(self.fake)
        self.assertTrue(found, "gate open after asset:Prod_Box re-roll; video sent %s" % sent)


class R11_FromStoryboardWithPrompt(Base):
    """crash/dead end: first_frame {"from": "storyboard", "prompt": ...} passes validate, but `--stage frames`
    fails on it and approve visuals can never pass (it waits for a first:SID image nothing can make)."""

    def test_validate_flags_the_contradiction(self):
        data = shotlist()
        data["shots"][1]["first_frame"] = {"from": "storyboard", "prompt": "aerial start"}
        self.write(data)
        sl = Shotlist(self.project.shotlist(), self.project)
        errors = sl.validate()[0]
        stage_error = None
        if not errors:
            generate.run_images(self.project, sl.image_targets("look"))
            review.approve_look(self.project)
            try:
                generate.run_images(self.project, sl.image_targets("frames"))
            except UsageError as exc:
                stage_error = str(exc)
        self.assertTrue(errors, "validate() passed; `vg image --stage frames` then fails: %r" % stage_error)
