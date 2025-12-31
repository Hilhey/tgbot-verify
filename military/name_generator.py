"""军人信息生成器"""
import random
from datetime import date

from one.name_generator import NameGenerator


def generate_email(first_name: str, last_name: str) -> str:
    """生成随机邮箱"""
    number = random.randint(100, 999)
    return f"{first_name.lower()}.{last_name.lower()}{number}@gmail.com"


def generate_birth_date() -> str:
    """生成随机生日（1955-1985）"""
    year = random.randint(1955, 1985)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


def generate_discharge_date(birth_date: str) -> str:
    """生成合理退役日期"""
    birth_year = int(birth_date.split("-")[0])
    current_year = date.today().year
    min_year = birth_year + 20
    max_year = min(birth_year + 45, current_year - 1)
    if min_year > max_year:
        max_year = min_year
    year = random.randint(min_year, max_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


def generate_name() -> dict:
    """生成名字"""
    return NameGenerator.generate()
