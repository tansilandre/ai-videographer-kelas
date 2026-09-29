# Pelajaran 05 · Cara Kerja AI Videographer

## Tujuan

- Menjelaskan peran tiga pemain: kamu, agent, dan alat vg.
- Membaca hasil `vg next`, satu langkah berikutnya proyekmu.
- Menyebut tujuh tahap dan tiga gerbang, apa yang kamu periksa di setiap gerbang, dan cara menyetujuinya.
- Menemukan file apa pun di folder proyek, dan membaca arti namanya.
- Memahami kredit, batas biaya, dan buku catatan biaya (*ledger*).

## Kenapa ini penting

Kamu tidak perlu hafal perintah. Tapi kamu perlu tahu posisimu: tahap berapa, apa yang ditunggu, dan berapa yang sudah terpakai. Dengan peta ini, kamu mengarahkan agent, bukan sekadar menonton.

## Tiga pemain, satu tim

| Pemain | Tugasnya |
|---|---|
| Kamu | Menulis brief, memilih hasil terbaik, dan menyetujui. |
| Agent AI (WorkBuddy dengan Expert AI Videographer, atau Claude Code) | Membaca skill, menulis rencana dan prompt, menjalankan alat, lalu memeriksa hasilnya. |
| Alat vg | Memanggil model, mencatat biaya, dan menolak video yang belum kamu setujui. |

Kamu bicara ke agent dengan bahasa biasa. Misalnya, setelah brief klien ada di folder proyek:

> Buat reel dari brief di 5_Projects/.../0_Source

Agent lalu membaca `1_Skills/vg-director/SKILL.md`, file instruksi yang menyebut semua tahap secara berurutan, dan mulai bekerja. Ia menjalankan alat vg dengan perintah `python3 2_Tools/vg/vg.py <perintah>`. Di kelas ini kita singkat menjadi `vg <perintah>`, tapi yang diketik selalu versi lengkapnya.

Agent pintar, tapi bisa salah. Alat vg tidak pintar, tapi tegas: langkah mahal yang belum kamu setujui ditolak, dengan pesan berawalan `REFUSED:`.

### Satu langkah sekali: `vg next`

Expert AI Videographer di WorkBuddy punya satu kebiasaan: sebelum setiap langkah, ia bertanya ke alat.

```bash
python3 2_Tools/vg/vg.py next -p NAMA_PROYEK
```

Ganti `NAMA_PROYEK` dengan nama folder proyekmu di `5_Projects/`. `vg next` membaca rencana, buku catatan biaya, dan file di folder proyek, lalu mencetak satu langkah berikutnya. Ia tidak menjalankan atau membayar apa pun. Setiap baris diawali satu tanda:

| Tanda | Artinya |
|---|---|
| `STAGE` | posisi proyek sekarang, dan alasannya |
| `RUN` | satu perintah yang dijalankan sekarang |
| `WRITE` | file yang harus ditulis atau diperbaiki, dan skill yang dibaca dulu |
| `ASK` | berhenti: beri tahu atau tanya kamu, lalu tunggu jawabanmu |
| `THEN` | yang dilakukan sesudahnya, biasanya menjalankan `vg next` lagi |
| `DONE` | reel selesai |

Kadang muncul juga baris `NOTE`, berisi catatanmu dari halaman review yang harus dikerjakan agent.

Karena alat yang mengingat alurnya, model yang cepat dan murah seperti glm-5.3-flash cukup menjadi otak agent. Kamu juga boleh menjalankan `vg next` sendiri kapan saja, misalnya saat bertanya-tanya "sekarang kita di mana?".

## Tujuh tahap, tiga gerbang

Aturan emasnya: **gambar itu murah, video itu mahal.** Satu gambar 10 kredit. Satu klip video 8 detik 35 kredit. Jadi seluruh reel disetujui sebagai gambar dulu, baru dibuat bergerak.

| # | Tahap | Yang terjadi | Gerbang |
|---|---|---|---|
| 1 | Brief dan shot list | brief dipecah menjadi bagian cerita (*beat*), satu shot per beat | |
| 2 | Look | 2–3 *style frame* (gambar contoh gaya): satu dunia, satu cahaya, satu *grade* (olahan warna) | **1** · klik *Approve look* |
| 3 | Karakter dan frame | lembar referensi Rani, panel *storyboard*, frame pertama tiap shot | |
| 4 | Audio | narasi, musik, efek suara | |
| 5 | Animatic | seluruh reel sebagai gambar diam, dengan caption dan suara | **2** · klik *Approve reel* |
| 6 | Video | gambar yang disetujui dibuat bergerak, mulai dari satu klip pilot | **3** · klik *Approve* per klip, lalu konfirmasi |
| 7 | Edit final | klip, suara, caption, dan grafis disatukan | |

Di setiap gerbang alat berhenti sampai kamu bilang setuju. Sebelum look disetujui, tidak ada storyboard atau frame. Sebelum reel disetujui sebagai gambar, tidak ada video.

![Frame animatic S01: Rani di mobil](../2_Studi_Kasus/Tebak_Harga/1_Gambar/Frame_Hook.jpg)

*Satu frame dari animatic reel contoh (S01). Belum ada video: ini masih gambar diam, tapi judul dan caption sudah terpasang. Rani dibuat AI dari nol, bukan orang asli.*

### Cara kamu menyetujui

Di Gerbang 1 dan 2 kamu memeriksa di **halaman review**, halaman web di komputermu sendiri. Di sana kamu melihat look, lembar referensi, dan setiap beat. Kamu bisa mengganti *take* (versi hasil) dan menulis catatan di samping gambar. Klik **Done, back to the agent** kalau selesai. Agent membaca catatanmu, memperbaiki, lalu membuka halamannya lagi.

Di kelas ini kita memakai `VG_APPROVAL_MODE=page` di `.env` (Pelajaran 04). Artinya ketiga gerbang adalah klik di halaman itu:

- **Gerbang 1:** tombol **Approve look** di bawah style frame.
- **Gerbang 2:** tombol **Approve reel** di bawah animatic.
- **Gerbang 3:** di bagian **Video**, setiap klip menunjukkan biayanya, dengan tombol seperti **Approve · 35 credits**. Setelah diklik, halaman bertanya sekali lagi sebelum menyetujui.

Di mode ini perintah `vg approve` dari terminal selalu ditolak. Jadi agent tidak bisa menyetujui apa pun untukmu. Halaman review hanya milikmu: agent dilarang mengklik tombolnya.

Di WorkBuddy, agent membuka halaman ini dengan `vg review --detach`: halamannya tetap terbuka, tapi agent tidak ikut tertahan. Ia mengirimimu tautannya di chat. Kamu mengklik, lalu bilang di chat bahwa kamu sudah selesai. Agent membaca klik dan catatanmu dengan `vg next`.

Cara lain: mode `terminal`. Di sana halaman review menampilkan perintah persetujuan. Kamu menjalankannya di Terminal-mu sendiri, dan alat memintamu mengetik kode acak 4 digit. Ada juga mode `chat`, yang paling lemah: agent sendiri yang mencatat persetujuan setelah kamu bilang ya di chat.

Gerbang 3 paling ketat, karena di situ uang keluar. Aturannya:

- Mulai dari **satu klip pilot**. Tonton dulu, baru lanjut.
- **Setiap persetujuan membayar tepat satu take.** Klip gagal atau diulang butuh persetujuan baru: klik baru di halaman review.

## Folder proyek dan nama file

Setiap video punya satu folder di `5_Projects/`, dibuat agent dengan `vg new`. Namanya tanggal ditambah nama proyek, misalnya `5_Projects/<tanggal>_Tebak_Harga/`. Isinya selalu sama:

| Folder | Isi | Contoh dari reel Tebak Harga |
|---|---|---|
| `0_Source` | bahan asli klien, tidak pernah diubah | brief klien (di proyek nyata: juga foto rumahnya) |
| `1_Script` | rencana: `Shotlist.json` dan naskah | daftar shot S01 sampai S11 |
| `2_References` | style frame dan lembar referensi | potret dan lembar putar Rani |
| `3_Storyboard` | panel storyboard per shot | `SB_S01_v1.png` |
| `4_Frames` | frame pertama (dan terakhir) per shot | `Frame_S05_First_v1.png` |
| `5_Clips` | klip video | `Clip_S05_v1.mp4` |
| `6_Edit` | rencana edit, animatic, draft; suara di `1_Audio` | `Edit_Spec.json`, `1_Audio/Narration_Take_Callirrhoe_v1.wav` |
| `99_Output` | hasil akhir, siap dikirim | `Contoh_Tebak_Harga_v1.0.mp4` |

Di folder proyek juga ada `project.json` (buku catatan biaya, dibahas di bawah) dan papan review `Board_<nama proyek>.html`.

Catatan: di proyek nyata, rumah yang dijual adalah foto asli dari klien, ditaruh di `0_Source`, dan hanya kameranya yang bergerak. Di contoh kelas ini rumahnya gambar AI, karena klien dan proyeknya fiktif.

Aturan nama file:

- **Title_Case_With_Underscores**: huruf besar di awal kata, garis bawah pengganti spasi, tanpa karakter aneh.
- **Alat** memberi versi pada media buatannya: `_v1`, `_v2`, dan seterusnya. Jangan ubah nama ini dengan tangan.
- **Kamu dan agent** memberi versi pada dokumen dan hasil akhir: `_v1.0`, `_v1.1`, `_v2.0`.
- Hasil yang sudah dikirim tidak pernah ditimpa. Revisi disimpan sebagai versi baru.

## Kredit, batas biaya, dan buku catatan

Ada dua dompet:

- **Kredit kie.ai** untuk gambar dan video. Gambar gpt-image-2: 10 kredit per gambar 2K, tanpa perlu persetujuan. Video Veo 3.1 Lite: 35 kredit per klip 8 detik di 1080p (30 kredit di 720p).
- **Dolar di OpenRouter** untuk suara. Narasi sekitar US$0,003 per take 20 detik; musik sekitar US$0,04 per klip 30 detik.

Reel contoh menghabiskan: gambar sekitar 70 kredit; video 7 klip × 35 = 245 kredit (pilot 35, lalu 6 klip 210); suara dan musik di bawah US$0,50.

Batas biaya ada di `.env`:

- `VG_MAX_PER_CALL=250`: biaya maksimal satu permintaan.
- `VG_BUDGET_PROJECT=800`: total maksimal satu proyek. Reel contoh, sekitar 315 kredit, masih jauh di bawahnya.

Sebelum setiap panggilan berbayar, alat mengecek kedua batas ini dan saldo kie.ai-mu. Kalau terlewati, alat menolak dan menyuruh agent bertanya kepadamu. Kamu yang memutuskan, dan hanya kamu yang mengubah `.env`. Di luar semua itu masih ada batas kredit di kunci kie.ai-mu (Pelajaran 04), pagar terakhir.

`project.json` adalah *ledger*: buku catatan setiap gambar dan klip, versinya, kredit yang terpakai, dan setiap persetujuan. **Hanya alat yang menulisnya.** Agent tidak boleh mengeditnya; agent hanya menulis `1_Script/Shotlist.json`.

Satu aturan lagi yang melindungi uangmu: tugas yang kehabisan waktu (*timeout*) diambil dengan `vg resume`, tidak pernah dikirim ulang. Mengirim ulang berarti membayar dua kali.

Tiga perintah ini hanya membaca, tanpa biaya. Ganti `NAMA_PROYEK` dengan nama folder proyekmu:

```bash
python3 2_Tools/vg/vg.py credits
python3 2_Tools/vg/vg.py status -p NAMA_PROYEK
python3 2_Tools/vg/vg.py estimate -p NAMA_PROYEK --stage video
```

Berturut-turut: saldo kie.ai; setiap gambar dan klip dengan versi, kredit terpakai, dan status dua gerbang visual; biaya video yang belum dibuat.

## Perintah yang kamu jalankan sendiri

Yang wajib kamu jalankan sendiri sedikit saja:

1. `bash install.sh`, dan untuk WorkBuddy `bash 2_Tools/workbuddy/install_workbuddy.sh --add-models`: sekali, saat persiapan.
2. `vg doctor`: saat persiapan, dan kapan pun ada yang terasa aneh.
3. `vg review -p NAMA_PROYEK`: halaman review. Biasanya agent yang membukanya, tapi tombol dan catatannya hanya milikmu. Di mode `page`, di sinilah kamu menyetujui ketiga gerbang.
4. `vg next -p NAMA_PROYEK`: kapan saja, untuk melihat langkah berikutnya. Hanya membaca, tanpa biaya.
5. Hanya di mode `terminal`: perintah persetujuan (`vg approve look`, `vg approve visuals`, `vg approve video`), saat halaman review atau agent memberikannya, dan hanya kalau kamu memang setuju. Kamu yang mengetik kodenya.

Selebihnya, kamu bicara ke agent.

## Latihan kecil

Buka folder `3_Templates/Project/` di folder kelas dan cocokkan isinya dengan tabel folder di atas. Lalu, untuk setiap file di bawah, tulis di folder mana ia seharusnya berada, dan apakah namanya benar:

1. `Brief_Rumah_Kita_Realty.pdf`
2. `Frame_S05_First_v2.png`
3. `Music_Take_Quiz_Pop_v1.mp3`
4. `video final revisi FIX.mp4`

<details>
<summary>Lihat jawaban</summary>

1. `0_Source`. Di folder ini nama file dari klien dibiarkan apa adanya: jangan diubah, jangan diganti nama.
2. `4_Frames`. Nama benar: versi kedua yang dibuat alat.
3. `6_Edit/1_Audio`. Nama benar: take musik pertama.
4. Nama salah: ada spasi dan tidak ada versi. Kalau ini hasil akhir revisi pertama, simpan di `99_Output` sebagai `Contoh_Tebak_Harga_v1.1.mp4`, tanpa menimpa `v1.0`.

</details>

## Cek pemahaman

1. Agent berkata, "Semua frame siap, aku lanjut buat videonya ya." Kamu belum menyetujui animatic. Apa yang terjadi?
2. Klip pilot S01 gagal di kie.ai. Bolehkah agent langsung mencoba lagi dengan persetujuan yang sama?
3. Siapa yang menulis `project.json`, dan siapa yang menulis `Shotlist.json`?

<details>
<summary>Lihat jawaban</summary>

1. Alat menolak (`REFUSED:`), karena Gerbang 2 belum dibuka. Agent seharusnya menunjukkan animatic dulu dan menunggu persetujuanmu.
2. Tidak. Setiap persetujuan membayar tepat satu take, dan klip yang gagal sudah memakainya. Perlu persetujuan baru darimu: klik baru di halaman review.
3. `project.json` hanya ditulis alat. `Shotlist.json` ditulis agent.

</details>

## Ringkasan

- Tiga pemain: kamu memutuskan, agent bekerja, alat vg menjaga uangmu.
- `vg next` mencetak satu langkah berikutnya. Expert AI Videographer selalu menjalankannya, dan kamu juga boleh.
- Tujuh tahap, tiga gerbang: look, seluruh reel sebagai gambar, lalu biaya video. Di mode `page`, setiap gerbang adalah klikmu di halaman review. Video selalu paling akhir.
- Setiap proyek punya folder yang sama, dari `0_Source` sampai `99_Output`. Alat memberi versi `_v1`; dokumen dan hasil akhir `_v1.0`.
- Batas biaya ada di `.env`, catatan biaya di `project.json`. Hanya kamu yang mengubah `.env`, hanya alat yang menulis `project.json`.
- Perintah yang kamu jalankan sendiri sedikit. Sisanya, bicara ke agent.

Berikutnya: [Pelajaran 06 · Dari Brief ke Shot List](Pelajaran_06_Brief_Ke_Shot_List_v1.1.md)
