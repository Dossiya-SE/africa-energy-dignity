"""Core indicator definitions.

This module contains definitions only. It does not assign country values.
"""

from dataclasses import dataclass
from typing import Literal


EvidenceStatus = Literal[
    "observed",
    "published",
    "derived",
    "assumed",
    "scenario",
    "expert_judgment",
    "unverified",
]


@dataclass(frozen=True)
class Indicator:
    """Metadata required before an indicator can enter a decision model."""

    code: str
    name: str
    definition: str
    unit: str
    direction: Literal["higher_is_better", "lower_is_better", "target"]
    evidence_status: EvidenceStatus
    source: str | None = None

    def validate(self) -> None:
        """Raise ValueError when required metadata is incomplete."""
        if not self.code.strip():
            raise ValueError("Indicator code is required.")
        if not self.name.strip():
            raise ValueError("Indicator name is required.")
        if not self.definition.strip():
            raise ValueError("Indicator definition is required.")
        if not self.unit.strip():
            raise ValueError("Indicator unit is required.")
        if self.evidence_status in {"observed", "published", "derived"} and not self.source:
            raise ValueError(
                f"A source is required for evidence status '{self.evidence_status}'."
            )
