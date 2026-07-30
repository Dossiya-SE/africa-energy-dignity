"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import styles from "@/components/map-shell.module.css";
import { layerDisclosure, layerIsSelectable } from "@/lib/map-layers";
import type { MapLayerRecord } from "@/lib/types";

const DEMO_STYLE_URL = "https://demotiles.maplibre.org/style.json";

interface MapShellProps {
  layers: MapLayerRecord[];
  apiBaseUrl: string;
}

export function MapShell({ layers, apiBaseUrl }: MapShellProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const published = useMemo(() => layers.filter(layerIsSelectable), [layers]);
  const [selectedId, setSelectedId] = useState<string | null>(published[0]?.asset_id ?? null);
  const [mapError, setMapError] = useState<string | null>(null);
  const selected = layers.find((layer) => layer.asset_id === selectedId) ?? layers[0] ?? null;

  useEffect(() => {
    if (!containerRef.current) return;
    let disposed = false;
    let map: import("maplibre-gl").Map | null = null;

    async function initializeMap() {
      try {
        const { Map, NavigationControl } = await import("maplibre-gl");
        if (disposed || !containerRef.current) return;
        map = new Map({
          container: containerRef.current,
          style: DEMO_STYLE_URL,
          center: [-1.5, 12.3],
          zoom: 4.7,
          attributionControl: { compact: true },
        });
        map.addControl(new NavigationControl({ visualizePitch: true }), "top-right");
        map.on("load", async () => {
          try {
            for (const layer of published) {
              if (!layer.data_url || disposed) continue;
              const response = await fetch(`${apiBaseUrl}${layer.data_url}`, {
                headers: { Accept: "application/geo+json, application/json" },
              });
              if (!response.ok) throw new Error(`AED API rejected ${layer.name}.`);
              const data = (await response.json()) as import("geojson").FeatureCollection;
              const sourceId = `source-${layer.asset_id}`;
              map?.addSource(sourceId, { type: "geojson", data });
              map?.addLayer({
                id: `fill-${layer.asset_id}`,
                type: "fill",
                source: sourceId,
                paint: { "fill-color": "#0b6b4f", "fill-opacity": 0.18 },
              });
              map?.addLayer({
                id: `line-${layer.asset_id}`,
                type: "line",
                source: sourceId,
                paint: { "line-color": "#064c39", "line-width": 2.4 },
              });
              if (layer.bbox?.length === 4) {
                map?.fitBounds(
                  [
                    [layer.bbox[0], layer.bbox[1]],
                    [layer.bbox[2], layer.bbox[3]],
                  ],
                  { padding: 55, duration: 0 },
                );
              }
            }
          } catch (error) {
            setMapError(error instanceof Error ? error.message : "Evidence layer failed.");
          }
        });
        map.on("error", (event) => {
          setMapError(event.error?.message ?? "Map rendering failed.");
        });
      } catch (error) {
        setMapError(error instanceof Error ? error.message : "Map initialization failed.");
      }
    }

    void initializeMap();
    return () => {
      disposed = true;
      map?.remove();
    };
  }, [apiBaseUrl, published]);

  return (
    <section className={styles.workspace} aria-label="AED geographic workspace">
      <aside className={styles.panel}>
        <p className="eyebrow">Evidence layers</p>
        <h2>Publication gate</h2>
        <div className={styles.list}>
          {layers.map((layer) => {
            const enabled = layerIsSelectable(layer);
            return (
              <button
                className={`${styles.option} ${selectedId === layer.asset_id ? styles.selected : ""}`}
                disabled={!enabled}
                key={layer.asset_id}
                onClick={() => setSelectedId(layer.asset_id)}
                type="button"
              >
                <strong>{layer.name}</strong>
                <span>{enabled ? "Published" : "Blocked"}</span>
              </button>
            );
          })}
        </div>
        {selected ? (
          <div className={styles.provenance}>
            <h3>{selected.name}</h3>
            <dl className="compact-metadata">
              <div><dt>Publisher</dt><dd>{selected.original_publisher}</dd></div>
              <div><dt>Licence</dt><dd>{selected.licence}</dd></div>
              <div><dt>Version</dt><dd>{selected.dataset_version ?? "Unknown"}</dd></div>
              <div><dt>Resolution</dt><dd>{selected.spatial_resolution ?? "Unknown"}</dd></div>
              <div><dt>Evidence</dt><dd>{selected.evidence_class}</dd></div>
              <div><dt>Validation</dt><dd>{selected.validation_status}</dd></div>
            </dl>
            <p>{layerDisclosure(selected)}</p>
          </div>
        ) : null}
      </aside>
      <div className="map-frame">
        <div ref={containerRef} className="map-canvas" />
        <div className="map-disclosure">
          <strong>Validated AED boundary layer.</strong>
          <span>
            The boundary is a generalized Natural Earth 1:110m public-domain asset. The external
            basemap remains cartographic context and is not an AED evidence source.
          </span>
        </div>
        {mapError ? (
          <div className="map-error" role="alert">
            Map unavailable: {mapError}
          </div>
        ) : null}
      </div>
    </section>
  );
}
