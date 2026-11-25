import pytest

from common.run import QualityGateError, load_artists
from export_site.handler import build_export, to_rows


def _page(columns, rows):
    header = {"Data": [{"VarCharValue": name} for name, _ in columns]}
    return {"ResultSet": {
        "ResultSetMetadata": {"ColumnInfo": [{"Name": n, "Type": t} for n, t in columns]},
        "Rows": [header] + [{"Data": [{} if v is None else {"VarCharValue": v} for v in row]} for row in rows],
    }}


COLUMNS = [("video_id", "varchar"), ("published_at", "timestamp"), ("views_latest", "bigint"),
           ("comparable", "boolean"), ("views_d7", "bigint")]


def test_rows_get_their_types_back_and_nulls_stay_null():
    page = _page(COLUMNS, [["aaaaaaaaaa1", "2025-07-11 04:00:00.000000", "61234567", "false", None]])
    assert to_rows([page]) == [{"video_id": "aaaaaaaaaa1", "published_at": "2025-07-11T04:00:00Z",
                                "views_latest": 61234567, "comparable": False, "views_d7": None}]


def test_header_is_skipped_only_on_the_first_page():
    first = _page(COLUMNS, [["aaaaaaaaaa1", "2025-07-11 04:00:00.000000", "1", "true", "5"]])
    second = {"ResultSet": {"Rows": [{"Data": [{"VarCharValue": v} for v in
                                               ["bbbbbbbbbb1", "2025-10-13 09:00:00.000000", "2", "true", "6"]]}]}}
    assert [r["video_id"] for r in to_rows([first, second])] == ["aaaaaaaaaa1", "bbbbbbbbbb1"]


def _video(**overrides):
    video = {"video_id": "aaaaaaaaaa1", "artist": "twice", "market": "kr", "title": 'TWICE "THIS IS FOR" M/V',
             "published_at": "2025-07-11T04:00:00Z", "first_snapshot_date": "2026-11-25",
             "last_snapshot_date": "2026-11-25", "views_latest": 1, "comparable": False, "is_duplicate": False,
             "views_d1": None, "views_d7": None, "views_d28": None, "rank_d1": None, "rank_d7": None,
             "rank_d28": None, "compared_d1": None, "compared_d7": None, "compared_d28": None}
    return {**video, **overrides}


def test_export_carries_the_snapshot_date_and_artist_list():
    export = build_export("2026-11-26", load_artists(), [_video()], [])
    assert export["snapshot_date"] == "2026-11-26"
    assert export["first_snapshot_date"] == "2026-11-25"
    assert {"slug": "misamo", "name": "MISAMO", "kind": "unit", "parent": "twice"} in export["artists"]


def test_one_bad_row_stops_the_export():
    with pytest.raises(QualityGateError):
        build_export("2026-11-26", load_artists(), [_video(), _video(artist="unknown")], [])


def test_lastfm_rows_only_for_artists_still_tracked_there():
    rows = [{"artist": "twice", "listeners": 1}, {"artist": "triples-aaa", "listeners": 1}]
    export = build_export("2026-11-26", load_artists(), [_video()], rows)
    assert [r["artist"] for r in export["lastfm"]] == ["twice"]
