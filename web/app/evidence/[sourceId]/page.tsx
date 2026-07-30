import Link from "next/link";

import { Notice } from "@/components/notice";
import { StatusBadge } from "@/components/status-badge";
import { getSource } from "@/lib/api";
import {
  evidenceTone,
  formatTemporalCoverage,
  humanize,
  verificationTone,
} from "@/lib/presentation";

export const dynamic = "force-dynamic";

interface SourceDetailPageProps {
  params: Promise<{ sourceId: string }>;
}

export default async function SourceDetailPage({ params }: SourceDetailPageProps) {
  const { sourceId } = await params;
  const result = await getSource(sourceId);
  const source = result.data;

  if (!source) {
    return (
      <>
        <header className="page-heading">
          <p className="eyebrow">Evidence Studio</p>
          <h1>Source unavailable</h1>
        </header>
        <Notice title="The requested source could not be retrieved" tone="error">
          <p>{result.error ?? "Source not found."}</p>
        </Notice>
        <Link className="text-link" href="/evidence">
          Return to evidence catalogue
        </Link>
      </>
    );
  }

  return (
    <>
      <header className="page-heading">
        <p className="eyebrow">Evidence provenance</p>
        <h1>{source.title}</h1>
        <div className="badge-row">
          <StatusBadge tone={evidenceTone(source.evidence_class)}>
            {humanize(source.evidence_class)}
          </StatusBadge>
          <StatusBadge tone={verificationTone(source.verification_status)}>
            {humanize(source.verification_status)}
          </StatusBadge>
        </div>
      </header>

      <div className="detail-layout">
        <section className="detail-panel">
          <h2>Traceability</h2>
          <dl className="detail-list">
            <div>
              <dt>Stable identifier</dt>
              <dd>{source.id}</dd>
            </div>
            <div>
              <dt>Original publisher</dt>
              <dd>{source.original_publisher}</dd>
            </div>
            <div>
              <dt>Source location</dt>
              <dd>
                {source.source_url ? (
                  <a href={source.source_url} rel="noreferrer" target="_blank">
                    Open original location
                  </a>
                ) : (
                  source.persistent_identifier ?? source.archive_reference ?? "Unknown"
                )}
              </dd>
            </div>
            <div>
              <dt>Access date</dt>
              <dd>{source.access_date}</dd>
            </div>
            <div>
              <dt>Access method</dt>
              <dd>{source.access_method}</dd>
            </div>
            <div>
              <dt>Responsible reviewer</dt>
              <dd>{source.responsible_reviewer}</dd>
            </div>
            <div>
              <dt>Version</dt>
              <dd>{source.version}</dd>
            </div>
          </dl>
        </section>

        <section className="detail-panel">
          <h2>Evidence conditions</h2>
          <dl className="detail-list">
            <div>
              <dt>Geographic coverage</dt>
              <dd>{source.geographic_coverage.join(", ")}</dd>
            </div>
            <div>
              <dt>Temporal coverage</dt>
              <dd>{formatTemporalCoverage(source.temporal_coverage)}</dd>
            </div>
            <div>
              <dt>Licence</dt>
              <dd>{source.licence}</dd>
            </div>
            <div>
              <dt>Attribution</dt>
              <dd>{source.attribution_requirements}</dd>
            </div>
            <div>
              <dt>Checksum</dt>
              <dd>{source.checksum ?? "Not recorded"}</dd>
            </div>
          </dl>
          <h2>Known limitations</h2>
          <ul className="limitations-list">
            {source.known_limitations.map((limitation) => (
              <li key={limitation}>{limitation}</li>
            ))}
          </ul>
        </section>
      </div>
    </>
  );
}
