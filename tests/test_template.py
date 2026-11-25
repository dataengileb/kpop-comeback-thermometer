"""Static checks on infra/template.yaml: the gold SQL must agree with the Glue table definitions."""

import re
from pathlib import Path

import pytest
from cfnlint.decode import cfn_yaml

TEMPLATE = cfn_yaml.load(str(Path(__file__).resolve().parent.parent / "infra" / "template.yaml"))
RESOURCES = TEMPLATE["Resources"]
STATES = RESOURCES["Pipeline"]["Properties"]["Definition"]["States"]


def _columns(logical_id: str) -> list[str]:
    return [c["Name"] for c in RESOURCES[logical_id]["Properties"]["TableInput"]["StorageDescriptor"]["Columns"]]


def _sql(state: str) -> str:
    return STATES[state]["Arguments"]["QueryString"]


@pytest.mark.parametrize("state, table", [("BuildMvLaunch", "GoldMvLaunch"), ("BuildArtistDaily", "GoldArtistDaily")])
def test_merge_inserts_every_gold_column(state, table):
    insert = re.search(r"INSERT \(([^)]*)\)", _sql(state)).group(1)
    assert [c.strip() for c in insert.split(",")] == _columns(table)


def test_merge_updates_every_non_key_column():
    updated = re.findall(r"^\s*(\w+) = s\.\1", _sql("BuildMvLaunch"), re.MULTILINE)
    assert updated == _columns("GoldMvLaunch")[1:]


def test_gold_tables_are_iceberg():
    for logical_id in ("GoldMvLaunch", "GoldArtistDaily"):
        assert RESOURCES[logical_id]["Properties"]["OpenTableFormatInput"]["IcebergInput"]["MetadataOperation"] == "CREATE"
