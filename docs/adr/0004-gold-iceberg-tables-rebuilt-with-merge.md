# 4. Gold layer: Iceberg tables in Athena, rebuilt with MERGE

**Status:** accepted · 2026-11

## Context
The RFP asks for views at day 1, 7 and 28 per music video, ranked within the same artist and market. That needs every daily snapshot of a video at once, and re-running a day must give the same numbers. The pipeline may only use AWS services, with no dbt or DuckDB.

## Decision
- **Silver:** Glue tables over `validated/`. Partition projection on `snapshot_date` means no crawler and no `MSCK REPAIR`.
- **Gold:** two Iceberg tables created by CloudFormation: `gold_video_launch` (one row per video) and `gold_artist_daily` (Last.fm per artist and day).
- **Daily build:** after ingestion, Step Functions runs one Athena `MERGE` per table. Each `MERGE` recomputes from all of silver and updates by key. It is followed by data checks (a failed check emails the alert) and a `VACUUM` that expires old Iceberg snapshots.
- **Definitions** in `gold_video_launch`:
  - **Day N:** the snapshot taken N days after the publish date (UTC). If that day is missing, N+1 is used, then N−1.
  - **Comparable:** the video has a snapshot at most one day after release. Only comparable videos get day-N values.
  - **Duplicate:** the same song uploaded twice by the same artist for the same market, as the same video type. The most viewed copy is kept; the other is flagged and never ranked.
  - **Rank:** among the artist's comparable originals for the same market and comparison group (`compare_with` in `src/config/artists.json`: an MV and a visual clip are both a `release`), with `compared_dN` giving how many there are.

## Consequences
- Re-running a day changes nothing: `MERGE` produces the same rows from the same silver.
- **Billed cost is not exactly zero.** Athena bills USD 5 per TB, with a 10 MB minimum per query. Five queries a day add up to about 1.5 GB billed a month: about USD 0.01 a month, all of it Athena, covered by free-tier credits, so the out-of-pocket cost is zero. The budget counts credits, so its alert fires only on real spend.
- Step Functions checks each Athena query about once a minute, so a run takes about 5 minutes. Standard workflows bill per state transition, so this costs nothing.
- CloudFormation writes the Iceberg schema only on creation. To add a column, use `ALTER TABLE ... ADD COLUMNS` or give the table a new name. Gold is rebuilt from silver, so a new name costs nothing: that is how `gold_mv_launch` became `gold_video_launch` when video types were added.
- A video deleted from YouTube stays in gold with its last known numbers.

## Alternatives considered
- **CTAS into a new table every day:** Athena has no atomic swap, so readers could see a missing table, and old data would pile up in S3.
- **Glue ETL (Spark) job:** billed per DPU-minute with a one-minute minimum, so it costs more than Athena for a few MB.
