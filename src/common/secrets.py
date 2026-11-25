"""API keys live in SSM Parameter Store (SecureString). See docs/adr/0002."""

from functools import cache

import boto3


@cache
def get_secret(name: str) -> str:
    response = boto3.client("ssm").get_parameter(Name=name, WithDecryption=True)
    return response["Parameter"]["Value"]
