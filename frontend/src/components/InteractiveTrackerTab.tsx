import React, { useState, useMemo } from "react";
import type { Project, DropdownLists } from "../types/tracker";
import {
  InlineSelectCell,
  InlineTextCell,
  InlineProgressCell,
} from "./InlineEditCells";
import { RequirementsSubPanel } from "./RequirementsSubPanel";
import { NewProjectModal } from "./NewProjectModal";
import { AuditDrawer } from "./AuditDrawer";
import {
  useProjects,
  useUpdateProject,
  useAuditHistory,
  useDropdowns,
  useRequirements,
} from "../hooks/useTrackerQueries";
import { useTrackerWebSocket } from "../hooks/useTrackerWebSocket";
import { useQueryClient } from "@tanstack/react-query";
import {
  Search,
  Filter,
  Plus,
  ChevronDown,
  ChevronRight,
  Clock,
  Download,
  Wifi,
  WifiOff,
  RefreshCw,
  FolderOpen,
} from "lucide-react";

export const InteractiveTrackerTab: React.FC = () => {
  const queryClient = useQueryClient();

  // Search & Filter State
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedDomain, setSelectedDomain] = useState("");
  const [selectedPhase, setSelectedPhase] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("");
  const [selectedPriority, setSelectedPriority] = useState("");

  // UI Expansion & Modal State
  const [expandedProjectId, setExpandedProjectId] = useState<string | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [auditEntityId, setAuditEntityId] = useState<string | null>(null);

  // Queries
  const { data: dropdowns } = useDropdowns();
  const {
    data: projectsData,
    isLoading: isLoadingProjects,
    refetch,
  } = useProjects({
    domain: selectedDomain || undefined,
    phase: selectedPhase || undefined,
    status: selectedStatus || undefined,
    priority: selectedPriority || undefined,
    search: searchTerm || undefined,
  });

  const { data: activeRequirementsData } = useRequirements(
    expandedProjectId || undefined
  );
  const { data: auditData, isLoading: isLoadingAudit } = useAuditHistory(
    auditEntityId || ""
  );

  const updateMutation = useUpdateProject();

  // WebSocket Live Push Synchronization
  const { isConnected: isWsConnected } = useTrackerWebSocket(() => {
    // On any broadcast mutation, refresh queries
    queryClient.invalidateQueries({ queryKey: ["tracker", "projects"] });
    if (expandedProjectId) {
      queryClient.invalidateQueries({
        queryKey: ["tracker", "requirements", expandedProjectId],
      });
    }
  });

  const projects = projectsData?.projects || [];

  // Status Badge Colors mapping
  const statusColorMap: Record<string, { bg: string; text: string; border: string }> = {
    "On Track": { bg: "#ECFDF5", text: "#065F46", border: "#A7F3D0" },
    "At Risk": { bg: "#FEF2F2", text: "#991B1B", border: "#FECACA" },
    Delayed: { bg: "#FFFBEB", text: "#92400E", border: "#FDE68A" },
    "Off Track": { bg: "#FEF2F2", text: "#7F1D1D", border: "#FCA5A5" },
    "Under Review": { bg: "#F0FDF4", text: "#166534", border: "#BBF7D0" },
    "Pending Decision": { bg: "#EFF6FF", text: "#1E40AF", border: "#BFDBFE" },
    Done: { bg: "#F0FDF4", text: "#15803D", border: "#86EFAC" },
    Retired: { bg: "#F3F4F6", text: "#4B5563", border: "#E5E7EB" },
    "Not Reported": { bg: "#F9FAFB", text: "#6B7280", border: "#E5E7EB" },
  };

  const priorityColorMap: Record<string, { bg: string; text: string; border: string }> = {
    High: { bg: "#FEF2F2", text: "#991B1B", border: "#FECACA" },
    Medium: { bg: "#FFFBEB", text: "#92400E", border: "#FDE68A" },
    Low: { bg: "#F3F4F6", text: "#4B5563", border: "#E5E7EB" },
  };

  const handleProjectUpdate = async (id: string, updates: Partial<Project>) => {
    const current = projects.find((p) => p.id === id);
    await updateMutation.mutateAsync({
      id,
      updates: {
        ...updates,
        expected_updated_at: current?.updated_at,
        user: "WebUser",
      },
    });
  };

  const handleExportCsv = () => {
    if (projects.length === 0) return;
    const headers = [
      "ID",
      "Project",
      "Team",
      "Type",
      "Domain",
      "Phase",
      "Status",
      "% Complete",
      "Priority",
      "Business Owner",
      "Start Date",
      "Due Date",
    ];
    const rows = projects.map((p) => [
      p.id,
      `"${(p.project || "").replace(/"/g, '""')}"`,
      p.team || "",
      p.type || "",
      `"${p.domain || ""}"`,
      p.phase || "",
      p.status || "",
      p.percent_complete !== null ? `${Math.round(p.percent_complete * 100)}%` : "",
      p.priority || "",
      `"${p.business_owner || ""}"`,
      p.start_date || "",
      p.due_date || "",
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `AI_Project_Tracker_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-4">
      {/* ── Top Bar with Filters, Actions, Live WS Status ───────────────── */}
      <div className="bg-white rounded-xl border border-stone-200 p-4 shadow-sm flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-stone-900 tracking-tight">
              AI Project Tracker
            </h2>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-900 font-semibold">
              {projects.length} Projects
            </span>
            {isWsConnected ? (
              <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                <Wifi className="w-3 h-3 text-emerald-600 animate-pulse" /> Live Sync
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-[11px] font-medium text-stone-500 bg-stone-100 px-2 py-0.5 rounded-full">
                <WifiOff className="w-3 h-3" /> Offline
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => refetch()}
              className="p-2 text-stone-600 hover:text-stone-900 rounded-lg hover:bg-stone-100 border border-stone-200 transition-colors"
              title="Refresh Data"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={handleExportCsv}
              className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-lg border border-stone-300 text-stone-700 hover:bg-stone-50 transition-colors shadow-xs"
            >
              <Download className="w-3.5 h-3.5 text-stone-500" /> Export CSV
            </button>
            <button
              onClick={() => setIsAddModalOpen(true)}
              className="inline-flex items-center gap-1.5 text-xs font-bold px-3.5 py-2 rounded-lg bg-amber-800 text-white hover:bg-amber-900 shadow-sm transition-colors"
            >
              <Plus className="w-4 h-4" /> Add Project
            </button>
          </div>
        </div>

        {/* Filters Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-2.5 pt-2 border-t border-stone-100 text-xs">
          {/* Search Box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-stone-400" />
            <input
              type="text"
              placeholder="Search projects..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-lg border border-stone-300 bg-stone-50/50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-amber-500"
            />
          </div>

          {/* Domain Filter */}
          <select
            value={selectedDomain}
            onChange={(e) => setSelectedDomain(e.target.value)}
            className="p-1.5 rounded-lg border border-stone-300 bg-white focus:outline-none"
          >
            <option value="">All Domains ({dropdowns?.domains.length || 0})</option>
            {dropdowns?.domains.map((d) => (
              <option key={d.code} value={d.code}>
                {d.label}
              </option>
            ))}
          </select>

          {/* Phase Filter */}
          <select
            value={selectedPhase}
            onChange={(e) => setSelectedPhase(e.target.value)}
            className="p-1.5 rounded-lg border border-stone-300 bg-white focus:outline-none"
          >
            <option value="">All Phases</option>
            {dropdowns?.phases.map((p) => (
              <option key={p.code} value={p.code}>
                {p.label}
              </option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="p-1.5 rounded-lg border border-stone-300 bg-white focus:outline-none"
          >
            <option value="">All Statuses</option>
            {dropdowns?.statuses.map((s) => (
              <option key={s.code} value={s.code}>
                {s.label}
              </option>
            ))}
          </select>

          {/* Priority Filter */}
          <select
            value={selectedPriority}
            onChange={(e) => setSelectedPriority(e.target.value)}
            className="p-1.5 rounded-lg border border-stone-300 bg-white focus:outline-none"
          >
            <option value="">All Priorities</option>
            {dropdowns?.priorities.map((pr) => (
              <option key={pr.code} value={pr.code}>
                {pr.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* ── Interactive Editable Grid ─────────────────────────────────── */}
      <div className="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden">
        {isLoadingProjects ? (
          <div className="p-12 text-center text-sm text-stone-500">Loading AI portfolio...</div>
        ) : projects.length === 0 ? (
          <div className="p-12 text-center text-sm text-stone-500">
            No projects match the selected criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-stone-100 text-stone-700 font-bold border-b border-stone-200">
                <tr>
                  <th className="py-2.5 px-3 w-10"></th>
                  <th className="py-2.5 px-3 w-20">ID</th>
                  <th className="py-2.5 px-3 min-w-[200px]">Project Name</th>
                  <th className="py-2.5 px-3 w-32">Domain</th>
                  <th className="py-2.5 px-3 w-28">Phase</th>
                  <th className="py-2.5 px-3 w-32">Status</th>
                  <th className="py-2.5 px-3 w-36">% Complete</th>
                  <th className="py-2.5 px-3 w-24">Priority</th>
                  <th className="py-2.5 px-3 w-32">Business Owner</th>
                  <th className="py-2.5 px-3 w-16 text-center">Audit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {projects.map((proj) => {
                  const isExpanded = expandedProjectId === proj.id;
                  return (
                    <React.Fragment key={proj.id}>
                      <tr
                        className={`transition-colors ${
                          isExpanded ? "bg-amber-50/50" : "hover:bg-amber-50/20"
                        }`}
                      >
                        {/* Expand / Collapse Icon */}
                        <td className="py-2 px-2 text-center">
                          <button
                            onClick={() =>
                              setExpandedProjectId(isExpanded ? null : proj.id)
                            }
                            className="p-1 rounded hover:bg-stone-200 text-stone-500 transition-colors"
                            title="Expand child requirements"
                          >
                            {isExpanded ? (
                              <ChevronDown className="w-4 h-4 text-amber-800" />
                            ) : (
                              <ChevronRight className="w-4 h-4 text-stone-400" />
                            )}
                          </button>
                        </td>

                        {/* ID */}
                        <td className="py-2 px-3 font-mono font-bold text-amber-900">
                          {proj.id}
                        </td>

                        {/* Project Name (Inline Editable) */}
                        <td className="py-2 px-3">
                          <InlineTextCell
                            value={proj.project}
                            onSave={(val) => handleProjectUpdate(proj.id, { project: val })}
                          />
                        </td>

                        {/* Domain (Inline Select) */}
                        <td className="py-2 px-3">
                          <InlineSelectCell
                            value={proj.domain}
                            options={dropdowns?.domains || []}
                            onSave={(val) => handleProjectUpdate(proj.id, { domain: val })}
                          />
                        </td>

                        {/* Phase (Inline Select) */}
                        <td className="py-2 px-3">
                          <InlineSelectCell
                            value={proj.phase}
                            options={dropdowns?.phases || []}
                            onSave={(val) => handleProjectUpdate(proj.id, { phase: val })}
                          />
                        </td>

                        {/* Status (Inline Select with Badge Colors) */}
                        <td className="py-2 px-3">
                          <InlineSelectCell
                            value={proj.status}
                            options={dropdowns?.statuses || []}
                            onSave={(val) => handleProjectUpdate(proj.id, { status: val })}
                            badgeStyle
                            colorMap={statusColorMap}
                          />
                        </td>

                        {/* % Complete (Inline Interactive Slider) */}
                        <td className="py-2 px-3">
                          <InlineProgressCell
                            value={proj.percent_complete}
                            onSave={(val) =>
                              handleProjectUpdate(proj.id, { percent_complete: val })
                            }
                          />
                        </td>

                        {/* Priority */}
                        <td className="py-2 px-3">
                          <InlineSelectCell
                            value={proj.priority}
                            options={dropdowns?.priorities || []}
                            onSave={(val) => handleProjectUpdate(proj.id, { priority: val })}
                            badgeStyle
                            colorMap={priorityColorMap}
                          />
                        </td>

                        {/* Business Owner */}
                        <td className="py-2 px-3">
                          <InlineTextCell
                            value={proj.business_owner}
                            onSave={(val) =>
                              handleProjectUpdate(proj.id, { business_owner: val })
                            }
                          />
                        </td>

                        {/* Audit Log Drawer Trigger */}
                        <td className="py-2 px-2 text-center">
                          <button
                            onClick={() => setAuditEntityId(proj.id)}
                            className="p-1 rounded text-stone-400 hover:text-amber-800 hover:bg-amber-100 transition-colors"
                            title="View Revision Audit Trail"
                          >
                            <Clock className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>

                      {/* Expandable Requirements Sub-Panel */}
                      {isExpanded && (
                        <tr>
                          <td colSpan={10} className="p-0">
                            <RequirementsSubPanel
                              projectId={proj.id}
                              projectName={proj.project}
                              requirements={activeRequirementsData?.requirements || []}
                              dropdowns={dropdowns}
                            />
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Add Project Modal ─────────────────────────────────────────── */}
      <NewProjectModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        dropdowns={dropdowns}
        existingCount={projects.length}
      />

      {/* ── Audit History Drawer ──────────────────────────────────────── */}
      <AuditDrawer
        isOpen={Boolean(auditEntityId)}
        onClose={() => setAuditEntityId(null)}
        entityId={auditEntityId}
        history={auditData?.history || []}
        isLoading={isLoadingAudit}
      />
    </div>
  );
};

