#!/usr/bin/env bash
# Packages the Lambda code and deploys the stack to the account in your current AWS profile.
# Usage: ALERT_EMAIL=you@example.com ./scripts/deploy.sh
set -euo pipefail

STACK="${STACK:-comeback-thermometer}"
REGION="${AWS_REGION:-us-east-1}"
: "${ALERT_EMAIL:?Set ALERT_EMAIL}"

ACCOUNT="$(aws sts get-caller-identity --query Account --output text)"
ARTIFACTS="${STACK}-artifacts-${ACCOUNT}"

if ! aws s3api head-bucket --bucket "$ARTIFACTS" 2>/dev/null; then
  aws s3 mb "s3://${ARTIFACTS}" --region "$REGION"
fi

cd "$(dirname "$0")/.."
aws cloudformation package \
  --region "$REGION" \
  --template-file infra/template.yaml \
  --s3-bucket "$ARTIFACTS" \
  --output-template-file infra/.packaged.yaml

aws cloudformation deploy \
  --region "$REGION" \
  --stack-name "$STACK" \
  --template-file infra/.packaged.yaml \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides "AlertEmail=${ALERT_EMAIL}"
