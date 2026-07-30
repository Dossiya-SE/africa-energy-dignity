"""GEO-002 geometry, provenance, publication and API tests."""
from pathlib import Path

import pytest
from sqlalchemy import select

from aed.database.models import Dataset, GeospatialAsset, Source, ValidationEvent
from aed.geospatial.integrity import (
    publication_ready,
    sha256_file,
    validate_boundary_geojson,
    validate_raster_contract,
)
from scripts.seed_geospatial import seed_with_session

BOUNDARY = Path("data/canonical/boundaries/bfa-natural-earth-5.1.1.geojson")
EXPECTED_SHA = "2dcb37ce024c79b9ef5d7e4aaa73763755d3073bba872b962333dffc45764b81"


def test_boundary_checksum_crs_geometry_and_coverage():
    result = validate_boundary_geojson(BOUNDARY)
    assert sha256_file(BOUNDARY) == EXPECTED_SHA
    assert result.checksum == EXPECTED_SHA
    assert result.crs == "OGC:CRS84"
    assert result.geometry_type == "Polygon"
    assert result.bbox == (-5.470565, 9.610835, 2.177108, 15.116158)


def test_raster_contract_requires_units_nodata_checksum_and_extent():
    with pytest.raises(ValueError, match="checksum, unit, nodata, bbox"):
        validate_raster_contract({"crs": "EPSG:4326"})
    validate_raster_contract(
        {
            "checksum": "sha256:test",
            "crs": "EPSG:4326",
            "unit": "persons per pixel",
            "nodata": -99999,
            "bbox": [-5.5, 9.5, 2.2, 15.2],
        }
    )


def test_unverified_or_incomplete_assets_are_not_publication_ready():
    assert not publication_ready(
        publication_status="published",
        asset_validation_status="validated",
        source_verification_status="schema_valid",
        evidence_class="unverified",
        licence="Creative Commons Attribution 4.0",
        checksum="sha256:test",
        crs="EPSG:4326",
        is_sensitive=False,
    )
    assert not publication_ready(
        publication_status="published",
        asset_validation_status="validated",
        source_verification_status="source_verified",
        evidence_class="published",
        licence="Creative Commons Attribution 4.0",
        checksum=None,
        crs="EPSG:4326",
        is_sensitive=False,
    )


def test_seed_preserves_source_dataset_asset_processing_and_validation_trace(db_session):
    seed_with_session(db_session)
    asset = db_session.get(
        GeospatialAsset, "asset.bfa.boundary.natural-earth.v5.1.1"
    )
    dataset = db_session.get(Dataset, asset.dataset_id)
    source = db_session.get(Source, dataset.source_id)
    event = db_session.scalar(
        select(ValidationEvent).where(
            ValidationEvent.entity_id == asset.id,
            ValidationEvent.status == "validated",
        )
    )
    assert source.id == "source.natural-earth.admin0.v5.1.1"
    assert source.licence == "Public domain"
    assert dataset.validation_status == "validated"
    assert asset.publication_status == "published"
    assert asset.processing_run_id == "run.bfa.boundary.natural-earth.v5.1.1"
    assert event is not None
    assert event.checks_json["iso_a3"] == "BFA"


def test_map_catalog_exposes_boundary_and_blocks_unvalidated_rasters(client, db_session):
    seed_with_session(db_session)
    response = client.get("/map-assets")
    assert response.status_code == 200
    layers = {layer["asset_id"]: layer for layer in response.json()}
    boundary = layers["asset.bfa.boundary.natural-earth.v5.1.1"]
    population = layers["asset.bfa.population.worldpop.2020.1km"]
    solar = layers["asset.bfa.solar.gsa.ghi.2020"]
    assert boundary["publication_status"] == "published"
    assert boundary["data_url"].endswith("/data")
    assert population["publication_status"] == "blocked"
    assert population["warning"]
    assert solar["publication_status"] == "blocked"
    assert solar["warning"]


def test_boundary_api_returns_checksum_verified_geojson(client, db_session):
    seed_with_session(db_session)
    response = client.get(
        "/map-assets/asset.bfa.boundary.natural-earth.v5.1.1/data"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["features"][0]["properties"]["iso_a3"] == "BFA"


def test_blocked_raster_is_not_served(client, db_session):
    seed_with_session(db_session)
    response = client.get("/map-assets/asset.bfa.population.worldpop.2020.1km/data")
    assert response.status_code == 409
