import Link from "next/link";

import { Notice } from "@/components/notice";
import { StatusBadge } from "@/components/status-badge";
import { getAssets, getGeographies, getInstitutions, getSources } from "@/lib/api";
import { humanize, verificationTone } from "@/lib/presentation";

export const dynamic = "force-dynamic";

export default async function BurkinaFasoPage() {
  const [geographiesResult, institutionsResult, sourcesResult, assetsResult] =
    await Promise.all([getGeographies(), getInstitutions(), getSources(), getAssets()]);

  const geography = geographiesResult.data?.find(
    (record) => record.id === "geo.bfa" || record.iso_code === "BFA",
  );
  const institutions = (institutionsResult.data ?? []).filter(
    (record) => record.country_code === "BFA" || record.id === "institution.wapp",
  );
  const sources = (sourcesResult.data ?? []).filter((record) =>
    record.geographic_coverage.includes("geo.bfa"),
  );
  const assets = (assetsResult.data ?? []).filter(
    (record) => record.geography_id === geography?.id,
  );
  const errors = [
    geographiesResult.error,
    institutionsResult.error,
    sourcesResult.error,
    assetsResult.error,
  ].filter(Boolean);

  return (
    <>
      <header className="page-heading">
        <p className="eyebrow">Country workspace</p>
        <h1>Burkina Faso</h1>
        <p>
          The first AED demonstration workspace connects controlled institutional records,
          source candidates and verified geospatial assets without converting unknowns into
          conclusions.
        </p>
      </header>

      {errors.length > 0 ? (
        <Notice title="Some registry services are unavailable" tone="warning">
          <p>{errors.join(" ")}</p>
        </Notice>
      ) : null}

      <section className="card-grid" aria-label="Burkina Faso registry summary">
        <article className="card">
          <p className="card-kicker">Geography</p>
          <h2>{geography?.name ?? "Not registered"}</h2>
          <p>
            Stable ID: <strong>{geography?.id ?? "Unknown"}</strong>
          </p>
          <StatusBadge tone={geography ? "positive" : "warning"}>
            {geography ? humanize(geography.geometry_status) : "Missing"}
          </StatusBadge>
        </article>
        <article className="card">
          <p className="card-kicker">Institutions</p>
          <h2>{institutions.length} controlled records</h2>
          <p>This is a registry count, not a count of all relevant institutions.</p>
          <Link className="text-link" href="/institutions">
            Inspect institutions
          </Link>
        </article>
        <article className="card">
          <p className="card-kicker">Evidence</p>
          <h2>{sources.length} source records</h2>
          <p>Candidate records remain visibly unverified until their original terms are checked.</p>
          <Link className="text-link" href="/evidence">
            Inspect sources
          </Link>
        </article>
      </section>

      <section className="section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Geospatial readiness</p>
            <h2>Registered map assets</h2>
          </div>
        </div>
        {assets.length === 0 ? (
          <section className="empty-state">
            <h2>No verified Burkina Faso asset is available</h2>
            <p>
              The map remains a cartographic shell until DATA work registers an authorized,
              licensed and traceable boundary or thematic asset.
            </p>
            <Link className="text-link" href="/map">
              Open map shell
            </Link>
          </section>
        ) : (
          <div className="card-grid">
            {assets.map((asset) => (
              <article className="card" key={asset.id}>
                <p className="card-kicker">{asset.asset_type}</p>
                <h2>{asset.name}</h2>
                <StatusBadge tone={verificationTone(asset.validation_status)}>
                  {humanize(asset.validation_status)}
                </StatusBadge>
                <p>{asset.spatial_resolution ?? "Spatial resolution not recorded"}</p>
              </article>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
