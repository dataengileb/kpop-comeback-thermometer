# RFP: Comeback Thermometer

## Client
The marketing team of Lumen Music MX, a K-pop distributor in Mexico. Lumen is fictional, created for teaching. For every comeback the team pays for ads, listening parties and streaming drives with partner fan clubs, and nearly all of that money is spent in the first four weeks after release. The team's two analysts and the brand managers for each artist will use the result. The artists are TWICE, NMIXX and tripleS, including their units and soloists (MISAMO, NAYEON, JIHYO, CHAEYOUNG, TZUYU and tripleS's eleven units), each judged against itself, in Korea and in Japan.

## Problem
The team judges a launch by the view count YouTube shows, and that number is a lifetime total. In November 2026, NAYEON's "BABY ANGEL" showed 15 million views five days after release, next to 958 million for TWICE's "What is Love?" from 2018. Side by side, every new release looks weak, and on day 3 nobody can say whether a launch is ahead of or behind the artist's usual pace. Budget is added or cut on gut feeling.

## Question
How strong is each new TWICE, NMIXX or tripleS launch at day 1, 7 and 28, compared with the same artist's earlier launches in the same market?

## Decision it supports
Whether to add or pull promotion budget for a release during its first four weeks, depending on whether it is ahead of or behind the same artist's earlier launches at the same day.

## Data available
| Source | What it provides | Update frequency | Access (API, file, scraping, synthetic) |
| --- | --- | --- | --- |
| YouTube Data API v3 | Views, likes and comments per music video, as lifetime totals | Live counters, read once a day | API, free key, 10,000 quota units a day |
| Last.fm API | Listeners and scrobbles per artist and top track, as lifetime totals | Live counters, read once a day | API, free key |
| MusicBrainz API | Releases and their release dates | Community-edited | API, open, 1 request per second |

None of them publishes history, so a launch curve exists only if someone records the counters every day. Spotify is out: since February 2026 its API no longer returns popularity or follower counts to new apps.

## Acceptance criteria
1. For every music video released on or after the first snapshot date, the site shows its YouTube views at day 1, 7 and 28 after release, or how many days remain until each.
2. Each of those values shows its rank among the same artist's launches in the same market that have that day's value, for example "#2 of 5".
3. No launch is ranked against another artist, or against the same artist's releases in the other market.
4. Videos released before the first snapshot are listed with views to date and age, are labelled as not comparable, and carry no rank.
5. The site shows the date of the data it displays, and it loads without any request to AWS.
6. Processing the same day again leaves every number on the site unchanged.
7. The question above appears word for word at the top of the site, in English and in Spanish.

## Constraints
Batch only, zero out-of-pocket cost, AWS only, CloudFormation, public static site.

## Out of scope
Sales and chart data, streams on other platforms, artists not named above, and any forecast of future views.
