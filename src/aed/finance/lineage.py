"""Deterministic canonicalization and lineage for FIN-001 calculations."""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
import hashlib
import json
import math
from typing import Any, TypeVar

from pydantic import BaseModel

from aed.finance.models import (
    CANONICALIZATION_VERSION,
    CalculationRunIdentity,
    DeterministicIndicatorResult,
    FinanceScenario,
    IndicatorLineage,
)

ResultT = TypeVar("ResultT", bound=DeterministicIndicatorResult)


def _canonical_decimal(value: Decimal) -> str:
    """Return one exponent-free representation for a finite Decimal value."""
    if not value.is_finite():
        raise ValueError("Canonical finance values must be finite.")
    if value == 0:
        return "0"
    normalized = value.normalize()
    rendered = format(normalized, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def _canonical_datetime(value: datetime) -> str:
    """Normalize an aware timestamp to UTC using an explicit Z suffix."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Canonical finance timestamps must be timezone-aware.")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize(value: Any) -> Any:
    """Convert supported values to a type-tagged canonical JSON structure."""
    if isinstance(value, BaseModel):
        return _normalize(
            value.model_dump(mode="python", by_alias=True, exclude_none=False)
        )
    if isinstance(value, Decimal):
        return {"$decimal": _canonical_decimal(value)}
    if isinstance(value, datetime):
        return {"$datetime": _canonical_datetime(value)}
    if isinstance(value, date):
        return {"$date": value.isoformat()}
    if isinstance(value, Enum):
        return _normalize(value.value)
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("Canonical finance mappings require string keys.")
            normalized[key] = _normalize(item)
        return normalized
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Canonical finance values must be finite.")
        return {"$float": format(value, ".17g")}
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise TypeError(f"Unsupported canonical finance value: {type(value).__name__}.")


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize supported values as canonical UTF-8 JSON bytes."""
    normalized = _normalize(value)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_scenario_bytes(scenario: FinanceScenario) -> bytes:
    """Return canonical bytes for one already validated finance scenario."""
    return canonical_json_bytes(scenario)


def scenario_input_hash(scenario: FinanceScenario) -> str:
    """Return the SHA-256 digest of the complete canonical scenario."""
    digest = hashlib.sha256(canonical_scenario_bytes(scenario)).hexdigest()
    return f"sha256:{digest}"


def build_calculation_run_identity(
    scenario: FinanceScenario,
    *,
    software_version: str,
) -> CalculationRunIdentity:
    """Build a deterministic content-addressed calculation-run identity."""
    if not software_version.strip():
        raise ValueError("software_version must be non-empty.")
    input_hash = scenario_input_hash(scenario)
    material = {
        "canonicalization_version": CANONICALIZATION_VERSION,
        "formula_version": scenario.formula_version,
        "input_hash": input_hash,
        "software_version": software_version,
    }
    digest = hashlib.sha256(canonical_json_bytes(material)).hexdigest()
    return CalculationRunIdentity(
        calculation_run_id=f"finance.run.sha256.{digest}",
        scenario_id=scenario.scenario_id,
        scenario_version=scenario.scenario_version,
        formula_version=scenario.formula_version,
        input_hash=input_hash,
        canonicalization_version=CANONICALIZATION_VERSION,
        software_version=software_version,
    )


def build_indicator_lineage(
    identity: CalculationRunIdentity,
    *,
    indicator_name: str,
) -> IndicatorLineage:
    """Bind one indicator name to an existing deterministic run identity."""
    if not indicator_name.strip():
        raise ValueError("indicator_name must be non-empty.")
    return IndicatorLineage(
        **identity.model_dump(),
        indicator_name=indicator_name,
    )


def attach_indicator_lineage(
    result: ResultT,
    identity: CalculationRunIdentity,
    *,
    indicator_name: str,
) -> ResultT:
    """Return a validated copy of an indicator result carrying lineage."""
    if result.formula_version != identity.formula_version:
        raise ValueError("Indicator and calculation-run formula versions must match.")
    lineage = build_indicator_lineage(
        identity,
        indicator_name=indicator_name,
    )
    payload = result.model_dump(mode="python")
    payload["lineage"] = lineage.model_dump(mode="python")
    return type(result).model_validate(payload)
