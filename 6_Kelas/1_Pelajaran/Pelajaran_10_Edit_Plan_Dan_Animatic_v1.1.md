# Pelajaran 10 · Rencana Edit dan Animatic

## Tujuan

Setelah pelajaran ini kamu bisa:

- membaca `6_Edit/Edit_Spec.json` dan tahu arti setiap bagiannya;
- memilih transisi yang punya alasan;
- menonton animatic sebagai penonton dan menulis catatan yang jelas;
- melewati Gerbang 2 dengan benar.

## Kenapa ini penting

Animatic adalah momen murah yang terakhir. Setelah Gerbang 2, tahap berikutnya video, dan video paling mahal. Semua yang kamu lihat di animatic (waktu, teks, peta, caption) adalah yang nanti dibayar.

Versi pertama reel kami gagal karena setiap shot dicek satu per satu. Hasilnya, tiap shot punya cahaya dan warna sendiri, dan janji di hook tidak ditepati. Sekarang seluruh reel dinilai utuh, sebagai gambar, sebelum ada video.

Di pelajaran ini, `vg` adalah singkatan dari `python3 2_Tools/vg/vg.py`.

## 1. Rencana edit: satu file yang mengatur semuanya

Rencana edit disimpan di `6_Edit/Edit_Spec.json`. *JSON* adalah format teks untuk menyimpan data sebagai pasangan nama dan nilai. Agent yang menulisnya. Kamu tidak perlu menulis JSON, tapi sebaiknya bisa membacanya. Buka contohnya di `6_Kelas/2_Studi_Kasus/Tebak_Harga/Edit_Spec.json`.

| Bagian | Artinya | Di reel Tebak Harga |
|---|---|---|
| `segments` | urutan potongan gambar, masing-masing dengan durasinya | 12 segmen, dari S01 (2,1 s) sampai S11 (2,8 s) |
| `graphics` | teks dan grafis di atas gambar; `at` dihitung dari awal segmennya | judul "PETUNJUK 2", peta, *callout*, hitungan 1.000, label ILUSTRASI RENCANA, *end card* |
| `narration` | file narasi dan teksnya; caption diambil dari teks ini | take Callirrhoe |
| `music` | file musik, detik masuknya (`at`), volume, dan `duck` | Quiz_Pop, `at` 3,27, `duck` 0,5 |
| `sfx` | efek suara, ditempel ke segmen | whoosh 0,28 s sebelum whip |
| `transition_in` | cara segmen masuk: `cut`, `whip`, atau `flash` | `flash` hanya di S10 |
| `grade` | satu perlakuan warna untuk semua gambar | contrast 1,04, saturation 0,96, temperature 5600 K, grain 3 |
| captions | tulisan kata demi kata, diatur di `style` | maksimal 3 kata, kata yang diucapkan berwarna oranye |

Beberapa istilah:

- *End card* adalah kartu penutup: nama brand, ajakan, dan nomor telepon (0812-0000-0000).
- `duck` artinya musik dikecilkan saat ada yang bicara. Nilai 0,5 berarti musik turun jadi setengahnya.
- *Grade* adalah perlakuan warna. Satu grade untuk semua shot membuat reel terasa satu film. Tapi grade tidak bisa memperbaiki gambar yang cahayanya salah.

Segmen punya beberapa jenis. `still` adalah gambar diam dengan dorongan kamera pelan (`zoom`). `background` adalah gambar latar untuk grafis, bisa dikaburkan (`blur`) dan digelapkan (`dim`). Di proyek sungguhan ada juga `clip`, yaitu klip AI. Di animatic, klip itu diwakili frame pertamanya.

Ini segmen S10, momen harga, dari file contoh (dipersingkat):

```json
{
  "id": "S10",
  "duration": 2.15,
  "transition_in": "flash",
  "background": { "image": "file:2_References/Look_Rumah_Depan_v1.png", "zoom": [1.22, 1.0] }
}
```

Perhatikan satu hal. Teks narasi di rencana edit menulis "mulai 1,3M-an!" dengan angka, karena teks ini yang muncul sebagai caption. Teks untuk model suara tetap "satu koma tiga M-an" (Pelajaran 09).

## 2. Transisi yang punya alasan

Transisi bukan hiasan. Potong keras hampir di semua tempat.

1. **Potong keras** (*hard cut*, gambar langsung berganti). Pilihan utama. Potong tepat sebelum frasa baru.
2. **Whip + whoosh**. *Whip* adalah kabur gerak horizontal di kedua sisi potongan. Dipakai saat pindah tempat, selalu dengan bunyi whoosh. Di reel contoh: S03 (foto udara), S04 (peta), S07 (rencana stasiun MRT).
3. **Flash + ding**. Gambar muncul dari putih dalam 0,2 detik. Hanya sekali: jawaban harga di S10, bersama bunyi ding dan drop musik pada kata "mulai".

Kalau semua shot memakai efek, tidak ada yang terasa istimewa.

## 3. Render animatic

*Animatic* adalah seluruh reel yang dibuat dari gambar diam: lengkap dengan caption, grafis, transisi, narasi, musik, dan efek suara. Gratis, dibuat di komputermu sendiri.

```bash
python3 2_Tools/vg/vg.py edit animatic -p NAMA_PROYEK
```

Ganti `NAMA_PROYEK` dengan nama folder proyekmu di `5_Projects/`. Hasilnya file `Animatic_<nama proyek>_v1.mp4` di folder `6_Edit/`. Setiap perbaikan berarti render baru: v2, v3, dan seterusnya. Tonton contohnya: `6_Kelas/2_Studi_Kasus/Tebak_Harga/Contoh_Tebak_Harga_Animatic_v1.0.mp4`.

Animatic kami pernah membeku sekitar 2,5 detik tanpa ada yang sadar. Sekarang jumlah frame setiap render dicek: jumlah frame = durasi × 30. Animatic contoh berdurasi 27,9 detik, jadi harus punya 837 frame. Cara mengeceknya ada di Pelajaran 12.

## 4. Tonton sebagai penonton

Tonton sekali dari awal sampai akhir tanpa berhenti, seperti orang yang sedang menggulir media sosial. Baru setelah itu, tanya:

- **Satu dunia?** Satu sore yang cerah, satu arah matahari, satu grade di semua shot.
- **Janji ditepati?** Hook bertanya "Tebak harganya?" Apakah harganya benar dijawab?
- **Rumahnya cukup lama terlihat?** Penonton datang untuk rumahnya.
- **Grafis rapi?** Satu gaya, dan tidak menutupi wajah.
- **Suara pas?** Drop jatuh di jawaban, dan tidak ada hening mati di akhir.
- **Caption jujur?** Tidak ada kata yang muncul sebelum diucapkan.

Tulis catatan yang konkret: nomor shot, apa yang salah, apa yang kamu mau. "S06: judul menutupi wajah Rani, pindahkan ke atas" jauh lebih berguna daripada "kurang bagus".

## 5. Caption tidak boleh mendahului kata

Ini bug nyata dari reel kami. Dulu caption selalu menggabungkan tiga kata. Saat Rani masih berkata "Harganya...", caption sudah menampilkan harganya. Jawabannya bocor sebelum diucapkan, dan permainan tebak harga jadi rusak.

Sekarang satu caption selalu berhenti di tanda jeda: titik, koma, tanda tanya, tanda seru, titik dua, atau elipsis (…). Jadi di reel contoh, "Harganya..." tampil sendiri. Baru setelah itu "mulai 1,3M-an!" muncul, tepat saat diucapkan.

![S10: harga muncul bersama kata yang diucapkan](../2_Studi_Kasus/Tebak_Harga/1_Gambar/Frame_Harga.jpg)

Rumah di gambar ini dibuat AI karena proyek contohnya fiktif. Di proyek nyata, rumah yang dijual adalah foto asli dari klien, dan hanya kameranya yang bergerak.

## 6. Gerbang 2: setujui seluruh reel sebagai gambar

1. Agent menonton animatic-nya sendiri dulu. Lalu ia membukakan halaman review untukmu dan mengirim tautannya di chat (kamu juga bisa menjalankannya sendiri di terminal):

   ```bash
   python3 2_Tools/vg/vg.py review -p NAMA_PROYEK
   ```

2. Di halaman itu kamu melihat setiap beat, mengganti take, menulis catatan di samping gambar, dan menonton animatic. Kalau sudah, klik **Done, back to the agent**.
3. Agent memperbaiki hanya yang kamu tandai, merender animatic baru, lalu membuka halaman lagi. Ulangi sampai kamu puas.
4. Kalau sudah puas, klik **Approve reel** di bawah animatic, lalu **Done, back to the agent**, dan bilang di chat bahwa kamu sudah selesai. Tombol itu baru muncul kalau animatic-nya menunjukkan persis gambar yang sekarang.

   Cara lain, di mode `terminal`: halaman review menampilkan perintah `python3 2_Tools/vg/vg.py approve visuals -p NAMA_PROYEK`. Kamu menjalankannya di Terminal-mu sendiri dan mengetik kode acak 4 digit.

Agent tidak pernah mengklik tombol di halaman review. Halaman itu milikmu. Di mode `page`, perintah `vg approve visuals` dari agent selalu ditolak.

Alat juga menjaga gerbang ini. Ia menolak persetujuan kalau animatic terakhir tidak menunjukkan gambar dan rencana edit yang sekarang. Setelah disetujui, perubahan pada frame, foto, grade, narasi, atau teks dan waktu di rencana edit membatalkan persetujuan. Kamu harus menonton animatic baru dan menyetujui lagi. Perubahan musik, efek suara, atau nama file output tidak membatalkannya.

## Latihan kecil

Tonton `Contoh_Tebak_Harga_Animatic_v1.0.mp4` sekali tanpa berhenti. Lalu tulis tiga catatan konkret: nomor shot, apa yang kamu lihat, apa yang kamu mau. Terakhir, buka `Edit_Spec.json` dan cari tiga segmen dengan `"whip"` dan satu segmen dengan `"flash"`.

## Cek pemahaman

1. Kapan kamu memakai whip, dan bunyi apa yang menyertainya?
2. Setelah Gerbang 2, kamu mengganti teks judul di S06. Apa yang terjadi?
3. Kenapa caption berhenti di tanda jeda?

<details>
<summary>Jawaban</summary>

1. Saat pindah tempat, misalnya dari deretan rumah ke foto udara. Selalu dengan whoosh.
2. Persetujuan visual batal. Agent merender animatic baru, kamu menontonnya, lalu menyetujui lagi.
3. Supaya kata berikutnya, misalnya harga, tidak muncul sebelum diucapkan.

</details>

## Ringkasan

- `Edit_Spec.json` adalah rencana edit: segmen, grafis, narasi, musik, efek, transisi, grade, dan caption.
- Potong keras hampir di semua tempat. Whip + whoosh untuk pindah tempat. Flash + ding hanya sekali, untuk jawaban.
- Animatic adalah seluruh reel dari gambar diam, dengan suara. Gratis, dan dirender ulang setiap ada perbaikan.
- Tonton sebagai penonton dulu, baru menilai. Tulis catatan yang konkret.
- Gerbang 2: kamu yang menyetujui, dengan klik **Approve reel** di halaman review.

Berikutnya: [Pelajaran 11 · Prompt Video dan Gerbang Biaya](Pelajaran_11_Video_Dan_Gerbang_Biaya_v1.1.md)
