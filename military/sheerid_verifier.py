"""SheerID 军人验证主程序"""
import logging
import random
import re
from typing import Dict, Optional, Tuple

import httpx

from . import config
from .name_generator import generate_birth_date, generate_discharge_date, generate_email, generate_name

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class SheerIDVerifier:
    """SheerID 军人身份验证器"""

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
            raise Exception(f"collectMilitaryStatus 失败 (状态码 {step1_status}): {step1_data}")
        if step1_data.get("currentStep") == "error":
            error_msg = ", ".join(step1_data.get("errorIds", ["Unknown error"]))
            raise Exception(f"collectMilitaryStatus 错误: {error_msg}")
        return step1_data

    def _collect_personal_info(self, submission_url: str, payload: Dict) -> Dict:
        step2_data, step2_status = self._sheerid_request("POST", submission_url, payload)
        if step2_status != 200:
            raise Exception(
                f"collectInactiveMilitaryPersonalInfo 失败 (状态码 {step2_status}): {step2_data}"
            )
        if step2_data.get("currentStep") == "error":
            error_msg = ", ".join(step2_data.get("errorIds", ["Unknown error"]))
            raise Exception(f"collectInactiveMilitaryPersonalInfo 错误: {error_msg}")
        return step2_data

    def verify(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        birth_date: str = None,
    ) -> Dict:
        """执行军人认证流程"""
        try:
            if not first_name or not last_name:
                name = generate_name()
                first_name = name["first_name"]
                last_name = name["last_name"]

            if not birth_date:
                birth_date = generate_birth_date()

            if not email:
                email = generate_email(first_name, last_name)

            discharge_date = generate_discharge_date(birth_date)
            organization = random.choice(config.MILITARY_ORGANIZATIONS)

            logger.info("军人信息: %s %s", first_name, last_name)
            logger.info("邮箱: %s", email)
            logger.info("出生日期: %s", birth_date)
            logger.info("退役日期: %s", discharge_date)
            logger.info("组织: %s", organization["name"])
            logger.info("验证 ID: %s", self.verification_id)

            logger.info("步骤 1/2: 收集军人状态...")
            step1_data = self._collect_military_status(config.MILITARY_STATUS)
            submission_url = step1_data.get("submissionUrl")
            if not submission_url:
                raise Exception("未获取到 submissionUrl")

            logger.info("步骤 2/2: 提交军人个人信息...")
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
            logger.info("✅ 个人信息提交完成: %s", current_step)

            return {
                "success": True,
                "pending": current_step not in {"success", "complete"},
                "message": "军人信息已提交",
                "verification_id": self.verification_id,
                "redirect_url": step2_data.get("redirectUrl"),
                "status": step2_data,
            }

        except Exception as e:
            logger.error("❌ 验证失败: %s", e)
            return {"success": False, "message": str(e), "verification_id": self.verification_id}


def main():
    """主函数 - 命令行界面"""
    import sys

    print("=" * 60)
    print("SheerID 军人身份验证工具 (Python版)")
    print("=" * 60)
    print()

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("请输入 SheerID 验证 URL: ").strip()

    if not url:
        print("❌ 错误: 未提供 URL")
        sys.exit(1)

    verification_id = SheerIDVerifier.parse_verification_id(url)
    if not verification_id:
        print("❌ 错误: 无效的验证 ID 格式")
        sys.exit(1)

    print(f"✅ 解析到验证 ID: {verification_id}")
    print()

    verifier = SheerIDVerifier(verification_id)
    result = verifier.verify()

    print()
    print("=" * 60)
    print("验证结果:")
    print("=" * 60)
    print(f"状态: {'✅ 成功' if result['success'] else '❌ 失败'}")
    print(f"消息: {result['message']}")
    if result.get("redirect_url"):
        print(f"跳转 URL: {result['redirect_url']}")
    print("=" * 60)

    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit(main())
