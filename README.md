# Comeback Thermometer

**English** · [Español](README.es.md)

How strong is each new TWICE, NMIXX or tripleS launch at day 1, 7 and 28, compared with the same artist's earlier launches in the same market? Artists include their units and soloists. YouTube only shows lifetime totals, which always favour old hits, so this project snapshots the counters every day.

**Site:** [dataengileb.github.io/kpop-comeback-thermometer](https://dataengileb.github.io/kpop-comeback-thermometer/) · **Scope:** [RFP](docs/rfp.md) and [SOW](docs/sow.md) · **Artists and channels:** [`artists.json`](src/config/artists.json) · **Adding artists or metrics:** [extending.md](docs/extending.md)

## How it works

1. Every day at 07:00 Mexico City time, Step Functions runs three Lambdas that snapshot YouTube, Last.fm and MusicBrainz into S3. Raw responses are kept. Records that break a [contract](src/contracts) go to quarantine, and if more than 5% break it, the run stops.
2. Athena rebuilds two Iceberg gold tables with `MERGE` and runs data checks ([ADR 4](docs/adr/0004-gold-iceberg-tables-rebuilt-with-merge.md)).
3. A Lambda exports gold to a dated JSON file, which the static site reads. The site never calls AWS.

![Architecture: EventBridge Scheduler starts Step Functions daily. It runs three ingestion Lambdas in parallel, which read API keys from SSM, pull from YouTube, Last.fm and MusicBrainz, and write to S3. Athena then MERGEs the validated data into two gold Iceberg tables through the Glue catalog, checks them and vacuums them. The export_site Lambda reads gold and writes a dated JSON export to S3; fetch_export.sh copies it into site/data/ and publish_site.sh pushes the site to GitHub Pages, which never calls AWS. Failed runs or checks go to SNS email, and AWS Budgets alerts on the first cent.](docs/architecture.png)

Drawn with [Diagramon](https://github.com/dataengileb/diagramon) from [its source](docs/architecture.diagramon.txt). Cyan marks the main data flow, pink the alerts.

A modernization of [my 2023 version](https://github.com/Proggleb/youtube_data_engineering_project) (EC2 + RDS + Tableau). Why it changed: [ADR 1](docs/adr/0001-serverless-batch-instead-of-ec2-rds.md).

## What it is and what it isn't

- It measures attention on YouTube and Last.fm, not sales, chart positions or streams on other platforms.
- Day-N values exist only for videos released after the first snapshot. Older comebacks are shown but not ranked.
- Each release is compared only with the same artist's releases for the same market (Korea or Japan): a Japanese MV or a solo debut is not measured against a TWICE title track.
- Last.fm users skew toward Western listeners, and Last.fm is skipped for tripleS's units, whose plays it credits to tripleS.
- Only artists with an official MV on the channels in `artists.json` are covered.

## Run it

You need an AWS account, the AWS CLI and Python 3.14. The keys and the stack must be in the same region (`us-east-1` unless you set `AWS_REGION`). Running cost is about USD 0.01 a month, all of it Athena, covered by free-tier credits: zero out-of-pocket cost. A budget alert, net of credits, emails you at the first cent spent.

```bash
read -rs KEY && aws ssm put-parameter --region us-east-1 --type SecureString --name /comeback-thermometer/youtube-api-key --value "$KEY"
read -rs KEY && aws ssm put-parameter --region us-east-1 --type SecureString --name /comeback-thermometer/lastfm-api-key --value "$KEY"
unset KEY
ALERT_EMAIL=you@example.com ./scripts/deploy.sh
```

Confirm the SNS email. The first run happens at the next 07:00, or start it by hand with `aws stepfunctions start-execution --state-machine-arn <PipelineArn>`. To refresh the site, run `./scripts/fetch_export.sh`, commit `site/data/`, then run `./scripts/publish_site.sh`.

Tests: `pip install -r requirements-dev.txt && pytest && cfn-lint`.
