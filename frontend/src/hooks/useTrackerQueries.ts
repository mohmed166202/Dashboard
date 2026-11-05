import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { trackerApi } from "../services/trackerApiClient";
import type { Project, Requirement, KpiFilterParams } from "../types/tracker";

export const TRACKER_KEYS = {
  projects: (filters?: any) => ["tracker", "projects", filters] as const,
  project: (id: string) => ["tracker", "project", id] as const,
  requirements: (projectId?: string) => ["tracker", "requirements", projectId] as const,
  dropdowns: ["tracker", "dropdowns"] as const,
  audit: (entityId: string) => ["tracker", "audit", entityId] as const,
  kpiSummary: (filters?: KpiFilterParams) => ["tracker", "kpi", "summary", filters] as const,
  kpiBenchmarks: (filters?: KpiFilterParams) => ["tracker", "kpi", "benchmarks", filters] as const,
};

// ── Projects Queries & Mutations ─────────────────────────────────────────────

export function useProjects(filters?: {
  domain?: string;
  phase?: string;
  status?: string;
  priority?: string;
  team?: string;
  search?: string;
}) {
  return useQuery({
    queryKey: TRACKER_KEYS.projects(filters),
    queryFn: () => trackerApi.getProjects(filters),
    staleTime: 1000 * 60, // 1 minute
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: TRACKER_KEYS.project(id),
    queryFn: () => trackerApi.getProject(id),
    enabled: Boolean(id),
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      updates,
    }: {
      id: string;
      updates: Partial<Project> & { expected_updated_at?: string; user?: string };
    }) => trackerApi.updateProject(id, updates),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["tracker", "projects"] });
      queryClient.invalidateQueries({ queryKey: TRACKER_KEYS.project(data.id) });
      queryClient.invalidateQueries({ queryKey: ["tracker", "kpi"] });
    },
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (project: Partial<Project> & { id: string; project: string }) =>
      trackerApi.createProject(project),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tracker", "projects"] });
      queryClient.invalidateQueries({ queryKey: ["tracker", "kpi"] });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => trackerApi.deleteProject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tracker", "projects"] });
      queryClient.invalidateQueries({ queryKey: ["tracker", "kpi"] });
    },
  });
}

// ── Requirements Queries & Mutations ─────────────────────────────────────────

export function useRequirements(projectId?: string) {
  return useQuery({
    queryKey: TRACKER_KEYS.requirements(projectId),
    queryFn: () => trackerApi.getRequirements(projectId),
    enabled: Boolean(projectId),
  });
}

export function useUpdateRequirement() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      reqId,
      updates,
    }: {
      reqId: string;
      updates: Partial<Requirement> & { expected_updated_at?: string; user?: string };
    }) => trackerApi.updateRequirement(reqId, updates),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["tracker", "requirements"] });
      queryClient.invalidateQueries({ queryKey: TRACKER_KEYS.project(data.project_id) });
      queryClient.invalidateQueries({ queryKey: ["tracker", "kpi"] });
    },
  });
}

export function useCreateRequirement() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (
      req: Partial<Requirement> & { req_id: string; project_id: string; requirement: string }
    ) => trackerApi.createRequirement(req),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["tracker", "requirements"] });
      queryClient.invalidateQueries({ queryKey: TRACKER_KEYS.project(data.project_id) });
      queryClient.invalidateQueries({ queryKey: ["tracker", "kpi"] });
    },
  });
}

// ── Dropdowns Query ──────────────────────────────────────────────────────────

export function useDropdowns() {
  return useQuery({
    queryKey: TRACKER_KEYS.dropdowns,
    queryFn: () => trackerApi.getDropdowns(),
    staleTime: 1000 * 60 * 30, // 30 minutes
  });
}

// ── Audit History Query ──────────────────────────────────────────────────────

export function useAuditHistory(entityId: string) {
  return useQuery({
    queryKey: TRACKER_KEYS.audit(entityId),
    queryFn: () => trackerApi.getAuditHistory(entityId),
    enabled: Boolean(entityId),
  });
}

// ── KPI Queries with Dynamic Filtering ───────────────────────────────────────

export function useKpiSummary(filters?: KpiFilterParams) {
  return useQuery({
    queryKey: TRACKER_KEYS.kpiSummary(filters),
    queryFn: () => trackerApi.getKpiSummary(filters),
    staleTime: 1000 * 30,
  });
}

export function useKpiBenchmarks(filters?: KpiFilterParams) {
  return useQuery({
    queryKey: TRACKER_KEYS.kpiBenchmarks(filters),
    queryFn: () => trackerApi.getKpiBenchmarks(filters),
    staleTime: 1000 * 60 * 5,
  });
}

