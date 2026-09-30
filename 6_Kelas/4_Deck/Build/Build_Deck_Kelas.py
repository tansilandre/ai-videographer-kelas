"""Builds the class deck as PowerPoint: 6_Kelas/4_Deck/Kelas_AI_Videographer_Deck_v<X.Y>.pptx (keep only the newest
there; git keeps the old ones). Export the PDF from PowerPoint next to it.

Part 1 is the AI basics (what AI is and how it "thinks"), part 2 the practice (brief to reel) with the
anonymised Tebak Harga example. Fonts are Arial (headings) and Calibri (body): both ship with Office.
Run: python3 Build_Deck_Kelas.py [version | draft]   (e.g. 1.5; draft writes Build/Draft_Kelas_Deck.pptx)
"""
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).resolve().parent
IMG = HERE / "1_Images"
VERSION = sys.argv[1] if len(sys.argv) > 1 else "1.0"
DRAFT = VERSION == "draft"  # a scratch build for checking, overwritten freely
OUT = HERE / "Draft_Kelas_Deck.pptx" if DRAFT else HERE.parent / ("Kelas_AI_Videographer_Deck_v%s.pptx" % VERSION)

INK, WHITE, PAPER = "16181D", "FFFFFF", "F4F2EE"
ORANGE, ORANGE_TXT = "FF5A1F", "C2410C"
BODY, BODY_DARK, MUTED = "3D424B", "D3CEC5", "6B7079"
CARD, LINE, CARD_DARK = "F7F6F3", "E3E0DA", "24272F"
HEAD, TEXT = "Arial", "Calibri"
W, H = 13.333, 7.5
M = 0.6            # side margin
CW = W - 2 * M     # content width

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
BLANK = prs.slide_layouts[6]
page = [0]


def rgb(hexstr):
    return RGBColor.from_string(hexstr)


def new_slide(bg=WHITE, notes=""):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(bg)
    page[0] += 1
    if page[0] > 1:
        text(s, W - M - 1.0, H - 0.5, 1.0, 0.3, str(page[0]), size=14,
             color=BODY_DARK if bg in (INK, CARD_DARK) else MUTED, align=PP_ALIGN.RIGHT)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def _runs(p, line, size, color, font, bold):
    """`line` may hold **bold** parts."""
    parts = line.split("**")
    for i, part in enumerate(parts):
        if not part:
            continue
        r = p.add_run()
        r.text = part
        r.font.size, r.font.name = Pt(size), font
        r.font.bold = bold or (i % 2 == 1)
        r.font.color.rgb = rgb(color)


def _bullet(p, kind, indent=0.34):
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(int(Inches(indent))))
    pPr.set("indent", str(-int(Inches(indent))))
    font = etree.SubElement(pPr, qn("a:buFont"))
    font.set("typeface", "Arial")
    if kind == "num":
        auto = etree.SubElement(pPr, qn("a:buAutoNum"))
        auto.set("type", "arabicPeriod")
    else:
        char = etree.SubElement(pPr, qn("a:buChar"))
        char.set("char", "•")


def text(s, x, y, w, h, lines, size=22, color=BODY, font=TEXT, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=1.12, after=0, bullets=None):
    """One text box; `lines` is a string or a list of paragraphs. bullets: None, "dot" or "num"."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, line in enumerate([lines] if isinstance(lines, str) else lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_after = Pt(after)
        _runs(p, line, size, color, font, bold)
        if bullets:
            _bullet(p, bullets)
    return tb


def box(s, x, y, w, h, fill=CARD, line=LINE, radius=0.08, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    shp = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        shp.adjustments[0] = radius
    shp.fill.solid()
    shp.fill.fore_color.rgb = rgb(fill)
    if line:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Pt(1)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def pill(s, x, y, w, h, label, fill=ORANGE, color=INK, size=18):
    shp = box(s, x, y, w, h, fill=fill, line=None, radius=0.5)
    tf = shp.text_frame
    tf.margin_left = tf.margin_right = Inches(0.12)
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    _runs(p, label, size, color, TEXT, True)
    return shp


def circle(s, x, y, d, label, fill=ORANGE, color=INK, size=24):
    shp = box(s, x, y, d, d, fill=fill, line=None, shape=MSO_SHAPE.OVAL)
    tf = shp.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    _runs(p, label, size, color, HEAD, True)
    return shp


def arrow(s, x, y, w=0.5, h=0.34, fill=ORANGE):
    return box(s, x, y, w, h, fill=fill, line=None, shape=MSO_SHAPE.RIGHT_ARROW)


def picture(s, name, x, y, w, h, radius=0.06, focus_y=0.5):
    """An image filling the box (cropped, not stretched), with rounded corners."""
    pic = s.shapes.add_picture(str(IMG / name), Inches(x), Inches(y))
    iw, ih = pic.image.size
    box_ratio, img_ratio = w / h, iw / ih
    if img_ratio > box_ratio:
        keep = box_ratio / img_ratio
        pic.crop_left = pic.crop_right = (1 - keep) / 2
    else:
        keep = img_ratio / box_ratio
        pic.crop_top = (1 - keep) * focus_y
        pic.crop_bottom = (1 - keep) * (1 - focus_y)
    pic.left, pic.top, pic.width, pic.height = Inches(x), Inches(y), Inches(w), Inches(h)
    geom = pic._element.spPr.find(qn("a:prstGeom"))
    geom.set("prst", "roundRect")
    av = geom.find(qn("a:avLst"))
    if av is None:
        av = etree.SubElement(geom, qn("a:avLst"))
    gd = etree.SubElement(av, qn("a:gd"))
    gd.set("name", "adj")
    gd.set("fmla", "val %d" % int(radius * 100000))
    return pic


def phone(s, name, x, y, h):
    """A 9:16 frame of the reel, `h` inches tall."""
    return picture(s, name, x, y, h * 9 / 16, h, radius=0.07)


def header(s, title, eyebrow=None, dark=False, size=40):
    if eyebrow:
        text(s, M, 0.42, CW, 0.35, eyebrow.upper(), size=16, bold=True, font=HEAD,
             color=ORANGE if dark else ORANGE_TXT)
    text(s, M, 0.78, CW, 1.0, title, size=size, bold=True, font=HEAD, color=WHITE if dark else INK,
         spacing=1.0)


def table(s, x, y, w, col_w, rows, size=20, dark=False, row_h=0.62):
    """rows[0] is the header."""
    shape = s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(row_h * len(rows)))
    tbl = shape.table
    tbl.first_row = True
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        tbl.rows[i].height = Inches(row_h)
        for j, value in enumerate(row):
            cell = tbl.cell(i, j)
            cell.fill.solid()
            if i == 0:
                cell.fill.fore_color.rgb = rgb(ORANGE)
            else:
                cell.fill.fore_color.rgb = rgb((CARD_DARK if i % 2 else INK) if dark else (WHITE if i % 2 else CARD))
            cell.margin_left = cell.margin_right = Inches(0.14)
            cell.margin_top = cell.margin_bottom = Inches(0.07)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            _runs(p, value, size, INK if i == 0 else (WHITE if dark else INK), TEXT, i == 0)
    return shape


# ============================================================ opening

s = new_slide(INK, "Selamat datang. Hari ini kita belajar dua hal: dasar AI, supaya kamu paham alat yang kamu pakai, lalu "
              "praktik membuat satu reel properti dari brief sampai video 9:16. Contohnya reel 'Tebak Harga'. Semua "
              "gambar di kelas ini dibuat AI dan semua nama fiktif.")
text(s, M, 1.1, 7.6, 0.4, "KELAS AI VIDEOGRAPHER", size=20, bold=True, font=HEAD, color=ORANGE)
text(s, M, 1.65, 7.8, 2.6, "Dari brief ke reel, dengan AI", size=60, bold=True, font=HEAD, color=WHITE, spacing=0.95)
text(s, M, 4.2, 7.4, 1.4, "Dasar AI dan praktik membuat video properti 9:16, langkah demi langkah, untuk kamu yang baru mulai.",
     size=24, color=BODY_DARK, spacing=1.15)
text(s, M, 6.55, 8.2, 0.5, "Contoh: reel ‘Tebak Harga’ · nama fiktif, semua gambar dibuat AI",
     size=16, color=BODY_DARK)
phone(s, "Frame_hook.jpg", W - M - 3.66, 0.6, 6.5)

s = new_slide(WHITE, "Kenalan dulu. Saya Andre Tansil. Delapan tahun lebih saya bekerja di software, business analysis dan "
              "product: mulai sebagai developer, lalu memimpin tim engineering, lalu product manager. Sekarang saya Senior "
              "Business Analyst di ROOTCLOUD dan memimpin komunitas AICLUB.ID Tangerang Selatan. Alat yang kita pakai hari "
              "ini, AI Videographer, saya bangun sendiri untuk membuat reel properti dengan AI.")
header(s, "Kenalan dulu", "Pengajar")
picture(s, "Andre_Tansil.jpg", M, 1.95, 4.1, 4.95, radius=0.06, focus_y=0.3)
text(s, 5.3, 1.95, 7.4, 0.8, "Andre Tansil", size=40, bold=True, font=HEAD, color=INK)
text(s, 5.3, 2.8, 7.4, 0.5, "AI Specialist · AI Automation Builder", size=22, bold=True, color=ORANGE_TXT)
text(s, 5.3, 3.4, 7.4, 3.0, ["8+ tahun di software, business analysis dan product: dari developer sampai product manager",
                             "Senior Business Analyst di **ROOTCLOUD**",
                             "Teknik Telekomunikasi **ITB**, S2 di **SeoulTech** Korea: riset machine learning",
                             "Community Lead **AICLUB.ID** Tangerang Selatan",
                             "Pembuat **AI Videographer**, alat yang kita pakai hari ini"],
     size=19, bullets="dot", after=6)
text(s, 5.3, 6.58, 7.4, 0.4, "linkedin.com/in/andretansil  ·  Instagram @andretansil", size=16, color=MUTED)

s = new_slide(WHITE, "Ini tiga frame dari reel contoh: hook di detik pertama, petunjuk tentang rumahnya, dan jawaban harga. "
              "Di akhir kelas kamu tahu cara membuat semua bagian ini, dan kapan harus berhenti untuk memeriksa.")
header(s, "Yang akan kamu buat")
for i, name in enumerate(("Frame_hook.jpg", "Frame_petunjuk3.jpg", "Frame_harga.jpg")):
    phone(s, name, M + i * 2.85, 1.95, 4.75)
text(s, 9.3, 2.2, 3.45, 1.2, "Reel 9:16, sekitar 28 detik", size=28, bold=True, font=HEAD, color=INK, spacing=1.0)
text(s, 9.3, 3.55, 3.45, 3.0, ["Narasi dan musik", "Caption yang menyala per kata", "Judul, peta dan transisi",
                               "Klip AI yang bergerak"], size=22, bullets="dot", after=10)

s = new_slide(WHITE, "Kelas ini punya dua bagian. Bagian pertama teori: apa itu AI dan bagaimana cara berpikirnya. "
              "Bagian kedua praktik: tujuh tahap membuat reel, dengan contoh nyata.")
header(s, "Dua bagian hari ini")
for i, (num, name, items) in enumerate((
        ("1", "Dasar AI", ["Apa itu AI, dan cara ia belajar", "Kenapa AI menebak, bukan tahu", "Model gambar, video dan suara",
                           "Agent AI", "Cara berpikir, prompt, batas dan etika"]),
        ("2", "Praktik", ["Aturan emas dan alur kerja", "Tujuh tahap dari brief ke reel", "Kesalahan kami, dan aturannya",
                          "Latihan pertamamu"]))):
    x = M + i * 6.15
    box(s, x, 1.95, 5.95, 4.95)
    circle(s, x + 0.4, 2.3, 0.85, num, size=32)
    text(s, x + 1.45, 2.42, 4.2, 0.7, name, size=32, bold=True, font=HEAD, color=INK)
    text(s, x + 0.45, 3.5, 5.1, 3.2, items, size=22, bullets="dot", after=10)

# ============================================================ part 1: AI basics

s = new_slide(INK, "Sebelum menyentuh alatnya, kita pahami dulu cara kerja AI. Orang yang paham cara berpikir AI "
              "menulis prompt yang lebih baik dan tahu kapan harus curiga pada hasilnya.")
circle(s, M, 1.4, 1.3, "1", size=48)
text(s, M, 3.0, 11.5, 0.4, "BAGIAN 1", size=20, bold=True, font=HEAD, color=ORANGE)
text(s, M, 3.5, 11.8, 2.0, "Dasar AI: apa itu AI, dan bagaimana ia “berpikir”", size=54, bold=True, font=HEAD,
     color=WHITE, spacing=0.95)
text(s, M, 5.55, 10.5, 1.0, "Kalau kamu paham cara kerjanya, kamu tahu cara memintanya, dan kapan harus curiga pada hasilnya.",
     size=24, color=BODY_DARK)

s = new_slide(WHITE, "Program biasa: manusia menulis semua aturannya. AI berbeda: kita tidak menulis aturannya, kita "
              "memberi contoh sangat banyak, lalu komputer menemukan polanya sendiri. Karena itu AI bisa membuat hal "
              "yang belum pernah ada, tapi juga bisa keliru.")
header(s, "Apa itu AI?", "Bagian 1 · Dasar AI")
for i, (name, lead, example) in enumerate((
        ("Program biasa", "Manusia menulis aturannya satu per satu.",
         "Contoh: “kalau luas tanah lebih dari 100 m², tulis ‘rumah besar’.” Komputer hanya menjalankan aturan itu."),
        ("Kecerdasan buatan (AI)", "Komputer belajar pola dari jutaan contoh, lalu menebak.",
         "Contoh: diberi jutaan foto rumah beserta keterangannya, ia belajar seperti apa ‘rumah modern’, lalu bisa "
         "menggambar rumah yang belum pernah ada."))):
    x = M + i * 6.15
    box(s, x, 1.95, 5.95, 3.7, fill=CARD if i == 0 else "FFF1EA", line=LINE if i == 0 else "F6C9B5")
    text(s, x + 0.4, 2.2, 5.2, 0.6, name, size=28, bold=True, font=HEAD, color=INK if i == 0 else ORANGE_TXT)
    text(s, x + 0.4, 2.9, 5.2, 1.0, lead, size=22, bold=True, color=INK)
    text(s, x + 0.4, 4.05, 5.2, 1.4, example, size=20, color=BODY)
box(s, M, 5.9, CW, 1.0, fill=INK, line=None, radius=0.2)
text(s, M + 0.4, 5.9, CW - 0.8, 1.0, "AI adalah mesin pengenal pola. Ia tidak berpikir seperti manusia: ia menebak "
     "berdasarkan pola yang pernah ia lihat.", size=22, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)

s = new_slide(WHITE, "Empat langkah ini berlaku untuk semua model yang kita pakai: teks, gambar, video, suara dan musik. "
              "Poin pentingnya: model menyimpan pola, bukan salinan contoh. Itu sebabnya ia bisa kreatif dan juga bisa salah.")
header(s, "Cara AI belajar: dari contoh ke model", "Bagian 1 · Dasar AI")
steps = [("1", "Data", "Jutaan contoh: teks, foto, video, suara."),
         ("2", "Latihan", "Menebak, dicek, diperbaiki. Miliaran kali."),
         ("3", "Model", "Hasilnya: pola yang tersimpan sebagai angka."),
         ("4", "Dipakai", "Kamu memberi prompt, model menjawab.")]
for i, (num, name, desc) in enumerate(steps):
    x = M + i * 3.1
    box(s, x, 1.95, 2.6, 3.3)
    circle(s, x + 0.3, 2.2, 0.75, num)
    text(s, x + 0.3, 3.1, 2.1, 0.55, name, size=26, bold=True, font=HEAD, color=INK)
    text(s, x + 0.3, 3.7, 2.05, 1.5, desc, size=20)
    if i < 3:
        arrow(s, x + 2.66, 3.43, 0.38, 0.34)
box(s, M, 5.55, CW, 1.3, fill="FFF1EA", line="F6C9B5", radius=0.15)
text(s, M + 0.4, 5.55, CW - 0.8, 1.3, "Model tidak menyimpan foto aslinya, ia menyimpan **polanya**. Karena itu ia bisa "
     "membuat hal baru, dan juga bisa keliru.", size=22, color=INK, anchor=MSO_ANCHOR.MIDDLE)

s = new_slide(WHITE, "Model bahasa seperti Claude menulis satu kata demi satu kata. Setiap kali, ia memilih lanjutan yang "
              "paling mungkin. Angka di grafik hanya ilustrasi. Akibatnya: jawabannya selalu terdengar lancar, bahkan saat "
              "salah. Itulah halusinasi. Maka fakta seperti harga, jarak dan nama selalu kita cek.")
header(s, "AI tidak tahu. AI menebak.", "Bagian 1 · Dasar AI")
text(s, M, 1.95, 6.2, 0.5, "“Rumah di pinggir kota itu biasanya …”", size=24, bold=True, color=INK)
data = CategoryChartData()
data.categories = ["lebih luas", "lebih murah", "jauh dari kantor", "sepi"]
data.add_series("Peluang", (0.46, 0.31, 0.15, 0.08))
chart = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(M), Inches(2.55), Inches(6.2), Inches(3.6), data).chart
chart.has_legend = False
chart.has_title = False
plot = chart.plots[0]
plot.gap_width = 55
plot.has_data_labels = True
labels = plot.data_labels
labels.number_format, labels.number_format_is_linked = "0%", False
labels.position = XL_LABEL_POSITION.OUTSIDE_END
labels.font.size, labels.font.bold = Pt(20), True
labels.font.color.rgb = rgb(INK)
series = plot.series[0]
series.format.fill.solid()
series.format.fill.fore_color.rgb = rgb(ORANGE)
chart.category_axis.reverse_order = True
chart.category_axis.tick_labels.font.size = Pt(20)
chart.category_axis.tick_labels.font.color.rgb = rgb(INK)
chart.category_axis.format.line.fill.background()
chart.value_axis.visible = False
chart.value_axis.has_major_gridlines = False
chart.value_axis.maximum_scale = 0.6
text(s, M, 6.25, 6.2, 0.4, "Angka ilustrasi: peluang kata berikutnya.", size=16, color=MUTED)
text(s, 7.35, 2.0, 5.4, 4.8, ["Model bahasa menulis **satu kata demi satu kata**, memilih lanjutan yang paling masuk akal.",
                              "Karena itu jawabannya selalu lancar, tapi bisa **salah dengan yakin**. Ini disebut halusinasi.",
                              "Aturan kita: fakta seperti harga, jarak dan nama **selalu dicek manusia**."],
     size=22, after=16, bullets="dot")

s = new_slide(WHITE, "Kita tidak memakai satu AI, tapi satu tim model. Masing-masing dilatih untuk satu jenis hasil. "
              "Agent yang mengatur semuanya adalah model teks. Video paling mahal, jadi selalu paling akhir.")
header(s, "Satu tim model, masing-masing satu keahlian", "Bagian 1 · Dasar AI")
models = [("Teks", "Claude", "Merencanakan, menulis prompt, memeriksa hasil."),
          ("Gambar", "gpt-image-2", "Style frame, storyboard, frame pertama."),
          ("Video", "Veo 3.1 Lite", "Membuat gambar yang disetujui bergerak."),
          ("Suara", "Gemini TTS", "Narasi dari naskah."),
          ("Musik", "Lyria", "Musik latar dengan drop.")]
for i, (kind, name, desc) in enumerate(models):
    x = M + i * 2.46
    box(s, x, 1.95, 2.3, 3.9)
    text(s, x + 0.25, 2.2, 1.85, 0.55, kind, size=26, bold=True, font=HEAD, color=INK)
    text(s, x + 0.25, 2.8, 1.85, 0.5, name, size=20, bold=True, color=ORANGE_TXT)
    text(s, x + 0.25, 3.4, 1.85, 2.3, desc, size=20)
text(s, M, 6.15, CW, 0.7, "Teks dan suara murah. Gambar murah. **Video paling mahal**, jadi dibuat paling akhir.",
     size=22, color=INK)

s = new_slide(WHITE, "Ini ilustrasi, bukan tangkapan layar model. Model gambar mulai dari bintik acak, lalu dalam banyak "
              "langkah membuang noise sampai gambarnya cocok dengan prompt. Ia menggambar yang paling masuk akal. "
              "Karena itu detail kecil seperti teks, logo dan jari sering salah: kita tambahkan teks di edit, bukan di gambar.")
header(s, "Model gambar: dari bintik acak ke gambar", "Bagian 1 · Dasar AI")
for i, (name, label) in enumerate((("Difusi_1.jpg", "Mulai: noise"), ("Difusi_2.jpg", "Langkah awal"),
                                   ("Difusi_3.jpg", "Hampir jadi"), ("Difusi_4.jpg", "Selesai"))):
    x = M + i * 2.12
    picture(s, name, x, 1.95, 1.95, 3.47, radius=0.05)
    text(s, x, 5.5, 1.95, 0.4, label, size=18, bold=True, color=INK, align=PP_ALIGN.CENTER)
text(s, M, 6.1, 8.3, 0.4, "Ilustrasi proses, bukan hasil langsung dari model.", size=16, color=MUTED)
text(s, 9.3, 2.0, 3.45, 4.9, ["Model mulai dari **bintik acak**, lalu sedikit demi sedikit membuang noise sampai cocok "
                              "dengan prompt.",
                              "Ia menggambar yang **paling masuk akal**, bukan yang benar.",
                              "Maka teks, logo dan jari sering salah. Teks kita tambahkan di edit."], size=21, after=14)

s = new_slide(WHITE, "Model video membuat urutan gambar, sekitar 30 per detik, yang harus konsisten satu sama lain. "
              "Frame pertama dan terakhir yang kita berikan menjadi pegangan. Yang paling sulit: gerakan tubuh, bibir, "
              "tangan, dan klip panjang. Maka aturan kita: klip pendek, satu gerakan kamera, frame pertama dari gambar "
              "yang sudah disetujui.")
header(s, "Model video: menebak gambar berikutnya", "Bagian 1 · Dasar AI")
for i, name in enumerate(("Video_Frame_1.jpg", "Video_Frame_2.jpg", "Video_Frame_3.jpg", "Video_Frame_4.jpg")):
    x = M + i * 2.12
    picture(s, name, x, 1.95, 1.95, 3.47, radius=0.05)
text(s, M, 5.5, 1.95, 0.4, "Frame pertama", size=18, bold=True, color=INK, align=PP_ALIGN.CENTER)
text(s, M + 2.12, 5.5, 4.07, 0.4, "30 gambar tiap detik", size=18, color=MUTED, align=PP_ALIGN.CENTER)
text(s, M + 6.36, 5.5, 1.95, 0.4, "Frame terakhir", size=18, bold=True, color=INK, align=PP_ALIGN.CENTER)
text(s, M, 6.1, 8.3, 0.4, "Ilustrasi: kamera maju pelan menuju pintu.", size=16, color=MUTED)
text(s, 9.3, 2.0, 3.45, 4.9, ["Setiap gambar harus **konsisten** dengan gambar sebelumnya.",
                              "Paling sulit: tubuh bergerak, **bibir**, tangan, klip panjang.",
                              "Jadi: klip pendek, **satu gerakan kamera**, frame pertama yang sudah disetujui."],
     size=21, after=14)

s = new_slide(WHITE, "Agent adalah model bahasa yang diberi alat: ia bisa membaca file, menjalankan perintah, dan melihat "
              "hasilnya. Ia bekerja dalam putaran: rencanakan, kerjakan, periksa, perbaiki. Di kelas ini agent-nya WorkBuddy "
              "dengan Expert AI Videographer; ia membaca skill, yaitu file instruksi cara kerja kita. Agent juga bisa salah, jadi gerbang persetujuan tetap di tangan kamu.")
header(s, "Agent AI: AI yang bisa memakai alat", "Bagian 1 · Dasar AI")
loop = [("1", "Rencanakan", "baca brief dan skill"), ("2", "Kerjakan", "jalankan alat vg"),
        ("4", "Perbaiki", "ulangi yang kurang"), ("3", "Periksa", "lihat hasilnya")]
for i, (num, name, desc) in enumerate(loop):
    col, row = i % 2, i // 2
    x, y = M + col * 3.75, 1.95 + row * 2.5
    box(s, x, y, 3.2, 2.0)
    circle(s, x + 0.28, y + 0.3, 0.7, num, size=22)
    text(s, x + 1.12, y + 0.4, 2.0, 0.6, name, size=22, bold=True, font=HEAD, color=INK)
    text(s, x + 0.3, y + 1.15, 2.7, 0.7, desc, size=20)
arrow(s, M + 3.26, 2.78, 0.43, 0.34)                                     # 1 -> 2
down = box(s, M + 5.18, 4.0, 0.34, 0.4, fill=ORANGE, line=None, shape=MSO_SHAPE.DOWN_ARROW)   # 2 -> 3
back = box(s, M + 3.26, 5.28, 0.43, 0.34, fill=ORANGE, line=None, shape=MSO_SHAPE.LEFT_ARROW)  # 3 -> 4
up = box(s, M + 1.43, 4.0, 0.34, 0.4, fill=ORANGE, line=None, shape=MSO_SHAPE.UP_ARROW)       # 4 -> 1
text(s, 8.25, 2.0, 4.5, 4.9, ["Agent-nya **WorkBuddy** dengan Expert **AI Videographer**. Ia membaca **skill**: "
                              "file instruksi cara kerja kita.",
                              "Ia menjalankan alat **vg** untuk membuat gambar, suara dan video.",
                              "Agent juga bisa salah. Karena itu **gerbang persetujuan** tetap di tangan kamu."],
     size=21, after=14)

s = new_slide(WHITE, "Enam prinsip ini dipakai di setiap tahap praktik nanti. Yang paling sering dilupakan pemula: nomor "
              "lima. Kalau kamu mengubah tiga hal sekaligus dan hasilnya membaik, kamu tidak tahu mana yang berhasil.")
header(s, "Cara berpikir saat bekerja dengan AI", "Bagian 1 · Dasar AI")
rules = [("Input menentukan hasil", "Brief, prompt dan gambar referensi yang jelas memberi hasil yang jelas."),
         ("Spesifik, bukan umum", "Sebut kamera, cahaya, lensa, durasi. Hindari kata ‘bagus’ dan ‘estetik’."),
         ("Selalu cek", "AI menebak. Periksa fakta, wajah, teks dan logo setiap kali."),
         ("Ulangi di tahap murah", "Perbaiki di gambar, bukan di video."),
         ("Satu perubahan sekali coba", "Supaya kamu tahu apa yang membuat hasil lebih baik."),
         ("Kamu yang memutuskan", "Selera, etika dan persetujuan tetap tugas manusia.")]
for i, (name, desc) in enumerate(rules):
    col, row = i % 3, i // 3
    x, y = M + col * 4.1, 1.95 + row * 2.5
    box(s, x, y, 3.9, 2.3)
    circle(s, x + 0.28, y + 0.28, 0.62, str(i + 1), size=22)
    text(s, x + 1.05, y + 0.25, 2.7, 0.75, name, size=21, bold=True, font=HEAD, color=INK, anchor=MSO_ANCHOR.MIDDLE,
         spacing=1.0)
    text(s, x + 0.3, y + 1.1, 3.35, 1.1, desc, size=19)

s = new_slide(WHITE, "Prompt yang baik menjawab pertanyaan yang biasanya dijawab juru kamera: untuk apa, apa yang terlihat, "
              "dari mana kita melihat, cahayanya dari mana, dan apa yang tidak boleh ada. Prompt ditulis dalam bahasa "
              "Inggris karena model paling paham bahasa itu; teks dan dialog di video tetap bahasa Indonesia.")
header(s, "Anatomi prompt yang baik", "Bagian 1 · Dasar AI")
table(s, M, 1.95, 8.6, [2.2, 6.4], [
    ["Bagian", "Isi (prompt asli, bahasa Inggris)"],
    ["Tujuan", "style frame, the house the reel sells"],
    ["Adegan", "one new two-storey modern townhouse, sunny afternoon"],
    ["Komposisi", "vertical 9:16, eye height 1.2 m, 24 mm, verticals straight"],
    ["Cahaya", "bright warm sun from camera left, clear blue sky"],
    ["Batasan", "no people, no text, no logos, not a render"],
], size=19, row_h=0.6)
box(s, M, 5.75, 8.6, 1.1, fill="FFF1EA", line="F6C9B5", radius=0.15)
text(s, M + 0.35, 5.75, 8.0, 1.1, "Prompt lemah: “rumah bagus, estetik, 4K”. Model harus menebak semuanya sendiri.",
     size=20, color=INK, anchor=MSO_ANCHOR.MIDDLE)
picture(s, "Look_Rumah_Depan.jpg", 9.75, 1.95, 2.75, 4.5, radius=0.06)
text(s, 9.75, 6.5, 2.95, 0.4, "Hasil prompt lengkap", size=16, color=MUTED)

s = new_slide(WHITE, "Setiap kelemahan AI di tabel ini kami alami sendiri saat membuat reel contoh. Kolom kanan adalah "
              "cara alur kerja kita menghindarinya. Kamu akan melihat semuanya lagi di bagian praktik.")
header(s, "Batas AI, dan cara kita mengakalinya", "Bagian 1 · Dasar AI")
table(s, M, 1.95, CW, [3.3, 3.7, 5.13], [
    ["Kelemahan", "Contoh", "Cara kita"],
    ["Wajah berubah antar shot", "presenter terlihat seperti orang lain", "lembar referensi karakter"],
    ["Teks dan logo kacau", "tulisan papan nama aneh", "teks ditambahkan di edit"],
    ["Bibir tidak sinkron", "suara ditempel, bibir tidak cocok", "narasi voice-over, mulut tertutup"],
    ["Mengarang detail", "jendela rumah berbeda", "foto asli klien untuk produk"],
    ["Gerakan panjang", "benda berubah bentuk", "klip pendek, satu gerakan kamera"],
], size=20, row_h=0.78)

s = new_slide(WHITE, "Etika bukan tambahan, tapi bagian dari pekerjaan. Presenter kita, Rani, dibuat AI dari nol, bukan dari "
              "foto orang asli. Untuk produk yang dijual, kita tidak boleh membuat penonton salah paham tentang apa yang "
              "mereka beli.")
header(s, "Jujur dan aman: aturan etika kita", "Bagian 1 · Dasar AI")
ethics = ["Beri label: ‘ILUSTRASI RENCANA’ untuk rencana, dan jelaskan bila gambar dibuat AI.",
          "Jangan palsukan produk: rumah yang dijual harus foto asli.",
          "Hak cipta: pakai foto hanya dengan izin pemiliknya.",
          "Wajah orang asli hanya dengan izin orangnya.",
          "Harga dan klaim selalu dicek, dengan catatan ‘S&K berlaku’."]
for i, item in enumerate(ethics):
    y = 1.95 + i * 0.97
    circle(s, M, y + 0.05, 0.6, str(i + 1), size=20)
    text(s, M + 0.85, y, 7.9, 0.75, item, size=21, color=INK, anchor=MSO_ANCHOR.MIDDLE)
picture(s, "Rani_Portrait_Ref.jpg", 9.75, 1.95, 2.95, 3.93, radius=0.06, focus_y=0.3)
text(s, 9.75, 5.98, 2.95, 0.8, "Rani: presenter yang dibuat AI dari nol, bukan orang asli.", size=16, color=MUTED)

s = new_slide(ORANGE, "Kalau hanya tiga kalimat yang kamu ingat dari bagian teori, ini dia. Setelah ini kita praktik.")
text(s, M, 0.9, CW, 0.4, "RANGKUMAN BAGIAN 1", size=20, bold=True, font=HEAD, color=INK)
for i, line in enumerate(("AI belajar pola dari contoh.",
                          "AI menebak yang paling masuk akal. Kamu yang mengecek.",
                          "Semakin jelas inputnya, semakin baik hasilnya.")):
    y = 1.8 + i * 1.65
    circle(s, M, y + 0.1, 1.0, str(i + 1), fill=INK, color=ORANGE, size=36)
    text(s, M + 1.35, y, 10.7, 1.2, line, size=36, bold=True, font=HEAD, color=INK, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)

# ============================================================ part 2: practice

s = new_slide(INK, "Sekarang praktik. Kita ikuti reel 'Tebak Harga' dari brief sampai video: tujuh tahap, tiga gerbang.")
circle(s, M, 1.4, 1.3, "2", size=48)
text(s, M, 3.0, 11.5, 0.4, "BAGIAN 2", size=20, bold=True, font=HEAD, color=ORANGE)
text(s, M, 3.5, 11.8, 2.0, "Praktik: dari brief ke reel", size=54, bold=True, font=HEAD, color=WHITE, spacing=0.95)
text(s, M, 4.75, 10.5, 1.0, "Contoh reel ‘Tebak Harga’: tujuh tahap, tiga gerbang.", size=24, color=BODY_DARK)

s = new_slide(ORANGE, "Kalimat ini yang paling penting di seluruh kelas. Memperbaiki gambar itu murah dan cepat. Memperbaiki "
              "video itu mahal dan lambat. Harga dari kie.ai: gambar gpt-image-2 10 kredit, klip Veo 3.1 Lite 8 detik "
              "1080p 35 kredit.")
text(s, M, 0.9, CW, 0.4, "ATURAN EMAS", size=20, bold=True, font=HEAD, color=INK)
text(s, M, 1.45, CW, 1.9, "Gambar itu murah. Video itu mahal.", size=60, bold=True, font=HEAD, color=INK, spacing=0.95)
for i, (num, label) in enumerate((("10 kredit", "per gambar"), ("35 kredit", "per klip video 8 detik"))):
    x = M + i * 5.2
    text(s, x, 3.5, 4.9, 1.0, num, size=60, bold=True, font=HEAD, color=INK)
    text(s, x, 4.5, 4.9, 0.5, label, size=24, color=INK)
text(s, M, 5.55, CW, 1.0, "Jadi seluruh reel disetujui sebagai gambar dulu. Baru setelah itu gambarnya dibuat bergerak.",
     size=26, color=INK)

s = new_slide(WHITE, "Kamu bicara ke agent dengan bahasa biasa, misalnya: buat reel dari brief ini. Agent menjalankan alat "
              "bernama vg. Alat itu yang menjaga uangmu: ia menolak membuat video sebelum kamu setuju.")
header(s, "Tiga pemain, satu tim", "Bagian 2 · Praktik")
players = [("Kamu", "Menulis brief, memilih hasil terbaik, dan menyetujui. Tidak perlu hafal perintah."),
           ("Agent AI", "WorkBuddy + Expert AI Videographer, otaknya glm-5.3-flash. Menulis rencana dan prompt, "
                        "menjalankan alat, lalu memeriksa."),
           ("Alat vg", "Memanggil model, mencatat biaya, dan menolak video yang belum kamu setujui.")]
for i, (name, desc) in enumerate(players):
    x = M + i * 4.1
    box(s, x, 1.95, 3.55, 4.6)
    circle(s, x + 0.35, 2.25, 0.75, str(i + 1))
    text(s, x + 0.35, 3.2, 2.9, 0.6, name, size=28, bold=True, font=HEAD, color=INK)
    text(s, x + 0.35, 3.9, 2.9, 2.5, desc, size=21)
    if i < 2:
        arrow(s, x + 3.6, 4.08, 0.45, 0.34)

s = new_slide(WHITE, "Otak Expert adalah model yang cepat dan murah. Supaya tidak tersesat, ia tidak menghafal "
              "urutan kerja: setiap kali ia menjalankan vg next, yang menulis satu langkah berikutnya. Di gerbang, vg next "
              "menyuruhnya berhenti dan bertanya ke kamu.")
header(s, "Satu langkah sekali: vg next", "Bagian 2 · Praktik")
box(s, M, 1.95, 6.9, 4.95, fill=INK, line=None, radius=0.06)
text(s, M + 0.35, 2.2, 6.2, 0.4, "CONTOH HASIL vg next", size=16, bold=True, font=HEAD, color=ORANGE)
text(s, M + 0.35, 2.75, 6.2, 4.0, ["STAGE  look review", "RUN    vg review -p Aster --detach",
                                   "ASK    Kirim link. Minta klik", "       Approve look, atau tulis",
                                   "       catatan lalu klik Done.",
                                   "THEN   setelah dia bilang sudah:", "       vg next lagi"],
     size=19, color=WHITE, font="Courier New", spacing=1.1)
text(s, 7.8, 2.0, 4.93, 4.9, ["**RUN**: jalankan perintah ini.", "**WRITE**: tulis file ini, baca skill-nya dulu.",
                              "**ASK**: berhenti, tanya manusia, tunggu jawabannya.", "**DONE**: reel selesai."],
     size=21, after=14)

s = new_slide(WHITE, "Tujuh tahap, selalu urut. Tiga di antaranya gerbang, tempat manusia wajib menyetujui: look, seluruh "
              "reel sebagai gambar, dan biaya video. Audio dibuat sebelum animatic, dan video baru di tahap enam.")
header(s, "Alur kerja: 7 tahap, 3 gerbang", "Bagian 2 · Praktik")
flow = [("Brief dan shot list", 0), ("Look", 1), ("Karakter dan frame", 0), ("Audio", 0), ("Animatic", 2),
        ("Video", 3), ("Edit final", 0)]
for i, (name, gate) in enumerate(flow):
    x = M + i * 1.75
    box(s, x, 1.95, 1.6, 3.4, fill=WHITE if gate else CARD, line=ORANGE if gate else LINE)
    text(s, x + 0.2, 2.15, 1.3, 0.9, str(i + 1), size=48, bold=True, font=HEAD, color=ORANGE_TXT if gate else INK)
    text(s, x + 0.2, 3.1, 1.25, 1.3, name, size=20, bold=True, color=INK, spacing=1.0)
    if gate:
        pill(s, x + 0.15, 4.65, 1.3, 0.45, "Gerbang %d" % gate, size=15)
text(s, M, 5.75, CW, 1.0, "Di setiap gerbang alat berhenti sampai **kamu** bilang setuju. Tanpa persetujuan, langkah "
     "berikutnya ditolak.", size=22, color=INK)

s = new_slide(INK, "Setiap gerbang adalah klik manusia di halaman review (VG_APPROVAL_MODE=page). Perintah approve "
              "dari agent selalu ditolak alat. Ini rem terhadap persetujuan tanpa sengaja. Batas keras tetap di kunci "
              "kie.ai dengan batas kredit.")
header(s, "Tiga gerbang yang menjaga uangmu", "Bagian 2 · Praktik", dark=True)
table(s, M, 1.95, CW, [2.1, 4.3, 2.7, 3.03], [
    ["Gerbang", "Yang kamu periksa", "Ditolak sebelum setuju", "Cara setuju"],
    ["1 · Look", "2–3 style frame: satu dunia, satu cahaya, satu grade", "storyboard dan frame", "klik Approve look"],
    ["2 · Visual", "seluruh reel sebagai gambar, dengan suara", "semua video", "klik Approve reel"],
    ["3 · Video", "biaya per klip, mulai dari 1 klip pilot", "pengiriman klip", "klik Approve per klip"],
], size=20, dark=True, row_h=0.85)
text(s, M, 5.65, CW, 1.2, "Di halaman review kamu ganti take, menulis catatan, dan klik Approve. Agent tidak bisa: "
     "perintah approve darinya selalu ditolak alat.", size=21, color=BODY_DARK)

s = new_slide(WHITE, "Panduan WorkBuddy memandu pemasangan dalam tiga langkah: AI di WorkBuddy yang memasang sisanya. "
              "Laptop Windows atau Mac sama-sama bisa. Angka biaya adalah hitungan nyata reel "
              "contoh ini.")
header(s, "Yang kamu butuhkan", "Bagian 2 · Praktik")
prep = [("Alat", ["Laptop Windows atau Mac", "WorkBuddy, dengan otak glm-5.3-flash di dalamnya",
                  "Setup memasang sisanya"]),
        ("Akun", ["kie.ai: gambar dan video (kredit)", "OpenRouter: suara dan musik"]),
        ("Biaya reel ini", ["Gambar: ±70 kredit", "Video: 7 klip × 35 = 245 kredit", "Suara dan musik: < US$0,50"])]
for i, (name, items) in enumerate(prep):
    x = M + i * 4.1
    box(s, x, 1.95, 3.9, 4.8)
    text(s, x + 0.35, 2.2, 3.2, 0.6, name, size=28, bold=True, font=HEAD, color=INK)
    text(s, x + 0.35, 3.0, 3.25, 3.6, items, size=21, bullets="dot", after=12)

s = new_slide(WHITE, "Brief klien diubah menjadi urutan beat, lalu satu shot per beat. Reel ini memakai format tebak-harga: "
              "janji di detik pertama, tiga petunjuk, penundaan, lalu jawaban. Agent menulisnya ke Shotlist.json dan "
              "mengeceknya dengan vg validate.")
header(s, "1 · Brief jadi shot list", "Bagian 2 · Praktik")
table(s, M, 1.95, 7.2, [1.5, 2.1, 3.6], [
    ["Detik", "Bagian", "Isi"],
    ["0–2", "Hook", "“Tebak harga rumah ini.”"],
    ["2–9", "Petunjuk 1–2", "lokasi, jarak ke tol"],
    ["9–14", "Petunjuk 3", "fitur rumah"],
    ["14–21", "Tunda", "bonus dan bukti"],
    ["21–24", "Jawaban", "harga, dengan flash"],
    ["24–28", "Ajakan", "DM untuk lihat langsung"],
], size=20, row_h=0.66)
for i, (lead, rest) in enumerate((("Satu ide per shot.", "Dua aksi membingungkan model dan penonton."),
                                  ("Hook di 2 detik pertama.", "Kata pertama sebelum detik 0,8."),
                                  ("Janji harus ditepati.", "“Tebak harga” harus dijawab."))):
    y = 1.95 + i * 1.6
    box(s, 8.15, y, 4.58, 1.42)
    text(s, 8.45, y, 4.05, 1.42, ["**%s**" % lead, rest], size=20, color=INK, anchor=MSO_ANCHOR.MIDDLE, after=4)

s = new_slide(WHITE, "Reel pertama kami gagal karena setiap shot punya cahaya dan warna sendiri. Sekarang look ditulis sekali: "
              "dunia, cahaya, grade, gaya grafis. Lalu dua sampai tiga style frame dibuat dan disetujui. Gambar rencana "
              "MRT selalu diberi label ilustrasi rencana.")
header(s, "2 · Look: satu dunia visual", "Bagian 2 · Praktik")
for i, name in enumerate(("Rani_Boulevard.jpg", "Area_Aerial.jpg", "Rencana_MRT.jpg")):
    phone(s, name, M + i * 2.75, 1.95, 4.6)
text(s, 9.1, 2.1, 3.65, 1.0, "Satu sore yang cerah", size=28, bold=True, font=HEAD, color=INK, spacing=1.0)
text(s, 9.1, 3.2, 3.65, 3.5, ["Matahari dari kiri, langit biru, satu grade warna.",
                              "Disetujui dulu di **Gerbang 1**, lalu jadi acuan semua gambar lain."], size=21, after=14)

s = new_slide(WHITE, "Untuk presenter, agent membuat potret referensi dan lembar putar dulu. Setiap panel storyboard memakai "
              "keduanya sebagai acuan, jadi wajahnya tetap sama. Untuk rumah yang dijual, di proyek nyata kita pakai foto "
              "asli klien dan hanya kameranya yang bergerak.")
header(s, "3 · Wajah yang sama di setiap shot", "Bagian 2 · Praktik")
figs = [("Rani_Portrait_Ref.jpg", 2.7, "Potret referensi"), ("Rani_Turnaround_Ref.jpg", 3.6, "Lembar putar"),
        ("Rani_Mobil.jpg", 2.03, "Panel storyboard")]
x = M + 0.35
for i, (name, w, label) in enumerate(figs):
    picture(s, name, x, 1.95, w, 3.6, radius=0.05, focus_y=0.35)
    text(s, x, 5.62, w, 0.4, label, size=18, bold=True, color=INK, align=PP_ALIGN.CENTER)
    x += w
    if i < 2:
        arrow(s, x + 0.35, 3.58, 0.5, 0.34)
        x += 1.2
box(s, M, 6.1, CW, 0.85, fill="FFF1EA", line="F6C9B5", radius=0.2)
text(s, M + 0.35, 6.1, CW - 0.7, 0.85, "**Rumah yang dijual = foto asli dari klien.** Di contoh ini rumahnya gambar AI "
     "karena proyeknya fiktif.", size=19, color=INK, anchor=MSO_ANCHOR.MIDDLE)

s = new_slide(INK, "Ini peta waktu reel contoh. Garis putih adalah potongan gambar, biru adalah frasa narasi, abu dan oranye "
              "adalah musik: tenang di bawah suara, lalu drop tepat saat harga disebut. vg audio curve mencari titik drop "
              "musik supaya bisa diselaraskan. Pilih suara narasi dengan telinga, bukan dengan skor.")
header(s, "4 · Audio dulu, gambar mengikuti suara", "Bagian 2 · Praktik", dark=True)
TX, TW, SEC = M + 1.9, CW - 1.9, 28.0


def tx(t):
    return TX + t * TW / SEC


phrases = [(0.36, 1.52), (2.27, 2.91), (3.69, 5.78), (6.49, 8.38), (9.20, 13.45), (14.36, 14.97), (15.66, 17.91),
           (18.63, 19.98), (20.59, 21.32), (21.82, 23.30), (24.02, 24.66), (25.12, 26.34)]
cuts = [2.1, 3.55, 6.3, 9.05, 14.2, 15.5, 18.45, 20.45, 21.75, 23.9, 25.0]
for i, label in enumerate(("Potongan", "Narasi", "Musik", "Efek")):
    y = 2.0 + i * 0.82
    text(s, M, y, 1.8, 0.6, label, size=20, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    box(s, TX, y, TW, 0.6, fill=CARD_DARK, line=None, radius=0.15)
for c in cuts:
    box(s, tx(c) - 0.02, 2.06, 0.04, 0.48, fill=WHITE, line=None, shape=MSO_SHAPE.RECTANGLE)
for a, b in phrases:
    box(s, tx(a), 2.94, max(0.05, tx(b) - tx(a)), 0.36, fill="8FB8FF", line=None, radius=0.2)
box(s, tx(3.27), 3.92, tx(21.3) - tx(3.27), 0.16, fill="7A7F88", line=None, radius=0.5)
box(s, tx(21.82), 3.78, tx(27.8) - tx(21.82), 0.44, fill=ORANGE, line=None, radius=0.2)
for t, col in ((3.27, BODY_DARK), (6.02, BODY_DARK), (15.22, BODY_DARK), (21.82, ORANGE)):
    box(s, tx(t) - 0.07, 4.66, 0.14, 0.48, fill=col, line=None, radius=0.5)
text(s, TX, 5.3, 1.0, 0.35, "0 s", size=16, color=BODY_DARK)
text(s, W - M - 1.0, 5.3, 1.0, 0.35, "28 s", size=16, color=BODY_DARK, align=PP_ALIGN.RIGHT)
text(s, tx(21.82) - 3.2, 5.3, 3.9, 0.35, "21,8 s: flash, ding, drop", size=16, bold=True, color=ORANGE,
     align=PP_ALIGN.RIGHT)
text(s, M, 5.95, CW, 0.95, "Setiap gambar berganti tepat sebelum frasa baru. Perintah: **vg audio voice**, **music**, "
     "**sfx**, **curve**.", size=21, color=BODY_DARK)

s = new_slide(WHITE, "Animatic adalah reel lengkap dari gambar diam, dengan caption, grafis, transisi, narasi, musik dan efek. "
              "Gratis, dibuat lokal. Kamu menilai reel sebagai penonton. Setiap perbaikan berarti render animatic baru.")
header(s, "5 · Animatic: seluruh reel sebagai gambar", "Bagian 2 · Praktik")
for i, name in enumerate(("Frame_hook.jpg", "Frame_rumah.jpg", "Frame_petunjuk1.jpg", "Frame_peta.jpg",
                          "Frame_petunjuk3.jpg", "Frame_harga.jpg")):
    phone(s, name, M + i * 2.04, 1.95, 3.35)
text(s, M, 5.55, CW, 1.3, "Tonton seluruh reel sebelum ada video: satu dunia? janjinya ditepati? rumahnya cukup lama "
     "terlihat? Lalu **Gerbang 2**.", size=22, color=INK)

s = new_slide(WHITE, "Transisi bukan hiasan. Potong keras hampir di semua tempat. Whip hanya saat lokasi berganti. Flash hanya "
              "sekali, di momen paling penting. Kalau semua shot memakai efek, tidak ada yang terasa istimewa.")
header(s, "Transisi yang punya alasan", "Bagian 2 · Praktik")
for i, (name, desc) in enumerate((("Potong keras", "Pilihan utama. Potong tepat sebelum frasa baru dimulai."),
                                  ("Whip + whoosh", "Untuk pindah tempat: kabur gerak di kedua sisi potongan."),
                                  ("Flash + ding", "Hanya sekali: jawaban harga, bersama drop musik."))):
    x = M + i * 4.1
    box(s, x, 1.95, 3.9, 4.3)
    circle(s, x + 0.35, 2.25, 0.75, str(i + 1))
    text(s, x + 0.35, 3.2, 3.2, 0.6, name, size=28, bold=True, font=HEAD, color=INK)
    text(s, x + 0.35, 3.95, 3.25, 2.2, desc, size=21)

s = new_slide(WHITE, "Prompt video hanya menjelaskan gerakan: satu gerakan kamera, cahaya, suara sekitar, dan apa yang tidak "
              "boleh berubah. Orang di klip tidak bicara; suaranya dari narasi. Setiap persetujuan membayar tepat satu "
              "take, jadi mulai dari satu klip pilot.")
header(s, "6 · Baru sekarang gambarnya bergerak", "Bagian 2 · Praktik")
box(s, M, 1.95, 6.9, 4.95, fill=INK, line=None, radius=0.06)
text(s, M + 0.35, 2.2, 6.2, 0.4, "CONTOH PROMPT VIDEO", size=16, bold=True, font=HEAD, color=ORANGE)
text(s, M + 0.35, 2.75, 6.2, 4.0, "Slow push-in of about half a metre over 6 seconds toward the front door, eye height "
     "1.5 m, verticals straight; eases out and holds. Bright afternoon sun from the left. AUDIO: quiet street, birds. "
     "Nobody speaks. LOCKS: the house stays exactly as in the first frame.", size=19, color=WHITE, font="Courier New",
     spacing=1.1)
table(s, 7.8, 1.95, 4.93, [3.1, 1.83], [
    ["Biaya video reel ini", "Kredit"], ["1 klip pilot", "35"], ["6 klip berikutnya", "210"], ["**Total**", "**245**"],
], size=20, row_h=0.62)
box(s, 7.8, 4.75, 4.93, 2.15, fill="FFF1EA", line="F6C9B5", radius=0.1)
text(s, 8.1, 4.75, 4.35, 2.15, "**Gerbang 3:** klik Approve di bagian Video, biayanya terlihat. Mulai dari satu klip pilot.",
     size=21, color=INK, anchor=MSO_ANCHOR.MIDDLE)

s = new_slide(WHITE, "vg edit final menyatukan klip, narasi, musik, efek, caption dan grafis, lalu menyimpan hasilnya di "
              "99_Output. Sebelum dikirim, cek daftar ini. Poin kedua lahir dari bug nyata: animatic kami pernah membeku "
              "dua setengah detik tanpa ketahuan.")
header(s, "7 · Edit final, lalu cek sebelum kirim", "Bagian 2 · Praktik")
checks = ["Caption tidak pernah mendahului kata yang diucapkan", "Tidak ada gambar beku: jumlah frame = durasi × 30",
          "Suara jelas di atas musik, sekitar −14 LUFS", "Ada label ‘ILUSTRASI RENCANA’ dan ‘S&K berlaku’",
          "Teks tidak menutupi wajah", "File berversi, misalnya Proyek_v1.0.mp4"]
for i, item in enumerate(checks):
    col, row = i % 2, i // 2
    x, y = M + col * 6.15, 2.0 + row * 1.55
    circle(s, x, y + 0.08, 0.6, "✓", size=22)
    text(s, x + 0.85, y, 5.1, 0.8, item, size=22, color=INK, anchor=MSO_ANCHOR.MIDDLE)

s = new_slide(INK, "Setiap aturan di kelas ini lahir dari kesalahan nyata saat membuat reel ini. Versi pertama kami dinilai "
              "jelek: cahayanya beda-beda, janjinya tidak ditepati, dan suaranya terdengar ditempel.")
header(s, "Kesalahan kami, dan aturannya", "Bagian 2 · Praktik", dark=True)
table(s, M, 1.95, CW, [4.4, 3.1, 4.63], [
    ["Yang terjadi", "Kenapa", "Aturannya sekarang"],
    ["Tiap shot beda cahaya dan warna", "dicek satu per satu", "look disetujui dulu, reel direview utuh"],
    ["Hook berjanji, akhir tidak menepati", "tidak ada yang mengecek", "shot list mencatat janji dan penepatnya"],
    ["Suara TTS ditempel di atas bibir AI", "dubbing", "narasi voice-over, mulut tertutup"],
    ["Harga muncul sebelum diucapkan", "caption digabung 3 kata", "caption berhenti di tanda jeda"],
    ["Animatic membeku 2,5 detik", "bug saat render", "setiap render dicek jumlah frame-nya"],
], size=19, dark=True, row_h=0.76)

s = new_slide(WHITE, "Semua bahan ada di repo github.com/tansilandre/ai-videographer-kelas: Panduan WorkBuddy, pelajaran, "
              "studi kasus Tebak Harga, dan brief latihan. Kunci API selalu ditempel di halaman setup, tidak pernah di chat.")
header(s, "Latihan pertamamu", "Bagian 2 · Praktik")
text(s, M, 2.0, CW, 4.8, ["Daftar **WorkBuddy** lewat link undangan, pasang, pilih model **glm-5.3-flash**.",
                          "Kirim satu pesan dari **Panduan WorkBuddy**: AI-nya memasang semuanya.",
                          "Tempel kunci kie.ai di **halaman setup**, klik Simpan.",
                          "Pilih Expert **AI Videographer**, klik “Buat video baru”, jawab lima pertanyaannya.",
                          "Klik di tiga gerbang: look, reel, satu klip pilot."], size=24, bullets="num", after=16, color=INK)

s = new_slide(INK, "Kalau hanya satu hal yang diingat: setujui gambarnya dulu, buat suaranya dulu, dan buat gambarnya "
              "bergerak paling akhir. Terima kasih.")
text(s, M, 1.5, CW, 0.4, "SATU HAL UNTUK DIINGAT", size=20, bold=True, font=HEAD, color=ORANGE)
text(s, M, 2.1, CW, 2.8, "Gambar dulu. Suara dulu. Gerak terakhir.", size=60, bold=True, font=HEAD, color=WHITE,
     spacing=0.95)
text(s, M, 5.2, CW, 1.0, "Pertanyaan? Semua bahan kelas: github.com/tansilandre/ai-videographer-kelas", size=24,
     color=BODY_DARK)

OUT.parent.mkdir(exist_ok=True)
if OUT.exists() and not DRAFT:
    raise SystemExit("%s already exists; never overwrite a delivered version, pass a new version" % OUT)
prs.save(str(OUT))
print("wrote %s (%d slides)" % (OUT, len(prs.slides)))
