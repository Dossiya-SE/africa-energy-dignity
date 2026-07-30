import { describe, expect, it } from "vitest";

import {
  layerCoordinates,
  layerDisclosure,
  layerIsSelectable,
} from "@/lib/map-layers";
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
  nodata: null,
  checksum: "sha256:test",
  spatial_resolution: "1:110m",
  temporal_coverage: "5.1.1",
  product_year: null,
  model_type: null,
  population_total: null,
  coverage_ratio: null,
  file_size_bytes: null,
  manifest_url: null,
  rendering_method: "geojson",
  data_url: "/map-assets/asset.bfa.boundary/data",
  preview_url: null,
  warning: null,
};

describe("geospatial publication presentation", () => {
  it("allows a published boundary with a controlled data endpoint", () => {
    expect(layerIsSelectable(baseLayer)).toBe(true);
    expect(layerDisclosure(baseLayer)).toContain("Validated");
  });

  it("allows a published WorldPop image overlay", () => {
    const population: MapLayerRecord = {
      ...baseLayer,
      asset_id: "asset.bfa.population.worldpop.2020.1km.cog",
      asset_type: "raster_population_cog",
      rendering_method: "image",
      data_url: "/map-assets/population/data",
      preview_url: "/evidence/population.preview.png",
      unit: "persons per pixel",
      nodata: { value: -99999, excluded_from_statistics: true },
      population_total: 22811078.2325013,
      product_year: 2020,
    };
    expect(layerIsSelectable(population)).toBe(true);
    expect(layerCoordinates(population)).toEqual([
      [-5.47, 15.12],
      [2.18, 15.12],
      [2.18, 9.61],
      [-5.47, 9.61],
    ]);
  });

  it("keeps the incomplete solar candidate blocked", () => {
    const blocked: MapLayerRecord = {
      ...baseLayer,
      asset_id: "asset.bfa.solar.gsa.ghi.2020",
      publication_status: "blocked",
      rendering_method: "image",
      data_url: null,
      preview_url: null,
      warning: "Checksum and nodata remain unverified.",
    };
    expect(layerIsSelectable(blocked)).toBe(false);
    expect(layerDisclosure(blocked)).toBe(blocked.warning);
  });
});
