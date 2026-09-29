# Pelajaran 13 · Kesalahan yang Kami Buat

## Tujuan

Setelah pelajaran ini kamu bisa:

- menceritakan apa yang salah di versi pertama reel Tebak Harga, dan kenapa;
- menghubungkan setiap aturan di kelas ini dengan kesalahan yang melahirkannya;
- mengenali tiga bug yang ditemukan saat memeriksa, dan cara mencegahnya;
- menilai hasil dengan menonton, mendengarkan, dan mengecek file, bukan hanya melihat skor.

## Kenapa ini penting

Setiap aturan di kelas ini lahir dari kesalahan nyata saat membuat reel ini. Kalau kamu tahu asal-usul sebuah aturan, kamu akan tetap menjalankannya saat terasa lambat atau merepotkan. Pelajaran ini jujur: kami juga salah, lebih dari sekali.

## Versi pertama: dinilai jelek

Versi pertama reel ini dinilai jelek saat ditonton utuh. Ada tiga masalah besar.

**1. Setiap shot punya cahaya dan warnanya sendiri.**
Setiap shot punya cahaya sendiri dan *grade* (perlakuan warna) sendiri. Kenapa bisa lolos? Karena setiap gambar dicek satu per satu, dan satu per satu semuanya terlihat baik. Masalahnya baru terlihat saat semua shot diputar berurutan: reelnya terasa seperti potongan dari film yang berbeda-beda.

**2. Hook berjanji, akhirnya tidak menepati.**
*Hook* adalah pembuka di detik-detik pertama yang membuat orang berhenti menggulir. Hook kami menjanjikan sesuatu kepada penonton, tapi reelnya tidak pernah membayar janji itu. Tidak ada yang mengecek apakah janji di awal dijawab di akhir.

**3. Suara TTS ditempel di atas bibir AI.**
*TTS* (*text-to-speech*) adalah suara buatan AI dari teks. Klip video AI sudah punya bibir yang bergerak. Lalu suara TTS yang lain ditempel di atasnya, dan suara ruangan aslinya dimatikan sampai hening total. Hasilnya seperti dubbing yang jelek: bibir bergerak untuk suara lain, dan di bawahnya sunyi.

## Perbaikannya: aturan yang kita pakai sekarang

| Masalah | Aturan sekarang | Dibahas di |
|---|---|---|
| Tiap shot beda cahaya dan warna | Look ditulis sekali dan disetujui dulu (Gerbang 1). Seluruh reel ditonton sebagai gambar sebelum video (Gerbang 2). | Pelajaran 07 dan 10 |
| Janji hook tidak ditepati | Shot list mencatat janjinya di `promise` dan shot yang menepatinya di `pays_off`. `vg validate` memberi peringatan kalau janji belum dibayar. | Pelajaran 06 |
| TTS di atas bibir AI, di bawahnya hening | Narasi voice-over; orang di klip mulutnya tertutup dan tidak bicara. Audio dulu: narasi, musik dan efek dibuat sebelum animatic, lalu gambar dipotong mengikuti suara. | Pelajaran 09 dan 11 |

Di reel yang sekarang, janji "Tebak harga rumah ini" di detik pertama dibayar di detik 21,8: layar berkedip putih, bunyi *ding*, musik masuk ke *drop* (bagian paling bertenaga), dan harganya muncul: "MULAI 1,3M-AN*".

![Frame hook dari animatic contoh](../2_Studi_Kasus/Tebak_Harga/1_Gambar/Frame_Hook.jpg)

Satu catatan: di contoh kelas ini rumahnya gambar AI, karena klien dan proyeknya fiktif. Di proyek nyata, rumah yang dijual adalah foto asli klien, dan hanya kameranya yang bergerak.

## Tiga bug yang ditemukan saat memeriksa

Setelah aturan baru dipakai, kami masih menemukan tiga *bug* (kesalahan di program). Semuanya ditemukan karena hasilnya diperiksa.

**Bug 1: harga muncul sebelum diucapkan.**
Caption menampilkan tiga kata sekaligus. Akibatnya, kata-kata yang belum diucapkan bisa ikut tampil. Di momen paling penting, harga terbaca di layar sebelum narator menyebutnya. Kejutannya hilang.
Perbaikannya: caption sekarang selalu berhenti di tanda jeda (. , ? ! : …). Jadi "HARGANYA..." tampil sendiri. Harganya baru muncul saat diucapkan.

**Bug 2: animatic membeku sekitar 2,5 detik.**
Di animatic versi 3 dan 4, sebagian gambar hilang saat *render* (proses menyusun gambar dan suara menjadi file video). Akibatnya layar diam sekitar 2,5 detik. Bug seperti ini mudah terlewat kalau video tidak ditonton utuh.
Perbaikannya: bug render-nya diperbaiki, dan sekarang jumlah frame setiap render dicek. Aturannya sederhana: jumlah frame = durasi × 30. Animatic contoh berdurasi 27,9 detik, jadi harus punya 837 frame. Dan memang 837.

**Bug 3: titik drop musik salah dua kali.**
Perintah `vg audio curve` mencari titik drop di lagu, supaya drop bisa diletakkan tepat di kata "mulai". Tebakan pertamanya adalah hentakan penutup di akhir lagu. Tebakan berikutnya malah bagian yang pelan. Baru setelah pencariannya diperbaiki, ia menemukan drop yang benar, di detik 18,5 lagu "Quiz_Pop".
Hitungannya: waktu mulai musik = waktu harga di reel − waktu drop di lagu. Dengan `music.at = 3.27`, musik mulai di detik 3,27 reel. Drop di detik 18,5 lagu jatuh di 3,27 + 18,5 ≈ 21,8 detik reel, tepat di kata "mulai".

## Pelajarannya: tonton, dengarkan, cek filenya

Perhatikan polanya. Di versi pertama, setiap shot lolos saat dicek satu per satu. Di bug musik, alatnya memberi jawaban dengan yakin, dan jawabannya salah. Di bug animatic, filenya jadi dan tidak ada pesan error.

Jadi, tiga kebiasaan:

1. **Tonton seluruh reel seperti penonton**, dari awal sampai akhir, bukan hanya shot per shot.
2. **Dengarkan dengan telinga.** Pilih suara narasi dengan telinga, bukan dengan skor. Dengarkan apakah drop jatuh di kata yang benar.
3. **Cek filenya.** Durasinya, jumlah frame-nya, captionnya di momen penting. "Selesai" dari alat belum berarti benar.

Agent juga bisa salah, dan alat juga bisa salah. Karena itu gerbang persetujuan tetap di tanganmu.

## Latihan kecil

Tonton `6_Kelas/2_Studi_Kasus/Tebak_Harga/Contoh_Tebak_Harga_Animatic_v1.0.mp4` dua kali.

- Pertama sebagai penonton. Jangan berhenti. Apa yang kamu ingat?
- Kedua sebagai pemeriksa, dengan tiga pertanyaan: apakah semua shot terasa satu dunia? Apakah janji di detik pertama dibayar? Apakah ada caption yang mendahului kata?

Tulis satu hal yang ingin kamu perbaiki, dan di tahap mana perbaikan itu paling murah.

## Cek pemahaman

1. Setiap shot di versi pertama lolos saat dicek. Kenapa reelnya tetap jelek?
2. Kenapa Rani tidak bicara di klip, padahal ada narasi?
3. Sebuah animatic berdurasi 28 detik, tapi filenya hanya punya 765 frame. Apa artinya?

<details>
<summary>Lihat jawaban</summary>

1. Karena setiap shot dicek sendiri-sendiri. Cahaya dan warna yang berbeda baru terlihat saat seluruh reel diputar. Karena itu look disetujui dulu, dan seluruh reel ditonton sebagai gambar sebelum video.
2. Suara lain yang ditempel di atas bibir AI terdengar seperti dubbing yang jelek. Jadi narasinya voice-over, dan orang di klip mulutnya tertutup.
3. Seharusnya 28 × 30 = 840 frame. Kurang 75 frame, artinya sekitar 2,5 detik gambar hilang atau beku. Render ulang, lalu cek lagi jumlah frame-nya.

</details>

## Ringkasan

- Versi pertama gagal karena cahaya beda-beda, janji hook tidak ditepati, dan suara TTS ditempel di atas bibir AI.
- Perbaikannya menjadi aturan: look dan review seluruh reel, `promise` dan `pays_off`, voice-over dengan mulut tertutup, audio dulu.
- Tiga bug ditemukan dengan memeriksa: caption mendahului harga, animatic membeku 2,5 detik, titik drop musik salah.
- Nilai hasilnya dengan menonton, mendengarkan, dan mengecek file. Jangan hanya percaya skor atau kata "selesai".

Berikutnya: [Brief Latihan](../3_Latihan/Brief_Latihan_v1.1.md)
