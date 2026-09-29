"""The Python + Pillow overlay renderer (render/overlay.py): the same byte contract as overlay.swift,
every layer type, fonts that never stop a render, and how finish.py picks a renderer."""
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

VG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(VG))

from vglib import finish  # noqa: E402
from vglib.errors import UsageError  # noqa: E402

RENDER = VG / "render"
SCRIPT = RENDER / "overlay.py"
SWIFT_BINARY = RENDER / ".build" / "overlay"

try:
    from PIL import Image, ImageChops
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

W, H, FPS = 108, 192, 10
# one time slot per layer type, so each can be checked on its own; nothing at t=0 or after 4.8 s
SLOTS = {"caption": (0.2, 0.95), "title": (1.0, 1.5), "pin": (1.5, 2.2), "badge": (2.2, 2.6),
         "counter": (2.6, 3.0), "map": (3.0, 3.6), "callouts": (3.6, 4.0), "card_text": (4.0, 4.4),
         "endcard": (4.4, 4.8)}
DURATION = 5.05  # 50.5 frames: the count rounds up, as Swift's .rounded(.up)


def tiny_spec(**extra):
    words = [{"text": "Tebak", "t0": 0.2, "t1": 0.35}, {"text": "harga", "t0": 0.4, "t1": 0.5},
             {"text": "rumah.", "t0": 0.5, "t1": 0.6}]
    layers = [
        {"type": "title", "t0": 1.0, "t1": 1.5, "text": "PETUNJUK 1\nMALL", "size": 10, "y": 0.2},
        {"type": "pin", "t0": 1.5, "t1": 2.2, "size": 6, "drop": 20, "label": "RUMAH", "label_size": 6},
        {"type": "badge", "t0": 2.2, "t1": 2.6, "text": "FOTO", "size": 6, "top": 10},
        {"type": "counter", "t0": 2.6, "t1": 3.0, "from": 0, "to": 1000, "run": 0.2, "size": 20,
         "caption": "UNIT", "sub": "TERJUAL"},
        {"type": "map", "t0": 3.0, "t1": 3.6,
         "roads": [{"points": [[0, 0.4], [0.5, 0.45], [1, 0.4]], "width": 3, "glow": True, "at": 0.05,
                    "draw": 0.2, "label": "TOL", "label_at": [0.3, 0.35], "label_size": 6}],
         "places": [{"at_xy": [0.5, 0.45], "label": "GT", "size": 3, "label_size": 6, "at": 0.1}],
         "distance": {"points": [[0.2, 0.6], [0.5, 0.45]], "at": 0.1, "label": "2 KM",
                      "label_at": [0.5, 0.7], "size": 8}},
        {"type": "callouts", "t0": 3.6, "t1": 4.0, "size": 8, "items": [{"text": "SMART LOCK"}, {"text": "CCTV"}]},
        {"type": "card_text", "t0": 4.0, "t1": 4.4, "text": "Peta ilustrasi\ntidak berskala", "size": 6},
        {"type": "endcard", "t0": 4.4, "t1": 4.8, "brand": "RUMAH KITA", "tagline": "CLUSTER", "cta": "DM",
         "phone": "0812", "disclaimer": "*S&K", "brand_size": 12},
        {"type": "caption", "words": words, "chunk": 3, "chunks": [3], "y": 0.74, "size": 12},
    ]
    spec = {"width": W, "height": H, "fps": FPS, "duration": DURATION, "layers": layers, "fonts": {}}
    spec.update(extra)
    return spec


def render(spec, command=None, timeout=120):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "overlay.json"
        path.write_text(json.dumps(spec), encoding="utf-8")
        cmd = (command or [sys.executable, str(SCRIPT)]) + [str(path)]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    return result


def frames_of(data, w=W, h=H):
    size = w * h * 4
    return [data[i:i + size] for i in range(0, len(data), size)]


def load_overlay_module():
    spec = importlib.util.spec_from_file_location("vg_overlay_py", str(SCRIPT))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(HAVE_PIL, "Pillow is not installed")
class OverlayRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = render(tiny_spec())
        cls.frames = frames_of(cls.result.stdout)

    def frame_at(self, t):
        return self.frames[int(round(t * FPS))]

    def test_exit_code_and_exact_byte_length(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr.decode("utf-8", "replace"))
        count = int(math.ceil(DURATION * FPS))
        self.assertEqual(count, 51)
        self.assertEqual(len(self.result.stdout), count * W * H * 4)

    def test_frames_outside_every_layer_are_fully_transparent(self):
        for t in (0.0, 4.8, 4.9, 5.0):
            self.assertEqual(self.frame_at(t), bytes(W * H * 4), "frame at %.1fs is not empty" % t)

    def test_every_layer_type_draws_in_its_slot(self):
        for kind, (t0, t1) in SLOTS.items():
            mid = self.frame_at(round((t0 + t1) / 2 + 0.05, 1))
            alpha = mid[3::4]
            self.assertGreater(max(alpha), 0, "%s drew nothing" % kind)

    def test_caption_frame_has_opaque_pixels(self):
        alpha = self.frame_at(0.5)[3::4]
        self.assertEqual(max(alpha), 255)

    def test_colour_is_premultiplied(self):
        for index, frame in enumerate(self.frames):
            img = Image.frombytes("RGBA", (W, H), frame)
            r, g, b, a = img.split()
            for channel in (r, g, b):  # subtract clips at 0: any bbox means a colour byte above alpha
                self.assertIsNone(ImageChops.subtract(channel, a).getbbox(), "frame %d is not premultiplied" % index)

    def test_malformed_layers_and_missing_fonts_do_not_stop_the_render(self):
        spec = tiny_spec(fonts={"heavy": "NoSuchFont-Black", "demi": "/no/such/font.ttf"})
        spec["layers"] += [{"type": "pin", "t0": 0, "t1": 1, "x": "left"},
                           {"type": "map", "t0": 0, "t1": 1, "roads": [{"points": [[0, "a"], 3]}], "places": [7]},
                           {"type": "callouts", "t0": 0, "t1": 1, "items": "nope"},
                           {"type": "caption", "words": [{"text": 5}], "chunks": [0, 1]},
                           {"type": "sparkles", "t0": 0, "t1": 1}]
        result = render(spec)
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        self.assertEqual(len(result.stdout), 51 * W * H * 4)

    def test_a_wide_font_keeps_the_end_card_and_title_inside_the_frame(self):
        wide = next((f for f in ("/System/Library/Fonts/Supplemental/Arial Black.ttf", r"C:\Windows\Fonts\ariblk.ttf",
                                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf") if os.path.isfile(f)), None)
        if not wide:
            self.skipTest("no wide bold font on this computer")
        w, h = 1080, 1920
        spec = {"width": w, "height": h, "fps": 2, "duration": 2, "fonts": {"heavy": wide, "demi": wide},
                "layers": [{"type": "endcard", "t0": 0, "t1": 2, "brand": "RUMAH KITA REALTY",
                            "cta": "DM UNTUK PROMO TERBARU SEKARANG JUGA", "phone": "0812-0000-0000-0000-0000",
                            "brand_size": 110, "bg_alpha": 0},
                           {"type": "title", "t0": 0, "t1": 2, "size": 80, "y": 0.12,
                            "text": "PETUNJUK 1\nSEBERANG MALL BESAR SEKALI DI KOTA"}]}
        result = render(spec)
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        last = frames_of(result.stdout, w, h)[-1]
        edge = 8  # no pixel of the button, the phone line or the title box in the outer columns
        for y in range(h):
            row = last[y * w * 4:(y + 1) * w * 4]
            for x in list(range(edge)) + list(range(w - edge, w)):
                self.assertEqual(row[x * 4 + 3], 0, "something touches the frame edge at x=%d y=%d" % (x, y))

    def test_a_closed_pipe_ends_quietly(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "overlay.json"
            path.write_text(json.dumps(tiny_spec(duration=600, width=320, height=320)), encoding="utf-8")
            proc = subprocess.Popen([sys.executable, str(SCRIPT), str(path)], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            proc.stdout.read(320 * 320 * 4)  # one frame, then the reader goes away (ffmpeg -t does this)
            proc.stdout.close()
            err = proc.stderr.read().decode("utf-8", "replace")
            proc.wait(timeout=60)
            proc.stderr.close()
        self.assertEqual(proc.returncode, 0, err)
        self.assertNotIn("Traceback", err)

    def test_bad_spec_is_a_usage_error(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "/no/such/spec.json"], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=60)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")


@unittest.skipUnless(HAVE_PIL and sys.platform == "darwin" and SWIFT_BINARY.exists()
                     and SWIFT_BINARY.stat().st_mtime >= (RENDER / "overlay.swift").stat().st_mtime,
                     "needs the built Swift renderer (macOS) to compare with")
class SameContractAsSwiftTests(unittest.TestCase):
    def test_same_length_and_same_empty_frames(self):
        swift = render(tiny_spec(), [str(SWIFT_BINARY)])
        python = render(tiny_spec())
        self.assertEqual(len(python.stdout), len(swift.stdout))
        blank = bytes(W * H * 4)
        empty = [[i for i, f in enumerate(frames_of(r.stdout)) if f == blank] for r in (swift, python)]
        self.assertEqual(empty[1], empty[0])


@unittest.skipUnless(HAVE_PIL, "Pillow is not installed")
class FontTests(unittest.TestCase):
    def setUp(self):
        self.ov = load_overlay_module()

    def resolve_on(self, platform, files, name, key):
        self.ov.PLATFORM = platform
        self.ov._FILES = dict(files)
        self.ov._RESOLVED.clear()
        return self.ov.resolve_font(name, key)

    def test_windows_maps_the_mac_defaults_to_segoe_by_weight(self):
        files = {"seguibl.ttf": r"C:\Windows\Fonts\seguibl.ttf", "segoeuib.ttf": r"C:\Windows\Fonts\segoeuib.ttf",
                 "seguisb.ttf": r"C:\Windows\Fonts\seguisb.ttf", "arialbd.ttf": r"C:\Windows\Fonts\arialbd.ttf"}
        self.assertEqual(self.resolve_on("win32", files, "AvenirNext-Heavy", "heavy"), (files["seguibl.ttf"], 0))
        self.assertEqual(self.resolve_on("win32", files, "AvenirNext-Bold", "bold"), (files["segoeuib.ttf"], 0))
        self.assertEqual(self.resolve_on("win32", files, "AvenirNext-DemiBold", "demi"), (files["seguisb.ttf"], 0))
        self.assertEqual(self.resolve_on("win32", files, "Segoe UI Black", "heavy"), (files["seguibl.ttf"], 0))

    def test_windows_without_segoe_falls_back_to_arial(self):
        files = {"ariblk.ttf": "C:/F/ariblk.ttf", "arialbd.ttf": "C:/F/arialbd.ttf", "arial.ttf": "C:/F/arial.ttf"}
        self.assertEqual(self.resolve_on("win32", files, "AvenirNext-Heavy", "heavy"), (files["ariblk.ttf"], 0))
        self.assertEqual(self.resolve_on("win32", files, "AvenirNext-DemiBold", "demi"), (files["arialbd.ttf"], 0))

    def test_linux_uses_dejavu(self):
        files = {"dejavusans-bold.ttf": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"}
        self.assertEqual(self.resolve_on("linux", files, "AvenirNext-Heavy", "heavy")[0],
                         files["dejavusans-bold.ttf"])

    def test_no_font_files_at_all_still_gives_a_font(self):
        self.assertIsNone(self.resolve_on("win32", {}, "AvenirNext-Heavy", "heavy"))
        with mock.patch.object(self.ov, "warn"):
            f = self.ov.Font("AvenirNext-Heavy", "heavy", 40)
        self.assertGreater(f.advance("HELLO"), 0)

    def test_a_font_file_path_in_the_spec_is_used(self):
        real = next((p for p in load_overlay_module().font_files().values() if p.lower().endswith(".ttf")), None)
        if not real:
            self.skipTest("no .ttf font installed")
        self.assertEqual(self.resolve_on(self.ov.PLATFORM, {}, real, "heavy"), (real, 0))

    def test_weight_roles(self):
        role = self.ov.weight_role
        self.assertEqual(role("AvenirNext-Heavy", "heavy"), "heavy")
        self.assertEqual(role("AvenirNext-DemiBold", "demi"), "demi")
        self.assertEqual(role("DINCondensed-Bold", "cond"), "cond")
        self.assertEqual(role("Futura-Bold", "Futura-Bold"), "bold")
        self.assertEqual(role("Something", "heavy"), "heavy")


class RendererChoiceTests(unittest.TestCase):
    def choose(self, platform, swiftc, pillow, env=None, built=False):
        which = (lambda tool: "/usr/bin/swiftc" if tool == "swiftc" and swiftc else None)
        with mock.patch.object(finish.sys, "platform", platform), \
                mock.patch.object(finish.shutil, "which", side_effect=which), \
                mock.patch.object(finish, "pillow_version", return_value="11.3.0" if pillow else None), \
                mock.patch.object(finish, "renderer_binary", return_value=Path("/vg/render/.build/overlay")), \
                mock.patch.dict(os.environ, env or {}, clear=False):
            if not env:
                os.environ.pop("VG_OVERLAY", None)
            if not swiftc:
                with mock.patch.object(finish, "_swift_ready", return_value=built):
                    return finish.renderer_command()
            return finish.renderer_command()

    def python_command(self):
        return [sys.executable, str(finish.RENDER_DIR / "overlay.py")]

    def test_mac_with_swiftc_keeps_the_swift_binary(self):
        self.assertEqual(self.choose("darwin", True, True), ["/vg/render/.build/overlay"])
        self.assertEqual(self.choose("darwin", True, False), ["/vg/render/.build/overlay"])

    def test_mac_with_a_built_binary_and_no_swiftc_keeps_it(self):
        self.assertEqual(self.choose("darwin", False, True, built=True), ["/vg/render/.build/overlay"])

    def test_vg_overlay_python_forces_the_port_on_a_mac(self):
        self.assertEqual(self.choose("darwin", True, True, env={"VG_OVERLAY": "python"}), self.python_command())

    def test_mac_without_swiftc_uses_pillow(self):
        self.assertEqual(self.choose("darwin", False, True), self.python_command())

    def test_windows_and_linux_use_pillow(self):
        self.assertEqual(self.choose("win32", False, True), self.python_command())
        self.assertEqual(self.choose("win32", True, True), self.python_command())  # swiftc means nothing there
        self.assertEqual(self.choose("linux", False, True), self.python_command())

    def test_windows_without_pillow_says_how_to_install_it(self):
        with self.assertRaises(UsageError) as caught:
            self.choose("win32", False, False)
        message = str(caught.exception)
        self.assertIn("Pillow is needed to draw captions and graphics on this computer", message)
        self.assertIn("python -m pip install pillow", message)
        self.assertNotIn("swiftc", message)
        self.assertNotIn("xcode", message)

    def test_mac_without_either_mentions_both(self):
        with self.assertRaises(UsageError) as caught:
            self.choose("darwin", False, False)
        self.assertIn("pip install pillow", str(caught.exception))
        self.assertIn("xcode-select --install", str(caught.exception))

    def test_pillow_version_reports_the_installed_pillow(self):
        version = finish.pillow_version()
        self.assertEqual(version is not None, HAVE_PIL)


class FfmpegPathTests(unittest.TestCase):
    def test_windows_drive_colon_is_escaped_in_filters(self):
        self.assertEqual(finish.filter_path(r"C:\Users\Rani\Look.cube"), "C\\:/Users/Rani/Look.cube")
        self.assertEqual(finish.filter_path("D:/x/y.cube"), "D\\:/x/y.cube")

    def test_posix_paths_are_unchanged(self):
        path = "/Users/manse/5_Projects/P/0_Source/Look.cube"
        self.assertEqual(finish.filter_path(path), path)
        self.assertEqual(finish.filter_path("/a/it's.cube"), "/a/it\\'s.cube")  # as before

    def test_concat_lines(self):
        self.assertEqual(finish.concat_line("/tmp/x/000.mp4"), "file '/tmp/x/000.mp4'\n")
        self.assertEqual(finish.concat_line(r"C:\Temp\tmp1\000.mp4"), "file 'C:/Temp/tmp1/000.mp4'\n")
        self.assertEqual(finish.concat_line("/tmp/O'Brien/000.mp4"), "file '/tmp/O'\\''Brien/000.mp4'\n")

    @unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg is not installed")
    def test_ffmpeg_reads_a_quoted_concat_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "it's here"
            folder.mkdir()
            clip = folder / "000.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=16x16:d=0.2",
                            "-c:v", "libx264", str(clip)], check=True, timeout=60)
            listing = Path(tmp) / "list.txt"
            listing.write_text(finish.concat_line(clip) * 2, encoding="utf-8")
            result = subprocess.run(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                                     "-f", "null", "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))


if __name__ == "__main__":
    unittest.main()
