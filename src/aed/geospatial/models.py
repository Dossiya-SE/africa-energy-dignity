"""Public map-layer response models."""
from datetime import date

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
    checksum: str | None
    spatial_resolution: str | None
    temporal_coverage: str | None
    data_url: str | None
    warning: str | None
