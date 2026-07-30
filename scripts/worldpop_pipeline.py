"""Preserve, inspect, validate and transform the GEO-002 WorldPop raster."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import shutil
import sys
import urllib.request
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from PIL import Image
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rio_cogeo.cogeo import cog_translate, cog_validate
from rio_cogeo.profiles import cog_profiles
from shapely.geometry import shape

OFFICIAL_FILENAME = "bfa_ppp_2020_1km_Aggregated.tif"
CANONICAL_FILENAME = "bfa_ppp_2020_1km_Aggregated.cog.tif"
PREVIEW_FILENAME = "bfa_ppp_2020_1km_Aggregated.preview.png"
MANIFEST_FILENAME = "bfa_ppp_2020_1km_Aggregated.manifest.json"
MIN_COVERAGE_RATIO = 0.95


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_download(url: str, destination: Path) -> dict[str, str | None]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(
            f"Refusing to replace preserved evidence bytes: {destination}"
        )
    partial = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Africa-Energy-Dignity-GEO-002/1.0",
            "Accept": "image/tiff,application/octet-stream;q=0.9,*/*;q=0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response, partial.open(
            "wb"
        ) as output:
            shutil.copyfileobj(response, output, length=1024 * 1024)
            metadata = {
                "resolved_url": response.geturl(),
                "content_type": response.headers.get("Content-Type"),
                "content_length": response.headers.get("Content-Length"),
                "last_modified": response.headers.get("Last-Modified"),
                "etag": response.headers.get("ETag"),
            }
        if partial.stat().st_size == 0:
            raise ValueError("WorldPop download returned an empty file.")
        os.replace(partial, destination)
        return metadata
    finally:
        partial.unlink(missing_ok=True)


def _boundary_geometry(boundary_path: Path):
    payload = json.loads(boundary_path.read_text(encoding="utf-8"))
    features = payload.get("features") or []
    if len(features) != 1:
        raise ValueError("Burkina Faso boundary must contain exactly one feature.")
    feature = features[0]
    if feature.get("properties", {}).get("iso_a3") != "BFA":
        raise ValueError("Boundary feature must identify Burkina Faso as BFA.")
    geometry = shape(feature.get("geometry"))
    if geometry.is_empty or not geometry.is_valid:
        raise ValueError("Burkina Faso boundary geometry is invalid.")
    return geometry


def inspect_raster(path: Path, boundary_path: Path) -> dict[str, Any]:
    boundary = _boundary_geometry(boundary_path)
    with rasterio.open(path) as dataset:
        if dataset.driver != "GTiff":
            raise ValueError(f"Expected GeoTIFF driver, received {dataset.driver}.")
        if dataset.count != 1:
            raise ValueError("WorldPop population raster must contain exactly one band.")
        if dataset.crs is None:
            raise ValueError("Population raster CRS is missing.")
        epsg = dataset.crs.to_epsg()
        if epsg != 4326:
            raise ValueError(f"Expected WGS84 / EPSG:4326, received {dataset.crs}.")
        if dataset.nodata is None:
            raise ValueError("Population raster nodata metadata is missing.")

        values = dataset.read(1, masked=True)
        compressed = values.compressed().astype("float64", copy=False)
        if compressed.size == 0:
            raise ValueError("Population raster contains no valid cells.")
        if not np.isfinite(compressed).all():
            raise ValueError("Population raster contains non-finite valid values.")
        if np.any(compressed < 0):
            minimum = float(compressed.min())
            raise ValueError(f"Population raster contains negative valid values: {minimum}.")

        boundary_mask = geometry_mask(
            [boundary.__geo_interface__],
            out_shape=(dataset.height, dataset.width),
            transform=dataset.transform,
            invert=True,
            all_touched=False,
        )
        valid_mask = ~np.ma.getmaskarray(values)
        boundary_pixels = int(boundary_mask.sum())
        valid_inside_boundary = int((boundary_mask & valid_mask).sum())
        if boundary_pixels == 0:
            raise ValueError("Boundary does not overlap the WorldPop raster grid.")
        coverage_ratio = valid_inside_boundary / boundary_pixels
        if coverage_ratio < MIN_COVERAGE_RATIO:
            raise ValueError(
                "WorldPop raster coverage is incomplete: "
                f"{coverage_ratio:.6f} < {MIN_COVERAGE_RATIO:.2f}."
            )

        west, south, east, north = map(float, dataset.bounds)
        bwest, bsouth, beast, bnorth = boundary.bounds
        x_tolerance = abs(dataset.transform.a) * 2
        y_tolerance = abs(dataset.transform.e) * 2
        bounds_cover_boundary = all(
            (
                west <= bwest + x_tolerance,
                south <= bsouth + y_tolerance,
                east >= beast - x_tolerance,
                north >= bnorth - y_tolerance,
            )
        )
        if not bounds_cover_boundary:
            raise ValueError("Raster bounds do not adequately cover Burkina Faso.")

        transform = dataset.transform
        valid_count = int(compressed.size)
        pixel_count = int(dataset.width * dataset.height)
        total = float(np.sum(compressed, dtype=np.float64))
        minimum = float(np.min(compressed))
        maximum = float(np.max(compressed))

        return {
            "driver": dataset.driver,
            "width": dataset.width,
            "height": dataset.height,
            "band_count": dataset.count,
            "dtype": dataset.dtypes[0],
            "crs": dataset.crs.to_string(),
            "epsg": epsg,
            "affine_transform": [
                float(transform.a),
                float(transform.b),
                float(transform.c),
                float(transform.d),
                float(transform.e),
                float(transform.f),
            ],
            "bounds": [west, south, east, north],
            "resolution_degrees": [abs(float(transform.a)), abs(float(transform.e))],
            "resolution_arcseconds": [
                abs(float(transform.a)) * 3600,
                abs(float(transform.e)) * 3600,
            ],
            "nodata": float(dataset.nodata),
            "minimum_valid_value": minimum,
            "maximum_valid_value": maximum,
            "valid_pixel_count": valid_count,
            "nodata_pixel_count": pixel_count - valid_count,
            "sum_valid_population_cells": total,
            "coverage": {
                "boundary_pixel_count": boundary_pixels,
                "valid_pixels_inside_boundary": valid_inside_boundary,
                "valid_coverage_ratio": coverage_ratio,
                "minimum_required_ratio": MIN_COVERAGE_RATIO,
                "bounds_cover_boundary": bounds_cover_boundary,
            },
        }


def create_cog(source: Path, destination: Path) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"Refusing to replace canonical raster: {destination}")
    profile = cog_profiles.get("deflate").copy()
    profile.update(
        {
            "BLOCKSIZE": 512,
            "BIGTIFF": "IF_SAFER",
            "NUM_THREADS": "ALL_CPUS",
            "PREDICTOR": "FLOATING_POINT",
        }
    )
    cog_translate(
        source,
        destination,
        profile,
        in_memory=False,
        quiet=True,
        overview_resampling="average",
        config={"GDAL_NUM_THREADS": "ALL_CPUS"},
    )
    result = cog_validate(destination, strict=True)
    if isinstance(result, tuple):
        valid, errors, warnings = result
    else:
        valid, errors, warnings = bool(result), [], []
    if not valid:
        raise ValueError(f"Canonical raster failed COG validation: {errors}")
    return {"valid": True, "errors": list(errors), "warnings": list(warnings)}


def compare_raster_semantics(original: dict[str, Any], canonical: dict[str, Any]) -> None:
    exact_keys = (
        "width",
        "height",
        "band_count",
        "dtype",
        "crs",
        "epsg",
        "nodata",
        "valid_pixel_count",
        "nodata_pixel_count",
    )
    for key in exact_keys:
        if original[key] != canonical[key]:
            raise ValueError(f"COG transformation changed required field {key}.")
    for key in ("bounds", "resolution_degrees", "affine_transform"):
        if not np.allclose(original[key], canonical[key], rtol=0, atol=1e-12):
            raise ValueError(f"COG transformation changed spatial field {key}.")
    for key in (
        "minimum_valid_value",
        "maximum_valid_value",
        "sum_valid_population_cells",
    ):
        if not math.isclose(original[key], canonical[key], rel_tol=1e-10, abs_tol=1e-6):
            raise ValueError(f"COG transformation changed population statistic {key}.")


def create_preview(cog_path: Path, destination: Path) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"Refusing to replace preview: {destination}")
    with rasterio.open(cog_path) as dataset:
        scale = min(1.0, 1024 / max(dataset.width, dataset.height))
        width = max(1, int(round(dataset.width * scale)))
        height = max(1, int(round(dataset.height * scale)))
        data = dataset.read(
            1,
            out_shape=(height, width),
            masked=True,
            resampling=Resampling.average,
        )
        mask = np.ma.getmaskarray(data)
        valid = data.compressed().astype("float64", copy=False)
        positive = valid[valid > 0]
        if positive.size == 0:
            low, high = 0.0, 1.0
        else:
            low, high = np.percentile(np.log1p(positive), [2, 98])
            if high <= low:
                high = low + 1.0
        logged = np.log1p(np.ma.filled(data, 0).astype("float64"))
        normalized = np.clip((logged - low) / (high - low), 0, 1)

        rgba = np.zeros((height, width, 4), dtype=np.uint8)
        rgba[..., 0] = (248 - 212 * normalized).astype(np.uint8)
        rgba[..., 1] = (241 - 103 * normalized).astype(np.uint8)
        rgba[..., 2] = (173 - 117 * normalized).astype(np.uint8)
        rgba[..., 3] = np.where(mask, 0, 205).astype(np.uint8)
        Image.fromarray(rgba, mode="RGBA").save(destination, format="PNG", optimize=True)
        return {
            "filename": destination.name,
            "media_type": "image/png",
            "width": width,
            "height": height,
            "bounds": list(map(float, dataset.bounds)),
            "visualization": {
                "scale": "log1p",
                "lower_percentile": 2,
                "upper_percentile": 98,
                "alpha": 205,
                "purpose": "Map visualization derivative; not an analytical raster.",
            },
        }


def software_versions() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "numpy": version("numpy"),
        "rasterio": version("rasterio"),
        "gdal": rasterio.__gdal_version__,
        "rio-cogeo": version("rio-cogeo"),
        "pillow": version("Pillow"),
        "shapely": version("shapely"),
    }


def prepare(args: argparse.Namespace) -> int:
    work_root = args.work_root.resolve()
    raw_path = work_root / "raw" / OFFICIAL_FILENAME
    cog_path = work_root / "canonical" / CANONICAL_FILENAME
    preview_path = work_root / "preview" / PREVIEW_FILENAME
    manifest_path = work_root / MANIFEST_FILENAME

    headers = atomic_download(args.source_url, raw_path)
    retrieved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    original = inspect_raster(raw_path, args.boundary)
    cog_validation = create_cog(raw_path, cog_path)
    canonical = inspect_raster(cog_path, args.boundary)
    compare_raster_semantics(original, canonical)
    preview = create_preview(cog_path, preview_path)

    raw_checksum = sha256_file(raw_path)
    canonical_checksum = sha256_file(cog_path)
    preview_checksum = sha256_file(preview_path)
    release_base = (
        "https://github.com/Dossiya-SE/africa-energy-dignity/releases/download/"
        f"{args.release_tag}"
    )

    manifest = {
        "schema_version": "1.0",
        "evidence_id": "worldpop-bfa-population-2020-1km-aggregated",
        "publisher": "WorldPop, University of Southampton",
        "product_title": "The spatial distribution of population in 2020",
        "product_year": 2020,
        "official_filename": OFFICIAL_FILENAME,
        "source_locator": args.source_url,
        "resolved_locator": headers["resolved_url"],
        "retrieved_at_utc": retrieved_at,
        "retrieval_headers": headers,
        "licence": {
            "identifier": "CC-BY-4.0",
            "name": "Creative Commons Attribution 4.0 International",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "attribution": (
                "WorldPop (School of Geography and Environmental Science, University of "
                "Southampton) and the dataset-specific recommended citation."
            ),
            "recommended_citation": (
                "WorldPop and CIESIN (2018), Global High Resolution Population "
                "Denominators Project, DOI 10.5258/SOTON/WP00647."
            ),
        },
        "model": {
            "type": "Random Forest-based dasymetric redistribution",
            "nominal_resolution": "30 arc-seconds, approximately 1 km at the equator",
            "units": "persons per pixel",
            "coordinate_reference_system_family": "WGS84 geographic coordinates",
        },
        "original": {
            "filename": OFFICIAL_FILENAME,
            "storage_uri": f"{release_base}/{OFFICIAL_FILENAME}",
            "file_size_bytes": raw_path.stat().st_size,
            "sha256": raw_checksum,
            **original,
        },
        "transformation": {
            "name": "GeoTIFF to lossless Cloud Optimized GeoTIFF",
            "command": (
                "python scripts/worldpop_pipeline.py prepare --source-url <official-url> "
                "--boundary data/canonical/boundaries/bfa-natural-earth-5.1.1.geojson "
                "--work-root .evidence --release-tag " + args.release_tag
            ),
            "software_versions": software_versions(),
            "parameters": {
                "driver": "COG",
                "compression": "DEFLATE",
                "block_size": 512,
                "predictor": "FLOATING_POINT",
                "overview_resampling": "average",
                "resolution_preserved": True,
                "crs_preserved": True,
                "nodata_preserved": True,
            },
            "input_sha256": raw_checksum,
            "output_sha256": canonical_checksum,
            "cog_validation": cog_validation,
        },
        "canonical": {
            "filename": CANONICAL_FILENAME,
            "storage_uri": f"{release_base}/{CANONICAL_FILENAME}",
            "file_size_bytes": cog_path.stat().st_size,
            "sha256": canonical_checksum,
            **canonical,
        },
        "preview": {
            **preview,
            "storage_uri": f"{release_base}/{PREVIEW_FILENAME}",
            "file_size_bytes": preview_path.stat().st_size,
            "sha256": preview_checksum,
        },
        "validation": {
            "crs_present_and_usable": True,
            "finite_values": True,
            "non_negative_values": True,
            "nodata_excluded_from_statistics": True,
            "burkina_faso_coverage_passed": True,
            "units_confirmed": "persons per pixel",
            "computed_population_total": original["sum_valid_population_cells"],
            "external_reference_comparison": None,
            "publication_decision": "eligible_for_registry_publication",
        },
        "known_limitations": [
            "Modeled population distribution, not a pixel-level census enumeration.",
            "The source product represents 2020 conditions and should not be treated as current population.",
            "People-per-pixel values depend on WorldPop input data and Random-Forest dasymetric redistribution.",
            "The PNG preview is a log-scaled visualization derivative and must not be used for quantitative analysis.",
            "No external reference population total is asserted in this validation; the recorded total is computed from valid raster cells only.",
        ],
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "manifest": str(manifest_path),
        "raw": str(raw_path),
        "canonical": str(cog_path),
        "preview": str(preview_path),
        "raw_sha256": raw_checksum,
        "canonical_sha256": canonical_checksum,
        "preview_sha256": preview_checksum,
        "population_total": original["sum_valid_population_cells"],
        "coverage_ratio": original["coverage"]["valid_coverage_ratio"],
    }, sort_keys=True))
    return 0


def _lookup(payload: dict[str, Any], dotted_key: str) -> Any:
    current: Any = payload
    for part in dotted_key.split("."):
        current = current[part]
    return current


def compare(args: argparse.Namespace) -> int:
    expected = json.loads(args.expected.read_text(encoding="utf-8"))
    actual = json.loads(args.actual.read_text(encoding="utf-8"))
    critical = (
        "evidence_id",
        "source_locator",
        "official_filename",
        "licence.identifier",
        "model.units",
        "original.sha256",
        "original.file_size_bytes",
        "original.crs",
        "original.nodata",
        "original.valid_pixel_count",
        "original.sum_valid_population_cells",
        "canonical.sha256",
        "canonical.file_size_bytes",
        "preview.sha256",
        "validation.publication_decision",
    )
    differences = [
        key for key in critical if _lookup(expected, key) != _lookup(actual, key)
    ]
    if differences:
        raise ValueError(
            "Official WorldPop bytes or deterministic outputs changed; create a new "
            "evidence version instead of replacing preserved assets: "
            + ", ".join(differences)
        )
    print("Existing release manifest matches the newly retrieved official bytes.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--source-url", required=True)
    prepare_parser.add_argument("--boundary", type=Path, required=True)
    prepare_parser.add_argument("--work-root", type=Path, required=True)
    prepare_parser.add_argument("--release-tag", required=True)
    prepare_parser.set_defaults(function=prepare)

    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--expected", type=Path, required=True)
    compare_parser.add_argument("--actual", type=Path, required=True)
    compare_parser.set_defaults(function=compare)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.function(args)


if __name__ == "__main__":
    sys.exit(main())
