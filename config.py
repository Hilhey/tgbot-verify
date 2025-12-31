"""Konfigurasi global"""
import os
from dotenv import load_dotenv

# Memuat file .env
load_dotenv()

# Konfigurasi bot Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "pk_oa")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/pk_oa")

# Konfigurasi admin
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "123456789"))

# Konfigurasi poin
VERIFY_COST = 1  # biaya poin untuk verifikasi
CHECKIN_REWARD = 1  # reward check-in
INVITE_REWARD = 2  # reward undangan
REGISTER_REWARD = 1  # reward registrasi

# Tautan bantuan
HELP_NOTION_URL = "https://rhetorical-era-3f3.notion.site/dd78531dbac745af9bbac156b51da9cc"
