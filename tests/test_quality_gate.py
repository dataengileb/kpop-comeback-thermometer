from datetime import datetime, timezone

import pytest

from common import run


@pytest.fixture
def written(monkeypatch):
    calls = {}
    monkeypatch.setattr(run.storage, "put_jsonl", lambda key, rows: calls.__setitem__(key, rows))
    monkeypatch.setenv("MAX_INVALID_RATIO", "0.25")
    return calls


def _record(views):
    return {"snapshot_date": "2026-11-24", "artist": "twice", "listeners": 1, "playcount": views}


def test_same_day_always_writes_the_same_keys(written):
    run.publish("lastfm_artist_stats", "lastfm_artist_stats", [_record(1)], "2026-11-24")
    run.publish("lastfm_artist_stats", "lastfm_artist_stats", [_record(1)], "2026-11-24")
    assert sorted(written) == [
        "quarantine/lastfm_artist_stats/snapshot_date=2026-11-24/part-0000.jsonl",
        "validated/lastfm_artist_stats/snapshot_date=2026-11-24/part-0000.jsonl",
    ]


def test_gate_stops_the_run_when_too_many_records_break_the_contract(written):
    with pytest.raises(run.QualityGateError):
        run.publish("lastfm_artist_stats", "lastfm_artist_stats", [_record(1), _record("x")], "2026-11-24")
    # The bad rows are kept for diagnosis, but nothing reaches validated/ for that day.
    assert list(written) == ["quarantine/lastfm_artist_stats/snapshot_date=2026-11-24/part-0000.jsonl"]


def test_gate_stops_the_run_on_an_empty_source(written):
    with pytest.raises(run.QualityGateError):
        run.publish("lastfm_artist_stats", "lastfm_artist_stats", [], "2026-11-24")


def test_snapshot_date_is_today_in_utc():
    today = datetime.now(timezone.utc).date().isoformat()
    assert run.snapshot_date({}) == today
    assert run.snapshot_date({"snapshot_date": today}) == today


def test_a_past_snapshot_date_is_rejected():
    with pytest.raises(ValueError, match="cannot be re-taken"):
        run.snapshot_date({"snapshot_date": "2026-11-01"})
