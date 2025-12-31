"""SheerID military verification flow."""
import logging
import random
import re
from datetime import datetime
from typing import Dict, Optional, Tuple

import httpx

from . import config
from .name_generator import (
    NameGenerator,
    generate_birth_date,
    generate_email,
    generate_service_id,
)
from .img_generator import generate_military_id_card

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class SheerIDVerifier:
    """SheerID military identity verifier."""

    def __init__(self, verification_id: str):
        self.verification_id = verification_id
        self.device_fingerprint = self._generate_device_fingerprint()
        self.http_client = httpx.Client(timeout=30.0)

    def __del__(self):
        if hasattr(self, "http_client"):
            self.http_client.close()

    @staticmethod
    def _generate_device_fingerprint() -> str:
        chars = "0123456789abcdef"
        return "".join(random.choice(chars) for _ in range(32))

    @staticmethod
    def normalize_url(url: str) -> str:
        return url

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
            method=method,
            url=url,
            json=body,
            headers=headers,
        )
        try:
            data = response.json()
        except Exception:
            data = response.text
        return data, response.status_code

    def _upload_to_s3(self, upload_url: str, img_data: bytes) -> bool:
        try:
            headers = {"Content-Type": "image/png"}
            response = self.http_client.put(
                upload_url, content=img_data, headers=headers, timeout=60.0
            )
            return 200 <= response.status_code < 300
        except Exception as exc:
            logger.error("S3 上传失败: %s", exc)
            return False

    @staticmethod
    def _normalize_date(raw_date: str) -> str:
        """Normalize date into YYYY-MM-DD."""
        if not raw_date:
            return ""
        raw_date = raw_date.strip()
        try:
            return datetime.strptime(raw_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            pass

        month_map = {
            "januari": "01",
            "februari": "02",
            "maret": "03",
            "april": "04",
            "mei": "05",
            "juni": "06",
            "juli": "07",
            "agustus": "08",
            "september": "09",
            "oktober": "10",
            "november": "11",
            "desember": "12",
        }
        parts = raw_date.replace(",", "").split()
        if len(parts) == 3:
            day, month_name, year = parts
            month = month_map.get(month_name.lower())
            if month:
                return f"{year}-{month}-{day.zfill(2)}"

        return raw_date

    def _collect_military_status(self) -> Tuple[Dict, int]:
        """Collect military status before personal info submission."""
        body = {"status": config.DEFAULT_STATUS}
        return self._sheerid_request(
            "POST",
            f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectMilitaryStatus",
            body,
        )

    def verify(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        birth_date: str = None,
        death_date: str = None,
        branch_name: str = None,
        rank: str = None,
    ) -> Dict:
        """Execute military verification flow."""
        try:
            current_step = "initial"

            if not first_name or not last_name:
                name = NameGenerator.generate()
                first_name = name["first_name"]
                last_name = name["last_name"]

            branch_name = branch_name or config.DEFAULT_BRANCH_NAME
            branch = config.BRANCHES.get(branch_name)
            if not branch:
                raise Exception(f"未知军种: {branch_name}")

            if not email:
                email = generate_email(first_name, last_name, branch["domain"])
            if not birth_date:
                birth_date = generate_birth_date()
            birth_date = self._normalize_date(birth_date)

            display_death_date = self._normalize_date(death_date) if death_date else ""
            if display_death_date:
                discharge_date = display_death_date
            else:
                discharge_date = datetime.utcnow().strftime("%Y-%m-%d")

            service_id = generate_service_id(first_name, last_name, birth_date)
            rank = rank or "Sergeant"

            logger.info("军人信息: %s %s", first_name, last_name)
            logger.info("邮箱: %s", email)
            logger.info("分支: %s", branch["name"])
            logger.info("生日: %s", birth_date)
            logger.info("验证 ID: %s", self.verification_id)

            logger.info("步骤 1/3: 生成军人证件 PNG...")
            img_data = generate_military_id_card(
                first_name,
                last_name,
                branch["name"],
                service_id,
                rank,
                birth_date,
                display_death_date,
            )
            file_size = len(img_data)
            logger.info("✅ PNG 大小: %.2fKB", file_size / 1024)

            logger.info("步骤 2/4: 收集军人状态...")
            status_data, status_status = self._collect_military_status()
            if status_status != 200:
                raise Exception(f"步骤 2 失败 (状态码 {status_status}): {status_data}")

            submission_url = status_data.get("submissionUrl")
            if not submission_url:
                raise Exception("步骤 2 失败: 未返回 submissionUrl")

            logger.info("步骤 3/4: 提交军人信息...")
            step2_body = {
                "firstName": first_name,
                "lastName": last_name,
                "birthDate": birth_date,
                "email": email,
                "phoneNumber": "",
                "organization": {
                    "id": int(branch["id"]),
                    "name": branch["name"],
                },
                "dischargeDate": discharge_date,
                "locale": "en-US",
                "country": "US",
                "deviceFingerprintHash": self.device_fingerprint,
                "metadata": {
                    "marketConsentValue": False,
                    "refererUrl": f"{config.SHEERID_BASE_URL}/verify/{config.PROGRAM_ID}/?verificationId={self.verification_id}",
                    "verificationId": self.verification_id,
                    "flags": (
                        "{\"doc-upload-considerations\":\"default\","
                        "\"doc-upload-may24\":\"default\","
                        "\"doc-upload-redesign-use-legacy-message-keys\":false,"
                        "\"docUpload-assertion-checklist\":\"default\","
                        "\"include-cvec-field-france-student\":\"not-labeled-optional\","
                        "\"org-search-overlay\":\"default\","
                        "\"org-selected-display\":\"default\"}"
                    ),
                    "submissionOptIn": (
                        "By submitting the personal information above, I acknowledge that my personal "
                        "information is being collected under the privacy policy of the business from "
                        "which I am seeking a discount, and I understand that my personal information "
                        "will be shared with SheerID as a processor/third-party service provider in order "
                        "for SheerID to confirm my eligibility for a special offer. Contact OpenAI Support "
                        "for further assistance at support@openai.com"
                    ),
                },
            }

            step2_data, step2_status = self._sheerid_request(
                "POST",
                submission_url,
                step2_body,
            )

            if step2_status != 200:
                raise Exception(f"步骤 3 失败 (状态码 {step2_status}): {step2_data}")
            if step2_data.get("currentStep") == "error":
                error_msg = ", ".join(step2_data.get("errorIds", ["Unknown error"]))
                raise Exception(f"步骤 3 错误: {error_msg}")

            logger.info("✅ 步骤 3 完成: %s", step2_data.get("currentStep"))
            current_step = step2_data.get("currentStep", current_step)

            if current_step in ["sso", "collectInactiveMilitaryPersonalInfo"]:
                logger.info("步骤 3.5/4: 跳过 SSO 验证...")
                step_sso_data, _ = self._sheerid_request(
                    "DELETE",
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso",
                )
                logger.info("✅ SSO 完成: %s", step_sso_data.get("currentStep"))
                current_step = step_sso_data.get("currentStep", current_step)

            logger.info("步骤 4/4: 请求并上传文档...")
            step3_body = {
                "files": [
                    {
                        "fileName": "military_id.png",
                        "mimeType": "image/png",
                        "fileSize": file_size,
                    }
                ]
            }
            step3_data, step3_status = self._sheerid_request(
                "POST",
                f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                step3_body,
            )

            if step3_status != 200 or not step3_data.get("documents"):
                raise Exception(f"步骤 3 失败: {step3_data}")

            upload_url = step3_data["documents"][0]["uploadUrl"]
            if not self._upload_to_s3(upload_url, img_data):
                raise Exception("S3 上传失败")

            step4_data, _ = self._sheerid_request(
                "POST",
                f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload",
            )
            logger.info("✅ 文档提交完成: %s", step4_data.get("currentStep"))

            return {
                "success": True,
                "pending": True,
                "message": "文档已提交，等待审核",
                "verification_id": self.verification_id,
                "redirect_url": step4_data.get("redirectUrl"),
                "status": step4_data,
            }
        except Exception as exc:
            logger.error("❌ 验证失败: %s", exc)
            return {
                "success": False,
                "message": str(exc),
                "verification_id": self.verification_id,
            }
