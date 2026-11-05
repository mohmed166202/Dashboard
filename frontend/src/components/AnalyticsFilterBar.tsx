import React, { useState, useRef, useEffect } from "react";
import type { Project, DropdownLists, KpiFilterParams } from "../types/tracker";
import {
  Search,
  Filter,
  X,
  Plus,
  Check,
  RotateCcw,
  Sparkles,
  Layers,
  ChevronDown,
  Building2,
} from "lucide-react";

interface AnalyticsFilterBarProps {
  projects: Project[];
  dropdowns?: DropdownLists;
  filters: KpiFilterParams;
  onFilterChange: (filters: KpiFilterParams) => void;
  matchedProjectsCount: number;
  totalProjectsCount: number;
}

export const AnalyticsFilterBar: React.FC<AnalyticsFilterBarProps> = ({
  projects,
  dropdowns,
  filters,
  onFilterChange,
  matchedProjectsCount,
  totalProjectsCount,
}) => {
  const [projectSearch, setProjectSearch] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close project selector dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const selectedProjectIds = filters.projects || [];

  // Toggle Project in selection
  const handleToggleProject = (id: string) => {
    const isSelected = selectedProjectIds.includes(id);
    const updated = isSelected
      ? selectedProjectIds.filter((p) => p !== id)
      : [...selectedProjectIds, id];
    onFilterChange({ ...filters, projects: updated.length > 0 ? updated : undefined });
  };

  // Remove Project Pill
  const handleRemoveProject = (id: string) => {
    const updated = selectedProjectIds.filter((p) => p !== id);
    onFilterChange({ ...filters, projects: updated.length > 0 ? updated : undefined });
  };

  // Filtered list of selectable projects in the dropdown
  const filteredProjects = projects.filter((p) => {
    const term = projectSearch.toLowerCase();
    const matchesSearch =
      p.id.toLowerCase().includes(term) ||
      p.project.toLowerCase().includes(term) ||
      (p.domain && p.domain.toLowerCase().includes(term));
    // If sector domain is selected, only show projects in that domain
    const matchesDomain = !filters.domain || p.domain === filters.domain;
    return matchesSearch && matchesDomain;
  });

  // Quick Preset Actions
  const applyPreset = (preset: "TOP2_LIVE" | "CLINICAL_INFORMATICS" | "GOVERNANCE" | "CLEAR") => {
    switch (preset) {
      case "TOP2_LIVE": {
        // AI-001 (MedVoice V2) and AI-006 (Clinical Notes AI Analyzer V2)
        onFilterChange({
          projects: ["AI-001", "AI-006"],
          domain: undefined,
          phase: undefined,
        });
        break;
      }
      case "CLINICAL_INFORMATICS": {
        onFilterChange({
          domain: "1. Clinical Informatics",
          projects: undefined,
          phase: undefined,
        });
        break;
      }
      case "GOVERNANCE": {
        onFilterChange({
          domain: "2. Clinical Governance",
          projects: undefined,
          phase: undefined,
        });
        break;
      }
      case "CLEAR": {
        onFilterChange({});
        break;
      }
    }
  };

  const isAnyFilterActive = Boolean(
    (filters.projects && filters.projects.length > 0) ||
      filters.domain ||
      filters.phase ||
      filters.priority ||
      filters.status
  );

  return (
    <div className="bg-white rounded-2xl border border-stone-200/90 p-5 shadow-xs space-y-4">
      {/* ── Header Strip: Title, Filter Counter & Reset ────────────────── */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-stone-100">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center">
            <Filter className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-stone-900 tracking-tight">
                Dynamic Scope & Comparison Filters
              </h3>
              <span className="text-xs px-2 py-0.5 rounded-full font-bold bg-amber-50 text-amber-900 border border-amber-200">
                {matchedProjectsCount} of {totalProjectsCount} Projects Scoped
              </span>
            </div>
            <p className="text-[11px] text-stone-500">
              Isolate a single project, compare 2 or more projects, or filter by healthcare sector domain
            </p>
          </div>
        </div>

        {/* Quick Presets & Clear */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <span className="text-stone-400 font-medium mr-1 hidden sm:inline">Presets:</span>
          <button
            onClick={() => applyPreset("TOP2_LIVE")}
            className="px-2.5 py-1 rounded-lg bg-amber-50 text-amber-900 hover:bg-amber-100 font-semibold border border-amber-200 transition-colors flex items-center gap-1"
          >
            <Sparkles className="w-3 h-3 text-amber-600" />
            Compare Top 2 AI Products
          </button>
          <button
            onClick={() => applyPreset("CLINICAL_INFORMATICS")}
            className="px-2.5 py-1 rounded-lg bg-stone-100 text-stone-700 hover:bg-stone-200 font-medium transition-colors"
          >
            Clinical Informatics
          </button>
          <button
            onClick={() => applyPreset("GOVERNANCE")}
            className="px-2.5 py-1 rounded-lg bg-stone-100 text-stone-700 hover:bg-stone-200 font-medium transition-colors"
          >
            Clinical Governance
          </button>
          {isAnyFilterActive && (
            <button
              onClick={() => applyPreset("CLEAR")}
              className="px-2.5 py-1 rounded-lg text-rose-700 hover:bg-rose-50 font-semibold transition-colors flex items-center gap-1"
              title="Reset all filters"
            >
              <RotateCcw className="w-3 h-3" />
              Reset All
            </button>
          )}
        </div>
      </div>

      {/* ── Main Filter Controls: Sector / Domain & Project Pill Selector ─ */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-3 text-xs">
        {/* Sector / Domain Dropdown (Col 1 to 4) */}
        <div className="md:col-span-4 space-y-1">
          <label className="block font-bold text-stone-700 uppercase tracking-wider text-[10px] flex items-center gap-1">
            <Building2 className="w-3 h-3 text-stone-500" /> Sector / Healthcare Domain
          </label>
          <select
            value={filters.domain || ""}
            onChange={(e) =>
              onFilterChange({
                ...filters,
                domain: e.target.value || undefined,
              })
            }
            className="w-full p-2 rounded-xl border border-stone-300 bg-white text-stone-800 font-medium focus:outline-none focus:ring-1 focus:ring-amber-500 shadow-xs"
          >
            <option value="">All Sectors & Domains ({dropdowns?.domains.length || 9})</option>
            {dropdowns?.domains.map((d) => (
              <option key={d.code} value={d.code}>
                {d.label}
              </option>
            ))}
          </select>
        </div>

        {/* Multi-Project Searchable Pill Selector (Col 5 to 12) */}
        <div className="md:col-span-8 space-y-1 relative" ref={dropdownRef}>
          <label className="block font-bold text-stone-700 uppercase tracking-wider text-[10px] flex items-center gap-1">
            <Layers className="w-3 h-3 text-stone-500" /> Focus Project(s) / Comparison Scope
          </label>

          <div
            onClick={() => setIsDropdownOpen(true)}
            className="w-full min-h-[38px] p-1.5 rounded-xl border border-stone-300 bg-white flex flex-wrap items-center gap-1.5 cursor-pointer focus-within:ring-1 focus-within:ring-amber-500 shadow-xs"
          >
            {selectedProjectIds.length === 0 ? (
              <span className="text-stone-400 px-2 py-0.5 text-xs">
                All Projects selected. Click to select 1 project or compare multiple...
              </span>
            ) : (
              selectedProjectIds.map((pid) => {
                const proj = projects.find((p) => p.id === pid);
                return (
                  <span
                    key={pid}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-amber-100 text-amber-900 border border-amber-300 text-xs font-semibold animate-in fade-in zoom-in-95 duration-100"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <span className="font-mono text-[11px] text-amber-700">{pid}</span>
                    <span className="truncate max-w-[150px]">{proj?.project || pid}</span>
                    <button
                      onClick={() => handleRemoveProject(pid)}
                      className="p-0.5 rounded-full hover:bg-amber-200 text-amber-800"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                );
              })
            )}
            <ChevronDown className="w-3.5 h-3.5 text-stone-400 ml-auto mr-1" />
          </div>

          {/* Searchable Dropdown Popup */}
          {isDropdownOpen && (
            <div className="absolute z-30 left-0 right-0 mt-1 bg-white rounded-xl border border-stone-300 shadow-xl p-2 space-y-2 animate-in fade-in duration-100 max-h-72 flex flex-col">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-stone-400" />
                <input
                  type="text"
                  placeholder="Search project name or ID..."
                  autoFocus
                  value={projectSearch}
                  onChange={(e) => setProjectSearch(e.target.value)}
                  className="w-full pl-8 pr-3 py-1.5 rounded-lg border border-stone-200 bg-stone-50 text-xs focus:outline-none focus:bg-white"
                />
              </div>

              <div className="overflow-y-auto flex-1 divide-y divide-stone-100">
                {filteredProjects.length === 0 ? (
                  <div className="py-4 text-center text-xs text-stone-400">
                    No matching projects found.
                  </div>
                ) : (
                  filteredProjects.map((p) => {
                    const isSelected = selectedProjectIds.includes(p.id);
                    return (
                      <div
                        key={p.id}
                        onClick={() => handleToggleProject(p.id)}
                        className={`p-2 rounded-lg flex items-center justify-between cursor-pointer transition-colors ${
                          isSelected ? "bg-amber-50 text-amber-900" : "hover:bg-stone-50"
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <div
                            className={`w-4 h-4 rounded border flex items-center justify-center text-white ${
                              isSelected ? "bg-amber-800 border-amber-800" : "border-stone-300 bg-white"
                            }`}
                          >
                            {isSelected && <Check className="w-3 h-3" />}
                          </div>
                          <span className="font-mono text-xs font-bold text-amber-800">{p.id}</span>
                          <span className="font-medium text-xs text-stone-800">{p.project}</span>
                        </div>
                        <span className="text-[10px] text-stone-400 bg-stone-100 px-1.5 py-0.5 rounded">
                          {p.phase}
                        </span>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── Delivery Phase Multi-Chips ─────────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-stone-100 text-xs">
        <span className="text-[11px] font-bold text-stone-500 uppercase tracking-wider">
          Filter by Phase:
        </span>
        {["Live", "UAT", "Development", "Planning", "Idea"].map((phaseOption) => {
          const isActive = filters.phase?.includes(phaseOption);
          return (
            <button
              key={phaseOption}
              onClick={() => {
                let currentPhases = filters.phase ? filters.phase.split(",") : [];
                if (currentPhases.includes(phaseOption)) {
                  currentPhases = currentPhases.filter((ph) => ph !== phaseOption);
                } else {
                  currentPhases.push(phaseOption);
                }
                onFilterChange({
                  ...filters,
                  phase: currentPhases.length > 0 ? currentPhases.join(",") : undefined,
                });
              }}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold border transition-all ${
                isActive
                  ? "bg-amber-800 text-white border-amber-800 shadow-xs"
                  : "bg-white text-stone-600 border-stone-200 hover:bg-stone-50"
              }`}
            >
              {phaseOption}
            </button>
          );
        })}
      </div>
    </div>
  );
};

