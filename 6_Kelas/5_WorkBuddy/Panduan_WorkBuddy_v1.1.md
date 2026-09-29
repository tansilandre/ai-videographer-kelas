# Panduan WorkBuddy · AI Videographer

Pasang sekali dalam tiga langkah. Setelah itu kamu cukup bicara, dan klik di tiga gerbang.

## Siapkan dulu

- Sebuah **Mac**.
- Kunci **kie.ai** untuk gambar dan video. Buat di https://kie.ai/api-key, isi saldo, dan beri batas kredit.
- Kunci **OpenRouter** untuk narasi dan musik, di https://openrouter.ai/keys. Boleh menyusul.

Kunci API itu seperti PIN ATM. Jangan pernah menempelnya di chat.

## Pasang: 3 langkah

**1 · Pasang WorkBuddy.** Unduh dari https://www.workbuddy.ai, lalu masuk dengan Google atau GitHub. Di pemilih model, pilih **glm-5.3-flash**. Model ini sudah ada di WorkBuddy.

**2 · Minta AI-nya memasang.** Di WorkBuddy, pilih folder kerja (misalnya folder baru `AI_Videographer` di Documents), lalu kirim pesan ini:

> Pasang AI Videographer: clone https://github.com/tansilandre/ai-videographer-kelas.git ke folder ini (atau ke subfolder ai-videographer-kelas kalau folder ini tidak kosong), lalu jalankan `bash setup.sh` di folder itu dan ikuti yang dicetaknya.

AI-nya memasang semuanya sendiri. Kamu hanya perlu:

- klik **izinkan** kalau WorkBuddy meminta izin menjalankan perintah;
- klik **Install** kalau jendela Apple muncul, lalu bilang "jalankan setup lagi" setelah selesai;
- kalau Homebrew belum ada, AI-nya memberimu satu baris untuk ditempel di app **Terminal**, karena pemasangannya butuh password Mac-mu.

**3 · Tempel kunci, lalu buka ulang.** Halaman **Setup AI Videographer** terbuka di browser. Tempel kuncimu di sana dan klik **Simpan**. Halaman itu langsung mengecek saldo kie.ai-mu. Lalu:

1. Tutup WorkBuddy (Cmd + Q) dan buka lagi.
2. Buka folder yang disebut di akhir setup.
3. Pilih Expert **AI Videographer**.

## Pakai

Klik **Buat video baru**. Expert bertanya lima hal tentang properti atau produkmu, dalam satu pesan. Jawab, dan lampirkan foto kalau ada. Setelah itu ia bekerja sendiri, dan hanya berhenti di tiga gerbang:

| Gerbang | Yang kamu lakukan di halaman review |
|---|---|
| 1 · Look | lihat gambar gayanya, lalu klik **Approve look**. Belum pas? Tulis catatan di gambarnya, lalu klik **Done** |
| 2 · Reel | tonton seluruh reel sebagai gambar diam, lalu klik **Approve reel** |
| 3 · Video | di bagian **Video**, klik **Approve** untuk satu klip pilot. Biayanya tertulis di tombol. Suka hasilnya? Setujui sisanya |

Setiap kali selesai di halaman review, kembali ke WorkBuddy dan bilang **"sudah"**. Reel akhirnya ada di folder `99_Output`.

Bingung di tengah jalan? Bilang **"lanjut"** atau **"kenapa berhenti?"**.

## Kalau macet

| Yang terjadi | Yang kamu lakukan |
|---|---|
| Expert bilang tidak bisa menjalankan perintah | izinkan perintahnya di WorkBuddy, lalu bilang "lanjut" |
| Expert bilang WorkBuddy tidak bisa membuat video | bilang: "Pakai alat vg di folder ini. Jalankan vg next." |
| Link review tidak terbuka | bilang "buka lagi halaman review" |
| Kunci salah, atau saldo kie.ai habis | isi saldo di kie.ai, lalu bilang "buka halaman setup" dan tempel kuncinya lagi |
| Expert lama diam | glm-5.3-flash sedang berpikir. Tunggu 1–2 menit, lalu bilang "lanjut" |

## Biaya

- **Otak** (glm-5.3-flash): memakai kredit WorkBuddy-mu.
- **Gambar**: 6–16 kredit kie.ai per gambar.
- **Klip video**: 35 kredit kie.ai per klip 8 detik.
- **Narasi dan musik**: beberapa sen dolar per take di OpenRouter.

Video hanya dibuat setelah kamu klik. Klip yang gagal tidak memotong kredit.

## Lanjutan (tidak wajib)

- **Memperbarui:** bilang ke Expert "perbarui AI Videographer". Ia menjalankan `git pull && bash setup.sh`, lalu kamu membuka ulang WorkBuddy.
- **Kredit WorkBuddy habis?** Pakai otak lewat gateway sendiri, misalnya SumoPod: `bash 2_Tools/workbuddy/install_workbuddy.sh --add-models`.
- **Tanpa WorkBuddy?** Claude Code juga bisa. Lihat [Pelajaran 04](../1_Pelajaran/Pelajaran_04_Persiapan_Alat_v1.2.md).
