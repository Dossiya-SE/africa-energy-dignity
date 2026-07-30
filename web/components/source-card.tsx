import Link from "next/link";

import { StatusBadge } from "@/components/status-badge";
import {
  evidenceTone,
  formatTemporalCoverage,
  humanize,
  verificationTone,
} from "@/lib/presentation";
import type { SourceRecord } from "@/lib/types";

interface SourceCardProps {
  source: SourceRecord;
}

export function SourceCard({ source }: SourceCardProps) {
  return (
    <article className="card source-card">
      <div className="card-kicker">{source.id}</div>
      <h2>{source.title}</h2>
      <p className="publisher">{source.original_publisher}</p>
      <div className="badge-row" aria-label="Evidence status">
        <StatusBadge tone={evidenceTone(source.evidence_class)}>
          {humanize(source.evidence_class)}
        </StatusBadge>
        <StatusBadge tone={verificationTone(source.verification_status)}>
          {humanize(source.verification_status)}
        </StatusBadge>
      </div>
      <dl className="compact-metadata">
        <div>
          <dt>Coverage</dt>
          <dd>{source.geographic_coverage.join(", ")}</dd>
        </div>
        <div>
          <dt>Time</dt>
          <dd>{formatTemporalCoverage(source.temporal_coverage)}</dd>
        </div>
        <div>
          <dt>Licence</dt>
          <dd>{source.licence}</dd>
        </div>
      </dl>
      <Link className="text-link" href={`/evidence/${encodeURIComponent(source.id)}`}>
        Inspect provenance
      </Link>
    </article>
  );
}
