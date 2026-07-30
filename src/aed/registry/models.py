"""Pydantic request and response models for registry entities."""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

ValidationStatus = Literal[
    "proposed",
    "schema_valid",
    "source_verified",
    "cross_checked",
    "model_ready",
    "validated",
    "rejected",
    "deprecated",
]
EvidenceClass = Literal[
    "observed",
    "published",
    "derived",
    "assumed",
    "scenario",
    "expert_judgment",
    "unverified",
]

STABLE_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]*$"
VERIFIED_STATES = {
    "source_verified",
    "cross_checked",
    "model_ready",
    "validated",
}


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TemporalCoverage(BaseModel):
    valid_from: date | None = None
    valid_to: date | None = None
    description: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_temporal_interval(self):
        if not any((self.valid_from, self.valid_to, self.description)):
            raise ValueError(
                "Temporal coverage requires valid_from, valid_to, or description."
            )
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to must not precede valid_from.")
        return self


class InstitutionCreate(BaseModel):
    id: str = Field(min_length=2, max_length=64, pattern=STABLE_ID_PATTERN)
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
    id: str = Field(min_length=2, max_length=64, pattern=STABLE_ID_PATTERN)
    name: str = Field(min_length=2, max_length=255)
    level: str = Field(min_length=2, max_length=64)
    parent_id: str | None = None
    iso_code: str | None = Field(default=None, max_length=16)
    geometry_status: str = "not_stored"


class GeographyRead(GeographyCreate, ORMModel):
    created_at: datetime
    updated_at: datetime


class SourceCreate(BaseModel):
    id: str = Field(min_length=2, max_length=64, pattern=STABLE_ID_PATTERN)
    title: str = Field(min_length=3, max_length=500)
    original_publisher: str = Field(min_length=2, max_length=500)
    publisher_id: str | None = None
    source_url: HttpUrl | None = None
    persistent_identifier: str | None = Field(default=None, min_length=1)
    archive_reference: str | None = Field(default=None, min_length=1)
    access_date: date
    temporal_coverage: TemporalCoverage
    geographic_coverage: list[str] = Field(min_length=1)
    licence: str = Field(min_length=1, max_length=255)
    attribution_requirements: str = Field(min_length=1)
    access_method: str = Field(min_length=1, max_length=255)
    known_limitations: list[str] = Field(min_length=1)
    evidence_class: EvidenceClass = "published"
    verification_status: ValidationStatus = "proposed"
    responsible_reviewer: str = Field(min_length=1, max_length=255)
    version: str = Field(min_length=1, max_length=128)
    checksum: str | None = Field(default=None, max_length=128)

    @model_validator(mode="after")
    def enforce_source_integrity(self):
        if not any(
            (self.source_url, self.persistent_identifier, self.archive_reference)
        ):
            raise ValueError(
                "A source requires source_url, persistent_identifier, "
                "or archive_reference."
            )
        if self.verification_status in VERIFIED_STATES:
            if self.licence.strip().lower() in {
                "unknown",
                "licence_unknown",
                "license_unknown",
            }:
                raise ValueError(
                    "A source cannot be source_verified while its licence is unknown."
                )
            if self.evidence_class == "unverified":
                raise ValueError(
                    "Unverified evidence cannot receive a verified validation state."
                )
        return self


class SourceRead(SourceCreate, ORMModel):
    source_url: str | None = None
    created_at: datetime
    updated_at: datetime


class AssetCreate(BaseModel):
    id: str = Field(min_length=2, max_length=64, pattern=STABLE_ID_PATTERN)
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
    id: str = Field(min_length=2, max_length=64, pattern=STABLE_ID_PATTERN)
    name: str = Field(min_length=2, max_length=500)
    geography_id: str | None = None
    project_status: str = "synthetic"
    description: str | None = None
    is_synthetic: bool = True

    @model_validator(mode="after")
    def protect_non_synthetic_claims(self):
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
