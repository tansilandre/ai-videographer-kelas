# Pelajaran 11 · Prompt Video dan Gerbang Biaya

## Tujuan

Setelah pelajaran ini kamu bisa:

- membaca prompt video dan menilai apakah ia hanya menjelaskan gerakan;
- menjelaskan kenapa tidak ada orang yang bicara di klip;
- membaca biaya per klip di bagian Video halaman review dan melewati Gerbang 3 dengan aman;
- memulai dari satu klip pilot, lalu memeriksa setiap klip yang jadi.

## Kenapa ini penting

Ini tahap paling mahal. Satu gambar 10 kredit. Satu klip video Veo 3.1 Lite 8 detik di 1080p 35 kredit (30 kredit di 720p). Semua yang sebelumnya sudah kamu setujui sebagai gambar: look di Gerbang 1, seluruh reel di Gerbang 2. Sekarang kita hanya menambahkan gerak. Kesalahan di tahap ini dibayar dengan kredit, jadi kita bergerak pelan dan hati-hati.

## Prompt video: hanya gerakan

Frame pertama sudah membawa look: wajah Rani, rumahnya, cahayanya, warnanya. Karena itu *prompt* video (instruksi tertulis untuk model) tidak menggambarkan ulang isi gambar. Kalau prompt menjelaskan wajah atau rumah lagi, model punya dua deskripsi yang saling bersaing, lalu hasilnya melenceng.

Prompt video cukup menjawab empat hal:

1. **Satu gerakan kamera**, dengan kecepatan, titik akhir, lalu diam sebentar (*hold*).
2. **Cahaya**, sama dengan look.
3. **Suara sekitar** (*ambience*): jalan yang tenang, burung, angin. Tidak ada yang bicara.
4. **Apa yang tidak boleh berubah** (*LOCKS*): rumahnya, wajahnya, garis tegak tetap tegak.

Ini contoh prompt dari deck, untuk shot depan rumah. Prompt ditulis dalam bahasa Inggris karena model paling paham bahasa itu.

> Slow push-in of about half a metre over 6 seconds toward the front door, eye height 1.5 m, verticals straight; eases out and holds. Bright afternoon sun from the left. AUDIO: quiet street, birds. Nobody speaks. LOCKS: the house stays exactly as in the first frame.

| Potongan prompt | Artinya |
|---|---|
| *Slow push-in of about half a metre over 6 seconds toward the front door* | satu gerakan: kamera maju setengah meter dalam 6 detik, menuju pintu |
| *eye height 1.5 m, verticals straight* | kamera setinggi mata, garis tegak rumah tetap lurus |
| *eases out and holds* | gerakan melambat, lalu diam di akhir |
| *Bright afternoon sun from the left* | cahaya sore dari kiri, sama dengan look |
| *AUDIO: quiet street, birds. Nobody speaks.* | hanya suara sekitar, tidak ada yang bicara |
| *LOCKS: the house stays exactly as in the first frame* | rumah tidak boleh berubah |

Perhatikan: semua kata bisa diukur. "Setengah meter", "6 detik", "dari kiri". Tidak ada kata seperti *cinematic*, *epic* atau *8K*. Kata-kata itu tidak bisa diukur, jadi model hanya menebak. Satu klip, satu gerakan kamera. Tidak ada teks yang diminta dari model; semua tulisan ditambahkan di edit.

Catatan penting: di proyek nyata, rumah yang dijual adalah foto asli dari klien, dan hanya kameranya yang bergerak. Di contoh kelas ini rumahnya gambar AI, karena klien dan proyeknya fiktif.

Agent menulis prompt ini ke kolom `video_prompt` di `1_Script/Shotlist.json`, lalu mengeceknya dengan `vg validate`. Kamu cukup membacanya di board.

## Tidak ada yang bicara di klip

Rani muncul di beberapa shot, tapi ia tidak bicara di klip. Untuk orang di klip, prompt menulis *mouth closed, not speaking*. Semua kata yang diucapkan datang dari narasi *voice-over* (suara narator di atas gambar) yang sudah kamu buat di Pelajaran 09.

Kenapa? *Lip-sync* (gerak bibir yang cocok dengan suara) adalah bagian AI video yang paling rapuh. Kalau suara lain ditempel di atas bibir yang bergerak, hasilnya terdengar seperti dubbing yang jelek. Kami pernah membuat kesalahan itu; ceritanya ada di Pelajaran 13. Musik juga tidak dibuat oleh model video. Musik ditambahkan di edit.

## Berapa biayanya?

Sebelum meminta persetujuan, agent menghitung biaya. Ingat, `vg` adalah singkatan dari `python3 2_Tools/vg/vg.py`. Perintah yang dijalankan agent:

```bash
python3 2_Tools/vg/vg.py estimate -p NAMA_PROYEK --stage video
```

Ganti `NAMA_PROYEK` dengan nama folder proyekmu di `5_Projects/`. Untuk reel contoh, hasilnya 7 klip:

| Biaya video reel ini | Kredit |
|---|---|
| 1 klip pilot | 35 |
| 6 klip berikutnya | 210 |
| Total | 245 |

Satu klip 8 detik bisa dipotong menjadi dua atau tiga potongan pendek di edit. Angka yang sama tampil di bagian **Video** halaman review, satu baris per klip.

## Gerbang 3, langkah demi langkah

Di kelas ini Gerbang 3 adalah klikmu di halaman review (`VG_APPROVAL_MODE=page`, Pelajaran 04).

1. **Agent membuka halaman review dan berhenti.** Ia mengirim tautannya di chat, dengan pesan seperti: "Video butuh kredit, jadi kamu yang memutuskan. Setujui klip pilot S01 (35 kredit) di bagian Video."
2. **Kamu membuka bagian Video.** Bagian ini baru terbuka setelah look dan reel disetujui. Di atasnya tertulis kredit yang sudah terpakai dari batas proyekmu (`VG_BUDGET_PROJECT`). Di bawahnya ada tabel: satu baris per klip, dengan nama shot, isinya, durasinya, dan biayanya dalam kredit.
3. **Kamu klik Approve di satu klip saja: klip pilot.** Tombolnya menyebut biayanya, misalnya **Approve · 35 credits**. Browser lalu bertanya sekali lagi: *Spend 35 credits on S01? This pays for one take of each clip.* (Pakai 35 kredit untuk S01? Ini membayar satu take untuk setiap klip.) Klik OK kalau kamu yakin, atau Cancel kalau ragu.
4. **Status klip berubah** menjadi *approved: the agent can make it now*. Klik **Done, back to the agent**, lalu bilang di chat bahwa kamu sudah menyetujui.
5. **Agent membuat klipnya**, hanya untuk shot yang baru disetujui. `vg next` memberinya perintah persis ini:

```bash
python3 2_Tools/vg/vg.py video -p NAMA_PROYEK --shots S01
```

Satu klik membayar satu take satu klip. Di mode `page`, perintah `vg approve video` dari agent selalu ditolak, jadi klikmu satu-satunya jalan. Klik dan konfirmasinya adalah rem terhadap persetujuan tanpa sengaja. Batas kerasnya tetap kunci kie.ai dengan batas kredit. Kalau alat menolak karena batas anggaran di `.env`, agent harus bertanya ke kamu. Hanya kamu yang boleh mengubah `.env`.

**Cara lain: mode terminal.** Agent memberimu perintah lengkap yang diawali `cd` ke folder kelasmu, kira-kira `python3 2_Tools/vg/vg.py approve video -p NAMA_PROYEK --shots S01 --confirm 35`. Kamu menjalankannya di Terminal-mu sendiri. Alat menampilkan tabel, lalu meminta kode acak 4 digit, misalnya `Type 4821 and press Enter to approve:`. Angka `--confirm` harus sama dengan total yang kamu setujui.

## Pilot dulu, lalu sisanya

Tonton klip pilot sebelum menyetujui yang lain. Apakah kamera bergerak seperti yang ditulis? Cahayanya cocok? Rumahnya tetap sama? Ada mulut yang bergerak?

Kalau pilotnya bagus, agent membuka halaman review lagi untuk sisanya: 6 klip, 210 kredit. Puas dengan pilot bukan berarti setuju untuk sisanya. Kamu menyetujui sisanya dengan klik baru: satu per satu, atau dengan tombol **Approve all not made · 210 credits**, yang juga meminta konfirmasi. Jangan klik tombol itu sebelum pilot ditonton. Setelah itu agent membuat klip yang sudah disetujui.

## Satu persetujuan, satu take

- Setiap persetujuan membayar tepat satu *take* (satu kali pembuatan) untuk satu shot.
- Klip yang gagal di *provider* (layanan yang menjalankan model, di sini kie.ai) tetap memakai persetujuannya. Tombol Approve muncul lagi di barisnya, dan mencoba lagi butuh klik baru.
- Membuat ulang klip yang sudah jadi memakai tombol **New take · 35** di barisnya. Tombol ini juga meminta konfirmasi, dan agent lalu menjalankan `video` dengan `--new-take`.
- Kalau frame, prompt atau durasi berubah setelah disetujui, persetujuannya batal. Minta lagi.
- Dua kegagalan yang sama berarti prompt atau gambarnya yang salah. Perbaiki itu. Jangan coba ketiga kali dengan cara yang sama.

## Kalau prosesnya terputus

Kadang pembuatan klip terlalu lama dan waktunya habis (*timeout*). Jangan kirim ulang, karena kamu bisa membayar dua kali. Ambil hasilnya dengan:

```bash
python3 2_Tools/vg/vg.py resume -p NAMA_PROYEK
```

Kalau `resume` mencetak baris `CHECK`, kamu yang membuka dashboard kie.ai untuk melihat apakah tugasnya ada. Agent akan menjelaskan langkah berikutnya.

## Tonton setiap klip

Status "success" dari provider belum berarti klipnya bagus. Tonton setiap klip seperti penonton:

- Wajah Rani tetap sama? Tangannya wajar?
- Kamera berhenti di tempat yang ditulis prompt?
- Cahaya dan warnanya cocok dengan shot sebelah?
- Ada yang bicara, atau tulisan aneh muncul?

Agent mencatat hasil pemeriksaan di `6_Edit/QC_Review.md`. Take yang gagal sering masih punya satu sampai tiga detik yang bagus. Edit bisa memakainya.

## Latihan kecil

Buka `6_Kelas/2_Studi_Kasus/Tebak_Harga/1_Gambar/Look_Rumah_Deret.jpg`. Tulis prompt video untuk gambar itu dalam empat bagian: satu gerakan kamera dengan durasi dan titik akhir, cahaya, suara sekitar dengan "Nobody speaks", dan LOCKS. Lalu cek: apakah semua katanya bisa diukur? Apakah ada kata yang menggambarkan ulang rumahnya? Terakhir, hitung biaya 3 klip di 1080p dan di 720p.

## Cek pemahaman

1. Kenapa prompt video tidak menggambarkan ulang wajah Rani atau rumahnya?
2. Kamu sudah bilang "ya" di chat. Kenapa agent masih memintamu mengklik di halaman review?
3. Klip pilot gagal di provider. Bolehkah agent langsung mencoba lagi?

<details>
<summary>Lihat jawaban</summary>

1. Frame pertama sudah membawa look. Dua deskripsi yang bersaing membuat model melenceng. Prompt hanya menjelaskan apa yang berubah: gerak, cahaya, suara, dan yang harus tetap.
2. Di mode `page`, hanya klik di halaman review yang menyetujui biaya video. Perintah `vg approve video` dari agent selalu ditolak. Di halaman itu kamu melihat biaya per klip dan mengonfirmasi sekali lagi, jadi uang tidak keluar tanpa sengaja.
3. Tidak. Klip yang gagal sudah memakai persetujuannya. Agent membuka halaman review lagi, dan kamu yang memutuskan: klik baru, dengan konfirmasi baru.

Hitungan di latihan kecil: 3 × 35 = 105 kredit di 1080p, 3 × 30 = 90 kredit di 720p.

</details>

## Ringkasan

- Prompt video hanya menjelaskan gerakan: satu gerakan kamera, cahaya, suara sekitar, dan apa yang tidak boleh berubah.
- Tidak ada yang bicara di klip. Suaranya dari narasi voice-over.
- Gerbang 3: di bagian Video halaman review, setiap klip menunjukkan biayanya. Kamu klik Approve, lalu konfirmasi sekali lagi. Agent tidak bisa menyetujui untukmu.
- Mulai dari satu klip pilot. Satu klik membayar tepat satu take; klip gagal atau diulang butuh klik baru.
- Waktu habis? `vg resume`, jangan kirim ulang. Lalu tonton setiap klip.

Berikutnya: [Pelajaran 12 · Edit Final dan Kirim](Pelajaran_12_Edit_Final_Dan_Kirim_v1.2.md)
