# 3. Daily snapshots of cumulative counters

**Status:** accepted · 2026-11

## Context
YouTube and Last.fm only return totals as of now. The question in the RFP is about the shape of the first weeks after a release, which no source publishes.

## Decision
Snapshot every counter once a day and keep each snapshot. "Views at day N" for a video is read from the snapshot taken N days after its publish time. Every file is keyed by `snapshot_date`, so re-running on the same day overwrites that day instead of adding rows. A run only accepts today's UTC date: the APIs return current totals, so taking a past day again would store today's numbers under the wrong date.

## Consequences
- The data only starts on the first run. Comebacks released earlier cannot be ranked (RFP criterion 3).
- A missed day leaves a gap that cannot be filled later. Day-N values use the nearest snapshot within one day and are blank otherwise.
- Storage grows by a few hundred KB per day, far below the S3 free tier.

## Alternative considered
Store only the latest totals and compare views per day since release. Rejected: it rewards old videos with long tails and cannot show the launch week.
