import type { MapLayerRecord } from "@/lib/types";

export function layerIsSelectable(layer: MapLayerRecord): boolean {
  return layer.publication_status === "published" && Boolean(layer.data_url);
}

export function layerDisclosure(layer: MapLayerRecord): string {
  if (layerIsSelectable(layer)) return "Validated and published through the AED evidence gate.";
  return layer.warning ?? "Layer is not publication-ready.";
}
