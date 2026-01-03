"""Pengendali perintah admin"""
import asyncio
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_USER_ID
from database_mysql import Database
from utils.checks import reject_group_command

logger = logging.getLogger(__name__)


async def addbalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /addbalance - admin menambah poin"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Cara penggunaan: /addbalance <user_id> <jumlah_poin>\n\nContoh: /addbalance 123456789 10"
        )
        return

    try:
        target_user_id = int(context.args[0])
        amount = int(context.args[1])

        if not db.user_exists(target_user_id):
            await update.message.reply_text("Pengguna tidak ditemukan.")
            return

        if db.add_balance(target_user_id, amount):
            user = db.get_user(target_user_id)
            await update.message.reply_text(
                f"✅ Berhasil menambah {amount} poin untuk pengguna {target_user_id}.\n"
                f"Poin saat ini: {user['balance']}"
            )
        else:
            await update.message.reply_text("Operasi gagal, silakan coba lagi nanti.")
    except ValueError:
        await update.message.reply_text("Format parameter salah, silakan masukkan angka yang valid.")


async def block_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /block - admin memblokir pengguna"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    if not context.args:
        await update.message.reply_text(
            "Cara penggunaan: /block <user_id>\n\nContoh: /block 123456789"
        )
        return

    try:
        target_user_id = int(context.args[0])

        if not db.user_exists(target_user_id):
            await update.message.reply_text("Pengguna tidak ditemukan.")
            return

        if db.block_user(target_user_id):
            await update.message.reply_text(f"✅ Pengguna {target_user_id} telah diblokir.")
        else:
            await update.message.reply_text("Operasi gagal, silakan coba lagi nanti.")
    except ValueError:
        await update.message.reply_text("Format parameter salah, silakan masukkan user_id yang valid.")


async def white_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /white - admin membuka blokir"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    if not context.args:
        await update.message.reply_text(
            "Cara penggunaan: /white <user_id>\n\nContoh: /white 123456789"
        )
        return

    try:
        target_user_id = int(context.args[0])

        if not db.user_exists(target_user_id):
            await update.message.reply_text("Pengguna tidak ditemukan.")
            return

        if db.unblock_user(target_user_id):
            await update.message.reply_text(f"✅ Pengguna {target_user_id} telah dikeluarkan dari daftar blokir.")
        else:
            await update.message.reply_text("Operasi gagal, silakan coba lagi nanti.")
    except ValueError:
        await update.message.reply_text("Format parameter salah, silakan masukkan user_id yang valid.")


async def blacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /blacklist - melihat daftar blokir"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    blacklist = db.get_blacklist()

    if not blacklist:
        await update.message.reply_text("Daftar blokir kosong.")
        return

    msg = "📋 Daftar blokir:\n\n"
    for user in blacklist:
        msg += f"User ID: {user['user_id']}\n"
        msg += f"Username: @{user['username']}\n"
        msg += f"Nama: {user['full_name']}\n"
        msg += "---\n"

    await update.message.reply_text(msg)


async def genkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /genkey - admin membuat kode"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Cara penggunaan: /genkey <kode> <poin> [jumlah_penggunaan] [hari_kedaluwarsa]\n\n"
            "Contoh:\n"
            "/genkey wandouyu 20 - buat kode 20 poin (sekali pakai, tidak kedaluwarsa)\n"
            "/genkey vip100 50 10 - buat kode 50 poin (bisa dipakai 10x, tidak kedaluwarsa)\n"
            "/genkey temp 30 1 7 - buat kode 30 poin (sekali pakai, kedaluwarsa 7 hari)"
        )
        return

    try:
        key_code = context.args[0].strip()
        balance = int(context.args[1])
        max_uses = int(context.args[2]) if len(context.args) > 2 else 1
        expire_days = int(context.args[3]) if len(context.args) > 3 else None

        if balance <= 0:
            await update.message.reply_text("Jumlah poin harus lebih dari 0.")
            return

        if max_uses <= 0:
            await update.message.reply_text("Jumlah penggunaan harus lebih dari 0.")
            return

        if db.create_card_key(key_code, balance, user_id, max_uses, expire_days):
            msg = (
                "✅ Kode berhasil dibuat!\n\n"
                f"Kode: {key_code}\n"
                f"Poin: {balance}\n"
                f"Jumlah penggunaan: {max_uses}x\n"
            )
            if expire_days:
                msg += f"Berlaku: {expire_days} hari\n"
            else:
                msg += "Berlaku: permanen\n"
            msg += f"\nCara penggunaan untuk user: /use {key_code}"
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("Kode sudah ada atau gagal dibuat, silakan gunakan nama kode lain.")
    except ValueError:
        await update.message.reply_text("Format parameter salah, silakan masukkan angka yang valid.")


async def listkeys_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /listkeys - admin melihat daftar kode"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    keys = db.get_all_card_keys()

    if not keys:
        await update.message.reply_text("Belum ada kode.")
        return

    msg = "📋 Daftar kode:\n\n"
    for key in keys[:20]:  # hanya tampilkan 20 teratas
        msg += f"Kode: {key['key_code']}\n"
        msg += f"Poin: {key['balance']}\n"
        msg += f"Jumlah penggunaan: {key['current_uses']}/{key['max_uses']}\n"

        if key["expire_at"]:
            expire_time = datetime.fromisoformat(key["expire_at"])
            if datetime.now() > expire_time:
                msg += "Status: kedaluwarsa\n"
            else:
                days_left = (expire_time - datetime.now()).days
                msg += f"Status: aktif (sisa {days_left} hari)\n"
        else:
            msg += "Status: aktif permanen\n"

        msg += "---\n"

    if len(keys) > 20:
        msg += f"\n(Hanya menampilkan 20 teratas, total {len(keys)} kode)"

    await update.message.reply_text(msg)


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /broadcast - admin mengirim pesan massal"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    text = " ".join(context.args).strip() if context.args else ""
    if not text and update.message.reply_to_message:
        text = update.message.reply_to_message.text or ""

    if not text:
        await update.message.reply_text("Cara penggunaan: /broadcast <teks>, atau balas pesan lalu kirim /broadcast")
        return

    user_ids = db.get_all_user_ids()
    success, failed = 0, 0

    status_msg = await update.message.reply_text(f"📢 Mulai broadcast, total {len(user_ids)} pengguna...")

    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=text)
            success += 1
            await asyncio.sleep(0.05)  # batasi agar tidak terkena limit
        except Exception as e:
            logger.warning("Broadcast ke %s gagal: %s", uid, e)
            failed += 1

    await status_msg.edit_text(f"✅ Broadcast selesai!\nBerhasil: {success}\nGagal: {failed}")
