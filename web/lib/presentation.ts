import type { EvidenceClass, TemporalCoverage, VerificationStatus } from "@/lib/types";

export type StatusTone = "neutral" | "warning" | "positive" | "negative";

const POSITIVE_STATES = new Set<VerificationStatus>([
  "source_verified",
  "cross_checked",
  "model_ready",
  "validated",
]);

export function humanize(value: string): string {
  return value
    .split("_")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function verificationTone(status: VerificationStatus): StatusTone {
  if (POSITIVE_STATES.has(status)) return "positive";
  if (status === "rejected" || status === "deprecated") return "negative";
  if (status === "proposed" || status === "schema_valid") return "warning";
  return "neutral";
}

export function evidenceTone(evidenceClass: EvidenceClass): StatusTone {
  return evidenceClass === "unverified" ? "warning" : "neutral";
}

export function formatTemporalCoverage(coverage: TemporalCoverage): string {
  if (coverage.description) return coverage.description;
  if (coverage.valid_from && coverage.valid_to) {
    return `${coverage.valid_from} to ${coverage.valid_to}`;
  }
  if (coverage.valid_from) return `From ${coverage.valid_from}`;
  if (coverage.valid_to) return `Through ${coverage.valid_to}`;
  return "Unknown";
}
