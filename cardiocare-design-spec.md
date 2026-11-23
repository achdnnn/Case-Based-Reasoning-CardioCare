# CardioCare: Spesifikasi Desain & Prompt Pembuatan

Dokumen ini menjelaskan desain prototype **CardioCare** (Sistem Pakar Diagnosis Penyakit Jantung, metode Case-Based Reasoning) secara cukup rinci agar bisa dibuat ulang oleh AI atau developer. Bagian terakhir berisi prompt siap tempel.

---

## 1. Konsep

- **Arah visual:** Premium Medical Technology Dashboard. Bersih, profesional, dominan putih dengan navy sebagai warna utama.
- **Karakter:** whitespace lega, border tipis, shadow lembut, radius konsisten, tanpa gradient berlebihan, tanpa emoji sebagai ikon.
- **Satu momen yang paling menonjol:** halaman hasil diagnosis (ring gauge kemiripan yang beranimasi). Elemen lain dibuat tenang.
- **Bahasa hasil:** selalu "indikasi awal" dan "tingkat kemiripan kasus", tidak pernah "diagnosis pasti".
- **Teknologi:** satu file HTML + CSS + JavaScript murni, tanpa backend dan database, tanpa framework.

## 2. Design Tokens

### Warna (mode terang)

| Token | Nilai | Dipakai untuk |
|---|---|---|
| `--bg` | `#F7F8FB` | latar halaman |
| `--surf` | `#FFFFFF` | kartu, sidebar, topbar |
| `--ink` | `#14284B` | teks utama |
| `--mute` | `#5F6F8A` | teks sekunder |
| `--line` | `#E2E8F2` | border tipis |
| `--navy` | `#14284B` | tombol utama, menu aktif, progres |
| `--red` | `#D95B5B` | aksen jantung, gejala terpilih, gauge |
| `--red-s` | `#FCEDED` | latar lembut merah |
| `--blue` | `#3C7BC4` | aksen informasi, focus ring |
| `--blue-s` | `#E8F0FA` | latar lembut biru, chip |
| `--ok` / `--ok-s` | `#2E8B6A` / `#E4F4EE` | status baik, gejala yang cocok |

### Warna (mode gelap)

`--bg #0D1730`, `--surf #152345`, `--ink #EAF0FB`, `--mute #9DB0D0`, `--line #26365D`, `--navy #4C7FD1`, `--red #F08080`, `--red-s #3A2530`, `--blue #7FB0EE`, `--blue-s #1C2E56`, `--ok #5FD0A5`, `--ok-s #17372F`.

Terapkan dengan `@media (prefers-color-scheme: dark)` dan tombol manual lewat atribut `data-theme="dark|light"` di `<html>`.

### Tipografi

- Font: **Plus Jakarta Sans** (Google Fonts), fallback `Inter, system-ui, sans-serif`.
- Body 16px, line-height 1.6. Teks kecil 0,9rem.
- `h1`: `clamp(2rem, 4.5vw, 3rem)`, bobot 800. `h2`: 1,5rem, bobot 700. `h3`: 1,05rem, bobot 700.
- Letter-spacing heading: `-0.02em`.

### Bentuk

- Radius: kartu 16px, input/checklist 14px, tombol 10px, chip 99px, hero 24px.
- Shadow: `0 1px 2px rgba(20,40,75,.06), 0 8px 24px rgba(20,40,75,.06)`.
- Jarak antar blok 20px, padding kartu 24px, padding halaman 32px (20px di mobile).

## 3. Layout

- **Desktop:** grid dua kolom, sidebar 260px (sticky, tinggi penuh) dan area konten. Topbar sticky di atas konten.
- **Konten:** lebar maksimum 1120px, rata tengah.
- **Sidebar:** logo (kotak navy 34px dengan ikon hati + teks "CardioCare"), menu navigasi, lalu catatan kecil di dasar: "Prototype akademik. Data kasus adalah data simulasi."
- **Menu aktif:** latar navy, teks putih (`aria-current="page"`).
- **Topbar:** teks kecil "Sistem Pakar CBR · Cosine Similarity", spacer, tombol ganti tema, tombol primer "Mulai diagnosis".
- **Tablet (≤960px):** grid 3 dan 4 kolom menjadi 2 kolom, hero menjadi 1 kolom.
- **Mobile (≤760px):** sidebar menjadi drawer geser dari kiri (tombol menu di topbar), semua grid menjadi 1 kolom.
- Dukung safe-area (`env(safe-area-inset-*)`) dan `viewport-fit=cover`.

## 4. Komponen

**Tombol:** `.btn` (outline), `.btn.p` (navy), `.btn.r` (merah), `.btn.lg` (besar). State disabled opacity 0,45.

**Chip:** pil kecil bobot 700. Varian biru (default), merah, hijau.

**Kartu:** latar `--surf`, border `--line`, radius 16px, shadow lembut.

**Input teks:** lebar penuh, padding 14px 18px, radius 14px, border `--line`. Dipakai untuk "Nama pasien" dan "Cari gejala", masing-masing dengan label tebal di atasnya.

**Checklist gejala (komponen utama):**
- Grid 2 kolom, gap 12px. Satu kolom di mobile.
- Setiap kartu adalah `<label>` berisi checkbox asli yang disembunyikan secara visual, kotak centang kustom 24px (radius 7px), lalu teks: kode gejala kecil abu-abu, nama gejala tebal 600, deskripsi abu-abu kecil.
- Hover: border navy. Terpilih (`:has(input:checked)`): border merah, latar `--red-s`, kotak centang terisi merah dengan ikon centang putih dan skala 1,08.
- Focus keyboard: outline 3px `--blue`.

**Progress bar:** tinggi 8px, latar `--blue-s`, isi navy, transisi lebar 0,4 detik.

**Bar sticky di Diagnosis:** kartu berisi teks "x dari 12 gejala dipilih", progress bar, tombol Reset dan "Proses diagnosis". Menempel di bawah topbar saat scroll.

**Tabel:** header abu-abu 600, baris dipisah border tipis, dibungkus wrapper `overflow-x:auto`.

**Modal:** latar gelap transparan, kartu maksimum 560px. Tutup lewat tombol, klik latar, atau tombol Esc.

**Toast:** kapsul navy di bawah tengah layar, hilang setelah 2,2 detik.

**Ikon:** SVG inline gaya garis (stroke 1,8px, 20px): hati, grid, stetoskop, buku, daftar, jam, info, rumah, menu, bulan, peringatan, silang, centang, tempat sampah.

## 5. Halaman

Navigasi memakai hash (`#beranda`, `#dashboard`, `#diagnosis`, `#hasil`, `#pengetahuan`, `#gejala`, `#riwayat`, `#metode`).

1. **Beranda:** hero dua kolom. Kiri: chip "Case-Based Reasoning", headline, paragraf, tombol "Mulai diagnosis" dan "Pelajari metode CBR". Kanan: kartu navy dengan garis EKG yang tergambar sendiri (animasi `stroke-dashoffset`) dan angka jumlah gejala, penyakit, kasus. Di bawahnya tiga kartu langkah, kartu "Tentang penyakit jantung", dan disclaimer.
2. **Dashboard:** empat kartu statistik (penyakit, gejala, kasus, konsultasi), grafik batang konsultasi 7 hari (dummy, hari ke-6 disorot navy), kartu metode berisi rumus dan tombol mulai diagnosis.
3. **Diagnosis:** judul "Pilih gejala pasien" dengan badge jumlah gejala di kanan atas, input nama pasien, input pencarian gejala, bar sticky, lalu checklist 2 kolom. Pencarian menyaring kartu secara langsung dan menampilkan pesan kosong bila tidak ada yang cocok. Tombol proses aktif hanya jika nama terisi dan minimal satu gejala dicentang.
4. **Hasil:** kartu utama berisi ring gauge SVG 240px (lingkaran merah beranimasi 1,4 detik, persentase besar di tengah), chip tingkat kemiripan, nama penyakit, deskripsi, dan chip hijau gejala yang cocok. Di bawahnya dua kartu: peringkat kemiripan semua penyakit (bar horizontal) dan saran tindak lanjut dengan disclaimer, tombol Kembali dan Diagnosis ulang. Tingkat kemiripan: ≥75% tinggi, 50–74% sedang, <50% rendah.
5. **Basis Pengetahuan:** kartu per penyakit (kode, nama, deskripsi, empat gejala pertama + sisa) dengan tombol "Lihat detail" yang membuka modal gejala terkait dan kasus.
6. **Data Gejala:** dropdown filter penyakit, tabel kode, gejala, deskripsi, dan kasus terkait.
7. **Riwayat:** tombol "Hapus semua riwayat", tabel tanggal, pasien, penyakit tertinggi, nilai, dan tombol hapus per baris. Setiap penghapusan meminta konfirmasi lewat modal. Kondisi kosong menampilkan ajakan memulai diagnosis. Data disimpan di `localStorage` (dibungkus try/catch).
8. **Metode CBR:** empat kartu bernomor Retrieve, Reuse, Revise, Retain dengan garis putus-putus penghubung, kotak "siklus" di bawahnya, dan kartu rumus Cosine Similarity.

## 6. Logika CBR

Data simulasi (ganti dengan data asli tanpa mengubah algoritma):

```js
const S = [["G01","Nyeri dada","deskripsi"], ...];        // gejala
const D = [["P01","Penyakit Jantung Koroner","deskripsi"], ...]; // penyakit
const C = [["K01","P01","G01 G02 G05 G07"], ...];         // kasus: id, penyakit, gejala
```

**Retrieve:** vektor gejala pengguna dan vektor tiap kasus bersifat biner, sehingga

```
sim(A, B) = |A ∩ B| / ( √|A| × √|B| )
```

Skor sebuah penyakit adalah skor tertinggi dari kasus-kasusnya, lalu penyakit diurutkan menurun. Kasus termirip juga menyimpan gejala yang cocok untuk ditampilkan.

**Retain:** setiap hasil disimpan ke riwayat dengan format `[tanggal, nama pasien, penyakit tertinggi, nilai%]`.

Jika kamu sudah punya algoritma dan data asli, **pertahankan keduanya**. Ubah hanya lapisan tampilan.

## 7. Animasi & Interaksi

- EKG di hero tergambar sekali saat halaman dimuat.
- Ring gauge terisi saat hasil muncul.
- Kartu checklist berubah warna, dan kotak centang membesar sedikit saat dipilih.
- Progress bar bergerak halus saat gejala dipilih.
- Tidak ada animasi masuk berlebihan pada setiap kartu.
- Hormati `prefers-reduced-motion`.

## 8. Aksesibilitas

- Checkbox asli (bisa dioperasikan keyboard), focus ring terlihat jelas.
- Tombol ikon memakai `aria-label`.
- Modal memakai `role="dialog"` dan `aria-modal`, tutup dengan Esc.
- Kontras teks memenuhi keterbacaan di mode terang dan gelap.

---

## 9. Prompt Siap Tempel

```
Buatkan prototype website "CardioCare", Sistem Pakar Diagnosis Penyakit Jantung
dengan metode Case-Based Reasoning (Cosine Similarity), dalam SATU file HTML
(HTML + CSS + JS murni, tanpa backend).

Ikuti dokumen cardiocare-design-spec.md yang saya lampirkan untuk design tokens,
layout, komponen, halaman, dan perilaku interaksi. Ketentuan penting:

1. Delapan halaman dengan routing hash: Beranda, Dashboard, Diagnosis, Hasil,
   Basis Pengetahuan, Data Gejala, Riwayat, Metode CBR.
2. Halaman Diagnosis berupa checklist gejala 2 kolom (kartu dengan checkbox),
   ada input nama pasien, kolom cari gejala, badge jumlah gejala, dan progress
   sticky. Centang = gejala dialami, tidak dicentang = tidak dialami.
3. Riwayat menyimpan nama pasien dan bisa dihapus per baris atau semua, dengan
   modal konfirmasi.
4. Hasil memakai ring gauge SVG beranimasi, gejala yang cocok, dan peringkat
   semua penyakit. Gunakan istilah "indikasi awal", bukan diagnosis pasti.
5. Dark mode, responsif (desktop, tablet, mobile), dan aksesibel.
6. Jangan mengarang algoritma. Pakai data simulasi yang diberi label jelas,
   atau data/algoritma asli saya bila saya lampirkan.
7. Jangan memakai emoji sebagai ikon, gradient berlebihan, atau layout padat.

Kerjakan bertahap: rencana desain, design system, implementasi, lalu review
konsistensi visual dan responsivitas.
```
