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
cd Assistant cli
.\install.ps1
```

### Linux / macOS

```bash
git clone https://github.com/Xvoid-glitch/Assistant-CLI-Manajemen.git
cd Assistant cli
chmod +x install.sh
./install.sh
```

### 📱 Termux (Android)

Panduan lengkap step-by-step untuk instalasi di **Termux** (HP Android):

**Step 1 — Install Termux**

Download & install [Termux dari F-Droid](https://f-droid.org/en/packages/com.termux/) (jangan dari Play Store, versi Play Store sudah discontinued).

**Step 2 — Update & upgrade paket**

```bash
pkg update && pkg upgrade -y
```

**Step 3 — Install dependensi sistem**

```bash
pkg install python git -y
```

**Step 4 — Install paket tambahan (diperlukan untuk kompilasi library Python)**

```bash
pkg install libjpeg-turbo libffi openssl -y
```

> ℹ️ `libjpeg-turbo` dibutuhkan oleh **Pillow** (untuk QR Code), `libffi` & `openssl` dibutuhkan oleh beberapa dependensi.

**Step 5 — Clone repository**

```bash
git clone https://github.com/Xvoid-glitch/Assistant-CLI-Manajemen.git
cd "Assistant cli"
```

**Step 6 — Buat virtual environment**

```bash
python -m venv venv
source venv/bin/activate
```

**Step 7 — Install dependensi Python**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Step 8 — Jalankan R Assist! 🎉**

```bash
python rizz_assistant.py
```

> **💡 Tips Termux:**
> - Kalau mau jalankan lagi nanti, jangan lupa aktifkan venv dulu:
>   ```bash
>   cd "Assistant cli"
>   source venv/bin/activate
>   python rizz_assistant.py
>   ```
> - Untuk akses penyimpanan internal: `termux-setup-storage`
> - Jika ada error saat install `psutil`, jalankan: `pkg install python-dev clang -y`

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
