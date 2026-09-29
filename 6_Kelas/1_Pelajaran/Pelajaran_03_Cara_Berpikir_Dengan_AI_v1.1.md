# Pelajaran 03 · Cara Berpikir dengan AI: Prompt, Batas, dan Etika

## Tujuan

Setelah pelajaran ini, kamu bisa:

- memakai enam prinsip kerja dengan AI di setiap tahap;
- menulis prompt gambar dengan lima bagian: tujuan, adegan, komposisi, cahaya, dan batasan;
- mengenali batas AI dan cara alur kerja kita mengakalinya;
- menerapkan lima aturan etika untuk video properti.

## Kenapa ini penting

AI selalu memberi hasil, bahkan kalau permintaanmu kabur. Hasilnya terlihat meyakinkan, tapi bisa salah. Cara berpikir yang benar membuatmu meminta dengan jelas, mengecek dengan teliti, dan tetap jujur kepada penonton.

## Enam prinsip

1. **Input menentukan hasil.** Brief, prompt, dan gambar acuan yang jelas memberi hasil yang jelas. Wajah Rani tetap sama di setiap shot karena setiap gambarnya diberi potret Rani dan lembar putar (Rani dari empat sisi) sebagai acuan.
2. **Spesifik, bukan umum.** Sebut kamera, cahaya, lensa, dan durasi. Kata "bagus", "estetik", "cinematic", atau "8K" tidak memberi tahu model apa pun. Tulis yang bisa diukur: "matahari dari kiri kamera", "kamera setinggi 1,2 m", "selama 6 detik".
3. **Selalu cek.** AI menebak. Periksa fakta, wajah, teks, dan logo setiap kali. Harga, jarak, dan nama selalu dicek manusia. "Cuma dua kilo ke tol" adalah klaim; di proyek nyata, kamu cek angka itu ke klien.
4. **Ulangi di tahap murah.** Perbaiki di gambar, bukan di video. Satu gambar 10 kredit, satu klip video 35 kredit. Karena itu seluruh reel disetujui dulu sebagai gambar, baru dibuat bergerak.
5. **Satu perubahan sekali coba.** Ini yang paling sering dilupakan pemula. Kalau kamu mengubah tiga hal sekaligus dan hasilnya membaik, kamu tidak tahu mana yang berhasil. Misalnya style frame terlalu kuning: ubah hanya baris cahayanya, misalnya tambahkan "neutral daylight, about 5500 K" (cahaya siang yang netral). Biarkan sisanya sama, lalu lihat hasilnya.
6. **Kamu yang memutuskan.** Selera, etika, dan persetujuan tetap tugas manusia. Agent menunggu kata "setuju" darimu di tiga gerbang: look (tampilan reel), seluruh reel sebagai gambar, dan biaya video.

## Anatomi prompt yang baik

Prompt yang baik menjawab pertanyaan juru kamera: untuk apa gambar ini, apa yang terlihat, dari mana kita melihat, cahayanya dari mana, dan apa yang tidak boleh ada.

**Prompt lemah:**

```text
rumah bagus, estetik, 4K
```

Model harus menebak semuanya sendiri. Rumah seperti apa? Dilihat dari mana? Jam berapa? Boleh ada orang atau tulisan? Hasilnya tidak bisa diulang dan tidak cocok dengan shot lain.

**Prompt kuat.** Ini prompt asli untuk `Look_Rumah_Depan` dari reel contoh. *Style frame* adalah gambar acuan tampilan untuk seluruh reel.

```text
Use: style frame, the front of one house for the price reveal. Scene: one new two-storey modern tropical townhouse in Kota Harapan on a sunny weekday afternoon, seen from its own driveway: warm white render with a mauve accent panel around the upper window, dark grey pitched roof tiles, a warm wood-slat canopy over the carport, a glass-railed balcony, a slim young tree in a planter and a strip of grass, pale stone paving leading to a dark wood front door. Composition: vertical 9:16, low eye height 1.2 m, slightly off-centre, the whole facade and roof in frame, verticals straight, 24 mm. Lighting: bright warm sun from camera left, clear blue sky with soft clouds. Constraints: an ordinary new Indonesian housing cluster, believable and a little imperfect (a hose on the lawn, a small crack line in the paving, uneven young trees). Real photograph, not a render. Avoid: people, cars in the driveway, text, signs, house numbers, logos, watermark, golden hour, HDR look, fisheye.
```

| Bagian | Label di prompt | Menjawab |
|---|---|---|
| Tujuan | Use | untuk apa gambar ini |
| Adegan | Scene | apa yang terlihat, sedetail mungkin |
| Komposisi | Composition | dari mana kamera melihat |
| Cahaya | Lighting | arah dan jenis cahaya |
| Batasan | Constraints, Avoid | apa yang harus benar, apa yang dilarang |

Istilahnya:

- *9:16*: format tegak, seperti layar HP. *Eye height 1.2 m*: kamera setinggi 1,2 meter.
- *24 mm*: lensa lebar; makin kecil angkanya, makin luas pandangannya.
- *Verticals straight*: garis tegak bangunan tidak miring.
- *Not a render*: bukan gambar 3D arsitek yang terlalu bersih.
- *Golden hour*, *HDR look*, *fisheye*: cahaya oranye menjelang senja, tampilan yang diproses berlebihan, lensa yang melengkungkan gambar.

<img src="../2_Studi_Kasus/Tebak_Harga/1_Gambar/Look_Rumah_Depan.jpg" width="260" alt="Style frame Look_Rumah_Depan">

Perhatikan tiga hal:

- **Avoid itu penting.** gpt-image-2 tidak punya kolom terpisah untuk larangan. Tempatnya di dalam prompt.
- **Sedikit tidak sempurna terasa nyata.** Prompt meminta selang di rumput dan retak kecil di paving. Keduanya muncul di gambar.
- **Prompt ditulis dalam bahasa Inggris**, karena model paling paham bahasa itu. Tulisan di layar dan narasi tetap bahasa Indonesia.

Rumah ini gambar AI karena proyeknya fiktif. Di proyek nyata, rumah yang dijual adalah foto asli dari klien, dan hanya kameranya yang bergerak.

## Batas AI, dan cara kita mengakalinya

Setiap kelemahan di tabel ini kami alami sendiri saat membuat reel contoh.

| Kelemahan | Contoh | Cara kita |
|---|---|---|
| Wajah berubah antar shot | presenter terlihat seperti orang lain | lembar referensi karakter |
| Teks dan logo kacau | tulisan papan nama aneh | teks ditambahkan saat edit |
| Bibir tidak sinkron | suara ditempel, bibir tidak cocok | narasi *voice-over*, mulut tertutup |
| Mengarang detail | jendela rumah berbeda | foto asli klien untuk produk |
| Gerakan panjang | benda berubah bentuk | klip pendek, satu gerakan kamera |

Satu batas lagi: setiap gambar dibuat terpisah, jadi tiap shot bisa punya cahaya dan warna sendiri. Itu terjadi di versi pertama reel kami, karena shot dicek satu per satu. Sekarang look disetujui dulu (Gerbang 1), dan seluruh reel ditonton utuh (Gerbang 2).

## Etika: jujur dan aman

Etika bukan tambahan, tapi bagian dari pekerjaan. Penonton tidak boleh salah paham tentang apa yang mereka beli.

1. **Beri label.** Stasiun MRT di reel ini baru rencana, jadi gambarnya diberi label ILUSTRASI RENCANA. Peta diberi catatan "Peta ilustrasi, tidak berskala." Jelaskan juga bila gambar dibuat AI.
2. **Jangan palsukan produk.** Rumah yang dijual harus foto asli. Jangan buat ia terlihat lebih besar atau lebih mewah dari aslinya.
3. **Hak cipta.** Pakai foto hanya dengan izin pemiliknya. Foto dari internet bukan milikmu.
4. **Wajah orang asli hanya dengan izin orangnya.** Rani dibuat AI dari nol, bukan dari foto orang asli. Jangan membuat presenter dari foto teman atau artis tanpa izin.
5. **Harga dan klaim selalu dicek, dengan S&K** (syarat dan ketentuan). Di reel contoh, harga tampil sebagai "MULAI 1,3M-AN*" dengan catatan "*S&K berlaku, dapat berubah."

Aturan klien seperti ini dicatat di bagian `rules` dalam `Shotlist.json`, file rencana proyek yang ditulis agent. Agent wajib mengikutinya. Di reel contoh, aturan label ILUSTRASI RENCANA dan catatan S&K dicatat di sana.

## Latihan kecil

Ubah prompt lemah "rumah bagus, estetik, 4K" menjadi prompt lima bagian untuk shot kedua: deretan rumah dua lantai. Tulis lima baris: Use, Scene, Composition, Lighting, dan Constraints/Avoid. Boleh dalam bahasa Indonesia dulu.

Lalu bandingkan dengan prompt asli. Apakah prompt-mu menyebut arah matahari? Tinggi kamera? Apa yang dilarang?

<details>
<summary>Prompt asli Look_Rumah_Deret</summary>

```text
Use: style frame, the house the reel sells. Scene: a row of four new two-storey modern tropical townhouses on a quiet cluster street in Kota Harapan on a sunny weekday afternoon; flat facades in warm white render with muted accent panels (dusty blue, mauve, terracotta), dark grey pitched roof tiles, warm wood-slat canopies over the carports, narrow balconies with glass rails, young trees, grass strips and pale stone driveways, an asphalt street in front. Composition: vertical 9:16 from the opposite sidewalk at eye height, the middle house centred and whole, its neighbours cut by the frame edges, verticals straight, 24 mm, sky in the top quarter. Lighting: bright warm sun from camera left, soft short shadows, clear blue sky with soft clouds.
```

Constraints dan Avoid-nya sama persis dengan `Look_Rumah_Depan`. Cahaya dan batasan yang sama membuat keduanya terasa satu dunia.

</details>

## Cek pemahaman

1. Style frame terlalu kuning. Kamu mengubah cahaya, lensa, dan gambar acuan sekaligus, dan hasilnya bagus. Apa masalahnya?
2. Kenapa tulisan "MULAI 1,3M-AN*" tidak diminta ke model gambar?
3. Klien mengirim foto rumahnya. Bolehkah kamu meminta AI membuat rumah itu terlihat lebih besar dan lebih mewah?

<details>
<summary>Jawaban</summary>

1. Kamu tidak tahu perubahan mana yang berhasil. Ubah satu hal, lihat hasilnya, baru ubah hal berikutnya.
2. Model gambar sering mengacaukan tulisan, padahal harga harus persis benar. Tulisan ditambahkan saat edit, lengkap dengan tanda * dan catatan S&K.
3. Tidak. Itu memalsukan produk. Rumah yang dijual harus tampil seperti aslinya; hanya kameranya yang bergerak.

</details>

## Ringkasan

- Enam prinsip: input menentukan hasil, spesifik, selalu cek, ulangi di tahap murah, satu perubahan sekali coba, kamu yang memutuskan.
- Prompt yang baik punya lima bagian: tujuan, adegan, komposisi, cahaya, dan batasan. Tulis dalam bahasa Inggris, dengan kata yang bisa diukur.
- Setiap kelemahan AI punya jalan keluar di alur kerja: referensi karakter, teks di edit, voice-over, foto asli, dan klip pendek.
- Jujur kepada penonton: beri label, jangan palsukan produk, minta izin untuk foto dan wajah, cek harga dengan S&K.

Berikutnya: [Pelajaran 04 · Persiapan Alat](Pelajaran_04_Persiapan_Alat_v1.1.md)
