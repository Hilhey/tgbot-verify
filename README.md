# Bot Telegram Verifikasi Otomatis SheerID

> 🤖 Bot Telegram untuk menyelesaikan verifikasi SheerID siswa/guru secara otomatis
> 
> Dikembangkan dari [@auto_sheerid_bot](https://t.me/auto_sheerid_bot) (kode lama GGBond)

## 📋 Ringkasan Proyek

Bot Telegram berbasis Python ini dapat menyelesaikan verifikasi SheerID untuk berbagai platform. Bot akan menghasilkan identitas, membuat dokumen verifikasi, lalu mengirimkannya ke platform SheerID sehingga proses lebih cepat.

### 🎯 Layanan yang Didukung

| Perintah | Layanan | Tipe | Status | Deskripsi |
|------|------|------|------|------|
| `/verify` | Gemini One Pro | Verifikasi guru | ✅ Lengkap | Google AI Studio Education Discount |
| `/verify2` | ChatGPT Teacher K12 | Verifikasi guru | ✅ Lengkap | OpenAI ChatGPT Education Discount |
| `/verify3` | Spotify Student | Verifikasi siswa | ✅ Lengkap | Spotify Student Subscription Discount |
| `/verify4` | Bolt.new Teacher | Verifikasi guru | ✅ Lengkap | Bolt.new Education Discount (auto ambil code) |
| `/verify5` | YouTube Premium Student | Verifikasi siswa | ⚠️ Beta | YouTube Premium Student Discount (lihat catatan) |
| `/verify6` | ChatGPT Military | Verifikasi militer | ✅ Lengkap | ChatGPT Military Discount |

> **⚠️ Catatan khusus YouTube**:
> 
> Fitur verifikasi YouTube saat ini masih beta. Baca dulu [`youtube/HELP.MD`](youtube/HELP.MD).
> 
> **Perbedaan utama**:
> - Format link YouTube berbeda dengan layanan lain
> - Harus mengambil `programId` dan `verificationId` dari log network browser
> - Lalu menyusun link SheerID secara manual
> 
> **Langkah penggunaan**:
> 1. Buka halaman verifikasi YouTube Premium Student
> 2. Buka DevTools (F12) → tab Network
> 3. Mulai proses verifikasi, cari `https://services.sheerid.com/rest/v2/verification/`
> 4. Ambil `programId` dari payload request dan `verificationId` dari response
> 5. Susun link: `https://services.sheerid.com/verify/{programId}/?verificationId={verificationId}`
> 6. Kirim link menggunakan `/verify5` atau `/verify6`

### ✨ Fitur Utama

- 🚀 **Otomatisasi penuh**: sekali klik untuk generate data, buat dokumen, dan submit verifikasi
- 🎨 **Generate dokumen**: otomatis membuat PNG kartu siswa/guru
- 💰 **Sistem poin**: check-in, undangan, dan kode
- 🔐 **Aman & stabil**: database MySQL dengan konfigurasi via env
- ⚡ **Kontrol konkruensi**: mengatur concurrent request agar stabil
- 👥 **Fitur admin**: manajemen pengguna dan poin

---

## 🛠️ Tech Stack

- **Bahasa**: Python 3.11+
- **Framework Bot**: python-telegram-bot 20.0+
- **Database**: MySQL 5.7+
- **Browser automation**: Playwright
- **HTTP client**: httpx
- **Pengolahan gambar**: Pillow, reportlab, xhtml2pdf
- **Env management**: python-dotenv

---

## 🚀 Mulai Cepat

### 1. Clone repositori

```bash
git clone https://github.com/PastKing/tgbot-verify.git
cd tgbot-verify
```

### 2. Install dependency

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi environment

Salin `env.example` menjadi `.env` lalu isi:

```ini
# Telegram Bot config
BOT_TOKEN=xxx
ADMIN_USER_ID=xxx
CHANNEL_USERNAME=xxx
CHANNEL_URL=xxx

# MySQL database config
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=xxx
MYSQL_DATABASE=tgbot_verify
```

### 4. Jalankan bot

```bash
python bot.py
```

---

## 🐳 Deployment Docker

### Menggunakan Docker Compose (disarankan)

```bash
# 1. Update file .env
# 2. Jalankan service
# 3. Lihat log
```

### Manual Docker

```bash
# Build image
# Jalankan container
```

---

## 📖 Panduan Penggunaan

### Perintah pengguna

```bash
/start              # Mulai (registrasi)
/about              # Info bot
/balance            # Cek saldo poin
/qd                 # Check-in harian (+1 poin)
/invite             # Undang teman (+2 poin/orang)
/use <kode>         # Tukar poin dengan kode
/verify <tautan>      # Gemini One Pro
/verify2 <tautan>     # ChatGPT Teacher K12
/verify3 <tautan>     # Spotify Student
/verify4 <tautan>     # Bolt.new Teacher
/verify5 <tautan>     # YouTube Premium Student
/verify6 <tautan> <email>  # ChatGPT Military
/getV4Code <id>     # Ambil kode verifikasi Bolt.new
/help               # Bantuan
```

### Perintah admin

```bash
/addbalance <user_id> <poin>     # Tambah poin pengguna
/block <user_id>                 # Blokir pengguna
/white <user_id>                 # Buka blokir
/blacklist                       # Lihat daftar blokir
/genkey <kode> <poin> [jumlah] [hari]  # Buat kode
/listkeys                        # Lihat daftar kode
/broadcast <teks>               # Broadcast pesan
```

### Alur penggunaan

1. **Ambil link verifikasi**
   - Buka halaman verifikasi layanan
   - Mulai proses verifikasi
   - Salin URL lengkap (termasuk `verificationId`)
2. **Kirim permintaan verifikasi**
   - Kirim perintah `/verify*` sesuai layanan
3. **Tunggu proses**
   - Bot otomatis membuat identitas
   - Membuat dokumen verifikasi
   - Mengirim ke SheerID
4. **Terima hasil**
   - Review biasanya beberapa menit
   - Jika sukses, akan ada link redirect

---

## 📁 Struktur Proyek

```
.
├── bot.py                  # Program utama bot
├── config.py               # Konfigurasi global
├── database_mysql.py       # Manajemen database MySQL
├── .env                    # Konfigurasi env (buat sendiri)
├── env.example             # Template env
├── requirements.txt        # Dependency Python
├── Dockerfile              # Build image Docker
├── docker-compose.yml      # Docker Compose config
├── handlers/               # Handler perintah
│   ├── user_commands.py    # Perintah user
│   ├── admin_commands.py   # Perintah admin
│   └── verify_commands.py  # Perintah verifikasi
├── one/                    # Modul Gemini One Pro
├── k12/                    # Modul ChatGPT K12
├── spotify/                # Modul Spotify Student
├── youtube/                # Modul YouTube Premium
├── Boltnew/                # Modul Bolt.new
└── utils/                  # Utilitas
    ├── messages.py         # Template pesan
    ├── concurrency.py      # Kontrol konkruensi
    └── checks.py           # Pengecekan izin
```

---

## ⚙️ Konfigurasi

### Environment variable

| Nama | Wajib | Keterangan | Default |
|---|---|---|---|
| `CHANNEL_USERNAME` | ❌ | Username channel | pk_oa |
| `CHANNEL_URL` | ❌ | Link channel | https://t.me/pk_oa |
| `ADMIN_USER_ID` | ✅ | Telegram ID admin | - |
| `MYSQL_HOST` | ✅ | Host MySQL | localhost |
| `MYSQL_PORT` | ❌ | Port MySQL | 3306 |
| `MYSQL_USER` | ✅ | Username MySQL | - |
| `MYSQL_PASSWORD` | ✅ | Password MySQL | - |
| `MYSQL_DATABASE` | ✅ | Nama database | tgbot_verify |

### Konfigurasi poin

Atur di `config.py`:

```python
VERIFY_COST = 1        # biaya verifikasi
CHECKIN_REWARD = 1     # reward check-in
INVITE_REWARD = 2      # reward undangan
REGISTER_REWARD = 1    # reward registrasi
```

---

## ⚠️ Penting

### 🔴 Wajib dibaca sebelum digunakan

**Sebelum menggunakan bot, pastikan konfigurasi verifikasi pada setiap modul sudah benar!**

`programId` dari SheerID dapat berubah, jadi cek ulang file konfigurasi:

- `one/config.py` - Gemini One Pro
- `k12/config.py` - ChatGPT Teacher K12
- `spotify/config.py` - Spotify Student
- `youtube/config.py` - YouTube Premium Student
- `Boltnew/config.py` - Bolt.new Teacher

**Cara mendapatkan programId terbaru**:

1. Buka halaman verifikasi layanan
2. Buka DevTools (F12) → tab Network
3. Mulai proses verifikasi
4. Cari request `https://services.sheerid.com/rest/v2/verification/`
5. Ambil `programId` dari URL atau payload
6. Update `config.py` masing-masing modul

> **Tips**: Jika verifikasi terus gagal, kemungkinan `programId` sudah kadaluarsa.

---

## 🔗 Link terkait

- 📺 **Telegram channel**: https://t.me/pk_oa
- 🐛 **Issue tracker**: [GitHub Issues](https://github.com/PastKing/tgbot-verify/issues)
- 📖 **Dokumen deployment**: [DEPLOY.md](DEPLOY.md)

---

## 🤝 Kontribusi

Silakan lakukan pengembangan lanjutan dengan ketentuan berikut:

1. **Tetap cantumkan author asli**
   - Sertakan link repositori asli
   - Tulis bahwa proyek ini adalah turunan
2. **Lisensi open source**
   - Proyek ini menggunakan MIT License
   - Proyek turunan juga harus open source
3. **Penggunaan komersial**
   - Bebas digunakan pribadi
   - Untuk komersial silakan optimasi sendiri
   - Tidak ada dukungan teknis/garansi

---

## 📜 Lisensi

Proyek ini menggunakan [MIT License](LICENSE).

---

## 🙏 Terima kasih

- Terima kasih kepada [@auto_sheerid_bot](https://t.me/auto_sheerid_bot) GGBond untuk dasar kode
- Terima kasih kepada semua kontributor
- Terima kasih kepada SheerID yang menyediakan layanan verifikasi

---

## 📝 Changelog

- ✨ Penambahan Spotify Student dan YouTube Premium Student (YouTube masih beta, lihat youtube/HELP.MD)
- 🚀 Optimasi konkruensi dan performa
- 📝 Pembaruan dokumentasi dan deployment
- 🐛 Perbaikan bug
- 🎉 Rilis awal
- ✅ Dukungan Gemini, ChatGPT, Bolt.new

---

<strong>⭐ Jika proyek ini membantu, tolong beri bintang!</strong>
