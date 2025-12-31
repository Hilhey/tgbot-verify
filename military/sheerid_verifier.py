"""Program utama verifikasi militer SheerID"""
import logging
import re
from typing import Dict, Optional, Tuple

import httpx

from . import config
from .data_store import get_organization, pop_random_record

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class SheerIDVerifier:
    """Verifier identitas militer SheerID"""

    def __init__(self, verification_id: str):
        self.verification_id = verification_id
        self.http_client = httpx.Client(timeout=30.0)

    def __del__(self):
        if hasattr(self, "http_client"):
            self.http_client.close()

    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _sheerid_request(
        self, method: str, url: str, body: Optional[Dict] = None
    ) -> Tuple[Dict, int]:
        headers = {
            "Content-Type": "application/json",
        }

        response = self.http_client.request(
            method=method, url=url, json=body, headers=headers
        )
        try:
            data = response.json()
        except Exception:
            data = response.text
        return data, response.status_code

    def _collect_military_status(self, status: str) -> Dict:
        step1_body = {"status": status}
        step1_data, step1_status = self._sheerid_request(
            "POST",
            f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectMilitaryStatus",
            step1_body,
        )
        if step1_status != 200:
            raise Exception(f"collectMilitaryStatus gagal (kode status {step1_status}): {step1_data}")
        if step1_data.get("currentStep") == "error":
            error_msg = ", ".join(step1_data.get("errorIds", ["Unknown error"]))
            raise Exception(f"collectMilitaryStatus error: {error_msg}")
        return step1_data

    def _collect_personal_info(self, submission_url: str, payload: Dict) -> Dict:
        step2_data, step2_status = self._sheerid_request("POST", submission_url, payload)
        if step2_status != 200:
            raise Exception(
                f"collectInactiveMilitaryPersonalInfo gagal (kode status {step2_status}): {step2_data}"
            )
        if step2_data.get("currentStep") == "error":
            error_msg = ", ".join(step2_data.get("errorIds", ["Unknown error"]))
            raise Exception(f"collectInactiveMilitaryPersonalInfo error: {error_msg}")
        return step2_data

    def verify(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        birth_date: str = None,
    ) -> Dict:
        """Jalankan alur verifikasi militer"""
        try:
            record = pop_random_record()
            first_name = record.first_name
            last_name = record.last_name
            birth_date = record.birth_date

            if not email:
                raise ValueError("Email wajib diisi oleh pengguna")

            discharge_date = record.discharge_date
            organization = get_organization(record.branch)

            logger.info("Data militer: %s %s", first_name, last_name)
            logger.info("Email: %s", email)
            logger.info("Tanggal lahir: %s", birth_date)
            logger.info("Tanggal pensiun: %s", discharge_date)
            logger.info("Organisasi: %s", organization["name"])
            logger.info("ID verifikasi: %s", self.verification_id)

            logger.info("Langkah 1/2: mengumpulkan status militer...")
            step1_data = self._collect_military_status(config.MILITARY_STATUS)
            submission_url = step1_data.get("submissionUrl")
            if not submission_url:
                raise Exception("submissionUrl tidak ditemukan")

            logger.info("Langkah 2/2: mengirim data pribadi militer...")
            step2_body = {
                "firstName": first_name,
                "lastName": last_name,
                "birthDate": birth_date,
                "email": email,
                "phoneNumber": "",
                "organization": {
                    "id": organization["id"],
                    "name": organization["name"],
                },
                "dischargeDate": discharge_date,
                "locale": "en-US",
                "country": "US",
                "metadata": {
                    "marketConsentValue": False,
                    "refererUrl": "",
                    "verificationId": self.verification_id,
                    "flags": config.SUBMISSION_FLAGS,
                    "submissionOptIn": config.SUBMISSION_OPT_IN,
                },
            }

            step2_data = self._collect_personal_info(submission_url, step2_body)
            current_step = step2_data.get("currentStep")
            logger.info("✅ Pengiriman data pribadi selesai: %s", current_step)

            return {
                "success": True,
                "pending": current_step not in {"success", "complete"},
                "message": "Informasi militer sudah dikirim",
                "verification_id": self.verification_id,
                "redirect_url": step2_data.get("redirectUrl"),
                "status": step2_data,
            }

        except Exception as e:
            logger.error("❌ Verifikasi gagal: %s", e)
            return {"success": False, "message": str(e), "verification_id": self.verification_id}


def main():
    """Fungsi utama - CLI"""
    import sys

    print("=" * 60)
    print("Alat verifikasi militer SheerID (Python)")
    print("=" * 60)
    print()

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Masukkan URL verifikasi SheerID: ").strip()

    if not url:
        print("❌ Error: URL tidak diberikan")
        sys.exit(1)

    verification_id = SheerIDVerifier.parse_verification_id(url)
    if not verification_id:
        print("❌ Error: format ID verifikasi tidak valid")
        sys.exit(1)

    print(f"✅ Berhasil mengambil ID verifikasi: {verification_id}")
    print()

    verifier = SheerIDVerifier(verification_id)
    result = verifier.verify()

    print()
    print("=" * 60)
    print("Hasil verifikasi:")
    print("=" * 60)
    print(f"Status: {'✅ Berhasil' if result['success'] else '❌ Gagal'}")
    print(f"Pesan: {result['message']}")
    if result.get("redirect_url"):
        print(f"Tautan lanjut: {result['redirect_url']}")
    print("=" * 60)

    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit(main())
