"""S3 layout. Every key is derived from (source, snapshot_date), so re-running the same day overwrites it.

bronze/     what the API returned, untouched
silver/     flattened records that passed their contract
quarantine/ records that failed their contract, with the reasons
gold/       Iceberg tables built from silver by Athena (see infra/template.yaml)
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


def bronze_key(source: str, snapshot_date: str, name: str) -> str:
    return f"bronze/source={source}/snapshot_date={snapshot_date}/{name}.json"


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
