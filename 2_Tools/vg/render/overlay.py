"""overlay.py: the Python + Pillow port of overlay.swift, for computers without the Swift renderer
(Windows, Linux, or a Mac without the Xcode command line tools).

Usage: python overlay.py <spec.json>
stdout: width*height*4 bytes per frame, premultiplied RGBA, top row first, ceil(duration * fps)
frames: the same frames as the Swift binary. Driven by `vg edit final` / `vg edit animatic`
(vglib/finish.py, renderer_command()). Needs Pillow; nothing else outside the standard library.

The spec, the nine layer types (caption, title, pin, badge, counter, map, callouts, card_text,
endcard), their positions, sizes, colours, shadows and animation curves follow overlay.swift line for
line; each draw_* function names the Swift function it ports. Where CoreGraphics/CoreText have no
Pillow equivalent it is approximated:
  - fonts: the Swift names (AvenirNext-Heavy, ...) resolve to font files per platform (Avenir Next on
    a Mac, Segoe UI Black/Bold/Semibold on Windows, DejaVu Sans Bold on Linux); a spec may name a
    font file directly. A missing font falls back by weight and never stops the render.
  - text: Pillow's basic layout (no GPOS pair kerning); tracking (kCTKern) is placed glyph by glyph;
    CoreText's centred text stroke is a Pillow outline plus a slightly eroded fill.
  - shapes are drawn 4x and averaged down for anti-aliasing; shadows are a Gaussian blur (sigma =
    0.45 x the CG blur, matched to Swift's output). CG shadows each drawing call: a caption's stroke
    shadow shades its fill, kept here; a title's box and text fade as one piece here, where CG fades
    each call on its own (visible only during the 0.2-0.35 s fades).
  - colours are the exact hex values; Swift's CGColor is Generic RGB, converted to the Mac's display
    profile (on the reference Mac #FF5A1F came out as #FF7127), so Swift output is a little lighter.
  - CG's setAlpha replaces the alpha instead of multiplying it, so a nested withTransform draws at
    its own alpha: caption words are always opaque, and map labels, places and the distance tag do
    not fade out with the map. Kept as in Swift, so both renderers give the same reel.
"""
import errno
import json
import math
import os
import re
import sys

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
except ImportError:  # finish.py checks first; this is for a direct run
    sys.stderr.write("overlay.py needs Pillow: python -m pip install pillow\n")
    sys.exit(3)

W, H, FPS, DURATION = 1080, 1920, 30.0, 1.0
FONT_NAMES = {"heavy": "AvenirNext-Heavy", "bold": "AvenirNext-Bold", "demi": "AvenirNext-DemiBold",
              "cond": "DINCondensed-Bold"}
SS = 4  # supersampling for anti-aliased shapes
BILINEAR = getattr(Image, "Resampling", Image).BILINEAR
AFFINE = getattr(Image, "Transform", Image).AFFINE


# ---------------------------------------------------------------- spec helpers

def num(j, k, d):
    v = j.get(k) if isinstance(j, dict) else None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    return d


def text_of(j, k, d):
    v = j.get(k) if isinstance(j, dict) else None
    return v if isinstance(v, str) else d


def dict_list(v):
    return [x for x in v if isinstance(x, dict)] if isinstance(v, list) else []


def point(v):
    """[x, y] as floats, or None (Swift: `as? [Double]`)."""
    if isinstance(v, list) and len(v) >= 2 and all(isinstance(x, (int, float)) for x in v):
        return [float(x) for x in v]
    return None


def color(hexs, alpha=1.0):
    """(r, g, b, a) in 0..1 from #RRGGBB or #RRGGBBAA, as Swift's color()."""
    s = (hexs if isinstance(hexs, str) else "").strip(" \t")
    if s.startswith("#"):
        s = s[1:]
    m = re.match(r"(?:0[xX])?([0-9a-fA-F]+)", s)
    v = int(m.group(1), 16) & 0xFFFFFFFFFFFFFFFF if m else 0
    if len(s) == 8:
        r, g, b, a = (v >> 24) & 255, (v >> 16) & 255, (v >> 8) & 255, (v & 255) / 255.0
    else:
        r, g, b, a = (v >> 16) & 255, (v >> 8) & 255, v & 255, 1.0
    return (r / 255.0, g / 255.0, b / 255.0, a * alpha)


# ---------------------------------------------------------------- easing

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def ease_out_cubic(t):
    return 1 - (1 - clamp(t)) ** 3


def ease_in_out(t):
    x = clamp(t)
    return 4 * x * x * x if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    x = clamp(t)
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def bounce(t):
    x = clamp(t)
    n1, d1 = 7.5625, 2.75
    if x < 1 / d1:
        return n1 * x * x
    if x < 2 / d1:
        x -= 1.5 / d1
        return n1 * x * x + 0.75
    if x < 2.5 / d1:
        x -= 2.25 / d1
        return n1 * x * x + 0.9375
    x -= 2.625 / d1
    return n1 * x * x + 0.984375


def envelope(t, t0, t1, in_dur=0.25, out_dur=0.2):
    """0..1 in over `in_dur` after t0, out over `out_dur` before t1."""
    return clamp((t - t0) / in_dur), clamp((t1 - t) / out_dur)


def swift_round(x):
    """Swift's .rounded(): halves away from zero (Python's round() goes to even)."""
    return int(math.floor(x + 0.5)) if x >= 0 else -int(math.floor(-x + 0.5))


# ---------------------------------------------------------------- fonts

FONT_EXT = (".ttf", ".otf", ".ttc", ".otc")
PLATFORM = "win32" if sys.platform.startswith("win") else ("darwin" if sys.platform == "darwin" else "linux")
# by weight, per platform: (lower-case file name, face style inside a collection or None)
ROLE_FILES = {
    "win32": {
        "heavy": [("seguibl.ttf", None), ("ariblk.ttf", None), ("arialbd.ttf", None), ("arial.ttf", None)],
        "bold": [("segoeuib.ttf", None), ("arialbd.ttf", None), ("arial.ttf", None)],
        "demi": [("seguisb.ttf", None), ("segoeuib.ttf", None), ("arialbd.ttf", None), ("arial.ttf", None)],
        "cond": [("arialnb.ttf", None), ("bahnschrift.ttf", None), ("arialbd.ttf", None), ("arial.ttf", None)],
        "regular": [("segoeui.ttf", None), ("arial.ttf", None)],
    },
    "darwin": {
        "heavy": [("avenir next.ttc", "Heavy"), ("arial black.ttf", None), ("arial bold.ttf", None)],
        "bold": [("avenir next.ttc", "Bold"), ("arial bold.ttf", None)],
        "demi": [("avenir next.ttc", "Demi Bold"), ("arial bold.ttf", None)],
        "cond": [("din condensed bold.ttf", None), ("arial narrow bold.ttf", None), ("arial bold.ttf", None)],
        "regular": [("avenir next.ttc", "Regular"), ("arial.ttf", None), ("helvetica.ttc", None)],
    },
    "linux": {
        "heavy": [("dejavusans-bold.ttf", None), ("liberationsans-bold.ttf", None), ("freesansbold.ttf", None)],
        "bold": [("dejavusans-bold.ttf", None), ("liberationsans-bold.ttf", None), ("freesansbold.ttf", None)],
        "demi": [("dejavusans-bold.ttf", None), ("liberationsans-bold.ttf", None), ("freesansbold.ttf", None)],
        "cond": [("dejavusanscondensed-bold.ttf", None), ("liberationsansnarrow-bold.ttf", None),
                 ("dejavusans-bold.ttf", None)],
        "regular": [("dejavusans.ttf", None), ("liberationsans-regular.ttf", None), ("freesans.ttf", None)],
    },
}
ANY_FILES = ["arialbd.ttf", "arial bold.ttf", "dejavusans-bold.ttf", "liberationsans-bold.ttf", "arial.ttf",
             "dejavusans.ttf", "helvetica.ttc"]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def font_dirs():
    if PLATFORM == "win32":
        windir = os.environ.get("WINDIR") or os.environ.get("SystemRoot") or r"C:\Windows"
        dirs = [os.path.join(windir, "Fonts")]
        if os.environ.get("LOCALAPPDATA"):
            dirs.append(os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Windows", "Fonts"))
    elif PLATFORM == "darwin":
        dirs = ["/System/Library/Fonts", "/Library/Fonts", os.path.expanduser("~/Library/Fonts")]
    else:
        dirs = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.local/share/fonts"),
                os.path.expanduser("~/.fonts")]
    return [d for d in dirs if os.path.isdir(d)]


_FILES = None


def font_files():
    """Every font file in the system font folders, by lower-case file name (first found wins)."""
    global _FILES
    if _FILES is None:
        _FILES = {}
        for d in font_dirs():
            for root, _, names in os.walk(d):
                for n in sorted(names):
                    if n.lower().endswith(FONT_EXT):
                        _FILES.setdefault(n.lower(), os.path.join(root, n))
    return _FILES


def faces(path):
    """(index, family, style) of each face in a font file."""
    out = []
    for i in range(64):
        try:
            family, style = ImageFont.truetype(path, 12, index=i).getname()
        except Exception:
            break
        out.append((i, family or "", style or ""))
        if not path.lower().endswith((".ttc", ".otc")):
            break
    return out


def face_index(path, wanted):
    """Index of the face whose family + style (normalised) is `wanted`, else None."""
    for i, family, style in faces(path):
        if norm(family + style) == wanted or (norm(family) == wanted and norm(style) in ("", "regular")):
            return i
    return None


_NAME_INDEX = None


def name_index():
    """normalised 'family style' -> (path, index) over every installed font: slow, built once and only
    for a font name that no file name matches (e.g. "Segoe UI Black" on Windows)."""
    global _NAME_INDEX
    if _NAME_INDEX is None:
        _NAME_INDEX = {}
        for path in list(font_files().values())[:4000]:
            for i, family, style in faces(path):
                _NAME_INDEX.setdefault(norm(family + style), (path, i))
                if norm(style) in ("", "regular"):
                    _NAME_INDEX.setdefault(norm(family), (path, i))
    return _NAME_INDEX


def weight_role(name, key):
    n = name.lower()
    if "cond" in n or "narrow" in n:
        return "cond"
    if "heavy" in n or "black" in n or "extrabold" in n or "ultrabold" in n:
        return "heavy"
    if "demi" in n or "semi" in n or "medium" in n:
        return "demi"
    if "bold" in n:
        return "bold"
    return key if key in ("heavy", "bold", "demi", "cond") else "bold"


def by_role(role):
    files = font_files()
    for fname, style in ROLE_FILES[PLATFORM].get(role, []) + [(f, None) for f in ANY_FILES]:
        path = files.get(fname)
        if path:
            index = face_index(path, norm(style)) if style else 0
            return path, index or 0
    return None


_RESOLVED = {}


def resolve_font(name, key):
    """A font name or file -> (file path, face index), or None for Pillow's own font."""
    if (name, key) in _RESOLVED:
        return _RESOLVED[(name, key)]
    found = None
    if name.lower().endswith(FONT_EXT) and os.path.isfile(name):  # a font file named in the spec
        found = (name, 0)
    if not found:
        wanted = norm(name)
        files = font_files()
        stems = [(norm(os.path.splitext(f)[0]), path) for f, path in files.items()]
        for stem, path in stems:  # a file named like the font: seguibl.ttf, "DIN Condensed Bold.ttf"
            if stem == wanted:
                found = (path, 0)
                break
        # the Mac defaults exist only on a Mac: elsewhere go straight to the same weight
        mac_default = name in FONT_NAMES.values() and PLATFORM != "darwin"
        if not found and not mac_default and wanted:
            # a face in a collection whose file name starts the font's name: AvenirNext-Heavy -> "Avenir Next.ttc"
            for stem, path in sorted(stems, key=lambda s: -len(s[0])):
                if len(stem) >= 4 and wanted.startswith(stem):
                    index = face_index(path, wanted)
                    if index is not None:
                        found = (path, index)
                        break
            if not found:
                found = name_index().get(wanted)
        if not found:
            found = by_role(weight_role(name, key))
    _RESOLVED[(name, key)] = found
    return found


class Font:
    """A Pillow font at one size, with CoreText-style ascent/descent."""

    def __init__(self, name, key, size):
        self.size = max(1.0, float(size))
        loc = resolve_font(name, key)
        self.pil = None
        if loc:
            try:
                self.pil = ImageFont.truetype(loc[0], self.size, index=loc[1])
            except Exception:
                self.pil = None
        if self.pil is None:
            warn("font %s: no font file found, using Pillow's default font" % name)
            try:
                self.pil = ImageFont.load_default(self.size)
            except Exception:
                self.pil = ImageFont.load_default()
        try:
            self.asc, self.desc = self.pil.getmetrics()
        except Exception:
            self.asc, self.desc = self.size * 0.8, self.size * 0.2
        self.key = (loc, self.size)

    def advance(self, s, kern=0.0):
        """CTLineGetTypographicBounds width: advances plus `kern` after every character."""
        return (self.pil.getlength(s) + kern * len(s)) if s else 0.0

    def runs(self, s, kern):
        """(x, text) pieces to draw: the whole string, or glyph by glyph when tracked."""
        if not kern:
            return [(0.0, s)]
        return [(self.pil.getlength(s[:i + 1]) - self.pil.getlength(ch) + kern * i, ch) for i, ch in enumerate(s)]


_FONTS = {}


def font(key, size):
    name = FONT_NAMES.get(key, key)
    ck = (name, key, round(float(size), 3))
    if ck not in _FONTS:
        _FONTS[ck] = Font(name, key, size)
    return _FONTS[ck]


_WARNED = set()


def warn(message):
    if message not in _WARNED:
        _WARNED.add(message)
        sys.stderr.write("overlay.py: %s\n" % message)


# ---------------------------------------------------------------- raster helpers

_LUTS = {}


def alpha_lut(a):
    a = clamp(a)
    k = round(a, 4)
    if k not in _LUTS:
        _LUTS[k] = [int(v * a + 0.5) for v in range(256)]
    return _LUTS[k]


def to8(c):
    return int(round(clamp(c) * 255))


def colored(mask, rgba):
    """A solid colour with `mask` (L) times the colour's alpha as its alpha."""
    layer = Image.new("RGBA", mask.size, (to8(rgba[0]), to8(rgba[1]), to8(rgba[2]), 255))
    layer.putalpha(mask if rgba[3] >= 0.9995 else mask.point(alpha_lut(rgba[3])))
    return layer


def fade(img, alpha):
    out = img.copy()
    out.putalpha(img.getchannel("A").point(alpha_lut(alpha)))
    return out


def composite(dst, src, x, y):
    """src over dst with src's top-left at (x, y), clipped to dst."""
    dw, dh = dst.size
    sw, sh = src.size
    x0, y0 = max(0, -x), max(0, -y)
    x1, y1 = min(sw, dw - x), min(sh, dh - y)
    if x1 <= x0 or y1 <= y0:
        return
    if (x0, y0, x1, y1) != (0, 0, sw, sh):
        src = src.crop((x0, y0, x1, y1))
    dst.alpha_composite(src, (x + x0, y + y0))


def shape_mask(x0, y0, x1, y1, draw):
    """Anti-aliased coverage (L image, left, top) of a shape inside the frame box (x0, y0)-(x1, y1).
    draw(d, T, s): d draws at SS x, T maps frame coordinates to it, s scales lengths."""
    X, Y = int(math.floor(x0)) - 1, int(math.floor(y0)) - 1
    w, h = int(math.ceil(x1)) + 1 - X, int(math.ceil(y1)) + 1 - Y
    if w <= 0 or h <= 0:
        return None
    ss = SS if w * h < 1500000 else 2
    big = Image.new("L", (w * ss, h * ss), 0)
    draw(ImageDraw.Draw(big), lambda x, y: ((x - X) * ss, (y - Y) * ss), ss)
    return big.reduce(ss), X, Y


def rrect_on(d, T, s, cx, cy, w, h, r, fill):
    r = max(0.0, min(r, w / 2, h / 2))
    if w <= 0 or h <= 0:
        return
    x0, y0 = T(cx - w / 2, cy - h / 2)
    x1, y1 = T(cx + w / 2, cy + h / 2)
    d.rounded_rectangle([int(round(x0)), int(round(y0)), int(round(x1)) - 1, int(round(y1)) - 1],
                        radius=int(round(r * s)), fill=fill)


def ellipse_on(d, T, cx, cy, rx, ry, fill):
    if rx <= 0 or ry <= 0:
        return
    x0, y0 = T(cx - rx, cy - ry)
    x1, y1 = T(cx + rx, cy + ry)
    d.ellipse([int(round(x0)), int(round(y0)), int(round(x1)) - 1, int(round(y1)) - 1], fill=fill)


def polyline_on(d, T, s, pts, width, round_caps=True):
    """A stroked polyline with round joins (and round caps), as CG with .round cap and join."""
    px = [T(x, y) for x, y in pts]
    wd = max(1, int(round(width * s)))
    d.line(px, fill=255, width=wd, joint="curve")
    if round_caps:
        r = width * s / 2
        for x, y in (px[0], px[-1]):
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)


_TEXT = {}


def text_layers(s, f, kern, rgba, stroke_rgba=None, stroke_pct=0.0):
    """(fill image, stroke image or None, left-edge x, baseline y, advance) of a CTLine: `s` in font
    `f` and colour `rgba`, tracked by `kern`, with an optional CoreText stroke of `stroke_pct` percent
    of the font size (centred on the outline: half outside, half over the fill)."""
    key = (s, f.key, kern, rgba, stroke_rgba, stroke_pct)
    hit = _TEXT.get(key)
    if hit:
        return hit
    half = f.size * stroke_pct / 200.0 if stroke_rgba and stroke_pct > 0 else 0.0
    adv = f.advance(s, kern)
    pad = int(math.ceil(f.size * 0.3 + half)) + 2
    w, h = int(math.ceil(adv)) + 2 * pad, int(math.ceil(f.asc + f.desc)) + 2 * pad
    bx, by = pad, pad + f.asc
    runs = f.runs(s, kern)
    fill = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(fill)
    for x, piece in runs:
        d.text((bx + x, by), piece, font=f.pil, fill=255, anchor="ls")
    band = None
    if half > 0:
        outer = Image.new("L", (w, h), 0)
        do = ImageDraw.Draw(outer)
        for x, piece in runs:
            do.text((bx + x, by), piece, font=f.pil, fill=255, anchor="ls", stroke_width=half, stroke_fill=255)
        k = int(round(half))
        if k >= 1:
            fill = fill.filter(ImageFilter.MinFilter(2 * k + 1))
        band = colored(ImageChops.subtract(outer, fill), stroke_rgba)
    if len(_TEXT) > 4000:
        _TEXT.clear()
    _TEXT[key] = (colored(fill, rgba), band, bx, by, adv)
    return _TEXT[key]


class Canvas:
    """A transparent RGBA image over a box of the frame; drawing takes frame (top-left) coordinates."""

    def __init__(self, x0, y0, x1, y1):
        self.x, self.y = int(math.floor(x0)), int(math.floor(y0))
        self.img = Image.new("RGBA", (max(1, int(math.ceil(x1)) - self.x), max(1, int(math.ceil(y1)) - self.y)),
                             (0, 0, 0, 0))

    @classmethod
    def wrap(cls, placed):
        img, x, y = placed
        c = cls.__new__(cls)
        c.img, c.x, c.y = img, x, y
        return c

    def element(self):
        return self.img, self.x, self.y

    def put(self, placed):
        if placed:
            img, x, y = placed
            composite(self.img, img, x - self.x, y - self.y)

    def paint(self, shape, rgba):
        if shape and rgba[3] > 0:
            mask, x, y = shape
            self.put((colored(mask, rgba), x, y))

    def text(self, s, f, cx, cy, rgba, kern=0.0, stroke_rgba=None, stroke_pct=0.0):
        """drawCentered: `s` centred on (cx, cy) the CoreText way (baseline at cy + (ascent-descent)/2)."""
        if not s:
            return
        fill, band, bx, by, adv = text_layers(s, f, kern, rgba, stroke_rgba, stroke_pct)
        x, y = int(round(cx - adv / 2 - bx)), int(round(cy + (f.asc - f.desc) / 2 - by))
        self.put((fill, x, y))
        if band:
            self.put((band, x, y))

    def rrect(self, cx, cy, w, h, r, rgba):
        self.paint(shape_mask(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2,
                              lambda d, T, s: rrect_on(d, T, s, cx, cy, w, h, r, 255)), rgba)

    def rrect_stroke(self, cx, cy, w, h, r, width, rgba):
        """A stroke centred on the rounded rectangle's edge, as CG strokePath."""
        hw = width / 2

        def draw(d, T, s):
            rrect_on(d, T, s, cx, cy, w + width, h + width, r + hw, 255)
            rrect_on(d, T, s, cx, cy, w - width, h - width, max(0.0, r - hw), 0)
        self.paint(shape_mask(cx - w / 2 - hw, cy - h / 2 - hw, cx + w / 2 + hw, cy + h / 2 + hw, draw), rgba)

    def ellipse(self, cx, cy, rx, ry, rgba):
        self.paint(shape_mask(cx - rx, cy - ry, cx + rx, cy + ry,
                              lambda d, T, s: ellipse_on(d, T, cx, cy, rx, ry, 255)), rgba)

    def polygon(self, pts, rgba):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        self.paint(shape_mask(min(xs), min(ys), max(xs), max(ys),
                              lambda d, T, s: d.polygon([T(x, y) for x, y in pts], fill=255)), rgba)

    def shadow(self, dy, blur, alpha):
        """CG setShadow for what is drawn so far: black at `alpha`, `dy` px down, blurred under it."""
        m = int(math.ceil(blur * 1.5 + abs(dy))) + 2
        grown = Image.new("RGBA", (self.img.width + 2 * m, self.img.height + 2 * m), (0, 0, 0, 0))
        grown.paste(self.img, (m, m))
        a = grown.getchannel("A")
        if alpha < 1:
            a = a.point(alpha_lut(alpha))
        sh = Image.new("L", grown.size, 0)
        sh.paste(a, (0, int(round(dy))))
        if blur > 0:
            sh = sh.filter(ImageFilter.GaussianBlur(blur * 0.45))
        out = Image.new("RGBA", grown.size, (0, 0, 0, 0))
        out.putalpha(sh)
        out.alpha_composite(grown)
        self.img, self.x, self.y = out, self.x - m, self.y - m


def place(el, alpha=1.0, scale=1.0, cx=0.0, cy=0.0, dx=0.0, dy=0.0):
    """Swift's withTransform for a drawn element (image, x, y): scale around (cx, cy), shift by
    (dx, dy), fade to `alpha`. None when invisible (the Swift guard alpha > 0.001)."""
    if el is None or alpha <= 0.001:
        return None
    img, x, y = el
    if abs(scale - 1.0) > 1e-6:
        if scale <= 0:
            return None
        w, h = img.size
        fx0, fy0 = cx + (x - cx) * scale + dx, cy + (y - cy) * scale + dy
        X0, Y0 = max(int(math.floor(fx0)), -2), max(int(math.floor(fy0)), -2)
        X1, Y1 = min(int(math.ceil(fx0 + w * scale)), W + 2), min(int(math.ceil(fy0 + h * scale)), H + 2)
        if X1 <= X0 or Y1 <= Y0:
            return None
        inv = 1.0 / scale
        img = img.transform((X1 - X0, Y1 - Y0), AFFINE, (inv, 0, (X0 - fx0) * inv, 0, inv, (Y0 - fy0) * inv),
                            resample=BILINEAR)
        x, y = X0, Y0
    else:
        x, y = x + int(round(dx)), y + int(round(dy))
    if alpha < 0.999:
        img = fade(img, alpha)
    return img, x, y


class Frame:
    """The frame being drawn; its image exists only once something is drawn."""

    def __init__(self):
        self.img = None

    def put(self, placed):
        if placed:
            if self.img is None:
                self.img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            img, x, y = placed
            composite(self.img, img, x, y)

    def paint(self, shape, rgba):
        if shape and rgba[3] > 0:
            mask, x, y = shape
            self.put((colored(mask, rgba), x, y))


_CACHE = {}


def cached(key, build, keep=0):
    """An element built once. keep > 0: a small cache of the latest `keep` keys of this kind."""
    if key in _CACHE:
        return _CACHE[key]
    value = build()
    _CACHE[key] = value
    if keep:
        kind = key[:2]
        same = [k for k in _CACHE if k[:2] == kind]
        for k in same[:-keep]:
            del _CACHE[k]
    return value


# ---------------------------------------------------------------- layers

_CHUNKS = {}


def caption_groups(j, li):
    """Words grouped into chunks: the spec's "chunks" sizes, else the fallback loop (as Swift)."""
    if li in _CHUNKS:
        return _CHUNKS[li]
    words = dict_list(j.get("words"))
    sizes = j.get("chunks")
    chunks = []
    if (isinstance(sizes, list) and sizes and all(isinstance(n, int) and not isinstance(n, bool) for n in sizes)
            and sum(sizes) == len(words)):
        start = 0
        for n in sizes:
            if n > 0:
                chunks.append(words[start:start + n])
            start += n
    else:
        size = int(num(j, "chunk", 3))
        cur = []
        for w in words:
            cur.append(w)
            if len(cur) >= size or text_of(w, "text", "").endswith((".", "?", ",", "!", ":", "\u2026")):
                chunks.append(cur)
                cur = []
        if cur:
            chunks.append(cur)
    _CHUNKS[li] = chunks
    return chunks


def draw_caption(fr, j, t, li):  # drawCaption
    chunks = caption_groups(j, li)
    if not chunks:
        return
    size = num(j, "size", 76)
    y = num(j, "y", 0.72) * H
    f = font(text_of(j, "font", "heavy"), size)
    fill = color(text_of(j, "color", "#FFFFFF"))
    hi = color(text_of(j, "highlight", "#FFD23F"))
    stroke = color(text_of(j, "stroke", "#000000"))
    dim = color(text_of(j, "color", "#FFFFFF"), 0.85)
    for i, chunk in enumerate(chunks):
        c0 = num(chunk[0], "t0", 0)
        last_end = num(chunk[-1], "t1", 0) + 0.35
        c_end = min(num(chunks[i + 1][0], "t0", 0), last_end) if i + 1 < len(chunks) else last_end
        if not (c0 <= t < c_end):
            continue
        appear = ease_out_back((t - c0) / 0.18)
        if clamp(appear * 1.4) <= 0.001:  # the outer withTransform's guard; the words set alpha 1 themselves
            continue
        texts = [text_of(w, "text", "").upper() for w in chunk]
        space = f.advance(" ") + size * 0.14  # the outline eats half of a plain space
        widths = [f.advance(s) for s in texts]
        total = sum(widths) + space * max(0, len(texts) - 1)
        fit = min(1.0, W * 0.9 / max(1.0, total))  # a long chunk shrinks instead of leaving the frame
        scale = (0.85 + 0.15 * appear) * fit
        looks, pops = [], []
        for w in chunk:
            w0, w1 = num(w, "t0", 0), num(w, "t1", 0)
            active = w0 <= t < w1 + 0.05
            looks.append(0 if active else (1 if t >= w0 else 2))
            pops.append(1 + 0.08 * (1 - clamp((t - w0) / 0.15)) if active else 1.0)
        settled = all(p == 1.0 for p in pops) and abs(scale - fit) < 1e-9

        def build():
            m = size * 0.6 + 8
            x = W / 2 - total / 2
            box = (x - m, y - size - m, x + total + m, y + size + m)
            fills, strokes = Canvas(*box), Canvas(*box)
            for k, s in enumerate(texts):
                cx = x + widths[k] / 2
                if s:  # each word pops around its own centre inside the group's scale
                    fl, band, bx, by, adv = text_layers(s, f, 0.0, (hi, fill, dim)[looks[k]], stroke, 9)
                    ox, oy = int(round(cx - adv / 2 - bx)), int(round(y + (f.asc - f.desc) / 2 - by))
                    fills.put(place((fl, ox, oy), scale=pops[k], cx=cx, cy=y))
                    strokes.put(place((band, ox, oy), scale=pops[k], cx=cx, cy=y))
                x += widths[k] + space
            placed = place(fills.element(), scale=scale, cx=W / 2, cy=y)
            if not placed:
                return None
            # CG shadows each drawing call, in device space (after the scale): the fill with its shadow,
            # then the stroke with its own shadow, which also falls over the fill and shades it
            group = Canvas.wrap(placed)
            group.shadow(4, 12, 0.55)
            outline = Canvas.wrap(place(strokes.element(), scale=scale, cx=W / 2, cy=y))
            outline.shadow(4, 12, 0.55)
            group.put(outline.element())
            return group.element()

        el = cached(("caption", li, i, tuple(looks)), build, keep=4) if settled else build()
        fr.put(el)


def draw_title(fr, j, t, li):  # drawTitle
    t0, t1 = num(j, "t0", 0), num(j, "t1", 0)
    if not (t0 <= t < t1):
        return
    p_in, p_out = envelope(t, t0, t1, 0.35, 0.25)
    size = num(j, "size", 64)
    cx, cy = num(j, "x", 0.5) * W, num(j, "y", 0.2) * H

    def build():
        fsize = size
        f = font(text_of(j, "font", "heavy"), fsize)
        lines = text_of(j, "text", "").split("\n")
        bw = max(f.advance(s, 1.5) for s in lines) + fsize * 0.9
        if bw > W * 0.88:  # a wide font (Windows has no Avenir) shrinks instead of leaving the frame
            fsize *= W * 0.88 / bw
            f = font(text_of(j, "font", "heavy"), fsize)
        pad, line_h = fsize * 0.45, fsize * 1.15
        fg = color(text_of(j, "color", "#FFFFFF"))
        bw = max(f.advance(s, 1.5) for s in lines) + pad * 2
        bh = line_h * len(lines) + pad * 1.1
        cv = Canvas(cx - bw / 2 - 2, cy - bh / 2 - 2, cx + bw / 2 + 2, cy + bh / 2 + 2)
        cv.rrect(cx, cy, bw, bh, fsize * 0.28, color(text_of(j, "bg", "#FF5A1F")))
        cv.shadow(6, 18, 0.35)
        for i, s in enumerate(lines):
            cv.text(s, f, cx, cy - line_h * (len(lines) - 1) / 2 + line_h * i, fg, kern=1.5)
        return cv.element()

    fr.put(place(cached(("title", li), build), alpha=min(p_in * 1.5, p_out),
                 scale=0.6 + 0.4 * ease_out_back(p_in), cx=cx, cy=cy))


def draw_pin(fr, j, t, li):  # drawPin
    t0, t1 = num(j, "t0", 0), num(j, "t1", 0)
    if not (t0 <= t < t1):
        return
    _, p_out = envelope(t, t0, t1, 0.2, 0.25)
    cx, tip_y = num(j, "x", 0.5) * W, num(j, "y", 0.4) * H
    r = num(j, "size", 58)
    drop = bounce((t - t0) / 0.7)
    y = tip_y - (1 - drop) * num(j, "drop", 260)
    hexs = text_of(j, "color", "#FF3B30")
    c = color(hexs)
    since = t - t0 - 0.7
    if since > 0:  # pulse rings at the tip after landing (drawn outside withTransform: alpha 1)
        for k in range(2):
            p = math.fmod(since + k * 0.6, 1.2) / 1.2
            rr = 20 + p * 110
            ring = color(hexs, (1 - p) * 0.8 * p_out)

            def draw(d, T, s, rr=rr):
                ellipse_on(d, T, cx, tip_y, rr + 3, rr * 0.45 + 3, 255)
                ellipse_on(d, T, cx, tip_y, rr - 3, rr * 0.45 - 3, 0)
            fr.paint(shape_mask(cx - rr - 3, tip_y - rr * 0.45 - 3, cx + rr + 3, tip_y + rr * 0.45 + 3, draw), ring)

    def body():
        top = tip_y - r * 2.2  # circle centre, above the tip
        cv = Canvas(cx - r - 2, top - r - 2, cx + r + 2, tip_y + 2)
        cv.ellipse(cx, top, r, r, c)
        cv.polygon([(cx - r * 0.82, top + r * 0.55), (cx + r * 0.82, top + r * 0.55), (cx, tip_y)], c)
        cv.shadow(8, 16, 0.45)
        cv.ellipse(cx, top, r * 0.42, r * 0.42, color("#FFFFFF"))
        return cv.element()

    fr.put(place(cached(("pin", li), body), alpha=p_out, dy=y - tip_y))
    label = j.get("label")
    if isinstance(label, str):
        ly = tip_y - r * 2.2 - 90
        label_size = num(j, "label_size", 40)

        def tag():
            f = font("heavy", label_size)
            cv = Canvas(0, ly - label_size, W, ly + label_size)
            cv.rrect(cx, ly, f.advance(label, 1) + 44, label_size * 1.6, 18, c)
            cv.text(label, f, cx, ly, color("#FFFFFF"), kern=1)
            return cv.element()
        fr.put(place(cached(("pin-label", li), tag), alpha=clamp((t - t0 - 0.6) / 0.3) * p_out))


def draw_badge(fr, j, t, li):  # drawBadge
    t0, t1 = num(j, "t0", 0), num(j, "t1", 0)
    if not (t0 <= t < t1):
        return
    p_in, p_out = envelope(t, t0, t1, 0.3, 0.2)

    def build():
        size = num(j, "size", 34)
        f = font(text_of(j, "font", "heavy"), size)
        s = text_of(j, "text", "")
        bw, bh = f.advance(s, 2) + size * 1.2, size * 1.7
        corner = text_of(j, "corner", "top-left")
        margin = 56.0
        cx = margin + bw / 2 if corner.endswith("left") else W - margin - bw / 2
        cy = num(j, "top", 170) + bh / 2 if corner.startswith("top") else H - num(j, "bottom", 320) - bh / 2
        cv = Canvas(cx - bw / 2 - 3, cy - bh / 2 - 3, cx + bw / 2 + 3, cy + bh / 2 + 3)
        cv.rrect(cx, cy, bw, bh, 12, color(text_of(j, "bg", "#000000B3")))
        cv.rrect_stroke(cx, cy, bw, bh, 12, 3, color(text_of(j, "border", "#FFD23F")))
        cv.text(s, f, cx, cy, color(text_of(j, "color", "#FFFFFF")), kern=2)
        return cv.element()

    fr.put(place(cached(("badge", li), build), alpha=min(p_in, p_out), dy=(1 - ease_out_cubic(p_in)) * -20))


def format_number(v, sep):
    out = []
    for i, ch in enumerate(reversed(str(v))):
        if i > 0 and i % 3 == 0:
            out.append(sep[::-1])
        out.append(ch)
    return "".join(out)[::-1]


def draw_counter(fr, j, t, li):  # drawCounter
    t0, t1 = num(j, "t0", 0), num(j, "t1", 0)
    if not (t0 <= t < t1):
        return
    p_in, p_out = envelope(t, t0, t1, 0.25, 0.25)
    start, end = num(j, "from", 0), num(j, "to", 1000)
    p = ease_out_cubic((t - t0) / num(j, "run", 1.6))
    value = swift_round(start + (end - start) * p)
    cx, cy = W / 2, num(j, "y", 0.42) * H
    size = num(j, "size", 230)

    def build():
        f, cf, sf = font("heavy", size), font("heavy", size * 0.3), font("demi", size * 0.18)
        digits = format_number(value, text_of(j, "sep", "."))
        caption, sub = text_of(j, "caption", ""), text_of(j, "sub", "")
        half = max(f.advance(digits), cf.advance(caption, 3), sf.advance(sub, 1)) / 2 + size * 0.3
        cv = Canvas(cx - half, cy - size, cx + half, cy + size * 1.4)
        cv.text(digits, f, cx, cy, color(text_of(j, "color", "#FFD23F")))
        cv.text(caption, cf, cx, cy + size * 0.72, color("#FFFFFF"), kern=3)
        cv.text(sub, sf, cx, cy + size * 1.08, color("#FFFFFF", 0.85), kern=1)
        cv.shadow(8, 24, 0.5)
        return cv.element()

    fr.put(place(cached(("counter", li, value), build, keep=3), alpha=min(p_in, p_out),
                 scale=0.9 + 0.1 * ease_out_back(p_in), cx=cx, cy=cy))


def grid():
    """The map's faint grid: 2 px lines every 90 px (vertical from the left, horizontal from the bottom)."""
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for x in range(0, W + 1, 90):
        d.rectangle([x - 1, 0, x, H - 1], fill=255)
    for i in range(0, H + 1, 90):
        d.rectangle([0, H - i - 1, W - 1, H - i], fill=255)
    return colored(m, color("#FFFFFF", 0.06)), 0, 0


def partial(pts, p):
    """The first `p` of a polyline, by length."""
    segs = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    remain = sum(segs) * p
    out = [pts[0]]
    for i in range(1, len(pts)):
        if remain >= segs[i - 1]:
            out.append(pts[i])
            remain -= segs[i - 1]
        else:
            f = remain / segs[i - 1]
            out.append((pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f,
                        pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f))
            break
    return out


def stroke_mask(pts, width, round_caps=True):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    m = width / 2 + 2
    return shape_mask(min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m,
                      lambda d, T, s: polyline_on(d, T, s, pts, width, round_caps))


def draw_map(fr, j, t, li):  # drawMap
    t0, t1 = num(j, "t0", 0), num(j, "t1", 0)
    if not (t0 <= t < t1):
        return
    p_in, p_out = envelope(t, t0, t1, 0.3, 0.25)
    a = min(p_in, p_out)
    if a <= 0.001:  # the outer withTransform: nothing of the map, labels included
        return
    fr.put(place(cached(("grid",), grid), alpha=a))
    round_caps = False  # CG keeps the roads' round cap for the distance line drawn after them
    for ri, road in enumerate(dict_list(j.get("roads"))):
        raw = road.get("points")
        pts = [point(q) for q in raw] if isinstance(raw, list) else []
        if len(pts) < 2 or any(q is None for q in pts):
            continue
        p = ease_in_out((t - (t0 + num(road, "at", 0.2))) / num(road, "draw", 1.0))
        if p <= 0:
            continue
        hexs = text_of(road, "color", "#FFD23F")
        width = num(road, "width", 14)
        px = [(q[0] * W, q[1] * H) for q in pts]

        def build(p=p, px=px, road=road, hexs=hexs, width=width):
            path = partial(px, p)
            xs, ys = [q[0] for q in path], [q[1] for q in path]
            m = width * 1.3 + 4
            cv = Canvas(min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m)
            if road.get("glow") is True or road.get("glow") == 1:
                cv.paint(stroke_mask(path, width * 2.6), color(hexs, 0.3))
            cv.paint(stroke_mask(path, width), color(hexs))
            return cv.element()

        key_p = 1.0 if p >= 1 else round(p, 4)
        fr.put(place(cached(("road", li, ri, key_p), build, keep=0 if key_p == 1.0 else 2), alpha=a))
        round_caps = True
        label, lp = road.get("label"), point(road.get("label_at"))
        if isinstance(label, str) and p > 0.6 and lp:
            def tag(road=road, label=label, lp=lp, hexs=hexs):
                f = font("heavy", num(road, "label_size", 34))
                cv = Canvas(0, lp[1] * H - f.size, W, lp[1] * H + f.size)
                cv.text(label, f, lp[0] * W, lp[1] * H, color(hexs), kern=1)
                return cv.element()
            fr.put(place(cached(("road-label", li, ri), tag), alpha=clamp((p - 0.6) / 0.3)))
    for pi, spot in enumerate(dict_list(j.get("places"))):
        at = point(spot.get("at_xy"))
        if not at:
            continue
        ps = t0 + num(spot, "at", 0.4)
        pa = ease_out_back((t - ps) / 0.35)
        if t < ps:
            continue
        cx, cy = at[0] * W, at[1] * H

        def build(spot=spot, cx=cx, cy=cy):
            c = color(text_of(spot, "color", "#FFFFFF"))
            r = num(spot, "size", 18)
            f = font(text_of(spot, "font", "bold"), num(spot, "label_size", 34))
            off = num(spot, "label_dy", -52)
            label = text_of(spot, "label", "")
            half = max(r + 4, f.advance(label) / 2 + f.size * 0.2)
            cv = Canvas(cx - half, min(cy - r, cy + off - f.size) - 4, cx + half, max(cy + r, cy + off + f.size) + 4)
            cv.ellipse(cx, cy, r, r, c)

            def ring(d, T, s):
                ellipse_on(d, T, cx, cy, r + 2, r + 2, 255)
                ellipse_on(d, T, cx, cy, r - 2, r - 2, 0)
            cv.paint(shape_mask(cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2, ring), color("#000000", 0.6))
            cv.text(label, f, cx, cy + off, c, stroke_rgba=color("#000000", 0.9), stroke_pct=5)
            return cv.element()

        fr.put(place(cached(("place", li, pi), build), alpha=clamp(pa), scale=max(0.01, pa), cx=cx, cy=cy))
    dist = j.get("distance")
    if isinstance(dist, dict) and isinstance(dist.get("points"), list) and len(dist["points"]) == 2:
        ends = [point(q) for q in dist["points"]]
        if None in ends:
            return
        p = ease_in_out((t - (t0 + num(dist, "at", 1.4))) / 0.7)
        if p <= 0:
            return
        a0 = (ends[0][0] * W, ends[0][1] * H)
        a1 = (ends[1][0] * W, ends[1][1] * H)

        def dashes(p=p, caps=round_caps):
            b = (a0[0] + (a1[0] - a0[0]) * p, a0[1] + (a1[1] - a0[1]) * p)
            length = math.hypot(b[0] - a0[0], b[1] - a0[1])
            if length <= 0:
                return None
            ux, uy = (b[0] - a0[0]) / length, (b[1] - a0[1]) / length
            spans, s0 = [], 0.0
            while s0 < length:  # CG dash [16, 12], phase 0
                s1 = min(s0 + 16, length)
                spans.append(((a0[0] + ux * s0, a0[1] + uy * s0), (a0[0] + ux * s1, a0[1] + uy * s1)))
                s0 += 28

            def draw(d, T, s):
                for q0, q1 in spans:
                    polyline_on(d, T, s, [q0, q1], 5, caps)
            mask = shape_mask(min(a0[0], b[0]) - 5, min(a0[1], b[1]) - 5, max(a0[0], b[0]) + 5,
                              max(a0[1], b[1]) + 5, draw)
            return (colored(mask[0], color("#FFFFFF")), mask[1], mask[2]) if mask else None

        key_p = 1.0 if p >= 1 else round(p, 4)
        fr.put(place(cached(("dist", li, key_p, round_caps), dashes, keep=0 if key_p == 1.0 else 2), alpha=a))
        lp = point(dist.get("label_at"))
        if p > 0.8 and lp:
            cx, cy = lp[0] * W, lp[1] * H

            def tag():
                size = num(dist, "size", 56)
                f = font("heavy", size)
                label = text_of(dist, "label", "")
                bw = f.advance(label, 1) + 50
                cv = Canvas(cx - bw / 2 - 2, cy - size, cx + bw / 2 + 2, cy + size)
                cv.rrect(cx, cy, bw, size * 1.5, 20, color(text_of(dist, "bg", "#FFD23F")))
                cv.text(label, f, cx, cy, color(text_of(dist, "color", "#111111")), kern=1)
                return cv.element()
            q = (p - 0.8) / 0.2
            fr.put(place(cached(("dist-label", li), tag), alpha=clamp(q), scale=0.7 + 0.3 * ease_out_back(q),
                         cx=cx, cy=cy))


def draw_callouts(fr, j, t, li):  # drawCallouts
    t0, t1 = num(j, "t0", 0), num(j, "t1", 0)
    if not (t0 <= t < t1):
        return
    _, p_out = envelope(t, t0, t1, 0.2, 0.25)
    size = num(j, "size", 58)
    y0 = num(j, "y", 0.3) * H
    for i, item in enumerate(dict_list(j.get("items"))):
        at = t0 + num(item, "at", i * 0.8)
        if t < at:
            continue
        p = ease_out_back((t - at) / 0.35)
        cy = y0 + i * size * 1.9

        def build(item=item, cy=cy):
            f = font("heavy", size)
            s = text_of(item, "text", "")
            bw = f.advance(s, 1.5) + size * 1.6
            cx = W / 2
            cv = Canvas(cx - bw / 2 - 2, cy - size, cx + bw / 2 + 2, cy + size)
            cv.rrect(cx, cy, bw, size * 1.45, 16, color(text_of(j, "bg", "#FFFFFF")))
            cv.shadow(6, 14, 0.4)
            cv.ellipse(cx - bw / 2 + size * 0.53, cy, size * 0.18, size * 0.18, color(text_of(j, "accent", "#FF5A1F")))
            cv.text(s, f, cx + size * 0.2, cy, color("#111111"), kern=1.5)
            return cv.element()

        fr.put(place(cached(("callout", li, i), build), alpha=clamp(p) * p_out, dx=(1 - clamp(p)) * -300))


def draw_card_text(fr, j, t, li):  # drawCardText
    t0, t1 = num(j, "t0", 0), num(j, "t1", 0)
    if not (t0 <= t < t1):
        return
    p_in, p_out = envelope(t, t0, t1, 0.3, 0.2)

    def build():
        cx, cy = W / 2, num(j, "y", 0.5) * H
        size = num(j, "size", 40)
        f = font(text_of(j, "font", "demi"), size)
        lines = text_of(j, "text", "").split("\n")
        ys = [cy + i * size * 1.35 - (len(lines) - 1) * size * 0.67 for i in range(len(lines))]
        cv = Canvas(0, min(ys) - size * 1.5, W, max(ys) + size * 1.5)
        for s, ly in zip(lines, ys):
            cv.text(s, f, cx, ly, color(text_of(j, "color", "#FFFFFF")), kern=1)
        return cv.element()

    fr.put(place(cached(("card", li), build), alpha=min(p_in, p_out) * num(j, "opacity", 1)))


def draw_endcard(fr, j, t, li):  # drawEndcard
    t0, t1 = num(j, "t0", 0), num(j, "t1", 0)
    if not (t0 <= t < t1):
        return
    p = ease_out_cubic((t - t0) / 0.5)
    bg = color(text_of(j, "bg", "#0F1B2D"), clamp(p * 1.2) * num(j, "bg_alpha", 1))
    if bg[3] > 0:
        fr.put((Image.new("RGBA", (W, H), (to8(bg[0]), to8(bg[1]), to8(bg[2]), to8(bg[3]))), 0, 0))
    cx, by = W / 2, H * 0.38

    def brand():
        name = text_of(j, "brand", "")
        brand_size = num(j, "brand_size", 110)
        width = font("heavy", brand_size).advance(name, 6)
        if width > W * 0.88:  # a long name shrinks to fit
            brand_size *= W * 0.88 / width
        cv = Canvas(0, by - brand_size * 1.5, W, by + 100 + 60)
        cv.text(name, font("heavy", brand_size), cx, by, color(text_of(j, "brand_color", "#FFFFFF")), kern=6)
        cv.text(text_of(j, "tagline", ""), font("demi", 40), cx, by + 100, color("#FFFFFF", 0.8), kern=3)
        return cv.element()

    fr.put(place(cached(("brand", li), brand), alpha=p, scale=0.9 + 0.1 * ease_out_back((t - t0) / 0.6),
                 cx=cx, cy=by))
    cta_p = ease_out_back((t - t0 - 0.35) / 0.4)
    if t > t0 + 0.35:
        cy = H * 0.55

        def cta():
            f = font("heavy", 60)
            s = text_of(j, "cta", "")
            bw = f.advance(s, 1) + 90
            if bw > W * 0.9:  # a wide font shrinks to keep the button inside the frame
                f = font("heavy", 60 * (W * 0.9 - 90) / (bw - 90))
                bw = f.advance(s, 1) + 90
            cv = Canvas(cx - bw / 2 - 2, cy - 57, cx + bw / 2 + 2, cy + 57)
            cv.rrect(cx, cy, bw, 110, 55, color(text_of(j, "accent", "#FFD23F")))
            cv.text(s, f, cx, cy, color("#111111"), kern=1)
            return cv.element()
        fr.put(place(cached(("cta", li), cta), alpha=clamp(cta_p), scale=0.7 + 0.3 * cta_p, cx=cx, cy=cy))

        def phone():
            cv = Canvas(0, H * 0.64 - 100, W, H * 0.64 + 100)
            phone_size = 64
            width = font("heavy", phone_size).advance(text_of(j, "phone", ""), 3)
            if width > W * 0.9:
                phone_size *= W * 0.9 / width
            cv.text(text_of(j, "phone", ""), font("heavy", phone_size), cx, H * 0.64, color("#FFFFFF"), kern=3)
            return cv.element()
        fr.put(place(cached(("phone", li), phone), alpha=clamp((t - t0 - 0.6) / 0.3)))

    def disclaimer():
        cv = Canvas(0, H * 0.9 - 60, W, H * 0.9 + 60)
        cv.text(text_of(j, "disclaimer", ""), font("demi", 30), cx, H * 0.9, color("#FFFFFF", 0.75))
        return cv.element()
    fr.put(place(cached(("disclaimer", li), disclaimer), alpha=clamp((t - t0 - 0.5) / 0.3)))


DRAW = {"caption": draw_caption, "title": draw_title, "pin": draw_pin, "badge": draw_badge,
        "counter": draw_counter, "map": draw_map, "callouts": draw_callouts, "card_text": draw_card_text,
        "endcard": draw_endcard}


# ---------------------------------------------------------------- main

def render(spec, out):
    """Write every frame of `spec` to the binary stream `out`."""
    global W, H, FPS, DURATION
    W, H = int(num(spec, "width", 1080)), int(num(spec, "height", 1920))
    FPS, DURATION = num(spec, "fps", 30), num(spec, "duration", 1)
    if isinstance(spec.get("fonts"), dict):
        FONT_NAMES.update({k: v for k, v in spec["fonts"].items() if isinstance(k, str) and isinstance(v, str)})
    layers = dict_list(spec.get("layers"))
    blank = bytes(W * H * 4)
    frames = int(math.ceil(DURATION * FPS))
    for i in range(frames):
        t = i / FPS
        fr = Frame()
        for li, layer in enumerate(layers):
            kind = text_of(layer, "type", "")
            if kind != "caption" and (t < num(layer, "t0", 0) or t >= num(layer, "t1", 0)):
                continue
            draw = DRAW.get(kind)
            if draw:
                try:
                    draw(fr, layer, t, li)
                except Exception as exc:  # a malformed layer is skipped, as Swift's `as?` casts skip it
                    warn("layer %d (%s) skipped: %s: %s" % (li, kind, type(exc).__name__, exc))
        out.write(fr.img.convert("RGBa").tobytes() if fr.img is not None else blank)


def main(argv):
    try:
        with open(argv[1], "rb") as fh:
            spec = json.loads(fh.read().decode("utf-8"))
        if not isinstance(spec, dict):
            raise ValueError("not an object")
    except (IndexError, OSError, ValueError):
        sys.stderr.write("usage: overlay.py <spec.json>\n")
        return 1
    if PLATFORM == "win32":  # raw bytes on stdout, no newline translation
        import msvcrt
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    out = sys.stdout.buffer
    try:
        render(spec, out)
        out.flush()
    except (BrokenPipeError, OSError) as exc:
        if not isinstance(exc, BrokenPipeError) and exc.errno not in (errno.EPIPE, errno.EINVAL):
            raise
        # the reader (ffmpeg) has every frame it needs and closed the pipe: not an error
        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
