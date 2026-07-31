"""Controlled public-map catalogue and checksum-verified asset delivery."""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from aed.database.models import Dataset, GeospatialAsset, Source
from aed.database.session import get_db
from aed.geospatial.integrity import publication_ready, verify_sha256
from aed.geospatial.models import MapLayerRead
from aed.settings import Settings, get_settings

router = APIRouter(prefix="/map-assets", tags=["map-assets"])
RELEASE_PREFIX = (
    "https://github.com/Dossiya-SE/africa-energy-dignity/releases/download/"
    "geo-002-worldpop-bfa-2020-v1/"
)


def _rows(db: Session):
    statement = (
        select(GeospatialAsset, Dataset, Source)
        .join(Dataset, GeospatialAsset.dataset_id == Dataset.id)
        .join(Source, Dataset.source_id == Source.id)
        .order_by(GeospatialAsset.id)
    )
    return db.execute(statement).all()


def _is_ready(asset: GeospatialAsset, dataset: Dataset, source: Source) -> bool:
    return publication_ready(
        publication_status=asset.publication_status,
        asset_validation_status=asset.validation_status,
        source_verification_status=source.verification_status,
        evidence_class=source.evidence_class,
        licence=asset.licence or source.licence,
        checksum=asset.checksum,
        crs=asset.crs,
        is_sensitive=asset.is_sensitive,
        asset_type=asset.asset_type,
        bbox=asset.bbox,
        nodata=asset.nodata,
        unit=dataset.unit,
        metadata=asset.metadata_json,
    )


def _catalogue_record(
    asset: GeospatialAsset, dataset: Dataset, source: Source
) -> MapLayerRead:
    metadata = asset.metadata_json or {}
    ready = _is_ready(asset, dataset, source)
    warning = metadata.get("warning")
    if not ready and not warning:
        warning = (
            "Layer remains blocked until source verification, licence, checksum, CRS, "
            "nodata, coverage and validation requirements pass."
        )
    return MapLayerRead(
        asset_id=asset.id,
        name=asset.name,
        asset_type=asset.asset_type,
        geography_id=asset.geography_id,
        publication_status=asset.publication_status,
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
        nodata=asset.nodata,
        checksum=asset.checksum,
        spatial_resolution=asset.spatial_resolution,
        temporal_coverage=asset.temporal_coverage,
        product_year=metadata.get("product_year"),
        model_type=metadata.get("model_type"),
        population_total=metadata.get("population_total"),
        coverage_ratio=metadata.get("coverage_ratio"),
        file_size_bytes=metadata.get("file_size_bytes"),
        manifest_url=metadata.get("manifest_url"),
        rendering_method=metadata.get("rendering_method", "geojson"),
        data_url=f"/map-assets/{asset.id}/data" if ready else None,
        preview_url=metadata.get("preview_url") if ready else None,
        warning=None if ready else warning,
    )


def _local_asset(path_text: str, settings: Settings) -> Path:
    path = Path(path_text).resolve()
    root = Path(settings.canonical_data_root).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise HTTPException(409, "Local asset is outside the canonical data root.") from exc
    return path


def _remote_asset(asset: GeospatialAsset, settings: Settings) -> Path:
    if not asset.uri.startswith(RELEASE_PREFIX):
        raise HTTPException(409, "Remote asset locator is not an approved evidence archive.")
    filename = Path(urlparse(asset.uri).path).name
    cache_root = Path(settings.asset_cache_root).resolve()
    cache_root.mkdir(parents=True, exist_ok=True)
    destination = cache_root / f"{asset.id}-{filename}"
    if destination.exists():
        try:
            verify_sha256(destination, asset.checksum)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc
        return destination

    partial = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(
        asset.uri,
        headers={"User-Agent": "Africa-Energy-Dignity-AED-API/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response, partial.open(
            "wb"
        ) as output:
            while block := response.read(1024 * 1024):
                output.write(block)
        verify_sha256(partial, asset.checksum)
        os.replace(partial, destination)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(503, f"Verified asset retrieval failed: {exc}") from exc
    finally:
        partial.unlink(missing_ok=True)
    return destination


def _materialize(asset: GeospatialAsset, settings: Settings) -> Path:
    path = (
        _remote_asset(asset, settings)
        if asset.uri.startswith("https://")
        else _local_asset(asset.uri, settings)
    )
    if not path.is_file():
        raise HTTPException(503, "Registered asset bytes are unavailable.")
    try:
        verify_sha256(path, asset.checksum)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return path


@router.get("", response_model=list[MapLayerRead])
def list_map_assets(db: Session = Depends(get_db)) -> list[MapLayerRead]:
    """List public map controls, including explicitly blocked candidates."""
    output = []
    for asset, dataset, source in _rows(db):
        if (asset.metadata_json or {}).get("map_layer") is not True:
            continue
        output.append(_catalogue_record(asset, dataset, source))
    return output


@router.get("/{asset_id}/data")
def get_map_asset_data(
    asset_id: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Deliver only publication-ready bytes after checksum verification."""
    row = db.execute(
        select(GeospatialAsset, Dataset, Source)
        .join(Dataset, GeospatialAsset.dataset_id == Dataset.id)
        .join(Source, Dataset.source_id == Source.id)
        .where(GeospatialAsset.id == asset_id)
    ).first()
    if row is None:
        raise HTTPException(404, "Map asset not found.")
    asset, dataset, source = row
    if not _is_ready(asset, dataset, source):
        raise HTTPException(409, "Asset is blocked by the AED publication gate.")
    path = _materialize(asset, settings)
    if path.suffix.lower() in {".json", ".geojson"}:
        return JSONResponse(json.loads(path.read_text(encoding="utf-8")))
    if path.name.lower().endswith((".tif", ".tiff")):
        return FileResponse(path, media_type="image/tiff", filename=path.name)
    raise HTTPException(415, "Registered asset media type is not supported.")
