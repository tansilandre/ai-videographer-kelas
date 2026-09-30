# Pelajaran 00 · Mulai di Sini

Selamat datang di Kelas AI Videographer. Di kelas ini kamu belajar membuat satu reel properti dari brief sampai video, dengan bantuan AI. Kamu tidak perlu pernah memakai terminal atau *coding agent* sebelumnya. Kita mulai dari nol.

## Tujuan

Setelah pelajaran ini, kamu bisa:

- menjelaskan isi kelas ini dan apa yang akan kamu buat;
- menemukan bahan kelas di folder repo dan tahu urutan belajarnya;
- menjelaskan aturan emas: gambar itu murah, video itu mahal dan butuh "ya" darimu;
- memperkirakan biaya satu reel seperti contoh.

## Kenapa ini penting

Membuat video dengan AI itu cepat, tapi juga gampang boros. Klip video yang salah tetap dibayar. Kalau dari awal kamu tahu arah kelas ini dan di mana uang keluar, kamu bisa belajar dengan tenang.

## Apa itu kelas ini

Kelas ini memakai AI Videographer, sebuah *harness* (rangka kerja: kumpulan instruksi dan alat yang membuat agent AI bekerja dengan urutan yang sama setiap kali). Semuanya ada di satu *repo* (folder proyek yang disimpan di GitHub):

https://github.com/tansilandre/ai-videographer-kelas

Kamu menyalin repo itu ke komputermu. Foldernya berisi alatnya sekaligus kelasnya.

Kamu tidak perlu menjalankan semua perintah sendiri. Kamu bicara ke *agent* (AI yang bisa membaca file dan menjalankan alat untukmu) dengan bahasa biasa. Di workshop kita memakai WorkBuddy, aplikasi agent di komputermu, dengan *Expert* (agent dengan uraian tugas khusus) bernama AI Videographer. Claude Code juga bisa dipakai, dengan cara yang sama. Misalnya: "Buat reel dari brief di 5_Projects/.../0_Source". Di WorkBuddy cukup klik **Buat video baru**, lalu Expert menanyakan lima hal tentang produkmu. Agent membaca *skill* (file instruksi cara kerja kita) di folder `1_Skills/`, lalu menjalankan alat bernama vg.

Kelas ini punya dua bagian:

- **Bagian 1, teori (Pelajaran 01–03):** apa itu AI dan cara ia belajar, model gambar, video, suara dan agent, lalu cara berpikir saat bekerja dengan AI.
- **Bagian 2, praktik (Pelajaran 04–13):** persiapan alat, tujuh tahap dari brief ke reel, dan kesalahan yang kami buat.

## Yang akan kamu buat

Satu reel properti vertikal 9:16, sekitar 28 detik. Detail teknisnya: 1080×1920 piksel, 30 *frame* (gambar diam) per detik, dan kekerasan suara sekitar −14 LUFS (*LUFS*: satuan untuk mengukur seberapa keras suara terdengar).

Contohnya reel "Tebak Harga". Kliennya Rumah Kita Realty, agen properti fiktif. Produknya Cluster Aster di Kota Harapan, kota fiktif. Presenternya Rani, orang yang dibuat AI dari nol, bukan orang asli.

<p>
<img src="../2_Studi_Kasus/Tebak_Harga/1_Gambar/Frame_Hook.jpg" width="220" alt="Hook: Rani di mobil dengan judul TEBAK HARGANYA?">
<img src="../2_Studi_Kasus/Tebak_Harga/1_Gambar/Frame_Petunjuk_3.jpg" width="220" alt="Petunjuk 3: depan rumah dengan label SMART LOCK, SOLAR WATER HEATER, 3 TITIK CCTV">
<img src="../2_Studi_Kasus/Tebak_Harga/1_Gambar/Frame_Harga.jpg" width="220" alt="Jawaban: MULAI 1,3M-AN* dengan catatan S&K berlaku">
</p>

Reel ini punya empat bagian yang akan kamu pelajari cara membuatnya:

- narasi dan musik;
- *caption* (teks ucapan di layar) yang menyala per kata;
- judul, peta dan transisi;
- klip AI yang bergerak.

Formatnya tebak harga. Ada janji di detik pertama ("Tebak harga rumah ini"), tiga petunjuk, penundaan, lalu jawaban harga. Jawaban itu datang bersama flash putih, bunyi ding, dan *drop* musik (saat musik tiba-tiba penuh setelah jeda singkat).

**Catatan penting.** Di reel contoh, rumahnya gambar AI karena klien dan proyeknya fiktif. Di proyek nyata, rumah yang dijual selalu foto asli dari klien, dan hanya kameranya yang bergerak.

Mau lihat hasilnya? Tonton [animatic reel contoh](../2_Studi_Kasus/Tebak_Harga/Contoh_Tebak_Harga_Animatic_v1.0.mp4). *Animatic* adalah seluruh reel dalam bentuk gambar diam, lengkap dengan suara, caption dan grafis, sebelum ada video.

## Peta bahan kelas

| Folder | Isi |
|---|---|
| `6_Kelas/1_Pelajaran/` | Pelajaran 00–13, termasuk yang sedang kamu baca |
| `6_Kelas/2_Studi_Kasus/Tebak_Harga/` | gambar, audio, rencana edit (`Edit_Spec.json`), naskah narasi (`Narasi.txt`) dan animatic reel contoh |
| `6_Kelas/3_Latihan/` | [brief latihan](../3_Latihan/Brief_Latihan_v1.2.md) dan [checklist per tahap](../3_Latihan/Checklist_Per_Tahap_v1.2.md) |
| `6_Kelas/4_Deck/` | slide kelas (.pptx dan .pdf), urutannya sama dengan pelajaran |
| `6_Kelas/5_WorkBuddy/` | [panduan WorkBuddy](../5_WorkBuddy/Panduan_WorkBuddy_v1.2.md) untuk memasang dan memakai agent workshop, dan run-sheet untuk fasilitator |

## Cara memakai pelajaran

1. **Kerjakan berurutan.** Setiap pelajaran memakai yang sebelumnya.
2. **Bentuknya selalu sama:** Tujuan, Kenapa ini penting, isi, Latihan kecil, Cek pemahaman, Ringkasan. Jawab Cek pemahaman dulu, baru buka jawabannya.
3. **Bagian 1 bisa dibaca tanpa komputer.** Bagian 2 dikerjakan di depan komputer.
4. **Perintah ditulis di kotak abu-abu.** Salin persis. Kamu tidak perlu menghafalnya.

Alatnya dijalankan dari folder repo, di *terminal* (jendela tempat kamu mengetik perintah ke komputer). Contohnya:

```bash
python3 2_Tools/vg/vg.py doctor
```

Perintah `doctor` memeriksa apakah semua alat dan kunci sudah siap. Di pelajaran berikutnya kami kadang menulisnya singkat: `vg doctor`. Itu hanya singkatan untuk `python3 2_Tools/vg/vg.py doctor`. Tidak ada perintah bernama `vg` di komputermu, jadi yang kamu ketik selalu versi lengkapnya.

Instalasi dijelaskan langkah demi langkah di Pelajaran 04. Dengan WorkBuddy, AI-nya yang memasang: kamu cukup mengklik, lalu menempel kunci di halaman setup. Kalau nanti macet, jalankan perintah di atas dan baca baris yang bertanda FAIL.

## Aturan emas: gambar itu murah, video itu mahal

Kalimat ini yang paling penting di seluruh kelas. Memperbaiki gambar itu murah dan cepat. Memperbaiki video itu mahal dan lambat.

- **Gambar:** gpt-image-2, 10 kredit per gambar 2K. Tidak perlu persetujuan. (*Kredit*: satuan bayar di kie.ai.)
- **Video:** Veo 3.1 Lite, 35 kredit per klip 8 detik di 1080p (30 kredit di 720p). Selalu butuh "ya" yang jelas darimu.

Jadi seluruh reel disetujui sebagai gambar dulu. Baru setelah itu gambarnya dibuat bergerak. Alur kerjanya tujuh tahap dengan tiga gerbang:

1. Brief dan shot list (*brief*: permintaan klien; *shot list*: daftar potongan gambar)
2. Look (**Gerbang 1**): satu tampilan untuk seluruh reel
3. Karakter dan frame
4. Audio
5. Animatic (**Gerbang 2**)
6. Video (**Gerbang 3**)
7. Edit final

*Gerbang* adalah titik tempat alat berhenti sampai kamu setuju. Tanpa persetujuanmu, langkah berikutnya ditolak. Di kelas ini, untuk menyetujui, kamu mengklik tombol di *halaman review*, halaman web yang berjalan di komputermu sendiri. Yang paling ketat adalah gerbang video, karena di situ uang keluar: setiap klip menunjukkan biayanya, dan halaman bertanya sekali lagi sebelum menyetujui. Agent tidak bisa menyetujui untukmu, karena perintah persetujuan dari terminal selalu ditolak. Ada juga cara lain: mengetik kode acak 4 digit di terminalmu sendiri. Pelajaran 04 dan 05 menjelaskan keduanya.

## Enam aturan keselamatan

1. **Hanya kamu yang mengubah file `.env`.** File ini menyimpan *API key* (kunci rahasia yang membuat alat bisa memakai akun kie.ai dan OpenRouter-mu). Kamu mengisinya lewat halaman setup di komputermu sendiri (Pelajaran 04).
2. **Jangan pernah menempel API key ke chat**, termasuk ke agent.
3. **Tidak ada video tanpa "ya" yang jelas darimu.**
4. **Mulai dari satu klip *pilot*** (klip percobaan pertama). Tonton dulu, baru putuskan sisanya.
5. **Satu persetujuan membayar tepat satu *take*** (satu kali percobaan membuat klip). Mengulang klip berarti "ya" baru dan persetujuan baru.
6. **Tugas yang *timeout* (waktu tunggunya habis) diambil dengan `vg resume`, tidak dikirim ulang.** Mengirim ulang bisa membayar dua kali untuk satu klip.

Kamu akan mempraktikkan semuanya mulai Pelajaran 04.

## Berapa biayanya

Ini hitungan nyata reel contoh:

| Bagian | Model | Biaya |
|---|---|---|
| Gambar | gpt-image-2 (kie.ai) | sekitar 70 kredit |
| Video | Veo 3.1 Lite (kie.ai) | 7 klip × 35 = 245 kredit (pilot 35, lalu 6 klip berikutnya 210) |
| Narasi | Gemini TTS (OpenRouter) | sekitar US$0,003 per take 20 detik |
| Musik | Lyria (OpenRouter) | sekitar US$0,04 per klip 30 detik |
| Suara dan musik, total | | di bawah US$0,50 |

Animatic, efek suara dan edit dibuat di komputermu sendiri, jadi gratis.

Kamu butuh dua akun: [kie.ai](https://kie.ai) untuk gambar dan video (dibayar dengan kredit), dan [OpenRouter](https://openrouter.ai) untuk suara dan musik. Saran kami: buat API key kie.ai khusus untuk kelas ini di https://kie.ai/api-key, lalu beri batas kredit total. Batas itu pagar terakhir kalau ada yang salah.

Biaya otak agent juga tidak termasuk dalam tabel ini. Di workshop, WorkBuddy memakai model glm-5.3-flash yang sudah ada di dalamnya, dan memakai kredit WorkBuddy-mu. Tidak perlu akun lain. Kalau kreditnya habis, ada cadangan yang tidak wajib: gateway milikmu sendiri seperti SumoPod (Pelajaran 04). Kalau kamu memakai Claude Code, ia butuh langganan Claude berbayar (misalnya paket Pro atau Max) atau kredit API Anthropic. Harga keduanya bisa berubah, jadi cek halaman harga resminya sebelum mulai.

## Berapa lama

Ini perkiraan kami, bukan angka pasti:

- **Bagian 1 (Dasar AI, Pelajaran 01–03):** sekitar 1,5–2 jam.
- **Persiapan alat (Pelajaran 04):** sekitar 1–2 jam kalau kamu baru pertama kali memakai terminal.
- **Satu reel seperti contoh (Pelajaran 05–12):** satu sampai dua hari kerja. Membuat gambar hanya butuh sekitar satu menit per gambar, dan satu klip video sekitar 2–3 menit. Sebagian besar waktumu habis untuk meninjau dan memperbaiki, dan memang di situlah pekerjaan terpentingnya.

Satu hal yang pasti: jangan buru-buru di gerbang. Persetujuan yang tergesa-gesa adalah cara paling cepat membuang kredit.

## Latihan kecil

Buka folder `6_Kelas/2_Studi_Kasus/Tebak_Harga/`. Tonton animatic contoh dua kali: sekali dengan suara, sekali tanpa suara. Catat tiga hal:

1. Di detik berapa harga pertama kali muncul di layar? Apakah muncul bersamaan dengan kata "mulai"?
2. Label apa saja yang kamu lihat? Perhatikan gambar rencana stasiun MRT dan layar harga.
3. Tanpa suara, apakah kamu masih paham ceritanya? Bagian apa yang membantumu?

Simpan catatanmu. Kamu akan memakainya lagi di Bagian 2.

## Cek pemahaman

1. Kenapa seluruh reel disetujui sebagai gambar dulu sebelum dibuat video?
2. Siapa yang menyetujui biaya video, dan kenapa bukan agent?
3. Di reel contoh rumahnya gambar AI. Bagaimana seharusnya di proyek nyata?

<details>
<summary>Lihat jawaban</summary>

1. Gambar murah (10 kredit) dan tidak perlu persetujuan, sedangkan satu klip video 35 kredit. Memperbaiki gambar itu murah dan cepat. Memperbaiki video itu mahal dan lambat. Jadi semua kesalahan dicari dan diperbaiki saat masih berupa gambar.
2. Kamu, dengan klik di halaman review, lalu konfirmasi sekali lagi. Klik itu rem supaya uang tidak keluar tanpa sengaja. Perintah persetujuan dari terminal selalu ditolak, jadi agent tidak bisa menyetujui untukmu. (Dengan cara lain, kamu mengetik kode acak 4 digit di terminalmu sendiri.)
3. Rumah yang dijual harus foto asli dari klien, dan hanya kameranya yang bergerak. Di contoh ini rumahnya AI hanya karena klien dan proyeknya fiktif.

</details>

## Ringkasan

- Kelas ini dimulai dengan teori (Pelajaran 01–03), lalu praktik (Pelajaran 04–13), dengan contoh reel Tebak Harga.
- Kamu membuat reel properti 9:16 sekitar 28 detik dengan bicara ke agent (di workshop: WorkBuddy) memakai bahasa biasa.
- Gambar murah (10 kredit). Video mahal (35 kredit per klip 8 detik) dan butuh "ya" darimu.
- Tujuh tahap, tiga gerbang. Di setiap gerbang, kamu yang mengklik setuju. Video selalu dimulai dari satu klip pilot.
- Reel contoh: gambar sekitar 70 kredit, video 245 kredit, suara dan musik di bawah US$0,50.

Berikutnya: [Pelajaran 01 · Apa Itu AI dan Cara Ia Belajar](Pelajaran_01_Apa_Itu_AI_v1.1.md)
