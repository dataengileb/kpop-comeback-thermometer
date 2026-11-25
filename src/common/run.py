"""Shared tail of every ingestion: validate, write silver and quarantine, enforce the quality gate."""

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path

from common import contracts, storage

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "groups.json"


class QualityGateError(Exception):
    """Raised when too many records break the contract. Step Functions stops the run on it."""


def load_groups() -> list[dict]:
    return json.loads(CONFIG_PATH.read_text())["groups"]


def snapshot_date(event: dict) -> str:
    """The run date comes from the scheduler so a re-run of a past day writes to that day."""
    value = (event or {}).get("snapshot_date")
    if value:
        return date.fromisoformat(value).isoformat()
    return datetime.now(timezone.utc).date().isoformat()


def publish(table: str, contract: str, records: list[dict], day: str) -> dict:
    valid, invalid = contracts.split_valid(records, contracts.load_contract(contract))
    storage.put_jsonl(storage.table_key("validated", table, day), valid)
    storage.put_jsonl(storage.table_key("quarantine", table, day), invalid)

    max_ratio = float(os.environ.get("MAX_INVALID_RATIO", "0.05"))
    total = len(valid) + len(invalid)
    summary = {"table": table, "snapshot_date": day, "valid": len(valid), "invalid": len(invalid)}
    print(json.dumps(summary))
    if total == 0:
        raise QualityGateError(f"{table}: source returned no records")
    if len(invalid) / total > max_ratio:
        raise QualityGateError(f"{table}: {len(invalid)}/{total} records broke the contract")
    return summary
