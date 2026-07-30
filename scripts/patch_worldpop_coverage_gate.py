"""Apply audited GEO-002 WorldPop pipeline corrections idempotently."""
from pathlib import Path

TARGET = Path("scripts/worldpop_pipeline.py")
OLD_FAILURE = '''        if not bounds_cover_boundary:\n            raise ValueError("Raster bounds do not adequately cover Burkina Faso.")\n'''
NEW_DIAGNOSTIC = '''        # Valid-cell coverage is the acceptance gate. The rectangular bounds\n        # comparison is retained as a diagnostic because WorldPop and Natural\n        # Earth use independently generalized national outlines.\n'''
OLD_RESULT = '''                "bounds_cover_boundary": bounds_cover_boundary,\n'''
NEW_RESULT = '''                "bounds_cover_generalized_boundary": bounds_cover_boundary,\n                "raster_bounds": [west, south, east, north],\n                "reference_boundary_bounds": [\n                    float(bwest),\n                    float(bsouth),\n                    float(beast),\n                    float(bnorth),\n                ],\n                "coverage_method": (\n                    "valid raster cell centres inside the reference boundary divided "\n                    "by all reference-boundary cell centres on the raster grid"\n                ),\n'''
OLD_PROFILE_PREDICTOR = '''            "PREDICTOR": "FLOATING_POINT",\n'''
NEW_PROFILE_PREDICTOR = '''            "PREDICTOR": 3,\n'''
OLD_MANIFEST_PREDICTOR = '''                "predictor": "FLOATING_POINT",\n'''
NEW_MANIFEST_PREDICTOR = '''                "predictor": 3,\n                "predictor_definition": "TIFF floating-point predictor",\n'''


def main() -> None:
    content = TARGET.read_text(encoding="utf-8")
    changes: list[str] = []

    coverage_updated = (
        NEW_DIAGNOSTIC in content
        and '"bounds_cover_generalized_boundary"' in content
    )
    if not coverage_updated:
        if OLD_FAILURE not in content or OLD_RESULT not in content:
            raise RuntimeError("Expected WorldPop coverage-gate source block was not found.")
        content = content.replace(OLD_FAILURE, NEW_DIAGNOSTIC, 1)
        content = content.replace(OLD_RESULT, NEW_RESULT, 1)
        changes.append("coverage gate")

    predictor_updated = (
        NEW_PROFILE_PREDICTOR in content
        and NEW_MANIFEST_PREDICTOR in content
    )
    if not predictor_updated:
        if (
            OLD_PROFILE_PREDICTOR not in content
            or OLD_MANIFEST_PREDICTOR not in content
        ):
            raise RuntimeError("Expected WorldPop COG predictor source block was not found.")
        content = content.replace(
            OLD_PROFILE_PREDICTOR,
            NEW_PROFILE_PREDICTOR,
            1,
        )
        content = content.replace(
            OLD_MANIFEST_PREDICTOR,
            NEW_MANIFEST_PREDICTOR,
            1,
        )
        changes.append("COG predictor")

    TARGET.write_text(content, encoding="utf-8")
    if changes:
        print("WorldPop pipeline corrections applied: " + ", ".join(changes) + ".")
    else:
        print("WorldPop pipeline corrections are already applied.")


if __name__ == "__main__":
    main()
