import { describe, expect, it } from "vitest";

import { layerDisclosure, layerIsSelectable } from "@/lib/map-layers";
import type { MapLayerRecord } from "@/lib/types";

const baseLayer: MapLayerRecord = {
  asset_id: "asset.bfa.boundary",
  name: "Burkina Faso national boundary",
  asset_type: "vector_boundary",
  geography_id: "geo.bfa",
  publication_status: "published",
  validation_status: "validated",
  evidence_class: "published",
  source_id: "source.natural-earth",
  source_title: "Natural Earth Admin 0",
  original_publisher: "Natural Earth",
  source_url: "https://www.naturalearthdata.com",
  access_date: "2026-07-30",
  licence: "Public domain",
  attribution_requirements: "Made with Natural Earth",
  known_limitations: ["Generalized geometry"],
  dataset_id: "dataset.natural-earth",
  dataset_version: "5.1.1",
  unit: null,
  crs: "OGC:CRS84",
  bbox: [-5.47, 9.61, 2.18, 15.12],
  checksum: "sha256:test",
  spatial_resolution: "1:110m",
  temporal_coverage: "5.1.1",
  data_url: "/map-assets/asset.bfa.boundary/data",
  warning: null,
};

describe("geospatial publication presentation", () => {
  it("allows only published layers with a controlled data endpoint", () => {
    expect(layerIsSelectable(baseLayer)).toBe(true);
    expect(layerDisclosure(baseLayer)).toContain("Validated");
  });

  it("keeps incomplete raster candidates blocked", () => {
    const blocked = {
      ...baseLayer,
      publication_status: "blocked" as const,
      data_url: null,
      warning: "Checksum and nodata remain unverified.",
    };
    expect(layerIsSelectable(blocked)).toBe(false);
    expect(layerDisclosure(blocked)).toBe(blocked.warning);
  });
});
