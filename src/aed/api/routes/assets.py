"""Geospatial asset registry endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from aed.database.models import GeospatialAsset
from aed.database.session import get_db
from aed.registry.models import AssetCreate, AssetRead
from aed.registry.repository import DuplicateIdentifierError, list_records
from aed.registry.service import create_with_audit

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetRead])
def list_assets(db: Session = Depends(get_db)):
    """List registered geospatial assets."""
    return list_records(db, GeospatialAsset)


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    """Create an asset while protecting sensitive public coordinates."""
    if payload.is_sensitive and payload.uri.startswith("http"):
        raise HTTPException(
            status_code=422,
            detail="Sensitive assets may not use a public URI.",
        )
    try:
        return create_with_audit(
            db,
            model=GeospatialAsset,
            entity_type="geospatial_asset",
            values=payload.model_dump(mode="json"),
        )
    except DuplicateIdentifierError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
