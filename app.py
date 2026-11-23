"""CardioCare - Sistem Pakar Diagnosis Penyakit Jantung (CBR + Cosine Similarity).
Tampilan & interaksi Streamlit. Semua logika CBR ada di backend/ (tanpa diubah).
"""
from datetime import datetime
import json
from pathlib import Path

import streamlit as st

from backend import cbr
from backend.data import (
    Basis_Kasus,
    Gejala,
    Gejala_Berat,
    Gejala_Ringan,
    Gejala_Sedang,
    Penyakit,
)

st.set_page_config(
    page_title="CardioCare - Sistem Pakar Jantung CBR",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = Path(__file__).parent
HALAMAN = [
    "Beranda",
    "Diagnosis",
    "Hasil Diagnosis",
    "Riwayat Diagnosis",
    "Basis Pengetahuan",
    "Tentang Sistem",
]

KATEGORI = [
    ("Gejala Berat", Gejala_Berat, "red", 5),
    ("Gejala Sedang", Gejala_Sedang, "blue", 3),
    ("Gejala Ringan", Gejala_Ringan, "ok", 1),
]

# Pemetaan kode gejala ke kategori & bobot
KATEGORI_MAP = {}
for judul, daftar, warna, bobot in KATEGORI:
    for g in daftar:
        KATEGORI_MAP[g] = (judul, warna, bobot)

ICONS = {
    "alert": '<svg viewBox="0 0 24 24"><path d="M12 3l10 18H2zM12 9v5M12 17h.01"/></svg>',
    "heart": '<svg viewBox="0 0 24 24"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>',
    "steth": '<svg viewBox="0 0 24 24"><path d="M5 3v6a4 4 0 0 0 8 0V3M9 13v2a5 5 0 0 0 10 0v-2"/><circle cx="19" cy="11" r="2"/></svg>',
    "book": '<svg viewBox="0 0 24 24"><path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 21V5"/></svg>',
    "grid": '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>',
    "info": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 11h1v5h1"/></svg>',
    "pulse": '<svg viewBox="0 0 24 24"><path d="M3 12h4l2-4 4 8 3-6 2 2h3"/></svg>',
    "check": '<svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>',
    "history": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
}

ALERT_ICON = f'<span class="cc-disc-icon">{ICONS["alert"]}</span>'
CATATAN = (
    f'<div class="cc-disc">{ALERT_ICON}'
    "<span><b>Catatan medis:</b> Sistem ini merupakan prototype akademik dan bukan pengganti pemeriksaan dokter spesialis jantung. "
    "Hasil diagnosis merupakan indikasi awal berdasarkan tingkat kemiripan kasus lama (Cosine Similarity).</span></div>"
)

# Muat style css
css_file = BASE / "assets/style.css"
if css_file.exists():
    st.markdown(f"<style>{css_file.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# Inisialisasi session state
if "halaman" not in st.session_state:
    st.session_state.halaman = "Beranda"
st.session_state.setdefault("hasil", None)
st.session_state.setdefault("kosong", False)
st.session_state.setdefault("nama_pasien", "Pasien 1")
st.session_state.setdefault("cari_gejala", "")
st.session_state.setdefault("filter_kategori", "Semua")
st.session_state.setdefault("riwayat", [])
st.session_state.setdefault("gejala_terpilih", set())

# Sinkronisasi state checklist antar halaman agar centang tidak hilang
for _kode in Gejala:
    if f"gej_{_kode}" in st.session_state:
        if st.session_state[f"gej_{_kode}"]:
            st.session_state.gejala_terpilih.add(_kode)
        else:
            st.session_state.gejala_terpilih.discard(_kode)
    else:
        st.session_state[f"gej_{_kode}"] = (_kode in st.session_state.gejala_terpilih)


# ---------- Callback functions ----------
def ke_halaman(nama):
    st.session_state.halaman = nama


def reset_jawaban():
    st.session_state.gejala_terpilih = set()
    for kode in Gejala:
        st.session_state[f"gej_{kode}"] = False
    st.session_state.hasil = None
    st.session_state.kosong = False


def pilih_daftar_gejala(daftar_kode):
    for kode in daftar_kode:
        st.session_state[f"gej_{kode}"] = True
        st.session_state.gejala_terpilih.add(kode)


def batalkan_daftar_gejala(daftar_kode):
    for kode in daftar_kode:
        st.session_state[f"gej_{kode}"] = False
        st.session_state.gejala_terpilih.discard(kode)


def proses_diagnosis():
    # Ambil semua gejala yang dicentang (True)
    dipilih = [k for k in Gejala if st.session_state.get(f"gej_{k}", False)]
    if not dipilih:
        st.session_state.kosong = True
        return

    st.session_state.kosong = False
    st.session_state.gejala_terpilih = set(dipilih)

    nama = st.session_state.get("nama_pasien", "").strip() or "Pasien"
    waktu_str = datetime.now().strftime("%d %b %Y, %H:%M")

    # Panggil fungsi backend CBR tanpa modifikasi backend
    ranking = cbr.diagnosa(dipilih)
    bobot = cbr.hitung_bobot(dipilih)

    hasil = {
        "pasien": nama,
        "waktu": waktu_str,
        "dipilih": dipilih,
        "ranking": ranking,
        "bobot": bobot,
    }
    st.session_state.hasil = hasil

    # Simpan ke riwayat diagnosis (urutan terbaru di paling atas)
    top = ranking[0]
    st.session_state.riwayat.insert(
        0,
        {
            "id": len(st.session_state.riwayat) + 1,
            "pasien": nama,
            "waktu": waktu_str,
            "kode": top["kode"],
            "penyakit": top["nama"],
            "similarity": top["similarity"],
            "jumlah_gejala": len(dipilih),
            "bobot": bobot,
            "hasil": hasil,
        },
    )

    st.session_state.halaman = "Hasil Diagnosis"


def buka_riwayat(hasil_data):
    st.session_state.hasil = hasil_data
    st.session_state.halaman = "Hasil Diagnosis"


def hapus_riwayat(idx):
    if 0 <= idx < len(st.session_state.riwayat):
        st.session_state.riwayat.pop(idx)


def hapus_semua_riwayat():
    st.session_state.riwayat = []


def chips(daftar, cocok=None):
    return "".join(
        f'<span class="cc-chip{"" if cocok is None or k in cocok else " no"}">{Gejala[k]}</span>'
        for k in daftar
    )


def ikon(nama, kelas="cc-ico"):
    return f'<div class="{kelas}" aria-hidden="true">{ICONS.get(nama, "")}</div>'


NAV_ICONS = {
    "Beranda": "home",
    "Diagnosis": "checklist",
    "Hasil Diagnosis": "monitoring",
    "Riwayat Diagnosis": "history",
    "Basis Pengetahuan": "menu_book",
    "Tentang Sistem": "info",
}


def label_menu(nama):
    icon_name = NAV_ICONS.get(nama, "circle")
    return f":material/{icon_name}: {nama}"


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(
        f'<div class="cc-side-brand">'
        f'<span class="cc-logo" aria-hidden="true">{ICONS["heart"]}</span>'
        '<div class="cc-brand-copy">'
        '<span class="cc-brand-name">CardioCare</span>'
        '<span class="cc-brand-sub">Sistem Pakar Jantung CBR</span>'
        "</div></div>"
        '<div class="cc-brand-meta"><span class="cc-meta-dot"></span>'
        "CBR · Cosine Similarity</div>",
        unsafe_allow_html=True,
    )

    st.radio(
        "Menu Navigasi",
        HALAMAN,
        key="halaman",
        format_func=label_menu,
        label_visibility="collapsed",
    )

    with st.container(border=True, key="side_action"):
        st.markdown(
            '<div class="cc-side-kicker">Mulai Cepat</div>'
            '<div class="cc-side-title">Kenali Gejala Jantung Anda</div>'
            '<div class="cc-side-copy">Centang gejala yang dirasakan pada checklist interaktif, lalu lihat estimasi kemiripan kasus.</div>',
            unsafe_allow_html=True,
        )
        st.button(
            "Mulai Diagnosis",
            type="primary",
            icon=":material/arrow_forward:",
            use_container_width=True,
            on_click=ke_halaman,
            args=("Diagnosis",),
            key="side_cta",
        )

    with st.container(key="side_footer"):
        st.markdown(
            f'<div class="cc-side-stats">'
            f"<div><b>{len(Gejala)}</b><span>Gejala</span></div>"
            f"<div><b>{len(Penyakit)}</b><span>Penyakit</span></div>"
            f"<div><b>{len(Basis_Kasus)}</b><span>Kasus</span></div>"
            "</div>"
            '<div class="cc-side-foot"><span class="cc-side-dot"></span>'
            "<div><b>Prototype Akademik</b>"
            "<span>Data simulasi · Bukan diagnosis medis final.</span></div></div>",
            unsafe_allow_html=True,
        )

halaman = st.session_state.halaman

# ==============================================================================
# 1. HALAMAN BERANDA
# ==============================================================================
if halaman == "Beranda":
    st.markdown(
        f"""
<div class="cc-hero">
  <div class="cc-hero-copy">
    <div class="cc-eyebrow"><span class="cc-chip">Case-Based Reasoning (CBR)</span></div>
    <h1>Kenali indikasi awal penyakit jantung dengan lebih cepat & jelas.</h1>
    <p>CardioCare membandingkan gejala yang Anda centang pada checklist dengan basis kasus tersimpan, lalu menghitung tingkat kemiripan menggunakan algoritma Cosine Similarity secara transparan.</p>
    <p class="cc-hero-note"><i>Prototype akademik. Data kasus pada aplikasi ini adalah data simulasi pembelajaran sistem pakar.</i></p>
  </div>
  <div class="cc-hero-visual" role="img" aria-label="Visual ringkasan CardioCare">
    <div class="cc-hero-visual-top">
      <div>
        <div class="cc-hero-kicker">Status Sistem Pakar</div>
      </div>
      <div class="cc-hero-pill">CBR Aktif</div>
    </div>
    <svg class="cc-ecg" viewBox="0 0 400 120" preserveAspectRatio="none" aria-hidden="true">
      <path d="M0 70H72l10-10 10 10h18l9 34 14-84 14 92 10-42h28l10-12 10 12h36l8 30 14-80 14 90 10-40h61"/>
    </svg>
    <div class="cc-hero-stats">
      <div class="cc-hero-stat"><b>{len(Gejala)}</b><span>Gejala</span></div>
      <div class="cc-hero-stat"><b>{len(Penyakit)}</b><span>Penyakit</span></div>
      <div class="cc-hero-stat"><b>{len(Basis_Kasus)}</b><span>Basis Kasus</span></div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.container(key="home_actions"):
        a1, a2, _ = st.columns([1.3, 1.4, 3.5])
        a1.button(
            "Mulai Diagnosis",
            type="primary",
            icon=":material/arrow_forward:",
            on_click=ke_halaman,
            args=("Diagnosis",),
        )
        a2.button(
            "Pelajari Metode CBR",
            icon=":material/info:",
            on_click=ke_halaman,
            args=("Tentang Sistem",),
        )

    st.write("")
    langkah = [
        ("check", "1. Centang Gejala", "Pilih gejala yang dialami langsung melalui checklist interaktif tanpa perlu memilih Ya/Tidak."),
        ("grid", "2. Cocokkan Kasus (CBR)", "Sistem menghitung Cosine Similarity terhadap 8 basis kasus penyakit jantung."),
        ("heart", "3. Lihat Hasil & Rekomendasi", "Dapatkan persentase kemiripan, penyakit yang terindikasi, dan saran medis awal.", "red"),
    ]
    with st.container(key="home_steps"):
        cols = st.columns(3)
        for kol, item in zip(cols, langkah):
            ic, judul, teks = item[0], item[1], item[2]
            cls = "cc-ico red" if len(item) > 3 else "cc-ico"
            kol.markdown(
                f'<div class="cc-card cc-step">{ikon(ic, cls)}<h3>{judul}</h3><p class="cc-muted">{teks}</p></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    st.markdown(
        '<div class="cc-card">'
        f'<div class="cc-card-head">{ikon("info", "cc-ico sm")}<h3>Tentang Penyakit Jantung & Sistem Pakar</h3></div>'
        '<p class="cc-muted" style="margin:0;max-width:85ch">Penyakit kardiovaskular mencakup berbagai kelainan pada pembuluh darah, otot jantung, katup, dan irama denyut. '
        "Gejala awal seperti nyeri dada, sesak nafas, dan kelelahan sering kali tumpang tindih antar penyakit. "
        "Metode Case-Based Reasoning membantu mencocokkan pola gejala pasien dengan kasus-kasus medis terdahulu untuk memberikan indikasi awal yang rasional dan transparan.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(CATATAN, unsafe_allow_html=True)

# ==============================================================================
# 2. HALAMAN DIAGNOSIS (CHECKLIST GEJALA)
# ==============================================================================
elif halaman == "Diagnosis":
    st.markdown(
        '<div class="cc-pagehead"><div>'
        '<span class="cc-chip">Langkah 1 dari 2</span>'
        "<h1>Pilih Gejala Pasien (Checklist)</h1>"
        "<p>Centang gejala yang dirasakan oleh pasien. Cukup beri tanda centang pada gejala yang dialami, "
        "gejala yang tidak dicentang otomatis dianggap tidak dialami.</p>"
        "</div>"
        f'<span class="cc-head-badge">{len(Gejala)} total gejala</span></div>',
        unsafe_allow_html=True,
    )

    # Input identitas pasien & pencarian gejala
    with st.container(key="patient_search_box"):
        c_nama, c_cari = st.columns([1.5, 2.5])
        with c_nama:
            st.text_input(
                "Nama Pasien / ID Rekam Medis",
                key="nama_pasien",
                placeholder="Misal: Budi Santoso",
                help="Nama pasien untuk pencatatan pada laporan dan riwayat konsultasi.",
            )
        with c_cari:
            st.text_input(
                "Cari Gejala (Nama atau Kode)",
                key="cari_gejala",
                placeholder="Ketik nama atau kode gejala, misal: Sesak, Nyeri Dada, G01...",
                help="Menyaring tampilan checklist gejala secara instan.",
            )

    # Sinkronisasi jumlah terpilih
    dipilih_saat_ini = [k for k in Gejala if st.session_state.get(f"gej_{k}", False)]
    n_pilih = len(dipilih_saat_ini)
    total_bobot = cbr.hitung_bobot(dipilih_saat_ini)
    status_label = "Siap Diproses" if n_pilih > 0 else "Menunggu Centang"
    status_color = "ok" if n_pilih > 0 else "warn"

    # Bar metrik pengisian
    st.markdown(
        f"""
<div class="cc-metrics">
  <div class="cc-metric"><span>Gejala Dipilih</span><b>{n_pilih}</b><small>dari {len(Gejala)} total gejala ({round(n_pilih / len(Gejala) * 100)}%)</small></div>
  <div class="cc-metric"><span>Total Bobot Gejala</span><b>{total_bobot}</b><small>bobot informasi keparahan (1-5)</small></div>
  <div class="cc-metric"><span>Status Diagnosis</span><b>{status_label}</b><small>{'dapat langsung diproses' if n_pilih > 0 else 'centang minimal 1 gejala'}</small></div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Progres bar
    st.markdown(
        f'<div class="cc-progress-meta"><b>Progres Checklist</b><span>{n_pilih} / {len(Gejala)} gejala terpilih</span></div>',
        unsafe_allow_html=True,
    )
    st.progress(n_pilih / len(Gejala), text=None)

    # Filter Kategori & Tombol Aksi Cepat
    c_tab, c_quick = st.columns([2, 1.8])
    with c_tab:
        kat_pilihan = st.pills(
            "Filter Tampilan Kategori",
            ["Semua", "Gejala Berat (7)", "Gejala Sedang (18)", "Gejala Ringan (6)"],
            default="Semua",
            key="filter_kategori_pill",
            label_visibility="collapsed",
        )
    with c_quick:
        q1, q2 = st.columns(2)
        q1.button(
            "Reset Checklist",
            icon=":material/refresh:",
            use_container_width=True,
            on_click=reset_jawaban,
            help="Hapus semua centang gejala.",
        )
        q2.button(
            "Proses Diagnosis",
            type="primary",
            icon=":material/arrow_forward:",
            use_container_width=True,
            on_click=proses_diagnosis,
            help="Mulai analisis kemiripan dengan CBR.",
        )

    st.write("")

    # Filter data berdasarkan pencarian dan kategori
    keyword = st.session_state.get("cari_gejala", "").strip().lower()

    # Siapkan daftar kategori yang akan ditampilkan
    kategori_aktif = []
    if "Berat" in kat_pilihan:
        kategori_aktif = [("Gejala Berat", Gejala_Berat, "red", 5)]
    elif "Sedang" in kat_pilihan:
        kategori_aktif = [("Gejala Sedang", Gejala_Sedang, "blue", 3)]
    elif "Ringan" in kat_pilihan:
        kategori_aktif = [("Gejala Ringan", Gejala_Ringan, "ok", 1)]
    else:
        kategori_aktif = KATEGORI

    total_gejala_tampil = 0

    for judul_kat, daftar_kode, warna, bobot_val in kategori_aktif:
        # Filter berdasarkan kata kunci pencarian
        if keyword:
            daftar_filtered = [
                k for k in daftar_kode
                if keyword in Gejala[k].lower() or keyword in k.lower()
            ]
        else:
            daftar_filtered = daftar_kode

        if not daftar_filtered:
            continue

        total_gejala_tampil += len(daftar_filtered)

        # Header kategori
        st.markdown(
            f'<div class="cc-section-title"><span class="cc-dot {warna}"></span>'
            f'<h3>{judul_kat}</h3>'
            f'<span class="cc-muted">({len(daftar_filtered)} gejala · Bobot {bobot_val})</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Tampilkan checklist dalam 2 kolom responsif
        col_left, col_right = st.columns(2)
        for idx, kode in enumerate(daftar_filtered):
            target_col = col_left if (idx % 2 == 0) else col_right
            with target_col:
                with st.container(key=f"chk_card_{warna}_{kode}"):
                    st.checkbox(
                        f"**{Gejala[kode]}** `{kode}`",
                        key=f"gej_{kode}",
                        help=f"Gejala {kode} ({judul_kat}, Bobot {bobot_val})",
                    )

    if total_gejala_tampil == 0:
        st.markdown(
            '<div class="cc-card cc-empty" style="padding:2rem;">'
            f'<div class="cc-empty-icon">{ICONS["pulse"]}</div>'
            "<h3>Tidak ada gejala yang cocok</h3>"
            f"<p>Tidak ditemukan gejala dengan kata kunci '<b>{keyword}</b>'. Silakan periksa kembali ejaan pencarian Anda.</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.write("")

    if st.session_state.kosong:
        st.warning("⚠️ Silakan centang minimal satu gejala pada checklist sebelum memproses diagnosis.")

    # Tombol Aksi di Bagian Bawah
    with st.container(key="consult_actions"):
        a, b, _ = st.columns([1.5, 1.2, 3.3])
        a.button("Proses Diagnosis Sekarang", type="primary", icon=":material/arrow_forward:", on_click=proses_diagnosis)
        b.button("Reset Semua Centang", icon=":material/refresh:", on_click=reset_jawaban)

    st.markdown(CATATAN, unsafe_allow_html=True)

# ==============================================================================
# 3. HALAMAN HASIL DIAGNOSIS
# ==============================================================================
elif halaman == "Hasil Diagnosis":
    st.markdown(
        '<div class="cc-pagehead"><div>'
        '<span class="cc-chip">Langkah 2 dari 2</span>'
        "<h1>Hasil Analisis Kemiripan Kasus</h1>"
        "<p>Indikasi awal penyakit jantung berdasarkan perhitungan Cosine Similarity dengan basis kasus. "
        "Gunakan hasil ini sebagai rujukan awal sebelum berkonsultasi lebih lanjut dengan dokter spesialis.</p>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    h = st.session_state.hasil
    if not h:
        st.markdown(
            '<div class="cc-card cc-empty">'
            f'<div class="cc-empty-icon">{ICONS["pulse"]}</div>'
            "<h3>Belum ada hasil diagnosis</h3>"
            "<p>Anda belum mengisi checklist gejala. Silakan buka halaman <b>Diagnosis</b>, centang gejala yang dialami, lalu tekan <b>Proses Diagnosis</b>.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.write("")
        st.button("Ke Halaman Diagnosis", type="primary", icon=":material/checklist:", on_click=ke_halaman, args=("Diagnosis",))
    else:
        top = h["ranking"][0]
        pct = top["similarity"]
        lvl = "Tinggi" if pct >= 75 else "Sedang" if pct >= 50 else "Rendah"
        lvl_cls = "red" if pct >= 75 else "warn" if pct >= 50 else "ok"
        dash = 597 * (1 - pct / 100)

        # Ringkasan identitas pasien & waktu
        nama_pasien_str = h.get("pasien", "Pasien")
        waktu_str = h.get("waktu", "-")

        st.markdown(
            f"""
<div class="cc-card cc-result-main">
  <div class="cc-ring" aria-label="Tingkat kemiripan {pct:.2f} persen">
    <svg width="240" height="240" viewBox="0 0 240 240">
      <circle class="bg" cx="120" cy="120" r="95"/>
      <circle class="fg" cx="120" cy="120" r="95" style="stroke-dashoffset:{dash:.1f}"/>
    </svg>
    <div class="cc-ring-val"><b>{pct:.2f}%</b><span>Kemiripan Kasus</span></div>
  </div>
  <div>
    <div style="display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;margin-bottom:.4rem;">
      <span class="cc-chip {lvl_cls}">Tingkat Kemiripan {lvl}</span>
      <span class="cc-chip">Pasien: {nama_pasien_str}</span>
      <span class="cc-chip no">{waktu_str}</span>
    </div>
    <h2 class="cc-result-title">{top["nama"]} ({top["kode"]})</h2>
    <p class="cc-result-lead">Berdasarkan <b>{len(h['dipilih'])} gejala</b> yang Anda centang pada checklist, sistem menemukan kemiripan tertinggi sebesar <b>{pct:.2f}%</b> dengan kasus <b>{top['nama']}</b> pada basis pengetahuan CBR.</p>
    <div class="cc-subtle-label">Gejala yang cocok dengan kasus ini ({len(top["gejala_cocok"])})</div>
    <div class="cc-chip-wrap">{chips(top["gejala_cocok"], top["gejala_cocok"])}</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.write("")

        # Peringkat Kemiripan Semua Kasus (8 Penyakit)
        baris = "".join(
            f'<div class="cc-row{" top" if i == 0 else ""}">'
            f'<span><b>#{i + 1}</b> {r["nama"]} <small>({r["kode"]})</small></span>'
            f'<div class="cc-bar"><i style="width:{max(r["similarity"], 0):.1f}%"></i></div>'
            f"<b>{r['similarity']:.2f}%</b></div>"
            for i, r in enumerate(h["ranking"])
        )
        st.markdown(
            f'<div class="cc-card">'
            f'<div class="cc-card-head">{ikon("grid", "cc-ico sm")}<h3>Peringkat Kemiripan Seluruh Penyakit</h3></div>'
            f'<p class="cc-muted" style="margin-top:-.3rem;margin-bottom:.9rem;">Perbandingan nilai Cosine Similarity terhadap seluruh 8 basis kasus dalam sistem:</p>'
            f'{baris}</div>',
            unsafe_allow_html=True,
        )

        st.write("")

        # Detail Perbandingan Gejala & Saran Medis
        with st.container(key="result_details"):
            k1, k2 = st.columns(2)

            # Gejala yang dicentang vs gejala yang tidak cocok
            gejala_tak_cocok = [k for k in h["dipilih"] if k not in top["gejala_cocok"]]
            with k1:
                st.markdown(
                    f'<div class="cc-card">'
                    f'<div class="cc-card-head">{ikon("steth", "cc-ico sm")}<h3>Analisis Gejala Terpilih ({len(h["dipilih"])})</h3></div>'
                    f'<div style="margin-bottom:.5rem;"><b>Gejala Cocok dengan {top["kode"]}:</b></div>'
                    f'<div class="cc-chip-wrap">{chips(top["gejala_cocok"], top["gejala_cocok"])}</div>'
                    + (
                        f'<div style="margin-top:.85rem;margin-bottom:.5rem;"><b>Gejala Lain yang Anda Centang:</b></div>'
                        f'<div class="cc-chip-wrap">{chips(gejala_tak_cocok)}</div>'
                        if gejala_tak_cocok
                        else ""
                    )
                    + "</div>",
                    unsafe_allow_html=True,
                )

            # Saran & Rekomendasi Klinis
            with k2:
                if pct >= 75:
                    saran_teks = (
                        "<b>Tingkat kemiripan tergolong TINGGI (≥75%).</b><br>"
                        "• Sangat disarankan untuk segera berkonsultasi ke <b>Dokter Spesialis Jantung & Pembuluh Darah (Sp.JP)</b>.<br>"
                        "• Bila Anda mengalami nyeri dada sebelah kiri menjalar ke pundak/lengan, keringat dingin, atau sesak nafas mendadak, segera menuju ke IGD terdekat.<br>"
                        "• Batasi aktivitas fisik berat dan hindari pemicu stres berlebih."
                    )
                elif pct >= 50:
                    saran_teks = (
                        "<b>Tingkat kemiripan tergolong SEDANG (50%–74%).</b><br>"
                        "• Disarankan untuk menjadwalkan pemeriksaan elektrokardiogram (EKG) atau konsultasi dokter umum.<br>"
                        "• Catat frekuensi dan situasi saat gejala muncul untuk memudahkan dokter mengevaluasi kondisi Anda.<br>"
                        "• Jaga pola makan rendah garam dan cukup istirahat."
                    )
                else:
                    saran_teks = (
                        "<b>Tingkat kemiripan tergolong RENDAH (<50%).</b><br>"
                        "• Gejala yang Anda centang memiliki kemiripan rendah dengan pola kasus spesifik dalam basis pengetahuan.<br>"
                        "• Meskipun demikian, jika keluhan mengganggu kenyamanan dan aktivitas harian Anda, tetap lakukan konsultasi kesehatan.<br>"
                        "• Pertahankan gaya hidup sehat, hidrasi cukup, dan olahraga teratur."
                    )

                st.markdown(
                    f'<div class="cc-card">'
                    f'<div class="cc-card-head">{ikon("heart", "cc-ico sm red")}<h3>Saran & Tindak Lanjut</h3></div>'
                    f'<div class="cc-muted" style="line-height:1.7;">{saran_teks}</div>'
                    "</div>",
                    unsafe_allow_html=True,
                )

        st.write("")

        # Info proses matematis CBR
        st.markdown(
            '<div class="cc-card">'
            f'<div class="cc-card-head">{ikon("info", "cc-ico sm")}<h3>Transparansi Perhitungan Algoritma CBR</h3></div>'
            f'<p class="cc-muted" style="margin:0">Setiap gejala yang Anda centang dikonversi menjadi vektor biner <b>31 dimensi</b> (1 = dicentang, 0 = tidak dicentang). '
            f'Vektor tersebut kemudian dibandingkan secara manual dengan 8 vektor kasus melalui rumus <b>Cosine Similarity</b>. '
            f'Total bobot gejala yang Anda pilih adalah <b>{h["bobot"]}</b> (berdasarkan tingkat keparahan: Berat=5, Sedang=3, Ringan=1).</p>'
            "</div>",
            unsafe_allow_html=True,
        )

        st.write("")

        # Tombol aksi hasil
        b1, b2, b3, _ = st.columns([1.4, 1.4, 1.6, 2.6])
        b1.button("Diagnosis Ulang", type="primary", icon=":material/checklist:", on_click=ke_halaman, args=("Diagnosis",))
        b2.button("Lihat Riwayat", icon=":material/history:", on_click=ke_halaman, args=("Riwayat Diagnosis",))

        # Unduh Ringkasan Hasil
        laporan_teks = f"""=== LAPORAN HASIL DIAGNOSIS CARDIOCARE ===
Waktu        : {waktu_str}
Nama Pasien  : {nama_pasien_str}
Indikasi     : {top['nama']} ({top['kode']})
Kemiripan    : {pct:.2f}% ({lvl})
Total Bobot  : {h['bobot']}

GEJALA YANG DICENTANG ({len(h['dipilih'])}):
{', '.join([f"{k} - {Gejala[k]}" for k in h['dipilih']])}

GEJALA YANG COCOK ({len(top['gejala_cocok'])}):
{', '.join([f"{k} - {Gejala[k]}" for k in top['gejala_cocok']])}

PERINGKAT SEMUA KASUS:
""" + "\n".join([f"- {r['kode']}: {r['nama']} = {r['similarity']:.2f}%" for r in h['ranking']]) + """

Catatan: Prototype akademik berbasis CBR Cosine Similarity. Bukan pengganti pemeriksaan dokter medis.
"""
        b3.download_button(
            label="Unduh Laporan (TXT)",
            data=laporan_teks,
            file_name=f"CardioCare_{nama_pasien_str.replace(' ', '_')}_{top['kode']}.txt",
            mime="text/plain",
            icon=":material/download:",
        )

        st.markdown(CATATAN, unsafe_allow_html=True)

# ==============================================================================
# 4. HALAMAN RIWAYAT DIAGNOSIS
# ==============================================================================
elif halaman == "Riwayat Diagnosis":
    st.markdown(
        '<div class="cc-pagehead"><div>'
        '<span class="cc-chip">Penyimpanan Sesi</span>'
        "<h1>Riwayat Diagnosis Pasien</h1>"
        "<p>Daftar konsultasi dan hasil evaluasi CBR yang telah dilakukan selama sesi ini. "
        "Anda dapat meninjau kembali detail hasil atau menghapus riwayat.</p>"
        "</div>"
        f'<span class="cc-head-badge">{len(st.session_state.riwayat)} riwayat</span></div>',
        unsafe_allow_html=True,
    )

    riwayat_list = st.session_state.riwayat

    if not riwayat_list:
        st.markdown(
            '<div class="cc-card cc-empty">'
            f'<div class="cc-empty-icon">{ICONS["history"]}</div>'
            "<h3>Belum ada riwayat diagnosis</h3>"
            "<p>Riwayat akan tersimpan otomatis setiap kali Anda memproses checklist gejala pada halaman Diagnosis.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.write("")
        st.button("Mulai Diagnosis Sekarang", type="primary", icon=":material/checklist:", on_click=ke_halaman, args=("Diagnosis",))
    else:
        # Metrik ringkasan riwayat
        avg_sim = sum(item["similarity"] for item in riwayat_list) / len(riwayat_list)
        penyakit_counts = {}
        for item in riwayat_list:
            penyakit_counts[item["penyakit"]] = penyakit_counts.get(item["penyakit"], 0) + 1
        top_penyakit_sering = max(penyakit_counts, key=penyakit_counts.get)

        st.markdown(
            f"""
<div class="cc-metrics">
  <div class="cc-metric"><span>Total Riwayat</span><b>{len(riwayat_list)}</b><small>konsultasi tercatat</small></div>
  <div class="cc-metric"><span>Rata-Rata Kemiripan</span><b>{avg_sim:.1f}%</b><small>dari seluruh diagnosis</small></div>
  <div class="cc-metric"><span>Paling Sering Terindikasi</span><b>{top_penyakit_sering}</b><small>{penyakit_counts[top_penyakit_sering]} kali muncul</small></div>
</div>
""",
            unsafe_allow_html=True,
        )

        r_act1, r_act2, _ = st.columns([1.5, 1.5, 3])
        r_act1.button("Mulai Diagnosis Baru", type="primary", icon=":material/add:", on_click=ke_halaman, args=("Diagnosis",))
        r_act2.button("Hapus Semua Riwayat", icon=":material/delete:", on_click=hapus_semua_riwayat)

        st.write("")

        # Tampilkan setiap baris riwayat
        for idx, item in enumerate(riwayat_list):
            with st.container():
                c_info, c_action = st.columns([4.2, 1.8])
                with c_info:
                    sim_val = item["similarity"]
                    sim_cls = "red" if sim_val >= 75 else "warn" if sim_val >= 50 else "ok"
                    st.markdown(
                        f'<div class="cc-hist-card">'
                        f'<div class="cc-hist-header">'
                        f'<span class="cc-hist-patient">{item["pasien"]}</span>'
                        f'<span class="cc-hist-time">{item["waktu"]}</span>'
                        f"</div>"
                        f'<div class="cc-hist-body">'
                        f'<div>Indikasi: <b class="cc-hist-disease">{item["penyakit"]}</b> ({item["kode"]})</div>'
                        f'<div style="display:flex;gap:.5rem;align-items:center;">'
                        f'<span class="cc-chip {sim_cls}">Kemiripan {sim_val:.2f}%</span>'
                        f'<span class="cc-chip no">{item["jumlah_gejala"]} gejala</span>'
                        f"</div></div></div>",
                        unsafe_allow_html=True,
                    )
                with c_action:
                    st.write("")
                    b_buka, b_hapus = st.columns(2)
                    b_buka.button(
                        "Buka",
                        key=f"buka_{item['id']}_{idx}",
                        icon=":material/visibility:",
                        use_container_width=True,
                        on_click=buka_riwayat,
                        args=(item["hasil"],),
                    )
                    b_hapus.button(
                        "Hapus",
                        key=f"hapus_{item['id']}_{idx}",
                        icon=":material/delete:",
                        use_container_width=True,
                        on_click=hapus_riwayat,
                        args=(idx,),
                    )

    st.markdown(CATATAN, unsafe_allow_html=True)

# ==============================================================================
# 5. HALAMAN BASIS PENGETAHUAN
# ==============================================================================
elif halaman == "Basis Pengetahuan":
    st.markdown(
        '<div class="cc-pagehead"><div>'
        '<span class="cc-chip">Basis Pengetahuan CBR</span>'
        "<h1>Basis Pengetahuan & Data Kasus</h1>"
        "<p>Daftar 8 basis kasus penyakit jantung dan kamus 31 gejala medis yang tersimpan dalam sistem pakar.</p>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    tab_kasus, tab_gejala = st.tabs(["8 Basis Kasus Penyakit", "Kamus 31 Data Gejala"])

    with tab_kasus:
        st.markdown("<p class='cc-muted'>Berikut adalah basis kasus (K01–K08) yang digunakan sebagai acuan perbandingan Cosine Similarity:</p>", unsafe_allow_html=True)
        for i in range(0, len(Basis_Kasus), 2):
            cols = st.columns(2)
            for kol, kasus in zip(cols, Basis_Kasus[i : i + 2]):
                kode = kasus["kode_penyakit"]
                nama_penyakit = Penyakit[kode]
                daftar_g = kasus["gejala"]
                kol.markdown(
                    f'<div class="cc-card cc-disease">'
                    f'<div class="cc-disease-top"><span class="cc-code">{kode}</span>'
                    f'<span class="cc-muted" style="font-size:.84rem;font-weight:700">{len(daftar_g)} gejala terkait</span></div>'
                    f"<h3>{nama_penyakit}</h3>"
                    f'<p class="cc-muted" style="font-size:.85rem;margin-bottom:.5rem;">Gejala khas pada kasus acuan:</p>'
                    f'<div class="cc-chip-wrap">{chips(daftar_g)}</div>'
                    "</div>",
                    unsafe_allow_html=True,
                )
            st.write("")

    with tab_gejala:
        st.markdown("<p class='cc-muted'>Kamus lengkap 31 gejala penyakit jantung beserta tingkat keparahan dan bobot informasinya:</p>", unsafe_allow_html=True)

        cari_gej_kb = st.text_input(
            "Cari Gejala di Basis Data",
            placeholder="Cari berdasarkan kode atau nama gejala...",
            key="cari_gej_kb",
        )

        baris_tabel = []
        for kode, nama in Gejala.items():
            if cari_gej_kb and (cari_gej_kb.lower() not in nama.lower() and cari_gej_kb.lower() not in kode.lower()):
                continue

            kat_judul, kat_warna, bobot_val = KATEGORI_MAP.get(kode, ("-", "no", 1))

            # Hitung muncul di berapa kasus
            muncul_di = [k["kode_penyakit"] for k in Basis_Kasus if kode in k["gejala"]]
            muncul_str = ", ".join(muncul_di) if muncul_di else "Tidak ada"

            baris_tabel.append(
                f"<tr>"
                f"<td><b>{kode}</b></td>"
                f"<td><b>{nama}</b></td>"
                f'<td><span class="cc-badge {kat_warna}">{kat_judul}</span></td>'
                f"<td>{bobot_val}</td>"
                f"<td><small>{muncul_str} ({len(muncul_di)} kasus)</small></td>"
                f"</tr>"
            )

        tabel_html = (
            '<div style="overflow-x:auto;">'
            '<table class="cc-kb-table">'
            "<thead><tr>"
            "<th>Kode</th>"
            "<th>Nama Gejala</th>"
            "<th>Kategori</th>"
            "<th>Bobot</th>"
            "<th>Muncul di Kasus</th>"
            "</tr></thead>"
            "<tbody>" + "".join(baris_tabel) + "</tbody>"
            "</table></div>"
        )
        st.markdown(tabel_html, unsafe_allow_html=True)

    st.markdown(CATATAN, unsafe_allow_html=True)

# ==============================================================================
# 6. HALAMAN TENTANG SISTEM
# ==============================================================================
else:
    st.markdown(
        '<div class="cc-pagehead"><div>'
        '<span class="cc-chip">Konsep & Metode</span>'
        "<h1>Tentang Sistem & Metode CBR</h1>"
        "<p>Penjelasan mengenai prinsip penalaran Case-Based Reasoning, algoritma Cosine Similarity, dan tujuan pengembangan prototype CardioCare.</p>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    info = [
        ("info", "Sistem Pakar", "Program komputer cerdas yang dirancang untuk mengadopsi keahlian pakar dalam menyelesaikan masalah spesifik."),
        ("grid", "Case-Based Reasoning", "Metodologi penalaran yang menyelesaikan masalah baru dengan mencari kemiripan terhadap kasus-kasus terdahulu."),
        ("heart", "Cosine Similarity", "Metode pengukuran sudut cosinus antara vektor biner pengguna dan vektor kasus acuan (skala 0%–100%).", "red"),
        ("book", "Tujuan Prototype", "Media pembelajaran dan demonstrasi akademik implementasi CBR murni tanpa library ML kompleks."),
    ]
    with st.container(key="about_grid"):
        cols = st.columns(2) + st.columns(2)
        for kol, item in zip(cols, info):
            ic, j, t = item[0], item[1], item[2]
            cls = "cc-ico red" if len(item) > 3 else "cc-ico"
            kol.markdown(
                f'<div class="cc-card cc-step">{ikon(ic, cls)}<h3>{j}</h3><p class="cc-muted">{t}</p></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    st.markdown(
        '<div class="cc-section-title"><h3>Tahapan Siklus Case-Based Reasoning (4R)</h3><span class="cc-muted">Alur penalaran sistem pakar</span></div>',
        unsafe_allow_html=True,
    )
    tahap = [
        ("1", "Retrieve (Memperoleh)", "Mengambil kasus lama yang paling mirip dengan gejala pengguna dari basis pengetahuan."),
        ("2", "Reuse (Menggunakan)", "Memanfaatkan solusi atau diagnosis dari kasus terpilih untuk menyelesaikan masalah baru."),
        ("3", "Revise (Meninjau)", "Mengevaluasi hasil kecocokan bersama dokter atau pengguna apabila ada ketidaksesuaian."),
        ("4", "Retain (Menyimpan)", "Menyimpan kasus baru yang telah tervalidasi ke dalam riwayat atau basis pengetahuan."),
    ]
    with st.container(key="cbr_flow"):
        for kol, (n, j, t) in zip(st.columns(4), tahap):
            kol.markdown(
                f'<div class="cc-card cc-flow"><div class="cc-flow-n">{n}</div><h3>{j}</h3><p class="cc-muted">{t}</p></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    st.markdown(
        '<div class="cc-card">'
        f'<div class="cc-card-head">{ikon("grid", "cc-ico sm")}<h3>Rumus Cosine Similarity</h3></div>'
        "<p class='cc-muted'>Cosine Similarity menghitung kosinus sudut antara dua vektor gejala n-dimensi (A = Vektor Gejala Pasien, B = Vektor Gejala Kasus):</p>"
        r"$$\text{Cosine Similarity}(A, B) = \frac{A \cdot B}{\|A\| \times \|B\|} = \frac{\sum_{i=1}^{n} (A_i \times B_i)}{\sqrt{\sum_{i=1}^{n} A_i^2} \times \sqrt{\sum_{i=1}^{n} B_i^2}} \times 100\%$$"
        "<p class='cc-muted' style='margin-top:.8rem;'>Karena vektor gejala bersifat <b>biner</b> (1 untuk gejala dialami, 0 untuk tidak), perkalian titik \\(A \\cdot B\\) secara langsung merepresentasikan <b>jumlah gejala yang cocok (irisan)</b> antara pasien dan kasus acuan.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(CATATAN, unsafe_allow_html=True)
