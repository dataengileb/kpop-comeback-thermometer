"""Data contracts: one JSON Schema per source record, stored in contracts/.

Only the subset of JSON Schema we use is implemented (type, required, properties,
minimum, minLength, pattern, enum, format: date / date-time). This keeps the
Lambdas dependency-free; if a contract needs more, switch to the jsonschema package.
"""

import json
import re
from datetime import date, datetime
from pathlib import Path

CONTRACTS_DIR = Path(__file__).resolve().parent.parent / "contracts"

_TYPES = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "object": dict,
    "array": list,
    "null": type(None),
}


def load_contract(name: str) -> dict:
    return json.loads((CONTRACTS_DIR / f"{name}.json").read_text())


def _check_type(value, expected) -> bool:
    expected = expected if isinstance(expected, list) else [expected]
    for name in expected:
        # bool is a subclass of int in Python; a contract that says integer means a real integer.
        if name in ("integer", "number") and isinstance(value, bool):
            continue
        if isinstance(value, _TYPES[name]):
            return True
    return False


def _check_format(value: str, fmt: str) -> bool:
    try:
        if fmt == "date":
            date.fromisoformat(value)
        elif fmt == "date-time":
            datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate(record: dict, schema: dict) -> list[str]:
    """Return a list of violations. Empty list means the record honours the contract."""
    errors = []
    for field in schema.get("required", []):
        if field not in record or record[field] is None:
            errors.append(f"{field}: missing")
    for field, rules in schema.get("properties", {}).items():
        value = record.get(field)
        if value is None:
            continue
        if "type" in rules and not _check_type(value, rules["type"]):
            errors.append(f"{field}: expected {rules['type']}, got {type(value).__name__}")
            continue
        if "minimum" in rules and value < rules["minimum"]:
            errors.append(f"{field}: {value} < {rules['minimum']}")
        if "minLength" in rules and len(value) < rules["minLength"]:
            errors.append(f"{field}: shorter than {rules['minLength']}")
        if "pattern" in rules and not re.search(rules["pattern"], value):
            errors.append(f"{field}: does not match {rules['pattern']}")
        if "enum" in rules and value not in rules["enum"]:
            errors.append(f"{field}: {value!r} not in {rules['enum']}")
        if "format" in rules and not _check_format(value, rules["format"]):
            errors.append(f"{field}: not a valid {rules['format']}")
    if schema.get("additionalProperties") is False:
        extra = set(record) - set(schema.get("properties", {}))
        errors.extend(f"{field}: not in contract" for field in sorted(extra))
    return errors


def split_valid(records: list[dict], schema: dict) -> tuple[list[dict], list[dict]]:
    """Separate good records from bad ones. Bad ones keep their errors for the quarantine file."""
    valid, invalid = [], []
    for record in records:
        errors = validate(record, schema)
        if errors:
            invalid.append({"record": record, "errors": errors})
        else:
            valid.append(record)
    return valid, invalid
