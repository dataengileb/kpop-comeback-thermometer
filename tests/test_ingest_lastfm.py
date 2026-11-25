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


def test_unknown_artist_is_skipped_not_fatal(fixture, monkeypatch):
    from ingest_lastfm import handler

    known = {"artist.getinfo": fixture("lastfm_artist_getinfo.json"), "artist.gettoptracks": fixture("lastfm_toptracks.json")}

    def fake_get_json(url, params):
        if params["artist"] == "+(KR)ystal Eyes":
            return {"error": 6, "message": "The artist you supplied could not be found"}
        return known[params["method"]]

    monkeypatch.setattr(handler, "get_json", fake_get_json)
    monkeypatch.setattr(handler, "get_secret", lambda name: "key")
    monkeypatch.setattr(handler.storage, "put_json", lambda key, payload: None)
    monkeypatch.setattr(handler, "publish", lambda table, contract, rows, day: {"table": table, "rows": len(rows)})
    monkeypatch.setattr(handler, "load_artists", lambda: [
        {"slug": "twice", "lastfm_name": "TWICE"},
        {"slug": "triples-kre", "lastfm_name": "+(KR)ystal Eyes"},
        {"slug": "triples-aria", "lastfm_name": None},
    ])
    monkeypatch.setenv("LASTFM_KEY_PARAM", "/x")

    result = handler.lambda_handler({}, None)
    assert result["not_found"] == ["triples-kre"]
    assert result["tables"][0] == {"table": "lastfm_artist_stats", "rows": 1}
