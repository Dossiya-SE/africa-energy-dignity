"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import styles from "@/components/map-shell.module.css";
import {
  layerCoordinates,
  layerDisclosure,
  layerIsSelectable,
} from "@/lib/map-layers";
import type { MapLayerRecord } from "@/lib/types";

const DEMO_STYLE_URL = "https://demotiles.maplibre.org/style.json";

interface MapShellProps {
  layers: MapLayerRecord[];
  apiBaseUrl: string;
}

export function MapShell({ layers, apiBaseUrl }: MapShellProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<import("maplibre-gl").Map | null>(null);
  const published = useMemo(() => layers.filter(layerIsSelectable), [layers]);
  const initial =
    published.find((layer) => layer.asset_type.startsWith("raster_population")) ??
    published[0] ??
    null;
  const [selectedId, setSelectedId] = useState<string | null>(initial?.asset_id ?? null);
  const [mapError, setMapError] = useState<string | null>(null);
  const selected = layers.find((layer) => layer.asset_id === selectedId) ?? layers[0] ?? null;

  useEffect(() => {
    if (!containerRef.current) return;
    let disposed = false;

    async function initializeMap() {
      try {
        const { Map, NavigationControl } = await import("maplibre-gl");
        if (disposed || !containerRef.current) return;
        const map = new Map({
          container: containerRef.current,
          style: DEMO_STYLE_URL,
          center: [-1.5, 12.3],
          zoom: 4.7,
          attributionControl: { compact: true },
        });
        mapRef.current = map;
        map.addControl(new NavigationControl({ visualizePitch: true }), "top-right");
        map.on("load", async () => {
          try {
            for (const layer of published) {
              if (disposed) return;
              const sourceId = `source-${layer.asset_id}`;
              if (layer.rendering_method === "image") {
                const coordinates = layerCoordinates(layer);
                if (!layer.preview_url || !coordinates) continue;
                map.addSource(sourceId, {
                  type: "image",
                  url: layer.preview_url,
                  coordinates,
                });
                map.addLayer({
                  id: `image-${layer.asset_id}`,
                  type: "raster",
                  source: sourceId,
                  layout: {
                    visibility: layer.asset_id === selectedId ? "visible" : "none",
                  },
                  paint: { "raster-opacity": 0.72 },
                });
                continue;
              }

              if (!layer.data_url) continue;
              const response = await fetch(`${apiBaseUrl}${layer.data_url}`, {
                headers: { Accept: "application/geo+json, application/json" },
              });
              if (!response.ok) throw new Error(`AED API rejected ${layer.name}.`);
              const data = (await response.json()) as import("geojson").FeatureCollection;
              map.addSource(sourceId, { type: "geojson", data });
              map.addLayer({
                id: `fill-${layer.asset_id}`,
                type: "fill",
                source: sourceId,
                paint: { "fill-color": "#0b6b4f", "fill-opacity": 0.1 },
              });
              map.addLayer({
                id: `line-${layer.asset_id}`,
                type: "line",
                source: sourceId,
                paint: { "line-color": "#064c39", "line-width": 2.4 },
              });
              if (layer.bbox?.length === 4) {
                map.fitBounds(
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
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [apiBaseUrl, published, selectedId]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map?.isStyleLoaded()) return;
    for (const layer of published.filter((item) => item.rendering_method === "image")) {
      const layerId = `image-${layer.asset_id}`;
      if (map.getLayer(layerId)) {
        map.setLayoutProperty(
          layerId,
          "visibility",
          layer.asset_id === selectedId ? "visible" : "none",
        );
      }
    }
  }, [published, selectedId]);

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
              <div><dt>Year</dt><dd>{selected.product_year ?? selected.temporal_coverage ?? "Unknown"}</dd></div>
              <div><dt>Resolution</dt><dd>{selected.spatial_resolution ?? "Unknown"}</dd></div>
              <div><dt>Units</dt><dd>{selected.unit ?? "Not applicable"}</dd></div>
              <div><dt>CRS</dt><dd>{selected.crs ?? "Unknown"}</dd></div>
              <div><dt>Nodata</dt><dd>{selected.nodata?.value ?? "Not applicable"}</dd></div>
              <div><dt>Population total</dt><dd>{selected.population_total?.toLocaleString(undefined, { maximumFractionDigits: 3 }) ?? "Not applicable"}</dd></div>
              <div><dt>Checksum</dt><dd>{selected.checksum ?? "Missing"}</dd></div>
              <div><dt>Validation</dt><dd>{selected.validation_status}</dd></div>
            </dl>
            <p>{layerDisclosure(selected)}</p>
            {selected.known_limitations.length > 0 ? (
              <ul className="limitations-list">
                {selected.known_limitations.map((limitation) => (
                  <li key={limitation}>{limitation}</li>
                ))}
              </ul>
            ) : null}
          </div>
        ) : null}
      </aside>
      <div className="map-frame">
        <div ref={containerRef} className="map-canvas" />
        <div className="map-disclosure">
          <strong>Validated Burkina Faso evidence layers.</strong>
          <span>
            The national boundary and WorldPop 2020 population layer passed AED provenance,
            checksum and validation gates. The solar control remains blocked. The external
            basemap is cartographic context only.
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
