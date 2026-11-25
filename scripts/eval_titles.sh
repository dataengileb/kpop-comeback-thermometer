#!/usr/bin/env bash
# Weekly eval sweep: scores the title matcher on the golden set, then lists the uploads in the
# latest bronze snapshot that are not in the golden set yet and need a verdict.
# Usage: ./scripts/eval_titles.sh   (with requirements-dev.txt installed; writes evals/review/<date>.jsonl, ignored by git)
set -euo pipefail

STACK="${STACK:-comeback-thermometer}"
REGION="${AWS_REGION:-us-east-1}"
cd "$(dirname "$0")/.."

python3 evals/run.py

BUCKET="$(aws cloudformation describe-stacks --region "$REGION" --stack-name "$STACK" \
  --query "Stacks[0].Outputs[?OutputKey=='DataBucketName'].OutputValue" --output text)"
DAY="$(aws s3 ls --region "$REGION" "s3://${BUCKET}/bronze/source=youtube/" | awk -F'=' '{print $2}' | tr -d '/' | sort | tail -1)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
aws s3 cp --region "$REGION" --recursive --only-show-errors --exclude "*" --include "uploads_*.json" \
  "s3://${BUCKET}/bronze/source=youtube/snapshot_date=${DAY}/" "$TMP"

mkdir -p evals/review
python3 evals/run.py --bronze "$TMP" > "evals/review/${DAY}.jsonl"
echo "evals/review/${DAY}.jsonl"
