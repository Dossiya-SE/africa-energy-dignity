"""Checksum, geometry, raster-metadata and publication integrity controls."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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


def sha256_file(path: Path) -> str:
    """Return a reproducible SHA-256 checksum for exact file bytes."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("type") != "FeatureCollection":
        raise ValueError("Boundary asset must be a GeoJSON FeatureCollection.")
    features = payload.get("features") or []
    if len(features) != 1:
        raise ValueError("Boundary asset must contain exactly one country feature.")
    feature = features[0]
    if feature.get("properties", {}).get("iso_a3") != expected_iso:
        raise ValueError(f"Boundary ISO identifier must equal {expected_iso}.")
    geometry = shape(feature.get("geometry"))
    if geometry.geom_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError("Country boundary must be Polygon or MultiPolygon geometry.")
    if geometry.is_empty or not geometry.is_valid:
        raise ValueError("Country boundary geometry must be non-empty and valid.")
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


def validate_raster_contract(metadata: dict[str, Any]) -> None:
    """Require the metadata needed before a raster may be published."""
    required = ("checksum", "crs", "unit", "nodata", "bbox")
    missing = [name for name in required if metadata.get(name) in (None, "", [])]
    if missing:
        raise ValueError("Raster publication requires: " + ", ".join(missing))


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
) -> bool:
    """Return whether an asset may cross the public-map boundary."""
    licence_normalized = (licence or "").strip().lower()
    licence_known = any(marker in licence_normalized for marker in KNOWN_LICENCE_MARKERS)
    return all(
        (
            publication_status == "published",
            asset_validation_status in VERIFIED_STATES,
            source_verification_status in {
                "source_verified",
                "cross_checked",
                "model_ready",
                "validated",
            },
            evidence_class != "unverified",
            licence_known,
            bool(checksum),
            bool(crs),
            not is_sensitive,
        )
    )
