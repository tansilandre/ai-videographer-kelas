"""Running the harness from an agent app like WorkBuddy with a smaller model (Andre, 2026-09-29): the human
approves by clicking on the review page (VG_APPROVAL_MODE=page), the command line never approves, and an
agent's shell never sees an approval code.

Run from the workspace root:  python3 -m unittest discover -s 2_Tools/vg/tests -v
"""
import contextlib
import io
import json
import os
import re
import sys
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_vg import Base, shotlist  # noqa: E402  (fake provider; fixture shot list with a look block)
from vglib import cli, config, generate, next_step, review, review_page  # noqa: E402
from vglib.errors import Refused  # noqa: E402
from vglib.shotlist import Shotlist  # noqa: E402


class PageHelpers:
    def seen(self):
        return review_page.page_data(self.project)["seen"]

    def look_ready(self):
        sl = Shotlist(self.project.shotlist(), self.project)
        generate.run_images(self.project, sl.image_targets("look"))

    def gates(self):
        return {g["name"]: g["ok"] for g in review_page.page_data(self.project)["gates"]}

    def page(self):
        config._env_cache["VG_APPROVAL_MODE"] = "page"

    def video_rows(self):
        return {row["shot"]: row for row in review_page.page_data(self.project)["video"]["rows"]}


class PageApprovalTests(PageHelpers, Base):
    def test_the_command_line_cannot_approve_the_look(self):
        self.look_ready()
        self.page()
        with self.assertRaises(Refused) as ctx:
            review.approve_look(self.project)
        self.assertIn("review page", str(ctx.exception))
        self.assertIn("vg review", str(ctx.exception).replace("vg.py review", "vg review"))
        self.assertNotIn("look", self.project.read_state()["approvals"])

    def test_a_click_on_the_page_approves_the_look(self):
        self.look_ready()
        self.page()
        review_page.approve(self.project, "look", self.seen())
        self.assertTrue(self.gates()["look"])

    def test_a_click_on_the_page_approves_the_reel(self):
        self.images_ready(visuals=False)
        self.write_edit_spec()
        self.show_animatic()
        self.page()
        with self.assertRaises(Refused):
            review.approve_visuals(self.project)
        review_page.approve(self.project, "visuals", self.seen())
        self.assertTrue(self.gates()["visuals"])

    def test_the_command_line_cannot_approve_video(self):
        self.images_ready()
        self.page()
        cost = self.video_rows()["S02"]["cost"]
        with self.assertRaises(Refused) as ctx:
            generate.approve_video(self.project, "S02", False, confirm=cost)
        self.assertIn("review page", str(ctx.exception))
        self.assertEqual(self.project.read_state()["approvals"]["video"], {})

    def test_the_page_shows_each_clip_and_its_cost_once_the_reel_is_approved(self):
        self.images_ready(visuals=False)
        self.page()
        self.assertFalse(review_page.page_data(self.project)["video"]["ready"])
        self.write_edit_spec()
        self.show_animatic()
        review_page.approve(self.project, "visuals", self.seen())
        video = review_page.page_data(self.project)["video"]
        self.assertTrue(video["ready"])
        rows = self.video_rows()
        self.assertEqual(sorted(rows), ["S01", "S02"])
        self.assertGreater(rows["S02"]["cost"], 0)
        self.assertEqual(rows["S02"]["status"], "not made")
        self.assertIn("committed", video["budget"])

    def test_a_click_approves_the_clip_for_the_cost_shown_and_the_clip_can_run(self):
        self.images_ready()
        self.page()
        cost = self.video_rows()["S02"]["cost"]
        with self.assertRaises(Refused):  # a total other than the one shown
            review_page.approve_video(self.project, ["S02"], cost + 1)
        review_page.approve_video(self.project, ["S02"], cost)
        self.assertEqual(self.video_rows()["S02"]["status"], "approved")
        generate.run_video(self.project, "S02", False)
        self.assertEqual(self.video_rows()["S02"]["status"], "made v1")

    def test_a_new_take_of_a_made_clip_needs_its_own_click(self):
        self.images_ready()
        self.page()
        cost = self.video_rows()["S02"]["cost"]
        review_page.approve_video(self.project, ["S02"], cost)
        generate.run_video(self.project, "S02", False)
        review_page.approve_video(self.project, ["S02"], cost, new_take=True)
        generate.run_video(self.project, "S02", False, new_take=True)
        self.assertEqual(self.video_rows()["S02"]["status"], "made v2")

    def test_video_is_not_clickable_before_the_reel_is_approved(self):
        self.images_ready(visuals=False)
        self.page()
        with self.assertRaises(Refused):
            review_page.approve_video(self.project, ["S02"], 63)

    def test_terminal_mode_page_still_refuses_video_clicks(self):
        self.images_ready()
        config._env_cache["VG_APPROVAL_MODE"] = "terminal"
        with self.assertRaises(Refused):
            review_page.approve_video(self.project, ["S02"], 63)

    def test_summary_after_a_click_names_the_approved_clips(self):
        self.images_ready()
        self.page()
        cost = self.video_rows()["S02"]["cost"]
        review_page.approve_video(self.project, ["S02"], cost)
        self.assertIn("APPROVED  video S02 (%g credits): run vg video -p %s --shots S02"
                      % (cost, self.project.name), review_page.summary(self.project))

    def test_summary_waits_for_a_click_not_a_terminal_command(self):
        self.images_ready(visuals=False)
        self.write_edit_spec()
        self.show_animatic()
        self.page()
        last = review_page.summary(self.project)[-1]
        self.assertNotIn("terminal", last)
        self.assertIn("ask the human", last)


class PageHtmlTests(unittest.TestCase):
    def test_the_page_offers_video_clicks_with_a_confirm_step(self):
        html = review_page.PAGE_HTML
        self.assertIn('"/api/approve_video"', html)
        self.assertIn("window.confirm(", html, "a spend click asks once more before it approves")
        self.assertIn('state.mode === "page"', html, "page mode shows the Approve buttons")


class DetachedReviewTests(PageHelpers, Base):
    """An agent app's shell call must return: the page runs on in its own process, the agent reads the
    human's clicks and notes later, and can stop the page."""

    def vg(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.main(list(argv))
        return code, out.getvalue()

    def get_state(self, url):
        base, token = url.split("/?t=")
        with urllib.request.urlopen(base + "/api/state?t=" + token, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def test_summary_prints_gates_and_notes_without_serving(self):
        self.look_ready()
        review_page.set_note(self.project, "look:Look_A", "lebih hangat")
        code, out = self.vg("review", "-p", str(self.project.path), "--summary")
        self.assertEqual(code, 0)
        self.assertIn("NOTE  look:Look_A  lebih hangat", out)
        self.assertIn("GATE  look:", out)

    def test_detach_returns_at_once_and_the_page_keeps_serving_until_stopped(self):
        self.look_ready()
        code, out = self.vg("review", "-p", str(self.project.path), "--detach", "--no-open")
        self.addCleanup(self.vg, "review", "-p", str(self.project.path), "--stop")
        self.assertEqual(code, 0, out)
        url = re.search(r"Review page: (http\S+)", out).group(1)
        self.assertEqual(self.get_state(url)["project"], self.project.name)
        code, again = self.vg("review", "-p", str(self.project.path), "--detach", "--no-open")
        self.assertIn(url, again, "a second --detach reuses the open page")
        self.vg("review", "-p", str(self.project.path), "--stop")
        with self.assertRaises((urllib.error.URLError, ConnectionError, OSError)):
            self.get_state(url)


class NextStepTests(PageHelpers, Base):
    """`vg next`: one step at a time, with the exact command, and a stop wherever a human decides."""

    def setUp(self):
        super().setUp()
        data = shotlist()
        s01 = data["shots"][0]  # frames mode: no identity to create (the workshop path)
        for key in ("characters", "dialogue"):
            s01.pop(key)
        s01.update({"mode": "frames", "video_prompt": "she walks to the gate, handheld"})
        self.write(data)
        self.page()

    def images_ready(self, visuals=True):
        """The fixture approves through the command line (chat mode); the tests then run in page mode."""
        config._env_cache["VG_APPROVAL_MODE"] = "chat"
        super().images_ready(visuals)
        self.page()

    def next(self):
        lines = next_step.steps(self.project)
        return {tag: text for tag, text in lines}, lines

    def run_line(self):
        step, lines = self.next()
        self.assertIn("RUN", step, lines)
        return step["RUN"]

    def test_first_the_style_frames(self):
        self.assertIn("vg.py image -p %s --stage look" % self.project.name, self.run_line())
        self.assertIn("TIME", self.next()[0])

    def test_then_the_human_reviews_the_look_on_the_page(self):
        self.look_ready()
        step, lines = self.next()
        self.assertIn("review -p %s --detach" % self.project.name, step["RUN"])
        self.assertIn("Approve look", step["ASK"])

    def test_notes_come_before_another_review_and_count_once_acted_on(self):
        self.look_ready()
        review_page.set_note(self.project, "look:Look_A", "lebih hangat")
        step, lines = self.next()
        self.assertIn("lebih hangat", "\n".join(text for _, text in lines))
        self.assertNotIn("RUN", step)
        self.assertIn("look:Look_A", step["DO"])
        generate.run_images(self.project, ["look:Look_A"], new_take=True)  # the agent re-rolled it
        self.assertIn("--detach", self.run_line())

    def test_after_the_look_the_remaining_images(self):
        self.look_ready()
        review.approve_look(self.project, via_page=True)
        self.assertIn("--stage refs", self.run_line())

    def test_then_the_edit_plan_then_the_animatic_then_the_reel_review(self):
        self.images_ready(visuals=False)
        step, lines = self.next()
        self.assertIn("Edit_Spec.json", step["WRITE"])
        self.assertIn("vg-edit", step["WRITE"])
        self.write_edit_spec()
        self.assertIn("edit animatic", self.run_line())
        self.show_animatic()
        step, lines = self.next()
        self.assertIn("--detach", step["RUN"])
        self.assertIn("Approve reel", step["ASK"])

    def test_video_starts_with_a_pilot_the_human_clicks(self):
        self.images_ready()
        step, lines = self.next()
        cost = self.video_rows()["S01"]["cost"]
        self.assertIn("S01", step["ASK"])
        self.assertIn("%g credits" % cost, step["ASK"])
        self.assertIn("Video", step["ASK"])
        review_page.approve_video(self.project, ["S01"], cost)
        self.assertIn("video -p %s --shots S01" % self.project.name, self.run_line())

    def test_after_the_pilot_the_rest_then_the_final_edit(self):
        self.images_ready()
        rows = self.video_rows()
        review_page.approve_video(self.project, ["S01"], rows["S01"]["cost"])
        generate.run_video(self.project, "S01", False)
        step, lines = self.next()
        self.assertIn("S02", step["ASK"])
        self.assertNotIn("pilot", step["ASK"])
        review_page.approve_video(self.project, ["S02"], rows["S02"]["cost"])
        generate.run_video(self.project, "S02", False)
        self.assertIn("edit final", self.run_line())

    def test_terminal_mode_hands_the_human_the_approve_command(self):
        self.images_ready()
        config._env_cache["VG_APPROVAL_MODE"] = "terminal"
        step, lines = self.next()
        self.assertIn("approve video -p %s --shots S01 --confirm" % self.project.name, step["ASK"])
        self.assertIn("own terminal", step["ASK"])

    def test_the_command_prints_one_step(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.main(["next", "-p", str(self.project.path)])
        self.assertEqual(code, 0)
        self.assertTrue(out.getvalue().startswith("STAGE"), out.getvalue())
        self.assertIn("RUN", out.getvalue())


class DoctorTests(Base):
    def doctor(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cli.main(["doctor"])
        return out.getvalue()

    def test_doctor_names_the_approval_mode_and_recommends_clicks_for_agent_apps(self):
        config._env_cache["VG_APPROVAL_MODE"] = "chat"
        self.assertRegex(self.doctor(), r"warn\s+approval mode\s+chat.*page")
        config._env_cache["VG_APPROVAL_MODE"] = "page"
        self.assertRegex(self.doctor(), r"ok\s+approval mode\s+page")

    def test_doctor_checks_the_skills_folder_workbuddy_reads(self):
        self.assertRegex(self.doctor(), r"skills \(WorkBuddy\)\s+.*\.codebuddy/skills")


class AgentShellTests(PageHelpers, Base):
    """WorkBuddy runs the agent's commands in a real pseudo-terminal: /dev/tty opens there, so terminal mode
    would print the approval code where the model reads it. Its shell is marked by CODEBUDDY_TOOL_CALL_ID."""

    def setUp(self):
        super().setUp()
        self.addCleanup(os.environ.pop, "CODEBUDDY_TOOL_CALL_ID", None)
        original = generate._open_tty
        self.addCleanup(setattr, generate, "_open_tty", original)
        self.opened = []
        generate._open_tty = lambda: self.opened.append(True)

    def test_terminal_mode_refuses_in_an_agent_shell_without_opening_the_terminal(self):
        self.look_ready()
        config._env_cache["VG_APPROVAL_MODE"] = "terminal"
        os.environ["CODEBUDDY_TOOL_CALL_ID"] = "call_1"
        with self.assertRaises(Refused) as ctx:
            review.approve_look(self.project)
        self.assertIn("own terminal", str(ctx.exception))
        self.assertEqual(self.opened, [])
        self.assertNotIn("look", self.project.read_state()["approvals"])


if __name__ == "__main__":
    unittest.main()
