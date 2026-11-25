"""Discography and release dates. MusicBrainz asks for at most 1 request per second and a
descriptive User-Agent: https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting
"""

import time

from common import storage
from common.http import get_json
from common.run import load_groups, publish, snapshot_date

API = "https://musicbrainz.org/ws/2"
RELEASE_TYPES = "album|ep|single"


def _get(path: str, params: dict) -> dict:
    time.sleep(1.1)
    return get_json(f"{API}/{path}", {**params, "fmt": "json"})


def resolve_artist_id(group: dict) -> str:
    """Use the pinned MBID when the config has one; otherwise take the exact-name Korean group."""
    if group.get("musicbrainz_id"):
        return group["musicbrainz_id"]
    result = _get("artist", {"query": f'artist:"{group["name"]}" AND type:group AND country:KR', "limit": 5})
    for artist in result.get("artists", []):
        if artist["name"].casefold() == group["name"].casefold():
            return artist["id"]
    raise ValueError(f"MusicBrainz artist not found: {group['name']}")


def browse_release_groups(artist_id: str) -> list[dict]:
    pages, offset = [], 0
    while True:
        page = _get("release-group", {"artist": artist_id, "type": RELEASE_TYPES, "limit": 100, "offset": offset})
        pages.append(page)
        offset += len(page.get("release-groups", []))
        if offset >= page.get("release-group-count", 0) or not page.get("release-groups"):
            return pages


def to_records(pages: list[dict], slug: str, day: str) -> list[dict]:
    return [
        {
            "snapshot_date": day,
            "group": slug,
            "release_group_id": rg["id"],
            "title": rg["title"],
            "primary_type": rg.get("primary-type"),
            "secondary_types": rg.get("secondary-types", []),
            # Partial dates such as "2016" fail the contract on purpose: they cannot anchor day 0.
            "first_release_date": rg.get("first-release-date") or None,
        }
        for page in pages
        for rg in page.get("release-groups", [])
    ]


def lambda_handler(event, context):
    day = snapshot_date(event)
    records = []
    for group in load_groups():
        artist_id = resolve_artist_id(group)
        pages = browse_release_groups(artist_id)
        storage.put_json(storage.raw_key("musicbrainz", day, f"release_groups_{group['slug']}"), pages)
        records.extend(to_records(pages, group["slug"], day))
    return publish("musicbrainz_release", "musicbrainz_release", records, day)
