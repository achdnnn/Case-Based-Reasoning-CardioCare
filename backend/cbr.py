"""Logika CBR manual (tanpa library tambahan)."""
from backend.data import (Gejala, Gejala_Ringan, Gejala_Sedang, Gejala_Berat,
                          Basis_Kasus, Penyakit)


def hitung_bobot(gejala_Dipilih):
    """Total bobot gejala (ringan=1, sedang=3, berat=5).
    CATATAN: hanya informasi, TIDAK dipakai dalam rumus Cosine Similarity."""
    n = 0
    for g in gejala_Dipilih:
        if g in Gejala_Ringan:
            n += 1
        elif g in Gejala_Sedang:
            n += 3
        elif g in Gejala_Berat:
            n += 5
    return n


def toBinary(gejala_Dipilih):
    """Ubah daftar gejala menjadi vektor biner 31 elemen (urutan G01..G31)."""
    hasil = []
    for kode in Gejala:
        if kode in gejala_Dipilih:
            hasil += [1]
        else:
            hasil += [0]
    return hasil


def cosine_similarity(A, B):
    """Cosine Similarity = (A.B) / (|A| x |B|), hasil dalam persen."""
    if len(A) != len(B):
        print("panjang vektor tidak valid!")
        return 0
    AB_atas = 0                      # perkalian titik A.B
    for i in range(len(A)):
        AB_atas += A[i] * B[i]
    AB_A = 0                         # panjang vektor A
    for i in range(len(A)):
        AB_A += A[i] ** 2
    AB_A = AB_A ** 0.5
    AB_B = 0                         # panjang vektor B
    for i in range(len(B)):
        AB_B += B[i] ** 2
    AB_B = AB_B ** 0.5
    AB_bawah = AB_A * AB_B
    if AB_bawah == 0:
        return 0
    return (AB_atas / AB_bawah) * 100


def diagnosa(gejala_Dipilih):
    """Bandingkan gejala pengguna dengan 8 basis kasus, urut similarity tertinggi.
    Mengembalikan list kosong jika tidak ada gejala dipilih."""
    if not gejala_Dipilih:
        return []
    vektor_user = toBinary(gejala_Dipilih)
    hasil = []
    for kasus in Basis_Kasus:
        vektor_kasus = toBinary(kasus["gejala"])
        kode = kasus["kode_penyakit"]
        hasil.append({
            "kode": kode,
            "nama": Penyakit[kode],
            "similarity": cosine_similarity(vektor_user, vektor_kasus),
            "gejala_cocok": [g for g in gejala_Dipilih if g in kasus["gejala"]],
        })
    hasil.sort(key=lambda x: x["similarity"], reverse=True)
    return hasil
