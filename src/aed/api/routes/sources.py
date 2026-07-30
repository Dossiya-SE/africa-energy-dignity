"""Source registry endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from aed.database.models import Source
from aed.database.session import get_db
from aed.registry.models import SourceCreate, SourceRead
from aed.registry.repository import (
    DuplicateIdentifierError,
    get_record,
    list_records,
)
from aed.registry.service import create_with_audit
from aed.registry.validation import validate_source_for_use

router = APIRouter(prefix="/sources", tags=["sources"])


def source_values(payload: SourceCreate) -> dict:
    """Convert validated API types into database-native values."""
    values = payload.model_dump(mode="python")
    values["source_url"] = str(payload.source_url) if payload.source_url else None
    values["temporal_coverage"] = payload.temporal_coverage.model_dump(
        mode="json", exclude_none=True
    )
    return values


@router.get("", response_model=list[SourceRead])
def list_sources(db: Session = Depends(get_db)):
    return list_records(db, Source)


@router.post("", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    try:
        validate_source_for_use(payload)
        return create_with_audit(
            db,
            model=Source,
            entity_type="source",
            values=source_values(payload),
        )
    except DuplicateIdentifierError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{source_id}", response_model=SourceRead)
def get_source(source_id: str, db: Session = Depends(get_db)):
    source = get_record(db, Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found.")
    return source
