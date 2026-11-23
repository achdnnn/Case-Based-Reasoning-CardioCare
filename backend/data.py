"""Basis pengetahuan CardioCare (data simulasi). Jangan ubah kode & isinya tanpa persetujuan."""

Penyakit = {
    "PO1": "Penyakit Jantung Koroner",
    "PO2": "Infark Miokard Akut",
    "PO3": "Gagal Jantung",
    "PO4": "Kardiomipati",
    "PO5": "Kelainan Katup jantung",
    "PO6": "Rematik Jantung",
    "PO7": "Fibrilasi Atrial",
    "PO8": "Penyakit Jantung Bawaan",
}

Gejala = {
    "G01": "Sesak Nafas", "G02": "Sakit dan atau Nyeri Pada Dada",
    "G03": "Buang Air Kecil Terlalu Banyak", "G04": "Sakit Kepala",
    "G05": "Rasa Lapar/Haus Berlebihan", "G06": "Kelelahan",
    "G07": "Infeksi Berulang-Ulang", "G08": "Mengkonsumsi Minuman Berakohol",
    "G09": "Perokok", "G10": "Ganguan Tidur",
    "G11": "Efisiensi Kerja Menurun", "G12": "Tingkat Aktivitas Menurun",
    "G13": "Kurang Percaya Diri", "G14": "Perasaan Terbebani",
    "G15": "Merasa Tidak Berguna", "G16": "Tengkuk dan Pundak Pegal",
    "G17": "Sering Pegal dan Kesemutan", "G18": "Pusing",
    "G19": "Pendarahan Pada Hidung", "G20": "Luka Susah Sembuh",
    "G21": "Frekuensi Detak Jantung Tidak Normal", "G22": "Pengelihatan Kabur",
    "G23": "Telinga Berdenging", "G24": "Wajah Memerah",
    "G25": "Kekakuan Sekitar Sendi Pada Pagi Hari",
    "G26": "Bengkak Pada Beberapa Sendi Saat Bersamaan",
    "G27": "Nyeri Pada Sendi Yang Sama Pada Kedua Tubuh",
    "G28": "Mudah Panik", "G29": "Gangguan Pencernaan",
    "G30": "Berkeringat", "G31": "Merasa Mual",
}

Gejala_Ringan = ["G03", "G05", "G07", "G19", "G20", "G23"]
Gejala_Sedang = ["G04", "G08", "G10", "G11", "G12", "G13", "G14", "G17", "G18",
                 "G22", "G24", "G25", "G26", "G27", "G28", "G29", "G30", "G31"]
Gejala_Berat = ["G01", "G02", "G06", "G09", "G15", "G16", "G21"]

Basis_Kasus = [
    {"kode_penyakit": "PO1", "gejala": ["G02", "G05", "G06", "G09", "G01", "G21", "G31", "G30", "G17", "G16", "G27", "G26"]},
    {"kode_penyakit": "PO2", "gejala": ["G09", "G02", "G01", "G06", "G21", "G27", "G22", "G23", "G28", "G31", "G16", "G17", "G20", "G11", "G12", "G13", "G14"]},
    {"kode_penyakit": "PO3", "gejala": ["G01", "G06", "G27", "G26", "G07", "G08", "G11", "G12", "G13", "G14"]},
    {"kode_penyakit": "PO4", "gejala": ["G08", "G09", "G01", "G02", "G07", "G19", "G20", "G21", "G23", "G24", "G26", "G06", "G18"]},
    {"kode_penyakit": "PO5", "gejala": ["G01", "G02", "G12", "G18", "G06", "G21", "G29", "G25", "G26", "G27"]},
    {"kode_penyakit": "PO6", "gejala": ["G01", "G27", "G25", "G17", "G06", "G10", "G26", "G29"]},
    {"kode_penyakit": "PO7", "gejala": ["G01", "G02", "G06", "G18", "G28", "G21", "G10", "G04", "G13", "G14"]},
    {"kode_penyakit": "PO8", "gejala": ["G08", "G09", "G01", "G29", "G28", "G02", "G18", "G07", "G21", "G26", "G27"]},
]
