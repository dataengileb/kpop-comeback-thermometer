"""Daily snapshot of every music video's cumulative counters.

Quota per run (YouTube Data API v3, 10,000 units/day free): 1 unit per channel lookup,
1 per page of 50 uploads, 1 per batch of 50 videos. A full run costs a few hundred units.
"""

import os
import re

from common import storage
from common.http import get_json
from common.run import load_config, publish, snapshot_date
from common.secrets import get_secret

API = "https://www.googleapis.com/youtube/v3"

# Official MV titles on the label channels, for example:
#   TWICE "THIS IS FOR" M/V
#   TWICE「Fanfare」Music Video
#   NMIXX(엔믹스) “긴 소원 (Birthday Wish)” M/V
#   NAYEON "LOVE COUNTDOWN" (Feat. Wonstein) M/V
#   tripleS(트리플에스) '깨어' (Are You Alive) Official MV
#   tripleS 'Baby Flower' Japanese Ver. Official MV
#   트리플에스(tripleS) 'Rising' MV
#   tripleS(트리플에스) msnz moon 'Cameo Love' Official MV      (unit titled under its group)
#   트리플에스(tripleS AAA) ‘Generation’ MV                      (same, native name first)
#   tripleS(트리플에스) sun ‘DNA’ Special Visual Clip           (video type "visual_clip")
# The ending ({suffix}) comes from the video types in config/artists.json. Teasers, dance
# practices and performance videos match no type. A unit's video never matches its group,
# because the unit name sits between the group name and the song title.
VIDEO_TITLE = (
    r"^{artist}\s*"                         # artist as written in titles, see title_prefix()
    r"[\"“'‘「『].+[\"”'’」』]\s*"           # quoted song title
    r"(\([^)]*\)\s*)?"                     # optional (Feat. ...) or English title
    r"(-?\s*Japanese\s+Ver\.?\s*-?\s*)?"    # optional Japanese version tag
    r"(?:{suffix})\s*$"
)
JAPANESE_TITLE = re.compile(r"Japanese\s+Ver|[「『]|[\u3040-\u30ff]", re.IGNORECASE)


def _literal(name: str) -> str:
    return re.escape(name).replace(r"\ ", r"\s+")


def title_prefix(artist: dict, parent: dict | None) -> str:
    """How the artist appears at the start of a title: 'NMIXX(엔믹스)', '트리플에스(tripleS)',
    or for a unit titled under its group, 'tripleS(트리플에스) msnz moon' / '트리플에스(tripleS AAA)'."""
    names = "|".join(_literal(n) for n in artist.get("title_names") or [artist["name"]])
    if artist.get("titled_under_parent"):
        group = _literal(parent["name"])
        return rf"(?:{group}(?:\s*\([^)]*\))?\s+(?:{names})|[^\s(]+\s*\({group}\s+(?:{names})\))"
    return rf"(?:(?:{names})(?:\s*\([^)]*\))?|[^\s(]+\s*\((?:{names})\))"


def video_pattern(artist: dict, parent: dict | None, suffix: str) -> re.Pattern:
    return re.compile(VIDEO_TITLE.format(artist=title_prefix(artist, parent), suffix=suffix), re.IGNORECASE)


def market_of(title: str, channel_market: str) -> str:
    """'jp' for videos on a Japan channel or with a Japanese title; 'kr' otherwise."""
    return "jp" if channel_market == "jp" or JAPANESE_TITLE.search(title) else "kr"


def uploads_playlist(handle: str, key: str) -> tuple[str, dict]:
    payload = get_json(f"{API}/channels", {"part": "contentDetails", "forHandle": handle, "key": key})
    items = payload.get("items") or []
    if not items:
        raise ValueError(f"YouTube handle not found: {handle}")
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"], payload


def list_uploads(playlist_id: str, key: str, earliest: str) -> list[dict]:
    """Walk the uploads playlist (newest first) until videos are older than `earliest`."""
    pages, token = [], None
    while True:
        params = {"part": "snippet", "playlistId": playlist_id, "maxResults": 50, "key": key}
        if token:
            params["pageToken"] = token
        page = get_json(f"{API}/playlistItems", params)
        pages.append(page)
        items = page.get("items") or []
        token = page.get("nextPageToken")
        if not token or not items or items[-1]["snippet"]["publishedAt"][:10] < earliest:
            return pages


def match_videos(pages: list[dict], artists: list[dict], channel_market: str,
                 video_types: list[dict], all_artists: list[dict] | None = None) -> dict[str, dict]:
    """Map video_id -> {artist, market, video_type, compare_with} for uploads whose title matches
    an artist and a video type, or that an artist lists in extra_mv_ids (type "mv")."""
    by_slug = {a["slug"]: a for a in all_artists or artists}
    patterns = [
        (a["slug"], vt, video_pattern(a, by_slug.get(a["parent"]), vt["suffix"]))
        for vt in video_types
        for a in artists
    ]
    mv = next(vt for vt in video_types if vt["type"] == "mv")
    extras = {vid: a["slug"] for a in artists for vid in a.get("extra_mv_ids", [])}
    matches = {}
    for page in pages:
        for item in page.get("items") or []:
            title = item["snippet"]["title"]
            video_id = item["snippet"]["resourceId"]["videoId"]
            if video_id in extras:
                slug, vt = extras[video_id], mv
            else:
                slug, vt = next(((s, v) for s, v, p in patterns if p.search(title)), (None, None))
            if slug:
                matches[video_id] = {"artist": slug, "market": market_of(title, channel_market),
                                     "video_type": vt["type"], "compare_with": vt["compare_with"]}
    return matches


def _int_or_none(value):
    return int(value) if value is not None else None


def to_records(video_pages: list[dict], matches: dict[str, dict], day: str) -> list[dict]:
    records = []
    for page in video_pages:
        for item in page.get("items") or []:
            stats = item.get("statistics", {})
            records.append({
                "snapshot_date": day,
                **matches[item["id"]],
                "video_id": item["id"],
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"],
                # The API returns counters as strings; likes and comments can be hidden by the owner.
                "view_count": _int_or_none(stats.get("viewCount")),
                "like_count": _int_or_none(stats.get("likeCount")),
                "comment_count": _int_or_none(stats.get("commentCount")),
            })
    return records


def lambda_handler(event, context):
    day = snapshot_date(event)
    key = get_secret(os.environ["YOUTUBE_KEY_PARAM"])
    config = load_config()
    earliest = os.environ.get("EARLIEST_MV_DATE", "2015-10-01")

    matches = {}
    for channel in config["channels"]:
        handle = channel["handle"]
        artists = [a for a in config["artists"] if handle in a["channels"]]
        playlist_id, payload = uploads_playlist(handle, key)
        pages = list_uploads(playlist_id, key, earliest)
        name = handle.lstrip("@").lower()
        storage.put_json(storage.raw_key("youtube", day, f"channel_{name}"), payload)
        storage.put_json(storage.raw_key("youtube", day, f"uploads_{name}"), pages)
        matches.update(match_videos(pages, artists, channel["market"], config["video_types"], config["artists"]))

    ids = sorted(matches)
    video_pages = [
        get_json(f"{API}/videos", {"part": "snippet,statistics", "id": ",".join(ids[i:i + 50]), "key": key})
        for i in range(0, len(ids), 50)
    ]
    storage.put_json(storage.raw_key("youtube", day, "videos"), video_pages)
    return publish("youtube_video_stats", "youtube_video_stats", to_records(video_pages, matches, day), day)
