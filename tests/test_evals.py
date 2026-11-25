import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "evals"))

import run as evals  # noqa: E402

ROWS = evals.load_golden()
CONFIG = evals.load_config()


def test_matcher_agrees_with_every_labeled_golden_row():
    result = evals.score(ROWS, evals.predict(ROWS, CONFIG))
    assert result["errors"] == []


def test_golden_rows_are_well_formed():
    slugs = {a["slug"] for a in CONFIG["artists"]}
    types = {t["type"] for t in CONFIG["video_types"]}
    channels = {c["handle"] for c in CONFIG["channels"]}
    assert len({r["video_id"] for r in ROWS}) == len(ROWS)
    for r in ROWS:
        assert r["status"] in {"labeled", "needs_review"}
        assert r["channel"] in channels and r["title"] and r["note"]
        if r["expected"]:
            assert r["expected"]["artist"] in slugs
            assert r["expected"]["market"] in {"kr", "jp"}
            assert r["expected"]["video_type"] in types


def test_golden_set_has_hard_negatives_for_tracked_artists():
    teasers = [r for r in ROWS if r["expected"] is None and r["note"] == "teaser"]
    assert len(teasers) >= 50
    assert any("TWICE" in r["title"] for r in teasers)


def test_score_counts_misses_false_launches_and_wrong_fields():
    launch = {"artist": "twice", "market": "kr", "video_type": "mv"}
    rows = [
        {"video_id": "a", "status": "labeled", "expected": launch},
        {"video_id": "b", "status": "labeled", "expected": None},
        {"video_id": "c", "status": "labeled", "expected": launch},
        {"video_id": "d", "status": "needs_review", "expected": None},
    ]
    predictions = {"a": None, "b": launch, "c": {**launch, "market": "jp"}, "d": launch}
    result = evals.score(rows, predictions)
    assert result["counts"] == {"fn": 1, "fp": 1, "tp": 1, "wrong_fields": 1}
    assert [kind for kind, _, _ in result["errors"]] == ["missed", "false launch", "wrong market"]


def test_review_candidates_skips_known_uploads(tmp_path, capsys):
    known = ROWS[0]
    for channel in CONFIG["channels"]:
        items = []
        if channel["handle"] == known["channel"]:
            items = [{"snippet": {"title": known["title"], "publishedAt": "2026-01-01T00:00:00Z",
                                  "resourceId": {"videoId": known["video_id"]}}},
                     {"snippet": {"title": 'TWICE "NEW SONG" M/V', "publishedAt": "2026-12-01T00:00:00Z",
                                  "resourceId": {"videoId": "new-video"}}}]
        name = channel["handle"].lstrip("@").lower()
        (tmp_path / f"uploads_{name}.json").write_text(json.dumps([{"items": items}]))
    evals.review_candidates(tmp_path)
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [line["video_id"] for line in lines] == ["new-video"]
    assert lines[0]["status"] == "needs_review"
