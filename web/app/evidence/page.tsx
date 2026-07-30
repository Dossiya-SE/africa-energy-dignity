import { Notice } from "@/components/notice";
import { SourceCard } from "@/components/source-card";
import { getSources } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function EvidencePage() {
  const result = await getSources();
  const sources = result.data ?? [];

  return (
    <>
      <header className="page-heading">
        <p className="eyebrow">Evidence Studio</p>
        <h1>Source catalogue</h1>
        <p>
          Every record remains tied to its original publisher, licence, access method,
          limitations and verification state.
        </p>
      </header>

      {result.error ? (
        <Notice title="Evidence registry unavailable" tone="error">
          <p>{result.error}</p>
        </Notice>
      ) : null}

      {sources.length === 0 ? (
        <section className="empty-state">
          <h2>No source records available</h2>
          <p>
            AED Studio will not fabricate evidence. Seed or register controlled sources through
            the AED API before this catalogue can display them.
          </p>
        </section>
      ) : (
        <section className="card-grid" aria-label="Registered evidence sources">
          {sources.map((source) => (
            <SourceCard key={source.id} source={source} />
          ))}
        </section>
      )}
    </>
  );
}
