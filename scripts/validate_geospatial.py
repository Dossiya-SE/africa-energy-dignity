"""Validate committed canonical GEO-002 assets and evidence manifests offline."""
import json
from pathlib import Path

from aed.geospatial.integrity import validate_boundary_geojson, validate_raster_contract

BOUNDARY_SHA = "2dcb37ce024c79b9ef5d7e4aaa73763755d3073bba872b962333dffc45764b81"
RAW_SHA = "1126f07b5f1b12872d4b20e58dcdf2cef27c1453c682ebdd3109804624c10a3b"
COG_SHA = "b8aa164c8e56190ebb6875458fdbf86ad044b266b75aaebe014739b5834bd3b1"
MANIFEST = Path("data/manifests/bfa_ppp_2020_1km_Aggregated.manifest.json")


def main() -> None:
    boundary = validate_boundary_geojson(
        Path("data/canonical/boundaries/bfa-natural-earth-5.1.1.geojson")
    )
    if boundary.checksum != BOUNDARY_SHA:
        raise SystemExit("Canonical Burkina Faso boundary checksum changed.")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    original = manifest["original"]
    canonical = manifest["canonical"]
    validation = manifest["validation"]
    if original["sha256"] != RAW_SHA or canonical["sha256"] != COG_SHA:
        raise SystemExit("WorldPop preserved checksums changed.")
    if manifest["official_filename"] != "bfa_ppp_2020_1km_Aggregated.tif":
        raise SystemExit("WorldPop official filename changed.")
    if manifest["licence"]["identifier"] != "CC-BY-4.0":
        raise SystemExit("WorldPop licence metadata is incomplete.")
    if not manifest["transformation"]["cog_validation"]["valid"]:
        raise SystemExit("WorldPop canonical raster is not a valid COG.")
    if validation["publication_decision"] != "eligible_for_registry_publication":
        raise SystemExit("WorldPop publication decision is not validated.")
    validate_raster_contract(
        {
            "checksum": f"sha256:{canonical['sha256']}",
            "crs": canonical["crs"],
            "unit": manifest["model"]["units"],
            "nodata": {"value": canonical["nodata"]},
            "bbox": canonical["bounds"],
            "population_total": canonical["sum_valid_population_cells"],
            "coverage_ratio": canonical["coverage"]["valid_coverage_ratio"],
        }
    )
    print("GEO-002 boundary and WorldPop manifest validation passed.")


if __name__ == "__main__":
    main()
