from common.contracts import load_contract, split_valid
from ingest_musicbrainz.handler import to_records


def test_partial_release_dates_are_quarantined(fixture):
    records = to_records([fixture("musicbrainz_release_groups.json")], "twice", "2026-11-24")
    valid, invalid = split_valid(records, load_contract("musicbrainz_release"))
    assert len(valid) == 2
    assert invalid[0]["record"]["title"] == "Unknown single"
