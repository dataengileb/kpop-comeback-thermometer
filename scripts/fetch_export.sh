#!/usr/bin/env bash
# Copies the latest export written by the daily run into site/data/, as latest.json and as a
# dated file. The site reads only these files: it never calls AWS.
# Usage: ./scripts/fetch_export.sh
set -euo pipefail

STACK="${STACK:-comeback-thermometer}"
REGION="${AWS_REGION:-us-east-1}"
cd "$(dirname "$0")/.."

BUCKET="$(aws cloudformation describe-stacks --region "$REGION" --stack-name "$STACK" \
  --query "Stacks[0].Outputs[?OutputKey=='DataBucketName'].OutputValue" --output text)"
aws s3 cp --region "$REGION" --only-show-errors "s3://${BUCKET}/exports/latest.json" site/data/latest.json

# Pretty-printed so each refresh shows up in git as a readable diff.
DAY="$(python3 - <<'PY'
import json
path = "site/data/latest.json"
data = json.load(open(path, encoding="utf-8"))
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
    f.write("\n")
print(data["snapshot_date"])
PY
)"
cp site/data/latest.json "site/data/${DAY}.json"
echo "site/data/${DAY}.json"
