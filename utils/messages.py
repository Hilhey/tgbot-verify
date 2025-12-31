"""消息模板"""
from config import CHANNEL_URL, VERIFY_COST, HELP_NOTION_URL


def get_welcome_message(full_name: str, invited_by: bool = False) -> str:
    """Ambil pesan sambutan"""
    msg = (
        f"🎉 Selamat datang, {full_name}!\n"
        "Anda berhasil terdaftar dan mendapatkan 1 poin.\n"
    )
    if invited_by:
        msg += "Terima kasih telah bergabung lewat tautan undangan, pengundang mendapatkan 2 poin.\n"

    msg += (
        "\nBot ini dapat menyelesaikan verifikasi SheerID secara otomatis.\n"
        "Mulai cepat:\n"
        "/about - Mengenal fitur bot\n"
        "/balance - Cek saldo poin\n"
        "/help - Lihat daftar perintah lengkap\n\n"
        "Dapatkan lebih banyak poin:\n"
        "/qd - Check-in harian\n"
        "/invite - Undang teman\n"
        f"Gabung channel: {CHANNEL_URL}"
    )
    return msg


def get_about_message() -> str:
    """Ambil pesan tentang bot"""
    return (
        "🤖 Bot verifikasi otomatis SheerID\n"
        "\n"
        "Fitur utama:\n"
        "- Otomatis menyelesaikan verifikasi SheerID untuk siswa/guru\n"
        "- Mendukung Gemini One Pro、ChatGPT Teacher K12、Spotify Student、YouTube Student、Bolt.new Teacher、ChatGPT Military\n"
        "\n"
        "Cara mendapatkan poin:\n"
        "- Registrasi mendapat 1 poin\n"
        "- Check-in harian +1 poin\n"
        "- Undang teman +2 poin/orang\n"
        "- Gunakan kode (sesuai aturan)\n"
        f"- Gabung channel: {CHANNEL_URL}\n"
        "\n"
        "Cara penggunaan:\n"
        "1. Mulai verifikasi di web dan salin tautan verifikasi lengkap\n"
        "2. Kirim /verify、/verify2、/verify3、/verify4、/verify5 atau /verify6 beserta tautannya\n"
        "3. Tunggu proses dan lihat hasilnya\n"
        "4. Verifikasi Bolt.new akan otomatis mengambil kode, untuk cek manual gunakan /getV4Code <verification_id>\n"
        "\n"
        "Untuk perintah lainnya kirim /help"
    )


def get_help_message(is_admin: bool = False) -> str:
    """Ambil pesan bantuan"""
    msg = (
        "📖 Bot verifikasi otomatis SheerID - Bantuan\n"
        "\n"
        "Perintah pengguna:\n"
        "/start - Mulai (registrasi)\n"
        "/about - Mengenal fitur bot\n"
        "/balance - Cek saldo poin\n"
        "/qd - Check-in harian (+1 poin)\n"
        "/invite - Buat tautan undangan (+2 poin/orang)\n"
        "/use <kode> - Tukar poin dengan kode\n"
        f"/verify <tautan> - Gemini One Pro (biaya {VERIFY_COST} poin)\n"
        f"/verify2 <tautan> - ChatGPT Teacher K12 (biaya {VERIFY_COST} poin)\n"
        f"/verify3 <tautan> - Spotify Student (biaya {VERIFY_COST} poin)\n"
        f"/verify4 <tautan> - Bolt.new Teacher (biaya {VERIFY_COST} poin)\n"
        f"/verify5 <tautan> - YouTube Student Premium (biaya {VERIFY_COST} poin)\n"
        f"/verify6 <tautan> <email> - ChatGPT Military (biaya {VERIFY_COST} poin)\n"
        "/getV4Code <verification_id> - Ambil kode verifikasi Bolt.new\n"
        "/help - Lihat bantuan ini\n"
        f"Gagal verifikasi lihat: {HELP_NOTION_URL}\n"
    )

    if is_admin:
        msg += (
            "\nPerintah admin:\n"
            "/addbalance <user_id> <poin> - Tambah poin pengguna\n"
            "/block <user_id> - Blokir pengguna\n"
            "/white <user_id> - Buka blokir pengguna\n"
            "/blacklist - Lihat daftar blokir\n"
            "/genkey <kode> <poin> [jumlah] [hari] - Buat kode\n"
            "/listkeys - Lihat daftar kode\n"
            "/broadcast <teks> - Kirim pemberitahuan ke semua pengguna\n"
        )

    return msg


def get_insufficient_balance_message(current_balance: int) -> str:
    """Ambil pesan saldo poin tidak cukup"""
    return (
        f"Poin tidak cukup! Dibutuhkan {VERIFY_COST} poin, saldo saat ini {current_balance} poin.\n\n"
        "Cara mendapatkan poin:\n"
        "- Check-in harian /qd\n"
        "- Undang teman /invite\n"
        "- Gunakan kode /use <kode>"
    )


def get_verify_usage_message(command: str, service_name: str) -> str:
    """Ambil petunjuk penggunaan perintah verifikasi"""
    return (
        f"Cara penggunaan: {command} <tautan SheerID>\n\n"
        "Contoh:\n"
        f"{command} https://services.sheerid.com/verify/xxx/?verificationId=xxx\n\n"
        "Cara mendapatkan tautan verifikasi:\n"
        f"1. Kunjungi halaman verifikasi {service_name}\n"
        "2. Mulai proses verifikasi\n"
        "3. Salin URL lengkap dari address bar browser\n"
        f"4. Kirim dengan perintah {command}"
    )
