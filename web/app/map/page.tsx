import { MapShell } from "@/components/map-shell";

export default function MapPage() {
  return (
    <>
      <header className="page-heading">
        <p className="eyebrow">Geography Studio</p>
        <h1>Map workspace</h1>
        <p>
          The basemap provides geographic orientation only. AED evidence layers will appear only
          after source, licence, temporal, spatial and validation requirements are satisfied.
        </p>
      </header>
      <MapShell />
    </>
  );
}
