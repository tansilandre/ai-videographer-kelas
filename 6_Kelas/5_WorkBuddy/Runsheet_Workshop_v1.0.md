# Runsheet Workshop · AI Videographer di WorkBuddy

Untuk fasilitator. Formatnya: **fasilitator yang menjalankan, peserta menonton dan mengikuti**. Satu Mac di proyektor menjalankan semuanya secara nyata. Peserta membawa pulang repo dan [Panduan WorkBuddy](Panduan_WorkBuddy_v1.0.md) untuk mengulangnya sendiri.

## Prinsip panggung

- **Tunjukkan gerbangnya.** Momen paling berkesan adalah saat Expert berhenti dan menunggu klik manusia. Beri jeda di setiap gerbang dan jelaskan kenapa.
- **Jangan menunggu di depan penonton.** Model glm-5.3-flash butuh 10–15 menit untuk menulis rencana, dan satu klip video butuh 3–6 menit. Siapkan proyek cadangan di setiap tahap, lalu isi waktu tunggu dengan penjelasan.
- **Semua yang tampil harus fiktif atau sudah diizinkan.** Pakai studi kasus Rumah Kita Realty, atau brief fiktif baru. Reel klien asli hanya boleh ditampilkan kalau klien sudah setuju.

## H-3 · Siapkan akun dan saldo

| Cek | Target |
|---|---|
| Saldo kie.ai | minimal 300 kredit, dengan kunci khusus workshop yang diberi batas total |
| Saldo SumoPod | cukup untuk beberapa sesi. Satu sesi rencana di bawah US$0,10 |
| OpenRouter | ada saldo untuk narasi dan musik |
| WorkBuddy | versi terbaru, sudah masuk, tampilan bahasa Indonesia kalau perlu |
| Repo | `git pull` di folder `ai-videographer-kelas`, lalu jalankan installer lagi |

## H-1 · Gladi dan proyek cadangan

1. Jalankan `python3 2_Tools/vg/vg.py doctor`. Pastikan tidak ada `FAIL`, dan `approval mode` bernilai `page`.
2. Buat satu reel penuh dari brief yang akan dipakai di hari H, lewat Expert, sampai selesai.
3. Di setiap gerbang, sebelum menekan Approve, salin folder proyeknya sebagai cadangan:

```bash
cp -R 5_Projects/2026-10-01_Aster_Tebak_Harga 5_Projects/2026-10-01_Aster_Tebak_Harga_C1_Look
```

Siapkan empat cadangan:

| Cadangan | Isi | Dipakai untuk |
|---|---|---|
| C1 · Look | rencana selesai, style frame sudah dibuat | lompat melewati 10–15 menit menulis rencana |
| C2 · Reel | semua gambar dan animatic selesai | demo halaman review untuk reel |
| C3 · Video | reel disetujui, belum ada klip | demo klik pilot dan biayanya |
| C4 · Final | semua klip dan reel final | tontonan penutup, dan cadangan kalau internet mati |

Salinan proyek meminta persetujuan ulang. Alat mencatat folder tempat persetujuan diberikan, jadi di cadangan kamu harus klik Approve lagi. Itu gratis, dan malah bagus untuk demo.

4. Tutup semua aplikasi lain. Nyalakan *Do Not Disturb*. Besarkan font WorkBuddy dan browser supaya terbaca dari belakang ruangan.
5. Siapkan hotspot HP sebagai internet cadangan.

## Hari H · Susunan sesi (contoh 2 jam)

| Waktu | Bagian | Di layar | Catatan |
|---|---|---|---|
| 0:00 | Pembuka | reel final (C4) diputar penuh | "Dua jam lagi kalian tahu cara membuat ini." |
| 0:05 | Dasar AI | deck Bagian 1 | model = otak, agent = badan, Expert = uraian tugas |
| 0:25 | Tur alat | WorkBuddy, folder repo, Expert AI Videographer, pemilih model glm-5.3-flash, `vg doctor` | tunjukkan baris `approval mode page` |
| 0:35 | Live 1 · Brief ke rencana | ketik brief ke Expert. Selagi ia berpikir, jelaskan struktur tebak harga di deck | rencananya belum selesai? Lanjutkan dengan C1 |
| 0:50 | Live 2 · Gerbang 1, look | Expert mengirim link review, lalu peserta memberi suara: approve atau catatan? | tulis satu catatan sungguhan, klik Done, tunjukkan Expert membuat ulang gambarnya |
| 1:05 | Istirahat dan tanya jawab | | |
| 1:15 | Live 3 · Gerbang 2, reel | buka C2, tonton animatic di halaman review, klik Approve reel | tekankan: seluruh reel disetujui sebagai gambar dulu, karena gambar murah |
| 1:30 | Live 4 · Gerbang 3, video | buka C3, bagian Video: biaya per klip, klik pilot, dialog konfirmasi | sambil menunggu 3–6 menit, tanya: "Kalau salah, kerugiannya berapa?" |
| 1:45 | Live 5 · Final | tonton pilot, lalu buka C4 dan jalankan `vg edit final` (atau putar hasilnya) | tunjukkan file di `99_Output/` |
| 1:55 | Bawa pulang | link repo dan Panduan WorkBuddy | peserta mengulang di rumah dengan kunci mereka sendiri |

Waktu bisa digeser. Bagian yang tidak boleh dipotong: tiga gerbang.

## Anggaran hari H

| Pos | Kredit kie.ai |
|---|---|
| Style frame dan satu kali perbaikan look | sekitar 30 |
| Satu pilot video Veo 3.1 Lite | 35 |
| Cadangan untuk hal tak terduga | 50 |
| **Total di panggung** | **sekitar 115** |

Semua yang lain sudah dibuat di gladi (H-1).

## Kalimat di setiap gerbang

- **Gerbang 1 (look):** "Ini gaya seluruh video: satu tempat, satu jam, satu cahaya. Kalau gaya ini salah, semua gambar setelahnya ikut salah. Jadi manusia yang memutuskan, dengan satu klik."
- **Gerbang 2 (reel):** "Ini seluruh video dalam bentuk gambar diam, lengkap dengan suara dan tulisan. Gambar murah, video mahal. Kita perbaiki di sini, bukan setelah bayar video."
- **Gerbang 3 (video):** "Lihat biayanya: 35 kredit untuk satu klip. Satu klik membayar satu take. Kita mulai dengan satu pilot dulu."
- **Saat agent ditolak:** "Lihat, agent tidak bisa menyetujui sendiri. Alatnya yang menolak, bukan karena agent-nya sopan."

## Rencana B

| Masalah | Tindakan |
|---|---|
| glm-5.3-flash lambat atau error | ganti model ke MiniMax-M3.1-Flash-Preview di pemilih model, lalu bilang "lanjut" |
| SumoPod tidak bisa diakses | pakai gateway lain yang menyediakan model yang sama (misalnya OpenRouter `z-ai/glm-5.3-flash`): tambahkan di Settings → Models |
| Expert keluar jalur | bilang: "Jalankan vg next dan kerjakan persis yang tertulis." |
| Antrean kie.ai lambat | lanjut ke cadangan berikutnya. Klip yang sedang dibuat bisa diambil nanti dengan `vg resume` |
| Internet mati | putar C4 dan animatic dari file lokal. Jelaskan gerbang dengan halaman review cadangan (tetap jalan di Mac tanpa internet) |
| WorkBuddy macet | Cmd + Q lalu buka lagi. Proyeknya aman: semua tercatat di folder proyek, bukan di chat |

## Setelah sesi

- Bagikan link repo: https://github.com/tansilandre/ai-videographer-kelas
- Minta peserta mulai dari [Pelajaran 00](../1_Pelajaran/Pelajaran_00_Mulai_Di_Sini_v1.1.md) dan Panduan WorkBuddy.
- Cabut atau turunkan batas kunci kie.ai khusus workshop.
