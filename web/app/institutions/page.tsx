import { Notice } from "@/components/notice";
import { getInstitutions } from "@/lib/api";
import { humanize } from "@/lib/presentation";

export const dynamic = "force-dynamic";

export default async function InstitutionsPage() {
  const result = await getInstitutions();
  const institutions = result.data ?? [];

  return (
    <>
      <header className="page-heading">
        <p className="eyebrow">Institution registry</p>
        <h1>African and regional authorities</h1>
        <p>
          Institutional owners and publishers are tracked separately from third-party data
          platforms and interfaces.
        </p>
      </header>

      {result.error ? (
        <Notice title="Institution registry unavailable" tone="error">
          <p>{result.error}</p>
        </Notice>
      ) : null}

      {institutions.length === 0 ? (
        <section className="empty-state">
          <h2>No institutions registered</h2>
          <p>The interface will remain empty until controlled institutional records exist.</p>
        </section>
      ) : (
        <section className="card-grid" aria-label="Registered institutions">
          {institutions.map((institution) => (
            <article className="card" key={institution.id}>
              <p className="card-kicker">{institution.id}</p>
              <h2>{institution.name}</h2>
              <dl className="compact-metadata">
                <div>
                  <dt>Type</dt>
                  <dd>{humanize(institution.institution_type)}</dd>
                </div>
                <div>
                  <dt>Country</dt>
                  <dd>{institution.country_code ?? "Regional or not specified"}</dd>
                </div>
              </dl>
              {institution.notes ? <p>{institution.notes}</p> : null}
              {institution.website ? (
                <a className="text-link" href={institution.website} rel="noreferrer" target="_blank">
                  Open institutional website
                </a>
              ) : null}
            </article>
          ))}
        </section>
      )}
    </>
  );
}
