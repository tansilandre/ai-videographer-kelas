"""Builds the attendee handbook: 6_Kelas/5_WorkBuddy/Pegangan_AI_Videographer_v<X.Y>.html.

One self-contained page in Bahasa Indonesia (pictures embedded, no files beside it), in the deck's palette.
It replaces the two separate handouts (Pegangan Workshop and Pegangan AI Video Agent). Pictures come from
the anonymised class example in 6_Kelas/2_Studi_Kasus/Tebak_Harga/1_Gambar.
Run: python3 Build_Pegangan.py 1.0
"""
import base64
import html
import io
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
KELAS = HERE.parents[1]
PICS = KELAS / "2_Studi_Kasus" / "Tebak_Harga" / "1_Gambar"
AVATAR = KELAS.parent / "2_Tools" / "workbuddy" / "expert" / "ai-videographer" / "avatars" / "expert.png"
VERSION = sys.argv[1] if len(sys.argv) > 1 else "1.0"
OUT = HERE.parent / ("Pegangan_AI_Videographer_v%s.html" % VERSION)

INVITE = "https://workbuddy.ai/invite?code=ULLL7X4E"
REPO = "https://github.com/tansilandre/ai-videographer-kelas"
MSG_WIN = ("Pasang AI Videographer: unduh https://github.com/tansilandre/ai-videographer-kelas ke folder ini (pakai "
           "git clone kalau git ada; kalau tidak, unduh https://github.com/tansilandre/ai-videographer-kelas/archive/"
           "refs/heads/main.zip lalu ekstrak ke subfolder ai-videographer-kelas), lalu jalankan powershell "
           "-ExecutionPolicy Bypass -File setup.ps1 di folder itu dan ikuti yang dicetaknya.")
MSG_MAC = ("Pasang AI Videographer: clone https://github.com/tansilandre/ai-videographer-kelas.git ke folder ini "
           "(atau ke subfolder ai-videographer-kelas kalau folder ini tidak kosong), lalu jalankan bash setup.sh di "
           "folder itu dan ikuti yang dicetaknya.")


def img(path, width=420, quality=78):
    """The picture as a small JPEG data URI."""
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def e(text):
    return html.escape(text, quote=True)


P = {name: img(PICS / (name + ".jpg")) for name in
     ("Frame_Hook", "Frame_Petunjuk_1", "Frame_Harga", "Frame_Akhir", "Rani_Mobil", "Look_Rumah_Depan", "Frame_Peta")}
P["Rani_Portrait_Ref"] = img(PICS / "Rani_Portrait_Ref.jpg", width=360)
P["avatar"] = img(AVATAR, width=128, quality=85)

CSS = r"""
/* A field manual for one class day: sticky part tabs, one reading column, mock screens beside the steps. */
:root{
  color-scheme:light;
  --paper:#FFFFFF; --card:#F7F6F3; --card-2:#EFECE6; --line:#E3E0DA;
  --ink:#16181D; --body:#3D424B; --muted:#6B7079; --on-ink:#FFFFFF; --on-ink-2:#D3CEC5;
  --accent:#FF5A1F; --accent-text:#C2410C; --accent-soft:#FFEDE4;
  --display:Arial,"Helvetica Neue",Helvetica,sans-serif;
  --text:Calibri,Carlito,"Segoe UI",Arial,sans-serif;
  --code:Consolas,"SF Mono",Menlo,"Courier New",monospace;
  --radius:14px;
}
*{box-sizing:border-box}
html{scroll-padding-top:calc(64px + env(safe-area-inset-top,0px));scroll-behavior:smooth}
body{background:var(--paper);color:var(--body);font-family:var(--text);font-size:18px;line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding-inline:20px;padding-block:20px 72px}
h1,h2,h3{font-family:var(--display);color:var(--ink);margin:0;text-wrap:balance}
h2{font-size:clamp(1.6rem,3.6vw,2.3rem);line-height:1.1;letter-spacing:-.01em;margin:6px 0 12px}
h3{font-size:1.15rem;line-height:1.25}
p{margin:0}
a{color:var(--accent-text)}
b,strong{color:var(--ink)}
code{font-family:var(--code);font-size:.88em;background:var(--card-2);padding:1px 6px;border-radius:5px;overflow-wrap:anywhere}
img{max-width:100%;display:block}
:focus-visible{outline:3px solid var(--accent);outline-offset:3px;border-radius:6px}
.eyebrow{font-family:var(--display);font-weight:700;font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent-text)}
.lead{font-size:1.1rem;max-width:62ch}
.note{font-size:.92rem;color:var(--muted)}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius)}
.grid{display:grid;gap:14px}
.g2{grid-template-columns:repeat(2,minmax(0,1fr))}
.g3{grid-template-columns:repeat(3,minmax(0,1fr))}
.g4{grid-template-columns:repeat(4,minmax(0,1fr))}
section{padding-block:44px 8px}
.part{margin-top:36px;padding:14px 18px;border-radius:var(--radius);background:var(--ink);color:var(--on-ink);display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
.part b{color:var(--accent);font-family:var(--display);font-size:13px;letter-spacing:.08em}
.part span{font-family:var(--display);font-weight:700;font-size:1.3rem}

/* part tabs */
.tabs{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--paper);border-bottom:1px solid var(--line);margin-inline:-20px;padding:10px 20px;display:flex;gap:6px;overflow-x:auto}
.tabs a{flex:none;font-family:var(--display);font-size:13px;font-weight:700;text-decoration:none;color:var(--ink);padding:7px 12px;border-radius:999px;border:1px solid var(--line);background:var(--paper)}
.tabs a:hover{border-color:var(--accent)}

/* cover */
.cover{background:var(--ink);color:var(--on-ink);border-radius:18px;padding:clamp(22px,4.5vw,44px);display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,.6fr);gap:28px;align-items:center}
.cover .eyebrow{color:var(--accent)}
.cover h1{color:var(--on-ink);font-size:clamp(2.3rem,6vw,3.8rem);line-height:1.02;letter-spacing:-.015em;margin:10px 0 14px}
.cover .lead{color:var(--on-ink-2)}
.cover .lead b{color:var(--accent)}
.req{display:inline-block;margin-top:16px;font-family:var(--code);font-size:13px;padding:6px 12px;border-radius:999px;background:#24272F;color:var(--on-ink)}
.phone{width:min(100%,210px);justify-self:center;aspect-ratio:9/16;border-radius:26px;border:8px solid #000;overflow:hidden;background:#000}
.phone img{width:100%;height:100%;object-fit:cover}
.path{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:22px}
.path a{text-decoration:none;color:inherit;padding:18px;border-top:5px solid var(--accent);display:flex;flex-direction:column;gap:6px}
.path a:hover{box-shadow:0 8px 22px rgba(22,24,29,.08)}
.path .tag{font-family:var(--display);font-size:12px;font-weight:700;letter-spacing:.08em;color:var(--accent-text)}
.path p{font-size:.95rem;color:var(--muted)}
.who2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:14px}
.who2 .card{padding:12px 16px;display:flex;gap:12px;align-items:center;font-size:.95rem}
.badge{font-family:var(--display);font-size:12px;font-weight:700;letter-spacing:.06em;padding:4px 9px;border-radius:6px;white-space:nowrap}
.badge.you{background:var(--accent);color:var(--ink)}
.badge.ai{background:var(--ink);color:var(--on-ink)}

/* levels, roles, providers */
.lvl{padding:18px;display:flex;flex-direction:column;gap:8px}
.lvl.here{background:var(--paper);border:2px solid var(--accent)}
.lvl .n{font-family:var(--display);font-weight:700;font-size:12px;letter-spacing:.08em;color:var(--accent-text)}
.lvl p{font-size:.96rem}
.lvl .ex{color:var(--muted);font-size:.9rem}
.role{padding:16px;display:flex;flex-direction:column;gap:6px}
.role .n{font-family:var(--display);font-weight:700;font-size:12px;letter-spacing:.08em;color:var(--accent-text)}
.role p{font-size:.94rem;color:var(--muted)}
.motto{margin-top:14px;font-family:var(--display);font-weight:700;color:var(--ink)}
.prov{padding:20px;display:flex;flex-direction:column;gap:10px;background:var(--paper);border:2px solid var(--accent)}
.prov h3{font-size:1.5rem}
.prov .what{font-family:var(--display);font-weight:700;color:var(--accent-text);font-size:.95rem}
.prov ul{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:4px;font-size:.96rem}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font-size:.85rem;font-weight:700;padding:4px 10px;border-radius:999px;background:var(--accent-soft);color:var(--accent-text);white-space:nowrap}
.callout{margin-top:14px;padding:14px 18px;border-radius:var(--radius);background:var(--card);border:1px solid var(--line);font-size:.97rem}
.callout.hot{background:var(--accent-soft);border-color:var(--accent)}

/* the route: seven stages, three gates */
.route{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:8px;margin-top:18px}
.stage{padding:12px;display:flex;flex-direction:column;gap:6px;min-width:0}
.stage .n{font-family:var(--display);font-weight:700;font-size:1.6rem;color:var(--ink)}
.stage b{font-size:.95rem;line-height:1.2}
.stage.gate{background:var(--paper);border:2px solid var(--accent)}
.stage.gate .n{color:var(--accent-text)}
.gtag{align-self:flex-start;font-family:var(--display);font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;background:var(--accent);color:var(--ink)}
.strip{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:16px;max-width:560px}
.strip img{aspect-ratio:9/16;object-fit:cover;border-radius:8px;width:100%}

/* tables */
.tw{overflow-x:auto;margin-top:14px}
table{width:100%;border-collapse:collapse;font-size:.95rem;min-width:520px}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-family:var(--display);font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
td b{white-space:nowrap}
.num{font-variant-numeric:tabular-nums;white-space:nowrap}

/* checklists (ticks are remembered on this device only) */
.check{list-style:none;margin:14px 0 0;padding:0;display:grid;gap:8px}
.check label{display:flex;gap:10px;align-items:flex-start;cursor:pointer;padding:10px 14px;border-radius:10px;background:var(--card);border:1px solid var(--line)}
.check input{width:20px;height:20px;accent-color:var(--accent);margin-top:2px;flex:none}
.check input:checked+span{color:var(--muted);text-decoration:line-through}

/* accounts */
.acc{padding:18px;display:flex;flex-direction:column;gap:8px}
.acc .for{font-family:var(--display);font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--accent-text)}
.acc ol{margin:0;padding-left:18px;font-size:.95rem;display:flex;flex-direction:column;gap:4px}
.invite{display:flex;flex-direction:column;gap:2px;margin-top:auto;padding:12px 14px;border-radius:12px;background:var(--accent);color:var(--ink);text-decoration:none}
.invite b{font-family:var(--display)}
.invite span{font-family:var(--code);font-size:12px;overflow-wrap:anywhere}
.url{font-family:var(--code);font-size:13px;margin-top:auto;color:var(--ink)}

/* steps */
.steps{list-style:none;margin:18px 0 0;padding:0;display:flex;flex-direction:column;gap:14px}
.step{padding:20px;display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:22px;align-items:start}
.step.solo{grid-template-columns:minmax(0,1fr)}
.step.gatestep{background:var(--paper);border:2px solid var(--accent)}
.head{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.circle{width:40px;height:40px;border-radius:50%;background:var(--accent);color:var(--ink);font-family:var(--display);font-weight:700;display:grid;place-items:center;flex:none}
.step ul,.step ol{margin:12px 0 0;padding-left:20px;display:flex;flex-direction:column;gap:6px;font-size:.98rem}
.hint{margin-top:10px;font-size:.92rem;color:var(--muted)}
.prompt{margin-top:12px;border:2px solid var(--ink);border-radius:12px;padding:12px 14px;background:var(--paper)}
.prompt .top{display:flex;justify-content:space-between;align-items:center;gap:8px;font-family:var(--display);font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.prompt p{font-family:var(--code);font-size:13px;line-height:1.55;margin-top:8px;color:var(--ink);overflow-wrap:anywhere}
.copy{font:inherit;font-family:var(--display);font-size:12px;font-weight:700;border:1px solid var(--ink);background:var(--ink);color:var(--on-ink);border-radius:8px;padding:5px 10px;cursor:pointer;text-transform:none;letter-spacing:0}
details{margin-top:10px}
details summary{cursor:pointer;font-weight:700;color:var(--ink)}
.done{margin-top:16px;padding:16px 18px;border-radius:var(--radius);background:var(--ink);color:var(--on-ink)}
.done b{color:var(--accent);font-family:var(--display)}

/* mock screens */
.mock{border:1px solid var(--line);border-radius:12px;background:var(--paper);overflow:hidden;box-shadow:0 8px 22px rgba(22,24,29,.07)}
.bar{display:flex;gap:6px;align-items:center;padding:8px 12px;border-bottom:1px solid var(--line);background:var(--card);font-family:var(--code);font-size:11.5px;color:var(--muted);overflow-wrap:anywhere}
.bar i{width:9px;height:9px;border-radius:50%;background:var(--line);flex:none}
.mb{padding:14px;display:flex;flex-direction:column;gap:8px;font-size:.9rem}
.mb .box{border:1px solid var(--line);border-radius:7px;padding:6px 10px;font-family:var(--code);font-size:12px;color:var(--muted)}
.mb .btn{align-self:flex-start;font-family:var(--display);font-weight:700;font-size:.85rem;padding:7px 14px;border-radius:8px;background:var(--ink);color:var(--on-ink)}
.mb .btn.or{background:var(--accent);color:var(--ink)}
.smart{background:#1F5FAD;color:#FFFFFF;padding:14px;display:flex;flex-direction:column;gap:6px;font-size:.88rem}
.smart b{color:#FFFFFF;font-size:1.05rem}
.smart .r{display:flex;justify-content:flex-end;gap:8px;margin-top:6px}
.smart .r span{border:1px solid #FFFFFF;padding:4px 10px;font-weight:700;font-size:.8rem}
.smart .r .hl{outline:3px solid var(--accent);outline-offset:2px}
.term{background:var(--ink);color:var(--on-ink);border-radius:12px;padding:12px 14px;font-family:var(--code);font-size:12px;line-height:1.7;overflow-x:auto}
.term .ok{color:var(--accent)}
.term div{white-space:pre}
.excard{display:flex;gap:12px;align-items:center;border:2px solid var(--accent);border-radius:12px;padding:10px}
.excard img{width:48px;height:48px;border-radius:12px}
.frames{display:flex;gap:6px;flex-wrap:wrap}
.frames img{height:120px;width:auto;aspect-ratio:9/16;object-fit:cover;border-radius:8px}

/* glossary */
dl{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0 20px;margin:14px 0 0}
dl div{padding:12px 0;border-bottom:1px solid var(--line)}
dt{font-family:var(--display);font-weight:700;color:var(--ink)}
dd{margin:3px 0 0;color:var(--muted);font-size:.93rem;line-height:1.4}
footer{margin-top:48px;padding-top:18px;border-top:1px solid var(--line);font-size:.9rem;color:var(--muted);display:flex;flex-direction:column;gap:6px}

@media (max-width:900px){
  .route{grid-template-columns:repeat(4,minmax(0,1fr))}
  .g4{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media (max-width:760px){
  body{font-size:17px}
  .cover{grid-template-columns:minmax(0,1fr)}
  .g2,.g3,.path,.who2,.step{grid-template-columns:minmax(0,1fr)}
  .route{grid-template-columns:repeat(2,minmax(0,1fr))}
  dl{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media (max-width:460px){
  .g4,dl{grid-template-columns:minmax(0,1fr)}
  .phone{width:min(100%,180px)}
}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important;animation:none!important}}
"""

JS = r"""
<script>
(function () {
  document.querySelectorAll("button.copy").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var text = document.getElementById(btn.dataset.from).textContent.trim();
      function selectIt() {
        var r = document.createRange(); r.selectNodeContents(document.getElementById(btn.dataset.from));
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        btn.textContent = "Terpilih: tekan Ctrl/Cmd + C";
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { btn.textContent = "Tersalin"; }, selectIt);
      } else { selectIt(); }
      setTimeout(function () { btn.textContent = "Salin"; }, 2500);
    });
  });
  var KEY = "pegangan-ai-videographer-v1";
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (err) { saved = {}; }
  document.querySelectorAll(".check input[type=checkbox]").forEach(function (box) {
    if (saved[box.id]) box.checked = true;
    box.addEventListener("change", function () {
      saved[box.id] = box.checked;
      try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (err) {}
    });
  });
})();
</script>
"""


def checklist(prefix, items):
    rows = "".join('<li><label><input type="checkbox" id="%s-%d"><span>%s</span></label></li>' % (prefix, i, item)
                   for i, item in enumerate(items))
    return '<ul class="check">%s</ul>' % rows


def page():
    return """<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Pegangan AI Videographer</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Carlito:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>%(css)s</style>
<div class="wrap">

<header class="cover">
  <div>
    <p class="eyebrow">Pegangan kelas · untuk pemula</p>
    <h1>AI Videographer</h1>
    <p class="lead">Dari brief ke reel properti 9:16, dengan AI. <b>AI yang mengerjakan, kamu yang memutuskan.</b> Semua yang kamu butuhkan untuk workshop ada di halaman ini: cara kerjanya, PR sebelum workshop, cara memasang, dan cara membuat reel pertama.</p>
    <span class="req">Windows 10/11 atau Mac · internet</span>
  </div>
  <div class="phone"><img src="%(Frame_Hook)s" alt="Frame pertama reel contoh: presenter di mobil, tulisan TEBAK HARGANYA?"></div>
</header>

<nav class="tabs" aria-label="Bagian">
  <a href="#paham">1 · Paham dulu</a><a href="#pr">2 · PR</a><a href="#sesi1">3 · Sesi 1: Pasang</a><a href="#sesi2">4 · Sesi 2: Reel pertama</a><a href="#bicara">Cara bicara ke AI</a><a href="#macet">Kalau macet</a><a href="#kamus">Kamus</a>
</nav>

<div class="path">
  <a class="card" href="#paham"><span class="tag">BAGIAN 1 · BACA DULU</span><h3>Paham dulu</h3><p>Tiga level AI, siapa mengerjakan apa, dan dari mana gambar dan videonya. Sekitar 10 menit.</p></a>
  <a class="card" href="#sesi1"><span class="tag">SESI 1</span><h3>Pasang</h3><p>WorkBuddy, lalu satu pesan: AI memasang AI Videographer untukmu.</p></a>
  <a class="card" href="#sesi2"><span class="tag">SESI 2</span><h3>Buat reel pertama</h3><p>Jawab lima pertanyaan, lalu setujui tiga gerbang dengan klik.</p></a>
</div>
<div class="who2">
  <div class="card"><span class="badge you">KAMU</span><span>Mendaftar, menempel kunci, klik Approve, dan membuka ulang aplikasi.</span></div>
  <div class="card"><span class="badge ai">AI</span><span>Sisanya. Kamu cukup mengizinkan dan memutuskan.</span></div>
</div>

<!-- ============ 1 · PAHAM ============ -->
<div class="part" id="paham"><b>BAGIAN 1</b><span>Paham dulu</span></div>

<section id="level">
  <p class="eyebrow">Gambaran besar</p>
  <h2>Tiga level AI. Kelas ini di Level 2.</h2>
  <p class="lead">Makin tinggi levelnya, makin sedikit kamu mengetik, dan makin penting keputusanmu.</p>
  <div class="grid g3" style="margin-top:18px">
    <article class="card lvl"><span class="n">LEVEL 1</span><h3>Konsultan</h3><p><b>AI:</b> menjawab pertanyaan. <b>Kamu:</b> mengerjakan sendiri.</p><p class="ex">Chatbot menulis naskah, lalu kamu membuat videonya sendiri di aplikasi lain.</p></article>
    <article class="card lvl here"><span class="n">LEVEL 2 · KELAS INI</span><h3>AI Agent</h3><p><b>AI:</b> mengerjakan langkah demi langkah dengan alat. <b>Kamu:</b> memberi brief, memeriksa, dan menyetujui.</p><p class="ex">Expert AI Videographer menulis rencana, membuat gambar dan video, lalu berhenti di tiga gerbang.</p></article>
    <article class="card lvl"><span class="n">LEVEL 3</span><h3>Orkestrator</h3><p><b>AI:</b> membagi kerja ke beberapa agent sekaligus, lalu memeriksa hasilnya. <b>Kamu:</b> menetapkan tujuan, standar, dan anggaran.</p><p class="ex">Satu agent menulis naskah, satu membuat gambar, satu memeriksa kualitas, bersamaan.</p></article>
  </div>
  <p class="callout">Di level mana pun, keputusan tetap di tangan manusia. Makin banyak yang dikerjakan AI, makin penting tiga klik persetujuanmu.</p>
</section>

<section id="siapa">
  <p class="eyebrow">Siapa mengerjakan apa</p>
  <h2>Empat pemain, seperti kru film kecil</h2>
  <div class="grid g4" style="margin-top:18px">
    <article class="card role"><span class="n">KLIEN</span><h3>Kamu</h3><p>Membawa ide, melihat gambar, dan klik Approve di tiga gerbang. Tanpa klikmu, tidak ada video yang dibayar.</p></article>
    <article class="card role"><span class="n">SUTRADARA</span><h3>Otak AI</h3><p>Model glm-5.3-flash di WorkBuddy. Merencanakan, menulis prompt, menjalankan alat, dan memeriksa setiap gambar.</p></article>
    <article class="card role"><span class="n">PRODUSER</span><h3>Alat vg</h3><p>Mengirim setiap pesanan, menghitung kredit, menyimpan catatan, dan menolak video yang belum kamu setujui.</p></article>
    <article class="card role"><span class="n">KRU KAMERA</span><h3>Model pembuat</h3><p>Model AI di kie.ai dan OpenRouter yang membuat gambar, klip video, suara, dan musik.</p></article>
  </div>
  <p class="motto">Otak berpikir. Pembuat membuat. Alat menjaga uang. Kamu memutuskan.</p>
</section>

<section id="model">
  <p class="eyebrow">Tempat model tinggal</p>
  <h2>kie.ai dan OpenRouter: satu akun, banyak model</h2>
  <p class="lead">Model gambar, video, dan suara tidak berjalan di laptopmu. Mereka berjalan di server pembuatnya: Google, OpenAI, Kuaishou, dan lainnya. Alat vg memanggil mereka lewat dua perantara. Seperti aplikasi pesan-antar makanan: satu aplikasi, satu dompet, banyak restoran.</p>
  <div class="grid g2" style="margin-top:18px">
    <article class="card prov"><h3>kie.ai</h3><span class="what">Gambar, video, dan musik · 100+ model</span>
      <ul><li>Kita pakai gpt-image-2 (gambar), Veo 3.1 Lite dan Kling (video).</li><li>Bayar dengan kredit yang kamu isi dulu. Kreditnya tidak hangus.</li><li>Kuncinya: <code>KIE_API_KEY</code></li></ul>
      <div class="chips"><span class="chip">1 kredit ≈ Rp80</span><span class="chip">gambar 10 kredit ≈ Rp800</span><span class="chip">klip 8 detik 35 kredit ≈ Rp2.900</span></div></article>
    <article class="card prov"><h3>OpenRouter</h3><span class="what">Teks dan suara · 400+ model</span>
      <ul><li>Kita pakai Gemini TTS (narasi) dan Lyria (musik).</li><li>Bayar dalam dolar, dipotong setiap kali dipakai.</li><li>Kuncinya: <code>OPENROUTER_API_KEY</code></li></ul>
      <div class="chips"><span class="chip">satu take narasi 20 detik ≈ Rp50</span><span class="chip">suara satu reel &lt; US$0,50</span></div></article>
  </div>
  <p class="callout hot"><b>Satu gambar ≈ Rp800. Satu klip video ≈ Rp2.900.</b> Karena itu seluruh reel disetujui sebagai gambar dulu, baru dibuat bergerak. Otak agent (glm-5.3-flash) dibayar dengan kredit WorkBuddy, bukan lewat keduanya. Rupiah dihitung dengan kurs sekitar Rp16.000 per dolar.</p>
</section>

<section id="aturan">
  <p class="eyebrow">Aturan emas</p>
  <h2>Gambar dulu. Suara dulu. Gerak terakhir.</h2>
  <p class="lead">Tujuh tahap, selalu berurutan. Di tiga gerbang, alat berhenti sampai kamu klik setuju.</p>
  <div class="route">
    <div class="card stage"><span class="n">1</span><b>Brief dan rencana</b></div>
    <div class="card stage gate"><span class="n">2</span><b>Look</b><span class="gtag">Gerbang 1</span></div>
    <div class="card stage"><span class="n">3</span><b>Gambar dan frame</b></div>
    <div class="card stage"><span class="n">4</span><b>Narasi dan musik</b></div>
    <div class="card stage gate"><span class="n">5</span><b>Animatic</b><span class="gtag">Gerbang 2</span></div>
    <div class="card stage gate"><span class="n">6</span><b>Video</b><span class="gtag">Gerbang 3</span></div>
    <div class="card stage"><span class="n">7</span><b>Edit final</b></div>
  </div>
  <div class="strip" aria-label="Contoh frame reel Tebak Harga">
    <img src="%(Frame_Hook)s" alt="Hook: TEBAK HARGANYA?"><img src="%(Frame_Petunjuk_1)s" alt="Petunjuk 1: seberang mall besar"><img src="%(Frame_Harga)s" alt="Harga: mulai 1,3M-an"><img src="%(Frame_Akhir)s" alt="Penutup: Rumah Kita Realty">
  </div>
  <p class="note" style="margin-top:8px">Reel contoh kelas: Rumah Kita Realty, Cluster Aster. Semua nama fiktif, semua gambar dibuat AI.</p>
</section>

<section id="masuk">
  <p class="eyebrow">Yang masuk ke model</p>
  <h2>Yang kamu berikan menentukan yang kamu dapat</h2>
  <div class="grid g3" style="margin-top:18px">
    <article class="card role"><span class="n">GAMBAR</span><h3>Menentukan tampilan</h3><p>Wajah, baju, rumah, cahaya, warna. Model video meniru gambar pertama yang sudah kamu setujui.</p></article>
    <article class="card role"><span class="n">KATA-KATA</span><h3>Menentukan gerak</h3><p>Satu gerakan kamera per klip, dengan angka yang bisa diukur: "maju setengah meter dalam 6 detik".</p></article>
    <article class="card role"><span class="n">SUARA</span><h3>Dibuat terpisah</h3><p>Narasi dan musik dibuat dulu, lalu klip mengikuti suaranya. Tulisan di layar ditambahkan saat edit.</p></article>
  </div>
  <div class="tw"><table>
    <tr><th>Model</th><th>Tugas</th><th>Biaya</th><th>Status</th></tr>
    <tr><td><b>glm-5.3-flash</b></td><td>otak agent di WorkBuddy</td><td>kredit WorkBuddy</td><td>dipakai di workshop</td></tr>
    <tr><td><b>gpt-image-2</b></td><td>semua gambar diam</td><td class="num">10 kredit</td><td>teruji</td></tr>
    <tr><td><b>Veo 3.1 Lite</b></td><td>klip video 8 detik dari gambar pertama</td><td class="num">35 kredit</td><td>teruji, 5 dari 5 berhasil</td></tr>
    <tr><td><b>Kling AI Avatar Pro</b></td><td>presenter bicara ke kamera, bibirnya ikut narasi</td><td class="num">16 kredit/detik</td><td>teruji, 4 dari 4 berhasil</td></tr>
    <tr><td><b>Gemini TTS</b></td><td>narasi dari naskah</td><td class="num">≈ Rp50/take</td><td>teruji</td></tr>
    <tr><td><b>Lyria</b></td><td>musik latar dengan drop</td><td class="num">≈ US$0,04/klip</td><td>teruji</td></tr>
  </table></div>
</section>

<!-- ============ 2 · PR ============ -->
<div class="part" id="pr"><b>BAGIAN 2</b><span>PR sebelum workshop</span></div>

<section>
  <h2>Tiga akun, sepuluh menit</h2>
  <p class="lead">Bagian ini butuh email dan pembayaran, jadi AI tidak bisa mengerjakannya. Selesaikan di rumah supaya Sesi 1 lancar.</p>
  <div class="grid g3" style="margin-top:18px">
    <article class="card acc"><span class="for">Aplikasi agent</span><h3>WorkBuddy</h3>
      <ol><li>Daftar lewat link undangan di bawah, dengan Google, GitHub, atau X.</li><li>Akun baru dapat kredit sambutan. Otak AI kita, glm-5.3-flash, memakai kredit ini.</li></ol>
      <a class="invite" href="%(invite)s"><b>Daftar WorkBuddy</b><span>workbuddy.ai/invite?code=ULLL7X4E</span></a></article>
    <article class="card acc"><span class="for">Gambar dan video</span><h3>kie.ai</h3>
      <ol><li>Buat akun dan isi saldo kredit.</li><li>Buat kunci baru khusus kelas.</li><li>Beri kunci itu <b>batas kredit total</b>. Ini pagar terakhirmu.</li></ol>
      <span class="url">kie.ai/api-key</span></article>
    <article class="card acc"><span class="for">Narasi dan musik</span><h3>OpenRouter</h3>
      <ol><li>Buat akun dan isi saldo sedikit. Suara dan musik satu reel habis kurang dari US$0,50.</li><li>Buat kunci. Boleh menyusul.</li></ol>
      <span class="url">openrouter.ai/keys</span></article>
  </div>
  <p class="callout hot"><b>Kunci API itu seperti PIN ATM.</b> Simpan di catatan pribadi. Jangan dikirim di chat, jangan difoto, jangan ditaruh di slide. Sebagian situs hanya menampilkan kunci sekali, jadi salin sebelum menutup halaman.</p>
  %(check_pr)s
</section>

<!-- ============ 3 · SESI 1 ============ -->
<div class="part" id="sesi1"><b>BAGIAN 3</b><span>Sesi 1 · Pasang</span></div>

<section>
  <h2>Tiga langkah. AI yang mengunduh dan memasang.</h2>
  <p class="lead">Kamu memasang WorkBuddy. AI di dalamnya mengambil AI Videographer dari GitHub dan memasang semua alatnya. Kuncimu kamu tempel sendiri, di halaman lokal, bukan di chat.</p>
  <ol class="steps">
    <li class="card step">
      <div>
        <div class="head"><span class="circle">1</span><h3>Pasang WorkBuddy</h3><span class="badge you">KAMU</span></div>
        <ul>
          <li>Sudah daftar lewat link undangan? Unduh aplikasinya dari <b>workbuddy.ai</b>.</li>
          <li><b>Windows:</b> jalankan file <code>.exe</code>. Muncul layar biru "Windows protected your PC"? Klik <b>More info</b>, lalu <b>Run anyway</b>.</li>
          <li><b>Mac:</b> buka file <code>.dmg</code>, seret WorkBuddy ke folder Applications.</li>
          <li>Buka WorkBuddy dan masuk dengan akun yang sama. Pertama kali bisa butuh 30–60 detik.</li>
        </ul>
      </div>
      <figure class="mock" style="margin:0"><div class="smart"><b>Windows protected your PC</b><span>Microsoft Defender SmartScreen prevented an unrecognized app from starting…</span><u>More info</u><div class="r"><span class="hl">Run anyway</span><span>Don't run</span></div></div></figure>
    </li>
    <li class="card step">
      <div>
        <div class="head"><span class="circle">2</span><h3>Minta AI memasang</h3><span class="badge ai">AI</span></div>
        <ul>
          <li>Buat folder baru, misalnya <code>AI_Videographer</code> di Documents.</li>
          <li>Di WorkBuddy: tugas baru, <b>Select Folder</b> ke folder itu, model <b>glm-5.3-flash</b>, izin <b>Default Permissions</b>.</li>
          <li>Tempel pesan ini, lalu Enter. Kebanyakan peserta memakai Windows, jadi pesan Windows ada di atas.</li>
        </ul>
        <div class="prompt"><div class="top">Windows · tempel ke WorkBuddy<button type="button" class="copy" data-from="msg-win">Salin</button></div><p id="msg-win">%(msg_win)s</p></div>
        <details><summary>Pakai Mac? Pesannya yang ini</summary>
          <div class="prompt"><div class="top">Mac · tempel ke WorkBuddy<button type="button" class="copy" data-from="msg-mac">Salin</button></div><p id="msg-mac">%(msg_mac)s</p></div>
          <p class="hint">Di Mac, klik Install kalau jendela Apple muncul, lalu bilang "jalankan setup lagi". Kalau Homebrew belum ada, AI memberimu satu baris untuk app Terminal, karena butuh password Mac-mu.</p>
        </details>
        <ul>
          <li>WorkBuddy bertanya sebelum tiap perintah: klik <b>Allow</b>. Windows bertanya "allow this app to make changes"? Klik <b>Yes</b>.</li>
          <li>Memasang Python dan FFmpeg butuh beberapa menit. Biarkan berjalan.</li>
        </ul>
        <p class="hint">Perintah yang wajar di langkah ini: <code>git clone</code> atau unduh <code>main.zip</code>, <code>setup.ps1</code> atau <code>setup.sh</code>, <code>winget install</code>, <code>pip install pillow</code>, <code>brew install ffmpeg</code>. Ada perintah lain yang aneh? Klik Cancel dan tanya: "Kenapa perintah ini perlu?"</p>
      </div>
      <figure class="term" role="img" aria-label="Contoh akhir setup yang berhasil" style="margin:0">
        <div><span class="ok">OK </span> Python 3.12</div><div><span class="ok">OK </span> FFmpeg</div><div><span class="ok">OK </span> Pillow (caption dan grafis)</div><div><span class="ok">OK </span> Expert AI Videographer terpasang</div><div><span class="ok">OK </span> File .env</div><div>Setup page: http://127.0.0.1:…</div><div>== Tinggal ini: tempel kunci …</div>
      </figure>
    </li>
    <li class="card step">
      <div>
        <div class="head"><span class="circle">3</span><h3>Tempel kunci, lalu buka ulang</h3><span class="badge you">KAMU</span></div>
        <ul>
          <li>Halaman <b>Setup AI Videographer</b> terbuka di browser. Tempel kunci kie.ai (dan OpenRouter kalau sudah ada), lalu klik <b>Simpan</b>. Halaman itu langsung mengecek saldo kie.ai-mu.</li>
          <li>Tutup WorkBuddy <b>sepenuhnya</b>. Windows: klik kanan ikon WorkBuddy di taskbar atau di pojok kanan bawah, pilih Quit. Mac: Cmd + Q.</li>
          <li>Buka lagi WorkBuddy. Tugas baru, <b>Select Folder</b> ke folder yang disebut di akhir setup (<code>…\\ai-videographer-kelas</code>).</li>
          <li>Pilih Expert di <b>Expert Center › My Experts › AI Videographer</b>, model <b>glm-5.3-flash</b>, lalu klik <b>Cek setup</b>.</li>
        </ul>
        <p class="hint">Halaman setup tertutup? Bilang ke AI: "buka halaman setup".</p>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <figure class="mock" style="margin:0"><div class="bar"><i></i><i></i><i></i>127.0.0.1 · Setup AI Videographer</div><div class="mb"><b>Setup AI Videographer</b><span>Kunci kie.ai</span><span class="box">••••••••••••••••</span><span>Kunci OpenRouter (opsional)</span><span class="box">tempel kunci dari openrouter.ai/keys</span><span class="btn">Simpan</span></div></figure>
        <div class="excard"><img src="%(avatar)s" alt=""><div><b>AI Videographer</b><div class="note">Expert Center › My Experts</div></div></div>
      </div>
    </li>
  </ol>
  <div class="done"><b>Sesi 1 selesai kalau</b> Cek setup tidak menampilkan FAIL, dan Expert AI Videographer sudah terpilih.</div>
  %(check_s1)s
</section>

<!-- ============ 4 · SESI 2 ============ -->
<div class="part" id="sesi2"><b>BAGIAN 4</b><span>Sesi 2 · Reel pertama</span></div>

<section>
  <h2>Kamu menjawab dan memutuskan. AI yang bekerja.</h2>
  <p class="lead">Setiap kali selesai di halaman review, kembali ke WorkBuddy dan bilang <b>"sudah"</b>. Hasil akhirnya ada di folder <code>99_Output</code>.</p>
  <ol class="steps">
    <li class="card step solo">
      <div class="head"><span class="circle">1</span><h3>Klik "Buat video baru", jawab lima pertanyaan</h3><span class="badge you">KAMU</span></div>
      <ol><li>Nama brand atau klien?</li><li>Apa yang dijual, di mana, dan mulai harga berapa?</li><li>Tiga alasan kenapa layak dibeli?</li><li>Apa yang harus dilakukan penonton di akhir (DM, WhatsApp, datang)?</li><li>Ada foto asli tempatnya? Lampirkan. Tanpa foto, semua gambar dibuat AI.</li></ol>
    </li>
    <li class="card step solo">
      <div class="head"><span class="circle">2</span><h3>Expert menulis rencana</h3><span class="badge ai">AI</span></div>
      <p style="margin-top:10px">Naskah, daftar shot, dan tampilan seluruh reel. Model glm-5.3-flash cepat dan murah, tapi berpikir cukup lama: 10 sampai 15 menit itu wajar. Baca ringkasannya, dan minta perubahan kalau perlu.</p>
    </li>
    <li class="card step gatestep">
      <div>
        <div class="head"><span class="circle">3</span><h3>Gerbang 1 · Look</h3></div>
        <ul><li>Expert membuat 1–3 gambar gaya, lalu mengirim link halaman review.</li><li>Pas? Klik <b>Approve look</b>. Belum? Tulis catatan di gambarnya, lalu klik <b>Done</b>.</li><li>Kembali ke WorkBuddy, bilang "sudah".</li></ul>
      </div>
      <div class="frames"><img src="%(Look_Rumah_Depan)s" alt="Gambar gaya: rumah dua lantai"><img src="%(Rani_Mobil)s" alt="Gambar gaya: presenter di mobil"></div>
    </li>
    <li class="card step solo">
      <div class="head"><span class="circle">4</span><h3>Gambar, narasi, musik, dan animatic</h3><span class="badge ai">AI</span></div>
      <p style="margin-top:10px">Expert membuat gambar setiap shot, narasi, dan musik, lalu menyusun <b>animatic</b>: seluruh reel sebagai gambar diam, lengkap dengan suara dan tulisan.</p>
    </li>
    <li class="card step gatestep">
      <div>
        <div class="head"><span class="circle">5</span><h3>Gerbang 2 · Reel</h3></div>
        <ul><li>Tonton animatic di halaman review.</li><li>Pas? Klik <b>Approve reel</b>. Gambar masih murah, jadi perbaiki sekarang, sebelum membayar video.</li></ul>
      </div>
      <div class="frames"><img src="%(Frame_Peta)s" alt="Frame animatic: peta ke tol"><img src="%(Frame_Harga)s" alt="Frame animatic: harga"></div>
    </li>
    <li class="card step gatestep">
      <div>
        <div class="head"><span class="circle">6</span><h3>Gerbang 3 · Video</h3></div>
        <ul><li>Di bagian <b>Video</b>, setiap klip menampilkan biayanya.</li><li>Klik <b>Approve</b> untuk <b>satu klip pilot</b> saja. Browser bertanya sekali lagi. Satu klik membayar satu take.</li><li>Bilang "sudah". Satu klip butuh sekitar 3–6 menit.</li></ul>
      </div>
      <figure class="mock" style="margin:0"><div class="bar"><i></i><i></i><i></i>Halaman review · Video</div><div class="mb"><span>S01 · hook · 8 detik · <b>35 kredit</b></span><span class="btn or">Approve · 35 credits</span><span class="note">Klip lain menunggu sampai pilotnya kamu tonton.</span></div></figure>
    </li>
    <li class="card step solo">
      <div class="head"><span class="circle">7</span><h3>Tonton pilot, lalu setujui sisanya</h3><span class="badge you">KAMU</span></div>
      <p style="margin-top:10px">Gerak, cahaya, dan harganya sudah pas? Setujui klip berikutnya. Klip yang gagal tidak memotong kredit, tapi mencoba lagi butuh klik baru.</p>
    </li>
    <li class="card step solo">
      <div class="head"><span class="circle">8</span><h3>Edit final</h3><span class="badge ai">AI</span></div>
      <p style="margin-top:10px">Expert menyatukan klip, narasi, musik, caption, dan grafis menjadi reel 9:16 di folder <code>99_Output</code>. Tonton, beri masukan, lalu kirim.</p>
    </li>
  </ol>
  %(check_s2)s
</section>

<!-- ============ BICARA ============ -->
<section id="bicara">
  <p class="eyebrow">Cara bicara ke AI</p>
  <h2>Pakai bahasa biasa</h2>
  <div class="tw"><table>
    <tr><th>Kamu bilang</th><th>Expert melakukan</th></tr>
    <tr><td><b>"Buat video baru"</b></td><td>membuat proyek, menanyakan lima hal, lalu mulai bekerja</td></tr>
    <tr><td><b>"Lanjut"</b></td><td>mengerjakan langkah berikutnya</td></tr>
    <tr><td><b>"Sudah"</b></td><td>membaca klik dan catatanmu di halaman review, lalu lanjut</td></tr>
    <tr><td><b>"Kenapa berhenti?"</b></td><td>menjelaskan apa yang sedang ia tunggu</td></tr>
    <tr><td><b>"Cek setup"</b></td><td>memeriksa alat dan kunci</td></tr>
    <tr><td><b>"Buka lagi halaman review"</b></td><td>membuka halaman review yang sudah tertutup</td></tr>
  </table></div>
  <h3 style="margin-top:26px">Kebiasaan yang menghemat kredit</h3>
  <div class="grid g2" style="margin-top:12px">
    <p class="callout" style="margin:0"><b>Satu pilot dulu.</b> Tonton satu klip sebelum menyetujui sisanya.</p>
    <p class="callout" style="margin:0"><b>Catatan yang spesifik.</b> "Cahayanya terlalu kuning" lebih berguna daripada "kurang bagus".</p>
    <p class="callout" style="margin:0"><b>Perbaiki di gambar, bukan di video.</b> Mengulang gambar ≈ Rp800, mengulang klip ≈ Rp2.900.</p>
    <p class="callout" style="margin:0"><b>Jujur ke penonton.</b> Rumah yang dijual selalu foto asli dari klien; label "ilustrasi" untuk rencana.</p>
  </div>
</section>

<!-- ============ MACET ============ -->
<section id="macet">
  <p class="eyebrow">Kalau macet</p>
  <h2>Yang sering terjadi, dan jalan keluarnya</h2>
  <div class="tw"><table>
    <tr><th>Yang terjadi</th><th>Yang kamu lakukan</th></tr>
    <tr><td>Expert bilang tidak bisa menjalankan perintah</td><td>izinkan perintahnya di WorkBuddy, lalu bilang "lanjut"</td></tr>
    <tr><td>Expert bilang WorkBuddy tidak bisa membuat video</td><td>bilang: "Pakai alat vg di folder ini. Jalankan vg next."</td></tr>
    <tr><td>Link review tidak terbuka</td><td>bilang "buka lagi halaman review"</td></tr>
    <tr><td>Kunci salah, atau saldo kie.ai habis</td><td>isi saldo di kie.ai, lalu bilang "buka halaman setup" dan tempel kuncinya lagi</td></tr>
    <tr><td>Expert lama diam</td><td>glm-5.3-flash sedang berpikir. Tunggu 1–2 menit, lalu bilang "lanjut"</td></tr>
    <tr><td>Windows: Microsoft Store terbuka saat perintah <code>python3</code></td><td>bilang: "Di Windows pakai <code>python</code>, bukan <code>python3</code>."</td></tr>
    <tr><td>Windows: <code>winget</code> tidak ditemukan</td><td>perbarui <b>App Installer</b> dari Microsoft Store, lalu bilang "jalankan setup lagi"</td></tr>
    <tr><td>Windows: caption tidak muncul, ada pesan tentang Pillow</td><td>bilang: "Jalankan <code>python -m pip install --user pillow</code>, lalu ulangi."</td></tr>
  </table></div>
</section>

<!-- ============ KAMUS ============ -->
<section id="kamus">
  <p class="eyebrow">Kamus kecil</p>
  <h2>Kata yang akan kamu dengar</h2>
  <dl>
    <div><dt>Agent</dt><dd>AI yang memakai alat dan mengerjakan langkahnya sendiri. Level 2.</dd></div>
    <div><dt>Expert</dt><dd>Uraian tugas yang dipasang ke WorkBuddy. Punya kita: AI Videographer.</dd></div>
    <div><dt>glm-5.3-flash</dt><dd>Otak agent di WorkBuddy: cepat dan murah.</dd></div>
    <div><dt>vg</dt><dd>Alat di folder kelas yang memesan gambar dan video, dan menjaga uangmu.</dd></div>
    <div><dt>kie.ai</dt><dd>Perantara model gambar, video, dan musik. Dibayar dengan kredit.</dd></div>
    <div><dt>OpenRouter</dt><dd>Perantara model teks dan suara. Dibayar dalam dolar per pemakaian.</dd></div>
    <div><dt>Kredit</dt><dd>Uangnya kie.ai. Gambar ≈ 10, klip ≈ 35.</dd></div>
    <div><dt>API key (kunci)</dt><dd>Kata sandi panjang untuk memakai layanan atas namamu. Seperti PIN ATM.</dd></div>
    <div><dt>Prompt</dt><dd>Kata-kata yang kamu berikan ke model.</dd></div>
    <div><dt>Look</dt><dd>Tampilan seluruh reel: satu tempat, satu cahaya, satu warna.</dd></div>
    <div><dt>Frame</dt><dd>Satu gambar diam. Video sekitar 30 frame per detik.</dd></div>
    <div><dt>Animatic</dt><dd>Reel sebagai gambar diam, lengkap dengan suara dan tulisan.</dd></div>
    <div><dt>Gerbang</dt><dd>Titik berhenti: alat menunggu klik setujumu.</dd></div>
    <div><dt>Pilot</dt><dd>Satu klip percobaan sebelum membayar sisanya.</dd></div>
    <div><dt>Take</dt><dd>Satu kali hasil. Mengulang berarti take baru.</dd></div>
    <div><dt>9:16</dt><dd>Video vertikal untuk Reels dan TikTok.</dd></div>
  </dl>
</section>

<footer>
  <span>Semua bahan kelas: <a href="%(repo)s">github.com/tansilandre/ai-videographer-kelas</a>. Versi teks halaman ini ada di Panduan WorkBuddy.</span>
  <span>Harga dari kie.ai dan OpenRouter per September 2026. Contoh gambar dari proyek kelas: semua dibuat AI, agen dan clusternya fiktif.</span>
</footer>
</div>
%(js)s
""" % dict(P, css=CSS, js=JS, invite=INVITE, repo=REPO, msg_win=e(MSG_WIN), msg_mac=e(MSG_MAC),
           check_pr=checklist("pr", ["Akun WorkBuddy lewat link undangan", "Kunci kie.ai dengan batas kredit, disimpan di catatan pribadi",
                                     "Kunci OpenRouter (boleh menyusul)"]),
           check_s1=checklist("s1", ["WorkBuddy terpasang dan sudah masuk", "Pesan pasang terkirim, setup selesai",
                                     "Kunci ditempel di halaman setup", "Cek setup bersih, Expert terpilih"]),
           check_s2=checklist("s2", ["Lima pertanyaan terjawab", "Gerbang 1: look disetujui", "Gerbang 2: reel disetujui",
                                     "Gerbang 3: satu pilot disetujui dan ditonton", "Reel final ada di 99_Output"]))


if __name__ == "__main__":
    if OUT.exists():
        raise SystemExit("%s already exists; never overwrite a delivered version, pass a new version" % OUT)
    OUT.write_text(page(), encoding="utf-8")
    print("wrote %s (%d KB)" % (OUT, OUT.stat().st_size // 1024))
