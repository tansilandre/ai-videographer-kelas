# Pelajaran 12 · Edit Final dan Kirim

## Tujuan

Setelah pelajaran ini kamu bisa:

- membuat draft, lalu versi final, dengan `vg edit final`;
- menemukan hasilnya di `99_Output/`, lengkap dengan file `.srt`;
- memeriksa reel dengan daftar cek sebelum dikirim;
- menamai versi tanpa pernah menimpa versi yang sudah dikirim.

## Kenapa ini penting

Klien hanya melihat satu file: hasil akhirnya. Mereka tidak melihat shot list, look, atau animatic. Satu caption yang muncul terlalu cepat bisa membocorkan harga sebelum waktunya. Gambar yang diam 2,5 detik terlihat seperti video rusak. Tahap ini gratis dan dibuat di komputermu sendiri, jadi luangkan waktu untuk memeriksa.

## Apa yang dikerjakan `vg edit final`

Perintah ini membaca rencana edit, `6_Edit/Edit_Spec.json`. Itu rencana yang sama yang sudah kamu setujui lewat animatic di Gerbang 2. Bedanya, di animatic setiap shot AI tampil sebagai frame pertamanya. Di edit final, klip videonya yang dipakai.

Alat ini lalu:

- memotong klip sesuai waktu di rencana edit;
- memasang narasi, musik, dan efek suara;
- mengecilkan musik saat narasi bicara (*ducking*);
- menampilkan *caption* (teks yang diucapkan, muncul di layar) kata demi kata;
- menggambar grafis: judul, peta, callout, penghitung, dan end card;
- memberi satu *grade* (perlakuan warna yang sama) ke semua gambar;
- menyamakan kekerasan suara ke sekitar −14 *LUFS* (satuan kekerasan suara yang dipakai platform video).

Semuanya dikerjakan di komputermu, tanpa kredit. Grafis dan caption digambar oleh program kecil berbahasa Swift, karena itu kelas ini butuh Mac.

## Langkah 1: draft

Ingat, `vg` adalah singkatan dari `python3 2_Tools/vg/vg.py`. Minta agent membuat draft, atau jalankan sendiri:

```bash
python3 2_Tools/vg/vg.py edit final -p NAMA_PROYEK --draft
```

Ganti `NAMA_PROYEK` dengan nama folder proyekmu. Dengan `--draft`, hasilnya masuk ke `6_Edit/` sebagai draft bernomor, misalnya `Draft_Contoh_Tebak_Harga_v1.0_d1.mp4`. Draft berikutnya menjadi `_d2`, `_d3`, dan seterusnya. Buat draft sebanyak yang kamu perlu. Tonton, tulis catatan, minta agent memperbaiki, lalu buat draft lagi.

## Langkah 2: versi final

Kalau draft terakhir sudah lolos semua cek di bawah, buat versi finalnya:

```bash
python3 2_Tools/vg/vg.py edit final -p NAMA_PROYEK
```

Tanpa `--draft`, hasilnya masuk ke `99_Output/`. Nama filenya diambil dari kolom `output` di rencana edit. Untuk reel contoh: `Contoh_Tebak_Harga_v1.0.mp4`.

Di sebelahnya ada file dengan nama sama berakhiran `.srt`. File `.srt` adalah file teks berisi caption beserta waktunya. Banyak platform video bisa memakainya sebagai subtitle.

## Daftar cek sebelum kirim

Tonton reelnya dari awal sampai akhir, dengan suara, seperti penonton. Lalu periksa satu per satu. Pemeriksaan ini disebut *QC* (*quality control*, pemeriksaan mutu).

**1. Caption tidak pernah mendahului kata yang diucapkan.**
Paling penting di momen harga. Di reel contoh, narasi berkata "Harganya..." lalu jeda. Caption harus menampilkan "HARGANYA..." saja. Tulisan "MULAI 1,3M-AN!" baru boleh muncul saat kata itu diucapkan. Alat sekarang selalu memutus caption di tanda jeda (. , ? ! : …), supaya kata berikutnya tidak tampil lebih awal.

![Frame harga dari animatic contoh](../2_Studi_Kasus/Tebak_Harga/1_Gambar/Frame_Harga.jpg)

**2. Tidak ada gambar beku: jumlah frame = durasi × 30.**
Reel kita 30 *frame* (gambar diam) per detik. Jadi jumlah frame harus sama dengan durasi dikali 30. Animatic contoh berdurasi 27,9 detik dan punya 837 frame: 27,9 × 30 = 837. Cocok. Kalau jumlahnya kurang, ada bagian gambar yang hilang dan layar terlihat diam. Minta agent mengeceknya, atau coba sendiri pada animatic contoh. Jalankan dari folder kelas:

```bash
ffprobe -v error -select_streams v -count_frames -show_entries stream=nb_read_frames -of csv=p=0 6_Kelas/2_Studi_Kasus/Tebak_Harga/Contoh_Tebak_Harga_Animatic_v1.0.mp4
```

Hasilnya `837`. Untuk reelmu sendiri, ganti path di akhir dengan file di folder `99_Output/` proyekmu. *FFprobe* ikut terpasang bersama FFmpeg.

**3. Suara jelas di atas musik, sekitar −14 LUFS.**
Alat sudah menyamakan kekerasannya. Tugasmu mendengar. Apakah setiap kata narasi jelas? Apakah musik mengecil saat narasi terdengar? Apakah drop musik jatuh tepat di kata "mulai"? Apakah reel berakhir tepat saat musiknya berhenti, bukan di keheningan?

**4. Ada label kejujuran.**
Cari label "ILUSTRASI RENCANA" di render stasiun MRT. Cari "*S&K berlaku, dapat berubah." di bawah harga. Peta di reel contoh juga diberi tulisan "Peta ilustrasi, tidak berskala." Di proyek nyata, kalau jarak harus tepat, pakai peta asli dari klien. Rumah yang dijual juga harus foto asli klien. Di contoh kelas ini rumahnya gambar AI, karena klien dan proyeknya fiktif, dan end card menyebutnya.

**5. Teks tidak menutupi wajah.**
Periksa setiap shot Rani. Jauhkan teks juga dari bagian paling atas dan paling bawah layar, karena di situ tombol-tombol platform muncul.

**6. File berversi.**
Nama file mengikuti pola `Proyek_v1.0.mp4`. Versi pertama `v1.0`. Perubahan kecil menjadi `v1.1`. Perubahan besar menjadi `v2.0`.

## Jangan pernah menimpa versi yang sudah dikirim

Misalnya klien minta satu kata diganti setelah `v1.0` terkirim. Jangan buat ulang dengan nama yang sama. Minta agent mengganti kolom `output` menjadi `Contoh_Tebak_Harga_v1.1.mp4`, lalu jalankan edit final lagi.

Alat juga menjaga aturan ini. Kalau file dengan nama itu sudah ada di `99_Output/`, alat menolak dan memintamu memakai nama baru. Dengan begitu, kamu selalu tahu persis file mana yang sudah dilihat klien.

## Kirim

Yang kamu kirim adalah isi `99_Output/`: file `.mp4`, dan file `.srt` kalau platformnya membutuhkan. Folder ini hanya berisi hasil akhir yang siap dikirim. Draft tetap di `6_Edit/`.

Sebelum menekan kirim, tanya dirimu satu hal: kalau kamu melihat reel ini di media sosial, apakah kamu percaya pada harganya dan paham apa yang dijual? Kalau belum yakin, kembali ke daftar cek.

## Latihan kecil

Buka `6_Kelas/2_Studi_Kasus/Tebak_Harga/Contoh_Tebak_Harga_Animatic_v1.0.mp4`. Jalankan daftar cek di atas pada file itu. Catat detik saat caption "HARGANYA..." muncul, dan detik saat "MULAI 1,3M-AN!" muncul. Temukan label ILUSTRASI RENCANA dan S&K. Kalau kamu menemukan satu hal yang ingin diperbaiki, tulis juga di tahap mana perbaikannya paling murah.

## Cek pemahaman

1. Apa beda `vg edit final` dengan dan tanpa `--draft`?
2. Reel berdurasi 28 detik. Berapa jumlah frame yang seharusnya?
3. Klien minta revisi kecil setelah `Proyek_v1.0.mp4` dikirim. Apa nama file berikutnya, dan kenapa?

<details>
<summary>Lihat jawaban</summary>

1. Dengan `--draft`, hasilnya draft bernomor di `6_Edit/`, boleh dibuat berkali-kali. Tanpa `--draft`, hasilnya file final di `99_Output/` plus file `.srt`.
2. 28 × 30 = 840 frame. Kalau kurang, ada gambar yang hilang atau beku.
3. `Proyek_v1.1.mp4`. Versi yang sudah dikirim tidak pernah ditimpa, supaya jelas file mana yang sudah dilihat klien.

</details>

## Ringkasan

- `vg edit final --draft` untuk draft di `6_Edit/`, lalu `vg edit final` untuk hasil di `99_Output/` plus `.srt`.
- Edit final gratis dan lokal: klip, narasi, musik, efek, caption, grafis, satu grade, sekitar −14 LUFS.
- Cek sebelum kirim: caption tidak mendahului kata, jumlah frame = durasi × 30, suara jelas di atas musik, label ILUSTRASI RENCANA dan S&K, teks tidak menutupi wajah, nama berversi.
- Jangan pernah menimpa versi yang sudah dikirim. Revisi berarti nomor versi baru.

Berikutnya: [Pelajaran 13 · Kesalahan yang Kami Buat](Pelajaran_13_Kesalahan_Yang_Kami_Buat_v1.1.md)
