# CardioCare – Sistem Pakar Penyakit Jantung (CBR + Cosine Similarity)

Prototype akademik sistem pakar untuk membantu identifikasi indikasi awal penyakit jantung menggunakan metode **Case-Based Reasoning (CBR)** dan algoritma **Cosine Similarity** manual (tanpa library ML tambahan).

> **Catatan Medis:** Prototype akademik dengan data simulasi. Hasil adalah indikasi awal berdasarkan kemiripan kasus, bukan pengganti pemeriksaan dokter spesialis jantung.

---

## Fitur Utama

1. **Checklist Gejala Interaktif (Pengganti Radio Ya/Tidak)**
   - Tidak perlu lagi memilih "Ya" atau "Tidak" untuk setiap 31 gejala satu per satu.
   - Cukup centang kotak gejala yang dialami langsung pada kartu checklist interaktif.
   - Dilengkapi kolom pencarian instan (nama atau kode gejala) dan filter kategori (Berat, Sedang, Ringan).
   - Fitur pemilihan cepat (*Pilih Semua*, *Batalkan*, dan *Reset Checklist*).
   - Indikator metrik langsung (jumlah gejala terpilih, total bobot keparahan, dan status kesiapan diagnosis).

2. **Hasil Analisis Kemiripan (Cosine Similarity)**
   - Ring gauge SVG beranimasi yang menampilkan persentase kemiripan tertinggi.
   - Klasifikasi tingkat kemiripan: **Tinggi (≥75%)**, **Sedang (50%–74%)**, dan **Rendah (<50%)**.
   - Analisis gejala yang cocok (*matched*) vs gejala lain yang dipilih.
   - Peringkat kemiripan terhadap seluruh 8 basis kasus penyakit jantung.
   - Rekomendasi tindakan klinis & panduan kegawatdaruratan medis.
   - Ekspor/unduh laporan hasil diagnosis dalam format TXT.

3. **Riwayat Diagnosis Pasien**
   - Riwayat diagnosis tersimpan otomatis selama sesi berlangsung.
   - Ringkasan metrik riwayat (total konsultasi, rata-rata kemiripan, kasus terbanyak).
   - Fitur membuka kembali detail diagnosis sebelumnya (*Buka Hasil*) atau menghapus riwayat.

4. **Basis Pengetahuan & Kamus Gejala**
   - Eksplorasi 8 basis kasus penyakit (K01–K08) beserta gejala khasnya.
   - Kamus data 31 gejala (G01–G31) dengan bobot, kategori keparahan, dan frekuensi kasus.

5. **Penjelasan Konseptual CBR & Rumus**
   - Siklus 4R CBR: *Retrieve*, *Reuse*, *Revise*, *Retain*.
   - Penjelasan matematis rumus Cosine Similarity dengan representasi vektor biner 31 dimensi.

---

## Instalasi & Menjalankan Aplikasi

Jalankan perintah berikut pada terminal PowerShell:

```powershell
# 1. Pastikan berada di folder project
cd CardioCare

# 2. Aktifkan virtual environment (venv sudah tersedia)
.\venv\Scripts\Activate.ps1

# Jika skrip diblokir oleh kebijakan PowerShell, jalankan terlebih dahulu:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3. Jalankan aplikasi Streamlit
streamlit run app.py
```

---

## Struktur Folder

```
CardioCare/
├── app.py                      # Tampilan, interaksi & navigasi Streamlit
├── backend/
│   ├── __init__.py
│   ├── cbr.py                  # Logika CBR & Cosine Similarity manual (ASLI/TIDAK DIUBAH)
│   └── data.py                 # Data simulasi: penyakit, gejala, basis kasus (ASLI/TIDAK DIUBAH)
├── assets/
│   ├── style.css               # Desain sistem tokens, checklist card, & tema visual
│   └── images/
│       └── hero.svg            # Ilustrasi visual
├── requirements.txt            # Dependensi (streamlit)
├── cardiocare-design-spec.md   # Spesifikasi desain prototype
└── README.md                   # Dokumentasi proyek
```

---

## Integritas Backend
Backend (`backend/cbr.py` dan `backend/data.py`) tetap dipertahankan 100% orisinil tanpa modifikasi logika maupun data simulasi. Perubahan antarmuka checklist sepenuhnya ditangani pada lapisan tampilan (`app.py` dan `assets/style.css`).
