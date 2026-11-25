# 2. API keys in SSM Parameter Store

**Status:** accepted · 2026-11

## Context
YouTube and Last.fm need API keys. They must not be in the repository, the template or the site.

## Decision
Store each key as an SSM Parameter Store `SecureString`, created by hand once per account (see the README). The Lambdas read it at runtime with `ssm:GetParameter`, limited by IAM to those two parameter names.

## Consequences
- Standard parameters are free; a Secrets Manager secret costs USD 0.40 per month.
- No automatic rotation. Acceptable: these are read-only keys for public data.
- CloudFormation cannot create a `SecureString`, so this is the one manual step in the deployment.

## Alternative considered
Lambda environment variables: free and simple, but the key would be visible in plain text in the console and in `get-function` output.
