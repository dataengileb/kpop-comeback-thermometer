from common.contracts import load_contract, split_valid
from ingest_lastfm.handler import artist_record, track_records


def test_artist_record_casts_strings_and_blanks_mbid(fixture):
    record = artist_record(fixture("lastfm_artist_getinfo.json"), "twice", "2026-11-24")
    assert record == {"snapshot_date": "2026-11-24", "artist": "twice", "artist_mbid": None,
                      "listeners": 1480312, "playcount": 198765432}
    assert split_valid([record], load_contract("lastfm_artist_stats"))[1] == []


def test_unparseable_counter_goes_to_quarantine(fixture):
    records = track_records(fixture("lastfm_toptracks.json"), "twice", "2026-11-24")
    valid, invalid = split_valid(records, load_contract("lastfm_track_stats"))
    assert [r["track"] for r in valid] == ["FANCY"]
    assert invalid[0]["errors"] == ["playcount: expected integer, got str"]
