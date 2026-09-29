# AI Videographer · Kelas

Repo ini berisi dua hal sekaligus: AI Videographer, sebuah *harness* (kumpulan instruksi dan alat yang membuat agent AI bekerja dengan urutan yang sama setiap kali), dan kelas pemula berbahasa Indonesia untuk memakainya. Kamu bicara ke agent dengan bahasa biasa, misalnya "Buat reel dari brief ini". Di workshop, agent-nya WorkBuddy dengan *Expert* (agent dengan uraian tugas khusus) bernama AI Videographer. Claude Code juga bisa dipakai, dengan cara yang sama. Agent mengikuti *skill* (file instruksi cara kerja) di `1_Skills/`, lalu menjalankan alat vg untuk membuat gambar, suara, dan video. Hasilnya reel properti vertikal 9:16. Aturan emasnya: gambar itu murah, video itu mahal. Jadi seluruh reel disetujui sebagai gambar dulu, dan video hanya dibuat setelah kamu bilang "ya".

## Mulai di sini

- **[Kelas AI Videographer](6_Kelas/README.md)**: daftar semua pelajaran, studi kasus, latihan, dan deck.
- **[Pelajaran 00 · Mulai di Sini](6_Kelas/1_Pelajaran/Pelajaran_00_Mulai_Di_Sini_v1.1.md)**: pelajaran pertama. Belum pernah memakai terminal? Mulai dari sini.
- **[Panduan WorkBuddy](6_Kelas/5_WorkBuddy/Panduan_WorkBuddy_v1.0.md)**: memasang dan memakai WorkBuddy dengan Expert AI Videographer, agent untuk workshop.

## Peta folder

| Folder | Isi |
|---|---|
| `1_Skills/` | skill untuk agent, file instruksi tahap demi tahap. Titik mulainya `1_Skills/vg-director/SKILL.md`. |
| `2_Tools/` | alat vg, program Python kecil yang memanggil model, mencatat biaya, dan menolak video yang belum disetujui. Pemasang Expert WorkBuddy ada di `2_Tools/workbuddy/`. |
| `3_Templates/` | templat folder proyek (`0_Source` sampai `99_Output`) |
| `4_Docs/` | dokumen desain dan catatan teknis harness |
| `5_Projects/` | proyek videomu, satu folder per video. Isinya tidak ikut diunggah ke GitHub. |
| `6_Kelas/` | kelasnya: pelajaran, studi kasus Tebak Harga, brief latihan, checklist, deck, dan panduan WorkBuddy |
| `99_Output/` | hasil akhir yang siap dikirim. Isinya juga tidak ikut diunggah ke GitHub. |

## Persiapan cepat

Yang kamu butuhkan: sebuah Mac dengan Xcode Command Line Tools, Homebrew, FFmpeg, Git, Python 3.9 atau lebih baru, dan sebuah agent: [WorkBuddy](https://www.workbuddy.ai) untuk workshop, atau Claude Code. Kamu juga butuh akun [kie.ai](https://kie.ai) untuk gambar dan video, dan [OpenRouter](https://openrouter.ai) untuk suara dan musik. Untuk WorkBuddy, otak agent-nya model glm-5.3-flash, dipanggil lewat gateway seperti [SumoPod](https://ai.sumopod.com) yang dibayar dalam rupiah. Belum pernah memasang semua ini? Ikuti [Pelajaran 04 · Persiapan Alat](6_Kelas/1_Pelajaran/Pelajaran_04_Persiapan_Alat_v1.1.md) langkah demi langkah.

Jalankan di Terminal, satu baris sekali:

```bash
git clone https://github.com/tansilandre/ai-videographer-kelas.git
cd ai-videographer-kelas
bash install.sh
python3 2_Tools/vg/vg.py doctor
```

`bash install.sh` membuat file `.env`. Isi kunci API kie.ai dan OpenRouter di file itu, **sendiri**, dan ubah `VG_APPROVAL_MODE=terminal` menjadi `VG_APPROVAL_MODE=page`, supaya persetujuan menjadi klik di halaman review. Lalu jalankan baris terakhir lagi sampai tidak ada baris `FAIL`. Memakai WorkBuddy? Pasang Expert-nya dengan `bash 2_Tools/workbuddy/install_workbuddy.sh --add-models`, lalu ikuti [Panduan WorkBuddy](6_Kelas/5_WorkBuddy/Panduan_WorkBuddy_v1.0.md). Tidak ada perintah bernama `vg` di komputermu. Tulisan `vg doctor` di kelas ini adalah singkatan dari `python3 2_Tools/vg/vg.py doctor`.

## Aturan keselamatan

- **Hanya kamu yang mengedit `.env`, dan API key tidak pernah ditempel ke chat.** Agent hanya boleh memeriksa `.env` lewat `vg doctor`. Buat kunci kie.ai khusus di https://kie.ai/api-key dan beri batas kredit total.
- **Tidak ada video tanpa "ya" yang jelas darimu.** Dengan `VG_APPROVAL_MODE=page` (disarankan untuk kelas), ketiga gerbang adalah klikmu di halaman review. Untuk video, setiap klip menunjukkan biayanya, dan halaman bertanya sekali lagi sebelum menyetujui. Perintah `vg approve` selalu ditolak di mode ini, jadi agent tidak bisa menyetujui untukmu. Cara lain, mode `terminal`: kamu mengetik kode acak 4 digit di terminalmu sendiri.
- **Mulai dari satu klip pilot.** Setiap persetujuan membayar tepat satu *take* (satu kali percobaan). Mengulang klip, termasuk klip yang gagal, butuh persetujuan baru.
- **Tugas yang *timeout* (waktu tunggunya habis) diambil dengan `vg resume`**, tidak pernah dikirim ulang. Mengirim ulang bisa membayar dua kali.

## In English

This repository is the AI Videographer harness plus a beginner class taught in Bahasa Indonesia. The harness is a set of agent skills and a small Python CLI that turns a client brief into a 9:16 short-form video, and it refuses to spend video credits until a human has approved the look, the whole reel as stills, and the per-clip cost. The class, in `6_Kelas/`, walks through one example reel from brief to final edit. The workshop runs the harness in WorkBuddy with the AI Videographer Expert and a fast model (glm-5.3-flash) that follows `vg next` one step at a time; Claude Code works the same way. With `VG_APPROVAL_MODE=page` every approval is a click on the local review page, and `vg approve` on the command line always refuses. The original English overview of the harness is in [4_Docs/Harness_Overview_EN.md](4_Docs/Harness_Overview_EN.md).
