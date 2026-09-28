# Glosarium

Semua istilah teknis di Pelajaran 00–13, urut abjad. Kolom terakhir menunjukkan pelajaran tempat istilah itu pertama kali muncul. Kadang istilahnya baru dijelaskan panjang di pelajaran sesudahnya.

Di kelas ini, `vg <perintah>` adalah singkatan dari `python3 2_Tools/vg/vg.py <perintah>`, dijalankan dari folder repo. Tidak ada perintah bernama `vg` di komputermu. Daftar perintahnya ada di bagian [Perintah vg](#perintah-vg) di bawah.

[Angka dan simbol](#angka-dan-simbol) · [A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) · [H](#h) · [I](#i) · [J](#j) · [K](#k) · [L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) · [Q](#q) · [R](#r) · [S](#s) · [T](#t) · [V](#v) · [W](#w) · [X](#x) · [Z](#z)

## Angka dan simbol

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **`.env`** | File pengaturan rahasia di folder repo, berisi API key dan batas biaya. Hanya kamu yang mengeditnya; agent hanya memeriksanya lewat `vg doctor`. | [Pelajaran 00][p00] |
| **`.env.example`** | Contoh isi `.env`. `bash install.sh` menyalinnya menjadi `.env` kalau `.env` belum ada. | [Pelajaran 04][p04] |
| **`.srt`** | File teks berisi caption beserta waktunya. Dibuat bersama video final di `99_Output/`, dan bisa dipakai platform video sebagai subtitle. | [Pelajaran 12][p12] |
| **`0_Source`** | Folder proyek untuk bahan asli dari klien, misalnya brief dan foto rumah. Isinya tidak pernah diubah atau diganti nama. | [Pelajaran 00][p00] |
| **1080p dan 720p** | Ukuran ketajaman video; 1080p lebih tajam. Satu klip Veo 3.1 Lite 8 detik: 35 kredit di 1080p, 30 kredit di 720p. | [Pelajaran 00][p00] |
| **24 mm** | Panjang lensa yang ditulis di prompt. Makin kecil angkanya, makin luas pandangannya; 24 mm termasuk lensa lebar. | [Pelajaran 03][p03] |
| **9:16** | Format tegak, seperti layar HP. Reel kita 9:16, 1080×1920 piksel. | [Pelajaran 00][p00] |
| **`99_Output`** | Folder untuk hasil akhir yang siap dikirim, misalnya `Contoh_Tebak_Harga_v1.0.mp4`. Draft tetap di `6_Edit/`. | [Pelajaran 05][p05] |

## A

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **`aerial_establish`** | Kategori shot: foto udara untuk menunjukkan lokasi. Contohnya S03 di reel Tebak Harga. | [Pelajaran 06][p06] |
| **Agent** | AI yang bisa membaca file, menjalankan alat, dan melihat hasilnya, dalam putaran rencanakan, kerjakan, periksa, perbaiki. Agent di kelas ini adalah Claude Code. | [Pelajaran 00][p00] |
| **AI (kecerdasan buatan)** | Program yang belajar pola dari jutaan contoh, lalu menebak. Ia tidak berpikir seperti manusia, jadi hasilnya bisa salah. | [Pelajaran 00][p00] |
| **`ai`, `real`, `mg`** | Label sumber gambar di shot list: `ai` dibuat AI, `real` foto atau video asli dari klien, `mg` grafis bergerak yang dibuat saat edit. Bagian `real` atau `mg` tidak boleh diam-diam diubah jadi `ai`. | [Pelajaran 06][p06] |
| **Ambience (suara sekitar)** | Suara latar di tempat itu, misalnya jalan yang tenang, burung, angin. Prompt video menyebutnya, dan menulis bahwa tidak ada yang bicara. | [Pelajaran 11][p11] |
| **Animatic** | Seluruh reel dalam bentuk gambar diam, lengkap dengan caption, grafis, transisi, narasi, musik dan efek suara, sebelum ada video. Gratis, dibuat dengan `vg edit animatic`. | [Pelajaran 00][p00] |
| **API key (kunci API)** | Kunci rahasia yang membuat alat vg bisa memakai akun kie.ai dan OpenRouter-mu, dan menagih saldomu. Simpan hanya di `.env`; jangan pernah ditempel ke chat. | [Pelajaran 00][p00] |
| **Approval mode (`VG_APPROVAL_MODE`)** | Cara alat mencatat persetujuan, diatur di `.env`. Bawaannya `terminal`: kamu menjalankan perintah persetujuan di terminalmu sendiri dan mengetik kode acak 4 digit. | [Pelajaran 05][p05] |

## B

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **`background`** | Jenis segmen di rencana edit: gambar latar untuk grafis. Bisa dikaburkan (`blur`) dan digelapkan (`dim`). | [Pelajaran 10][p10] |
| **Batas kredit** | Batas total pemakaian yang kamu pasang pada API key kie.ai di https://kie.ai/api-key. Ini pagar terakhir kalau semua pengaman lain gagal. | [Pelajaran 00][p00] |
| **Beat** | Satu perubahan informasi atau emosi dalam cerita. Beat disusun dulu, lalu biasanya satu beat menjadi satu shot. | [Pelajaran 05][p05] |
| **Board** | Papan review berisi semua gambar proyek, file `Board_<nama proyek>.html` di folder proyek. Agent menunjukkannya sebelum meminta persetujuan video. | [Pelajaran 05][p05] |
| **Brief** | Catatan permintaan dari klien: produk, fakta, aturan, dan tujuan video. Disimpan apa adanya di `0_Source`. | [Pelajaran 00][p00] |
| **Bug** | Kesalahan di program. Tiga bug di reel contoh ditemukan karena hasilnya diperiksa ([Pelajaran 13][p13]). | [Pelajaran 10][p10] |
| **Build** | Bagian musik yang naik pelan-pelan sebelum drop. | [Pelajaran 09][p09] |

## C

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **Callout** | Label kecil penunjuk fitur di layar, misalnya SMART LOCK di S05. Muncul dengan efek tap. | [Pelajaran 06][p06] |
| **`camera`** | Label gerak kamera satu shot di shot list, misalnya `static` (diam), `push_in` (maju pelan), atau `drone_approach` (drone mendekat). Satu shot, satu gerak kamera. | [Pelajaran 06][p06] |
| **Caption** | Teks ucapan yang muncul di layar, kata demi kata. Caption selalu berhenti di tanda jeda, supaya tidak mendahului kata yang diucapkan. | [Pelajaran 00][p00] |
| **`category`** | Label jenis shot di shot list, misalnya `aerial_establish`, `room_reveal`, `lifestyle_broll`, `concept_render`, atau `graphic`. | [Pelajaran 06][p06] |
| **`cd`, `ls`, `pwd`** | Perintah dasar Terminal. `pwd` menunjukkan folder tempatmu sekarang, `ls` menampilkan isinya, dan `cd` pindah folder (`cd ..` naik satu folder). | [Pelajaran 04][p04] |
| **Chatbot** | AI yang hanya menjawab dengan teks. Beda dengan agent, yang juga bisa memakai alat. | [Pelajaran 02][p02] |
| **CHECK** | Baris dari `vg resume` yang berarti status sebuah tugas belum jelas. Kamu yang membuka dashboard kie.ai untuk melihat apakah tugasnya ada. | [Pelajaran 11][p11] |
| **`chmod 600`** | Perintah Terminal yang membuat sebuah file hanya bisa dibaca akunmu. Dipakai kalau `vg doctor` menampilkan `warn .env permissions`. | [Pelajaran 04][p04] |
| **Claude** | Model bahasa yang menjadi otak agent kita. Tugasnya merencanakan, menulis prompt, dan memeriksa hasil. | [Pelajaran 01][p01] |
| **Claude Code** | Agent yang kamu ajak bicara dengan bahasa biasa. Ia membaca skill di `1_Skills/` dan menjalankan alat vg. Pasang dengan panduan instalasi resmi dari Anthropic. | [Pelajaran 00][p00] |
| **`concept_render`** | Kategori shot untuk rencana yang belum dibangun, misalnya stasiun yang baru direncanakan. Gambar rencana seperti ini diberi label ILUSTRASI RENCANA. | [Pelajaran 06][p06] |
| **Continuity** | Lihat **Kesinambungan**. | [Pelajaran 08][p08] |
| **Counter (penghitung)** | Angka yang berjalan di layar, misalnya hitungan ke 1.000 UNIT TERJUAL di S08. Diberi efek tick. | [Pelajaran 09][p09] |
| **`crop_x`** | Pengaturan di `first_frame` yang menentukan bagian foto yang dipotong ke 9:16: 0 kiri, 0,5 tengah, 1 kanan. | [Pelajaran 08][p08] |
| **CTA (*call to action*)** | Ajakan yang jelas di akhir video, misalnya "DM Rumah Kita Realty". | [Pelajaran 06][p06] |

## D

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **Dashboard kie.ai** | Halaman akunmu di kie.ai. Kamu memeriksanya kalau `vg resume` mencetak baris CHECK. | [Pelajaran 11][p11] |
| **Data** | Kumpulan contoh (teks, foto, video, suara) yang dipakai AI untuk belajar. | [Pelajaran 01][p01] |
| **dB (desibel)** | Ukuran kenyaringan. Di kurva musik, makin dekat ke nol, makin keras. | [Pelajaran 09][p09] |
| **Deck** | Slide kelas (.pptx dan .pdf) di `6_Kelas/4_Deck/`. Urutan dan isinya sama dengan pelajaran. | [Pelajaran 00][p00] |
| **Ding** | Efek suara untuk jawaban, dipakai hanya sekali: di S10, bersama flash putih dan drop musik. | [Pelajaran 00][p00] |
| **Draft** | Versi percobaan edit final, dibuat dengan `vg edit final --draft`. Disimpan bernomor di `6_Edit/`, misalnya `_d1`, `_d2`. | [Pelajaran 05][p05] |
| **Drop** | Momen saat musik tiba-tiba penuh setelah jeda singkat. Di reel contoh, drop jatuh tepat saat harga disebut. | [Pelajaran 00][p00] |
| **Dubbing** | Suara lain yang ditempel di atas bibir yang bergerak. Terdengar palsu, karena itu kita memakai voice-over dengan mulut tertutup. | [Pelajaran 02][p02] |
| **`duck` (*ducking*)** | Musik dikecilkan otomatis saat ada yang bicara. `duck` 0,5 berarti musik turun jadi setengahnya. | [Pelajaran 10][p10] |

## E

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **`Edit_Spec.json` (rencana edit)** | File di `6_Edit/` yang mengatur seluruh edit: segmen, grafis, narasi, musik, efek, transisi, grade, dan caption. Ditulis agent, dipakai untuk animatic dan edit final. | [Pelajaran 00][p00] |
| **Efek suara (SFX)** | Bunyi pendek yang memperkuat gambar: whoosh, tap, ding, dan tick. Dibuat gratis di komputermu dengan `vg audio sfx`. | [Pelajaran 00][p00] |
| **End card (kartu penutup)** | Layar penutup berisi nama brand, ajakan, dan nomor telepon. Di reel contoh: S11, dengan nomor 0812-0000-0000. | [Pelajaran 06][p06] |
| **Eye height** | Tinggi kamera yang ditulis di prompt. *Eye height 1.2 m* berarti kamera setinggi 1,2 meter. | [Pelajaran 02][p02] |

## F

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **FAIL, warn, ok** | Tiga tanda di hasil `vg doctor`. `ok` beres, `warn` peringatan (kamu masih bisa mulai), `FAIL` harus diperbaiki sebelum lanjut. | [Pelajaran 00][p00] |
| **FFmpeg** | Program pengolah video dan audio, dipakai untuk animatic dan edit final. Dipasang dengan `brew install ffmpeg`. | [Pelajaran 04][p04] |
| **FFprobe** | Alat pemeriksa file video yang ikut terpasang bersama FFmpeg. Dipakai untuk menghitung jumlah frame. | [Pelajaran 04][p04] |
| **Fisheye** | Lensa yang melengkungkan gambar. Dilarang di prompt style frame kita. | [Pelajaran 03][p03] |
| **Flag** | Tambahan di belakang perintah yang diawali dua tanda minus, misalnya `--draft` atau `--voices`. Flag mengubah cara perintah bekerja. | [Pelajaran 09][p09] |
| **Flash** | Transisi: gambar muncul dari putih dalam 0,2 detik. Hanya sekali, di jawaban harga, bersama ding dan drop musik. | [Pelajaran 00][p00] |
| **Folder proyek** | Satu folder per video di `5_Projects/`, dengan isi yang selalu sama: `0_Source`, `1_Script`, `2_References`, `3_Storyboard`, `4_Frames`, `5_Clips`, `6_Edit` (suara di `6_Edit/1_Audio`), dan `99_Output`. | [Pelajaran 05][p05] |
| **Frame** | Satu gambar diam dalam video. Reel kita 30 frame per detik, jadi jumlah frame = durasi × 30. | [Pelajaran 00][p00] |
| **Frame pertama dan frame terakhir** | Gambar awal yang diberikan ke model video, dan gambar akhir yang dituju. Frame terakhir hanya dibuat kalau gerakan berakhir di komposisi yang berbeda. | [Pelajaran 02][p02] |

## G

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **Gambar acuan (*reference image*)** | Gambar yang diberikan ke model sebagai pegangan, misalnya potret Rani, supaya wajahnya sama di setiap shot. | [Pelajaran 02][p02] |
| **`GATE`, `NOTE`, `NEXT`** | Baris ringkasan yang diterima agent setelah kamu klik *Done, back to the agent*: status gerbang, catatanmu, dan langkah berikutnya. | [Pelajaran 07][p07] |
| **Gemini TTS** | Model suara yang mengubah naskah menjadi narasi (google/gemini-3.8-flash-lite-tts, lewat OpenRouter). Sekitar US$0,003 per take 20 detik. | [Pelajaran 00][p00] |
| **Gerbang** | Titik tempat alat berhenti sampai kamu setuju. Ada tiga: look (Gerbang 1), seluruh reel sebagai gambar (Gerbang 2), dan video (Gerbang 3). | [Pelajaran 00][p00] |
| **Git dan `git clone`** | Git mengunduh folder proyek dan mencatat versinya. `git clone` mengunduh seluruh repo kelas ke komputermu. | [Pelajaran 04][p04] |
| **GitHub** | Situs tempat repo kelas disimpan. | [Pelajaran 00][p00] |
| **Golden hour** | Cahaya oranye keemasan menjelang matahari terbenam. Dilarang di look reel contoh, supaya semua shot tetap satu sore yang cerah. | [Pelajaran 03][p03] |
| **gpt-image-2** | Model gambar yang kita pakai lewat kie.ai, untuk style frame, lembar referensi, storyboard, dan frame. 10 kredit per gambar 2K, tanpa persetujuan biaya. | [Pelajaran 00][p00] |
| **Grade** | Perlakuan atau olahan warna. Satu grade untuk semua shot membuat reel terasa satu film, tapi grade tidak bisa memperbaiki gambar yang cahayanya salah. | [Pelajaran 05][p05] |
| **`graphic`** | Kategori shot untuk peta, angka, atau teks. | [Pelajaran 06][p06] |
| **`graphics`** | Baris di blok look yang mengatur gaya teks dan grafis: font, warna aksen, dan posisi caption. | [Pelajaran 07][p07] |

## H

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **Halaman review** | Halaman web di komputermu sendiri (`vg review`) tempat kamu melihat look, lembar referensi dan reel, memilih take, dan menulis catatan. Halaman ini milikmu; agent tidak boleh mengklik tombolnya. | [Pelajaran 02][p02] |
| **Halusinasi** | Saat AI menyampaikan sesuatu yang tidak benar dengan nada yakin. Karena itu harga, jarak, dan nama selalu dicek manusia. | [Pelajaran 01][p01] |
| **Hard cut** | Lihat **Potong keras**. | [Pelajaran 10][p10] |
| **Harness** | Rangka kerja: kumpulan instruksi (skill) dan alat (vg) yang membuat agent bekerja dengan urutan yang sama setiap kali. | [Pelajaran 00][p00] |
| **HDR look** | Tampilan foto yang diproses berlebihan. Dilarang di prompt style frame kita. | [Pelajaran 03][p03] |
| **Hold** | Diam sebentar di akhir gerakan kamera. Prompt video menulisnya sebagai *eases out and holds*. | [Pelajaran 02][p02] |
| **Homebrew (`brew`)** | "Toko aplikasi" untuk Terminal: memasang program dengan satu perintah, misalnya `brew install ffmpeg`. | [Pelajaran 04][p04] |
| **Hook** | Pembuka di 2 detik pertama yang membuat orang berhenti menggulir. Hook berjanji, dan janjinya harus ditepati. | [Pelajaran 00][p00] |

## I

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **Image-to-image** | Membuat gambar baru dengan gambar lain sebagai acuan, misalnya lembar putar Rani yang dibuat dari potretnya. | [Pelajaran 08][p08] |
| **`install.sh`** | Skrip persiapan yang dijalankan dengan `bash install.sh`. Ia memeriksa alat, membuat `.env`, menghubungkan skill untuk Claude Code, lalu menjalankan `vg doctor`. Aman dijalankan ulang. | [Pelajaran 04][p04] |

## J

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **JSON** | Format teks untuk data yang tersusun rapi sebagai pasangan nama dan nilai, bisa dibaca manusia dan komputer. `Shotlist.json` dan `Edit_Spec.json` memakai format ini. | [Pelajaran 06][p06] |

## K

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **K (Kelvin)** | Satuan warna cahaya. Di kelas ini, cahaya siang yang netral ditulis sekitar 5500 K, dan grade reel contoh memakai 5600 K. | [Pelajaran 03][p03] |
| **Kartu penutup** | Lihat **End card**. | [Pelajaran 06][p06] |
| **Kecerdasan buatan** | Lihat **AI**. | [Pelajaran 01][p01] |
| **Kesinambungan (*continuity*)** | Semua shot terasa berasal dari satu dunia dan satu waktu: wajah, pakaian, arah dan warna cahaya, jam, tempat, dan rumah tetap sama. Dicek saat masih gambar, sebelum video. | [Pelajaran 08][p08] |
| **kie.ai** | Layanan tempat alat vg memanggil model gambar dan video, dibayar dengan kredit. | [Pelajaran 00][p00] |
| **Klip** | Potongan video hasil model video, misalnya `Clip_S05_v1.mp4` di `5_Clips/`. Klip kita pendek, paling lama 8 detik, dengan satu gerakan kamera. Di rencana edit, klip AI ditulis sebagai segmen `clip`. | [Pelajaran 00][p00] |
| **Kode persetujuan** | Kode acak 4 digit yang diminta alat saat menyetujui di mode terminal. Hanya manusia yang mengetiknya, di terminalnya sendiri; agent tidak bisa. | [Pelajaran 00][p00] |
| **Kredit** | Satuan bayar di kie.ai. Satu gambar 10 kredit, satu klip video 8 detik di 1080p 35 kredit. | [Pelajaran 00][p00] |
| **Kunci API** | Lihat **API key**. | [Pelajaran 04][p04] |
| **Kurva kenyaringan** | Daftar kenyaringan musik per setengah detik dari `vg audio curve`. Dipakai untuk menemukan drop. | [Pelajaran 09][p09] |

## L

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **Latihan** | Lihat **Training**. | [Pelajaran 01][p01] |
| **Ledger (`project.json`)** | Buku catatan biaya proyek: setiap gambar dan klip, versinya, kredit terpakai, dan setiap persetujuan. Hanya alat yang menulisnya. | [Pelajaran 05][p05] |
| **Lembar putar (*turnaround*)** | Satu gambar berisi empat tampilan karakter: depan, tiga perempat, samping, dan belakang. Dibuat dari potret referensi. | [Pelajaran 03][p03] |
| **Lembar referensi (*reference sheet*)** | Gambar acuan wajah, tempat, atau produk yang dibuat sekali lalu dipakai berulang, supaya tampilannya sama di setiap shot. | [Pelajaran 02][p02] |
| **libass** | Bagian FFmpeg untuk cara cadangan membuat subtitle. `warn ffmpeg libass` di `vg doctor` boleh dibiarkan. | [Pelajaran 04][p04] |
| **`lifestyle_broll`** | Kategori shot: suasana hidup di tempat itu, di bawah narasi. Contohnya S06: Rani berjalan di boulevard dengan mulut tertutup. | [Pelajaran 06][p06] |
| **Lip-sync** | Gerak bibir yang cocok dengan suara. Bagian paling rapuh dari video AI, jadi orang di klip kita tidak bicara. | [Pelajaran 09][p09] |
| **`live-tested`** | Tanda di daftar model bahwa model itu sudah dicoba dengan pembayaran nyata. | [Pelajaran 02][p02] |
| **LOCKS** | Bagian prompt video yang menyebut apa yang tidak boleh berubah, misalnya rumahnya tetap persis seperti di frame pertama. | [Pelajaran 02][p02] |
| **Look** | Satu arah visual untuk seluruh reel: `world`, `light`, `grade`, `graphics`, dan 2–3 style frame. Disetujui di Gerbang 1. | [Pelajaran 00][p00] |
| **`look_refs`** | Pengaturan untuk mengecualikan grafis datar, seperti peta, dari acuan style frame otomatis: `"look_refs": false`. | [Pelajaran 07][p07] |
| **LUFS** | Satuan kekerasan suara yang dipakai platform video. Reel kita disamakan ke sekitar −14 LUFS. | [Pelajaran 00][p00] |
| **Lyria** | Model musik (google/lyria-3-clip-preview, lewat OpenRouter). Sekitar US$0,04 per klip 30 detik. | [Pelajaran 00][p00] |

## M

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **Model** | Hasil latihan AI: pola yang tersimpan sebagai angka. Kita memakai lima model, masing-masing untuk satu jenis hasil. | [Pelajaran 00][p00] |
| **Model bahasa** | Model yang dilatih dengan teks dan menulis satu kata demi satu kata, misalnya Claude. | [Pelajaran 01][p01] |
| **Motion graphic (`mg`)** | Grafis bergerak yang dibuat saat edit, misalnya peta. Lihat juga **`ai`, `real`, `mg`**. | [Pelajaran 06][p06] |
| **`music.at`** | Detik di reel saat musik mulai masuk. Rumusnya: waktu jawaban di reel − waktu drop di lagu. Di reel contoh 3,27, jadi drop di detik 18,5 lagu jatuh di sekitar detik 21,8 reel. | [Pelajaran 09][p09] |

## N

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **Narasi** | Suara narator yang membawa cerita, dibuat dari naskah dengan Gemini TTS. Di kelas ini narasi selalu berupa voice-over. | [Pelajaran 00][p00] |
| **Noise** | Bintik acak seperti layar TV tanpa siaran. Model gambar mulai dari noise, lalu membuangnya sedikit demi sedikit sampai gambarnya cocok dengan prompt. | [Pelajaran 02][p02] |

## O

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **OpenRouter** | Layanan tempat alat vg memanggil model suara dan musik, dibayar dalam dolar. | [Pelajaran 00][p00] |
| **`output`** | Kolom di rencana edit berisi nama file final, misalnya `Contoh_Tebak_Harga_v1.0.mp4`. Untuk revisi, ganti nama ini ke versi baru; alat menolak menimpa file yang sudah ada. | [Pelajaran 12][p12] |

## P

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **Panel storyboard** | Satu gambar rencana 9:16 untuk satu shot AI. Dibingkai di awal aksi, bukan di puncaknya. | [Pelajaran 05][p05] |
| **Penghitung** | Lihat **Counter**. | [Pelajaran 12][p12] |
| **`photo_move`** | Gerak pelan di atas foto diam saat edit. Gratis dan aman, dipakai kalau klien tidak mengizinkan fotonya digerakkan model video. | [Pelajaran 08][p08] |
| **Piksel** | Titik terkecil sebuah gambar. Reel kita 1080×1920 piksel. | [Pelajaran 00][p00] |
| **Pilot** | Klip percobaan pertama. Video selalu dimulai dari satu klip pilot; tonton dulu, baru putuskan sisanya. | [Pelajaran 00][p00] |
| **Potong keras (*hard cut*)** | Gambar langsung berganti tanpa efek. Pilihan utama, tepat sebelum frasa baru dimulai. | [Pelajaran 10][p10] |
| **Potret referensi** | Gambar setengah badan karakter, menghadap kamera, latar abu-abu polos, cahaya rata. Ini jangkar identitas wajahnya. | [Pelajaran 01][p01] |
| **`project.json`** | Lihat **Ledger**. | [Pelajaran 05][p05] |
| **`promise` dan `pays_off`** | Kolom di shot list. `promise` berisi janji hook; `pays_off` ditaruh di shot yang menepatinya, berisi id hook. `vg validate` memberi peringatan kalau ada janji tanpa penepat. | [Pelajaran 06][p06] |
| **Prompt** | Perintah atau permintaan dalam bentuk teks untuk model. Prompt yang baik spesifik dan memakai kata yang bisa diukur. | [Pelajaran 01][p01] |
| **Prompt video (`video_prompt`)** | Prompt yang hanya menjelaskan gerak: satu gerakan kamera, cahaya, suara sekitar, dan LOCKS. Ditulis agent di kolom `video_prompt` di `Shotlist.json`. | [Pelajaran 02][p02] |
| **Provider** | Layanan yang menjalankan model, di sini kie.ai. Klip yang gagal di provider tetap memakai persetujuannya. | [Pelajaran 11][p11] |
| **Push-in (`push_in`)** | Kamera maju pelan, misalnya menuju pintu depan. | [Pelajaran 02][p02] |
| **Python** | Bahasa pemrograman yang menjalankan alat vg. Butuh versi 3.9 atau lebih baru. | [Pelajaran 00][p00] |

## Q

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **QC (*quality control*)** | Pemeriksaan mutu, misalnya dengan daftar cek sebelum kirim. Hasil pemeriksaan klip dicatat agent di `6_Edit/QC_Review.md`. | [Pelajaran 11][p11] |

## R

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **Reel** | Video pendek vertikal untuk media sosial. Reel contoh kita 9:16, sekitar 28 detik. | [Pelajaran 00][p00] |
| **Reference sheet** | Lihat **Lembar referensi**. | [Pelajaran 07][p07] |
| **REFUSED** | Awal pesan saat alat vg menolak sebuah langkah, misalnya karena gerbangnya belum disetujui atau batas biaya terlewati. Penolakan terjadi sebelum ada kredit terpakai. | [Pelajaran 05][p05] |
| **Render** | Punya dua arti. Pertama, gambar 3D arsitek yang terlalu mulus, yang kita hindari dengan *not a render*. Kedua, proses menyusun gambar dan suara menjadi file video, misalnya render animatic. | [Pelajaran 03][p03] |
| **Renderer** | Program penggambar caption dan grafis di alat vg. Memakai Swift, karena itu kelas ini butuh Mac. | [Pelajaran 04][p04] |
| **Repo** | Folder proyek yang disimpan di GitHub. Repo kelas berisi alat dan kelasnya sekaligus. | [Pelajaran 00][p00] |
| **Reveal** | Saat sesuatu dibuka atau diperlihatkan, misalnya jawaban harga. Shot seperti ini bisa butuh frame terakhir. | [Pelajaran 03][p03] |
| **`room_reveal`** | Kategori shot: ruang asli dari foto klien. | [Pelajaran 06][p06] |
| **`rules`** | Bagian di `Shotlist.json` berisi aturan klien: label wajib, catatan hukum, dan larangan. Agent wajib mematuhinya di setiap shot. | [Pelajaran 03][p03] |

## S

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **S&K (syarat dan ketentuan)** | Catatan wajib di bawah harga, misalnya "*S&K berlaku, dapat berubah." | [Pelajaran 00][p00] |
| **Segmen (`segments`)** | Urutan potongan gambar di rencana edit, masing-masing dengan durasinya. Jenisnya `still`, `background`, dan `clip`. | [Pelajaran 09][p09] |
| **Shot** | Satu potongan gambar tanpa putus. Satu ide per shot. | [Pelajaran 00][p00] |
| **Shot list** | Daftar semua shot: detik, yang terlihat, dan teks di layar. Ditulis agent ke `1_Script/Shotlist.json`. | [Pelajaran 00][p00] |
| **`Shotlist.json`** | File rencana proyek di `1_Script/`. Isinya nama proyek dan format, `rules`, `look`, tokoh dan lembar referensinya, lalu daftar shot. Ditulis agent dan dicek dengan `vg validate`. | [Pelajaran 03][p03] |
| **`size` (ukuran shot)** | Label ukuran shot, dari paling dekat ke paling lebar: `ecu`, `cu`, `mcu`, `ms`, `mws`, `ws`, `ews`. | [Pelajaran 06][p06] |
| **Skill** | File instruksi di `1_Skills/` yang menjelaskan cara kerja kita tahap demi tahap, seperti SOP di kantor. Titik mulainya `1_Skills/vg-director/SKILL.md`. | [Pelajaran 00][p00] |
| **`still`** | Jenis segmen di rencana edit: gambar diam dengan dorongan kamera pelan (`zoom`). | [Pelajaran 10][p10] |
| **Storyboard** | Urutan gambar rencana, satu panel per shot. | [Pelajaran 02][p02] |
| **Style frame** | Gambar contoh yang menunjukkan look seluruh reel. Dua atau tiga style frame disetujui di Gerbang 1, lalu jadi acuan semua gambar lain. | [Pelajaran 02][p02] |
| **Suara sekitar** | Lihat **Ambience**. | [Pelajaran 02][p02] |
| **Sumber gambar** | Lihat **`ai`, `real`, `mg`**. | [Pelajaran 06][p06] |
| **Swift dan `swiftc`** | Swift adalah bahasa pemrograman buatan Apple yang dipakai renderer caption dan grafis. `swiftc` adalah penerjemahnya, dan ikut terpasang bersama Xcode Command Line Tools. | [Pelajaran 04][p04] |

## T

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **Take** | Satu hasil dari satu kali pembuatan: gambar, suara, atau klip. Membuat ulang berarti take baru; untuk video, setiap take butuh persetujuan sendiri. | [Pelajaran 00][p00] |
| **Tap** | Efek suara kecil saat judul atau callout muncul. | [Pelajaran 09][p09] |
| **Teal-orange** | Olahan warna biru-oranye khas film. Dilarang di grade reel contoh. | [Pelajaran 07][p07] |
| **Terminal** | Aplikasi Mac untuk memberi perintah dengan mengetik, bukan mengklik. Buka dengan Cmd + Spasi, ketik "Terminal", lalu Enter. | [Pelajaran 00][p00] |
| **Tick** | Efek suara saat angka berjalan (counter). | [Pelajaran 09][p09] |
| **Timeout** | Waktu tunggu habis sebelum hasil selesai. Ambil hasilnya dengan `vg resume`, jangan kirim ulang, supaya tidak membayar dua kali. | [Pelajaran 00][p00] |
| **Title_Case_With_Underscores** | Pola nama file: huruf besar di awal kata, garis bawah pengganti spasi, tanpa karakter aneh. | [Pelajaran 05][p05] |
| **Token** | Potongan kata yang ditulis model bahasa satu per satu. | [Pelajaran 01][p01] |
| **Training (latihan)** | Proses AI belajar: menebak, tebakannya dicek, lalu diperbaiki, miliaran kali. | [Pelajaran 01][p01] |
| **`transition_in`** | Cara sebuah segmen masuk di rencana edit: `cut`, `whip`, atau `flash`. | [Pelajaran 10][p10] |
| **TTS (*text-to-speech*)** | Pengubah teks menjadi suara. Model TTS membaca teks persis seperti tertulis, jadi angka di naskah ditulis seperti diucapkan. | [Pelajaran 00][p00] |
| **Turnaround** | Lihat **Lembar putar**. | [Pelajaran 08][p08] |

## V

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **Veo 3.1 Lite** | Model video yang membuat gambar yang sudah disetujui bergerak (`veo-3-1-lite` di kie.ai). 35 kredit per klip 8 detik di 1080p, 30 kredit di 720p. | [Pelajaran 00][p00] |
| **Versi (`_v1` dan `_v1.0`)** | Alat memberi versi `_v1`, `_v2` pada media buatannya. Kamu dan agent memberi versi `_v1.0`, `_v1.1`, `_v2.0` pada dokumen dan hasil akhir, dan versi yang sudah dikirim tidak pernah ditimpa. | [Pelajaran 05][p05] |
| **Verticals straight** | Garis tegak bangunan tidak miring. Ditulis di prompt gambar dan prompt video. | [Pelajaran 02][p02] |
| **vg** | Alat Python di `2_Tools/vg/` yang memanggil model, mencatat biaya, dan menolak video yang belum kamu setujui. `vg <perintah>` adalah singkatan dari `python3 2_Tools/vg/vg.py <perintah>`. | [Pelajaran 00][p00] |
| **`VG_BUDGET_PROJECT` dan `VG_MAX_PER_CALL`** | Batas biaya di `.env`: total maksimal satu proyek, dan biaya maksimal satu permintaan. Hanya kamu yang boleh mengubahnya. | [Pelajaran 04][p04] |
| **Voice-over** | Suara narator terdengar, tapi orangnya tidak terlihat bicara. Orang di klip kita menutup mulut. | [Pelajaran 02][p02] |

## W

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **Whip** | Transisi kabur gerak cepat di kedua sisi potongan. Dipakai saat pindah tempat, selalu dengan whoosh. | [Pelajaran 06][p06] |
| **Whoosh** | Efek suara untuk potongan whip, mulai sekitar 0,28 detik sebelum potongan. | [Pelajaran 09][p09] |
| **`world` dan `light`** | Dua baris di blok look. `world` berisi satu tempat dan satu waktu; `light` berisi arah dan sifat cahaya. | [Pelajaran 07][p07] |

## X

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **Xcode Command Line Tools** | Paket alat dasar dari Apple, berisi `swiftc`, Git, dan Python. Dipasang dengan `xcode-select --install`. | [Pelajaran 04][p04] |

## Z

| Istilah | Arti | Pertama muncul |
|---|---|---|
| **`zoom`** | Dorongan kamera pelan di atas gambar diam, ditulis di rencana edit. Contohnya `"zoom": [1.22, 1.0]` di S10. | [Pelajaran 10][p10] |

## Perintah vg

Semua perintah dijalankan dari folder repo dengan `python3 2_Tools/vg/vg.py`. Ganti `NAMA_PROYEK` dengan nama folder proyekmu di `5_Projects/`. Sebagian besar dijalankan agent. Yang kamu jalankan sendiri: `bash install.sh`, `vg doctor`, halaman review, dan perintah persetujuan saat alat memintanya.

| Perintah (singkat) | Gunanya | Dibahas di |
|---|---|---|
| `vg doctor` | memeriksa alat, `.env`, kunci, dan saldo | [Pelajaran 04][p04] |
| `vg models` | daftar model gambar dan video yang dikenal alat | [Pelajaran 02][p02] |
| `vg credits` | saldo kredit kie.ai | [Pelajaran 05][p05] |
| `vg new` | membuat folder proyek baru dari templat | [Pelajaran 05][p05] |
| `vg status -p NAMA_PROYEK` | setiap gambar dan klip, versinya, kredit terpakai, dan status gerbang | [Pelajaran 05][p05] |
| `vg estimate -p NAMA_PROYEK --stage video` | biaya video yang belum dibuat | [Pelajaran 05][p05] |
| `vg validate -p NAMA_PROYEK` | memeriksa `Shotlist.json` | [Pelajaran 06][p06] |
| `vg image -p NAMA_PROYEK --stage look` | membuat style frame; juga `--stage refs`, `storyboard`, dan `frames`. Berbayar, tanpa persetujuan biaya. | [Pelajaran 07][p07], [Pelajaran 08][p08] |
| `vg review -p NAMA_PROYEK` | membuka halaman review | [Pelajaran 07][p07] |
| `vg approve look -p NAMA_PROYEK` | Gerbang 1: menyetujui look. Kamu yang mengetik kodenya. | [Pelajaran 07][p07] |
| `vg image -p NAMA_PROYEK --target ... --new-take` | membuat take baru untuk satu gambar tanpa menimpa yang lama | [Pelajaran 08][p08] |
| `vg select -p NAMA_PROYEK --target ... --version 2` | memilih versi yang dipakai tahap berikutnya | [Pelajaran 08][p08] |
| `vg audio voice`, `vg audio music` | membuat take narasi dan take musik lewat OpenRouter | [Pelajaran 09][p09] |
| `vg audio curve` | membaca kurva kenyaringan musik dan mencari drop | [Pelajaran 09][p09] |
| `vg audio sfx` | membuat empat efek suara, gratis | [Pelajaran 09][p09] |
| `vg edit animatic -p NAMA_PROYEK` | merender animatic, gratis | [Pelajaran 10][p10] |
| `vg approve visuals -p NAMA_PROYEK` | Gerbang 2: menyetujui seluruh reel sebagai gambar. Kamu yang mengetik kodenya. | [Pelajaran 10][p10] |
| `vg approve video -p NAMA_PROYEK --shots S01 --confirm 35` | Gerbang 3: menyetujui biaya klip. Kamu yang mengetik kodenya. | [Pelajaran 11][p11] |
| `vg video -p NAMA_PROYEK --shots S01` | membuat klip yang sudah disetujui; `--all` untuk semua yang disetujui | [Pelajaran 11][p11] |
| `vg resume -p NAMA_PROYEK` | mengambil hasil tugas yang timeout, tanpa mengirim ulang | [Pelajaran 11][p11] |
| `vg edit final -p NAMA_PROYEK` | edit final ke `99_Output/`; dengan `--draft`, draft bernomor ke `6_Edit/` | [Pelajaran 12][p12] |

Kembali ke [daftar kelas](README.md).

[p00]: 1_Pelajaran/Pelajaran_00_Mulai_Di_Sini_v1.0.md
[p01]: 1_Pelajaran/Pelajaran_01_Apa_Itu_AI_v1.0.md
[p02]: 1_Pelajaran/Pelajaran_02_Model_Dan_Agent_v1.0.md
[p03]: 1_Pelajaran/Pelajaran_03_Cara_Berpikir_Dengan_AI_v1.0.md
[p04]: 1_Pelajaran/Pelajaran_04_Persiapan_Alat_v1.0.md
[p05]: 1_Pelajaran/Pelajaran_05_Cara_Kerja_Harness_v1.0.md
[p06]: 1_Pelajaran/Pelajaran_06_Brief_Ke_Shot_List_v1.0.md
[p07]: 1_Pelajaran/Pelajaran_07_Look_Dan_Review_v1.0.md
[p08]: 1_Pelajaran/Pelajaran_08_Karakter_Storyboard_Frame_v1.0.md
[p09]: 1_Pelajaran/Pelajaran_09_Audio_Dulu_v1.0.md
[p10]: 1_Pelajaran/Pelajaran_10_Edit_Plan_Dan_Animatic_v1.0.md
[p11]: 1_Pelajaran/Pelajaran_11_Video_Dan_Gerbang_Biaya_v1.0.md
[p12]: 1_Pelajaran/Pelajaran_12_Edit_Final_Dan_Kirim_v1.0.md
[p13]: 1_Pelajaran/Pelajaran_13_Kesalahan_Yang_Kami_Buat_v1.0.md
