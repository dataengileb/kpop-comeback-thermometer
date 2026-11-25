# RFP: Comeback Thermometer

## Client
The marketing team of a K-pop label's Mexican distributor, and the fan clubs they work with. They plan promotion (ads, listening parties, streaming drives) for the launch week of each comeback by TWICE, NMIXX and tripleS, in Korea and Japan, of their units (TWICE's MISAMO and tripleS's, from Acid Angel from Asia to msnz) and of the soloists NAYEON, JIHYO, CHAEYOUNG and TZUYU.

## Problem
Today the team judges a comeback by the total views shown on YouTube. Totals favour old videos, so a new release always looks weak next to a hit from 2019, and the team cannot tell on day 3 whether a launch is ahead of or behind the artist's usual pace.

## Question
How strong was the start of each comeback by these artists, compared with the same artist's previous comebacks in the same market?

## Decision it supports
Whether to add or pull promotion budget during the first four weeks after a release.

## Data available
| Source | What it provides | Update frequency | Access |
| --- | --- | --- | --- |
| YouTube Data API v3 | Cumulative views, likes and comments per music video | Live counters, read daily | Free API key, 10,000 units/day |
| Last.fm API | Cumulative listeners and scrobbles per artist and top track | Live counters, read daily | Free API key |
| MusicBrainz | Releases and their release dates | Community-edited | Open, 1 request/second |

None of these sources publishes history: they only return today's totals. Daily snapshots are the only way to see a launch curve.

## Acceptance criteria
1. For every music video released after the first snapshot, the site shows views at day 1, 7 and 28 after release.
2. Each new comeback is ranked against the same artist's earlier comebacks for the same market (Korea or Japan) that have the same day-N value.
3. Comebacks released before the first snapshot are shown with views-to-date and age only, labelled as not comparable.
4. The site shows the snapshot date and opens without any connection to AWS.
5. Re-running any day produces the same numbers.

## Constraints
Batch only, zero cost, AWS only, CloudFormation, public static site.

## Out of scope
Spotify (its API no longer returns popularity or followers to new apps), units and solo artists without an official MV on the configured channels, chart positions, and any prediction of future views.
