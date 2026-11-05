export interface Project {
  id: string;
  team: string | null;
  project: string;
  type: string | null;
  domain: string | null;
  description: string | null;
  phase: string | null;
  status: string | null;
  percent_complete: number | null;
  todo_tasks: string | null;
  inprogress_tasks: string | null;
  completed_tasks: string | null;
  blockers: string | null;
  blocker_owner: string | null;
  business_owner: string | null;
  technical_owner: string | null;
  start_date: string | null;
  due_date: string | null;
  last_updated: string | null;
  last_followup: string | null;
  notes: string | null;
  priority: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface Requirement {
  req_id: string;
  project: string | null;
  project_id: string;
  category: string;
  nfr_area: string | null;
  requirement: string;
  description: string | null;
  business_benefit: string | null;
  request_type: string | null;
  owner: string | null;
  priority: string | null;
  status: string | null;
  target_date: string | null;
  source: string | null;
  notes: string | null;
  user?: string;
  created_at?: string;
  updated_at?: string;
}

export interface DropdownItem {
  code: string;
  label: string;
  description?: string | null;
  stage?: string | null;
}

export interface DropdownLists {
  types: DropdownItem[];
  phases: DropdownItem[];
  statuses: DropdownItem[];
  domains: DropdownItem[];
  teams: DropdownItem[];
  priorities: DropdownItem[];
  req_categories: DropdownItem[];
  nfr_areas: DropdownItem[];
  request_types: DropdownItem[];
  req_priorities: DropdownItem[];
  req_statuses: DropdownItem[];
  team_members: DropdownItem[];
}

export interface AuditRecord {
  id: number;
  entity_type: string;
  entity_id: string;
  action: string;
  field_name: string | null;
  old_value: string | null;
  new_value: string | null;
  user: string;
  timestamp: string;
}

export interface KPIMetric {
  id: number;
  metric_key: string;
  metric_name: string;
  category: string;
  current_value: number;
  target_value: number | null;
  unit: string | null;
  industry_benchmark_min: number | null;
  industry_benchmark_max: number | null;
  industry_benchmark_unit: string | null;
  benchmark_source: string | null;
  benchmark_notes: string | null;
  last_calculated: string;
}

export interface ScopedProjectMetric {
  id: string;
  project: string;
  domain: string | null;
  phase: string | null;
  status: string | null;
  priority: string | null;
  percent_complete: number | null;
  time_saved_hrs: number;
  revenue_impact_sar: number;
  net_profit_sar: number;
  target_subscribers: number;
  current_subscribers: number;
  csat_score: number;
  productivity_pct: number;
}

export interface KpiFilterParams {
  projects?: string[]; // Array of project IDs e.g. ["AI-001", "AI-006"]
  domain?: string;
  phase?: string;
  priority?: string;
  status?: string;
}

export interface KPISummaryResponse {
  portfolio_summary: {
    total_projects: number;
    on_track: number;
    at_risk: number;
    delayed: number;
    live: number;
    uat: number;
    avg_progress_pct: number;
    total_requirements: number;
    implemented_requirements: number;
    req_implementation_pct: number;
  };
  distributions: {
    by_domain: { domain: string; count: number }[];
    by_status: { status: string; count: number }[];
    by_phase: { phase: string; count: number }[];
  };
  core_kpis: Record<string, KPIMetric>;
  scoped_projects?: ScopedProjectMetric[];
  filter_applied?: {
    projects: string[];
    domain: string | null;
    phase: string | null;
    priority: string | null;
    is_filtered: boolean;
  };
}
