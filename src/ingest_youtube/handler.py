"""Daily snapshot of every music video's cumulative counters.

Quota per run (YouTube Data API v3, 10,000 units/day free): 1 unit per channel lookup,
1 per page of 50 uploads, 1 per batch of 50 videos. A full run costs well under 200 units.
"""

import os
import re

from common import storage
from common.http import get_json
from common.run import load_groups, publish, snapshot_date
from common.secrets import get_secret

API = "https://www.googleapis.com/youtube/v3"


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


def match_music_videos(pages: list[dict], groups: list[dict]) -> dict[str, str]:
    """Map video_id -> group slug for uploads whose title looks like an official MV."""
    patterns = [(g["slug"], re.compile(g["mv_title_pattern"], re.IGNORECASE)) for g in groups]
    matches = {}
    for page in pages:
        for item in page.get("items") or []:
            title = item["snippet"]["title"]
            video_id = item["snippet"]["resourceId"]["videoId"]
            for slug, pattern in patterns:
                if pattern.search(title):
                    matches[video_id] = slug
                    break
    return matches


def _int_or_none(value):
    return int(value) if value is not None else None


def to_records(video_pages: list[dict], groups_by_video: dict[str, str], day: str) -> list[dict]:
    records = []
    for page in video_pages:
        for item in page.get("items") or []:
            stats = item.get("statistics", {})
            records.append({
                "snapshot_date": day,
                "group": groups_by_video[item["id"]],
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
    config_groups = load_groups()
    earliest = os.environ.get("EARLIEST_MV_DATE", "2015-10-01")

    groups_by_video = {}
    for handle in sorted({g["youtube_handle"] for g in config_groups}):
        groups = [g for g in config_groups if g["youtube_handle"] == handle]
        playlist_id, channel = uploads_playlist(handle, key)
        pages = list_uploads(playlist_id, key, earliest)
        name = handle.lstrip("@").lower()
        storage.put_json(storage.raw_key("youtube", day, f"channel_{name}"), channel)
        storage.put_json(storage.raw_key("youtube", day, f"uploads_{name}"), pages)
        groups_by_video.update(match_music_videos(pages, groups))

    ids = sorted(groups_by_video)
    video_pages = [
        get_json(f"{API}/videos", {"part": "snippet,statistics", "id": ",".join(ids[i:i + 50]), "key": key})
        for i in range(0, len(ids), 50)
    ]
    storage.put_json(storage.raw_key("youtube", day, "videos"), video_pages)
    return publish("youtube_video_stats", "youtube_video_stats", to_records(video_pages, groups_by_video, day), day)
