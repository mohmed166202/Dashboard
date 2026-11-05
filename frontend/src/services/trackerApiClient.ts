import type {
  Project,
  Requirement,
  DropdownLists,
  AuditRecord,
  KPISummaryResponse,
  KpiFilterParams,
} from "../types/tracker";
import { getAuthHeaders } from "./authApiClient";

const BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "";

function getFullUrl(path: string, params?: Record<string, string | number | undefined>): string {
  const base = BASE_URL || (typeof window !== "undefined" ? window.location.origin : "http://localhost:8055");
  const url = new URL(path, base);

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

async function fetchJson<T>(path: string, params?: Record<string, string | number | undefined>): Promise<T> {
  const url = getFullUrl(path, params);
  const res = await fetch(url, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    const errorBody = await res.text().catch(() => "Unknown error");
    throw new Error(`API ${res.status} from ${path}: ${errorBody}`);
  }
  return res.json();
}

export const trackerApi = {
  // Projects
  async getProjects(filters?: {
    domain?: string;
    phase?: string;
    status?: string;
    priority?: string;
    team?: string;
    search?: string;
  }): Promise<{ total: number; projects: Project[] }> {
    return fetchJson<{ total: number; projects: Project[] }>("/api/projects", filters);
  },

  async getProject(id: string): Promise<{
    project: Project;
    requirements_count: number;
    requirements: Requirement[];
    audit_history: AuditRecord[];
  }> {
    return fetchJson(`/api/projects/${id}`);
  },

  async createProject(project: Partial<Project> & { id: string; project: string }): Promise<Project> {
    const url = getFullUrl("/api/projects");
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json", ...getAuthHeaders() },
      body: JSON.stringify(project),
    });
    if (!res.ok) {
      const err = await res.text().catch(() => "Failed to create project");
      throw new Error(err);
    }
    return res.json();
  },

  async updateProject(
    id: string,
    updates: Partial<Project> & { expected_updated_at?: string; user?: string }
  ): Promise<Project> {
    const url = getFullUrl(`/api/projects/${id}`);
    const res = await fetch(url, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", Accept: "application/json", ...getAuthHeaders() },
      body: JSON.stringify(updates),
    });
    if (!res.ok) {
      const err = await res.text().catch(() => "Failed to update project");
      throw new Error(err);
    }
    return res.json();
  },

  async deleteProject(id: string, user = "WebUser"): Promise<void> {
    const url = getFullUrl(`/api/projects/${id}`, { user });
    const res = await fetch(url, { method: "DELETE", headers: { ...getAuthHeaders() } });
    if (!res.ok) {
      const err = await res.text().catch(() => "Failed to delete project");
      throw new Error(err);
    }
  },

  // Requirements
  async getRequirements(projectId?: string): Promise<{ total: number; requirements: Requirement[] }> {
    return fetchJson<{ total: number; requirements: Requirement[] }>("/api/requirements", {
      project: projectId,
    });
  },

  async createRequirement(
    requirement: Partial<Requirement> & { req_id: string; project_id: string; requirement: string }
  ): Promise<Requirement> {
    const url = getFullUrl("/api/requirements");
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json", ...getAuthHeaders() },
      body: JSON.stringify(requirement),
    });
    if (!res.ok) {
      const err = await res.text().catch(() => "Failed to create requirement");
      throw new Error(err);
    }
    return res.json();
  },

  async updateRequirement(
    reqId: string,
    updates: Partial<Requirement> & { expected_updated_at?: string; user?: string }
  ): Promise<Requirement> {
    const url = getFullUrl(`/api/requirements/${reqId}`);
    const res = await fetch(url, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", Accept: "application/json", ...getAuthHeaders() },
      body: JSON.stringify(updates),
    });
    if (!res.ok) {
      const err = await res.text().catch(() => "Failed to update requirement");
      throw new Error(err);
    }
    return res.json();
  },

  // Dropdowns
  async getDropdowns(): Promise<DropdownLists> {
    return fetchJson<DropdownLists>("/api/dropdowns");
  },

  // Audit History
  async getAuditHistory(entityId: string): Promise<{ entity_id: string; history: AuditRecord[] }> {
    return fetchJson(`/api/audit/${entityId}`);
  },

  // KPI Analytics with Dynamic Multi-Filter Support
  async getKpiSummary(filters?: KpiFilterParams): Promise<KPISummaryResponse> {
    const params: Record<string, string | undefined> = {};
    if (filters?.projects && filters.projects.length > 0) {
      params.projects = filters.projects.join(",");
    }
    if (filters?.domain) params.domain = filters.domain;
    if (filters?.phase) params.phase = filters.phase;
    if (filters?.priority) params.priority = filters.priority;
    if (filters?.status) params.status = filters.status;

    return fetchJson<KPISummaryResponse>("/api/kpi/summary", params);
  },

  async getKpiBenchmarks(filters?: KpiFilterParams): Promise<{ benchmarks: any[]; filter_applied?: any }> {
    const params: Record<string, string | undefined> = {};
    if (filters?.projects && filters.projects.length > 0) {
      params.projects = filters.projects.join(",");
    }
    if (filters?.domain) params.domain = filters.domain;
    if (filters?.phase) params.phase = filters.phase;
    if (filters?.priority) params.priority = filters.priority;
    if (filters?.status) params.status = filters.status;

    return fetchJson("/api/kpi/benchmarks", params);
  },
};

