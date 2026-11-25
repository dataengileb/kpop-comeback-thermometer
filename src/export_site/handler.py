"""Daily export of the gold tables to one JSON file for the static site.

Writes exports/snapshot_date=YYYY-MM-DD/site.json and exports/latest.json. scripts/fetch_export.sh
copies it into site/data/, so the published site never talks to AWS.
"""

import os
import time

import boto3

from common import contracts, storage
from common.run import QualityGateError, load_artists, snapshot_date

VIDEOS_SQL = """
SELECT video_id, artist, market, video_type, compare_with, title, published_at, first_snapshot_date,
       last_snapshot_date, views_latest, comparable, is_duplicate, views_d1, views_d7, views_d28,
       rank_d1, rank_d7, rank_d28, compared_d1, compared_d7, compared_d28
FROM gold_video_launch
ORDER BY artist, market, published_at DESC
"""

LASTFM_SQL = """
SELECT artist, snapshot_date, listeners, playcount, listeners_change, playcount_change
FROM gold_artist_daily
WHERE snapshot_date = (SELECT max(snapshot_date) FROM gold_artist_daily)
ORDER BY artist
"""


def _cast(value: str | None, athena_type: str):
    """Athena returns every cell as text; restore the types the site needs."""
    if value is None:
        return None
    if athena_type in ("bigint", "integer"):
        return int(value)
    if athena_type == "boolean":
        return value == "true"
    if athena_type.startswith("timestamp"):
        # "2025-07-11 04:00:00.000000" -> "2025-07-11T04:00:00Z", which browsers parse as UTC.
        return value[:19].replace(" ", "T") + "Z"
    return value


def to_rows(pages: list[dict]) -> list[dict]:
    """Turn GetQueryResults pages into dicts. The first row of the first page is the header."""
    columns = pages[0]["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
    rows = [row for page in pages for row in page["ResultSet"]["Rows"]][1:]
    return [
        {c["Name"]: _cast(cell.get("VarCharValue"), c["Type"]) for c, cell in zip(columns, row["Data"])}
        for row in rows
    ]


def run_query(sql: str) -> list[dict]:
    athena = boto3.client("athena")
    query_id = athena.start_query_execution(
        QueryString=sql,
        WorkGroup=os.environ["ATHENA_WORKGROUP"],
        QueryExecutionContext={"Database": os.environ["ATHENA_DATABASE"]},
    )["QueryExecutionId"]
    while True:
        status = athena.get_query_execution(QueryExecutionId=query_id)["QueryExecution"]["Status"]
        if status["State"] in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(1)
    if status["State"] != "SUCCEEDED":
        raise RuntimeError(f"Athena query {query_id} {status['State']}: {status.get('StateChangeReason')}")
    pages = list(athena.get_paginator("get_query_results").paginate(QueryExecutionId=query_id))
    return to_rows(pages)


def build_export(day: str, artists: list[dict], videos: list[dict], lastfm: list[dict]) -> dict:
    """Everything the site shows, in one document. All rows must honour the site contract."""
    valid, invalid = contracts.split_valid(videos, contracts.load_contract("site_video"))
    if invalid:
        raise QualityGateError(f"site_video: {len(invalid)} rows broke the contract, first: {invalid[0]['errors']}")
    tracked = {a["slug"] for a in artists if a["lastfm_name"]}
    return {
        "snapshot_date": day,
        "first_snapshot_date": min((v["first_snapshot_date"] for v in valid), default=None),
        "artists": [{k: a[k] for k in ("slug", "name", "kind", "parent")} for a in artists],
        "videos": valid,
        # gold keeps rows for artists later dropped from Last.fm (MERGE never deletes): skip them.
        "lastfm": [row for row in lastfm if row["artist"] in tracked],
    }


def lambda_handler(event, context):
    day = snapshot_date(event)
    export = build_export(day, load_artists(), run_query(VIDEOS_SQL), run_query(LASTFM_SQL))
    storage.put_json(f"exports/snapshot_date={day}/site.json", export)
    storage.put_json("exports/latest.json", export)
    return {"snapshot_date": day, "videos": len(export["videos"]), "lastfm": len(export["lastfm"])}
