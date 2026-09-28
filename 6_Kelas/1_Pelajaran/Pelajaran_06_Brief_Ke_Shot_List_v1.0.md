# Pelajaran 06 · Dari Brief ke Shot List

## Tujuan

Setelah pelajaran ini kamu bisa:

- membaca *brief* (catatan permintaan dari klien) apa adanya, lalu memisahkan fakta, aturan, dan sumber gambar;
- menyusun *beat* sebelum memikirkan *shot*, dengan struktur tebak harga;
- memeriksa shot list yang ditulis agent: hook, janji, potongan, dan waktu tampil produk;
- mengerti apa yang ada di `1_Script/Shotlist.json` dan apa arti hasil `vg validate`.

## Kenapa ini penting

Shot list adalah rencana seluruh reel. Setiap gambar, suara, dan video nanti dibuat dari rencana ini. Memperbaikinya sekarang cukup dengan mengubah satu baris. Memperbaikinya setelah video jadi berarti membayar kredit lagi.

## Langkah 1 · Baca brief apa adanya

Kamu bicara ke agent dengan bahasa biasa, misalnya:

> Buat reel dari brief di 5_Projects/NAMA_PROYEK/0_Source

Folder `0_Source` berisi bahan asli dari klien. Isinya tidak pernah diubah.

Agent membaca brief kata demi kata. Untuk setiap bagian, ia mencari tiga hal:

1. Apa yang dilihat penonton.
2. Apa yang diucapkan atau ditulis di layar.
3. **Sumber gambarnya** (*source*): `ai` (dibuat AI), `real` (foto atau video asli dari klien), atau `mg` (*motion graphic*, grafis bergerak yang dibuat saat edit, misalnya peta).

Aturannya tegas: bagian yang ditandai `real` atau `mg` tidak boleh diam-diam diubah jadi `ai`, walaupun lebih mudah atau lebih murah. Klien sengaja menandainya begitu, supaya iklannya tidak berisi gambar karangan.

Reel contoh menjual rumah dua lantai di Cluster Aster, Kota Harapan: seberang mall besar, dua kilo ke tol, seribu unit terjual, harga mulai 1,3 M-an. Semua fakta ini harus datang dari klien dan dicek manusia, bukan ditebak AI (Pelajaran 01).

## Langkah 2 · Catat aturan klien

Semua batasan yang bukan shot masuk ke daftar `rules`: label wajib, catatan hukum, larangan. Agent wajib mematuhinya di setiap shot. Aturan reel contoh:

- Rencana infrastruktur selalu diberi label ILUSTRASI RENCANA.
- Harga selalu dengan tanda (*) dan "S&K berlaku, dapat berubah".
- Contoh kelas: semua nama fiktif, semua gambar dibuat AI.

Di proyek nyata hampir selalu ada satu aturan lagi: rumah yang dijual adalah foto asli dari klien, dan AI tidak pernah mengarang bangunannya. Kita bahas di Pelajaran 08.

## Langkah 3 · Beat dulu, baru shot

*Beat* adalah satu perubahan informasi atau emosi. Beat yang tidak mengubah apa pun hanya mengisi waktu, jadi dibuang. Reel contoh memakai format **tebak harga**: janji di detik pertama, tiga petunjuk, penundaan, lalu jawaban.

| Detik | Bagian | Isi |
|---|---|---|
| 0–2 | Hook | "Tebak harga rumah ini." |
| 2–9 | Petunjuk 1–2 | lokasi, jarak ke tol |
| 9–14 | Petunjuk 3 | fitur rumah |
| 14–21 | Tunda | bonus dan bukti |
| 21–24 | Jawaban | harga, dengan flash |
| 24–28 | Ajakan | DM untuk lihat langsung |

*Hook* adalah pembuka yang membuat orang berhenti menggulir layar. Jawaban harga harus muncul sebagai teks dan suara pada saat yang sama. Angka yang tertulis sebelum diucapkan terasa ceroboh, bukan menegangkan.

Satu tes sederhana: tulis satu kalimat yang bisa diulang penonton setelah menonton. Kalau kalimat itu butuh kata "dan" untuk dua hal berbeda, itu dua video.

## Langkah 4 · Satu beat, satu shot

*Shot* adalah satu potongan gambar tanpa putus. Biasanya satu beat jadi satu shot. Ini shot list reel contoh (*whip* adalah transisi kabur cepat saat pindah tempat):

| Shot | Detik | Yang terlihat | Teks di layar |
|---|---|---|---|
| S01 | 0–2,1 | Rani di mobilnya | TEBAK HARGANYA? |
| S02 | 2,1–3,55 | deretan rumah | RUMAH 2 LANTAI |
| S03 | 3,55–6,3 | foto udara, masuk dengan whip | PETUNJUK 1 SEBERANG MALL BESAR |
| S04 | 6,3–9,05 | peta, masuk dengan whip | PETUNJUK 2, 2 km ke tol |
| S05 | 9,05–14,2 | depan rumah | SMART LOCK, SOLAR WATER HEATER, 3 TITIK CCTV |
| S06 | 14,2–15,5 | Rani di boulevard | UDAH KETEBAK? |
| S07 | 15,5–18,45 | rencana stasiun MRT, whip | ILUSTRASI RENCANA |
| S08 | 18,45–20,45 | deretan rumah, angka naik | 1.000 UNIT TERJUAL |
| S09 | 20,45–21,75 | Rani; narasi: "Harganya..." | |
| S10 | 21,75–23,9 | depan rumah, flash putih + ding | MULAI 1,3M-AN*, *S&K berlaku, dapat berubah |
| S09B | 23,9–25,0 | Rani; narasi: "Mau lihat langsung?" | |
| S11 | 25,0–27,8 | kartu penutup | |

Rani adalah presenter yang dibuat AI dari nol. Ia tidak berbicara di klip; semua suara berasal dari narasi. Rumah di reel contoh juga dibuat AI, karena klien dan proyeknya fiktif. Di proyek nyata, rumahnya foto asli dari klien.

Aturan kerajinan yang dipakai agent saat menyusun tabel ini:

- **Hook dalam 2 detik.** Kata pertama sebelum detik 0,8, teks pertama paling lambat sekitar detik 0,5. Di reel contoh, judul TEBAK HARGANYA? muncul di detik 0,2.
- **Satu ide per shot.** Dua aksi dalam satu shot membingungkan model dan penonton.
- **Potong setiap 1,5–3 detik** untuk gambar rumah dan suasana. Lihat tabelnya: hanya S05 yang lebih dari 3 detik, dan di situ tiga *callout* (label penunjuk fitur) muncul satu per satu, jadi mata selalu dapat hal baru.
- **Jangan tiga potongan berturut-turut** dengan ukuran shot dan gerak kamera yang sama.
- **Produk harus cukup lama terlihat.** Untuk rumah, minimal 40% durasi. Di shot list ditulis `"product_share_min": 0.4` di bagian `format`.
- **Tutup dengan ajakan yang jelas** (*CTA*, *call to action*): di sini "DM Rumah Kita Realty".

## Langkah 5 · Janji harus ditepati

Setiap hook berjanji. "Tebak harga" berjanji bahwa harganya akan dijawab. Di versi pertama reel kami, hook berjanji tapi akhirnya tidak menepati, dan tidak ada yang mengecek. Sekarang janji itu ditulis di shot list:

```json
{ "id": "S01", "time": "0-2.1s", "beat": "HOOK", "promise": "the price is revealed" }
{ "id": "S10", "time": "21.75-23.9s", "beat": "REVEAL", "pays_off": "S01" }
```

Ini potongan saja; shot aslinya punya lebih banyak kolom. `promise` berisi janjinya. `pays_off` ditaruh di shot yang menepatinya, berisi id hook. Kalau ada janji tanpa penepat, `vg validate` memberi peringatan.

## Langkah 6 · Kategori, kamera, dan ukuran

Setiap shot diberi tiga label yang bisa dicek `vg validate`:

- `category`: jenis shot. Misalnya `aerial_establish` (foto udara untuk menunjukkan lokasi), `room_reveal` (ruang asli dari foto klien), `lifestyle_broll` (suasana hidup di tempat itu, di bawah narasi), `concept_render` (rencana yang belum dibangun), `graphic` (peta, angka, teks).
- `camera`: satu gerak kamera, misalnya `static` (diam), `push_in` (maju pelan), `drone_approach` (drone mendekat).
- `size`: ukuran shot, dari paling dekat ke paling lebar: `ecu`, `cu`, `mcu`, `ms`, `mws`, `ws`, `ews`.

Contoh dari reel ini: S03 adalah `aerial_establish`, kamera `drone_approach`, ukuran `ews`. S06 adalah `lifestyle_broll`: Rani berjalan dengan mulut tertutup, suaranya dari narasi.

## Langkah 7 · Blok look

Di tahap yang sama, agent menulis blok `look`: satu dunia, satu cahaya, satu *grade* (pengolahan warna), satu gaya grafis, dan 2–3 *style frame*. Detailnya di Pelajaran 07.

## Langkah 8 · Shotlist.json dan vg validate

Agent menulis semua ini ke satu file: `1_Script/Shotlist.json`. *JSON* adalah format teks untuk data yang tersusun rapi, bisa dibaca manusia dan komputer. Isinya: nama proyek dan format (9:16), `rules`, `look`, tokoh dan lembar referensinya, lalu daftar `shots`.

Lalu agent memeriksanya:

```bash
python3 2_Tools/vg/vg.py validate -p NAMA_PROYEK
```

Ganti `NAMA_PROYEK` dengan nama folder proyekmu di `5_Projects/`. Alat ini mengecek kolom wajib, id, referensi antar-gambar, dan panjang dialog. Ia juga memberi peringatan, misalnya untuk janji tanpa penepat, produk yang terlalu sebentar terlihat, dan tiga potongan sama berturut-turut. Di tahap ini wajar kalau ia masih menyebut panel, frame, dan prompt video; kolom itu baru diisi di tahap berikutnya.

Tugasmu bukan menghafal file ini. Tugasmu membaca tabel beat dan shot list yang ditunjukkan agent, lalu bertanya: faktanya benar? Janjinya ditepati? Rumahnya cukup lama terlihat? Kalau ada yang salah, bilang ke agent dengan bahasa biasa.

## Latihan kecil

Pilih satu rumah, kos, atau toko yang kamu kenal. Tanpa alat apa pun, tulis tabel beat tebak harga enam baris (detik, bagian, isi) untuk reel sekitar 28 detik. Tandai beat mana yang berjanji dan beat mana yang menepati. Tulis juga satu kalimat yang harus diingat penonton.

## Cek pemahaman

1. Brief menandai peta jarak ke tol sebagai `mg`. Agent bilang gambar AI lebih mudah. Boleh diganti?
2. Kenapa S10 punya `"pays_off": "S01"`?
3. Tiga shot berturut-turut semuanya `ws` dengan `push_in`. Apa masalahnya?

<details>
<summary>Jawaban</summary>

1. Tidak. Bagian `real` atau `mg` tetap begitu, kecuali klien sendiri mengizinkan. Peta dan jarak harus tepat, bukan karangan AI.
2. S01 berjanji harganya akan dijawab, dan S10 menjawabnya. Tanpa itu, `vg validate` memberi peringatan.
3. Potongannya terasa sama dan membosankan. Ini tanda paling umum dari shot list buatan mesin. `vg validate` memberi peringatan; ubah ukuran atau gerak kamera salah satunya.

</details>

## Ringkasan

- Baca brief apa adanya: fakta, aturan, dan sumber gambar (`ai`, `real`, `mg`).
- Susun beat dulu, lalu satu shot per beat, satu ide per shot.
- Hook dalam 2 detik, potong setiap 1,5–3 detik, rumah minimal 40% durasi.
- Janji hook dicatat dengan `promise` dan `pays_off`.
- Agent menulis `1_Script/Shotlist.json` dan mengeceknya dengan `vg validate`. Kamu memeriksa isinya.

Berikutnya: [Pelajaran 07 · Look: Satu Dunia Visual, dan Halaman Review](Pelajaran_07_Look_Dan_Review_v1.0.md)
