"use client";

import { useEffect, useRef, useState } from "react";

const DEMO_STYLE_URL = "https://demotiles.maplibre.org/style.json";

export function MapShell() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [mapError, setMapError] = useState<string | null>(null);

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
          attributionControl: true,
        });
        map.addControl(new NavigationControl({ visualizePitch: true }), "top-right");
        map.on("error", (event) => {
          const message = event.error?.message ?? "Map rendering failed.";
          setMapError(message);
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
  }, []);

  return (
    <section className="map-frame" aria-label="AED geographic workspace">
      <div ref={containerRef} className="map-canvas" />
      <div className="map-disclosure">
        <strong>No verified AED boundary layer is displayed.</strong>
        <span>
          The external demonstration basemap is cartographic context only and is not an AED
          evidence source.
        </span>
      </div>
      {mapError ? (
        <div className="map-error" role="alert">
          Map unavailable: {mapError}
        </div>
      ) : null}
    </section>
  );
}
