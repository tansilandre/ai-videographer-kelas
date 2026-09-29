# Brief Latihan · Rumah Melati, 3 Alasan

> **Semua di brief ini fiktif.** Klien, rumah, kota, jarak dan harga dibuat khusus untuk latihan. Karena itu semua gambar di reel ini akan dibuat AI, termasuk rumahnya. Di proyek nyata, rumah yang dijual selalu foto asli dari klien, dan hanya kameranya yang bergerak.

## Untuk kamu: cara memakai brief ini

Brief ini untuk latihan pertamamu dari awal sampai akhir. Kerjakan setelah kamu menyelesaikan Pelajaran 00 sampai 13, dan perintah doctor (Pelajaran 04) sudah bersih tanpa FAIL. Di WorkBuddy, klik quick prompt **Cek setup**, atau jalankan sendiri:

```bash
python3 2_Tools/vg/vg.py doctor
```

Lalu:

1. Buka WorkBuddy di folder kelas (folder yang disebut di akhir setup), pilih Expert **AI Videographer** dan model **glm-5.3-flash**, lalu klik quick prompt **Buat video baru** (lihat [Panduan WorkBuddy](../5_WorkBuddy/Panduan_WorkBuddy_v1.1.md)).
2. Expert menanyakan lima hal dalam satu pesan: brand, apa yang dijual beserta lokasi dan harga mulainya, tiga alasan, ajakan di akhir video, dan foto asli. Jawab dari brief di bawah garis ini, misalnya:

   > 1. Griya Cerah, agen properti.
   > 2. Rumah Melati, rumah satu lantai di Kota Lestari, mulai 780 juta-an, dengan catatan S&K berlaku, dapat berubah.
   > 3. Dekat ke mana-mana (stasiun, sekolah, taman); halaman belakang dan dapur terbuka, jadi anak main dan orang tua tetap bisa melihat; harganya mulai 780 juta-an.
   > 4. DM Griya Cerah.
   > 5. Tidak ada foto. Ini latihan fiktif, jadi semua gambar dibuat AI.
   >
   > Fakta lengkap, aturan klien, dan suasananya ada di 6_Kelas/3_Latihan/Brief_Latihan_v1.2.md. Ikuti semuanya. Aku pilih versi dasar, tanpa presenter.

   Memakai Claude Code? Buka Claude Code di folder repo, lalu ketik: "Buat reel dari brief latihan di 6_Kelas/3_Latihan/Brief_Latihan_v1.2.md."
3. Agent membuat folder proyek di `5_Projects/` dan menyimpan brief-nya di folder `0_Source` proyek itu. Setelah itu isi `0_Source` tidak boleh diubah.
4. Ikuti [Checklist per Tahap](Checklist_Per_Tahap_v1.2.md). Centang semua sebelum pindah tahap. Bingung sedang di tahap mana? Tanya agent, misalnya "kita di tahap mana?", atau jalankan sendiri `vg next` (Pelajaran 05), yang mencetak satu langkah berikutnya.
5. Di tiga gerbang (look, animatic, video), kamu yang memutuskan, dan kamu sendiri yang mengklik tombol persetujuan di halaman review (`VG_APPROVAL_MODE=page`). Setelah setiap klik, kembali ke WorkBuddy dan bilang "sudah". Jangan klik Approve kalau kamu belum benar-benar melihat hasilnya.
6. Untuk video, mulai dari **satu klip pilot**. Tonton dulu, baru putuskan sisanya.

Semua yang ada di bawah garis ini adalah brief dari klien. Baca seperti kamu menerimanya dari klien sungguhan.

---

## Brief dari klien

### Klien dan produk

- **Klien:** Griya Cerah, agen properti (fiktif).
- **Produk:** Rumah Melati, rumah satu lantai di Kota Lestari (kota fiktif).
- **CTA (ajakan):** DM Griya Cerah.

### Tujuan reel

Membuat keluarga muda penasaran dengan Rumah Melati dan mengirim DM untuk melihat rumahnya.

### Penonton

Pasangan muda dan keluarga kecil yang sedang mencari rumah pertama. Mereka menonton di ponsel sambil lalu, sering tanpa suara.

### Format

| Hal | Isi |
|---|---|
| Format | "3 alasan": hook menyebut jumlahnya, lalu tiga alasan, lalu ajakan |
| Durasi | 20–25 detik |
| Rasio | 9:16 vertikal, 1080×1920 |
| Bahasa | Bahasa Indonesia santai, sopan |
| Suara | satu narasi voice-over untuk seluruh reel, plus musik latar |

### Fakta yang boleh dipakai

Hanya fakta di tabel ini yang boleh muncul di reel. Semuanya fiktif.

| Fakta | Isi |
|---|---|
| Tipe rumah | satu lantai |
| Luas tanah / bangunan | 72 m² / 45 m² |
| Kamar | 2 kamar tidur, 1 kamar mandi |
| Parkir | carport untuk 1 mobil |
| Dapur | dapur terbuka yang menghadap halaman belakang |
| Halaman belakang | 3 × 5 m, berumput, dengan satu pohon jambu |
| Stasiun | 7 menit jalan kaki ke Stasiun Kota Lestari |
| Sekolah | sekolah dasar 1 km dari rumah |
| Taman | Taman Kota Lestari di ujung jalan |
| Harga | mulai 780 juta-an* |
| Catatan harga | *S&K berlaku, dapat berubah |

### Struktur yang kami bayangkan

Ini arahan, bukan naskah jadi. Detik boleh bergeser sedikit mengikuti narasi.

| Detik | Bagian | Isi | Sumber gambar |
|---|---|---|---|
| 0–2 | Hook | "3 alasan" Rumah Melati cocok untuk keluarga kecil; jumlahnya disebut di kalimat pertama | AI |
| 2–7 | Alasan 1 | dekat ke mana-mana: stasiun, sekolah, taman | peta grafis + AI |
| 7–12 | Alasan 2 | halaman belakang dan dapur terbuka: anak main, orang tua tetap bisa melihat | AI |
| 12–18 | Alasan 3 | harganya: mulai 780 juta-an* | AI + teks harga |
| 18–23 | Ajakan | "DM Griya Cerah" di kartu penutup | grafis |

### Presenter

- **Versi dasar (disarankan untuk latihan pertama):** tanpa presenter. Hanya narasi voice-over di atas gambar rumah dan lingkungan.
- **Versi tantangan:** satu presenter bernama Laras, perempuan akhir 20-an, **dibuat AI dari nol** (bukan wajah orang asli). Ia muncul di hook dan ajakan saja, dengan mulut tertutup; suaranya dari narasi. Versi ini melatih Pelajaran 08 (wajah yang sama di setiap shot), tapi lebih sulit.

Pilih satu versi dan katakan pilihanmu ke agent sebelum mulai.

### Aturan klien

Aturan ini wajib. Agent mencatatnya di bagian `rules` shot list dan mematuhinya di setiap shot.

1. Setiap gambar yang dibuat AI diberi label kecil **ILUSTRASI AI** yang terbaca, tidak menutupi wajah atau caption.
2. Peta boleh skematis (bukan peta asli), dan diberi label **PETA ILUSTRASI**.
3. Harga selalu ditulis dengan tanda bintang dan catatan **\*S&K berlaku, dapat berubah**.
4. Harga tidak boleh muncul di layar sebelum diucapkan di narasi.
5. Jangan menyebut atau menampilkan merek asli: nama mal, bank, developer, produk atau logo apa pun.
6. Jangan menjanjikan apa pun yang tidak ada di tabel fakta. Misalnya: jangan menulis "bebas banjir" atau "dekat tol".
7. Rumahnya harus terlihat jelas dan cukup lama, bukan hanya di kartu penutup.

### Suasana yang kami suka

- Satu pagi yang cerah di hari kerja, di Kota Lestari. Tidak ada senja, tidak ada malam.
- Hangat, bersih, terasa seperti tempat tinggal keluarga, bukan brosur mewah.
- Grafis: satu jenis huruf tebal dan satu warna aksen hijau daun.
- Musik: ceria, tenang di bawah suara, lalu drop tepat saat harga disebut.

### Anggaran

- **Gambar:** bebas dipakai secukupnya (gpt-image-2, 10 kredit per gambar 2K).
- **Video:** paling banyak **4 klip AI** (Veo 3.1 Lite, 35 kredit per klip 8 detik di 1080p), jadi paling banyak 4 × 35 = 140 kredit. Mulai dari **1 klip pilot (35 kredit)**. Bagian lain boleh memakai gambar diam dengan gerak pelan di edit, yang gratis.
- **Suara dan musik:** beberapa sen dolar lewat OpenRouter.

Angka pastinya tampil di bagian Video halaman review (dan di perintah estimate) sebelum kamu menyetujui video. Jangan menebak.

### Yang diserahkan

- Satu video 9:16, 1080×1920, 20–25 detik, di folder `99_Output` proyekmu, dengan nama berversi, misalnya `Griya_Cerah_Tiga_Alasan_v1.0.mp4`.
- File caption `.srt` yang dibuat bersama video final.
- Animatic yang sudah kamu setujui di Gerbang 2.

---

## Catatan untuk kamu

- **Tulis angka di naskah narasi seperti diucapkan.** Misalnya "tujuh ratus delapan puluh juta-an", bukan "780 juta-an". Suara AI membaca teks persis seperti tertulis. Caption di layar tetap boleh memakai angka.
- **Satu alasan, satu shot.** Kalau satu shot berisi dua ide, model dan penonton sama-sama bingung.
- **Hook harus ditepati.** Kalau hook menjanjikan tiga alasan, penonton harus melihat tiga alasan, dengan nomornya.
- **Semua gambar di latihan ini AI karena brief-nya fiktif.** Itu sebabnya aturan nomor 1 ada. Di proyek nyata, minta foto asli rumah dari klien.
