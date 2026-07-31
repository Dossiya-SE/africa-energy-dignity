export type VerificationStatus =
  | "proposed"
  | "schema_valid"
  | "source_verified"
  | "cross_checked"
  | "model_ready"
  | "validated"
  | "rejected"
  | "deprecated";

export type EvidenceClass =
  | "observed"
  | "published"
  | "derived"
  | "assumed"
  | "scenario"
  | "expert_judgment"
  | "unverified";

export interface TemporalCoverage {
  valid_from?: string;
  valid_to?: string;
  description?: string;
}

export interface SourceRecord {
  id: string;
  title: string;
  original_publisher: string;
  publisher_id: string | null;
  source_url: string | null;
  persistent_identifier: string | null;
  archive_reference: string | null;
  access_date: string;
  temporal_coverage: TemporalCoverage;
  geographic_coverage: string[];
  licence: string;
  attribution_requirements: string;
  access_method: string;
  known_limitations: string[];
  evidence_class: EvidenceClass;
  verification_status: VerificationStatus;
  responsible_reviewer: string;
  version: string;
  checksum: string | null;
  created_at: string;
  updated_at: string;
}

export interface InstitutionRecord {
  id: string;
  name: string;
  institution_type: string;
  country_code: string | null;
  website: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface GeographyRecord {
  id: string;
  name: string;
  level: string;
  parent_id: string | null;
  iso_code: string | null;
  geometry_status: string;
  created_at: string;
  updated_at: string;
}

export interface AssetRecord {
  id: string;
  dataset_id: string | null;
  geography_id: string | null;
  name: string;
  asset_type: string;
  uri: string;
  spatial_resolution: string | null;
  temporal_coverage: string | null;
  licence: string | null;
  validation_status: VerificationStatus;
  is_sensitive: boolean;
  created_at: string;
  updated_at: string;
}

export interface MapLayerRecord {
  asset_id: string;
  name: string;
  asset_type: string;
  geography_id: string | null;
  publication_status: "published" | "blocked";
  validation_status: VerificationStatus;
  evidence_class: EvidenceClass;
  source_id: string;
  source_title: string;
  original_publisher: string;
  source_url: string | null;
  access_date: string;
  licence: string;
  attribution_requirements: string;
  known_limitations: string[];
  dataset_id: string;
  dataset_version: string | null;
  unit: string | null;
  crs: string | null;
  bbox: number[] | null;
  nodata: { value?: number; excluded_from_statistics?: boolean } | null;
  checksum: string | null;
  spatial_resolution: string | null;
  temporal_coverage: string | null;
  product_year: number | null;
  model_type: string | null;
  population_total: number | null;
  coverage_ratio: number | null;
  file_size_bytes: number | null;
  manifest_url: string | null;
  rendering_method: "geojson" | "image";
  data_url: string | null;
  preview_url: string | null;
  warning: string | null;
}

export interface ServiceStatus {
  status: string;
  service?: string;
  database?: string;
}

export interface ApiResult<T> {
  data: T | null;
  error: string | null;
}
