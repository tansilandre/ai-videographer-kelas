# Pelajaran 04 · Persiapan Alat

## Tujuan

- Membuka *Terminal* dan menjalankan perintah sederhana tanpa takut.
- Memasang semua alat: Xcode Command Line Tools, Homebrew, FFmpeg, Git, Python, dan Claude Code.
- Membuat kunci API di kie.ai dan OpenRouter, lalu menyimpannya dengan aman di file `.env`.
- Menjalankan `vg doctor` dan membaca hasilnya: `ok`, `warn`, `FAIL`.

## Kenapa ini penting

Semua pelajaran praktik berjalan di atas persiapan ini. Kalau satu alat hilang, pekerjaan macet di tengah jalan, sering di tahap edit, saat kamu sudah capek. Lebih baik semuanya beres sekarang. `vg doctor` yang memastikannya.

Yang kamu butuhkan: sebuah Mac, internet, dan sedikit saldo di kie.ai dan OpenRouter. Kenapa Mac? *Renderer* (program penggambar) caption dan grafis di alat ini memakai Swift, bahasa pemrograman buatan Apple.

## Langkah 1 · Kenalan dengan Terminal

*Terminal* adalah aplikasi Mac untuk memberi perintah dengan mengetik, bukan mengklik. Buka dengan Cmd + Spasi, ketik "Terminal", lalu Enter.

Caranya selalu sama: ketik perintah, tekan Enter, baca hasilnya. Coba ini, satu per satu:

```bash
pwd
ls
cd Documents
```

- `pwd` menunjukkan kamu sedang berada di folder mana.
- `ls` menampilkan isi folder itu.
- `cd Documents` masuk ke folder Documents. `cd ..` naik satu folder.

Kebiasaan yang membantu:

- Salin-tempel perintah dari pelajaran ini (Cmd + C, lalu Cmd + V di Terminal). Lebih aman daripada mengetik ulang.
- Panah atas memanggil perintah sebelumnya. Ctrl + C menghentikan perintah yang sedang berjalan.
- Saat Terminal meminta *password* Mac-mu, huruf yang kamu ketik tidak terlihat sama sekali. Itu normal. Ketik saja, lalu Enter.

## Langkah 2 · Xcode Command Line Tools

Paket alat dasar dari Apple. Di dalamnya ada `swiftc` (untuk caption dan grafis), Git, dan Python.

```bash
xcode-select --install
```

Jendela kecil muncul. Klik Install dan tunggu sampai selesai. Kalau muncul pesan bahwa alat ini sudah terpasang, langsung lanjut.

## Langkah 3 · Homebrew dan FFmpeg

*Homebrew* adalah "toko aplikasi" untuk Terminal: memasang program cukup dengan satu perintah. Buka https://brew.sh, salin perintah instalasi yang tertulis di halaman itu, tempel di Terminal, lalu Enter. Di akhir, Homebrew bisa menampilkan bagian *Next steps* berisi beberapa perintah. Jalankan juga, persis seperti tertulis.

Lalu pasang *FFmpeg*, program pengolah video dan audio untuk animatic dan edit final:

```bash
brew install ffmpeg
```

## Langkah 4 · Cek Git dan Python

*Git* mengunduh folder proyek dan mencatat versinya. *Python* adalah bahasa pemrograman yang menjalankan alat vg. Keduanya biasanya sudah ikut Xcode Command Line Tools. Cek:

```bash
git --version
python3 --version
```

Kalau keduanya menampilkan nomor versi, beres. Python harus 3.9 atau lebih baru, misalnya `Python 3.9.6`. Kalau `git` tidak ditemukan, jalankan `brew install git`. Kalau Python lebih lama dari 3.9, jalankan `brew install python`, lalu tutup dan buka lagi Terminal.

## Langkah 5 · Claude Code

Claude Code adalah agent yang nanti kamu ajak bicara. Pasang dengan mengikuti panduan instalasi resmi Claude Code dari Anthropic, termasuk langkah masuk (*login*) ke akunmu dan cara membukanya di sebuah folder. Perintahnya sengaja tidak ditulis di sini, karena bisa berubah.

## Langkah 6 · Akun dan kunci API

*API key* (kunci API) adalah kata sandi panjang yang dipakai alat vg untuk memakai layanan atas namamu, dan menagih saldomu. Perlakukan seperti PIN ATM.

**kie.ai**, untuk gambar dan video, dibayar dengan kredit:

1. Buat akun di https://kie.ai dan isi saldo kredit.
2. Di https://kie.ai/api-key, buat kunci baru khusus untuk kelas ini.
3. Pasang batas kredit pada kunci itu, misalnya batas total. Ini pagar terakhir: kalau semua pengaman lain gagal, kunci itu tetap tidak bisa memakai lebih dari batasnya.

**OpenRouter**, untuk narasi dan musik, dibayar dalam dolar, beberapa sen per *take* (satu kali hasil):

1. Buat akun di https://openrouter.ai dan isi saldo sedikit. Untuk reel contoh, suara dan musik habis kurang dari US$0,50.
2. Buat kunci di https://openrouter.ai/keys.

Sebagian layanan hanya menampilkan kunci sekali. Jangan tutup halamannya sebelum kunci tersimpan di `.env` (langkah 8).

## Langkah 7 · Unduh folder kelas dan jalankan install

```bash
cd ~/Documents
git clone https://github.com/tansilandre/ai-videographer-kelas
cd ai-videographer-kelas
bash install.sh
```

`git clone` mengunduh seluruh folder kelas: alat, skill, pelajaran, dan studi kasus. Lalu `bash install.sh`:

- memeriksa Python, FFmpeg, dan swiftc;
- membuat file `.env` dari contohnya, `.env.example`, dan mengunci aksesnya supaya hanya akunmu yang bisa membacanya;
- menghubungkan folder `1_Skills/` supaya Claude Code bisa membaca skill-nya;
- terakhir menjalankan `vg doctor`.

Aman dijalankan ulang: `.env` yang sudah ada tidak disentuh.

## Langkah 8 · Isi kunci di .env (hanya kamu)

`.env` adalah file pengaturan rahasia. Namanya berawalan titik, jadi tersembunyi di Finder. Buka dengan TextEdit:

```bash
open -e .env
```

Cari dua baris ini. Tempel kuncimu tepat setelah tanda `=`, tanpa spasi dan tanpa tanda kutip:

```text
KIE_API_KEY=
OPENROUTER_API_KEY=
```

Simpan (Cmd + S), lalu tutup. Baris lain biarkan apa adanya. Pelajaran 05 menjelaskan artinya.

Tiga aturan yang tidak boleh dilanggar:

1. **Hanya kamu yang mengedit `.env`.** Agent hanya boleh memeriksanya lewat `vg doctor`. Kalau agent menawarkan untuk mengubahnya, tolak.
2. **Jangan pernah menempel kunci ke chat** dengan agent, ke prompt, ke grup, atau ke screenshot.
3. Kalau kunci sempat bocor, hapus kunci itu di halaman kunci kie.ai atau OpenRouter, lalu buat yang baru.

Folder kelas sudah diatur supaya `.env` tidak pernah ikut terunggah ke GitHub.

## Langkah 9 · Jalankan vg doctor

Alat vg dijalankan dengan Python, dari folder kelas:

```bash
python3 2_Tools/vg/vg.py doctor
```

Tidak ada perintah `vg` yang terpasang di komputermu. Jadi mulai sekarang, tulisan "vg doctor" di kelas ini adalah singkatan dari perintah lengkap di atas.

Setiap baris diawali satu dari tiga tanda:

- `ok`: beres.
- `warn`: peringatan. Bagian itu belum siap, tapi kamu masih bisa mulai. Baca alasannya.
- `FAIL`: gagal. Harus diperbaiki sebelum lanjut.

Contoh hasilnya setelah `bash install.sh`, sebelum kunci diisi:

```text
ok   python                 3.9.6
ok   ffmpeg                 /opt/homebrew/bin/ffmpeg
ok   ffprobe                /opt/homebrew/bin/ffprobe
warn ffmpeg libass          no (only needed for burned-in subtitles; see vg-setup)
ok   swiftc                 /usr/bin/swiftc
warn OPENROUTER_API_KEY     missing (only needed for `vg audio voice` and `vg audio music`)
ok   .env                   /Users/kamu/Documents/ai-videographer-kelas/.env
FAIL kie.ai                 KIE_API_KEY is empty. Open .env in the workspace root and set KIE_API_KEY=<your key>.
ok   budget                 VG_BUDGET_PROJECT=800  VG_MAX_PER_CALL=250
ok   image model            gpt-image-2 (live-tested)
ok   video model            veo-3-1-lite (live-tested)
ok   skills linked          /Users/kamu/Documents/ai-videographer-kelas/.claude/skills
```

Setelah kunci diisi, baris FAIL berganti menjadi `ok KIE_API_KEY set (value hidden)`, dan muncul baris `kie.ai balance` berisi saldo kreditmu. Kuncinya sendiri tidak pernah ditampilkan.

Targetnya: nol FAIL. `warn ffmpeg libass` boleh dibiarkan, karena hanya dipakai untuk cara cadangan membuat subtitle.

## Kalau ada FAIL

Baca dulu teks di belakang tandanya. Hampir selalu ia sudah menyebut cara memperbaikinya. Perbaiki satu hal, lalu jalankan `vg doctor` lagi.

| Baris | Artinya | Yang kamu lakukan |
|---|---|---|
| `FAIL python` | Python lebih lama dari 3.9 | `brew install python`, buka ulang Terminal |
| `FAIL ffmpeg` atau `ffprobe` | FFmpeg belum terpasang | `brew install ffmpeg` |
| `FAIL kie.ai ... KIE_API_KEY is empty` | kunci belum diisi | isi di `.env` (langkah 8) |
| `FAIL kie.ai ... 401 ... invalid API key` | kunci salah atau terpotong | salin ulang dari kie.ai; pastikan tidak ada spasi |
| `FAIL image model` atau `video model` | nama model di `.env` berubah | samakan lagi dengan `.env.example` |
| `warn swiftc` | Xcode Command Line Tools belum ada | `xcode-select --install` |
| `warn OPENROUTER_API_KEY` | kunci OpenRouter kosong | isi di `.env` |
| `warn .env permissions` | `.env` bisa dibaca pengguna lain | `chmod 600 .env` |
| `warn skills linked` | skill belum terhubung | `bash install.sh` |

Masih macet? Buka Claude Code di folder kelas dan tulis, misalnya: "vg doctor menunjukkan FAIL di baris kie.ai, bantu aku." Agent boleh menjalankan `vg doctor` sendiri dan menjelaskan hasilnya. Tapi yang mengubah isi `.env` tetap kamu, dan kuncinya tidak pernah masuk ke chat.

## Latihan kecil

Jalankan `vg doctor` sampai tidak ada FAIL. Salin hasilnya ke catatanmu (aman, kunci tidak pernah tampil). Di samping setiap baris `warn`, tulis dengan kata-katamu sendiri: perlu diperbaiki sekarang, atau boleh dibiarkan?

## Cek pemahaman

1. Kenapa kunci kie.ai tidak boleh ditempel ke chat, padahal agent-nya bekerja untukmu?
2. Hasil doctor-mu punya satu `warn ffmpeg libass` dan tidak ada FAIL. Boleh lanjut?
3. Alat menolak membuat gambar karena melewati `VG_BUDGET_PROJECT`. Siapa yang boleh menaikkan angka itu?

<details>
<summary>Lihat jawaban</summary>

1. Isi chat tercatat dan bisa terbawa ke tempat lain: riwayat, log, screenshot. Siapa pun yang memegang kunci bisa menghabiskan saldomu. Kunci hanya tinggal di `.env`.
2. Boleh. `libass` hanya untuk cara cadangan membuat subtitle. Yang wajib nol adalah FAIL.
3. Hanya kamu, dan hanya kalau kamu memang setuju. Agent tidak boleh mengubah `.env`; ia harus bertanya kepadamu.

</details>

## Ringkasan

- Di Terminal: ketik perintah, tekan Enter, baca hasilnya.
- Alat yang dipasang: Xcode Command Line Tools, Homebrew, FFmpeg, Git, Python 3.9+, dan Claude Code.
- Kunci kie.ai dan OpenRouter hanya tinggal di `.env`. Hanya kamu yang mengeditnya, dan kunci tidak pernah masuk ke chat.
- `vg doctor` adalah singkatan dari `python3 2_Tools/vg/vg.py doctor`. Targetnya nol FAIL.
- Kalau ada FAIL: baca teksnya, perbaiki satu hal, jalankan lagi.

Berikutnya: [Pelajaran 05 · Cara Kerja AI Videographer](Pelajaran_05_Cara_Kerja_Harness_v1.0.md)
