# 1. Serverless batch instead of EC2 and RDS

**Status:** accepted · 2026-11

## Context
The 2023 version of this project ([youtube_data_engineering_project](https://github.com/Proggleb/youtube_data_engineering_project)) ran a Python script on an EC2 instance, stored results in RDS PostgreSQL and showed them in Tableau Public. Both EC2 and RDS bill per hour while running, and the job only works for a few minutes a day.

## Decision
Run the daily job as Lambda functions orchestrated by Step Functions, triggered by EventBridge Scheduler. Store data as files in S3 and query it with Athena. Publish a dated export to a static site instead of a live dashboard.

## Consequences
- Cost follows usage: a few minutes of Lambda per day stays inside the free tier.
- Nothing to patch or keep running; a failed run sends an email instead of leaving a server in a bad state.
- Lambda has a 15-minute limit. The current run takes about a minute, so this is not a constraint yet.
- Tableau is gone. The site is plain HTML and JavaScript that anyone can host, but charts are built by hand.

## Alternative considered
Keep the 2023 design on a free-tier `t4g.micro` with RDS. Rejected: the free tier for both expires, and the instance would sit idle 23 hours a day.
