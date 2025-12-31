# Panduan Deployment Bot Verifikasi SheerID

Dokumen ini menjelaskan cara deploy bot verifikasi SheerID di server Anda.

## 📋 Daftar Isi

1. [Persyaratan lingkungan](#persyaratan-lingkungan)
2. [Deploy cepat](#deploy-cepat)
3. [Deploy Docker](#deploy-docker)
4. [Deploy manual](#deploy-manual)
5. [Konfigurasi](#konfigurasi)
6. [FAQ](#faq)
7. [Maintenance & update](#maintenance--update)

---

## 🔧 Persyaratan lingkungan

### Minimum

- **OS**: Linux (Ubuntu 20.04+ disarankan) / Windows 10+ / macOS 10.15+
- **Python**: 3.11+
- **MySQL**: 5.7+
- **RAM**: 512MB (disarankan 1GB+)
- **Storage**: 2GB+
- **Network**: koneksi internet stabil

### Rekomendasi

- **OS**: Ubuntu 22.04 LTS
- **RAM**: 2GB+
- **Storage**: 5GB+
- **Bandwidth**: 10Mbps+

---

## 🚀 Deploy cepat

### Gunakan Docker Compose (paling mudah)

```bash
# 1. Clone repo
git clone https://github.com/PastKing/tgbot-verify.git
cd tgbot-verify

# 2. Konfigurasi env
cp env.example .env
nano .env

# 3. Jalankan service
docker compose up -d

# 4. Lihat log
docker compose logs -f

# 5. Stop service
docker compose down
```

Selesai! Bot seharusnya sudah berjalan.

---

## 🐳 Deploy Docker

### Metode 1: Docker Compose (disarankan)

#### 1. Siapkan konfigurasi

Buat file `.env`:

```ini
# Konfigurasi bot Telegram
BOT_TOKEN=xxx
ADMIN_USER_ID=xxx
CHANNEL_USERNAME=xxx
CHANNEL_URL=xxx

# Konfigurasi database MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=tgbot_user
MYSQL_PASSWORD=xxx
MYSQL_DATABASE=tgbot_verify
```

#### 2. Jalankan service

```bash
docker compose up -d
```

#### 3. Cek status

```bash
# Cek status container
docker compose ps

# Lihat log realtime
docker compose logs -f

# Lihat 50 baris terakhir log
docker compose logs --tail=50
```

#### 4. Restart service

```bash
# Restart semua service
docker compose restart

# Restart service tertentu
docker compose restart tgbot
```

#### 5. Update kode

```bash
# Tarik update terbaru
git pull

# Rebuild dan jalankan ulang
docker compose up -d --build
```

### Metode 2: Docker manual

```bash
# 1. Build image
docker build -t sheerid-tgbot .

# 2. Jalankan container
docker run -d --name sheerid-tgbot --env-file .env sheerid-tgbot

# 3. Lihat log
docker logs -f sheerid-tgbot

# 4. Stop container
docker stop sheerid-tgbot

# 5. Hapus container
docker rm sheerid-tgbot
```

---

## 🔨 Deploy manual

### 1. Install dependency

```bash
pip install -r requirements.txt
```

### 2. Buat virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Konfigurasi database

```bash
# Masuk ke MySQL
mysql -u root -p

# Buat database dan user
CREATE DATABASE tgbot_verify;
CREATE USER 'tgbot_user'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON tgbot_verify.* TO 'tgbot_user'@'%';
FLUSH PRIVILEGES;
```

### 4. Konfigurasi environment

```bash
cp env.example .env
nano .env
```

### 5. Jalankan bot

```bash
# Jalankan di foreground (tes)
python bot.py

# Jalankan di background (nohup)
nohup python bot.py > logs/bot.log 2>&1 &
```

---

## ⚙️ Konfigurasi

### Detail environment variable

#### Telegram

```ini
BOT_TOKEN=xxx          # wajib, dari @BotFather
CHANNEL_USERNAME=pk_oa  # opsional, tanpa @
CHANNEL_URL=https://t.me/pk_oa
ADMIN_USER_ID=123456789
```

#### MySQL

```ini
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=tgbot_user
MYSQL_PASSWORD=xxx
MYSQL_DATABASE=tgbot_verify
```

### Konfigurasi poin

Edit di `config.py`:

```python
VERIFY_COST = 1
CHECKIN_REWARD = 1
INVITE_REWARD = 2
REGISTER_REWARD = 1
```

### Kontrol konkruensi

Edit di `utils/concurrency.py`:

```python
# dihitung otomatis dari resource sistem
```

---

## 🔍 FAQ

### 1. Bot Token tidak valid

**Masalah**: `telegram.error.InvalidToken: The token was rejected by the server.`

**Solusi**:
- Pastikan `BOT_TOKEN` di `.env` benar
- Tidak ada spasi ekstra atau tanda kutip
- Ambil token baru dari @BotFather

### 2. Gagal koneksi database

**Masalah**: `pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")`

**Solusi**:
- Pastikan service MySQL berjalan
- Periksa konfigurasi DB
- Pastikan firewall tidak memblokir
- Cek izin user database

### 3. Playwright gagal install browser

**Masalah**: `playwright._impl._api_types.Error: Executable doesn't exist`

**Solusi**:
```bash
playwright install chromium
```

### 4. Port bentrok

**Masalah**: Container gagal start karena port conflict

**Solusi**:
- Cek port yang digunakan
- Update mapping port di `docker-compose.yml`

### 5. RAM tidak cukup

**Masalah**: Server crash karena RAM kurang

**Solusi**:
- Tambah RAM
- Kurangi konkruensi
- Aktifkan swap

### 6. Log terlalu besar

**Masalah**: Log memenuhi disk

**Solusi**:
- Batasi ukuran log via Docker
- Bersihkan manual: `truncate -s 0 logs/*.log`
- Aktifkan log rotation

---

## 🔄 Maintenance & update

### Cek log

```bash
# Docker
docker compose logs -f

# Manual
 tail -f logs/bot.log
```

### Backup database

```bash
# Backup penuh
mysqldump -u root -p tgbot_verify > backup.sql

# Restore
mysql -u root -p tgbot_verify < backup.sql
```

### Update kode

```bash
# Tarik update
git pull

# Docker
docker compose up -d --build

# Manual
pip install -r requirements.txt
```

### Monitoring service

#### systemd (Linux)

Buat file `/etc/systemd/system/tgbot-verify.service`:

```ini
[Unit]
Description=SheerID Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/tgbot-verify
ExecStart=/path/to/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Aktifkan:

```bash
sudo systemctl daemon-reload
sudo systemctl enable tgbot-verify
sudo systemctl start tgbot-verify
```

---

## 🔒 Keamanan

1. **Gunakan password kuat**
   - Token bot diganti berkala
   - Password DB minimal 16 karakter
   - Hindari password default
2. **Batasi akses database**
   - Izinkan koneksi lokal saja jika memungkinkan
   - Batasi IP yang diizinkan
3. **Konfigurasi firewall**
   - Buka port yang diperlukan saja
4. **Update berkala**
5. **Backup rutin**
   - Backup harian
   - Simpan minimal 7 hari
   - Tes restore secara berkala

---

## 📞 Dukungan

- 📺 Telegram channel: https://t.me/pk_oa
- 🐛 Issue tracker: [GitHub Issues](https://github.com/PastKing/tgbot-verify/issues)

---

<strong>Semoga deployment Anda lancar!</strong>
