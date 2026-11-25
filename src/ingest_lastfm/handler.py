"""Daily snapshot of cumulative Last.fm listeners and scrobbles per artist and per top track."""

import json
import os

from common import storage
from common.http import get_json
from common.run import load_artists, publish, snapshot_date
from common.secrets import get_secret

API = "https://ws.audioscrobbler.com/2.0/"
ARTIST_NOT_FOUND = 6  # https://www.last.fm/api/errorcodes


def _call(method: str, artist: str, key: str, **extra) -> dict | None:
    """None when Last.fm does not know the artist; any other API error stops the run."""
    payload = get_json(API, {"method": method, "artist": artist, "api_key": key, "format": "json", **extra})
    if payload.get("error") == ARTIST_NOT_FOUND:
        return None
    if "error" in payload:
        raise RuntimeError(f"Last.fm {method} failed for {artist}: {payload.get('message')}")
    return payload


def _to_int(value):
    """Last.fm sends numbers as strings. Leave anything unparseable as-is so the contract catches it."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def artist_record(info: dict, slug: str, day: str) -> dict:
    artist = info["artist"]
    return {
        "snapshot_date": day,
        "artist": slug,
        "artist_mbid": artist.get("mbid") or None,
        "listeners": _to_int(artist.get("stats", {}).get("listeners")),
        "playcount": _to_int(artist.get("stats", {}).get("playcount")),
    }


def track_records(top: dict, slug: str, day: str) -> list[dict]:
    return [
        {
            "snapshot_date": day,
            "artist": slug,
            "track": track.get("name"),
            "track_mbid": track.get("mbid") or None,
            "rank": _to_int(track.get("@attr", {}).get("rank")),
            "listeners": _to_int(track.get("listeners")),
            "playcount": _to_int(track.get("playcount")),
        }
        for track in top.get("toptracks", {}).get("track", [])
    ]


def lambda_handler(event, context):
    day = snapshot_date(event)
    key = get_secret(os.environ["LASTFM_KEY_PARAM"])
    artists, tracks, not_found = [], [], []
    # Units with generic names (Aria, Sun, Moon...) have lastfm_name null: Last.fm would
    # return a different artist with the same name.
    for artist in (a for a in load_artists() if a["lastfm_name"]):
        info = _call("artist.getinfo", artist["lastfm_name"], key)
        if info is None:
            # Logged and returned, not fatal: one unknown unit must not cost the day's snapshot.
            print(json.dumps({"lastfm_artist_not_found": artist["lastfm_name"]}))
            not_found.append(artist["slug"])
            continue
        top = _call("artist.gettoptracks", artist["lastfm_name"], key, limit=50)
        storage.put_json(storage.raw_key("lastfm", day, f"artist_{artist['slug']}"), info)
        storage.put_json(storage.raw_key("lastfm", day, f"toptracks_{artist['slug']}"), top)
        artists.append(artist_record(info, artist["slug"], day))
        tracks.extend(track_records(top, artist["slug"], day))
    return {
        "tables": [
            publish("lastfm_artist_stats", "lastfm_artist_stats", artists, day),
            publish("lastfm_track_stats", "lastfm_track_stats", tracks, day),
        ],
        "not_found": not_found,
    }
