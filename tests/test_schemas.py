import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATHS = tuple(
    ROOT / "schemas" / name
    for name in (
        "geographies.schema.json",
        "demand.schema.json",
        "technologies.schema.json",
        "resources.schema.json",
        "infrastructure.schema.json",
        "policies.schema.json",
        "sources.schema.json",
    )
)
ENTITY_SCHEMA_PATHS = SCHEMA_PATHS[:-1]

EVIDENCE_CLASSES = {
    "observed", "published", "derived", "assumed", "scenario",
    "expert_judgment", "unverified",
}
VALIDATION_STATES = {
    "proposed", "schema_valid", "source_verified", "cross_checked",
    "model_ready", "validated", "rejected", "deprecated",
}
MISSING_STATES = {
    "not_missing", "not_collected", "unavailable", "suppressed",
    "not_applicable", "imputed", "below_detection_limit",
}


def load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validator(path: Path) -> Draft202012Validator:
    return Draft202012Validator(load_schema(path), format_checker=FormatChecker())


@pytest.mark.parametrize("path", SCHEMA_PATHS)
def test_schema_file_exists(path):
    assert path.is_file()


@pytest.mark.parametrize("path", SCHEMA_PATHS)
def test_schema_and_examples_are_valid(path):
    schema = load_schema(path)
    Draft202012Validator.check_schema(schema)
    assert schema["examples"]
    for example in schema["examples"]:
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(example)


@pytest.mark.parametrize("path", SCHEMA_PATHS)
def test_empty_object_is_rejected(path):
    with pytest.raises(ValidationError):
        validator(path).validate({})


@pytest.mark.parametrize("path", SCHEMA_PATHS)
def test_unknown_property_is_rejected(path):
    schema = load_schema(path)
    record = copy.deepcopy(schema["examples"][0])
    record["unexpected_property"] = True
    with pytest.raises(ValidationError):
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(record)


@pytest.mark.parametrize("path", ENTITY_SCHEMA_PATHS)
@pytest.mark.parametrize("evidence_class", ["observed", "published"])
def test_sourced_evidence_requires_source_id(path, evidence_class):
    schema = load_schema(path)
    record = copy.deepcopy(schema["examples"][0])
    record["evidence_class"] = evidence_class
    record.pop("source_id", None)
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(record)


@pytest.mark.parametrize("path", ENTITY_SCHEMA_PATHS)
def test_derived_evidence_requires_processing_method(path):
    schema = load_schema(path)
    record = copy.deepcopy(schema["examples"][0])
    record["evidence_class"] = "derived"
    record.pop("processing_method", None)
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(record)


@pytest.mark.parametrize("path", ENTITY_SCHEMA_PATHS)
def test_imputed_record_requires_method_and_uncertainty(path):
    schema = load_schema(path)
    record = copy.deepcopy(schema["examples"][0])
    record["missing_status"] = "imputed"
    for field in ("processing_method", "uncertainty_type", "uncertainty_value"):
        record.pop(field, None)
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(record)


@pytest.mark.parametrize("path", ENTITY_SCHEMA_PATHS)
def test_common_contract_is_consistent(path):
    schema = load_schema(path)
    defs = schema["$defs"]
    assert set(defs["evidence_class"]["enum"]) == EVIDENCE_CLASSES
    assert set(defs["validation_status"]["enum"]) == VALIDATION_STATES
    assert set(defs["missing_status"]["enum"]) == MISSING_STATES

    properties = schema["properties"]
    assert properties["source_id"] == {"$ref": "#/$defs/identifier"}
    assert properties["geography_id"] == {"$ref": "#/$defs/identifier"}
    assert properties["unit"] == {"$ref": "#/$defs/non_empty_string"}
    assert not any(
        token in name.lower()
        for name in properties
        for token in ("energyrt", "pyomo", "solver", "dashboard")
    )


@pytest.mark.parametrize("path", SCHEMA_PATHS)
def test_references_are_local(path):
    schema_text = path.read_text(encoding="utf-8")
    references = []

    def collect(value):
        if isinstance(value, dict):
            references.extend(item for key, item in value.items() if key == "$ref")
            for item in value.values():
                collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)

    collect(json.loads(schema_text))
    assert all(reference.startswith("#/") for reference in references)


def test_schema_validator_script_passes():
    result = subprocess.run(
        [sys.executable, "scripts/validate_schemas.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("path", ENTITY_SCHEMA_PATHS)
def test_zero_is_not_a_missing_value_marker(path):
    schema = load_schema(path)
    record = copy.deepcopy(schema["examples"][0])
    record["missing_status"] = "unavailable"
    record["value"] = 0
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(record)
