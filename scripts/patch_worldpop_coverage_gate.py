"""Apply the GEO-002 coverage-gate correction idempotently."""
from pathlib import Path

TARGET = Path("scripts/worldpop_pipeline.py")
OLD_FAILURE = '''        if not bounds_cover_boundary:\n            raise ValueError("Raster bounds do not adequately cover Burkina Faso.")\n'''
NEW_DIAGNOSTIC = '''        # Valid-cell coverage is the acceptance gate. The rectangular bounds\n        # comparison is retained as a diagnostic because WorldPop and Natural\n        # Earth use independently generalized national outlines.\n'''
OLD_RESULT = '''                "bounds_cover_boundary": bounds_cover_boundary,\n'''
NEW_RESULT = '''                "bounds_cover_generalized_boundary": bounds_cover_boundary,\n                "raster_bounds": [west, south, east, north],\n                "reference_boundary_bounds": [\n                    float(bwest),\n                    float(bsouth),\n                    float(beast),\n                    float(bnorth),\n                ],\n                "coverage_method": (\n                    "valid raster cell centres inside the reference boundary divided "\n                    "by all reference-boundary cell centres on the raster grid"\n                ),\n'''


def main() -> None:
    content = TARGET.read_text(encoding="utf-8")
    already_updated = (
        NEW_DIAGNOSTIC in content
        and '"bounds_cover_generalized_boundary"' in content
    )
    if already_updated:
        print("WorldPop coverage gate is already corrected.")
        return
    if OLD_FAILURE not in content or OLD_RESULT not in content:
        raise RuntimeError("Expected WorldPop coverage-gate source block was not found.")
    content = content.replace(OLD_FAILURE, NEW_DIAGNOSTIC, 1)
    content = content.replace(OLD_RESULT, NEW_RESULT, 1)
    TARGET.write_text(content, encoding="utf-8")
    print("WorldPop coverage gate updated; rectangular bounds retained as diagnostics.")


if __name__ == "__main__":
    main()
