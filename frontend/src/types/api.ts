/**
 * Normalized TypeScript schemas for the Andalusia Healthcare Portfolio.
 * These mirror the FastAPI response models exactly, ensuring end-to-end type safety.
 */

// ─── Domain Taxonomy (from domain_taxonomy.py) ─────────────────────────────

export interface TaxonomyDomain {
  id: string;
  name: string;
  description: string;
  token_count: number;
  high_precision_tokens: string[];
  specialized_standards: string[];
  semantic_profile_text: string;
}

export interface TaxonomyResponse {
  domains: TaxonomyDomain[];
  total: number;
}

// ─── Summary / KPI Metrics ──────────────────────────────────────────────────

export interface DashboardSummary {
  total_repositories: number;
  active_repositories: number;
  total_classified: number;
  total_dossiers: number;
  avg_confidence_score: number;        // 0–100 percentage
  unique_standards_detected: number;
  matrix_coverage_pct: number;         // 0–100 percentage
  top_languages: Record<string, number>;
}

// ─── Domain Distribution ────────────────────────────────────────────────────

export interface DomainStat {
  domain: string;
  repo_count: number;
  avg_confidence_pct: number;          // 0–100 percentage
  detected_standards: string[];
}

export interface DomainDistributionResponse {
  domains: DomainStat[];
  total_domains: number;
}

// ─── Repository ─────────────────────────────────────────────────────────────

export interface Repository {
  id: number;
  name: string;
  name_with_owner: string;
  owner: string;
  description: string | null;
  url: string | null;
  primary_language: string | null;
  languages: string[];
  topics: string[];
  is_archived: 0 | 1;
  is_private: 0 | 1;
  pushed_at: string | null;
  disk_usage_kb: number;
  open_issues_count: number;
  has_readme: 0 | 1;
  // Joined from domain_classifications
  primary_domain: string | null;
  secondary_domains: string[];
  confidence_score: number | null;
  detected_standards: string[];
  project_status: string | null;
  key_technologies: string[];
  domain_justification: string | null;
}

export interface RepositoryListResponse {
  items: Repository[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// ─── Single Repository Detail ────────────────────────────────────────────────

export interface RepositoryClassification {
  id: number;
  repo_name: string;
  name_with_owner: string;
  primary_domain: string;
  secondary_domains: string[];
  confidence_score: number;
  domain_justification: string;
  detected_standards: string[];
  project_status: string;
  key_technologies: string[];
  classified_at: string;
}

export interface DossierMeta {
  repo_name: string;
  priority_files_count: number;
  priority_files_list: string[];
  extracted_entities: string[];
  extracted_dependencies: string[];
  extracted_apis: string[];
  dossier_size_bytes: number;
  extracted_at: string;
}

export interface RepositoryDetail {
  repository: Repository;
  classification: RepositoryClassification | null;
  dossier_meta: DossierMeta | null;
}

// ─── Matrix XLSX ─────────────────────────────────────────────────────────────

export interface MatrixResponse {
  rows: Record<string, string | number | null>[];
  total: number;
  limit: number;
  offset: number;
  headers: string[];
}

// ─── Analytics ───────────────────────────────────────────────────────────────

export interface ConfidenceBucket {
  range: string;
  count: number;
}

export interface ConfidenceDistributionResponse {
  distribution_buckets: ConfidenceBucket[];
  per_domain_avg_pct: Record<string, number>;
}

export interface StandardFrequency {
  name: string;
  count: number;
}

export interface StandardsAnalyticsResponse {
  standards: StandardFrequency[];
  total_unique: number;
}

// ─── Health ──────────────────────────────────────────────────────────────────

export interface HealthResponse {
  status: string;
  db_connected: boolean;
  xlsx_loaded: boolean;
  api_version: string;
}

// ─── Query Params Helpers ────────────────────────────────────────────────────

export interface RepositoryFilters {
  domain?: string;
  language?: string;
  status?: string;
  search?: string;
  limit?: number;
  offset?: number;
}

