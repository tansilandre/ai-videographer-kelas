# Pelajaran 09 · Audio Dulu

## Tujuan

Setelah pelajaran ini kamu bisa:

- menjelaskan kenapa suara dibuat sebelum gambar dipotong;
- menulis naskah narasi yang mudah dipotong, lalu memilih suara dengan telinga;
- membaca kurva kenyaringan musik dan menghitung `music.at` supaya *drop* jatuh di momen harga;
- memilih efek suara yang cocok untuk setiap jenis potongan.

## Kenapa ini penting

Di video pendek, suara yang mengatur waktu. Penonton mendengar "Petunjuk satu" dan menunggu gambar baru. Kalau gambar dipotong duluan lalu suara ditempel belakangan, potongannya jatuh di tempat yang aneh. Jadi urutannya dibalik: suara dibuat dulu, gambar mengikuti suara.

Aturan ini lahir dari kesalahan nyata. Di versi pertama reel kami, suara *TTS* (*text-to-speech*, suara buatan komputer dari teks) ditempel di atas bibir AI, dan suara ruangan dimatikan sampai hening. Hasilnya terdengar ditempel.

Di pelajaran ini, `vg` adalah singkatan dari `python3 2_Tools/vg/vg.py`. Perintahnya biasanya dijalankan oleh agent. Kamu cukup tahu apa yang terjadi dan kapan harus mendengarkan.

## 1. Narasi sebagai voice-over, mulut tertutup

*Voice-over* artinya suara narator terdengar, tapi orangnya tidak terlihat bicara. Di reel Tebak Harga, satu suara membawa seluruh cerita. Rani, presenter yang dibuat AI dari nol, muncul di layar dengan mulut tertutup. Yang bicara hanya suara narasi.

Kenapa? *Lip-sync* (gerak bibir yang cocok dengan suara) adalah bagian paling rapuh dari video AI. Suara lain yang ditempel di atas bibir yang bergerak langsung terasa palsu. Semakin sedikit bibir yang bergerak, semakin sedikit yang bisa gagal.

## 2. Tulis naskah untuk dipotong

Tulis narasi pendek, seperti orang bicara. Satu kalimat atau satu petunjuk per frasa. Taruh titik (.) atau titik dua (:) di tempat potongan gambar boleh jatuh. Alat membaca tanda itu, juga tanda tanya dan tanda seru, sebagai batas frasa. Koma tidak memecah frasa, karena narator membaca daftar tanpa berhenti.

Dua aturan lagi:

- **Tulis angka seperti diucapkan.** Model suara membaca teks apa adanya. Tulis "satu koma tiga M-an", bukan "1,3M".
- **Kata pertama secepat mungkin.** Kata pertama harus terdengar sebelum detik 0,8. Di reel contoh, "Tebak" terdengar di sekitar detik 0,4.

Ini naskah reel contoh (`6_Kelas/2_Studi_Kasus/Tebak_Harga/Narasi.txt`):

```text
Tebak harga rumah ini. Tiga petunjuk.
Petunjuk satu: seberang mall besar.
Dua: cuma dua kilo ke tol.
Tiga: udah ada smart lock, solar water heater, sama CCTV.
Udah ketebak?
Bonus: ada rencana stasiun MRT.
Seribu unit udah laku.
Harganya... mulai satu koma tiga M-an!
Mau lihat langsung? DM Rumah Kita Realty.
```

## 3. Buat beberapa take, pilih dengan telinga

*Take* artinya satu kali rekaman. Agent membuat satu take per suara, dari naskah yang sama:

```bash
python3 2_Tools/vg/vg.py audio voice -p NAMA_PROYEK --text-file 1_Script/Narasi.txt --voices Callirrhoe,Leda,Aoede --style "A warm, natural Indonesian voice-over for a short social video, conversational, not a newsreader."
```

- Ganti `NAMA_PROYEK` dengan nama folder proyekmu di `5_Projects/`.
- `--text-file` adalah file naskah di dalam folder proyek itu, misalnya `1_Script/Narasi.txt`.
- `--voices` adalah daftar suara. Tanpa flag ini, alat mencoba enam suara: Callirrhoe, Leda, Laomedeia, Aoede, Zephyr, Sulafat.
- `--style` adalah arahan dalam bahasa Inggris: siapa yang bicara, ke siapa, temponya, suasananya.

Hasilnya masuk ke `6_Edit/1_Audio/`, misalnya `Narration_Take_Callirrhoe_v1.wav`. Modelnya google/gemini-3.8-flash-lite-tts lewat OpenRouter, sekitar US$0,003 per take 20 detik.

Lalu dengarkan semua take, satu per satu. Pilih yang terdengar seperti orang sungguhan. **Pilih dengan telinga, bukan dengan skor.** Di reel contoh, pilihannya Callirrhoe. Dengarkan di `6_Kelas/2_Studi_Kasus/Tebak_Harga/2_Audio/Narration_Take_Callirrhoe_v1.mp3`.

Perintah ini memakai kunci OpenRouter di file `.env`. Kalau agent bilang kuncinya belum ada, **kamu sendiri** yang membuka `.env` dan mengisinya. Kunci dibuat di <https://openrouter.ai/keys>. Jangan pernah menempelkan kunci API ke chat.

## 4. Musik dengan struktur

Musik latar punya bentuk, bukan sekadar lagu:

1. tenang di bawah suara narator;
2. *build*: naik pelan-pelan;
3. hening setengah ketukan;
4. *drop*: bagian yang tiba-tiba ramai, tepat di momen jawaban.

Agent menulis prompt musik yang menyebut bentuk ini beserta waktunya, lalu menjalankan:

```bash
python3 2_Tools/vg/vg.py audio music -p NAMA_PROYEK --prompt-file 1_Script/Music_Prompt.txt --label Quiz_Pop --takes 3
```

`--prompt-file` adalah file teks berisi prompt musiknya. `--label` adalah nama pendek untuk take-nya. `--takes` bisa 1 sampai 3. Hasilnya `Music_Take_Quiz_Pop_v1.mp3` dan seterusnya. Modelnya google/lyria-3-clip-preview lewat OpenRouter, sekitar US$0,04 per klip 30 detik. Seluruh audio reel contoh habis di bawah US$0,50.

Tolak take yang punya bagian mati, yaitu bagian yang tiba-tiba kosong atau datar.

## 5. Temukan drop, lalu hitung music.at

Untuk mencari drop, agent membaca kurva kenyaringan musik:

```bash
python3 2_Tools/vg/vg.py audio curve -p NAMA_PROYEK --file 6_Edit/1_Audio/Music_Take_Quiz_Pop_v1.mp3
```

Alat menulis satu baris per setengah detik. Ini potongan hasil asli dari take Quiz_Pop:

```text
 17.00s  -19.4 dB ####################
 17.50s  -23.5 dB ##################
 18.00s  -39.3 dB ##########
 18.50s  -13.9 dB #######################
 19.00s  -12.3 dB #######################
 19.50s  -10.1 dB ########################
drop   at about 18.50s (set music.at = reveal time - this)
```

*dB* (desibel) adalah ukuran kenyaringan. Makin dekat ke nol, makin keras. Di detik 18,0 lagunya hampir hening: itu jeda setengah ketukan. Di detik 18,5 musiknya melompat keras: itu drop-nya.

`music.at` adalah detik di reel saat musik mulai masuk. Rumusnya:

> **music.at = waktu jawaban di reel − waktu drop di lagu**

Di reel contoh, flash, bunyi ding, dan kata "mulai" jatuh di sekitar detik 21,8. Jadi 21,8 − 18,5 = 3,3 detik. Di file contoh tertulis 3,27. Musik masuk di detik itu, dan drop-nya jatuh tepat di jawaban harga.

Satu lagi: akhiri reel di hentian musik, bukan musik yang memudar ke hening. Reel contoh berakhir tepat saat musiknya berhenti.

Cerita jujurnya: pencarian drop otomatis sempat salah dua kali. Pertama ia memilih pukulan penutup di akhir lagu. Lalu ia memilih bagian yang sepi. Baru setelah diperbaiki ia menemukan 18,5 detik. Pelajarannya: angka dari alat tetap didengarkan. Putar lagunya dan dengarkan detik 18,5.

## 6. Efek suara: whoosh, tap, ding, tick

```bash
python3 2_Tools/vg/vg.py audio sfx -p NAMA_PROYEK
```

Perintah ini gratis. Empat efek dibuat di komputermu sendiri:

| Efek | Dipakai saat | Di reel contoh |
|---|---|---|
| Whoosh | potongan *whip* (kabur gerak saat pindah tempat) | S03, S04, S07, mulai sekitar 0,28 detik sebelum potongan |
| Tap | judul atau *callout* (label kecil) muncul | "TEBAK HARGANYA?", tiga fitur di S05 |
| Ding | jawaban, hanya sekali | S10, bersama flash dan drop |
| Tick | angka yang berjalan (*counter*) | S08, hitungan ke 1.000 UNIT TERJUAL |

Efek selalu di bawah suara narator. Kalau ada yang bilang efeknya terdengar seperti kartun atau terlalu keras, kecilkan dan lembutkan.

## 7. Potong gambar ke awal frasa

Setelah take dipilih, alat mencari di mana setiap frasa mulai, dengan mendeteksi jeda di rekaman. Lalu setiap segmen gambar diatur panjangnya supaya potongannya jatuh sedikit sebelum frasanya.

| Potongan | Frasa mulai | Frasa |
|---|---|---|
| 2,10 s (S02) | 2,27 s | "Tiga petunjuk." |
| 3,55 s (S03) | 3,69 s | "Petunjuk satu: ..." |
| 6,30 s (S04) | 6,49 s | "Dua: ..." |
| 9,05 s (S05) | 9,20 s | "Tiga: ..." |
| 14,20 s (S06) | 14,36 s | "Udah ketebak?" |
| 18,45 s (S08) | 18,63 s | "Seribu unit udah laku." |
| 21,75 s (S10) | 21,82 s | "mulai satu koma tiga M-an!" |

Satu beat per frasa. Frasa berisi daftar boleh menahan satu shot. S05 bertahan 5,15 detik di depan rumah, sementara SMART LOCK, SOLAR WATER HEATER, dan 3 TITIK CCTV muncul satu per satu mengikuti kata-katanya.

![S05: tiga fitur muncul satu per satu di atas satu shot rumah](../2_Studi_Kasus/Tebak_Harga/1_Gambar/Frame_Petunjuk_3.jpg)

Catatan: di contoh kelas ini rumahnya gambar AI, karena klien dan proyeknya fiktif. Di proyek nyata, rumah yang dijual selalu foto asli dari klien, dan hanya kameranya yang bergerak.

## Latihan kecil

1. Dengarkan `2_Audio/Music_Take_Quiz_Pop_v1.mp3` di folder studi kasus. Cari hening pendek di sekitar detik 18, lalu drop di detik 18,5.
2. Misalkan jawaban di reelmu jatuh di detik 20,0 dan drop lagunya di detik 16,5. Hitung `music.at`.
3. Tulis narasi 10 detik untuk rumah imajiner. Pakai titik atau titik dua di setiap tempat potongan, dan tulis angka seperti diucapkan.

## Cek pemahaman

1. Kenapa Rani tidak berbicara di layar?
2. Drop di lagu ada di detik 18,5. Jawaban di reel jatuh di detik 21,8. Berapa `music.at`?
3. Kenapa naskah menulis "satu koma tiga M-an", bukan "1,3M"?

<details>
<summary>Jawaban</summary>

1. *Lip-sync* adalah bagian paling rapuh dari video AI, dan suara lain di atas bibir yang bergerak terasa palsu. Jadi narasinya *voice-over*, dan orang di layar menutup mulut.
2. 21,8 − 18,5 = 3,3 detik (di file contoh: 3,27).
3. Model suara membaca teks apa adanya. Angka ditulis seperti cara mengucapkannya.

</details>

## Ringkasan

- Suara dibuat dulu. Gambar dipotong mengikuti suara.
- Narasi adalah *voice-over*: satu suara, dan orang di layar menutup mulut.
- Titik dan titik dua di naskah menandai tempat potongan. Pilih take dengan telinga.
- Musik punya bentuk: tenang, *build*, hening setengah ketukan, drop. `music.at` = waktu jawaban − waktu drop.
- Whoosh untuk whip, tap untuk judul, tick untuk counter, ding hanya sekali untuk jawaban.

Berikutnya: [Pelajaran 10 · Rencana Edit dan Animatic](Pelajaran_10_Edit_Plan_Dan_Animatic_v1.1.md)
