/**
 * TanStack Query hooks for all API endpoints.
 *
 * Cache strategy:
 *  - staleTime: 5 min  → data is fresh for 5 minutes; no background refetch within that window
 *  - gcTime: 10 min    → cached data is kept in memory for 10 minutes after last subscriber unmounts
 *  - retry: 2          → retry failed requests up to 2 times with exponential back-off
 *
 * Query Keys are structured arrays so invalidation is granular and predictable.
 */

import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { apiClient } from "../services/apiClient";
import type { RepositoryFilters } from "../types/api";

/** Shared cache configuration — applied to all queries */
const CACHE_CONFIG = {
  staleTime: 5 * 60 * 1000,   // 5 minutes
  gcTime:    10 * 60 * 1000,  // 10 minutes
  retry: 2,
} as const;

// ─── Query Key Factory (type-safe, prevents typos) ───────────────────────────
export const queryKeys = {
  health:               () => ["health"] as const,
  summary:              () => ["summary"] as const,
  domains:              () => ["domains"] as const,
  taxonomy:             () => ["taxonomy"] as const,
  repositories:         (filters: RepositoryFilters) => ["repositories", filters] as const,
  repositoryDetail:     (nameWithOwner: string) => ["repository", nameWithOwner] as const,
  matrix:               (limit: number, offset: number) => ["matrix", limit, offset] as const,
  confidenceDist:       () => ["analytics", "confidence"] as const,
  standardsAnalytics:   () => ["analytics", "standards"] as const,
} as const;

// ─── Health ──────────────────────────────────────────────────────────────────
export function useHealth() {
  return useQuery({
    queryKey: queryKeys.health(),
    queryFn: () => apiClient.health(),
    ...CACHE_CONFIG,
    // Poll every 60s to show live API connectivity in the Navbar
    refetchInterval: 60_000,
  });
}

// ─── Dashboard Summary ────────────────────────────────────────────────────────
export function useSummary() {
  return useQuery({
    queryKey: queryKeys.summary(),
    queryFn: () => apiClient.getSummary(),
    ...CACHE_CONFIG,
  });
}

// ─── Domain Distribution ──────────────────────────────────────────────────────
export function useDomains() {
  return useQuery({
    queryKey: queryKeys.domains(),
    queryFn: () => apiClient.getDomains(),
    ...CACHE_CONFIG,
  });
}

// ─── Full Taxonomy ────────────────────────────────────────────────────────────
export function useTaxonomy() {
  return useQuery({
    queryKey: queryKeys.taxonomy(),
    queryFn: () => apiClient.getTaxonomy(),
    // Taxonomy never changes at runtime — cache forever for this session
    staleTime: Infinity,
    gcTime: Infinity,
    retry: 1,
  });
}

// ─── Repositories (paginated + filtered) ─────────────────────────────────────
export function useRepositories(filters: RepositoryFilters = {}) {
  return useQuery({
    queryKey: queryKeys.repositories(filters),
    queryFn: () => apiClient.getRepositories(filters),
    ...CACHE_CONFIG,
    // Keep previous page data visible while new page loads (no flicker)
    placeholderData: keepPreviousData,
  });
}

// ─── Single Repository Detail ─────────────────────────────────────────────────
export function useRepositoryDetail(nameWithOwner: string | null) {
  return useQuery({
    queryKey: queryKeys.repositoryDetail(nameWithOwner ?? ""),
    queryFn: () => apiClient.getRepositoryDetail(nameWithOwner!),
    enabled: Boolean(nameWithOwner),
    ...CACHE_CONFIG,
  });
}

// ─── Matrix XLSX ──────────────────────────────────────────────────────────────
export function useMatrix(limit = 500, offset = 0) {
  return useQuery({
    queryKey: queryKeys.matrix(limit, offset),
    queryFn: () => apiClient.getMatrix(limit, offset),
    staleTime: 10 * 60 * 1000, // Matrix file doesn't change often; cache 10 min
    gcTime: 15 * 60 * 1000,
    retry: 1,
    placeholderData: keepPreviousData,
  });
}

// ─── Confidence Distribution ──────────────────────────────────────────────────
export function useConfidenceDistribution() {
  return useQuery({
    queryKey: queryKeys.confidenceDist(),
    queryFn: () => apiClient.getConfidenceDistribution(),
    ...CACHE_CONFIG,
  });
}

// ─── Standards Analytics ──────────────────────────────────────────────────────
export function useStandardsAnalytics() {
  return useQuery({
    queryKey: queryKeys.standardsAnalytics(),
    queryFn: () => apiClient.getStandardsAnalytics(),
    ...CACHE_CONFIG,
  });
}

