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


@router.get("", response_model=list[SourceRead])
def list_sources(db: Session = Depends(get_db)):
    """List registered sources."""
    return list_records(db, Source)


@router.post("", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    """Create a source without silently validating or overwriting it."""
    validate_source_for_use(payload)
    values = payload.model_dump(mode="json")
    try:
        return create_with_audit(
            db, model=Source, entity_type="source", values=values
        )
    except DuplicateIdentifierError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{source_id}", response_model=SourceRead)
def get_source(source_id: str, db: Session = Depends(get_db)):
    """Retrieve a source by stable identifier."""
    source = get_record(db, Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found.")
    return source
