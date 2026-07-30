import Link from "next/link";

import { Notice } from "@/components/notice";
import { StatusBadge } from "@/components/status-badge";
import { getHealth, getReadiness } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [health, readiness] = await Promise.all([getHealth(), getReadiness()]);
  const apiOnline = health.data?.status === "ok";
  const databaseReady = readiness.data?.status === "ready";

  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Africa Energy Dignity Studio</p>
          <h1>Evidence before infrastructure decisions.</h1>
          <p>
            A sovereign workspace for tracing African energy evidence from original publisher
            through validation, geography, engineering and later public decisions.
          </p>
          <div className="hero-actions">
            <Link className="button" href="/evidence">
              Explore evidence
            </Link>
            <Link className="button-secondary" href="/burkina-faso">
              Open Burkina Faso
            </Link>
          </div>
        </div>
        <aside className="hero-panel" aria-label="Platform status">
          <p className="eyebrow">Runtime status</p>
          <h2>Executable foundation</h2>
          <dl className="metric-list">
            <div>
              <dt>Registry API</dt>
              <dd>
                <StatusBadge tone={apiOnline ? "positive" : "negative"}>
                  {apiOnline ? "Online" : "Unavailable"}
                </StatusBadge>
              </dd>
            </div>
            <div>
              <dt>PostgreSQL/PostGIS</dt>
              <dd>
                <StatusBadge tone={databaseReady ? "positive" : "negative"}>
                  {databaseReady ? "Ready" : "Unavailable"}
                </StatusBadge>
              </dd>
            </div>
            <div>
              <dt>Product phase</dt>
              <dd>Evidence and Geography MVP</dd>
            </div>
          </dl>
        </aside>
      </section>

      {!apiOnline || !databaseReady ? (
        <Notice title="Registry connection is incomplete" tone="warning">
          <p>
            AED Studio is not substituting example values. Start the API and database to display
            controlled registry records.
          </p>
        </Notice>
      ) : null}

      <section className="section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">First operational workspaces</p>
            <h2>Traceable evidence, visible uncertainty</h2>
          </div>
        </div>
        <div className="card-grid">
          <article className="card">
            <p className="card-kicker">Evidence</p>
            <h2>Source catalogue</h2>
            <p>
              Inspect publishers, licences, temporal coverage, limitations and verification
              states without converting candidates into facts.
            </p>
            <Link className="text-link" href="/evidence">
              Open catalogue
            </Link>
          </article>
          <article className="card">
            <p className="card-kicker">Institutions</p>
            <h2>African authority first</h2>
            <p>
              Track national and regional institutions separately from platforms that merely
              display their data.
            </p>
            <Link className="text-link" href="/institutions">
              View institutions
            </Link>
          </article>
          <article className="card">
            <p className="card-kicker">Geography</p>
            <h2>Map with evidence gates</h2>
            <p>
              Use cartographic context while refusing to display invented boundaries or
              unverified infrastructure layers.
            </p>
            <Link className="text-link" href="/map">
              Open map workspace
            </Link>
          </article>
        </div>
      </section>
    </>
  );
}
