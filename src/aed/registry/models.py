"""Pydantic request and response models for registry entities."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

ValidationStatus = Literal["proposed", "reviewed", "validated", "rejected"]
EvidenceClass = Literal[
    "observed", "published", "derived", "assumed", "synthetic", "unverified"
]


class ORMModel(BaseModel):
    """Enable validation from SQLAlchemy objects."""

    model_config = ConfigDict(from_attributes=True)


class InstitutionCreate(BaseModel):
    id: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    name: str = Field(min_length=2, max_length=255)
    institution_type: str = Field(min_length=2, max_length=64)
    country_code: str | None = Field(default=None, min_length=2, max_length=3)
    website: HttpUrl | None = None
    notes: str | None = None


class InstitutionRead(InstitutionCreate, ORMModel):
    website: str | None = None
    created_at: datetime
    updated_at: datetime


class GeographyCreate(BaseModel):
    id: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    name: str = Field(min_length=2, max_length=255)
    level: str = Field(min_length=2, max_length=64)
    parent_id: str | None = None
    iso_code: str | None = Field(default=None, max_length=16)
    geometry_status: str = "not_stored"


class GeographyRead(GeographyCreate, ORMModel):
    created_at: datetime
    updated_at: datetime


class SourceCreate(BaseModel):
    id: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    title: str = Field(min_length=3, max_length=500)
    publisher_id: str | None = None
    source_url: HttpUrl
    access_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    temporal_coverage: str | None = None
    geographic_coverage: str | None = None
    licence: str | None = None
    attribution: str | None = None
    limitations: str | None = None
    evidence_class: EvidenceClass = "published"
    validation_status: ValidationStatus = "proposed"
    checksum: str | None = None

    @model_validator(mode="after")
    def enforce_validated_metadata(self):
        """Block validation when licence, time or limitations are absent."""
        if self.validation_status == "validated":
            required = {
                "licence": self.licence,
                "temporal_coverage": self.temporal_coverage,
                "limitations": self.limitations,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise ValueError(
                    "Validated sources require: " + ", ".join(sorted(missing))
                )
        return self


class SourceRead(SourceCreate, ORMModel):
    source_url: str
    created_at: datetime
    updated_at: datetime


class AssetCreate(BaseModel):
    id: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    dataset_id: str | None = None
    geography_id: str | None = None
    name: str = Field(min_length=2, max_length=500)
    asset_type: str = Field(min_length=2, max_length=64)
    uri: str = Field(min_length=3, max_length=1000)
    spatial_resolution: str | None = None
    temporal_coverage: str | None = None
    licence: str | None = None
    validation_status: ValidationStatus = "proposed"
    is_sensitive: bool = False


class AssetRead(AssetCreate, ORMModel):
    created_at: datetime
    updated_at: datetime


class ProjectCreate(BaseModel):
    id: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    name: str = Field(min_length=2, max_length=500)
    geography_id: str | None = None
    project_status: str = "synthetic"
    description: str | None = None
    is_synthetic: bool = True

    @model_validator(mode="after")
    def protect_non_synthetic_claims(self):
        """Require synthetic fixtures to remain explicitly synthetic."""
        if self.project_status == "synthetic" and not self.is_synthetic:
            raise ValueError("Synthetic projects must set is_synthetic=true.")
        return self


class ProjectRead(ProjectCreate, ORMModel):
    created_at: datetime
    updated_at: datetime


class AuditEventRead(ORMModel):
    id: str
    actor: str
    action: str
    entity_type: str
    entity_id: str
    event_hash: str
    payload: str
    created_at: datetime
