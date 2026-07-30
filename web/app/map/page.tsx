import { MapShell } from "@/components/map-shell";
import { Notice } from "@/components/notice";
import { getMapAssets } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function MapPage() {
  const result = await getMapAssets();
  const apiBaseUrl = (
    process.env.NEXT_PUBLIC_AED_API_URL ??
    process.env.AED_API_URL ??
    "http://localhost:8000"
  ).replace(/\/$/, "");

  return (
    <>
      <header className="page-heading">
        <p className="eyebrow">Geography Studio</p>
        <h1>Burkina Faso verified evidence map</h1>
        <p>
          Only assets that pass provenance, licence, checksum, CRS and validation controls can be
          rendered. Blocked layers remain visible in the catalogue with their unresolved risks.
        </p>
      </header>
      {result.error ? (
        <Notice title="Geospatial registry unavailable" tone="warning">
          <p>{result.error}</p>
        </Notice>
      ) : null}
      <MapShell layers={result.data ?? []} apiBaseUrl={apiBaseUrl} />
    </>
  );
}
