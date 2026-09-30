# Pelajaran 01 · Apa Itu AI dan Cara Ia Belajar

Sebelum menyentuh alatnya, kita pahami dulu cara kerja AI. Kalau kamu paham cara kerjanya, kamu tahu cara memintanya, dan kapan harus curiga pada hasilnya.

## Tujuan

Setelah pelajaran ini, kamu bisa:

- menjelaskan beda program biasa dan AI dengan satu contoh;
- menyebutkan empat langkah AI belajar: data, latihan, model, dipakai;
- menjelaskan kenapa AI menebak, bukan tahu, dan apa itu halusinasi;
- menunjuk fakta mana di sebuah reel yang wajib dicek manusia.

## Kenapa ini penting

Di kelas ini kamu akan meminta banyak hal ke AI: naskah, gambar, suara, video. Hasilnya hampir selalu terlihat meyakinkan. Tapi terlihat meyakinkan tidak sama dengan benar. Orang yang paham cara berpikir AI menulis permintaan yang lebih baik, dan tahu bagian mana yang harus ia periksa sendiri.

## Program biasa dan AI

**Program biasa: manusia menulis aturannya satu per satu.**

Contoh: "kalau luas tanah lebih dari 100 m², tulis 'rumah besar'." Komputer hanya menjalankan aturan itu. Ia tidak pernah salah menjalankannya, tapi ia juga tidak bisa melakukan apa pun yang tidak ditulis.

**Kecerdasan buatan (AI): komputer belajar pola dari jutaan contoh, lalu menebak.**

Contoh: AI diberi jutaan foto rumah beserta keterangannya. Dari situ ia belajar seperti apa "rumah modern". Setelah itu ia bisa menggambar rumah yang belum pernah ada.

Kamu sudah melihat buktinya. Rumah-rumah di Cluster Aster pada reel contoh tidak ada di dunia nyata. Rani juga tidak ada. Ia dibuat AI dari nol, bukan dari foto orang asli.

<p>
<img src="../2_Studi_Kasus/Tebak_Harga/1_Gambar/Look_Rumah_Deret.jpg" width="220" alt="Deretan rumah dua lantai di Cluster Aster, dibuat AI">
<img src="../2_Studi_Kasus/Tebak_Harga/1_Gambar/Rani_Portrait_Ref.jpg" width="220" alt="Potret referensi Rani, presenter yang dibuat AI dari nol">
</p>

Jadi ingat kalimat ini: **AI adalah mesin pengenal pola.** Ia tidak berpikir seperti manusia. Ia menebak berdasarkan pola yang pernah ia lihat.

## Cara AI belajar: dari contoh ke model

Semua model yang kita pakai di kelas ini (teks, gambar, video, suara dan musik) melewati empat langkah yang sama.

1. **Data.** Jutaan contoh: teks, foto, video, suara. *Data* artinya kumpulan contoh yang dipakai untuk belajar.
2. **Latihan.** Komputer menebak, tebakannya dicek, lalu diperbaiki. Begitu terus, miliaran kali. Proses ini disebut *training* (pelatihan).
3. **Model.** Hasil latihan adalah pola yang tersimpan sebagai angka. Kumpulan angka itu disebut *model*. Ketika orang bilang "model gambar" atau "model video", maksudnya hasil latihan ini.
4. **Dipakai.** Kamu memberi *prompt* (perintah atau permintaan dalam bentuk teks), lalu model menjawab.

Poin terpentingnya: **model tidak menyimpan foto aslinya, ia menyimpan polanya.**

Bayangkan kamu sudah melihat ratusan rumah minimalis. Kamu tidak ingat setiap foto satu per satu. Tapi kalau diminta menggambar rumah minimalis, kamu tahu bentuknya: atap sederhana, jendela besar, garis lurus. Model bekerja mirip seperti itu.

Ada dua akibat dari cara belajar ini:

- **Ia bisa membuat hal baru.** Rumah yang belum pernah ada, presenter yang bukan orang asli.
- **Ia juga bisa keliru.** Karena ia menyusun dari pola, detail yang tidak ada di permintaanmu akan ia karang sendiri.

## AI tidak tahu. AI menebak.

Model bahasa seperti Claude (*model bahasa*: model yang dilatih dengan teks) menulis satu kata demi satu kata. Sebenarnya yang ia tulis adalah potongan kata yang disebut *token*, tapi anggap saja kata. Setiap kali, ia memilih lanjutan yang paling masuk akal.

Misalnya kalimatnya: *"Rumah di pinggir kota itu biasanya …"*

| Kata berikutnya | Peluang |
|---|---|
| lebih luas | 46% |
| lebih murah | 31% |
| jauh dari kantor | 15% |
| sepi | 8% |

*Angka di tabel ini hanya ilustrasi, bukan dari model sungguhan.*

Model memilih lanjutan yang paling mungkin, lalu mengulanginya untuk kata berikutnya, dan seterusnya. Perhatikan: ia tidak memeriksa rumah mana yang sedang kita bicarakan. Ia hanya tahu kalimat seperti apa yang biasanya muncul.

Akibatnya: **jawabannya selalu lancar, tapi bisa salah dengan yakin.** Ini disebut *halusinasi*, yaitu saat AI menyampaikan sesuatu yang tidak benar dengan nada seolah-olah benar. AI tidak berbohong dengan sengaja. Ia hanya menebak lanjutan yang terdengar paling wajar.

## Contoh dari reel Tebak Harga

Coba lihat narasi reel contoh:

> "Tebak harga rumah ini. Tiga petunjuk. Petunjuk satu: seberang mall besar. Dua: cuma dua kilo ke tol. Tiga: udah ada smart lock, solar water heater, sama CCTV. Udah ketebak? Bonus: ada rencana stasiun MRT. Seribu unit udah laku. Harganya... mulai satu koma tiga M-an! Mau lihat langsung? DM Rumah Kita Realty."

Hampir setiap kalimat berisi fakta: letak, jarak, fitur rumah, rencana stasiun, jumlah unit terjual, harga. Fakta-fakta ini harus datang dari brief klien, bukan dari tebakan AI.

Bayangkan dua kesalahan yang mungkin terjadi kalau tidak ada yang mengecek:

- AI menulis "dekat stasiun MRT" seolah stasiunnya sudah ada. Padahal itu baru rencana. Karena itu di reel contoh, gambar stasiun diberi label **ILUSTRASI RENCANA**.
- AI membulatkan jarak atau harga supaya kalimatnya terdengar lebih menarik. Kalimatnya jadi enak didengar, tapi angkanya salah.

Kedua kalimat itu akan terdengar lancar dan meyakinkan. Justru itu bahayanya.

Hal yang sama berlaku untuk gambar. Model gambar menggambar yang paling masuk akal, bukan yang benar. Karena itu di proyek nyata, rumah yang dijual selalu foto asli dari klien. Di reel contoh rumahnya gambar AI hanya karena klien dan proyeknya fiktif.

**Aturan kita: fakta seperti harga, jarak dan nama selalu dicek manusia.** Cara mengeceknya sederhana:

1. Bandingkan dengan brief asli klien.
2. Kalau ragu, tanyakan ke klien.
3. Harga selalu diberi catatan "S&K berlaku". Di reel contoh: "*S&K berlaku, dapat berubah".

## Latihan kecil

Ambil narasi reel contoh di atas (juga ada di `6_Kelas/2_Studi_Kasus/Tebak_Harga/Narasi.txt`). Buat tabel kecil di kertas dengan tiga kolom:

| Fakta | Sudah ada atau baru rencana? | Dicek ke mana? |
|---|---|---|
| seberang mall besar | ... | ... |

Isi satu baris untuk setiap fakta yang kamu temukan. Berapa banyak fakta yang kamu temukan? Mana yang paling berbahaya kalau salah?

## Cek pemahaman

1. Apa beda program biasa dan AI?
2. Model menyimpan foto asli atau pola? Apa akibatnya?
3. Kenapa jawaban AI bisa terdengar yakin padahal salah, dan apa aturan kita untuk itu?

<details>
<summary>Lihat jawaban</summary>

1. Di program biasa, manusia menulis semua aturannya dan komputer hanya menjalankannya. Di AI, komputer belajar pola sendiri dari jutaan contoh, lalu menebak.
2. Pola, yang tersimpan sebagai angka. Akibatnya model bisa membuat hal baru, seperti rumah atau presenter yang belum pernah ada, tapi juga bisa keliru dan mengarang detail.
3. Model bahasa memilih kata berikutnya yang paling masuk akal, bukan yang paling benar. Jadi jawabannya selalu lancar, bahkan saat salah. Ini disebut halusinasi. Aturan kita: fakta seperti harga, jarak dan nama selalu dicek manusia.

</details>

## Ringkasan

- Program biasa menjalankan aturan yang ditulis manusia. AI belajar pola dari contoh, lalu menebak.
- AI belajar dalam empat langkah: data, latihan, model, dipakai.
- Model menyimpan pola, bukan salinan. Karena itu ia bisa membuat hal baru, dan juga bisa keliru.
- Model bahasa menulis satu kata demi satu kata. Jawabannya lancar, tapi bisa salah dengan yakin (halusinasi).
- Harga, jarak dan nama selalu dicek manusia.

Berikutnya: [Pelajaran 02 · Model Gambar, Video, Suara, dan Agent](Pelajaran_02_Model_Dan_Agent_v1.2.md)
