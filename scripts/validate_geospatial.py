"""Validate committed canonical GEO-002 assets without network access."""
from pathlib import Path

from aed.geospatial.integrity import validate_boundary_geojson

EXPECTED = "2dcb37ce024c79b9ef5d7e4aaa73763755d3073bba872b962333dffc45764b81"


def main() -> None:
    result = validate_boundary_geojson(
        Path("data/canonical/boundaries/bfa-natural-earth-5.1.1.geojson")
    )
    if result.checksum != EXPECTED:
        raise SystemExit("Canonical Burkina Faso boundary checksum changed.")
    print("GEO-002 canonical boundary validation passed.")


if __name__ == "__main__":
    main()
