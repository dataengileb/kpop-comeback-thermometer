import pytest

from common.contracts import load_contract, split_valid
from common.run import load_groups
from ingest_youtube.handler import match_music_videos, to_records


def test_only_official_mvs_of_configured_groups_match(fixture):
    groups = [g for g in load_groups() if g["youtube_handle"] == "@JYPEntertainment"]
    matches = match_music_videos([fixture("youtube_uploads_page.json")], groups)
    assert matches == {"aaaaaaaaaa1": "twice", "bbbbbbbbbb1": "nmixx"}


# Title formats seen on the official channels (2026-11), including the Korean-name suffix.
@pytest.mark.parametrize(
    "title, expected",
    [
        ("NMIXX(엔믹스) “긴 소원 (Birthday Wish)” M/V", "nmixx"),
        ("NMIXX(엔믹스) “긴 소원 (Birthday Wish)” M/V Teaser", None),
        ("TWICE(트와이스) \"TT\" M/V", "twice"),
        ("NAYEON “BABY ANGEL” M/V", None),
        ("tripleS(트리플에스) 'Andless’ Official MV", "triples"),
    ],
)
def test_real_channel_titles(title, expected):
    page = {"items": [{"snippet": {"title": title, "resourceId": {"videoId": "x" * 11}}}]}
    assert match_music_videos([page], load_groups()).get("x" * 11) == expected


def test_records_cast_counters_and_keep_hidden_likes_as_null(fixture):
    records = to_records([fixture("youtube_videos_page.json")], {"aaaaaaaaaa1": "twice", "bbbbbbbbbb1": "nmixx"}, "2026-11-24")
    assert records[0]["view_count"] == 61234567
    assert records[1]["like_count"] is None
    valid, invalid = split_valid(records, load_contract("youtube_video_stats"))
    assert len(valid) == 2 and invalid == []
