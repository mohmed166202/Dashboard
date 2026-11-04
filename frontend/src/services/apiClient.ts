/**
 * Centralized API client for the FastAPI backend.
 * All fetch calls are funnelled through this module so that:
 *  - Base URL is configured once (falls back to Vite env var)
 *  - Error handling is consistent
 *  - Request serialization (query params, JSON) is uniform
 */

import type {
  DashboardSummary,
  DomainDistributionResponse,
  RepositoryListResponse,
  RepositoryDetail,
  TaxonomyResponse,
  MatrixResponse,
  ConfidenceDistributionResponse,
  StandardsAnalyticsResponse,
  HealthResponse,
  RepositoryFilters,
} from "../types/api";

const BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8000";

// ─── Core Fetch Wrapper ───────────────────────────────────────────────────────

async function apiFetch<T>(path: string, params?: Record<string, string | number | undefined>): Promise<T> {
  const url = new URL(`${BASE_URL}${path}`);

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }

  const res = await fetch(url.toString(), {
    headers: { "Accept": "application/json" },
  });

  if (!res.ok) {
    const errorBody = await res.text().catch(() => "Unknown error");
    throw new Error(`API ${res.status} from ${path}: ${errorBody}`);
  }

  return res.json() as Promise<T>;
}

// ═══════════════════════════════════════════════════════════════════════════════
//  API Functions — one per endpoint
// ═══════════════════════════════════════════════════════════════════════════════

export const apiClient = {
  /** Health check — used to show API connection status in the Navbar. */
  health(): Promise<HealthResponse> {
    return apiFetch<HealthResponse>("/health");
  },

  /** Dashboard KPI summary metrics. */
  getSummary(): Promise<DashboardSummary> {
    return apiFetch<DashboardSummary>("/api/summary");
  },

  /**
   * Domain distribution: per-domain repo count, avg confidence, standards.
   * Powers the DomainFilterBar and analytics charts.
   */
  getDomains(): Promise<DomainDistributionResponse> {
    return apiFetch<DomainDistributionResponse>("/api/domains");
  },

  /**
   * Full domain taxonomy from domain_taxonomy.py.
   * Provides token counts, regex patterns, semantic profiles.
   */
  getTaxonomy(): Promise<TaxonomyResponse> {
    return apiFetch<TaxonomyResponse>("/api/taxonomy");
  },

  /**
   * Paginated + filterable repository list with joined classifications.
   * Used in the Phase 3 virtualized table.
   */
  getRepositories(filters?: RepositoryFilters): Promise<RepositoryListResponse> {
    return apiFetch<RepositoryListResponse>("/api/repositories", filters as Record<string, string | number | undefined>);
  },

  /** Single repository + classification + dossier meta. */
  getRepositoryDetail(nameWithOwner: string): Promise<RepositoryDetail> {
    return apiFetch<RepositoryDetail>(`/api/repositories/${nameWithOwner}`);
  },

  /** Parsed rows from andalusia_healthcare_domains_matrix.xlsx. */
  getMatrix(limit = 500, offset = 0): Promise<MatrixResponse> {
    return apiFetch<MatrixResponse>("/api/matrix", { limit, offset });
  },

  /** Confidence score distribution for the analytics histogram. */
  getConfidenceDistribution(): Promise<ConfidenceDistributionResponse> {
    return apiFetch<ConfidenceDistributionResponse>("/api/analytics/confidence");
  },

  /** Standards frequency for the bar chart. */
  getStandardsAnalytics(): Promise<StandardsAnalyticsResponse> {
    return apiFetch<StandardsAnalyticsResponse>("/api/analytics/standards");
  },
};

