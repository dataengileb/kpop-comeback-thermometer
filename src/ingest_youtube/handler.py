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
# Teasers, dance practices and sub-unit videos (tripleS(トリプルエス) ∞! ‘...’) do not match.
MV_TITLE = (
    r"^{name}\s*(\([^)]*\))?\s*"            # artist, optional native-script name
    r"[\"“'‘「『].+[\"”'’」』]\s*"           # quoted song title
    r"(\([^)]*\)\s*)?"                     # optional (Feat. ...) or English title
    r"(-?\s*Japanese\s+Ver\.?\s*-?\s*)?"    # optional Japanese version tag
    r"(Official\s+)?(M/?V|Music\s+Video)\s*$"
)
JAPANESE_TITLE = re.compile(r"Japanese\s+Ver|[「『]|[\u3040-\u30ff]", re.IGNORECASE)


def mv_pattern(name: str) -> re.Pattern:
    return re.compile(MV_TITLE.format(name=re.escape(name)), re.IGNORECASE)


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


def match_music_videos(pages: list[dict], artists: list[dict], channel_market: str) -> dict[str, dict]:
    """Map video_id -> {artist, market} for uploads whose title looks like an official MV."""
    patterns = [(a["slug"], mv_pattern(a["name"])) for a in artists]
    matches = {}
    for page in pages:
        for item in page.get("items") or []:
            title = item["snippet"]["title"]
            video_id = item["snippet"]["resourceId"]["videoId"]
            for slug, pattern in patterns:
                if pattern.search(title):
                    matches[video_id] = {"artist": slug, "market": market_of(title, channel_market)}
                    break
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
        matches.update(match_music_videos(pages, artists, channel["market"]))

    ids = sorted(matches)
    video_pages = [
        get_json(f"{API}/videos", {"part": "snippet,statistics", "id": ",".join(ids[i:i + 50]), "key": key})
        for i in range(0, len(ids), 50)
    ]
    storage.put_json(storage.raw_key("youtube", day, "videos"), video_pages)
    return publish("youtube_video_stats", "youtube_video_stats", to_records(video_pages, matches, day), day)
