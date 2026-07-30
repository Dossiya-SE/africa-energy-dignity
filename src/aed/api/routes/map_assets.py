"""Controlled public geospatial catalogue and data endpoints."""
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from aed.database.models import Dataset, GeospatialAsset, Source
from aed.database.session import get_db
from aed.geospatial.integrity import publication_ready, sha256_file
from aed.geospatial.models import MapLayerRead
from aed.settings import get_settings

router = APIRouter(prefix="/map-assets", tags=["map-assets"])


def _catalog_row(asset: GeospatialAsset, dataset: Dataset, source: Source) -> MapLayerRead:
    ready = publication_ready(
        publication_status=asset.publication_status,
        asset_validation_status=asset.validation_status,
        source_verification_status=source.verification_status,
        evidence_class=source.evidence_class,
        licence=asset.licence or source.licence,
        checksum=asset.checksum,
        crs=asset.crs,
        is_sensitive=asset.is_sensitive,
    )
    warning = None
    if not ready:
        warning = (
            "Layer is withheld from the public map until exact bytes, checksum, CRS, "
            "licence and validation requirements pass."
        )
    return MapLayerRead(
        asset_id=asset.id,
        name=asset.name,
        asset_type=asset.asset_type,
        geography_id=asset.geography_id,
        publication_status="published" if ready else "blocked",
        validation_status=asset.validation_status,
        evidence_class=source.evidence_class,
        source_id=source.id,
        source_title=source.title,
        original_publisher=source.original_publisher,
        source_url=source.source_url,
        access_date=source.access_date,
        licence=asset.licence or source.licence,
        attribution_requirements=source.attribution_requirements,
        known_limitations=source.known_limitations,
        dataset_id=dataset.id,
        dataset_version=dataset.version,
        unit=dataset.unit,
        crs=asset.crs,
        bbox=asset.bbox,
        checksum=asset.checksum,
        spatial_resolution=asset.spatial_resolution,
        temporal_coverage=asset.temporal_coverage,
        data_url=f"/map-assets/{asset.id}/data" if ready else None,
        warning=warning,
    )


@router.get("", response_model=list[MapLayerRead])
def list_map_assets(db: Session = Depends(get_db)):
    statement = (
        select(GeospatialAsset, Dataset, Source)
        .join(Dataset, GeospatialAsset.dataset_id == Dataset.id)
        .join(Source, Dataset.source_id == Source.id)
        .where(GeospatialAsset.is_sensitive.is_(False))
        .order_by(GeospatialAsset.name)
    )
    return [_catalog_row(*row) for row in db.execute(statement).all()]


@router.get("/{asset_id}/data")
def get_map_asset_data(asset_id: str, db: Session = Depends(get_db)):
    statement = (
        select(GeospatialAsset, Dataset, Source)
        .join(Dataset, GeospatialAsset.dataset_id == Dataset.id)
        .join(Source, Dataset.source_id == Source.id)
        .where(GeospatialAsset.id == asset_id)
    )
    row = db.execute(statement).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Map asset not found.")
    asset, dataset, source = row
    catalog = _catalog_row(asset, dataset, source)
    if catalog.publication_status != "published":
        raise HTTPException(status_code=409, detail=catalog.warning)
    settings = get_settings()
    root = Path(settings.canonical_data_root).resolve()
    path = Path(asset.uri).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise HTTPException(status_code=500, detail="Canonical asset path is unavailable.")
    checksum = f"sha256:{sha256_file(path)}"
    if checksum != asset.checksum:
        raise HTTPException(status_code=503, detail="Canonical asset checksum mismatch.")
    return JSONResponse(content=json.loads(path.read_text(encoding="utf-8")))
