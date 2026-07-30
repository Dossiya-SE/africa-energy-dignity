"""Generate deterministic release notes from the preserved WorldPop manifest."""
import json
from pathlib import Path

MANIFEST = Path(".evidence/bfa_ppp_2020_1km_Aggregated.manifest.json")
OUTPUT = Path(".evidence/release-notes.md")


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    notes = f"""# GEO-002 WorldPop evidence archive

Official file: `{manifest['official_filename']}`

Source: {manifest['source_locator']}

Licence: {manifest['licence']['name']}

Raw SHA-256: `{manifest['original']['sha256']}`

Canonical COG SHA-256: `{manifest['canonical']['sha256']}`

Population total computed from valid cells: `{manifest['validation']['computed_population_total']}` persons

This prerelease is a controlled evidence archive outside normal Git history. Assets must not be replaced in place; changed upstream bytes require a new evidence version and release tag.
"""
    OUTPUT.write_text(notes, encoding="utf-8")


if __name__ == "__main__":
    main()
