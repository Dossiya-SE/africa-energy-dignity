"""GEO-002 geometry, raster, provenance, publication and API tests."""
import json
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from sqlalchemy import select

from aed.database.models import (
    Dataset,
    GeospatialAsset,
    ProcessingRun,
    Source,
    ValidationEvent,
)
from aed.geospatial.integrity import (
    publication_ready,
    sha256_file,
    validate_boundary_geojson,
    validate_population_raster,
    validate_raster_contract,
    verify_sha256,
)
from scripts.seed_geospatial import seed_with_session

BOUNDARY = Path("data/canonical/boundaries/bfa-natural-earth-5.1.1.geojson")
EXPECTED_SHA = "2dcb37ce024c79b9ef5d7e4aaa73763755d3073bba872b962333dffc45764b81"
POPULATION_ID = "asset.bfa.population.worldpop.2020.1km.cog"
SOLAR_ID = "asset.bfa.solar.gsa.ghi.2020"


def _test_boundary(path: Path) -> Path:
    payload = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"iso_a3": "BFA"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]],
                },
            }
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _raster(path: Path, values: np.ndarray, *, nodata=-99999.0) -> Path:
    profile = {
        "driver": "GTiff",
        "width": values.shape[1],
        "height": values.shape[0],
        "count": 1,
        "dtype": "float32",
        "crs": "EPSG:4326",
        "transform": from_origin(0, 2, 1, 1),
    }
    if nodata is not None:
        profile["nodata"] = nodata
    with rasterio.open(path, "w", **profile) as dataset:
        dataset.write(values.astype("float32"), 1)
    return path


def test_boundary_checksum_crs_geometry_and_coverage():
    result = validate_boundary_geojson(BOUNDARY)
    assert sha256_file(BOUNDARY) == EXPECTED_SHA
    assert result.checksum == EXPECTED_SHA
    assert result.crs == "OGC:CRS84"
    assert result.geometry_type == "Polygon"
    assert result.bbox == (-5.470565, 9.610835, 2.177108, 15.116158)


def test_checksum_mismatch_blocks_delivery(tmp_path):
    path = tmp_path / "asset.tif"
    path.write_bytes(b"changed bytes")
    with pytest.raises(ValueError, match="Checksum mismatch"):
        verify_sha256(path, "sha256:" + "0" * 64)


def test_raster_contract_requires_units_nodata_checksum_and_extent():
    with pytest.raises(ValueError, match="checksum, unit, nodata, bbox"):
        validate_raster_contract({"crs": "EPSG:4326"})


def test_missing_nodata_blocks_population_validation_and_publication(tmp_path):
    boundary = _test_boundary(tmp_path / "boundary.geojson")
    raster = _raster(tmp_path / "missing-nodata.tif", np.ones((2, 2)), nodata=None)
    with pytest.raises(ValueError, match="nodata metadata is missing"):
        validate_population_raster(raster, boundary)
    assert not publication_ready(
        publication_status="published",
        asset_validation_status="validated",
        source_verification_status="source_verified",
        evidence_class="published",
        licence="Creative Commons Attribution 4.0",
        checksum="sha256:test",
        crs="EPSG:4326",
        is_sensitive=False,
        asset_type="raster_population_cog",
        bbox=[0, 0, 2, 2],
        nodata=None,
        unit="persons per pixel",
        metadata={"population_total": 4, "coverage_ratio": 1.0},
    )


def test_negative_population_values_fail_validation(tmp_path):
    boundary = _test_boundary(tmp_path / "boundary.geojson")
    raster = _raster(tmp_path / "negative.tif", np.array([[1, 2], [3, -1]]))
    with pytest.raises(ValueError, match="negative valid values"):
        validate_population_raster(raster, boundary)


def test_incomplete_burkina_coverage_fails_validation(tmp_path):
    boundary = _test_boundary(tmp_path / "boundary.geojson")
    raster = _raster(
        tmp_path / "incomplete.tif",
        np.array([[1, 2], [3, -99999.0]]),
    )
    with pytest.raises(ValueError, match="coverage is incomplete"):
        validate_population_raster(raster, boundary)


def test_population_total_excludes_nodata(tmp_path):
    boundary = _test_boundary(tmp_path / "boundary.geojson")
    raster = _raster(
        tmp_path / "total.tif",
        np.array([[1, 2], [3, -99999.0]]),
    )
    result = validate_population_raster(
        raster,
        boundary,
        minimum_coverage_ratio=0.70,
    )
    assert result.population_total == pytest.approx(6.0)
    assert result.valid_pixel_count == 3
    assert result.nodata_pixel_count == 1


def test_seed_registers_complete_worldpop_chain(db_session):
    seed_with_session(db_session)
    canonical = db_session.get(GeospatialAsset, POPULATION_ID)
    original = db_session.get(
        GeospatialAsset,
        "asset.bfa.population.worldpop.2020.1km.original",
    )
    dataset = db_session.get(Dataset, canonical.dataset_id)
    source = db_session.get(Source, dataset.source_id)
    run = db_session.get(ProcessingRun, canonical.processing_run_id)
    event = db_session.scalar(
        select(ValidationEvent).where(ValidationEvent.entity_id == canonical.id)
    )
    assert source.verification_status == "source_verified"
    assert source.checksum.startswith("sha256:")
    assert dataset.validation_status == "model_ready"
    assert original.publication_status == "blocked"
    assert canonical.publication_status == "published"
    assert canonical.nodata["value"] == -99999.0
    assert run.input_checksum == source.checksum
    assert run.output_checksum == canonical.checksum
    assert event.checks_json["population_total"] == pytest.approx(22811078.2325013)


def test_map_catalog_exposes_boundary_population_and_blocked_solar(client, db_session):
    seed_with_session(db_session)
    response = client.get("/map-assets")
    assert response.status_code == 200
    layers = {layer["asset_id"]: layer for layer in response.json()}
    assert "asset.bfa.population.worldpop.2020.1km.original" not in layers
    boundary = layers["asset.bfa.boundary.natural-earth.v5.1.1"]
    population = layers[POPULATION_ID]
    solar = layers[SOLAR_ID]
    assert boundary["publication_status"] == "published"
    assert population["publication_status"] == "published"
    assert population["preview_url"].endswith(".preview.png")
    assert population["unit"] == "persons per pixel"
    assert population["population_total"] == pytest.approx(22811078.2325013)
    assert population["nodata"]["value"] == -99999.0
    assert solar["publication_status"] == "blocked"
    assert solar["data_url"] is None
    assert solar["warning"]


def test_boundary_api_returns_checksum_verified_geojson(client, db_session):
    seed_with_session(db_session)
    response = client.get(
        "/map-assets/asset.bfa.boundary.natural-earth.v5.1.1/data"
    )
    assert response.status_code == 200
    assert response.json()["features"][0]["properties"]["iso_a3"] == "BFA"


def test_blocked_solar_raster_is_not_served(client, db_session):
    seed_with_session(db_session)
    response = client.get(f"/map-assets/{SOLAR_ID}/data")
    assert response.status_code == 409
