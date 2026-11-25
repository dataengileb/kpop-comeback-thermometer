"""Shared tail of every ingestion: validate, write silver and quarantine, enforce the quality gate."""

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path

from common import contracts, storage

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "artists.json"


class QualityGateError(Exception):
    """Raised when too many records break the contract. Step Functions stops the run on it."""


def load_config() -> dict:
    """Artists (groups, units and soloists) and the YouTube channels their videos appear on."""
    return json.loads(CONFIG_PATH.read_text())


def load_artists() -> list[dict]:
    return load_config()["artists"]


def snapshot_date(event: dict) -> str:
    """Today's UTC date. The APIs only return current totals, so a past date would be mislabelled."""
    today = datetime.now(timezone.utc).date()
    value = (event or {}).get("snapshot_date")
    if value and date.fromisoformat(value) != today:
        raise ValueError(f"snapshot_date {value} is not today ({today}); past days cannot be re-taken")
    return today.isoformat()


def publish(table: str, contract: str, records: list[dict], day: str) -> dict:
    """Quarantine is always written so a failed run can be diagnosed. Silver is written
    only when the gate passes, so downstream never reads a day that failed."""
    valid, invalid = contracts.split_valid(records, contracts.load_contract(contract))
    storage.put_jsonl(storage.table_key("quarantine", table, day), invalid)

    max_ratio = float(os.environ.get("MAX_INVALID_RATIO", "0.05"))
    total = len(valid) + len(invalid)
    summary = {"table": table, "snapshot_date": day, "valid": len(valid), "invalid": len(invalid)}
    print(json.dumps(summary))
    if total == 0:
        raise QualityGateError(f"{table}: source returned no records")
    if len(invalid) / total > max_ratio:
        raise QualityGateError(f"{table}: {len(invalid)}/{total} records broke the contract")
    storage.put_jsonl(storage.table_key("silver", table, day), valid)
    return summary
