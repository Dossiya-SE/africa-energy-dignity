"""Domain validation that supplements Pydantic request validation."""
from aed.registry.models import SourceCreate


def validate_source_for_use(source: SourceCreate) -> None:
    """Reject a source that lacks metadata required for validated use."""
    if source.validation_status != "validated":
        return
    if not source.licence:
        raise ValueError("A validated source requires a licence.")
    if not source.temporal_coverage:
        raise ValueError("A validated source requires temporal coverage.")
    if not source.limitations:
        raise ValueError("A validated source requires documented limitations.")
