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

export interface FinanceMoney {
  amount: string;
  currency: string;
  price_year: number;
  basis: "real" | "nominal";
}

export interface FinanceUncertainty {
  type: "range" | "confidence_interval" | "scenario";
  lower: string;
  upper: string;
}

export interface FinanceEvidenceReference {
  source_id: string | null;
  evidence_class: EvidenceClass;
  validation_status: VerificationStatus;
  responsible_contributor: string;
  limitations: string[];
  uncertainty: FinanceUncertainty | null;
}

export interface FinanceCostItem {
  cost_id: string;
  category: string;
  timing_year: number;
  value: FinanceMoney;
  quantity_driver: string | null;
  quantity_unit: string | null;
  evidence: FinanceEvidenceReference;
}

export interface FinanceEnergyYear {
  year: number;
  energy: string;
  unit: string;
  evidence: FinanceEvidenceReference;
}

export interface FinanceFinancingComponent {
  component_id: string;
  type: "debt" | "equity" | "grant" | "subsidy";
  amount: FinanceMoney;
  interest_rate: string | null;
  tenor_years: number | null;
  grace_period_years: number | null;
  repayment_profile: string | null;
  evidence: FinanceEvidenceReference;
}

export interface FinanceCustomerClass {
  customer_class_id: string;
  name: string;
  customer_count: number;
  annual_consumption_per_customer: string;
  energy_unit: string;
  tariff_per_energy: FinanceMoney;
  monthly_fixed_charge: FinanceMoney | null;
  monthly_disposable_income: FinanceMoney;
  connection_charge: FinanceMoney;
  evidence: FinanceEvidenceReference;
}

export interface FinanceScenarioPayload {
  scenario_id: string;
  name: string;
  scenario_version: string;
  formula_version: string;
  geography_id: string;
  project_id: string | null;
  is_synthetic: boolean;
  reporting_currency: string;
  price_year: number;
  monetary_basis: "real" | "nominal";
  discount_rate: string;
  discount_rate_basis: "real" | "nominal";
  inflation_rate: string | null;
  funding_requirement: FinanceMoney;
  project_start_year: number;
  project_lifetime_years: number;
  construction_years: number;
  cost_items: FinanceCostItem[];
  annual_energy: FinanceEnergyYear[];
  financing_components: FinanceFinancingComponent[];
  customer_classes: FinanceCustomerClass[];
  validation_status: VerificationStatus;
  responsible_contributor: string;
  created_at: string;
  updated_at: string;
}

export interface FinanceScenarioSummary {
  scenario_record_id: string;
  scenario_id: string;
  scenario_version: string;
  name: string;
  formula_version: string;
  canonicalization_version: string;
  input_hash: string;
  geography_id: string;
  project_id: string | null;
  is_synthetic: boolean;
  reporting_currency: string;
  price_year: number;
  monetary_basis: string;
  validation_status: string;
  recorded_at: string;
}

export interface FinanceScenarioDetail extends FinanceScenarioSummary {
  scenario: FinanceScenarioPayload;
}

export interface FinanceScenarioPage {
  items: FinanceScenarioSummary[];
  limit: number;
  offset: number;
}

export interface FinanceExecutionRecord {
  execution_id: string;
  scenario_record_id: string;
  scenario_id: string;
  scenario_version: string;
  is_synthetic: boolean;
  calculation_run_id: string;
  formula_version: string;
  input_hash: string;
  canonicalization_version: string;
  software_version: string;
  status: "succeeded" | "failed";
  error_message: string | null;
  started_at: string;
  completed_at: string;
  indicator_count: number;
}

export interface FinanceCashFlowYear {
  year: number;
  lifecycle_cost: string;
  project_revenue: string;
  net_cash_flow: string;
  discount_factor: string;
  discounted_cash_flow: string;
}

export interface FinanceCashFlowResponse {
  execution_id: string;
  calculation_run_id: string;
  input_hash: string;
  formula_version: string;
  software_version: string;
  currency: string;
  price_year: number;
  monetary_basis: string;
  is_synthetic: boolean;
  rows: FinanceCashFlowYear[];
}

export interface FinanceIndicatorRecord {
  result_id: string;
  execution_id: string;
  indicator_name: string;
  status: string;
  result: Record<string, unknown>;
  lineage: Record<string, unknown>;
  created_at: string;
}

export interface FinanceIndicatorPage {
  items: FinanceIndicatorRecord[];
  limit: number;
  offset: number;
}

export interface FinanceAffordabilityRecord extends FinanceIndicatorRecord {
  customer_class_id: string;
}

export interface FinanceAffordabilityPage {
  items: FinanceAffordabilityRecord[];
  limit: number;
  offset: number;
}

export interface FinanceValidationRecord {
  validation_event_id: string;
  scenario_record_id: string;
  execution_id: string | null;
  status: "passed" | "warning" | "failed";
  message: string;
  checks: Record<string, unknown>;
  created_at: string;
}

export interface FinanceValidationPage {
  items: FinanceValidationRecord[];
  limit: number;
  offset: number;
}

export interface FinanceWorkspaceData {
  scenario: FinanceScenarioDetail;
  execution: FinanceExecutionRecord | null;
  cashFlow: FinanceCashFlowResponse | null;
  indicators: FinanceIndicatorRecord[];
  affordability: FinanceAffordabilityRecord[];
  validations: FinanceValidationRecord[];
}

export interface FinanceWorkspaceActionResult {
  data: FinanceWorkspaceData | null;
  error: string | null;
}
