"""Domain validation that supplements Pydantic request validation."""
from aed.registry.models import SourceCreate, VERIFIED_STATES


def validate_source_for_use(source: SourceCreate) -> None:
    """Reject unsupported upgrades from unverified evidence to verified use."""
    if source.verification_status not in VERIFIED_STATES:
        return
    if source.evidence_class == "unverified":
        raise ValueError(
            "Unverified evidence cannot receive a verified validation state."
        )
    if source.licence.strip().lower() in {
        "unknown",
        "licence_unknown",
        "license_unknown",
    }:
        raise ValueError("A verified source requires a known licence.")
