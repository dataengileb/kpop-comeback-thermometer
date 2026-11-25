import json
from pathlib import Path

import pytest

from common.contracts import CONTRACTS_DIR, load_contract, split_valid, validate
from common.run import load_groups

SCHEMA = {
    "required": ["id", "views"],
    "properties": {
        "id": {"type": "string", "pattern": "^[a-z]+$"},
        "views": {"type": "integer", "minimum": 0},
        "day": {"type": "string", "format": "date"},
        "likes": {"type": ["integer", "null"]},
    },
    "additionalProperties": False,
}


def test_valid_record_has_no_errors():
    assert validate({"id": "abc", "views": 10, "day": "2026-11-24", "likes": None}, SCHEMA) == []


@pytest.mark.parametrize(
    "record, expected",
    [
        ({"views": 1}, "id: missing"),
        ({"id": "abc", "views": "10"}, "views: expected integer"),
        ({"id": "abc", "views": True}, "views: expected integer"),
        ({"id": "abc", "views": -1}, "views: -1 < 0"),
        ({"id": "ABC", "views": 1}, "id: does not match"),
        ({"id": "abc", "views": 1, "day": "2016"}, "day: not a valid date"),
        ({"id": "abc", "views": 1, "surprise": 1}, "surprise: not in contract"),
    ],
)
def test_violations_are_reported(record, expected):
    assert any(error.startswith(expected) for error in validate(record, SCHEMA))


def test_split_keeps_errors_with_the_bad_record():
    valid, invalid = split_valid([{"id": "ok", "views": 1}, {"id": "ok"}], SCHEMA)
    assert valid == [{"id": "ok", "views": 1}]
    assert invalid[0]["errors"] == ["views: missing"]


@pytest.mark.parametrize("path", sorted(CONTRACTS_DIR.glob("*.json")), ids=lambda p: p.stem)
def test_contract_group_enum_matches_config(path: Path):
    """A new group in config/groups.json must be added to every contract, or its rows get quarantined."""
    contract = load_contract(path.stem)
    assert contract["title"] == path.stem
    slugs = sorted(g["slug"] for g in load_groups())
    assert sorted(contract["properties"]["group"]["enum"]) == slugs
