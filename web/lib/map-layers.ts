import type { MapLayerRecord } from "@/lib/types";

export function layerIsSelectable(layer: MapLayerRecord): boolean {
  return (
    layer.publication_status === "published" &&
    Boolean(layer.data_url || layer.preview_url)
  );
}

export function layerDisclosure(layer: MapLayerRecord): string {
  if (layerIsSelectable(layer)) {
    return "Validated and published through the AED evidence gate.";
  }
  return layer.warning ?? "Layer is not publication-ready.";
}

export function layerCoordinates(
  layer: MapLayerRecord,
): [[number, number], [number, number], [number, number], [number, number]] | null {
  if (!layer.bbox || layer.bbox.length !== 4) return null;
  const [west, south, east, north] = layer.bbox;
  return [
    [west, north],
    [east, north],
    [east, south],
    [west, south],
  ];
}
