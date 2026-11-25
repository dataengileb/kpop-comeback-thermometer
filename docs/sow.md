# Statement of Work: Comeback Thermometer

**Client:** Lumen Music MX, marketing team (fictional). **Provider:** the data engineering team that answered the [RFP](rfp.md). **Starts:** 24 November 2026.

## 1. Approach
YouTube and Last.fm only return totals as of today, and no source publishes how a video grew. The provider will therefore build a daily batch pipeline in the client's AWS account. It takes a snapshot of every counter each day, keeps the raw responses, validates each record against a data contract, and computes views at day 1, 7 and 28 from those snapshots. A dated export of the results feeds a static bilingual site. The design decisions are recorded in [docs/adr](adr/).

The sources are the three in the RFP's [Data available](rfp.md#data-available). Known limits: Last.fm users are mostly Western, and Last.fm credits tripleS's units to tripleS; some MusicBrainz dates have only the year.

## 2. Deliverables and acceptance
| # | Deliverable | Accepted when |
| --- | --- | --- |
| 1 | Daily ingestion | Seven consecutive daily runs succeed; invalid records land in quarantine with a reason; a forced failure sends the alert email |
| 2 | Gold tables | Re-running a day leaves the tables unchanged, and every data check passes |
| 3 | Dated export | One command copies the latest export into `site/data/` |
| 4 | Public site | Every [acceptance criterion](rfp.md#acceptance-criteria) in the RFP holds when the client checks the site |
| 5 | Handover | The README, ADRs and this SOW let the client's team deploy from scratch |
| 6 | Executive presentation | Twenty minutes with the client, followed by questions; the slides go in `docs/presentation.pdf` |

## 3. Milestones
| Week | Milestone |
| --- | --- |
| 1 | Ingestion running daily (deliverable 1) |
| 1 | Gold tables in Athena (deliverable 2) |
| 2 | Export and site published (deliverables 3 and 4) |
| 2 to 6 | The pipeline runs daily; the first launch measured from day 1 is reviewed with the client |
| 6 | Handover and presentation (deliverables 5 and 6) |

## 4. Responsibilities
- **Client:** provides one AWS account and the YouTube and Last.fm API keys, confirms the alert email, and reviews each deliverable within three working days.
- **Provider:** builds, tests and documents the pipeline and the site, and reports any failure that is not resolved the same day.

## 5. Assumptions
- Official music videos are uploaded to the channels listed in [`src/config/artists.json`](../src/config/artists.json).
- A music video's publish time is the start of its comeback (day 0).
- The client accepts that launches released before the first snapshot cannot be ranked.

## 6. Risks
| Risk | Mitigation |
| --- | --- |
| No history before the first snapshot | Older launches are shown but labelled as not comparable |
| A missed day cannot be recovered later | Each source runs independently, and a failure alerts the client the same day |
| A channel changes its title format and an MV is missed | Title patterns are tested against real titles; there is a manual list for exceptions |
| A source changes or rate-limits its API | Contracts and the quality gate stop bad data before it reaches gold |
| YouTube's [Developer Policies](https://developers.google.com/youtube/terms/developer-policies) (III.E.4) forbid keeping statistics fetched with an API key for more than 30 days, and forbid derived metrics; this design keeps daily view counts and ranks them | Open. Acceptable for a non-commercial course project only. A real client must either get YouTube's written approval or keep 30 days of statistics, which loses comparisons with older launches |
| Last.fm's [API terms](https://www.last.fm/api/tos) allow non-commercial use only and require attribution | The site credits "Powered by AudioScrobbler" and links each artist to its Last.fm page; a commercial client needs a separate Last.fm agreement |

## 7. Cost
No fixed cost. Athena bills per query with a 10 MB minimum: about USD 0.01 a month, all of it Athena, covered by free-tier credits, so the out-of-pocket cost is zero. Every other service stays inside the free tier. A budget alert, net of credits, emails the client at the first cent actually spent. This course project carries no fee. In a commercial SOW, each milestone would have a price, paid when it is accepted.

## 8. Change control
Any change in scope is written down as a change request, estimated, and approved by the client before work starts. Changes so far:

| # | Date | Change | Effect |
| --- | --- | --- | --- |
| CR-1 | 2026-11-24 | Add MISAMO, the four TWICE soloists, and Japanese releases | Config split into artists and channels; results compared per market |
| CR-2 | 2026-11-25 | Add tripleS units | Eleven units added; Last.fm skipped for them |

## 9. Out of scope
Everything listed under "Out of scope" in the [RFP](rfp.md).
