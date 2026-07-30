"""Institution registry endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from aed.database.models import Institution
from aed.database.session import get_db
from aed.registry.models import InstitutionCreate, InstitutionRead
from aed.registry.repository import DuplicateIdentifierError, list_records
from aed.registry.service import create_with_audit

router = APIRouter(prefix="/institutions", tags=["institutions"])


@router.get("", response_model=list[InstitutionRead])
def list_institutions(db: Session = Depends(get_db)):
    """List registered institutions."""
    return list_records(db, Institution)


@router.post(
    "", response_model=InstitutionRead, status_code=status.HTTP_201_CREATED
)
def create_institution(
    payload: InstitutionCreate, db: Session = Depends(get_db)
):
    """Create an institution and append an audit event."""
    try:
        return create_with_audit(
            db,
            model=Institution,
            entity_type="institution",
            values=payload.model_dump(mode="json"),
        )
    except DuplicateIdentifierError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
