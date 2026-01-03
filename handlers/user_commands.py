"""Pengendali perintah pengguna"""
import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_USER_ID
from database_mysql import Database
from utils.checks import reject_group_command
from utils.messages import (
    get_welcome_message,
    get_about_message,
    get_help_message,
)

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /start"""
    if await reject_group_command(update):
        return

    user = update.effective_user
    user_id = user.id
    username = user.username or ""
    full_name = user.full_name or ""

    # Jika sudah terdaftar, langsung kembalikan
    if db.user_exists(user_id):
        await update.message.reply_text(
            f"Selamat datang kembali, {full_name}!\n"
            "Anda sudah terdaftar sebelumnya.\n"
            "Kirim /help untuk melihat perintah yang tersedia."
        )
        return

    # Undangan
    invited_by: Optional[int] = None
    if context.args:
        try:
            invited_by = int(context.args[0])
            if not db.user_exists(invited_by):
                invited_by = None
        except Exception:
            invited_by = None

    # Buat pengguna
    if db.create_user(user_id, username, full_name, invited_by):
        welcome_msg = get_welcome_message(full_name, bool(invited_by))
        await update.message.reply_text(welcome_msg)
    else:
        await update.message.reply_text("Registrasi gagal, silakan coba lagi nanti.")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /about"""
    if await reject_group_command(update):
        return

    await update.message.reply_text(get_about_message())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /help"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id
    is_admin = user_id == ADMIN_USER_ID
    await update.message.reply_text(get_help_message(is_admin))


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /balance"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir dan tidak dapat menggunakan fitur ini.")
        return

    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("Silakan gunakan /start terlebih dahulu untuk mendaftar.")
        return

    await update.message.reply_text(
        f"💰 Saldo poin\n\nPoin saat ini: {user['balance']}"
    )


async def checkin_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /qd (check-in) - sementara dinonaktifkan"""
    user_id = update.effective_user.id

    # Fitur check-in sementara dinonaktifkan (sedang perbaikan bug)
    # await update.message.reply_text(
    #     "⚠️ Fitur check-in sedang maintenance\n\n"
    #     "Ditemukan bug, fitur check-in sementara ditutup dan sedang diperbaiki.\n"
    #     "Akan dipulihkan segera, mohon maaf atas ketidaknyamanannya.\n\n"
    #     "💡 Anda bisa mendapatkan poin dengan cara berikut:\n"
    #     "• Undang teman /invite (+2 poin)\n"
    #     "• Gunakan kode /use <kode>"
    # )
    # return
    
    # ===== Kode di bawah ini dinonaktifkan =====
    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir dan tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start terlebih dahulu untuk mendaftar.")
        return

    # Pemeriksaan tahap 1: di level handler
    if not db.can_checkin(user_id):
        await update.message.reply_text("❌ Anda sudah check-in hari ini, coba lagi besok.")
        return

    # Pemeriksaan tahap 2: di level database (operasi SQL atomik)
    if db.checkin(user_id):
        user = db.get_user(user_id)
        await update.message.reply_text(
            f"✅ Check-in berhasil!\nPoin didapat: +1\nPoin saat ini: {user['balance']}"
        )
    else:
        # Jika database mengembalikan False, berarti sudah check-in hari ini
        await update.message.reply_text("❌ Anda sudah check-in hari ini, coba lagi besok.")


async def invite_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /invite"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir dan tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start terlebih dahulu untuk mendaftar.")
        return

    bot_username = context.bot.username
    invite_link = f"https://t.me/{bot_username}?start={user_id}"

    await update.message.reply_text(
        f"🎁 Tautan undangan Anda:\n{invite_link}\n\n"
        "Setiap 1 teman yang berhasil mendaftar, Anda akan mendapat 2 poin."
    )


async def use_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /use - gunakan kode"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir dan tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start terlebih dahulu untuk mendaftar.")
        return

    if not context.args:
        await update.message.reply_text(
            "Cara penggunaan: /use <kode>\n\nContoh: /use wandouyu"
        )
        return

    key_code = context.args[0].strip()
    result = db.use_card_key(key_code, user_id)

    if result is None:
        await update.message.reply_text("Kode tidak ditemukan, silakan periksa dan coba lagi.")
    elif result == -1:
        await update.message.reply_text("Kode ini sudah mencapai batas penggunaan.")
    elif result == -2:
        await update.message.reply_text("Kode ini sudah kedaluwarsa.")
    elif result == -3:
        await update.message.reply_text("Anda sudah menggunakan kode ini.")
    else:
        user = db.get_user(user_id)
        await update.message.reply_text(
            f"Kode berhasil digunakan!\nPoin didapat: {result}\nPoin saat ini: {user['balance']}"
        )
