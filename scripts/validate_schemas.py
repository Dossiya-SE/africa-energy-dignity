"""Validate the approved AED JSON Schemas and embedded examples."""

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILES = (
    "schemas/geographies.schema.json",
    "schemas/demand.schema.json",
    "schemas/technologies.schema.json",
    "schemas/resources.schema.json",
    "schemas/infrastructure.schema.json",
    "schemas/policies.schema.json",
    "schemas/sources.schema.json",
    "schemas/finance.schema.json",
)


def validate_schema(path: Path) -> None:
    """Validate one schema and every embedded example."""
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)

    examples = schema.get("examples")
    if not isinstance(examples, list) or not examples:
        raise ValidationError("Schema must contain at least one example.")

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for example in examples:
        validator.validate(example)


def error_path(error: Exception) -> str:
    """Return the most useful JSON validation path available."""
    path = getattr(error, "json_path", None)
    if path:
        return path
    schema_path = getattr(error, "schema_path", None)
    return "/".join(map(str, schema_path)) if schema_path else "$"


def main() -> int:
    for relative_path in SCHEMA_FILES:
        path = ROOT / relative_path
        try:
            validate_schema(path)
        except (OSError, json.JSONDecodeError, SchemaError, ValidationError) as error:
            print(f"Schema validation failed: {relative_path} [{error_path(error)}] {error}")
            return 1
        print(f"Schema valid: {relative_path}")

    print(f"Canonical schema validation passed: {len(SCHEMA_FILES)} schemas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
