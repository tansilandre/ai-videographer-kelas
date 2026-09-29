# Panduan WorkBuddy · AI Videographer

## Tujuan

- Memasang WorkBuddy, Expert **AI Videographer**, dan model **glm-5.3-flash** di Mac-mu.
- Membuat satu reel dengan bicara ke Expert, dan menyetujui setiap gerbang dengan satu klik.
- Tahu apa yang harus dilakukan kalau ada yang macet.

## Gambaran singkat

Ada empat bagian yang bekerja bersama:

| Bagian | Perannya | Ibaratnya |
|---|---|---|
| **WorkBuddy** | aplikasi *agent* dari Tencent: membaca file, menjalankan perintah, mengobrol denganmu | badan |
| **Model** glm-5.3-flash | yang berpikir dan memutuskan langkah | otak |
| **Expert** AI Videographer | *playbook* (buku panduan kerja) yang dipasang ke WorkBuddy | uraian tugas |
| **Alat vg** | program di repo ini yang membuat gambar, suara, dan video, mencatat biaya, dan menjaga gerbang | tangan yang memegang dompet |

Expert tidak menghafal urutan kerja. Setiap kali, ia menjalankan satu perintah: `vg next`. Perintah itu melihat proyekmu dan menulis **satu** langkah berikutnya: perintah yang harus dijalankan, file yang harus ditulis, atau pertanyaan yang harus ditanyakan kepadamu. Karena itu model yang cepat dan murah pun bisa menjalankannya dengan rapi.

Uangmu dijaga oleh alat vg, bukan oleh model. Semua persetujuan (look, reel, dan setiap klip video) hanya bisa kamu berikan dengan **klik di halaman review**. Expert tidak bisa menyetujui apa pun atas namamu.

## Yang kamu butuhkan

- Sebuah **Mac**. Caption dan grafis digambar dengan Swift, bahasa pemrograman buatan Apple.
- Alat dasar: Xcode Command Line Tools, Homebrew, FFmpeg, Git, dan Python 3.9 atau lebih baru. Ikuti Langkah 1 sampai 4 di [Pelajaran 04 · Persiapan Alat](../1_Pelajaran/Pelajaran_04_Persiapan_Alat_v1.1.md).
- **WorkBuddy**, dari https://www.workbuddy.ai. Masuk dengan akun Google atau GitHub. Tampilan bahasa Indonesia tersedia di pengaturan.
- **SumoPod** (https://ai.sumopod.com): gerbang (*gateway*) model AI, bayar dengan rupiah lewat QRIS. Di sini kamu membuat **API key** untuk model glm-5.3-flash. Gateway lain yang kompatibel dengan OpenAI juga bisa, asal menyediakan model yang sama.
- **kie.ai** (https://kie.ai): gambar dan video, dibayar dengan kredit. Buat kunci baru khusus kelas ini dan beri **batas kredit total** di https://kie.ai/api-key.
- **OpenRouter** (https://openrouter.ai): narasi dan musik, beberapa sen per take. Opsional, tapi reel tanpa suara terasa hampa.

Perlakukan setiap API key seperti PIN ATM: jangan dikirim di chat, jangan difoto, jangan ditaruh di slide.

## Bagian A · Pasang (sekali saja)

### Langkah 1 · Alat dasar

Selesaikan Langkah 1 sampai 4 di Pelajaran 04. Kalau `git --version`, `python3 --version`, dan `ffmpeg -version` semuanya menampilkan nomor versi, lanjut.

### Langkah 2 · WorkBuddy

1. Unduh WorkBuddy dari https://www.workbuddy.ai, pindahkan ke folder Applications, lalu buka.
2. Masuk dengan Google atau GitHub.
3. Tutup lagi. Membuka sekali ini penting: WorkBuddy membuat folder pengaturannya (`~/.workbuddy-ai`) saat pertama kali dibuka.

### Langkah 3 · Unduh repo kelas

Buka Terminal, lalu jalankan satu baris sekali:

```bash
cd ~/Documents
git clone https://github.com/tansilandre/ai-videographer-kelas.git
cd ai-videographer-kelas
```

### Langkah 4 · Jalankan installer

```bash
bash 2_Tools/workbuddy/install_workbuddy.sh --add-models
```

Installer bertanya dua hal:

1. **URL**: tekan Enter untuk memakai SumoPod (`https://ai.sumopod.com/v1/chat/completions`).
2. **API key**: tempel kunci SumoPod-mu, lalu Enter. Huruf yang kamu ketik tidak terlihat. Itu normal.

Yang dikerjakan installer:

- membuat file `.env` dan menghubungkan skill ke `.codebuddy/skills`, tempat WorkBuddy membacanya;
- menyalin Expert **AI Videographer** ke WorkBuddy dan mendaftarkannya dengan skrip resmi WorkBuddy sendiri;
- menambahkan model **glm-5.3-flash** dan **MiniMax-M3.1-Flash-Preview** ke daftar model WorkBuddy (salinan lama pengaturanmu disimpan sebagai `models.json.bak`).

Installer boleh dijalankan ulang kapan saja. Kalau kamu sudah punya kunci SumoPod di WorkBuddy dan tidak mau menambah model, jalankan tanpa `--add-models`, lalu tambahkan model sendiri di pengaturan WorkBuddy: **Settings → Models → Custom API** (atau *Model kustom*), dengan URL di atas, nama model `glm-5.3-flash`, dan sakelar *tool calling* serta *image input* dinyalakan.

### Langkah 5 · Isi `.env`

`.env` adalah file rahasia di folder repo. Buka dengan TextEdit:

```bash
open -e .env
```

Isi atau ubah baris-baris ini, **sendiri**:

```
KIE_API_KEY=kunci-kie-ai-mu
OPENROUTER_API_KEY=kunci-openrouter-mu
VG_APPROVAL_MODE=page
```

`VG_APPROVAL_MODE=page` artinya: semua persetujuan adalah klik di halaman review. Biarkan baris lain seperti apa adanya. Simpan (Cmd + S) lalu tutup.

Agent tidak pernah boleh mengubah `.env`. Itu tugasmu, dan hanya kamu.

### Langkah 6 · Cek

```bash
python3 2_Tools/vg/vg.py doctor
```

Kamu mencari tiga hal:

- tidak ada baris `FAIL`;
- `ok   approval mode   page (the human clicks Approve on the review page)`;
- `ok   skills (WorkBuddy)`.

Baris `warn` boleh. Kalau ada `FAIL`, baca penjelasannya di baris itu, perbaiki, lalu jalankan lagi.

### Langkah 7 · Buka di WorkBuddy

1. Keluar penuh dari WorkBuddy (Cmd + Q), lalu buka lagi. WorkBuddy membaca Expert dan model baru saat dibuka.
2. Pilih folder kerja (*workspace*): folder `ai-videographer-kelas` yang tadi kamu unduh. Expert hanya bekerja di folder ini.
3. Buka menu **Experts** → **My Experts** (namanya bisa sedikit berbeda di tampilan bahasa Indonesia), lalu pilih **AI Videographer**.
4. Di pemilih model, pilih **glm-5.3-flash**.
5. Mode izin: pakai **Default**. WorkBuddy akan meminta izin sebelum menjalankan perintah. Baca perintahnya, lalu izinkan. Kalau yang diminta adalah `python3 2_Tools/vg/vg.py ...`, itu alat kita.

### Langkah 8 · Percakapan pertama

Klik saran **"Cek setup: apakah semua alat dan kunci sudah siap?"**. Expert menjalankan `vg doctor` dan melaporkan hasilnya dalam satu atau dua kalimat. Kalau laporannya bersih, kamu siap.

## Bagian B · Pakai: membuat satu reel

### Cara bicara ke Expert

Tidak perlu hafal perintah. Pakai bahasa biasa:

| Kamu bilang | Expert melakukan |
|---|---|
| "Buat video baru dari brief ini: …" | membuat proyek, menyimpan brief, menulis rencana, lalu melanjutkan |
| "Lanjut" atau "Lanjutkan project saya" | menjalankan `vg next` dan mengerjakan langkah berikutnya |
| "Sudah" / "Sudah saya approve" | membaca klik dan catatanmu di halaman review, lalu lanjut |
| "Cek status project" | menjalankan `vg status` dan menjelaskannya |
| "Kenapa berhenti?" | menjelaskan langkah yang sedang ditunggu |

Setelah setiap langkah, Expert menulis satu baris: apa yang ia kerjakan, berapa kredit terpakai, apa berikutnya.

### Alurnya, dari brief sampai reel

| Tahap | Expert mengerjakan | Kamu mengerjakan |
|---|---|---|
| 1 · Rencana | menyimpan brief di `0_Source/Brief.md`, menulis `1_Script/Shotlist.json`, memeriksanya dengan `vg validate` | membaca ringkasan rencana, minta perubahan kalau perlu |
| 2 · Look | membuat 1–3 *style frame* (gambar contoh gaya seluruh reel), memeriksa setiap gambar, lalu mengirim link halaman review | membuka link, lalu klik **Approve look**, atau menulis catatan dan klik **Done** |
| 3 · Gambar | membuat lembar referensi, panel storyboard, dan frame pertama tiap shot, lalu memeriksa semuanya | menunggu |
| 4 · Suara dan edit plan | menulis rencana edit, membuat narasi dan musik, lalu merender *animatic* (reel sebagai gambar diam, lengkap dengan suara dan caption) | menonton animatic di halaman review, lalu klik **Approve reel**, atau menulis catatan dan klik **Done** |
| 5 · Video | menunjukkan biaya pilot, lalu menunggu klikmu | di bagian **Video** halaman review, klik **Approve** untuk klip pilot. Setelah pilot ditonton dan disukai, setujui sisanya |
| 6 · Edit final | merender reel final ke `99_Output/` | menonton, memberi masukan, mengirim ke klien |

Waktunya berbeda-beda. Model glm-5.3-flash cepat dan murah, tapi berpikir cukup lama: menulis rencana dari brief bisa makan 10–15 menit. Satu klip video butuh sekitar 3–6 menit. Sambil menunggu, kamu bebas mengerjakan hal lain.

## Halaman review

Halaman review adalah milikmu. Expert membukanya dengan `vg review --detach` lalu mengirim link seperti `http://127.0.0.1:52011/?t=…`. Link itu hanya jalan di Mac-mu sendiri.

Isi halamannya dari atas ke bawah:

| Bagian | Isinya | Tombol |
|---|---|---|
| Look | teks look (dunia, cahaya, *grade*, grafis) dan style frame | **Approve look** |
| Reference sheets | lembar referensi karakter, lokasi, produk | pilih *take* (v1, v2, …) |
| Reel | setiap *beat* dengan gambar dan teksnya | kotak catatan per gambar |
| Animatic | video gambar diam seluruh reel | **Approve reel** |
| Video | setiap klip, panjangnya, dan biayanya dalam kredit | **Approve · N credits**, **New take**, **Approve all not made** |
| Bawah | | **Done, back to the agent** |

Aturannya sederhana:

- **Setuju?** Klik Approve. Untuk video, browser bertanya sekali lagi ("Spend 35 credits on S01?"). Satu klik membayar **satu take satu klip**.
- **Belum setuju?** Tulis catatan di gambar yang harus berubah, misalnya "cahayanya terlalu kuning" atau "dia harus menatap kamera". Lalu klik **Done**.
- Setelah klik, kembali ke WorkBuddy dan bilang **"sudah"**. Expert membaca klik dan catatanmu.
- Halaman tertutup setelah Done. Butuh lagi? Bilang "buka lagi halaman review".

Mulailah video dengan **satu klip pilot**. Tonton pilotnya. Baru setujui sisanya kalau gerak, cahaya, dan harganya sudah pas.

## Uang: apa membayar apa

| Yang dibuat | Dibayar ke | Kira-kira |
|---|---|---|
| Satu gambar (style frame, storyboard, frame) | kie.ai | 6–16 kredit |
| Satu klip video Veo 3.1 Lite, 8 detik, 1080p | kie.ai | 35 kredit |
| Presenter bicara ke kamera (Kling AI Avatar Pro) | kie.ai | 16 kredit per detik |
| Satu take narasi atau musik | OpenRouter | beberapa sen dolar |
| Otak Expert (glm-5.3-flash) | SumoPod | kecil. Di uji coba kami, satu sesi menulis rencana dari brief memakai sekitar 1,2 juta token masuk (sebagian besar ter-*cache*) dan 29 ribu token keluar, di bawah US$0,10 dengan harga resmi Z.ai |

Ada tiga pagar pengaman:

1. **Klik di halaman review.** Tanpa klikmu, video tidak dibuat.
2. **Batas di `.env`**: `VG_BUDGET_PROJECT` (batas per proyek) dan `VG_MAX_PER_CALL` (batas per permintaan). Alat menolak kalau batas terlampaui.
3. **Batas kredit di kunci kie.ai**, yang kamu atur di kie.ai. Ini dinding terakhir.

Kalau sebuah klip **gagal**, kreditnya tidak dipotong. Tapi mencoba lagi butuh klik baru.

## Kalau macet

| Yang terjadi | Artinya | Yang kamu lakukan |
|---|---|---|
| Expert bilang tidak bisa menjalankan perintah | izin Bash ditolak | izinkan perintahnya di WorkBuddy (mode Default), lalu bilang "lanjut" |
| Expert bilang WorkBuddy "tidak mendukung pembuatan video" | model bingung dengan alat bawaan WorkBuddy | bilang: "Video dibuat dengan alat vg di folder ini, bukan alat bawaan WorkBuddy. Jalankan vg next." |
| `REFUSED: VG_APPROVAL_MODE=page …` | agent mencoba menyetujui sendiri, dan alat menolaknya. Ini aman | setujui di halaman review, lalu bilang "sudah" |
| Link review tidak terbuka, atau "server not answering" | halamannya sudah ditutup setelah Done | bilang "buka lagi halaman review" |
| `FAIL KIE_API_KEY` di doctor | kunci belum diisi | isi `.env` (Langkah 5) |
| `PROVIDER ERROR … 402` | kredit kie.ai habis | isi saldo di kie.ai |
| Expert lama diam | glm-5.3-flash sedang berpikir | tunggu 1–2 menit. Kalau tetap diam, bilang "lanjut" |
| Sebuah perintah kehabisan waktu | tugas mungkin masih jalan di kie.ai | minta Expert menjalankan `vg resume`, **jangan** mengulang perintahnya |
| Status `submitting` atau `unknown` yang tidak berubah | alat tidak tahu apakah kie.ai sudah membuat tugasnya | buka dashboard kie.ai dan cek. Ada tugasnya: `vg adopt`. Tidak ada: `vg release`. Dua perintah ini hanya untukmu |
| Expert tidak muncul di My Experts | WorkBuddy belum dibuka ulang, atau installer gagal | Cmd + Q, buka lagi WorkBuddy. Jalankan installer lagi dan baca pesannya |

Ingin tahu posisi proyek tanpa bertanya ke Expert? Jalankan sendiri di Terminal:

```bash
python3 2_Tools/vg/vg.py next -p NAMA_PROYEK
```

## Membuat ulang dan memperbarui

- **Laptop baru?** Ulangi Bagian A dari awal. Semua yang dibutuhkan ada di repo ini dan di akun-akunmu.
- **Ada versi baru repo?** Jalankan `git pull`, lalu jalankan installer lagi, lalu buka ulang WorkBuddy.
- **Mengubah Expert sendiri?** Ubah file di `2_Tools/workbuddy/expert/ai-videographer/`, naikkan `version` di `.codebuddy-plugin/plugin.json` (misalnya 1.0.0 menjadi 1.0.1), lalu jalankan installer lagi. WorkBuddy menyimpan Expert berdasarkan nomor versi, jadi perubahan dengan nomor yang sama tidak terbaca.
- **Ganti otak?** Pilih MiniMax-M3.1-Flash-Preview di pemilih model. Playbook-nya sama.

## Ringkasan

1. Pasang sekali: alat dasar, WorkBuddy, repo, installer, `.env`, doctor.
2. Buka folder repo di WorkBuddy, pilih Expert AI Videographer dan glm-5.3-flash.
3. Bicara dengan bahasa biasa. Expert selalu mengerjakan satu langkah dari `vg next`.
4. Setiap gerbang adalah klikmu di halaman review. Mulai video dengan satu pilot.
