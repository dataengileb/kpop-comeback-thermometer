import pytest

from common.contracts import load_contract, split_valid
from common.run import load_artists, load_config
from ingest_youtube.handler import match_music_videos, to_records


def _artists_on(handle):
    return [a for a in load_artists() if handle in a["channels"]]


def test_only_official_mvs_of_configured_artists_match(fixture):
    matches = match_music_videos([fixture("youtube_uploads_page.json")], _artists_on("@JYPEntertainment"), "kr")
    assert matches == {
        "aaaaaaaaaa1": {"artist": "twice", "market": "kr"},
        "bbbbbbbbbb1": {"artist": "nmixx", "market": "kr"},
    }


# Titles seen on the configured channels in 2026-11. None means it must not match.
@pytest.mark.parametrize(
    "handle, title, expected",
    [
        ("@JYPEntertainment", "TWICE(트와이스) \"TT\" M/V", ("twice", "kr")),
        ("@JYPEntertainment", "TWICE “Strategy (feat. Megan Thee Stallion)” M/V", ("twice", "kr")),
        ("@JYPEntertainment", "NMIXX(엔믹스) “긴 소원 (Birthday Wish)” M/V", ("nmixx", "kr")),
        ("@JYPEntertainment", "NMIXX(엔믹스) “긴 소원 (Birthday Wish)” M/V Teaser", None),
        ("@JYPEntertainment", "NAYEON \"LOVE COUNTDOWN\" (Feat. Wonstein) M/V", ("nayeon", "kr")),
        ("@JYPEntertainment", "NAYEON “BABY ANGEL” M/V Teaser 1", None),
        ("@JYPEntertainment", "JIHYO \"Killin' Me Good\" M/V", ("jihyo", "kr")),
        ("@JYPEntertainment", "JIHYO \"Killin’ Me Good\" M/V Behind EP.01", None),
        ("@JYPEntertainment", "CHAEYOUNG “SHOOT (Firecracker)” M/V", ("chaeyoung", "kr")),
        ("@JYPEntertainment", "TZUYU \"Run Away\" M/V", ("tzuyu", "kr")),
        ("@JYPEntertainment", "TZUYU \"Run Away\" MV Reaction with TWICE", None),
        ("@JYPEntertainment", "MISAMO “Do not touch” M/V", ("misamo", "kr")),
        ("@JYPEntertainment", "CHAERYEONG “Lovesick” M/V", None),
        ("@twicejapan_official", "TWICE「Breakthrough」Music Video", ("twice", "jp")),
        ("@twicejapan_official", "TWICE 「Perfect World」 Music Video", ("twice", "jp")),
        ("@twicejapan_official", "MISAMO「Marshmallow」Music Video", ("misamo", "jp")),
        ("@twicejapan_official", "MISAMO「Do not touch」 Choreography Video", None),
        ("@twicejapan_official", "TWICE「DIVE」 Live Stage @Nissan Stadium", None),
        ("@nmixxjapan_official", "NMIXX 「N=MIXX」 Trailer", None),
        ("@triplescosmos", "tripleS(트리플에스) 'Andless’ Official MV", ("triples", "kr")),
        ("@triplescosmos", "tripleS(트리플에스) '깨어' (Are You Alive) Official MV", ("triples", "kr")),
        ("@triplescosmos", "tripleS 'Baby Flower' Japanese Ver. Official MV", ("triples", "jp")),
        ("@triplescosmos", "트리플에스(tripleS) 'Rising' MV", ("triples", "kr")),
        ("@triplescosmos", "tripleS(トリプルエス) ∞! ‘Password’ Official MV", ("triples-infinity", "jp")),
        ("@triplescosmos", "tripleS(트리플에스) Visionary Vision ‘Hit the Floor’ Official MV", ("triples-vv", "kr")),
        ("@triplescosmos", "tripleS(트리플에스) msnz moon 'Cameo Love' Official MV", ("triples-msnz-moon", "kr")),
        ("@triplescosmos", "tripleS(트리플에스) msnz zenith ‘Q&A’ Official MV", ("triples-msnz-zenith", "kr")),
        ("@triplescosmos", "tripleS(트리플에스) msnz zenith ‘Q&A’ Official Performance Video", None),
        ("@triplescosmos", "트리플에스(tripleS AAA) ‘Generation’ MV", ("triples-aaa", "kr")),
        ("@triplescosmos", "tripleS AAA Generation : M/V Ver.", None),
        ("@triplescosmos", "트리플에스(tripleS +(KR)ystal Eyes) ‘Cherry Talk’ MV", ("triples-kre", "kr")),
        ("@triplescosmos", "tripleS(트리플에스) +(KR)ystal Eyes ‘Touch+’ MV", ("triples-kre", "kr")),
        ("@triplescosmos", "tripleS(트리플에스) LOVElution ‘Girls' Capitalism’ MV", ("triples-lovelution", "kr")),
        ("@triplescosmos", "tripleS(트리플에스) EVOLution ‘Invincible’ MV", ("triples-evolution", "kr")),
        ("@triplescosmos", "tripleS(트리플에스) Aria ‘Door’ MV", ("triples-aria", "kr")),
        ("@triplescosmos", "tripleS Glow (트리플에스) '내적 댄스 (Inner Dance)' Official Performance", None),
    ],
)
def test_real_channel_titles(handle, title, expected):
    market = next(c["market"] for c in load_config()["channels"] if c["handle"] == handle)
    page = {"items": [{"snippet": {"title": title, "resourceId": {"videoId": "x" * 11}}}]}
    match = match_music_videos([page], _artists_on(handle), market).get("x" * 11)
    assert (None if match is None else (match["artist"], match["market"])) == expected


def test_listed_video_ids_match_even_when_the_title_does_not():
    title = 'TWICE Pre-release english track "MOONLIGHT SUNRISE" M/V'
    page = {"items": [{"snippet": {"title": title, "resourceId": {"videoId": "cKlEE_EYuNM"}}},
                      {"snippet": {"title": title + " Teaser 1", "resourceId": {"videoId": "2P997RmZRU4"}}}]}
    matches = match_music_videos([page], _artists_on("@JYPEntertainment"), "kr")
    assert matches == {"cKlEE_EYuNM": {"artist": "twice", "market": "kr"}}


def test_records_cast_counters_and_keep_hidden_likes_as_null(fixture):
    matches = {"aaaaaaaaaa1": {"artist": "twice", "market": "kr"}, "bbbbbbbbbb1": {"artist": "nmixx", "market": "kr"}}
    records = to_records([fixture("youtube_videos_page.json")], matches, "2026-11-24")
    assert records[0]["view_count"] == 61234567
    assert records[1]["like_count"] is None
    valid, invalid = split_valid(records, load_contract("youtube_video_stats"))
    assert len(valid) == 2 and invalid == []
