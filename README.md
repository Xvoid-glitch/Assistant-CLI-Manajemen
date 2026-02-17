# 🚀 R Assist v3.0

**R Assist** adalah asisten CLI personal serba guna berbasis Python — dirancang untuk membantu produktivitas harian, manajemen keuangan, pelacakan kebiasaan, dan banyak lagi. Semua teks antarmuka dalam **Bahasa Indonesia**.

---

## ✨ Fitur

| # | Modul | Deskripsi |
|---|-------|-----------|
| 1 | 📅 Jadwal Pelajaran | Atur jadwal harian & mingguan |
| 2 | 📝 Catatan Pintar | Buat & kelola catatan |
| 3 | ✅ Manajer Task | Target dan deadline |
| 4 | 💰 Pencatat Pengeluaran | Catat keuangan harian |
| 5 | 🔥 Pelacak Kebiasaan | Streak & check-in harian |
| 6 | ⚡ Utilitas | Password generator, QR code, konverter |
| 7 | 🎯 Alat Belajar | Pomodoro timer & musik fokus |
| 8 | 📋 Manajer Clipboard | Simpan & cari teks |
| 9 | 🌐 Cek Jaringan | Ping, speed test, IP publik |
| 10 | 🧠 Pelatih Produktivitas | Analisa & motivasi harian |
| 11 | 📊 Dashboard Kehidupan | Ringkasan satu layar |
| 12 | 💀 Dirimu di Masa Depan | Target 1 tahun & refleksi |
| 13 | 💸 Mode Bertahan Finansial | Simulasi keuangan |
| 14 | ⛅ Info Cuaca | Prakiraan cuaca real-time |

---

## 📦 Instalasi

### Prasyarat

- Python 3.10+

### Windows (PowerShell)

```powershell
git clone https://github.com/Xvoid-glitch/Assistant-CLI-Manajemen.git
cd "Assistant cli"
.\install.ps1
```

### Linux / macOS

```bash
git clone https://github.com/Xvoid-glitch/Assistant-CLI-Manajemen.git
cd "Assistant cli"
chmod +x install.sh
./install.sh
```

### Manual

```bash
python -m venv venv
# Windows: .\venv\Scripts\Activate
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python rizz_assistant.py
```

---

## 📁 Struktur Proyek

```
r-assist/
├── rizz_assistant.py      # Entry point utama
├── requirements.txt       # Dependensi Python
├── install.ps1            # Installer Windows
├── install.sh             # Installer Linux/macOS
├── config/
│   └── config_manager.py  # Manajemen profil & konfigurasi
├── modules/
│   ├── ai_chat.py         # AI Chat
│   ├── clipboard_manager.py
│   ├── converter.py
│   ├── database.py        # SQLite database handler
│   ├── expense_tracker.py
│   ├── financial_survival.py
│   ├── future_you.py
│   ├── habit_tracker.py
│   ├── jadwal.py
│   ├── life_dashboard.py
│   ├── network_check.py
│   ├── notes.py
│   ├── organizer.py
│   ├── productivity_coach.py
│   ├── study_tools.py
│   ├── tasks.py
│   ├── utilities.py
│   └── weather.py
├── data/                  # Data runtime (auto-generated)
├── backups/               # Backup data
└── assets/                # Aset tambahan
```

---

## 🛠️ Teknologi

- **[Rich](https://github.com/Textualize/rich)** — UI terminal yang cantik
- **[Click](https://click.palletsprojects.com/)** — CLI framework
- **SQLite** — Database lokal ringan
- **psutil** — Informasi sistem
- **requests** — HTTP client

---

## 📜 Lisensi

MIT License — Bebas dipakai dan dimodifikasi.
