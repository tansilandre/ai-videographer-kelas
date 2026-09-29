# Checklist per Tahap

Satu checklist untuk setiap tahap. Centang semua kotak sebelum pindah ke tahap berikutnya. Kalau ada satu yang belum, berhenti dan perbaiki dulu. Memperbaiki di tahap awal selalu lebih murah daripada di tahap akhir.

**Cara membaca perintah di sini.** Alatnya dijalankan dari folder repo dengan `python3 2_Tools/vg/vg.py <perintah>`. Supaya pendek, di bawah ini ditulis `vg <perintah>`. Tidak ada perintah bernama `vg` di komputermu: yang dijalankan selalu versi lengkapnya. Ganti `NAMA_PROYEK` dengan nama folder proyekmu di `5_Projects/`.

Sebagian besar perintah dijalankan oleh agent. Yang kamu kerjakan sendiri hanya persiapan (tiga langkah di bawah) dan perintah doctor. Halaman review dibuka oleh agent, tapi yang memakainya kamu: dengan `VG_APPROVAL_MODE=page`, ketiga gerbang adalah klikmu di sana. Kapan pun bingung, `vg next -p NAMA_PROYEK` mencetak satu langkah berikutnya.

Alurnya: **1** Brief dan shot list → **2** Look (Gerbang 1) → **3** Karakter dan frame → **4** Audio → **5** Animatic (Gerbang 2) → **6** Video (Gerbang 3) → **7** Edit final.

---

## Sebelum mulai · Persiapan

Tiga langkah dari [Panduan WorkBuddy](../5_WorkBuddy/Panduan_WorkBuddy_v1.1.md), lalu doctor:

- [ ] **1 · WorkBuddy terpasang.** Kamu masuk dengan Google atau GitHub, dan memilih model **glm-5.3-flash**. Model ini sudah ada di WorkBuddy: tidak perlu akun atau kunci lain.
- [ ] **2 · AI-nya sudah memasang.** Kamu memilih folder kerja dan mengirim satu pesan dari Panduan. AI-nya mengunduh folder kelas dan menjalankan `bash setup.sh` sampai selesai. Kamu hanya mengklik izinkan, mengklik Install di jendela Apple, atau menempel satu baris Homebrew di Terminal kalau diminta.
- [ ] **3 · Kunci tersimpan, WorkBuddy dibuka ulang.** Kamu sendiri yang menempel kunci kie.ai (dan OpenRouter) di halaman **Setup AI Videographer**, dengan pilihan **Klik di halaman review**, lalu klik **Simpan**. Halaman itu menunjukkan saldo kie.ai-mu. Lalu kamu menutup WorkBuddy (Cmd + Q), membukanya lagi, membuka folder yang disebut di akhir setup, dan memilih Expert **AI Videographer**.
- [ ] Kamu tidak pernah menempel API key ke chat, dan agent tidak pernah mengubah `.env`.
- [ ] Disarankan: API key kie.ai khusus untuk kelas ini, dengan batas kredit total (dibuat di https://kie.ai/api-key).
- [ ] Doctor bersih, tanpa baris FAIL, dengan baris `ok approval mode page` dan (untuk WorkBuddy) `ok skills (WorkBuddy)`. Di WorkBuddy klik quick prompt **Cek setup**, atau jalankan sendiri dari folder kelas:

```bash
python3 2_Tools/vg/vg.py doctor
```

Memakai Claude Code? Ganti langkah 1–3 dengan Langkah 1–8 di [Pelajaran 04](../1_Pelajaran/Pelajaran_04_Persiapan_Alat_v1.2.md): pasang alatnya sendiri, jalankan `bash install.sh`, lalu tempel kunci di halaman setup (`python3 2_Tools/vg/vg.py setup`) atau isi `.env` sendiri.

---

## Tahap 1 · Brief dan shot list

- [ ] Brief asli ada di folder `0_Source` proyek dan tidak diubah sama sekali.
- [ ] Aturan klien tercatat di bagian `rules` shot list (label, catatan S&K, larangan merek).
- [ ] Sumber gambar setiap bagian jelas: foto asli, grafis, atau AI. Rumah yang dijual = foto asli klien (kecuali di latihan fiktif).
- [ ] Hook ada di 2 detik pertama. Kata pertama terdengar sebelum detik 0,8.
- [ ] Satu ide per shot.
- [ ] Janji hook tercatat (`promise`), dan ada shot yang menepatinya (`pays_off`).
- [ ] Rumah atau produk mendapat waktu layar yang cukup. Untuk tur properti: rumah minimal 40% dari durasi.
- [ ] Potongan setiap 1,5–3 detik untuk gambar rumah dan lingkungan. Tidak ada tiga potongan berturut-turut dengan ukuran shot dan gerak kamera yang sama.
- [ ] Semua kata yang diucapkan datang dari narasi voice-over. Orang di layar mulutnya tertutup dan tidak bicara di depan kamera.
- [ ] Blok `look` sudah ditulis: dunia, cahaya, grade warna, gaya grafis.
- [ ] Fakta seperti harga, jarak dan nama sudah kamu cek sendiri ke brief.
- [ ] Validate tidak menunjukkan error di bagian yang ditulis tahap ini. Kolom storyboard, frame dan `video_prompt` memang masih kosong.

```bash
vg validate -p NAMA_PROYEK
```

---

## Tahap 2 · Look — GERBANG 1

- [ ] 2–3 *style frame* (gambar contoh gaya seluruh reel) sudah dibuat, dan agent sudah melihat setiap gambar.
- [ ] Satu dunia, satu waktu, arah matahari sama, satu grade warna.
- [ ] Tidak ada teks, logo atau tulisan aneh di gambar. Teks ditambahkan di edit.
- [ ] Kamu melihat semuanya di halaman review, memilih *take* (versi gambar) terbaik, dan menulis catatan di gambar yang perlu diperbaiki.
- [ ] Agent hanya memperbaiki yang kamu catat, lalu menunjukkan lagi.
- [ ] Kamu bisa menjawab "ya" untuk pertanyaan ini: *apakah ini look seluruh reel?*
- [ ] Kamu mengklik **Approve look** di halaman review, lalu **Done, back to the agent**. (Mode `terminal`: kamu menjalankan perintah `approve look` di terminalmu sendiri dan mengetik kode 4 digit.)
- [ ] Status menunjukkan look sudah disetujui.

```bash
vg image -p NAMA_PROYEK --stage look
vg review -p NAMA_PROYEK --detach
vg next -p NAMA_PROYEK
vg status -p NAMA_PROYEK
```

Ingat: mengubah style frame atau teks look membatalkan persetujuan ini.

---

## Tahap 3 · Karakter dan frame

- [ ] Kalau ada presenter: potret referensi dan lembar putar sudah dibuat, dan wajahnya sama di setiap gambar.
- [ ] Presenter dibuat AI dari nol, bukan dari wajah orang asli tanpa izin.
- [ ] Satu panel storyboard untuk setiap shot AI, 9:16, dibingkai di awal gerakan, bukan di puncaknya.
- [ ] Frame pertama biasanya memakai panel storyboard. Frame terakhir hanya dibuat kalau akhir shot memang berbeda dan perlu dikunci, misalnya kamera maju sampai komposisinya berubah.
- [ ] Konsisten antar shot: arah cahaya, warna, waktu, pakaian.
- [ ] Gambar dengan cahaya salah, wajah seperti plastik, atau detail karangan dibuat ulang sekarang, bukan nanti.
- [ ] Rumah yang dijual = foto asli klien. Di latihan fiktif rumahnya AI dan diberi label.

```bash
vg image -p NAMA_PROYEK --stage refs
vg image -p NAMA_PROYEK --stage storyboard
vg image -p NAMA_PROYEK --stage frames
```

---

## Tahap 4 · Audio

- [ ] Naskah narasi pendek dan terdengar seperti bicara. Satu kalimat atau satu petunjuk per frasa. Titik, titik dua, tanda tanya atau tanda seru ada di tempat potongan gambar (koma tidak memecah frasa).
- [ ] Angka dan nama ditulis seperti diucapkan (misalnya "satu koma tiga M-an").
- [ ] Beberapa take suara sudah dibuat, dan **kamu** memilih suaranya dengan telinga.
- [ ] Satu suara untuk seluruh reel, sebagai voice-over. Orang di layar mulutnya tertutup.
- [ ] Musik: tenang di bawah suara, naik, jeda setengah ketukan, lalu drop tepat di jawaban. Take dengan bagian mati ditolak.
- [ ] Titik drop musik sudah dicari, dan `music.at` = waktu jawaban − waktu drop di lagu. Contoh reel Tebak Harga: drop di detik 18,5 lagu, `music.at` = 3,27, jadi drop jatuh di detik 21,8.
- [ ] Efek suara ada di bawah suara narasi: whoosh untuk whip, tap saat judul muncul, ding untuk jawaban, tick untuk penghitung.
- [ ] Reel berakhir di stop musik, bukan memudar ke sunyi.

```bash
vg audio voice -p NAMA_PROYEK --text-file 1_Script/Narasi.txt --voices Callirrhoe,Leda --style "A warm, natural Indonesian voice-over for a short social video, conversational, not a newsreader."
vg audio music -p NAMA_PROYEK --prompt-file 1_Script/Music_Prompt.txt --label Quiz_Pop --takes 3
vg audio curve -p NAMA_PROYEK --file 6_Edit/1_Audio/Music_Take_Quiz_Pop_v1.mp3
vg audio sfx -p NAMA_PROYEK
```

Nama file dan label di atas diambil dari reel Tebak Harga. Di proyekmu, pakai file naskah, prompt musik dan take musikmu sendiri (Pelajaran 09).

---

## Tahap 5 · Animatic — GERBANG 2

- [ ] Rencana edit (`6_Edit/Edit_Spec.json`) ditulis: waktu dipotong mengikuti frasa narasi, teks, peta, caption, transisi, efek suara.
- [ ] Animatic sudah dirender, dan agent menontonnya dulu sebelum menunjukkannya ke kamu.
- [ ] Kamu menontonnya sebagai penonton: satu dunia? Janjinya ditepati? Rumahnya cukup lama terlihat? Grafisnya satu gaya dan tidak menutupi wajah?
- [ ] Caption tidak pernah mendahului kata yang diucapkan. Periksa terutama harga.
- [ ] Tidak ada gambar beku: jumlah frame = durasi × 30.
- [ ] Transisi punya alasan: potong keras hampir di semua tempat, whip hanya saat pindah tempat, flash hanya sekali di jawaban.
- [ ] Label wajib ada, misalnya "ILUSTRASI RENCANA" dan "S&K berlaku".
- [ ] Setiap perbaikan menghasilkan animatic baru. Persetujuan ditolak kalau animatic terakhir tidak menunjukkan gambar dan rencana edit yang terbaru.
- [ ] Kamu mengklik **Approve reel** di bawah animatic, lalu **Done, back to the agent**. (Mode `terminal`: kamu menjalankan perintah `approve visuals` di terminalmu sendiri dan mengetik kodenya.)
- [ ] Status menunjukkan visuals sudah disetujui.

```bash
vg edit animatic -p NAMA_PROYEK
vg board -p NAMA_PROYEK
vg review -p NAMA_PROYEK --detach
vg next -p NAMA_PROYEK
vg status -p NAMA_PROYEK
```

Ingat: mengubah frame, teks, atau waktu di rencana edit membatalkan persetujuan ini.

---

## Tahap 6 · Video — GERBANG 3

- [ ] Prompt video hanya menjelaskan yang berubah: satu gerakan kamera dengan titik akhir dan jeda diam, cahaya, suara sekitar, dan apa yang tidak boleh berubah. Isi frame tidak dideskripsikan ulang.
- [ ] Orang di klip tidak bicara. Suaranya dari narasi.
- [ ] Validate bersih.
- [ ] Kamu sudah melihat bagian **Video** di halaman review: biaya per klip, dan kredit yang sudah terpakai dari batas proyekmu.
- [ ] Kamu mengklik **Approve** di **satu klip pilot** saja (contoh: *Approve · 35 credits* untuk satu klip 8 detik 1080p), membaca angka di kotak konfirmasi, lalu klik OK.
- [ ] Agent tidak pernah menyetujui sendiri: di mode `page`, `vg approve video` selalu ditolak. (Mode `terminal`: **kamu** menjalankan perintah dari agent di terminalmu sendiri dan mengetik kode 4 digit.)
- [ ] Klip pilot dibuat dan ditonton: cahaya cocok dengan tetangganya, kamera berakhir sesuai prompt, tidak ada yang bicara, tidak ada teks karangan.
- [ ] Untuk sisa klip: klik baru (per klip, atau *Approve all not made*), dengan total sisanya.
- [ ] Satu persetujuan = satu take. Klip yang gagal atau diulang butuh klik baru (*New take* untuk klip yang sudah jadi).
- [ ] Kalau waktu tunggu habis (*timeout*): `vg resume`, tidak pernah kirim ulang.
- [ ] Kalau alat menampilkan baris CHECK tentang target yang macet, **kamu** memeriksa dashboard kie.ai dulu sebelum ada yang dilepas atau diambil alih.
- [ ] Kalau alat menolak karena batas anggaran, kamu yang memutuskan. Agent tidak mengubah `.env`.

```bash
vg validate -p NAMA_PROYEK
vg board -p NAMA_PROYEK
vg estimate -p NAMA_PROYEK --stage video
vg credits
vg review -p NAMA_PROYEK --detach
vg next -p NAMA_PROYEK
vg video -p NAMA_PROYEK --shots S01
vg resume -p NAMA_PROYEK
```

---

## Tahap 7 · Edit final

- [ ] Draft dibuat dulu dan dicek, baru versi final.
- [ ] Caption tidak pernah mendahului kata yang diucapkan.
- [ ] Tidak ada gambar beku: jumlah frame = durasi × 30.
- [ ] Suara jelas di atas musik, sekitar −14 LUFS.
- [ ] Ada label "ILUSTRASI RENCANA" (atau label yang diminta klien) dan "S&K berlaku".
- [ ] Teks tidak menutupi wajah.
- [ ] File berversi di folder `99_Output` proyek, misalnya `Proyek_v1.0.mp4`. Versi yang sudah dikirim tidak pernah ditimpa: revisi = versi baru.

```bash
vg edit final -p NAMA_PROYEK --draft
vg edit final -p NAMA_PROYEK
```

Selesai? Bandingkan hasilmu dengan animatic yang kamu setujui di Gerbang 2. Kalau ada yang berbeda, cari tahu kenapa sebelum mengirim.
