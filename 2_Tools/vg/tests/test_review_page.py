"""Offline tests for the review page (`vg review`). No network: the fake provider from test_vg.

Run from the workspace root:  python3 -m unittest discover -s 2_Tools/vg/tests -v
"""
import json
import unittest
import queue
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_vg import Base  # noqa: E402  (fake provider; fixture shot list with a look block)
from vglib import board, config, generate, review  # noqa: E402
from vglib.shotlist import Shotlist  # noqa: E402


class BeatTests(Base):
    def sl(self):
        return Shotlist(self.project.shotlist(), self.project)

    def beats(self):
        return review.reel_beats(self.project, self.sl(), self.project.read_state(), review.edit_spec(self.project))

    def test_segment_image_follows_the_animatic_rules(self):
        self.images_ready(visuals=False)
        state = self.project.read_state()
        clip = review.segment_image(self.project, self.sl(), state, {"id": "S01", "clip": "S01"})
        self.assertEqual(clip, self.project.selected("storyboard:S01", state))
        background = review.segment_image(self.project, self.sl(), state,
                                          {"id": "S03", "background": {"image": "storyboard:S02"}})
        self.assertEqual(background, self.project.selected("storyboard:S02", state))
        self.assertIsNone(review.segment_image(self.project, self.sl(), state, {"id": "X", "duration": 2}))
        self.assertIsNone(review.segment_image(self.project, self.sl(), state, {"id": "X", "clip": "S99"}))

    def test_reel_beats_from_the_edit_plan_then_the_shot_list(self):
        self.images_ready(visuals=False)
        beats = self.beats()
        self.assertEqual([b["id"] for b in beats], ["S01", "S02", "S03"])  # no edit plan: shot list
        self.assertEqual(beats[2]["placeholder"], "motion graphic")
        self.assertIsNone(beats[2]["shot"])
        self.write_edit_spec()
        beats = self.beats()
        self.assertEqual([b["id"] for b in beats], ["S01", "S02", "S03"])
        self.assertEqual(beats[2]["text"], "TOL 2 KM")
        self.assertEqual(beats[1]["shot"], "S02")

    def test_board_still_renders_the_filmstrip(self):
        self.images_ready(visuals=False)
        self.write_edit_spec()
        text = Path(board.build(self.project)).read_text(encoding="utf-8")
        self.assertIn("Filmstrip", text)
        self.assertIn("TOL 2 KM", text)

    def test_board_reports_a_broken_edit_plan_and_shows_the_shot_list(self):
        self.images_ready(visuals=False)
        (self.project.path / "6_Edit").mkdir(exist_ok=True)
        (self.project.path / "6_Edit" / "Edit_Spec.json").write_text('{"segments": "nope"}', encoding="utf-8")
        text = Path(board.build(self.project)).read_text(encoding="utf-8")
        self.assertIn("Edit plan cannot be read", text)
        self.assertIn("hook", text)  # S01's summary from the shot list


from vglib import review_page  # noqa: E402


class PageDataTests(Base):
    def test_empty_project_has_nothing_to_review(self):
        data = review_page.page_data(self.project)
        self.assertEqual(review_page.allowed_files(data), set())
        self.assertEqual([c["item"] for c in data["look"]["frames"]], ["look:Look_A"])

    def test_page_shows_look_sheets_and_reel(self):
        self.images_ready(visuals=False)
        self.write_edit_spec()
        data = review_page.page_data(self.project)
        self.assertTrue(data["look"]["text"]["world"].startswith("Harbor Homes"))
        self.assertEqual([c["label"] for c in data["refs"]], ["Char_Rani_Portrait", "Char_Rani_Turnaround"])
        self.assertEqual([b["item"] for b in data["reel"]], ["beat:S01", "beat:S02", "beat:S03"])
        self.assertEqual([f["label"] for f in data["reel"][1]["frames"]], ["S02 storyboard", "S02 last frame"])
        self.assertEqual({g["name"]: g["ok"] for g in data["gates"]}, {"look": True, "visuals": False})
        self.assertEqual(data["mode"], "chat")
        self.assertIn("approve visuals -p", data["commands"]["visuals"])
        self.assertIsNone(data["animatic"])
        self.assertIsNone(data["edit_error"])
        files = review_page.allowed_files(data)
        self.assertIn(data["reel"][1]["image"], files)
        self.assertNotIn("project.json", files)

    def test_takes_list_every_version(self):
        self.images_ready(visuals=False)
        generate.run_images(self.project, ["storyboard:S02"], new_take=True)
        take = review_page.page_data(self.project)["reel"][1]["frames"][0]
        self.assertEqual([v["v"] for v in take["versions"]], [1, 2])
        self.assertEqual(take["selected"], 2)

    def test_animatic_marked_out_of_date_after_a_new_take(self):
        self.images_ready(visuals=False)
        self.write_edit_spec()
        self.show_animatic()
        self.assertTrue(review_page.page_data(self.project)["animatic"]["current"])
        generate.run_images(self.project, ["storyboard:S02"], new_take=True)
        self.assertFalse(review_page.page_data(self.project)["animatic"]["current"])

    def test_broken_edit_plan_is_reported_and_the_shot_list_shown(self):
        self.images_ready(visuals=False)
        (self.project.path / "6_Edit").mkdir(exist_ok=True)
        (self.project.path / "6_Edit" / "Edit_Spec.json").write_text("{not json", encoding="utf-8")
        data = review_page.page_data(self.project)
        self.assertIn("not valid JSON", data["edit_error"])
        self.assertEqual([b["id"] for b in data["reel"]], ["S01", "S02", "S03"])


from vglib.errors import Refused, UsageError  # noqa: E402


class ActionHelpers:
    def seen(self):
        return review_page.page_data(self.project)["seen"]

    def note(self, item):
        return (self.project.read_state().get(review_page.NOTES) or {}).get(item)

    def look_ready(self):
        sl = Shotlist(self.project.shotlist(), self.project)
        generate.run_images(self.project, sl.image_targets("look"))

    def gates(self):
        return {g["name"]: g["ok"] for g in review_page.page_data(self.project)["gates"]}


class ActionTests(ActionHelpers, Base):
    def test_note_saved_in_utf8_cleared_and_checked(self):
        self.images_ready(visuals=False)
        review_page.set_note(self.project, "beat:S02", "Rani harus jalan, bukan pose 🙏")
        self.assertEqual(self.note("beat:S02")["note"], "Rani harus jalan, bukan pose 🙏")
        review_page.set_note(self.project, "beat:S02", "   ")
        self.assertIsNone(self.note("beat:S02"))
        with self.assertRaises(UsageError):
            review_page.set_note(self.project, "beat:S99", "x")
        review_page.set_note(self.project, "asset:Char_Rani_Portrait", "x" * 5000)
        self.assertEqual(len(self.note("asset:Char_Rani_Portrait")["note"]), review_page.MAX_NOTE)

    def test_switching_takes_voids_and_restores_the_look_approval(self):
        self.images_ready(visuals=False)
        generate.run_images(self.project, ["look:Look_A"], new_take=True)  # made after the page loaded
        self.assertFalse(self.gates()["look"])
        review_page.select_take(self.project, "look:Look_A", 1)
        self.assertTrue(self.gates()["look"])
        with self.assertRaises(UsageError):
            review_page.select_take(self.project, "look:Look_A", 9)
        with self.assertRaises(UsageError):
            review_page.select_take(self.project, "clip:S01", 1)
        with self.assertRaises(UsageError):
            review_page.select_take(self.project, "look:Look_A", "two")

    def test_approve_in_chat_mode_records_and_clears_look_notes(self):
        self.look_ready()
        review_page.set_note(self.project, "look:Look_A", "warmer")
        review_page.approve(self.project, "look", self.seen())
        self.assertTrue(self.gates()["look"])
        self.assertIsNone(self.note("look:Look_A"))

    def test_approve_in_terminal_mode_shows_the_command_and_records_nothing(self):
        self.look_ready()
        config._env_cache["VG_APPROVAL_MODE"] = "terminal"
        with self.assertRaises(Refused) as ctx:
            review_page.approve(self.project, "look", self.seen())
        self.assertIn("approve look -p", str(ctx.exception))
        self.assertNotIn("look", self.project.read_state()["approvals"])

    def test_gate_refusal_is_passed_through(self):
        self.images_ready(visuals=False)
        self.write_edit_spec()
        with self.assertRaises(Refused) as ctx:
            review_page.approve(self.project, "visuals", self.seen())
        self.assertIn("animatic", str(ctx.exception))
        with self.assertRaises(UsageError):
            review_page.approve(self.project, "video", self.seen())

    def test_approve_visuals_clears_beat_and_sheet_notes(self):
        self.images_ready(visuals=False)
        self.write_edit_spec()
        self.show_animatic()
        review_page.set_note(self.project, "beat:S02", "tighter")
        review_page.set_note(self.project, "asset:Char_Rani_Portrait", "hair down")
        review_page.approve(self.project, "visuals", self.seen())
        self.assertEqual(self.project.read_state()[review_page.NOTES], {})
        self.assertTrue(all(self.gates().values()))

    def test_summary_names_gates_notes_and_next_step(self):
        self.images_ready(visuals=False)
        review_page.set_note(self.project, "beat:S02", "make her\nmid-step")
        lines = review_page.summary(self.project)
        self.assertIn("GATE  look: approved", lines)
        self.assertIn("NOTE  beat:S02  make her / mid-step", lines)
        self.assertTrue(lines[-1].startswith("NEXT  act on the notes"))
        review_page.set_note(self.project, "beat:S02", "")
        self.write_edit_spec()
        self.show_animatic()
        review_page.approve(self.project, "visuals", self.seen())
        self.assertTrue(review_page.summary(self.project)[-1].startswith("NEXT  both gates approved"))


class ServerHelpers:
    def start(self):
        server = review_page.ReviewServer(self.project)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return server

    def call(self, server, path, body=None, token=True, headers=None, raw=None):
        h = dict(headers or {})
        if token:
            h["X-VG-Token"] = server.token if token is True else token
        data = raw if raw is not None else (None if body is None else json.dumps(body).encode("utf-8"))
        if data is not None:
            h["Content-Type"] = "application/json"
        req = urllib.request.Request("http://127.0.0.1:%d%s" % (server.server_address[1], path), data=data,
                                     headers=h, method="POST" if data is not None else "GET")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, resp.read(), resp.headers
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(), exc.headers


class ServerTests(ServerHelpers, Base):
    def test_token_required(self):
        server = self.start()
        self.assertEqual(self.call(server, "/api/state", token=False)[0], 403)
        self.assertEqual(self.call(server, "/api/state", token="wrong")[0], 403)
        self.assertEqual(self.call(server, "/?t=wrong", token=False)[0], 403)
        self.assertEqual(self.call(server, "/api/note", {"item": "beat:S02", "note": "x"}, token=False)[0], 403)
        status, body, _ = self.call(server, "/api/state")
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)["ok"])
        status, body, _ = self.call(server, "/?t=%s" % server.token, token=False)
        self.assertEqual(status, 200)
        self.assertIn(b"Done, back to the agent", body)

    def test_only_files_on_the_page_are_served(self):
        self.images_ready(visuals=False)
        server = self.start()
        rel = review_page.page_data(self.project)["look"]["frames"][0]["versions"][0]["path"]
        status, body, _ = self.call(server, "/file?path=%s" % urllib.parse.quote(rel))
        self.assertEqual((status, body), (200, (self.project.path / rel).read_bytes()))
        for bad in ("project.json", "../../etc/passwd", "1_Script/Shotlist.json", ""):
            self.assertEqual(self.call(server, "/file?path=%s" % urllib.parse.quote(bad))[0], 404, bad)

    def test_video_byte_ranges_for_safari(self):
        self.images_ready(visuals=False)
        self.write_edit_spec()
        self.show_animatic()
        (self.project.path / "6_Edit" / "Animatic_Test_v1.mp4").write_bytes(b"0123456789")
        server = self.start()
        path = "/file?path=6_Edit/Animatic_Test_v1.mp4"
        status, body, headers = self.call(server, path, headers={"Range": "bytes=2-5"})
        self.assertEqual((status, body), (206, b"2345"))
        self.assertEqual(headers["Content-Range"], "bytes 2-5/10")
        self.assertEqual(headers["Accept-Ranges"], "bytes")
        self.assertEqual(self.call(server, path, headers={"Range": "bytes=8-"})[1], b"89")
        self.assertEqual(self.call(server, path, headers={"Range": "bytes=-3"})[1], b"789")
        self.assertEqual(self.call(server, path, headers={"Range": "bytes=20-30"})[0], 416)

    def test_api_actions_and_errors(self):
        self.images_ready(visuals=False)
        server = self.start()
        status, body, _ = self.call(server, "/api/note", {"item": "beat:S02", "note": "tighter"})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["notes"]["beat:S02"]["note"], "tighter")
        status, body, _ = self.call(server, "/api/select", {"target": "clip:S01", "version": 1})
        self.assertEqual(status, 400)
        self.assertIn("Takes can be switched only", json.loads(body)["error"])
        self.assertEqual(self.call(server, "/api/note", raw=b"not json")[0], 400)
        self.assertEqual(self.call(server, "/api/note", raw=b"[1, 2]")[0], 400)
        self.assertEqual(self.call(server, "/api/note", raw=b"x" * (review_page.MAX_BODY + 1))[0], 413)
        self.assertEqual(self.call(server, "/api/nothing", {})[0], 404)

    def test_serve_round_trip_ends_with_done(self):
        self.images_ready(visuals=False)
        ready, result = queue.Queue(), {}
        worker = threading.Thread(target=lambda: result.update(lines=review_page.serve(
            self.project, open_browser=False, ready=ready.put)), daemon=True)
        worker.start()
        server = ready.get(timeout=10)
        self.call(server, "/api/note", {"item": "beat:S02", "note": "mid-step"})
        self.assertEqual(self.call(server, "/api/done", {})[0], 200)
        worker.join(timeout=10)
        self.assertFalse(worker.is_alive())
        self.assertIn("NOTE  beat:S02  mid-step", result["lines"])

    def test_serve_with_nothing_to_review(self):
        self.assertEqual(review_page.serve(self.project, open_browser=False), [])


import contextlib  # noqa: E402
import io  # noqa: E402

from vglib import cli  # noqa: E402


class CliTests(Base):
    def test_review_command_with_nothing_to_review(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = cli.main(["review", "-p", str(self.project.path), "--no-open"])
        self.assertEqual(code, 0)
        self.assertIn("Nothing to review yet", out.getvalue())


class SummaryStageTests(Base):
    def test_look_notes_do_not_ask_for_an_animatic(self):
        sl = Shotlist(self.project.shotlist(), self.project)
        generate.run_images(self.project, sl.image_targets("look"))
        review_page.set_note(self.project, "look:Look_A", "jeans, not beige trousers")
        last = review_page.summary(self.project)[-1]
        self.assertTrue(last.startswith("NEXT  act on the notes"))
        self.assertNotIn("animatic", last)


class ApproveWhatWasShownTests(Base):
    """C1 (final review): an approval covers exactly what the page showed, never what changed on disk
    after it loaded."""

    def test_look_changed_after_the_page_loaded_is_refused(self):
        sl = Shotlist(self.project.shotlist(), self.project)
        generate.run_images(self.project, sl.image_targets("look"))
        shown = review_page.page_data(self.project)["seen"]
        generate.run_images(self.project, ["look:Look_A"], new_take=True)  # the agent re-rolls meanwhile
        with self.assertRaises(Refused) as ctx:
            review_page.approve(self.project, "look", shown)
        self.assertIn("changed after the review page showed it", str(ctx.exception))
        self.assertNotIn("look", self.project.read_state()["approvals"])
        review_page.approve(self.project, "look", review_page.page_data(self.project)["seen"])
        self.assertIn("look", self.project.read_state()["approvals"])

    def test_animatic_rendered_after_the_page_loaded_is_refused(self):
        self.images_ready(visuals=False)
        self.write_edit_spec()
        shown = review_page.page_data(self.project)["seen"]  # the page said "No animatic yet"
        self.show_animatic()
        with self.assertRaises(Refused):
            review_page.approve(self.project, "visuals", shown)
        self.assertNotIn("visuals", self.project.read_state()["approvals"])

    def test_gate_checks_the_expected_snapshot_itself(self):
        sl = Shotlist(self.project.shotlist(), self.project)
        generate.run_images(self.project, sl.image_targets("look"))
        with self.assertRaises(Refused):
            review.approve_look(self.project, expected="not-what-is-on-disk")
        self.assertNotIn("look", self.project.read_state()["approvals"])

    def test_approve_without_what_the_page_showed_is_an_error(self):
        sl = Shotlist(self.project.shotlist(), self.project)
        generate.run_images(self.project, sl.image_targets("look"))
        with self.assertRaises(UsageError):
            review_page.approve(self.project, "look", None)


class PageShowsWhatItApprovesTests(unittest.TestCase):
    """I1 (final review): every frame the reel approval covers is pictured on the page."""

    def test_each_frame_behind_a_beat_is_pictured(self):
        self.assertTrue('$("div", {class: "frame"}, [$("span", {class: "muted", text: f.label}), picture(f), takeButtons(f)])'
                        in review_page.PAGE_HTML, "frames behind a beat must show their picture")


class NotesAreNeverLostTests(ServerHelpers, Base):
    """I2 (final review): typed notes survive re-renders and Done saves every note it carries."""

    def test_done_saves_the_notes_it_carries(self):
        self.images_ready(visuals=False)
        server = self.start()
        status, _, _ = self.call(server, "/api/done", {"notes": {"beat:S02": "tighter", "look:Look_A": "warmer"}})
        self.assertEqual(status, 200)
        self.assertTrue(server.finished.is_set())
        lines = review_page.summary(self.project)
        self.assertIn("NOTE  beat:S02  tighter", lines)
        self.assertIn("NOTE  look:Look_A  warmer", lines)

    def test_done_with_a_bad_note_is_refused_and_keeps_the_page_open(self):
        self.images_ready(visuals=False)
        server = self.start()
        self.assertEqual(self.call(server, "/api/done", {"notes": {"beat:S99": "x"}})[0], 400)
        self.assertFalse(server.finished.is_set())

    def test_page_keeps_unsaved_text_and_sends_it_with_done(self):
        self.assertTrue("drafts[item]" in review_page.PAGE_HTML, "unsaved note text must survive a re-render")
        self.assertTrue('api("/api/done", {notes: drafts})' in review_page.PAGE_HTML, "Done must carry unsaved notes")


class NextStepTests(ActionHelpers, Base):
    """I3 (final review): NEXT always names a step that can work."""

    def last(self):
        return review_page.summary(self.project)[-1]

    def test_look_approved_in_chat_mode_continues_the_pipeline(self):
        self.look_ready()
        review_page.approve(self.project, "look", self.seen())
        self.assertTrue(self.last().startswith("NEXT  look approved: continue"), self.last())

    def test_terminal_mode_after_the_look_does_not_wait_for_an_impossible_approval(self):
        self.look_ready()
        review.approve_look(self.project)  # chat mode in the fixture
        config._env_cache["VG_APPROVAL_MODE"] = "terminal"
        self.assertTrue(self.last().startswith("NEXT  look approved: continue"), self.last())

    def test_stale_animatic_asks_for_a_render_first(self):
        self.images_ready(visuals=False)
        self.write_edit_spec()
        self.show_animatic()
        review_page.select_take(self.project, "storyboard:S02", 1)
        generate.run_images(self.project, ["storyboard:S02"], new_take=True)
        config._env_cache["VG_APPROVAL_MODE"] = "terminal"
        self.assertIn("render the animatic", self.last())

    def test_terminal_mode_with_a_current_animatic_waits_for_the_visuals_command(self):
        self.images_ready(visuals=False)
        self.write_edit_spec()
        self.show_animatic()
        config._env_cache["VG_APPROVAL_MODE"] = "terminal"
        self.assertIn("approve visuals", self.last())

    def test_look_not_approved_in_chat_mode_asks_the_human(self):
        self.look_ready()
        self.assertIn("ask the human", self.last())


class FastFilesTests(ServerHelpers, Base):
    """M4 (re-graded Important): serving a picture must not re-hash the whole reel, and pictures cache."""

    def test_file_requests_skip_the_gate_checks(self):
        self.images_ready(visuals=False)
        server = self.start()
        rel = review_page.page_data(self.project)["look"]["frames"][0]["versions"][0]["path"]
        from unittest import mock
        with mock.patch.object(review, "gate_status", side_effect=AssertionError("gate_status called")), \
                mock.patch.object(review, "visual_items", side_effect=AssertionError("visual_items called")):
            status, _, headers = self.call(server, "/file?path=%s" % urllib.parse.quote(rel))
        self.assertEqual(status, 200)
        self.assertEqual(headers["Cache-Control"], "private, max-age=86400")
        self.assertEqual(self.call(server, "/api/state")[2]["Cache-Control"], "no-store")
