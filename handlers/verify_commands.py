"""Pengendali perintah verifikasi"""
import asyncio
import logging
import httpx
import time
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes
from utils.checks import reject_group_command

from config import VERIFY_COST
from database_mysql import Database
from one.sheerid_verifier import SheerIDVerifier as OneVerifier
from k12.sheerid_verifier import SheerIDVerifier as K12Verifier
from spotify.sheerid_verifier import SheerIDVerifier as SpotifyVerifier
from youtube.sheerid_verifier import SheerIDVerifier as YouTubeVerifier
from Boltnew.sheerid_verifier import SheerIDVerifier as BoltnewVerifier
from military.sheerid_verifier import SheerIDVerifier as MilitaryVerifier
from utils.messages import get_insufficient_balance_message, get_verify_usage_message
from utils.http_client import create_async_client

# Coba impor kontrol konkruensi, jika gagal gunakan implementasi sederhana
try:
    from utils.concurrency import get_verification_semaphore
except ImportError:
    # Jika impor gagal, gunakan implementasi sederhana
    def get_verification_semaphore(verification_type: str):
        return asyncio.Semaphore(3)

logger = logging.getLogger(__name__)


def _normalize_proxy(raw_proxy: Optional[str]) -> Optional[str]:
    if not raw_proxy:
        return None
    proxy = raw_proxy.strip()
    if proxy.lower() in {"skip", "none", "-"}:
        return None
    if "://" not in proxy:
        proxy = f"http://{proxy}"
    return proxy


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /verify - Gemini One Pro"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir dan tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start terlebih dahulu untuk mendaftar.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify", "Gemini One Pro")
        )
        return

    url = context.args[0]
    proxy = _normalize_proxy(context.args[1]) if len(context.args) > 1 else None
    proxy = context.args[1] if len(context.args) > 1 else None
    proxy = context.args[1] if len(context.args) > 1 else None
    proxy = context.args[1] if len(context.args) > 1 else None
    proxy = context.args[1] if len(context.args) > 1 else None
    proxy = context.args[1] if len(context.args) > 1 else None
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = OneVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Tautan SheerID tidak valid, silakan periksa dan coba lagi.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Gagal memotong poin, silakan coba lagi nanti.")
        return

    processing_msg = await update.message.reply_text(
        f"Mulai memproses verifikasi Gemini One Pro...\n"
        f"ID Verifikasi: {verification_id}\n"
        f"{VERIFY_COST} poin telah dipotong\n\n"
        "Mohon tunggu, proses ini bisa memakan waktu 1-2 menit..."
    )

    try:
        verifier = OneVerifier(verification_id, proxy=proxy)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "gemini_one_pro",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Verifikasi berhasil - verificattion succesfull!\n\n"
            if result.get("pending"):
                result_msg += "Dokumen sudah dikirim, menunggu peninjauan manual.\n"
            if result.get("redirect_url"):
                result_msg += f"Tautan lanjut:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verifikasi gagal: {result.get('message', 'Kesalahan tidak diketahui')}\n\n"
                f"{VERIFY_COST} poin telah dikembalikan"
            )
    except Exception as e:
        logger.error("Terjadi kesalahan saat verifikasi: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan saat proses: {str(e)}\n\n"
            f"{VERIFY_COST} poin telah dikembalikan"
        )


async def verify2_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /verify2 - ChatGPT Teacher K12"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir dan tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start terlebih dahulu untuk mendaftar.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify2", "ChatGPT Teacher K12")
        )
        return

    url = context.args[0]
    proxy = _normalize_proxy(context.args[1]) if len(context.args) > 1 else None
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = K12Verifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Tautan SheerID tidak valid, silakan periksa dan coba lagi.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Gagal memotong poin, silakan coba lagi nanti.")
        return

    processing_msg = await update.message.reply_text(
        f"Mulai memproses verifikasi ChatGPT Teacher K12...\n"
        f"ID Verifikasi: {verification_id}\n"
        f"{VERIFY_COST} poin telah dipotong\n\n"
        "Mohon tunggu, proses ini bisa memakan waktu 1-2 menit..."
    )

    try:
        verifier = K12Verifier(verification_id, proxy=proxy)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "chatgpt_teacher_k12",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Verifikasi berhasil - verificattion succesfull!\n\n"
            if result.get("pending"):
                result_msg += "Dokumen sudah dikirim, menunggu peninjauan manual.\n"
            if result.get("redirect_url"):
                result_msg += f"Tautan lanjut:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verifikasi gagal: {result.get('message', 'Kesalahan tidak diketahui')}\n\n"
                f"{VERIFY_COST} poin telah dikembalikan"
            )
    except Exception as e:
        logger.error("Terjadi kesalahan saat verifikasi: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan saat proses: {str(e)}\n\n"
            f"{VERIFY_COST} poin telah dikembalikan"
        )


async def verify3_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /verify3 - Spotify Student"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir dan tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start terlebih dahulu untuk mendaftar.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify3", "Spotify Student")
        )
        return

    url = context.args[0]
    proxy = _normalize_proxy(context.args[1]) if len(context.args) > 1 else None
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # Parse verificationId
    verification_id = SpotifyVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Tautan SheerID tidak valid, silakan periksa dan coba lagi.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Gagal memotong poin, silakan coba lagi nanti.")
        return

    processing_msg = await update.message.reply_text(
        f"🎵 Mulai memproses verifikasi Spotify Student...\n"
        f"{VERIFY_COST} poin telah dipotong\n\n"
        "📝 Sedang menyiapkan data siswa...\n"
        "🎨 Sedang membuat PNG kartu siswa...\n"
        "📤 Sedang mengirim dokumen..."
    )

    # Gunakan semaphore untuk kontrol konkruensi
    semaphore = get_verification_semaphore("spotify_student")

    try:
        async with semaphore:
            verifier = SpotifyVerifier(verification_id, proxy=proxy)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "spotify_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Verifikasi Spotify Student berhasil - verificattion succesfull!\n\n"
            if result.get("pending"):
                result_msg += "✨ Dokumen sudah dikirim, menunggu peninjauan SheerID\n"
                result_msg += "⏱️ Estimasi waktu peninjauan: beberapa menit\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 Tautan lanjut:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verifikasi gagal: {result.get('message', 'Kesalahan tidak diketahui')}\n\n"
                f"{VERIFY_COST} poin telah dikembalikan"
            )
    except Exception as e:
        logger.error("Terjadi kesalahan saat verifikasi Spotify: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan saat proses: {str(e)}\n\n"
            f"{VERIFY_COST} poin telah dikembalikan"
        )


async def verify4_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /verify4 - Bolt.new Teacher (ambil kode otomatis)"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir dan tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start terlebih dahulu untuk mendaftar.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify4", "Bolt.new Teacher")
        )
        return

    url = context.args[0]
    proxy = _normalize_proxy(context.args[1]) if len(context.args) > 1 else None
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # Parse externalUserId atau verificationId
    external_user_id = BoltnewVerifier.parse_external_user_id(url)
    verification_id = BoltnewVerifier.parse_verification_id(url)

    if not external_user_id and not verification_id:
        await update.message.reply_text("Tautan SheerID tidak valid, silakan periksa dan coba lagi.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Gagal memotong poin, silakan coba lagi nanti.")
        return

    processing_msg = await update.message.reply_text(
        f"🚀 Mulai memproses verifikasi Bolt.new Teacher...\n"
        f"{VERIFY_COST} poin telah dipotong\n\n"
        "📤 Sedang mengirim dokumen..."
    )

    # Gunakan semaphore untuk kontrol konkruensi
    semaphore = get_verification_semaphore("bolt_teacher")

    try:
        async with semaphore:
            # Langkah 1: kirim dokumen
            verifier = BoltnewVerifier(url, verification_id=verification_id, proxy=proxy)
            result = await asyncio.to_thread(verifier.verify)

        if not result.get("success"):
            # Gagal kirim, kembalikan poin
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Pengiriman dokumen gagal: {result.get('message', 'Kesalahan tidak diketahui')}\n\n"
                f"{VERIFY_COST} poin telah dikembalikan"
            )
            return
        
        vid = result.get("verification_id", "")
        if not vid:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Tidak mendapatkan ID verifikasi\n\n"
                f"{VERIFY_COST} poin telah dikembalikan"
            )
            return
        
        # Perbarui pesan
        await processing_msg.edit_text(
            f"✅ Dokumen sudah dikirim!\n"
            f"📋 ID Verifikasi: `{vid}`\n\n"
            f"🔍 Sedang mengambil kode verifikasi otomatis...\n"
            f"(maksimal menunggu 20 detik)"
        )
        
        # Langkah 2: ambil kode verifikasi otomatis (maks 20 detik)
        code = await _auto_get_reward_code(vid, max_wait=20, interval=5, proxy=proxy)
        
        if code:
            # Berhasil mendapatkan kode
            result_msg = (
                f"🎉 Verifikasi berhasil - verificattion succesfull!\n\n"
                f"✅ Dokumen sudah dikirim\n"
                f"✅ Peninjauan disetujui\n"
                f"✅ Kode verifikasi sudah didapatkan\n\n"
                f"🎁 Kode verifikasi: `{code}`\n"
            )
            if result.get("redirect_url"):
                result_msg += f"\n🔗 Tautan lanjut:\n{result['redirect_url']}"
            
            await processing_msg.edit_text(result_msg)
            
            # Simpan catatan sukses
            db.add_verification(
                user_id,
                "bolt_teacher",
                url,
                "success",
                f"Code: {code}",
                vid
            )
        else:
            # Tidak mendapatkan dalam 20 detik, minta pengguna cek nanti
            await processing_msg.edit_text(
                f"✅ Dokumen berhasil dikirim!\n\n"
                f"⏳ Kode verifikasi belum tersedia (peninjauan bisa 1-5 menit)\n\n"
                f"📋 ID Verifikasi: `{vid}`\n\n"
                f"💡 Silakan cek nanti dengan perintah berikut:\n"
                f"`/getV4Code {vid}`\n\n"
                f"Catatan: poin sudah terpakai, pengecekan nanti tidak dikenakan biaya lagi"
            )
            
            # Simpan catatan pending
            db.add_verification(
                user_id,
                "bolt_teacher",
                url,
                "pending",
                "Waiting for review",
                vid
            )
            
    except Exception as e:
        logger.error("Terjadi kesalahan saat verifikasi Bolt.new: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan saat proses: {str(e)}\n\n"
            f"{VERIFY_COST} poin telah dikembalikan"
        )


async def _auto_get_reward_code(
    verification_id: str,
    max_wait: int = 20,
    interval: int = 5,
    proxy: Optional[str] = None,
) -> Optional[str]:
    """Ambil kode verifikasi otomatis (polling ringan, tidak mengganggu konkruensi)
    
    Args:
        verification_id: ID verifikasi
        max_wait: waktu tunggu maksimal (detik)
        interval: interval polling (detik)
        
    Returns:
        str: kode verifikasi, jika gagal None
    """
    import time
    start_time = time.time()
    attempts = 0
    
    async with create_async_client(timeout=30.0, proxy=proxy) as client:
        while True:
            elapsed = int(time.time() - start_time)
            attempts += 1
            
            # Cek timeout
            if elapsed >= max_wait:
                logger.info(f"Pengambilan kode otomatis timeout ({elapsed} detik), minta pengguna cek manual")
                return None
            
            try:
                # Cek status verifikasi
                response = await client.get(
                    f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    current_step = data.get("currentStep")
                    
                    if current_step == "success":
                        # Ambil kode verifikasi
                        code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
                        if code:
                            logger.info(f"✅ Berhasil mengambil kode otomatis: {code} (durasi {elapsed} detik)")
                            return code
                    elif current_step == "error":
                        # Peninjauan gagal
                        logger.warning(f"Peninjauan gagal: {data.get('errorIds', [])}")
                        return None
                    # else: pending, lanjut tunggu
                
                # Tunggu polling berikutnya
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.warning(f"Gagal mengecek kode verifikasi: {e}")
                await asyncio.sleep(interval)
    
    return None


async def verify5_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /verify5 - YouTube Student Premium"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir dan tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start terlebih dahulu untuk mendaftar.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify5", "YouTube Student Premium")
        )
        return

    url = context.args[0]
    proxy = _normalize_proxy(context.args[1]) if len(context.args) > 1 else None
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # Parse verificationId
    verification_id = YouTubeVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Tautan SheerID tidak valid, silakan periksa dan coba lagi.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Gagal memotong poin, silakan coba lagi nanti.")
        return

    processing_msg = await update.message.reply_text(
        f"📺 Mulai memproses verifikasi YouTube Student Premium...\n"
        f"{VERIFY_COST} poin telah dipotong\n\n"
        "📝 Sedang menyiapkan data siswa...\n"
        "🎨 Sedang membuat PNG kartu siswa...\n"
        "📤 Sedang mengirim dokumen..."
    )

    # Gunakan semaphore untuk kontrol konkruensi
    semaphore = get_verification_semaphore("youtube_student")

    try:
        async with semaphore:
            verifier = YouTubeVerifier(verification_id, proxy=proxy)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "youtube_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Verifikasi YouTube Student Premium berhasil - verificattion succesfull!\n\n"
            if result.get("pending"):
                result_msg += "✨ Dokumen sudah dikirim, menunggu peninjauan SheerID\n"
                result_msg += "⏱️ Estimasi waktu peninjauan: beberapa menit\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 Tautan lanjut:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verifikasi gagal: {result.get('message', 'Kesalahan tidak diketahui')}\n\n"
                f"{VERIFY_COST} poin telah dikembalikan"
            )
    except Exception as e:
        logger.error("Terjadi kesalahan saat verifikasi YouTube: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan saat proses: {str(e)}\n\n"
            f"{VERIFY_COST} poin telah dikembalikan"
        )


async def verify6_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /verify6 - ChatGPT Military"""
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
            "Cara penggunaan: /verify6 <tautan SheerID>\n\n"
            "Contoh:\n"
            "/verify6 https://services.sheerid.com/verify/xxx/?verificationId=xxx\n\n"
            "Cara mendapatkan tautan verifikasi:\n"
            "1. Kunjungi halaman verifikasi ChatGPT Military\n"
            "2. Mulai proses verifikasi\n"
            "3. Salin URL lengkap dari address bar browser\n"
            "4. Kirim dengan perintah /verify6"
        )
        return

    url = context.args[0]
    context.user_data["verify6"] = {"url": url, "stage": "await_email_choice"}
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = MilitaryVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Tautan SheerID tidak valid, silakan periksa dan coba lagi.")
        return
    program_id = MilitaryVerifier.parse_program_id(url)
    if not program_id:
        await update.message.reply_text(
            "Program ID tidak ditemukan di tautan. Pastikan link berformat:\n"
            "https://services.sheerid.com/verify/{programId}/?verificationId=..."
        )
        return

    context.user_data["verify6"].update(
        {"verification_id": verification_id, "program_id": program_id}
    )
    await update.message.reply_text(
        "Pilih metode email untuk verifikasi:\n"
        "1) TempMail otomatis (bot akan handle email)\n"
        "2) Input email manual"
    )


async def verify6_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    if await reject_group_command(update):
        return

    if not update.message or not update.message.text:
        return

    data = context.user_data.get("verify6")
    if not data:
        return

    stage = data.get("stage")
    text = update.message.text.strip()

    if stage == "await_email_choice":
        if text in {"1", "tempmail", "auto", "otomatis"}:
            data["email_mode"] = "tempmail"
            data["stage"] = "await_proxy_choice"
            await update.message.reply_text(
                "✅ Mode TempMail otomatis dipilih. Bot akan handle email verifikasi.\n\n"
                "Pilih penggunaan proxy:\n"
                "1) Tanpa proxy\n"
                "2) Pakai proxy manual"
            )
            return
        if text in {"2", "manual", "email manual"}:
            data["email_mode"] = "manual"
            data["stage"] = "await_email"
            await update.message.reply_text("Silakan input email untuk verifikasi.")
            return
        await update.message.reply_text(
            "Pilihan tidak valid. Balas dengan 1 (TempMail otomatis) atau 2 (email manual)."
        )
        return

    if stage == "await_email":
        if "@" not in text:
            await update.message.reply_text(
                "Format email tidak valid. Silakan input email yang benar."
            )
            return
        data["email"] = text
        data["stage"] = "await_proxy_choice"
        await update.message.reply_text(
            "Pilih penggunaan proxy:\n"
            "1) Tanpa proxy\n"
            "2) Pakai proxy manual"
        )
        return

    if stage == "await_proxy_choice":
        if text in {"1", "tanpa", "tanpa proxy", "no", "n"}:
            data["proxy"] = None
            stage = "await_proxy_done"
        elif text in {"2", "proxy", "pakai proxy", "manual"}:
            data["stage"] = "await_proxy"
            await update.message.reply_text(
                "Silakan input proxy (format host:port atau http://user:pass@host:port)."
            )
            return
        else:
            await update.message.reply_text(
                "Pilihan tidak valid. Balas dengan 1 (tanpa proxy) atau 2 (pakai proxy manual)."
            )
            return

    if stage not in {"await_proxy", "await_proxy_done"}:
        return

    proxy = data.get("proxy")
    if stage == "await_proxy":
        proxy = _normalize_proxy(text)
    url = data["url"]
    use_tempmail = data.get("email_mode") == "tempmail"
    email = data.get("email")
    verification_id = data["verification_id"]
    program_id = data["program_id"]

    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user or user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"] if user else 0)
        )
        context.user_data.pop("verify6", None)
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Gagal memotong poin, silakan coba lagi nanti.")
        context.user_data.pop("verify6", None)
        return

    processing_msg = await update.message.reply_text(
        f"🪖 Mulai memproses verifikasi ChatGPT Military...\n"
        f"ID Verifikasi: {verification_id}\n"
        f"{VERIFY_COST} poin telah dipotong\n\n"
        "Mohon tunggu, proses ini bisa memakan waktu 1-2 menit..."
    )

    semaphore = get_verification_semaphore("chatgpt_military")

    try:
        async with semaphore:
            verifier = MilitaryVerifier(
                verification_id, program_id=program_id, proxy=proxy
            )
            result = await asyncio.to_thread(
                verifier.verify, email=email, use_tempmail=use_tempmail
            )

        db.add_verification(
            user_id,
            "chatgpt_military",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Verifikasi ChatGPT Military berhasil - verificattion succesfull!\n\n"
            if result.get("pending"):
                result_msg += "✨ Informasi sudah dikirim, menunggu peninjauan SheerID\n"
                result_msg += "⏱️ Estimasi waktu peninjauan: beberapa menit\n\n"
            if result.get("email"):
                result_msg += f"📧 Email: {result['email']}\n"
                if use_tempmail:
                    result_msg += (
                        "📨 TempMail otomatis dipakai"
                        f"{' (email diverifikasi otomatis)' if result.get('email_verified') else ''}\n\n"
                    )
            if result.get("redirect_url"):
                result_msg += f"🔗 Tautan lanjut:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verifikasi gagal: {result.get('message', 'Kesalahan tidak diketahui')}\n\n"
                f"{VERIFY_COST} poin telah dikembalikan"
            )
    except Exception as e:
        logger.error("Terjadi kesalahan saat verifikasi ChatGPT Military: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan saat proses: {str(e)}\n\n"
            f"{VERIFY_COST} poin telah dikembalikan"
        )
    finally:
        context.user_data.pop("verify6", None)


async def getV4Code_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /getV4Code - ambil kode verifikasi Bolt.new Teacher"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir dan tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start terlebih dahulu untuk mendaftar.")
        return

    # Cek apakah verification_id diberikan
    if not context.args:
        await update.message.reply_text(
            "Cara penggunaan: /getV4Code <verification_id>\n\n"
            "Contoh: /getV4Code 6929436b50d7dc18638890d0\n\n"
            "verification_id akan dikirimkan setelah Anda menggunakan perintah /verify4."
        )
        return

    verification_id = context.args[0].strip()

    processing_msg = await update.message.reply_text(
        "🔍 Sedang mengecek kode verifikasi, mohon tunggu..."
    )

    try:
        # Cek SheerID API untuk mengambil kode verifikasi
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
            )

            if response.status_code != 200:
                await processing_msg.edit_text(
                    f"❌ Pencarian gagal, kode status: {response.status_code}\n\n"
                    "Silakan coba lagi nanti atau hubungi admin."
                )
                return

            data = response.json()
            current_step = data.get("currentStep")
            reward_code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
            redirect_url = data.get("redirectUrl")

            if current_step == "success" and reward_code:
                result_msg = "✅ Verifikasi berhasil - verificattion succesfull!\n\n"
                result_msg += f"🎉 Kode verifikasi: `{reward_code}`\n\n"
                if redirect_url:
                    result_msg += f"Tautan lanjut:\n{redirect_url}"
                await processing_msg.edit_text(result_msg)
            elif current_step == "pending":
                await processing_msg.edit_text(
                    "⏳ Verifikasi masih dalam proses peninjauan, silakan coba lagi nanti.\n\n"
                    "Biasanya membutuhkan 1-5 menit, mohon bersabar."
                )
            elif current_step == "error":
                error_ids = data.get("errorIds", [])
                await processing_msg.edit_text(
                    "❌ Verifikasi gagal\n\n"
                    f"Pesan error: {', '.join(error_ids) if error_ids else 'Kesalahan tidak diketahui'}"
                )
            else:
                await processing_msg.edit_text(
                    f"⚠️ Status saat ini: {current_step}\n\n"
                    "Kode verifikasi belum tersedia, silakan coba lagi nanti."
                )

    except Exception as e:
        logger.error("Gagal mengambil kode verifikasi Bolt.new: %s", e)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan saat pengecekan: {str(e)}\n\n"
            "Silakan coba lagi nanti atau hubungi admin."
        )
