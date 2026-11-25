# Statement of Work: Comeback Thermometer

## Scope
A daily batch pipeline in the client's AWS account that snapshots the three sources, keeps the raw data, validates it against contracts and builds a "views at day N" table. A dated export of that table feeds a public static site.

## Deliverables
| # | Deliverable | Done when |
| --- | --- | --- |
| 1 | Ingestion | Three Lambdas write raw, validated and quarantine files daily; bad data stops the run and emails an alert |
| 2 | Gold layer | Athena tables with day-N views per comeback, rebuilt idempotently |
| 3 | Snapshot export | One command downloads the dated gold export into `site/data/` |
| 4 | Public site | GitHub Pages site in English and Spanish answering the RFP question |
| 5 | Executive presentation | 20 minutes with the client |

## Assumptions
- The client provides one AWS free-tier account and creates the two API keys.
- YouTube music videos are uploaded to the official channels listed in `src/config/groups.json`.
- A music video's publish time is the start of the comeback (day 0).

## Risks
| Risk | Mitigation |
| --- | --- |
| No history before the first snapshot | Criterion 3: older comebacks are shown but not ranked |
| A channel renames its videos and the title filter misses one | Matched videos are logged; filter covered by tests |
| YouTube quota exhausted | A run uses under 200 of 10,000 daily units |
| Free-tier credits run out | Budget alert on the first cent; the site keeps working from the last export |

## Out of scope
Everything listed under "Out of scope" in the [RFP](rfp.md).
