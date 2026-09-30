# Runsheet Workshop · AI Videographer di WorkBuddy

Untuk fasilitator. Peserta memakai laptop mereka sendiri (kebanyakan Windows, Mac juga bisa) dan mengikuti dua sesi: **Sesi 1** memasang, **Sesi 2** membuat reel pertama. Fasilitator menjalankan hal yang sama di layar besar, satu langkah di depan.

## Materi (semua di `6_Kelas/`, satu-satunya sumber)

| Materi | File | Untuk |
|---|---|---|
| Deck | `4_Deck/Kelas_AI_Videographer_Deck_v1.5.pptx` (+ `.pdf`) | layar besar |
| Pegangan workshop | `5_WorkBuddy/Pegangan_Workshop_v1.0.html` | dibagikan ke peserta |
| Pegangan AI Video Agent | `5_WorkBuddy/Pegangan_AI_Video_Agent_v1.0.html` | dibagikan ke peserta |
| Panduan WorkBuddy | `5_WorkBuddy/Panduan_WorkBuddy_v1.2.md` | versi teks dari pegangan workshop |
| Repo | https://github.com/tansilandre/ai-videographer-kelas | yang diunduh AI di laptop peserta |

Bagikan dua file pegangan HTML lewat grup chat atau Drive. Peserta membukanya di browser.

## Seminggu sebelumnya: PR peserta

Kirim ke peserta, bersama dua pegangan:

1. Daftar WorkBuddy lewat link undangan: https://workbuddy.ai/invite?code=ULLL7X4E
2. Buat akun kie.ai, isi saldo, buat kunci khusus kelas dengan batas kredit.
3. Buat akun OpenRouter dan kuncinya (boleh menyusul).

Bagian ini butuh email dan pembayaran, jadi AI tidak bisa mengerjakannya. Peserta yang datang tanpa PR akan tertinggal di Sesi 1.

## Sehari sebelumnya: laptop fasilitator

1. Pasang dengan satu pesan dari Panduan, di laptop yang akan tampil di layar. Pastikan **Cek setup** bersih.
2. Buat satu reel penuh lewat Expert. Di setiap gerbang, sebelum klik Approve, salin folder proyeknya sebagai cadangan:

```bash
cp -R 5_Projects/NAMA_PROYEK 5_Projects/NAMA_PROYEK_C1
```

| Cadangan | Isi | Dipakai untuk |
|---|---|---|
| C1 | look sudah dibuat | melompati 10–15 menit menulis rencana |
| C2 | animatic sudah jadi | Gerbang 2 |
| C3 | reel disetujui, belum ada video | Gerbang 3 |
| C4 | reel final | pembuka, dan cadangan kalau internet mati |

Di salinan proyek, persetujuan harus diklik ulang. Itu gratis, dan bagus untuk demo.

3. Nyalakan *Do Not Disturb*, besarkan font, siapkan hotspot HP.

## Sesi 1 · Pasang (±75 menit)

| Waktu | Di layar | Peserta |
|---|---|---|
| 0:00 | putar reel final (C4) | menonton |
| 0:05 | deck Bagian 1: model = otak, WorkBuddy = badan, Expert = uraian tugas | menonton |
| 0:25 | buka WorkBuddy, pilih glm-5.3-flash, kirim pesan pasang (Windows atau Mac) | melakukan hal yang sama |
| 0:35 | izinkan perintah, klik Yes/Install saat diminta | fasilitator keliling membantu |
| 0:55 | halaman setup: tempel kunci, Simpan | tempel kunci sendiri, **tidak pernah di chat** |
| 1:05 | tutup dan buka lagi WorkBuddy, pilih Expert, klik **Cek setup** | selesai kalau cek setup bersih |

Masalah yang paling sering muncul ada di tabel **Kalau macet** di Panduan: SmartScreen, "allow this app", `winget`, Homebrew, `python3` di Windows.

## Sesi 2 · Reel pertama (±90 menit)

| Waktu | Di layar | Peserta |
|---|---|---|
| 0:00 | klik **Buat video baru**, jawab lima pertanyaan | melakukan hal yang sama, dengan properti atau produk mereka sendiri |
| 0:15 | selagi Expert berpikir, jelaskan format tebak harga dengan deck | menunggu rencana |
| 0:30 | Gerbang 1: halaman review, look | klik Approve look, atau tulis catatan dan Done |
| 0:50 | Gerbang 2: buka C2, tonton animatic, klik **Approve reel** | menyusul di proyek sendiri, atau ikut menonton |
| 1:05 | Gerbang 3: buka C3, bagian Video, klik satu pilot | boleh klik satu pilot (35 kredit dari saldo sendiri) |
| 1:20 | tonton pilot, lalu putar C4 | link repo dan Panduan untuk dilanjutkan di rumah |

## Kalimat di tiap gerbang

- **Look:** "Kalau gayanya salah, semua gambar setelahnya ikut salah. Jadi manusia yang memutuskan, dengan satu klik."
- **Reel:** "Ini seluruh video sebagai gambar diam. Kita perbaiki di sini, sebelum bayar video."
- **Video:** "Satu klik, satu klip, 35 kredit. Mulai dari satu pilot."

## Rencana B

| Masalah | Tindakan |
|---|---|
| Expert keluar jalur | bilang: "Jalankan vg next dan kerjakan persis yang tertulis." |
| glm-5.3-flash lambat | lanjut dengan cadangan berikutnya di layar; peserta menyusul di rumah |
| Antrean kie.ai lambat | lanjut dengan cadangan berikutnya. Klip yang sedang dibuat bisa diambil nanti dengan "vg resume" |
| Laptop peserta gagal pasang | pasangkan dengan peserta sebelahnya; lanjutkan di rumah dengan Panduan |
| Internet mati | putar C4 dan animatic dari file lokal |
