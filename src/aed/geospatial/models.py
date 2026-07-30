"""Public map-layer response models."""
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict


class MapLayerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_id: str
    name: str
    asset_type: str
    geography_id: str | None
    publication_status: str
    validation_status: str
    evidence_class: str
    source_id: str
    source_title: str
    original_publisher: str
    source_url: str | None
    access_date: date
    licence: str
    attribution_requirements: str
    known_limitations: list[str]
    dataset_id: str
    dataset_version: str | None
    unit: str | None
    crs: str | None
    bbox: list[float] | None
    nodata: dict[str, Any] | None
    checksum: str | None
    spatial_resolution: str | None
    temporal_coverage: str | None
    product_year: int | None
    model_type: str | None
    population_total: float | None
    coverage_ratio: float | None
    file_size_bytes: int | None
    manifest_url: str | None
    rendering_method: str
    data_url: str | None
    preview_url: str | None
    warning: str | None
