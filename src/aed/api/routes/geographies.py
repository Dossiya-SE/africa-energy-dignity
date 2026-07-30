"""Geography registry endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from aed.database.models import Geography
from aed.database.session import get_db
from aed.registry.models import GeographyCreate, GeographyRead
from aed.registry.repository import DuplicateIdentifierError, list_records
from aed.registry.service import create_with_audit

router = APIRouter(prefix="/geographies", tags=["geographies"])


@router.get("", response_model=list[GeographyRead])
def list_geographies(db: Session = Depends(get_db)):
    """List canonical geography records."""
    return list_records(db, Geography)


@router.post(
    "", response_model=GeographyRead, status_code=status.HTTP_201_CREATED
)
def create_geography(payload: GeographyCreate, db: Session = Depends(get_db)):
    """Create a geography and append an audit event."""
    try:
        return create_with_audit(
            db,
            model=Geography,
            entity_type="geography",
            values=payload.model_dump(mode="json"),
        )
    except DuplicateIdentifierError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
