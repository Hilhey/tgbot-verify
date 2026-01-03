"""Manajemen data verifikasi militer."""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List

from . import config

DATA_FILE = Path(__file__).with_name("data_records.tsv")
POOL_FILE = Path(__file__).with_name("data_pool.json")

MONTH_MAP = {
    "Januari": "01",
    "Februari": "02",
    "Maret": "03",
    "April": "04",
    "Mei": "05",
    "Juni": "06",
    "Juli": "07",
    "Agustus": "08",
    "September": "09",
    "Oktober": "10",
    "November": "11",
    "Desember": "12",
}


@dataclass
class MilitaryRecord:
    status: str
    branch: str
    first_name: str
    last_name: str
    birth_date: str
    discharge_date: str


def _parse_date(raw: str) -> str:
    parts = raw.strip().split()
    if len(parts) != 3:
        raise ValueError(f"Format tanggal tidak valid: {raw}")
    day, month_name, year = parts
    month = MONTH_MAP.get(month_name)
    if not month:
        raise ValueError(f"Nama bulan tidak valid: {month_name}")
    return f"{year}-{month}-{int(day):02d}"


def _parse_records() -> List[MilitaryRecord]:
    if not DATA_FILE.exists():
        raise FileNotFoundError("data_records.tsv tidak ditemukan")

    records: List[MilitaryRecord] = []
    for line in DATA_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.lower().startswith("status"):
            continue
        columns = [col.strip() for col in line.split("\t")]
        if len(columns) < 6:
            raise ValueError(f"Baris data tidak lengkap: {line}")
        status, branch, first_name, last_name, birth_raw, discharge_raw = columns[:6]
        records.append(
            MilitaryRecord(
                status=status,
                branch=branch,
                first_name=first_name,
                last_name=last_name,
                birth_date=_parse_date(birth_raw),
                discharge_date=_parse_date(discharge_raw),
            )
        )
    return records


def _load_pool() -> List[MilitaryRecord]:
    if POOL_FILE.exists():
        raw = json.loads(POOL_FILE.read_text(encoding="utf-8"))
        return [MilitaryRecord(**item) for item in raw]

    records = _parse_records()
    _save_pool(records)
    return records


def _save_pool(records: List[MilitaryRecord]) -> None:
    POOL_FILE.write_text(
        json.dumps([record.__dict__ for record in records], indent=2),
        encoding="utf-8",
    )


def pop_random_record() -> MilitaryRecord:
    records = _load_pool()
    if not records:
        raise RuntimeError("Data verifikasi militer sudah habis")
    index = random.randrange(len(records))
    record = records.pop(index)
    _save_pool(records)
    return record


def get_organization(branch: str) -> dict:
    organization = config.ORGANIZATION_BY_NAME.get(branch)
    if not organization:
        raise ValueError(f"Branch tidak dikenali: {branch}")
    return {
        "id": organization["id"],
        "name": organization["name"],
    }
