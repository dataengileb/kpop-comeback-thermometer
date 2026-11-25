# Extending the Comeback Thermometer

Three common changes, what each one touches, and what it leaves alone. Every change starts in [`src/config/artists.json`](../src/config/artists.json); the tests then say what else must follow.

## Which layers a change touches

| Change | Config | Contracts | Tests | Lambda code | Template | Gold SQL | Site |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Add an artist | ✓ | ✓ enum | ✓ titles | — | — | — | — |
| Add a video category | ✓ | ✓ enums | ✓ titles | — | — | — | label only |
| Add a YouTube-only metric | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Gold is always rebuilt from silver, and the site takes its artist list from the export, so the first two changes need no SQL and no HTML.

## 1. Add an artist (for example ITZY or aespa)

1. **Look at real titles first.** Open the channel and copy five MV titles and five near misses (teasers, dance practices, performance videos). Each label writes titles its own way:
   - JYP: `ITZY "GOLD" M/V`. This matches the default pattern.
   - SM: `aespa 에스파 'Supernova' MV`. The Korean name follows a space instead of sitting in parentheses, so list both forms in `title_names`: `["aespa 에스파", "aespa"]`.
2. **Add the channel** to `channels` if it is new (`@SMTOWN`, `"market": "kr"`). ITZY shares `@JYPEntertainment`, so it needs no new channel.
3. **Add the artist** to `artists`:
   ```json
   {"slug": "itzy", "name": "ITZY", "kind": "group", "parent": null, "lastfm_name": "ITZY",
    "musicbrainz_id": "<id>", "channels": ["@JYPEntertainment"]}
   ```
   - Find the MusicBrainz id at `https://musicbrainz.org/ws/2/artist?query=artist:ITZY&fmt=json`, and check its relations before pinning it: names are often shared.
   - Set `lastfm_name` to `null` if Last.fm credits the artist's plays to someone else, as it does for tripleS's units.
   - For a unit or a soloist, set `kind` and `parent`. Set `"titled_under_parent": true` when the titles read `<group> <unit> '<song>'`.
4. **Run `pytest`.** `test_contract_artist_enum_matches_config` fails and names the contracts that need the new slug in their `artist` enum. Add it to each one.
5. **Add the real titles** from step 1 to `test_real_channel_titles`, with the result you expect, near misses included.
6. **Deploy.** The next daily run picks the artist up.

**What it affects**
- **YouTube quota:** one more channel adds one unit, plus one unit per 50 uploads walked back to 2015. A label channel with thousands of uploads adds about 100 units, well inside 10,000.
- **Run time:** MusicBrainz adds about two seconds per artist (one request per second).
- **History:** there is no backfill. Every MV released before the day you add the artist is "not comparable", and its first ranked launch is its next release.

**What it doesn't affect**
- No Lambda code, template, gold SQL or site file changes.
- Existing artists' numbers and ranks stay the same, because ranks never cross artists.

## 2. Add a video category (for example dance practices)

Video types live in `video_types`. A title matches a type when it ends with the type's `suffix`. `compare_with` decides which videos are ranked against each other.

```json
{"type": "dance_practice", "suffix": "Dance\\s+Practice(?:\\s+Video)?", "compare_with": "dance_practice"}
```

1. Add the entry. Types are tried in order, and the first match wins.
2. Run `pytest`. `test_youtube_contract_knows_every_video_type` names the enums to update in `youtube_video_stats.json` and `site_video.json`.
3. Add real titles to the tests, such as `NMIXX "Blue Valentine" Dance Practice`. Variants such as `Dance Practice (Fix ver.)` don't match this suffix. Extend it (`Dance\\s+Practice(?:\\s+Video)?(?:\\s*\\([^)]*\\))?`) if you want them too.
4. Give the type a label in `site/app.js`, next to `visual_clip`, so the page doesn't show the raw type name.
5. Deploy.

**Choosing `compare_with`**
- Use a new group, as above, to rank dance practices only against dance practices.
- Use `"release"` only for a video that stands in for the release's MV. That is why msnz's 2026 "Special Visual Clip" videos are `release`: those singles have no MV.

**What it affects**
- More matched videos means more `videos.list` batches: one quota unit per 50 videos.
- Duplicate detection runs per type, so a song's MV and its dance practice are never treated as copies of each other.

## 3. Add a YouTube-only metric (for example likes per 1,000 views)

Last.fm has nothing like this, so the change only touches the YouTube path. `like_count` and `comment_count` are already collected and kept in gold as `likes_latest` and `comments_latest`. Start from those before you collect anything new.

1. **Collect it** (skip if already collected). Add the field in `to_records` in [`src/ingest_youtube/handler.py`](../src/ingest_youtube/handler.py).
   - Statistics come from `part=statistics`. Duration or definition need `part=contentDetails` added to the `videos.list` call, which still costs one quota unit per call.
   - Channel subscribers come from `channels.list`. That is a new table, not a new column.
2. **Contract and silver.** Add the property to `youtube_video_stats.json`, optional if old snapshots won't have it, and add the column to `SilverYouTube` in the template.
3. **Gold.** Add the column to `GoldVideoLaunch` and to the `MERGE` in `BuildVideoLaunch`. `test_template.py` fails until the column lists agree.
   - CloudFormation writes an Iceberg schema only when it creates the table. Either run `ALTER TABLE gold_video_launch ADD COLUMNS (...)` once in Athena, or give the table a new name, as [ADR 4](adr/0004-gold-iceberg-tables-rebuilt-with-merge.md) explains. Gold is rebuilt from silver, so the new name loses nothing.
4. **Export and site.** Add it to `VIDEOS_SQL` in [`src/export_site/handler.py`](../src/export_site/handler.py), to `site_video.json`, and to the page.
5. **Deploy, run once by hand, and check `quarantine/`** before you trust the new numbers.

**Be careful with ratios.** Likes per view at day 7 is comparable across launches. Likes per view to date is not, for the same reason lifetime views are not.

## Before you merge

`pytest` and `cfn-lint` pass. Then deploy, start one run by hand, and check that nothing unexpected landed in `quarantine/`. Finally, run `./scripts/fetch_export.sh` and open `site/` locally (`python3 -m http.server --directory site`) to see the change.
