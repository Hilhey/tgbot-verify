"""Program utama bot Telegram"""
import logging
from functools import partial

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import BOT_TOKEN
from database_mysql import Database
from handlers.user_commands import (
    start_command,
    about_command,
    help_command,
    balance_command,
    checkin_command,
    invite_command,
    use_command,
)
from handlers.verify_commands import (
    verify_command,
    verify2_command,
    verify3_command,
    verify4_command,
    verify5_command,
    verify6_command,
    verify6_text_handler,
    getV4Code_command,
)
from handlers.admin_commands import (
    addbalance_command,
    block_command,
    white_command,
    blacklist_command,
    genkey_command,
    listkeys_command,
    broadcast_command,
)

# Konfigurasi logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context) -> None:
    """Penanganan error global"""
    logger.exception("Terjadi error saat memproses update: %s", context.error, exc_info=context.error)


def main():
    """Fungsi utama"""
    # Inisialisasi database
    db = Database()

    # Buat aplikasi - aktifkan pemrosesan konkruen
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)  # 🔥 Kunci: aktifkan pemrosesan konkruen untuk banyak perintah
        .build()
    )

    # Daftarkan perintah pengguna (gunakan partial untuk meneruskan db)
    application.add_handler(CommandHandler("start", partial(start_command, db=db)))
    application.add_handler(CommandHandler("about", partial(about_command, db=db)))
    application.add_handler(CommandHandler("help", partial(help_command, db=db)))
    application.add_handler(CommandHandler("balance", partial(balance_command, db=db)))
    application.add_handler(CommandHandler("qd", partial(checkin_command, db=db)))
    application.add_handler(CommandHandler("invite", partial(invite_command, db=db)))
    application.add_handler(CommandHandler("use", partial(use_command, db=db)))

    # Daftarkan perintah verifikasi
    application.add_handler(CommandHandler("verify", partial(verify_command, db=db)))
    application.add_handler(CommandHandler("verify2", partial(verify2_command, db=db)))
    application.add_handler(CommandHandler("verify3", partial(verify3_command, db=db)))
    application.add_handler(CommandHandler("verify4", partial(verify4_command, db=db)))
    application.add_handler(CommandHandler("verify5", partial(verify5_command, db=db)))
    application.add_handler(CommandHandler("verify6", partial(verify6_command, db=db)))
    application.add_handler(CommandHandler("getV4Code", partial(getV4Code_command, db=db)))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, partial(verify6_text_handler, db=db))
    )

    # Daftarkan perintah admin
    application.add_handler(CommandHandler("addbalance", partial(addbalance_command, db=db)))
    application.add_handler(CommandHandler("block", partial(block_command, db=db)))
    application.add_handler(CommandHandler("white", partial(white_command, db=db)))
    application.add_handler(CommandHandler("blacklist", partial(blacklist_command, db=db)))
    application.add_handler(CommandHandler("genkey", partial(genkey_command, db=db)))
    application.add_handler(CommandHandler("listkeys", partial(listkeys_command, db=db)))
    application.add_handler(CommandHandler("broadcast", partial(broadcast_command, db=db)))

    # Daftarkan handler error
    application.add_error_handler(error_handler)

    logger.info("Bot sedang berjalan...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
