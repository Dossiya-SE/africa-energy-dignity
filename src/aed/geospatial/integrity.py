"""Checksum, geometry, raster-metadata and publication integrity controls."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from shapely.geometry import shape

VERIFIED_STATES = {"cross_checked", "model_ready", "validated"}
KNOWN_LICENCE_MARKERS = {
    "public domain",
    "cc by 4.0",
    "creative commons attribution 4.0",
}


@dataclass(frozen=True)
class BoundaryValidation:
    checksum: str
    crs: str
    bbox: tuple[float, float, float, float]
    geometry_type: str


@dataclass(frozen=True)
class PopulationRasterValidation:
    checksum: str
    crs: str
    bbox: tuple[float, float, float, float]
    nodata: float
    minimum: float
    maximum: float
    valid_pixel_count: int
    nodata_pixel_count: int
    population_total: float
    coverage_ratio: float


def sha256_file(path: Path) -> str:
    """Return a reproducible SHA-256 checksum for exact file bytes."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_sha256(path: Path, expected: str | None) -> str:
    """Verify exact bytes and return the normalized sha256 identifier."""
    if not expected or not expected.startswith("sha256:"):
        raise ValueError("A sha256 checksum is required before asset delivery.")
    actual = f"sha256:{sha256_file(path)}"
    if actual != expected:
        raise ValueError(f"Checksum mismatch: expected {expected}, received {actual}.")
    return actual


def _single_boundary(path: Path, expected_iso: str = "BFA"):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("type") != "FeatureCollection":
        raise ValueError("Boundary asset must be a GeoJSON FeatureCollection.")
    features = payload.get("features") or []
    if len(features) != 1:
        raise ValueError("Boundary asset must contain exactly one country feature.")
    feature = features[0]
    properties = feature.get("properties", {})
    iso = properties.get("iso_a3") or properties.get("ADM0_A3")
    if iso != expected_iso:
        raise ValueError(f"Boundary ISO identifier must equal {expected_iso}.")
    geometry = shape(feature.get("geometry"))
    if geometry.geom_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError("Country boundary must be Polygon or MultiPolygon geometry.")
    if geometry.is_empty or not geometry.is_valid:
        raise ValueError("Country boundary geometry must be non-empty and valid.")
    return payload, feature, geometry


def validate_boundary_geojson(
    path: Path,
    *,
    expected_iso: str = "BFA",
    expected_bbox: tuple[float, float, float, float] = (
        -5.470565,
        9.610835,
        2.177108,
        15.116158,
    ),
) -> BoundaryValidation:
    """Validate a single-country canonical GeoJSON boundary."""
    payload, feature, geometry = _single_boundary(path, expected_iso)
    bounds = tuple(round(value, 6) for value in geometry.bounds)
    if bounds != expected_bbox:
        raise ValueError(f"Unexpected Burkina Faso extent: {bounds}.")
    declared_bbox = tuple(feature.get("bbox") or [])
    if declared_bbox != expected_bbox:
        raise ValueError("Declared GeoJSON bbox does not match validated geometry bounds.")
    crs_name = payload.get("crs", {}).get("properties", {}).get("name")
    if crs_name != "urn:ogc:def:crs:OGC:1.3:CRS84":
        raise ValueError("Canonical boundary must declare OGC:CRS84.")
    return BoundaryValidation(
        checksum=sha256_file(path),
        crs="OGC:CRS84",
        bbox=expected_bbox,
        geometry_type=geometry.geom_type,
    )


def validate_population_raster(
    path: Path,
    boundary_path: Path,
    *,
    unit: str = "persons per pixel",
    expected_epsg: int = 4326,
    minimum_coverage_ratio: float = 0.95,
) -> PopulationRasterValidation:
    """Validate a population GeoTIFF and compute nodata-safe statistics."""
    if unit != "persons per pixel":
        raise ValueError("Population raster units must be persons per pixel.")
    _, _, boundary = _single_boundary(boundary_path)
    with rasterio.open(path) as dataset:
        if dataset.driver != "GTiff":
            raise ValueError("Population raster must use the GeoTIFF driver.")
        if dataset.count != 1:
            raise ValueError("Population raster must contain exactly one band.")
        if dataset.crs is None or dataset.crs.to_epsg() != expected_epsg:
            raise ValueError(f"Population raster CRS must be EPSG:{expected_epsg}.")
        if dataset.nodata is None:
            raise ValueError("Population raster nodata metadata is missing.")

        values = dataset.read(1, masked=True)
        valid = values.compressed().astype("float64", copy=False)
        if valid.size == 0:
            raise ValueError("Population raster contains no valid cells.")
        if not np.isfinite(valid).all():
            raise ValueError("Population raster contains non-finite valid values.")
        if np.any(valid < 0):
            raise ValueError("Population raster contains negative valid values.")

        inside = geometry_mask(
            [boundary.__geo_interface__],
            out_shape=(dataset.height, dataset.width),
            transform=dataset.transform,
            invert=True,
            all_touched=False,
        )
        valid_mask = ~np.ma.getmaskarray(values)
        boundary_pixels = int(inside.sum())
        valid_inside = int((inside & valid_mask).sum())
        if boundary_pixels == 0:
            raise ValueError("Population raster does not overlap Burkina Faso.")
        coverage_ratio = valid_inside / boundary_pixels
        if coverage_ratio < minimum_coverage_ratio:
            raise ValueError(
                "Population raster coverage is incomplete: "
                f"{coverage_ratio:.6f} < {minimum_coverage_ratio:.2f}."
            )
        pixel_count = dataset.width * dataset.height
        return PopulationRasterValidation(
            checksum=sha256_file(path),
            crs=dataset.crs.to_string(),
            bbox=tuple(map(float, dataset.bounds)),
            nodata=float(dataset.nodata),
            minimum=float(np.min(valid)),
            maximum=float(np.max(valid)),
            valid_pixel_count=int(valid.size),
            nodata_pixel_count=int(pixel_count - valid.size),
            population_total=float(np.sum(valid, dtype=np.float64)),
            coverage_ratio=coverage_ratio,
        )


def validate_raster_contract(metadata: dict[str, Any]) -> None:
    """Require metadata needed before a raster may be published."""
    required = ("checksum", "crs", "unit", "nodata", "bbox")
    missing = [name for name in required if metadata.get(name) in (None, "", [])]
    if missing:
        raise ValueError("Raster publication requires: " + ", ".join(missing))
    if metadata["unit"] == "persons per pixel":
        total = metadata.get("population_total")
        coverage = metadata.get("coverage_ratio")
        if total is None or coverage is None:
            raise ValueError(
                "Population raster publication requires population_total and coverage_ratio."
            )
        if float(total) < 0 or float(coverage) < 0.95:
            raise ValueError("Population raster statistics do not pass publication gates.")


def publication_ready(
    *,
    publication_status: str,
    asset_validation_status: str,
    source_verification_status: str,
    evidence_class: str,
    licence: str | None,
    checksum: str | None,
    crs: str | None,
    is_sensitive: bool,
    asset_type: str | None = None,
    bbox: list[float] | None = None,
    nodata: dict[str, Any] | None = None,
    unit: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> bool:
    """Return whether an asset may cross the public-map boundary."""
    licence_normalized = (licence or "").strip().lower()
    licence_known = any(marker in licence_normalized for marker in KNOWN_LICENCE_MARKERS)
    common_ready = all(
        (
            publication_status == "published",
            asset_validation_status in VERIFIED_STATES,
            source_verification_status
            in {"source_verified", "cross_checked", "model_ready", "validated"},
            evidence_class != "unverified",
            licence_known,
            bool(checksum),
            bool(crs),
            not is_sensitive,
        )
    )
    if not common_ready:
        return False
    if (asset_type or "").startswith("raster"):
        contract = {
            "checksum": checksum,
            "crs": crs,
            "unit": unit,
            "nodata": nodata,
            "bbox": bbox,
            "population_total": (metadata or {}).get("population_total"),
            "coverage_ratio": (metadata or {}).get("coverage_ratio"),
        }
        try:
            validate_raster_contract(contract)
        except ValueError:
            return False
    return True
