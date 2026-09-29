# Pelajaran 04 · Persiapan Alat

## Tujuan

- Membuka *Terminal* dan menjalankan perintah sederhana tanpa takut.
- Memasang semua alat. Dengan WorkBuddy, AI-nya yang memasang lewat `bash setup.sh`, dan kamu cukup mengklik. Dengan Claude Code, kamu memasang sendiri: Xcode Command Line Tools, Homebrew, FFmpeg, Git, dan Python.
- Membuat kunci API di kie.ai dan OpenRouter, lalu menyimpannya dengan aman lewat halaman **Setup AI Videographer** (atau langsung di file `.env`), bersama cara persetujuan `VG_APPROVAL_MODE=page`.
- Menjalankan `vg doctor` dan membaca hasilnya: `ok`, `warn`, `FAIL`.

## Kenapa ini penting

Semua pelajaran praktik berjalan di atas persiapan ini. Kalau satu alat hilang, pekerjaan macet di tengah jalan, sering di tahap edit, saat kamu sudah capek. Lebih baik semuanya beres sekarang. `vg doctor` yang memastikannya.

Yang kamu butuhkan: sebuah Mac, internet, dan sedikit saldo di kie.ai dan OpenRouter. Kalau kamu memakai WorkBuddy, otak agent-nya (model glm-5.3-flash) sudah ada di dalam WorkBuddy dan memakai kredit WorkBuddy-mu, jadi tidak perlu akun lain. Kenapa Mac? *Renderer* (program penggambar) caption dan grafis di alat ini memakai Swift, bahasa pemrograman buatan Apple.

## Dua jalan

Pilih satu:

- **WorkBuddy (workshop, paling mudah).** Baca Langkah 1, buat kunci di Langkah 5, lalu kerjakan Langkah 6. Di sana AI di WorkBuddy mengunduh folder kelas dan menjalankan `bash setup.sh`, yang mengerjakan Langkah 2, 3, 4 dan 7 untukmu. Langkah 8 menjelaskan halaman tempat kamu menempel kunci. Terakhir, Langkah 9.
- **Claude Code, atau memasang sendiri.** Kerjakan Langkah 1 sampai 9 berurutan.

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

## Langkah 5 · Akun dan kunci API

*API key* (kunci API) adalah kata sandi panjang yang dipakai alat vg untuk memakai layanan atas namamu, dan menagih saldomu. Perlakukan seperti PIN ATM.

**kie.ai**, untuk gambar dan video, dibayar dengan kredit:

1. Buat akun di https://kie.ai dan isi saldo kredit.
2. Di https://kie.ai/api-key, buat kunci baru khusus untuk kelas ini.
3. Pasang batas kredit pada kunci itu, misalnya batas total. Ini pagar terakhir: kalau semua pengaman lain gagal, kunci itu tetap tidak bisa memakai lebih dari batasnya.

**OpenRouter**, untuk narasi dan musik, dibayar dalam dolar, beberapa sen per *take* (satu kali hasil). Kunci ini boleh menyusul:

1. Buat akun di https://openrouter.ai dan isi saldo sedikit. Untuk reel contoh, suara dan musik habis kurang dari US$0,50.
2. Buat kunci di https://openrouter.ai/keys.

Sebagian layanan hanya menampilkan kunci sekali. Biarkan halamannya terbuka sampai kuncinya kamu tempel di halaman setup (Langkah 8).

## Langkah 6 · Agent: WorkBuddy dan Expert AI Videographer

Agent adalah AI yang nanti kamu ajak bicara (Pelajaran 02). Di workshop, agent kita punya tiga bagian:

- **WorkBuddy**, aplikasi agent desktop dari Tencent, di https://www.workbuddy.ai. Kamu masuk (*login*) dengan akun Google atau GitHub. Tampilannya tersedia dalam bahasa Indonesia.
- **Expert AI Videographer**, uraian tugas agent kita. Ia dipasang dari folder kelas.
- **glm-5.3-flash**, model yang cepat dan murah sebagai otaknya. Model ini sudah ada di WorkBuddy dan memakai kredit WorkBuddy-mu. Tidak perlu akun atau kunci lain.

Pasangnya tiga langkah. Pesan yang kamu kirim ke AI-nya tertulis di [Panduan WorkBuddy](../5_WorkBuddy/Panduan_WorkBuddy_v1.1.md). Salin persis dari sana.

1. **Pasang WorkBuddy.** Unduh dari https://www.workbuddy.ai, pindahkan ke folder Applications, buka, lalu masuk dengan Google atau GitHub. Di pemilih model, pilih **glm-5.3-flash**.
2. **Minta AI-nya memasang.** Di WorkBuddy, pilih folder kerja, misalnya folder baru `AI_Videographer` di Documents. Lalu kirim satu pesan dari Panduan. Pesan itu meminta AI-nya mengunduh folder kelas ke folder kerjamu dan menjalankan `bash setup.sh`. AI-nya bekerja sendiri. Kamu hanya perlu:
   - klik **izinkan** kalau WorkBuddy meminta izin menjalankan perintah;
   - klik **Install** kalau jendela Apple untuk Xcode Command Line Tools muncul, lalu bilang "jalankan setup lagi" setelah selesai;
   - kalau Homebrew belum ada, AI-nya memberimu satu baris untuk ditempel di app **Terminal** (Langkah 1), karena pemasangannya butuh password Mac-mu. Setelah selesai, bilang "jalankan setup lagi".
3. **Tempel kunci, lalu buka ulang.** Halaman **Setup AI Videographer** terbuka di browser. Tempel kunci dari Langkah 5 dan klik **Simpan** (Langkah 8 menjelaskan halaman ini). Lalu tutup WorkBuddy sepenuhnya (Cmd + Q), buka lagi, buka folder yang disebut di akhir setup, dan pilih Expert **AI Videographer**.

Apa yang dikerjakan `bash setup.sh`? Ia memeriksa Xcode Command Line Tools dan Python, memasang FFmpeg lewat Homebrew, menghubungkan skill, memasang Expert AI Videographer, lalu membuka halaman setup kalau kunci kie.ai belum ada. Jadi Langkah 2, 3, 4 dan 7 sudah dikerjakan untukmu. Skrip ini aman dijalankan ulang kapan saja.

Kredit WorkBuddy habis? Otaknya bisa dipanggil lewat *gateway* (pintu masuk ke banyak model dengan satu kunci) milikmu sendiri, misalnya SumoPod, dengan `bash 2_Tools/workbuddy/install_workbuddy.sh --add-models`. Ini cadangan, tidak wajib.

**Cara lain: Claude Code.** Claude Code adalah agent buatan Anthropic, dan semua pelajaran di kelas ini berjalan sama dengannya. Pasang dengan mengikuti panduan instalasi resmi Claude Code dari Anthropic, termasuk langkah masuk ke akunmu dan cara membukanya di sebuah folder. Perintahnya sengaja tidak ditulis di sini, karena bisa berubah. Setelah itu lanjut ke Langkah 7.

## Langkah 7 · Unduh folder kelas dan jalankan install

Memakai WorkBuddy? Langkah ini sudah dikerjakan AI-nya di Langkah 6. Lanjut ke Langkah 8.

```bash
cd ~/Documents
git clone https://github.com/tansilandre/ai-videographer-kelas
cd ai-videographer-kelas
bash install.sh
```

`git clone` mengunduh seluruh folder kelas: alat, skill, pelajaran, dan studi kasus. Lalu `bash install.sh`:

- memeriksa Python, FFmpeg, dan swiftc;
- membuat file `.env` dari contohnya, `.env.example`, dan mengunci aksesnya supaya hanya akunmu yang bisa membacanya;
- menghubungkan folder `1_Skills/` supaya agent, WorkBuddy atau Claude Code, bisa membaca skill-nya;
- terakhir menjalankan `vg doctor`.

Aman dijalankan ulang: `.env` yang sudah ada tidak disentuh.

## Langkah 8 · Simpan kunci di halaman setup (hanya kamu)

Kuncimu disimpan di `.env`, file pengaturan rahasia di folder kelas. Cara termudah mengisinya adalah halaman **Setup AI Videographer**, halaman kecil yang berjalan di komputermu sendiri. Di WorkBuddy, halaman ini terbuka sendiri di akhir `bash setup.sh` selama kunci kie.ai belum ada. Kapan saja kamu bisa membukanya lagi: bilang ke Expert "buka halaman setup", atau jalankan dari folder kelas:

```bash
python3 2_Tools/vg/vg.py setup
```

Di halaman itu:

1. Tempel kunci kie.ai. Kunci OpenRouter boleh menyusul.
2. Biarkan **Cara menyetujui** di pilihan **Klik di halaman review (disarankan)**.
3. Klik **Simpan**.

Halaman itu menulis kuncimu langsung ke `.env`, mengunci aksesnya supaya hanya akunmu yang bisa membacanya, lalu mengecek kunci kie.ai dengan membaca saldomu. Kalau berhasil, muncul **Tersimpan ✓** beserta saldo kreditmu. Kalau kuncinya salah, halaman itu mengatakannya. Salin ulang kuncinya dari kie.ai, buka lagi halaman setup, lalu tempel ulang.

Pilihan **Klik di halaman review** menulis `VG_APPROVAL_MODE=page` di `.env`. *Approval mode* adalah cara kamu menyetujui di tiga gerbang. Dengan `page`, ketiga gerbang adalah klikmu di halaman review, dan perintah persetujuan dari terminal selalu ditolak. Jadi agent tidak pernah bisa menyetujui untukmu.

**Cara lain: edit `.env` sendiri.** Namanya berawalan titik, jadi tersembunyi di Finder. Buka dengan TextEdit:

```bash
open -e .env
```

Cari dua baris ini. Tempel kuncimu tepat setelah tanda `=`, tanpa spasi dan tanpa tanda kutip:

```text
KIE_API_KEY=
OPENROUTER_API_KEY=
```

Cari juga baris `VG_APPROVAL_MODE=terminal`, lalu ganti `terminal` dengan `page`:

```text
VG_APPROVAL_MODE=page
```

Simpan (Cmd + S), lalu tutup. Baris lain biarkan apa adanya. Pelajaran 05 menjelaskan artinya.

Tiga aturan yang tidak boleh dilanggar:

1. **Hanya kamu yang mengisi `.env`**, lewat halaman setup atau dengan tangan. Agent hanya boleh memeriksanya lewat `vg doctor`, dan boleh membukakan halaman setup untukmu. Kalau agent menawarkan untuk mengubah `.env` sendiri, tolak.
2. **Jangan pernah menempel kunci ke chat** dengan agent, ke prompt, ke grup, atau ke screenshot. Tempat kunci hanya halaman setup atau `.env`.
3. Kalau kunci sempat bocor, hapus kunci itu di halaman kunci kie.ai atau OpenRouter, lalu buat yang baru.

Folder kelas sudah diatur supaya `.env` tidak pernah ikut terunggah ke GitHub.

## Langkah 9 · Jalankan vg doctor

Di WorkBuddy, cara termudah adalah klik quick prompt **Cek setup**. Expert menjalankan doctor dan menjelaskan hasilnya.

Kamu juga bisa menjalankannya sendiri. Alat vg dijalankan dengan Python, dari folder kelas (di WorkBuddy: folder yang disebut di akhir setup):

```bash
python3 2_Tools/vg/vg.py doctor
```

Tidak ada perintah `vg` yang terpasang di komputermu. Jadi mulai sekarang, tulisan "vg doctor" di kelas ini adalah singkatan dari perintah lengkap di atas.

Setiap baris diawali satu dari tiga tanda:

- `ok`: beres.
- `warn`: peringatan. Bagian itu belum siap, tapi kamu masih bisa mulai. Baca alasannya.
- `FAIL`: gagal. Harus diperbaiki sebelum lanjut.

Contoh hasilnya setelah `bash install.sh` (atau `bash setup.sh`), sebelum kunci diisi:

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
ok   approval mode          terminal (the human types a code in their own terminal)
ok   skills (Claude Code)   /Users/kamu/Documents/ai-videographer-kelas/.claude/skills
ok   skills (WorkBuddy)     /Users/kamu/Documents/ai-videographer-kelas/.codebuddy/skills
```

Setelah kunci diisi, baris FAIL berganti menjadi `ok KIE_API_KEY set (value hidden)`, dan muncul baris `kie.ai balance` berisi saldo kreditmu. Kuncinya sendiri tidak pernah ditampilkan.

Setelah kamu klik **Simpan** di halaman setup dengan pilihan **Klik di halaman review** (atau menulis `VG_APPROVAL_MODE=page` sendiri), baris approval mode berubah menjadi `ok approval mode page (the human clicks Approve on the review page)`. Dua baris `skills` menunjukkan skill sudah terhubung untuk Claude Code dan untuk WorkBuddy. Untuk workshop, pastikan ada `ok skills (WorkBuddy)`.

Targetnya: nol FAIL. `warn ffmpeg libass` boleh dibiarkan, karena hanya dipakai untuk cara cadangan membuat subtitle.

## Kalau ada FAIL

Baca dulu teks di belakang tandanya. Hampir selalu ia sudah menyebut cara memperbaikinya. Perbaiki satu hal, lalu jalankan `vg doctor` lagi.

| Baris | Artinya | Yang kamu lakukan |
|---|---|---|
| `FAIL python` | Python lebih lama dari 3.9 | `brew install python`, buka ulang Terminal |
| `FAIL ffmpeg` atau `ffprobe` | FFmpeg belum terpasang | `bash setup.sh` lagi (di WorkBuddy: bilang "jalankan setup lagi"), atau `brew install ffmpeg` |
| `FAIL kie.ai ... KIE_API_KEY is empty` | kunci belum diisi | tempel di halaman setup (Langkah 8) |
| `FAIL kie.ai ... 401 ... invalid API key` | kunci salah atau terpotong | salin ulang dari kie.ai dan tempel lagi di halaman setup; pastikan tidak ada spasi |
| `FAIL image model` atau `video model` | nama model di `.env` berubah | samakan lagi dengan `.env.example` |
| `warn swiftc` | Xcode Command Line Tools belum ada | `xcode-select --install` |
| `warn OPENROUTER_API_KEY` | kunci OpenRouter kosong | tempel di halaman setup |
| `warn .env permissions` | `.env` bisa dibaca pengguna lain | `chmod 600 .env` |
| `warn skills (WorkBuddy)` atau `skills (Claude Code)` | skill belum terhubung | `bash setup.sh` (WorkBuddy) atau `bash install.sh` |
| `warn approval mode ... chat` | agent boleh menyetujui sendiri, cara yang paling lemah | buka halaman setup, pilih **Klik di halaman review**, lalu **Simpan** |
| `FAIL approval mode` | nilainya salah ketik | simpan lagi lewat halaman setup, atau tulis persis `VG_APPROVAL_MODE=page` di `.env` |

Masih macet? Tanya agent-mu di folder kelas (Expert AI Videographer di WorkBuddy, atau Claude Code), misalnya: "vg doctor menunjukkan FAIL di baris kie.ai, bantu aku." Agent boleh menjalankan `vg doctor` sendiri, menjelaskan hasilnya, dan membukakan halaman setup. Tapi yang menempel kunci tetap kamu, dan kuncinya tidak pernah masuk ke chat.

## Latihan kecil

Jalankan `vg doctor` (atau klik **Cek setup** di WorkBuddy) sampai tidak ada FAIL, dan sampai ada baris `ok approval mode page` dan `ok skills (WorkBuddy)`. Salin hasilnya ke catatanmu (aman, kunci tidak pernah tampil). Di samping setiap baris `warn`, tulis dengan kata-katamu sendiri: perlu diperbaiki sekarang, atau boleh dibiarkan?

## Cek pemahaman

1. Kenapa kunci kie.ai tidak boleh ditempel ke chat, padahal agent-nya bekerja untukmu?
2. Hasil doctor-mu punya satu `warn ffmpeg libass` dan tidak ada FAIL. Boleh lanjut?
3. Alat menolak membuat gambar karena melewati `VG_BUDGET_PROJECT`. Siapa yang boleh menaikkan angka itu?

<details>
<summary>Lihat jawaban</summary>

1. Isi chat tercatat dan bisa terbawa ke tempat lain: riwayat, log, screenshot. Siapa pun yang memegang kunci bisa menghabiskan saldomu. Kunci hanya ditempel di halaman setup, yang menyimpannya di `.env`.
2. Boleh. `libass` hanya untuk cara cadangan membuat subtitle. Yang wajib nol adalah FAIL.
3. Hanya kamu, dan hanya kalau kamu memang setuju. Agent tidak boleh mengubah `.env`; ia harus bertanya kepadamu.

</details>

## Ringkasan

- Di Terminal: ketik perintah, tekan Enter, baca hasilnya.
- WorkBuddy dipasang dalam tiga langkah: pasang WorkBuddy dan pilih glm-5.3-flash; kirim satu pesan supaya AI-nya menjalankan `bash setup.sh`; tempel kunci di halaman setup, lalu buka ulang WorkBuddy dan pilih Expert AI Videographer. Otaknya memakai kredit WorkBuddy-mu.
- Dengan Claude Code, kamu memasang sendiri: Xcode Command Line Tools, Homebrew, FFmpeg, Git, Python 3.9+, lalu `bash install.sh`.
- Kunci kie.ai dan OpenRouter ditempel di halaman setup (`vg setup`), yang menyimpannya di `.env`. Mengedit `.env` sendiri juga bisa. Hanya kamu yang mengisinya, dan kunci tidak pernah masuk ke chat.
- `VG_APPROVAL_MODE=page`: ketiga gerbang menjadi klikmu di halaman review. Halaman setup menuliskannya untukmu.
- `vg doctor` adalah singkatan dari `python3 2_Tools/vg/vg.py doctor`. Targetnya nol FAIL.
- Kalau ada FAIL: baca teksnya, perbaiki satu hal, jalankan lagi.

Berikutnya: [Pelajaran 05 · Cara Kerja AI Videographer](Pelajaran_05_Cara_Kerja_Harness_v1.2.md)
