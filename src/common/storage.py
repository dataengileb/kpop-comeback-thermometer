"""S3 layout. Every key is derived from (source, snapshot_date), so re-running a day overwrites it.

raw/        what the API returned, untouched (bronze)
validated/  flattened records that passed the contract (silver input)
quarantine/ records that failed the contract, with the reasons
"""

import json
import os

import boto3

_s3 = None


def _client():
    global _s3
    if _s3 is None:
        _s3 = boto3.client("s3")
    return _s3


def raw_key(source: str, snapshot_date: str, name: str) -> str:
    return f"raw/source={source}/snapshot_date={snapshot_date}/{name}.json"


def table_key(zone: str, table: str, snapshot_date: str) -> str:
    return f"{zone}/{table}/snapshot_date={snapshot_date}/part-0000.jsonl"


def put_json(key: str, payload) -> None:
    _client().put_object(
        Bucket=os.environ["DATA_BUCKET"],
        Key=key,
        Body=json.dumps(payload, ensure_ascii=False).encode(),
        ContentType="application/json",
    )


def put_jsonl(key: str, rows: list[dict]) -> None:
    body = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
    _client().put_object(
        Bucket=os.environ["DATA_BUCKET"],
        Key=key,
        Body=body.encode(),
        ContentType="application/x-ndjson",
    )
