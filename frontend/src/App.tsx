/**
 * App.tsx — Phase 5: Performance Optimized Orchestrator
 * ───────────────────────────────────────────────────────────────────────────
 * Key upgrades over Phase 4:
 *  • React.lazy() + Suspense for Recharts analytics tab (async chunk)
 *  • useDebouncedValue (300ms) on search query before passing to worker
 *  • useFilterWorker — Web Worker handles all regex/text filtering off main thread
 *  • CSS contain hints via inline style on the main scroll container
 *  • manualChunks splits: vendor-recharts, vendor-tanstack-table, vendor-tanstack-query
 */

import { useState, useMemo, lazy, Suspense } from "react";
import type { FC } from "react";
import { Navbar } from "./components/Navbar";
import { MetricCard } from "./components/MetricCard";
import { DomainFilterBar } from "./components/DomainFilterBar";
import { SearchAndFilterControls } from "./components/SearchAndFilterControls";
import { ApiStatusBadge } from "./components/ApiStatusBadge";
import { VirtualizedMatrixTable } from "./components/VirtualizedMatrixTable";
import { AnalyticsSkeleton } from "./components/AnalyticsSkeleton";
import {
  useSummary,
  useDomains,
  useTaxonomy,
  useRepositories,
  useStandardsAnalytics,
} from "./hooks/useApiQueries";
import { useDebouncedValue } from "./hooks/useDebouncedValue";
import { useFilterWorker } from "./hooks/useWorker";
import { queryClient } from "./providers/QueryProvider";
import type { Repository } from "./types/api";
import {
  Loader2,
  ShieldAlert,
  AlertCircle,
  Table as TableIcon,
  LayoutGrid,
  BarChart3,
  Zap,
} from "lucide-react";

// ── Lazy-loaded Analytics Components (split into vendor-recharts chunk) ───────
const DomainRadarChart = lazy(() => import("./components/DomainRadarChart"));
const StandardsBarChart = lazy(() => import("./components/StandardsBarChart"));
const MatrixCorrelationHeatmap = lazy(() => import("./components/MatrixCorrelationHeatmap"));
const RepositoryDetailDrawer = lazy(() => import("./components/RepositoryDetailDrawer"));

// ─── Loading Skeleton ─────────────────────────────────────────────────────────
const SkeletonCard = () => (
  <div
    className="rounded-xl p-5 border animate-pulse"
    style={{ backgroundColor: "var(--row-even)", borderColor: "var(--border)" }}
  >
    <div className="w-10 h-10 rounded-lg bg-stone-300 mb-4" />
    <div className="h-3 w-24 bg-stone-300 rounded mb-2" />
    <div className="h-7 w-16 bg-stone-200 rounded mb-1" />
    <div className="h-3 w-32 bg-stone-200 rounded" />
  </div>
);

// ─── Error Banner ─────────────────────────────────────────────────────────────
const ErrorBanner = ({ message }: { message: string }) => (
  <div
    className="rounded-xl border px-5 py-4 flex items-center gap-3"
    style={{ backgroundColor: "#FEF2F2", borderColor: "#FCA5A5" }}
  >
    <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
    <div>
      <p className="text-sm font-semibold text-red-800">API Error</p>
      <p className="text-xs text-red-700 mt-0.5">{message}</p>
      <p className="text-xs text-red-600 mt-1">
        Make sure the FastAPI server is running:{" "}
        <code className="bg-red-100 px-1 rounded">python -m uvicorn api:app --reload</code>
      </p>
    </div>
  </div>
);

// ─── Worker Status Badge ───────────────────────────────────────────────────────
const WorkerBadge = ({
  isFiltering,
  durationMs,
  count,
}: {
  isFiltering: boolean;
  durationMs: number;
  count: number;
}) => (
  <span
    className="inline-flex items-center gap-1.5 text-[11px] font-semibold px-2 py-0.5 rounded-full border"
    style={{
      backgroundColor: isFiltering ? "var(--row-even)" : "var(--highlight)",
      borderColor: "var(--border)",
      color: "var(--text)",
    }}
  >
    {isFiltering ? (
      <>
        <Loader2 className="w-3 h-3 animate-spin" />
        <span>Filtering…</span>
      </>
    ) : (
      <>
        <Zap className="w-3 h-3" />
        <span>
          {count} rows · {durationMs > 0 ? `${durationMs.toFixed(1)}ms` : "Worker"}
        </span>
      </>
    )}
  </span>
);

// ─── Main App ─────────────────────────────────────────────────────────────────
export const App: FC = () => {
  const [selectedDomainId, setSelectedDomainId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedStandards, setSelectedStandards] = useState<string[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const [viewMode, setViewMode] = useState<"table" | "cards">("table");
  const [activeTab, setActiveTab] = useState<"matrix" | "analytics">("matrix");
  const [inspectRepo, setInspectRepo] = useState<Repository | null>(null);

  // ── Debounced search — 300ms trailing, React concurrent-safe ─────────────
  const debouncedQuery = useDebouncedValue(searchQuery, 300);

  // ── API Queries ──────────────────────────────────────────────────────────
  const { data: summary, isLoading: summaryLoading, error: summaryError } = useSummary();
  const { data: domainsData, isLoading: domainsLoading } = useDomains();
  const { data: taxonomyData } = useTaxonomy();
  const { data: standardsData } = useStandardsAnalytics();

  // Fetch full portfolio (up to 300) — domain filter applied server-side
  const { data: reposData, isLoading: reposLoading } = useRepositories({
    domain: selectedDomainId
      ? (domainsData?.domains.find(
          (d) => d.domain.toLowerCase().replace(/[\s&]+/g, "-") === selectedDomainId
        )?.domain ?? undefined)
      : undefined,
    limit: 300,
    // NOTE: search is NOT passed to API — the Worker handles it client-side
    // so we avoid a network round-trip on every keystroke
  });

  // ── Derived Memos ─────────────────────────────────────────────────────────
  const allStandards = useMemo(() => {
    if (!domainsData?.domains) return [];
    const set = new Set<string>();
    domainsData.domains.forEach((d) => d.detected_standards.forEach((s) => set.add(s)));
    return Array.from(set).sort();
  }, [domainsData]);

  const domainNames = useMemo(() => {
    if (!domainsData?.domains) return [];
    return domainsData.domains.map((d) => d.domain);
  }, [domainsData]);

  const domainFilterList = useMemo(() => {
    if (!domainsData?.domains || !taxonomyData?.domains) return [];
    return domainsData.domains.map((d) => {
      const tax = taxonomyData.domains.find((t) => t.name === d.domain);
      return {
        id: d.domain.toLowerCase().replace(/[\s&]+/g, "-"),
        name: d.domain,
        description: tax?.description ?? "",
        standards: d.detected_standards,
        tokenCount: tax?.token_count ?? 0,
        coveragePercentage: d.avg_confidence_pct,
        repoCount: d.repo_count,
      };
    });
  }, [domainsData, taxonomyData]);

  // Raw repos from API (before text search)
  const rawRepos = useMemo(() => reposData?.items ?? [], [reposData]);

  // ── Web Worker Filter ─────────────────────────────────────────────────────
  // The worker handles: text search (plain or regex) + standards cross-filter
  const { filteredData, isFiltering, workerError, lastDurationMs } = useFilterWorker({
    repos: rawRepos,
    query: debouncedQuery,
    useRegex: false, // regex mode toggle is managed inside VirtualizedMatrixTable
    selectedStandards,
    enabled: !reposLoading,
  });

  // ── Handlers ──────────────────────────────────────────────────────────────
  const handleSync = async () => {
    setIsSyncing(true);
    await queryClient.invalidateQueries();
    setTimeout(() => setIsSyncing(false), 800);
  };

  const handleToggleStandard = (standard: string) => {
    setSelectedStandards((prev) =>
      prev.includes(standard) ? prev.filter((s) => s !== standard) : [...prev, standard]
    );
  };

  const handleSelectDomainByName = (domainName: string) => {
    const slug = domainName.toLowerCase().replace(/[\s&]+/g, "-");
    setSelectedDomainId((prev) => (prev === slug ? null : slug));
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#FAF7F2] text-[#1E140F]">
      {/* Top Navbar */}
      <Navbar
        onRefresh={handleSync}
        isRefreshing={isSyncing}
        statusBadge={<ApiStatusBadge />}
      />

      <main
        className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6"
        // CSS containment: prevents scroll/layout recalcs from propagating upward
        style={{ contain: "layout style" }}
      >
        {/* API Error Banner */}
        {summaryError && (
          <ErrorBanner message={(summaryError as Error).message} />
        )}

        {/* Worker Error Banner */}
        {workerError && (
          <div
            className="rounded-xl border px-5 py-3 flex items-center gap-3"
            style={{ backgroundColor: "#FFFBEB", borderColor: "#FCD34D" }}
          >
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            <p className="text-xs text-amber-800 font-mono">{workerError}</p>
          </div>
        )}

        {/* ── KPI Metric Ribbon ─────────────────────────────────────────── */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {summaryLoading ? (
            [0, 1, 2, 3].map((i) => <SkeletonCard key={i} />)
          ) : (
            <>
              <MetricCard
                title="Total Repositories"
                value={summary?.total_repositories ?? 0}
                subtitle={`${summary?.active_repositories ?? 0} active · ${(summary?.total_repositories ?? 0) - (summary?.active_repositories ?? 0)} archived`}
                badge={`${summary?.total_classified ?? 0} Classified`}
                icon="repos"
              />
              <MetricCard
                title="Domain Coverage"
                value={`${summary?.matrix_coverage_pct ?? 0}%`}
                subtitle="Complete taxonomy classification"
                badge="V2 Matrix"
                trend="+4.8%"
                icon="coverage"
              />
              <MetricCard
                title="Avg Confidence"
                value={`${summary?.avg_confidence_score ?? 0}%`}
                subtitle="Hybrid classifier confidence"
                trend="+12%"
                icon="tokens"
              />
              <MetricCard
                title="Standards Detected"
                value={summary?.unique_standards_detected ?? 0}
                subtitle="Unique clinical & operational standards"
                icon="domains"
              />
            </>
          )}
        </section>

        {/* ── Domain Filter Bar ──────────────────────────────────────────── */}
        <section className="space-y-4">
          {domainsLoading ? (
            <div className="flex items-center gap-2 py-2">
              <Loader2 className="w-4 h-4 animate-spin text-stone-500" />
              <span className="text-xs text-stone-500">Loading domain distribution...</span>
            </div>
          ) : (
            <DomainFilterBar
              domains={domainFilterList}
              selectedDomainId={selectedDomainId}
              onSelectDomain={setSelectedDomainId}
            />
          )}

          <SearchAndFilterControls
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            availableStandards={allStandards}
            selectedStandards={selectedStandards}
            onToggleStandard={handleToggleStandard}
            onClearStandards={() => setSelectedStandards([])}
          />
        </section>

        {/* ── Dashboard Navigation Tabs ──────────────────────────────────── */}
        <div
          className="flex items-center gap-2 border-b pb-1"
          style={{ borderColor: "var(--border)" }}
        >
          <button
            type="button"
            onClick={() => setActiveTab("matrix")}
            className={`flex items-center gap-2 px-4 py-2 rounded-t-lg text-xs font-bold transition-all border-b-2 ${
              activeTab === "matrix"
                ? "border-[#4A3426] text-white shadow-xs"
                : "border-transparent text-stone-600 hover:text-stone-900"
            }`}
            style={{
              backgroundColor:
                activeTab === "matrix" ? "var(--header-bg)" : "transparent",
            }}
          >
            <TableIcon className="w-4 h-4" />
            <span>Portfolio Matrix Table</span>
            <span
              className="text-[10px] px-1.5 py-0.5 rounded-full font-mono"
              style={{
                backgroundColor:
                  activeTab === "matrix" ? "var(--highlight)" : "var(--row-even)",
                color: "var(--text)",
              }}
            >
              {filteredData.length}
            </span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("analytics")}
            className={`flex items-center gap-2 px-4 py-2 rounded-t-lg text-xs font-bold transition-all border-b-2 ${
              activeTab === "analytics"
                ? "border-[#4A3426] text-white shadow-xs"
                : "border-transparent text-stone-600 hover:text-stone-900"
            }`}
            style={{
              backgroundColor:
                activeTab === "analytics" ? "var(--header-bg)" : "transparent",
            }}
          >
            <BarChart3 className="w-4 h-4" />
            <span>Visualizations &amp; Analytics</span>
            <span
              className="text-[10px] px-1.5 py-0.5 rounded-full font-mono uppercase"
              style={{
                backgroundColor:
                  activeTab === "analytics" ? "var(--highlight)" : "var(--row-even)",
                color: "var(--text)",
              }}
            >
              Phase 5
            </span>
          </button>
        </div>

        {/* ── TAB 1: PORTFOLIO MATRIX ────────────────────────────────────── */}
        {activeTab === "matrix" && (
          <section className="space-y-3">
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div className="flex items-center gap-3 flex-wrap">
                <h2 className="text-sm font-bold uppercase tracking-wider text-stone-700">
                  {reposLoading
                    ? "Loading Portfolio Matrix..."
                    : `Portfolio Matrix (${rawRepos.length} total)`}
                </h2>
                <WorkerBadge
                  isFiltering={isFiltering}
                  durationMs={lastDurationMs}
                  count={filteredData.length}
                />
              </div>

              {/* View Mode Toggle */}
              <div
                className="flex items-center p-1 rounded-lg border bg-white shadow-xs"
                style={{ borderColor: "var(--border)" }}
              >
                <button
                  type="button"
                  onClick={() => setViewMode("table")}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-semibold transition-all ${
                    viewMode === "table"
                      ? "text-white shadow-xs"
                      : "text-stone-600 hover:text-stone-900"
                  }`}
                  style={{
                    backgroundColor:
                      viewMode === "table" ? "var(--header-bg)" : "transparent",
                  }}
                >
                  <TableIcon className="w-3.5 h-3.5" />
                  <span>Virtualized Table</span>
                </button>

                <button
                  type="button"
                  onClick={() => setViewMode("cards")}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-semibold transition-all ${
                    viewMode === "cards"
                      ? "text-white shadow-xs"
                      : "text-stone-600 hover:text-stone-900"
                  }`}
                  style={{
                    backgroundColor:
                      viewMode === "cards" ? "var(--header-bg)" : "transparent",
                  }}
                >
                  <LayoutGrid className="w-3.5 h-3.5" />
                  <span>Card Grid</span>
                </button>
              </div>
            </div>

            {/* Table or Cards */}
            {viewMode === "table" ? (
              <VirtualizedMatrixTable
                data={filteredData}
                isLoading={reposLoading || isFiltering}
                onSelectStandard={handleToggleStandard}
                onSelectRepository={setInspectRepo}
              />
            ) : reposLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[0, 1, 2, 3, 4, 5].map((i) => <SkeletonCard key={i} />)}
              </div>
            ) : filteredData.length === 0 ? (
              <div
                className="rounded-xl border p-12 text-center"
                style={{ backgroundColor: "var(--row-even)", borderColor: "var(--border)" }}
              >
                <ShieldAlert className="w-10 h-10 mx-auto text-amber-800 mb-2 opacity-80" />
                <p className="font-bold text-base text-stone-800">No matching repositories found</p>
                <p className="text-xs text-stone-600 mt-1 max-w-md mx-auto">
                  Adjust your search query, domain scope, or standards filter.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredData.map((repo, index) => {
                  const isEven = index % 2 === 1;
                  const confidencePct = Math.round((repo.confidence_score ?? 0) * 100);
                  return (
                    <div
                      key={repo.name_with_owner}
                      onClick={() => setInspectRepo(repo)}
                      className="rounded-xl border p-5 transition-all duration-200 hover:shadow-card flex flex-col justify-between cursor-pointer group"
                      style={{
                        backgroundColor: isEven ? "var(--row-even)" : "var(--row-odd)",
                        borderColor: "var(--border)",
                      }}
                    >
                      <div>
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <h3 className="font-bold text-sm text-stone-900 group-hover:text-[#4A3426] leading-snug">
                              {repo.name}
                            </h3>
                            <p className="text-[11px] text-stone-500 font-mono mt-0.5">
                              {repo.owner}
                            </p>
                          </div>
                          <span
                            className="text-[11px] font-bold px-2 py-0.5 rounded-full border whitespace-nowrap shrink-0"
                            style={{
                              backgroundColor: "var(--highlight)",
                              borderColor: "var(--border)",
                            }}
                          >
                            {confidencePct}%
                          </span>
                        </div>

                        {repo.description && (
                          <p className="text-xs text-stone-700 mt-2 line-clamp-2 leading-relaxed">
                            {repo.description}
                          </p>
                        )}

                        <div className="flex flex-wrap gap-1 mt-2.5">
                          <span
                            className="text-[11px] font-semibold px-2 py-0.5 rounded border"
                            style={{
                              backgroundColor: "var(--header-bg)",
                              color: "var(--header-text)",
                              borderColor: "var(--border)",
                            }}
                          >
                            {repo.primary_domain}
                          </span>
                        </div>
                      </div>

                      <div className="mt-4 pt-3 border-t border-stone-200/80 flex items-center justify-between">
                        <div className="flex flex-wrap gap-1">
                          {repo.detected_standards.slice(0, 3).map((std) => (
                            <span
                              key={std}
                              className="text-[10px] px-1.5 py-0.5 rounded bg-white border border-stone-300 font-mono text-stone-700"
                            >
                              {std}
                            </span>
                          ))}
                        </div>
                        {repo.primary_language && (
                          <span className="text-[11px] text-stone-500 font-mono">
                            {repo.primary_language}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        )}

        {/* ── TAB 2: ANALYTICS (Lazy loaded Recharts chunk) ─────────────── */}
        {activeTab === "analytics" && (
          <Suspense fallback={<AnalyticsSkeleton />}>
            <section className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <DomainRadarChart
                  data={domainsData?.domains ?? []}
                  selectedDomain={
                    selectedDomainId
                      ? domainsData?.domains.find(
                          (d) =>
                            d.domain.toLowerCase().replace(/[\s&]+/g, "-") ===
                            selectedDomainId
                        )?.domain
                      : null
                  }
                  onSelectDomain={handleSelectDomainByName}
                />

                <StandardsBarChart
                  data={standardsData?.standards ?? []}
                  selectedStandards={selectedStandards}
                  onSelectStandard={handleToggleStandard}
                />
              </div>

              <MatrixCorrelationHeatmap
                repositories={rawRepos}
                domains={domainNames}
                onSelectDomainPair={(primary, _secondary) => {
                  handleSelectDomainByName(primary);
                  setActiveTab("matrix");
                }}
              />
            </section>
          </Suspense>
        )}
      </main>

      {/* Drawer: lazy-loaded (Recharts chunk already downloaded if analytics visited) */}
      <Suspense fallback={null}>
        <RepositoryDetailDrawer
          repository={inspectRepo}
          onClose={() => setInspectRepo(null)}
        />
      </Suspense>

      {/* Footer */}
      <footer
        className="w-full border-t py-4 px-6 text-center text-xs mt-12"
        style={{ borderColor: "var(--border)", backgroundColor: "var(--row-even)", color: "var(--text)" }}
      >
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Andalusia Healthcare Portfolio · Phase 5 Performance Optimized</span>
          <span className="font-mono text-[11px] opacity-75">
            React.lazy · Web Worker Filter · Debounced Search · Code-Split Recharts
          </span>
        </div>
      </footer>
    </div>
  );
};

export default App;
