# Request for Proposal: Launch-week tracking for K-pop releases

| | |
| --- | --- |
| **Issued by** | Marketing team, Lumen Music MX (a fictional distributor, used for teaching) |
| **Issued** | 3 November 2026 |
| **Questions until** | 10 November 2026 |
| **Proposals due** | 17 November 2026 |

## 1. Background
We distribute and promote K-pop releases in Mexico. For every comeback we pay for ads, listening parties and streaming drives with partner fan clubs, and nearly all of that money is spent in the first four weeks after release.

## 2. The problem
We judge a launch by the view count YouTube shows. That number is a lifetime total, so a new release always looks weak next to a hit from 2019. On day 3 we cannot tell whether a launch is ahead of or behind the artist's usual pace, so budget decisions come down to gut feeling.

## 3. What we need
For every new comeback, an answer to one question: **is this launch stronger or weaker than the same artist's previous launches at the same point after release?** We will use the answer to decide whether to add or pull promotion budget during weeks 1 to 4.

Artists: TWICE, NMIXX and tripleS, including their units and solo releases, for Korea and Japan.

## 4. Requirements
**Must**
1. For each new music video, show its views 1, 7 and 28 days after release, and how it ranks against the same artist's earlier launches in the same market.
2. Clearly label releases that cannot be compared fairly, instead of hiding them or estimating their numbers.
3. Publish the results on a public web page, in English and Spanish, that shows how current the data is.
4. Update every day without anyone running it, and tell us when an update fails.
5. Give the same numbers if a day is processed again.

**Should**
6. Add a second source of attention data besides YouTube.
7. Be simple enough for our two-person analytics team to maintain.

## 5. Constraints
- It runs in our AWS account. IT allows only AWS-managed services, with infrastructure defined in CloudFormation.
- This project has no budget for fixed costs: nothing may bill just for being switched on.
- The public page must not connect to our AWS account, and no credentials may appear in code or on the page.

## 6. Out of scope
Sales and chart data, other streaming platforms, artists not listed above, and forecasts of future views.

## 7. What your proposal should include
- Your approach and architecture, and the main risks you see.
- Which data sources you would use, and what they cannot tell us.
- A plan with milestones.
- The expected monthly running cost.

## 8. How we will choose
| Criterion | Weight |
| --- | --- |
| Meets the requirements in section 4 | 40% |
| Is honest about what the data can and cannot show | 20% |
| Running cost and simplicity | 20% |
| Plan and risk handling | 20% |
