import React, { useState, useMemo } from "react";
import {
  Briefcase,
  ArrowRight,
  Sparkles,
  Target,
  Award,
  CheckCircle2,
  Clock,
  TrendingUp,
  DollarSign,
  Users,
  Search,
  Filter,
  Layers,
  ChevronDown,
  AlertCircle,
  ExternalLink,
  ShieldCheck,
  Check,
  Building2,
  Calendar,
  UserCheck,
  Activity,
  BarChart3,
  Globe,
  SlidersHorizontal,
  ChevronRight,
  Gauge,
  HelpCircle,
} from "lucide-react";
import {
  useProjects,
  useProjectSummary,
  useKpiSummary,
  useKpiBenchmarks,
  useRequirements,
} from "../hooks/useTrackerQueries";
import { FeatureSummary, BenchmarkComparison } from "../types/tracker";

interface ProjectSummaryTabProps {
  onNavigateToTracker?: () => void;
  onNavigateToAnalytics?: () => void;
}

export const ProjectSummaryTab: React.FC<ProjectSummaryTabProps> = ({
  onNavigateToTracker,
  onNavigateToAnalytics,
}) => {
  // ── Fetch Projects & Portfolio Aggregate ────────────────────────────────────
  const { data: projectsData, isLoading: isLoadingProjects } = useProjects();
  const projects = projectsData?.projects || [];

  const { data: portfolioKpis, isLoading: isLoadingPortfolio } = useKpiSummary();
  const { data: portfolioBenchmarksData } = useKpiBenchmarks();
  const { data: allRequirementsData } = useRequirements();

  // "ALL" represents the whole Portfolio aggregate view, or specific initiative ID
  const [selectedProjectId, setSelectedProjectId] = useState<string>("AI-001");
  const [featureSearch, setFeatureSearch] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [categoryFilter, setCategoryFilter] = useState<string>("ALL");

  const isPortfolioMode = selectedProjectId === "ALL";

  // ── Fetch Project-Specific Summary & Benchmarks ─────────────────────────────
  const {
    data: summaryData,
    isLoading: isLoadingSummary,
    isError,
  } = useProjectSummary(isPortfolioMode ? "" : selectedProjectId);

  const project = summaryData?.project;
  const projectOverview = summaryData?.overview;

  // ── Synthesize Portfolio Feature Deliverables when in Portfolio Mode ────────
  const portfolioFeatures: FeatureSummary[] = useMemo(() => {
    if (!isPortfolioMode || !allRequirementsData?.requirements) return [];
    return allRequirementsData.requirements.map((req) => ({
      req_id: req.req_id,
      feature_name: req.requirement,
      category: req.category,
      nfr_area: req.nfr_area || null,
      description: req.description || "System functional specification requirement.",
      status: req.status || "Proposed",
      priority: req.priority || "Medium",
      business_impact: req.business_benefit || "Direct operational workflow efficiency.",
      financial_impact_sar: 12500, // Normalized portfolio feature value
      time_saved_hrs: 10.4,
      owner: req.owner || req.project || "AI Team",
      target_date: req.target_date || null,
    }));
  }, [isPortfolioMode, allRequirementsData]);

  // Unified Features list
  const activeFeatures: FeatureSummary[] = useMemo(() => {
    if (isPortfolioMode) return portfolioFeatures;
    return summaryData?.features || [];
  }, [isPortfolioMode, portfolioFeatures, summaryData]);

  // Unified Benchmarks list
  const activeBenchmarks: BenchmarkComparison[] = useMemo(() => {
    if (isPortfolioMode) {
      if (!portfolioBenchmarksData?.benchmarks) return [];
      return portfolioBenchmarksData.benchmarks.map((b) => ({
        metric_key: b.metric_key,
        metric_name: b.metric_name,
        actual_value: b.current_value,
        target_value: b.target_value,
        benchmark_min: b.benchmark_min,
        benchmark_max: b.benchmark_max,
        unit: b.unit,
        benchmark_unit: b.benchmark_unit,
        source: b.source,
        notes: b.notes,
        status: b.status,
      }));
    }
    return summaryData?.benchmarks || [];
  }, [isPortfolioMode, portfolioBenchmarksData, summaryData]);

  // ── Filter Features based on search & filters ──────────────────────────────
  const filteredFeatures = useMemo(() => {
    const q = featureSearch.toLowerCase().trim();
    return activeFeatures.filter((f) => {
      const matchesSearch =
        q === "" ||
        f.feature_name.toLowerCase().includes(q) ||
        f.req_id.toLowerCase().includes(q) ||
        (f.description && f.description.toLowerCase().includes(q)) ||
        (f.business_impact && f.business_impact.toLowerCase().includes(q)) ||
        (f.owner && f.owner.toLowerCase().includes(q));

      const matchesStatus = statusFilter === "ALL" || f.status === statusFilter;
      const matchesCategory = categoryFilter === "ALL" || f.category === categoryFilter;

      return matchesSearch && matchesStatus && matchesCategory;
    });
  }, [activeFeatures, featureSearch, statusFilter, categoryFilter]);

  // Extract unique statuses and categories for filter dropdowns
  const uniqueStatuses = useMemo(() => {
    const set = new Set<string>();
    activeFeatures.forEach((f) => {
      if (f.status) set.add(f.status);
    });
    return Array.from(set);
  }, [activeFeatures]);

  const uniqueCategories = useMemo(() => {
    const set = new Set<string>();
    activeFeatures.forEach((f) => {
      if (f.category) set.add(f.category);
    });
    return Array.from(set);
  }, [activeFeatures]);

  // ── Unified Financial & Operational Metrics ────────────────────────────────
  const unifiedMetrics = useMemo(() => {
    if (isPortfolioMode) {
      const pSummary = portfolioKpis?.portfolio_summary;
      const kpis = portfolioKpis?.core_kpis;
      return {
        revenue_sar: kpis?.revenue_impact?.current_value || 1278000,
        net_profit_sar: kpis?.net_profit?.current_value || 894600,
        hours_saved: kpis?.time_saved_hours?.current_value || 2495,
        productivity_pct: kpis?.productivity_gain?.current_value || 34.5,
        csat_score: kpis?.customer_satisfaction?.current_value || 8.6,
        adoption_rate: kpis?.adoption_rate?.current_value || 78.4,
        subscribers: kpis?.current_subscribers?.current_value || 420,
        total_features: pSummary?.total_requirements || 240,
        implemented_features: pSummary?.implemented_requirements || 140,
        implementation_pct: pSummary?.req_implementation_pct || 58.3,
        avg_progress: pSummary?.avg_progress_pct || 47.5,
      };
    }

    const fm = projectOverview?.financial_metrics;
    return {
      revenue_sar: fm?.revenue_impact_sar || 0,
      net_profit_sar: fm?.net_profit_sar || 0,
      hours_saved: fm?.time_saved_hrs || 0,
      productivity_pct: fm?.productivity_pct || 0,
      csat_score: fm?.csat_score || 0,
      adoption_rate: fm?.adoption_rate || 0,
      subscribers: fm?.current_subscribers || 0,
      total_features: projectOverview?.total_features || 0,
      implemented_features: projectOverview?.implemented_features || 0,
      implementation_pct: projectOverview?.implementation_pct || 0,
      avg_progress: project ? Math.round((project.percent_complete || 0) * 100) : 0,
    };
  }, [isPortfolioMode, portfolioKpis, projectOverview, project]);

  // Status badge styling helper
  const getStatusBadge = (status: string) => {
    const s = status.toLowerCase();
    if (s.includes("implement") || s.includes("done") || s.includes("live") || s.includes("verified")) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
          {status}
        </span>
      );
    }
    if (s.includes("progress") || s.includes("uat") || s.includes("pilot")) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
          <Clock className="w-3 h-3 text-amber-600" />
          {status}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-stone-100 text-stone-700 border border-stone-200">
        <Activity className="w-3 h-3 text-stone-500" />
        {status}
      </span>
    );
  };

  // Benchmark status badge helper
  const getBenchmarkBadge = (status: BenchmarkComparison["status"]) => {
    switch (status) {
      case "EXCEEDING":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-black tracking-wider bg-emerald-100 text-emerald-800 border border-emerald-300">
            EXCEEDING TARGET
          </span>
        );
      case "ON_TARGET":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-black tracking-wider bg-amber-100 text-amber-800 border border-amber-300">
            ON TARGET
          </span>
        );
      case "BELOW_BENCHMARK":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-black tracking-wider bg-rose-100 text-rose-800 border border-rose-300">
            ATTENTION NEEDED
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6 w-full max-w-full pb-12 animate-fadeIn">
      {/* ── 1. Executive Quick Switcher & Header ─────────────────────────── */}
      <div className="bg-white rounded-2xl p-5 border border-stone-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl bg-amber-700 text-amber-50 flex items-center justify-center font-bold shadow-xs">
            <Briefcase className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-black text-stone-900 tracking-tight flex items-center gap-2">
              <span>Executive Project Summary</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold border border-emerald-200 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Live Strategic View
              </span>
            </h1>
            <p className="text-xs text-stone-500">
              Feature deliverables, clinical & financial ROI attribution, and industry performance benchmarks.
            </p>
          </div>
        </div>

        {/* Project Selector Dropdown with Portfolio Aggregate Option */}
        <div className="flex items-center gap-3">
          <label htmlFor="project-picker" className="text-xs font-bold text-stone-600 uppercase tracking-wider shrink-0">
            Scope / Initiative:
          </label>
          <div className="relative min-w-[280px] sm:min-w-[360px]">
            <select
              id="project-picker"
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              disabled={isLoadingProjects}
              className="w-full appearance-none bg-stone-50 border border-stone-300 hover:border-amber-600 focus:border-amber-600 rounded-xl px-4 py-2.5 text-xs font-bold text-stone-900 shadow-2xs focus:outline-hidden focus:ring-2 focus:ring-amber-500/20 transition-all pr-10 cursor-pointer"
            >
              <option value="ALL">🌐 Entire AI Portfolio (All 28 Initiatives Aggregate)</option>
              <optgroup label="Clinical & Operational Initiatives">
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.id} · {p.project} {p.domain ? `(${p.domain.split(". ")[1] || p.domain})` : ""}
                  </option>
                ))}
              </optgroup>
            </select>
            <ChevronDown className="w-4 h-4 text-stone-500 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        </div>
      </div>

      {isLoadingSummary && !isPortfolioMode ? (
        <div className="bg-white rounded-2xl p-16 border border-stone-200 text-center space-y-3">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-amber-600 border-t-transparent" />
          <p className="text-sm font-semibold text-stone-600">Loading project deliverables & benchmarks...</p>
        </div>
      ) : isError && !isPortfolioMode ? (
        <div className="bg-rose-50 border border-rose-200 rounded-2xl p-8 text-center text-rose-800">
          <AlertCircle className="w-8 h-8 mx-auto mb-2 text-rose-600" />
          <h3 className="text-base font-bold">Failed to load project summary</h3>
          <p className="text-xs text-rose-600 mt-1">Please select another initiative or try again.</p>
        </div>
      ) : (
        <>
          {/* ── 2. Executive Overview Hero Banner ──────────────────────────── */}
          <div className="bg-gradient-to-r from-[#38261A] via-[#4d3627] to-[#2c1d13] text-amber-50 rounded-2xl p-6 sm:p-7 shadow-sm border border-amber-900/40 relative overflow-hidden">
            <div className="relative z-10 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="px-2.5 py-1 rounded-md bg-amber-400/25 text-amber-300 text-xs font-black border border-amber-400/30">
                    {isPortfolioMode ? "PORTFOLIO AGGREGATE" : project?.id}
                  </span>
                  <span className="px-2.5 py-1 rounded-md bg-white/10 text-stone-200 text-xs font-semibold border border-white/10">
                    {isPortfolioMode ? "All 8 Healthcare Domains" : project?.domain}
                  </span>
                  <span className="px-2.5 py-1 rounded-md bg-emerald-500/20 text-emerald-300 text-xs font-bold border border-emerald-500/30">
                    {isPortfolioMode ? "Status: 28 Active Projects" : `Phase: ${project?.phase}`}
                  </span>
                  {!isPortfolioMode && project?.status && (
                    <span className="px-2.5 py-1 rounded-md bg-blue-500/20 text-blue-300 text-xs font-bold border border-blue-500/30">
                      Status: {project.status}
                    </span>
                  )}
                </div>

                {/* Direct Deep-Links to Matrix & Analytics */}
                <div className="flex items-center gap-2">
                  {onNavigateToTracker && (
                    <button
                      onClick={onNavigateToTracker}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-amber-100 text-xs font-semibold border border-white/15 transition-all cursor-pointer"
                    >
                      <span>Delivery Matrix</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                  {onNavigateToAnalytics && (
                    <button
                      onClick={onNavigateToAnalytics}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-400 hover:bg-amber-300 text-stone-900 text-xs font-black transition-all shadow-xs cursor-pointer"
                    >
                      <span>Detailed Analytics</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>

              <div>
                <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                  {isPortfolioMode ? "Andalusia Enterprise AI Strategic Portfolio" : project?.project}
                </h2>
                <p className="text-stone-300 text-xs sm:text-sm mt-1.5 max-w-5xl leading-relaxed">
                  {isPortfolioMode
                    ? "Comprehensive governance view consolidating 28 clinical, operational, and administrative AI initiatives across Andalusia Health clusters. Features automated financial ROI tracking, clinician time savings, and international healthcare benchmark alignment."
                    : project?.description}
                </p>
              </div>

              {/* Progress & Governance Metadata Grid */}
              <div className="pt-3 border-t border-white/10 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                <div>
                  <span className="text-amber-200/70 block text-[11px] font-semibold uppercase">Overall Completion</span>
                  <div className="flex items-center gap-3 mt-1">
                    <div className="flex-1 bg-white/15 rounded-full h-2.5 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-amber-400 to-emerald-400 h-full rounded-full transition-all duration-500"
                        style={{ width: `${unifiedMetrics.avg_progress}%` }}
                      />
                    </div>
                    <span className="font-bold text-white text-sm">
                      {unifiedMetrics.avg_progress}%
                    </span>
                  </div>
                </div>

                <div>
                  <span className="text-amber-200/70 block text-[11px] font-semibold uppercase">
                    {isPortfolioMode ? "Steering Committee" : "Business Owners"}
                  </span>
                  <span className="font-semibold text-stone-200 mt-1 block truncate">
                    {isPortfolioMode ? "Dr. Germeen / Clinical IT Steering" : project?.business_owner || "Dr. Germeen"}
                  </span>
                </div>

                <div>
                  <span className="text-amber-200/70 block text-[11px] font-semibold uppercase">
                    {isPortfolioMode ? "Lead Architecture" : "Technical Lead"}
                  </span>
                  <span className="font-semibold text-stone-200 mt-1 block truncate">
                    {isPortfolioMode ? "Enterprise AI Engineering Core" : project?.technical_owner || "AI Engineering Core"}
                  </span>
                </div>

                <div>
                  <span className="text-amber-200/70 block text-[11px] font-semibold uppercase">
                    {isPortfolioMode ? "Strategic Target" : "Target Due Date"}
                  </span>
                  <span className="font-semibold text-stone-200 mt-1 block">
                    {isPortfolioMode ? "Q4 2026 Milestone" : project?.due_date || "2026-11-30"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* ── 3. High-Impact KPI Cards (Financial & Operational) ───────────── */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Revenue Impact */}
            <div className="bg-white p-5 rounded-2xl border border-stone-200 shadow-2xs flex flex-col justify-between hover:border-amber-400 transition-all">
              <div className="flex items-center justify-between text-stone-500">
                <span className="text-xs font-bold uppercase tracking-wider text-stone-500">
                  Revenue Impact (SAR)
                </span>
                <div className="p-2 bg-emerald-50 text-emerald-700 rounded-xl">
                  <DollarSign className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-2xl font-black text-stone-900">
                  SAR {unifiedMetrics.revenue_sar.toLocaleString()}
                </div>
                <div className="flex items-center gap-1.5 mt-1 text-xs text-emerald-700 font-semibold">
                  <TrendingUp className="w-3.5 h-3.5" />
                  <span>Net Profit: SAR {unifiedMetrics.net_profit_sar.toLocaleString()}</span>
                </div>
              </div>
            </div>

            {/* Clinical Hours Saved */}
            <div className="bg-white p-5 rounded-2xl border border-stone-200 shadow-2xs flex flex-col justify-between hover:border-amber-400 transition-all">
              <div className="flex items-center justify-between text-stone-500">
                <span className="text-xs font-bold uppercase tracking-wider text-stone-500">
                  Clinician Time Saved
                </span>
                <div className="p-2 bg-amber-50 text-amber-700 rounded-xl">
                  <Clock className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-2xl font-black text-stone-900">
                  {unifiedMetrics.hours_saved.toLocaleString()} hrs
                </div>
                <div className="flex items-center gap-1.5 mt-1 text-xs text-amber-800 font-semibold">
                  <span>Productivity Uplift: +{unifiedMetrics.productivity_pct}%</span>
                </div>
              </div>
            </div>

            {/* Clinician CSAT & Adoption */}
            <div className="bg-white p-5 rounded-2xl border border-stone-200 shadow-2xs flex flex-col justify-between hover:border-amber-400 transition-all">
              <div className="flex items-center justify-between text-stone-500">
                <span className="text-xs font-bold uppercase tracking-wider text-stone-500">
                  Satisfaction & Adoption
                </span>
                <div className="p-2 bg-blue-50 text-blue-700 rounded-xl">
                  <Users className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-2xl font-black text-stone-900">
                  {unifiedMetrics.csat_score} / 10
                </div>
                <div className="flex items-center gap-1.5 mt-1 text-xs text-blue-700 font-semibold">
                  <span>Adoption: {unifiedMetrics.adoption_rate}% ({unifiedMetrics.subscribers} active users)</span>
                </div>
              </div>
            </div>

            {/* Feature Deliverables Completion */}
            <div className="bg-white p-5 rounded-2xl border border-stone-200 shadow-2xs flex flex-col justify-between hover:border-amber-400 transition-all">
              <div className="flex items-center justify-between text-stone-500">
                <span className="text-xs font-bold uppercase tracking-wider text-stone-500">
                  Feature Deliverables
                </span>
                <div className="p-2 bg-purple-50 text-purple-700 rounded-xl">
                  <Layers className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-2xl font-black text-stone-900">
                  {unifiedMetrics.implemented_features} / {unifiedMetrics.total_features}
                </div>
                <div className="flex items-center gap-1.5 mt-1 text-xs text-purple-700 font-semibold">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>{unifiedMetrics.implementation_pct}% Features Delivered</span>
                </div>
              </div>
            </div>
          </div>

          {/* ── 4. Project Benchmarks Strip ─────────────────────────────────── */}
          <div className="bg-white rounded-2xl p-6 border border-stone-200 shadow-2xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-stone-100 pb-3">
              <div>
                <h3 className="text-sm font-black text-stone-900 uppercase tracking-wider flex items-center gap-2">
                  <Award className="w-4 h-4 text-amber-700" />
                  <span>Calibrated Healthcare Industry Benchmarks</span>
                </h3>
                <p className="text-xs text-stone-500 mt-0.5">
                  Real-time comparison against KLAS Research, HIMSS, and Andalusia Healthcare clinical targets.
                </p>
              </div>
              <span className="text-xs font-semibold text-stone-600 bg-stone-100 px-2.5 py-1 rounded-md border border-stone-200 self-start sm:self-auto">
                {activeBenchmarks.length} Calibrated Benchmarks Active
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {activeBenchmarks.map((b) => (
                <div
                  key={b.metric_key}
                  className="bg-stone-50/70 p-3.5 rounded-xl border border-stone-200/70 flex flex-col justify-between hover:bg-stone-50 transition-colors"
                >
                  <div>
                    <div className="flex items-center justify-between gap-1 mb-1.5">
                      <span className="text-[11px] font-bold text-stone-700 truncate" title={b.metric_name}>
                        {b.metric_name}
                      </span>
                      {getBenchmarkBadge(b.status)}
                    </div>
                    <div className="text-lg font-black text-stone-900">
                      {b.actual_value?.toLocaleString()}{" "}
                      <span className="text-xs font-medium text-stone-500">{b.unit}</span>
                    </div>
                  </div>

                  <div className="mt-3 pt-2 border-t border-stone-200/60 text-[10px] space-y-0.5 text-stone-600">
                    <div className="flex justify-between">
                      <span className="text-stone-600">Industry Target:</span>
                      <span className="font-semibold text-stone-800">
                        {b.benchmark_min !== null ? `${b.benchmark_min}` : ""}{" "}
                        {b.benchmark_max !== null ? `– ${b.benchmark_max}` : ""} {b.benchmark_unit}
                      </span>
                    </div>
                    <div className="flex justify-between text-stone-600 truncate" title={b.source}>
                      <span>Source:</span>
                      <span className="truncate max-w-[140px] text-stone-600">{b.source}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* ── 5. Feature-Level Deliverables Matrix (Primary Value) ────────── */}
          <div className="bg-white rounded-2xl border border-stone-200 shadow-2xs overflow-hidden">
            <div className="p-6 border-b border-stone-200 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <h3 className="text-base font-black text-stone-900 tracking-tight flex items-center gap-2">
                    <Layers className="w-5 h-5 text-amber-700" />
                    <span>Feature Deliverables & Direct Impact Attribution</span>
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 font-bold">
                      {filteredFeatures.length} of {activeFeatures.length} Features
                    </span>
                  </h3>
                  <p className="text-xs text-stone-500 mt-1">
                    Granular breakdown of every functional capability, technical non-functional requirement, and attributed SAR return.
                  </p>
                </div>
              </div>

              {/* Filter & Search Bar */}
              <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 pt-1">
                {/* Search */}
                <div className="sm:col-span-6 relative">
                  <Search className="w-4 h-4 text-stone-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="text"
                    value={featureSearch}
                    onChange={(e) => setFeatureSearch(e.target.value)}
                    placeholder="Search features, descriptions, owners, or impact..."
                    className="w-full bg-stone-50 border border-stone-300 rounded-xl pl-9 pr-3 py-2 text-xs text-stone-900 focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
                  />
                </div>

                {/* Status Filter */}
                <div className="sm:col-span-3">
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3 py-2 text-xs font-semibold text-stone-700 focus:outline-hidden focus:ring-2 focus:ring-amber-500/20 cursor-pointer"
                  >
                    <option value="ALL">All Delivery Statuses</option>
                    {uniqueStatuses.map((st) => (
                      <option key={st} value={st}>
                        {st}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Category Filter */}
                <div className="sm:col-span-3">
                  <select
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                    className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3 py-2 text-xs font-semibold text-stone-700 focus:outline-hidden focus:ring-2 focus:ring-amber-500/20 cursor-pointer"
                  >
                    <option value="ALL">All Categories</option>
                    {uniqueCategories.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Feature Cards / Dense Grid */}
            <div className="divide-y divide-stone-100">
              {filteredFeatures.length === 0 ? (
                <div className="p-12 text-center text-stone-500 text-xs">
                  No features match your active search and filter criteria.
                </div>
              ) : (
                filteredFeatures.map((feat) => (
                  <div
                    key={feat.req_id}
                    className="p-5 hover:bg-stone-50/70 transition-colors flex flex-col lg:flex-row lg:items-center justify-between gap-4"
                  >
                    {/* Feature Details */}
                    <div className="space-y-1.5 flex-1 max-w-4xl">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-mono text-xs font-black text-amber-900 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                          {feat.req_id}
                        </span>
                        <h4 className="text-sm font-bold text-stone-900">
                          {feat.feature_name}
                        </h4>
                        <span
                          className={`text-[11px] font-semibold px-2 py-0.2 rounded-full border ${
                            feat.category === "Functional"
                              ? "bg-blue-50 text-blue-700 border-blue-200"
                              : "bg-purple-50 text-purple-700 border-purple-200"
                          }`}
                        >
                          {feat.category} {feat.nfr_area ? `· ${feat.nfr_area}` : ""}
                        </span>
                        <span className="text-[11px] font-medium text-stone-500 bg-stone-100 px-2 py-0.2 rounded border border-stone-200">
                          Priority: {feat.priority}
                        </span>
                        {feat.owner && (
                          <span className="text-[11px] font-medium text-stone-600 bg-stone-50 px-2 py-0.2 rounded border border-stone-200 truncate max-w-[200px]">
                            {feat.owner}
                          </span>
                        )}
                      </div>

                      <p className="text-xs text-stone-600 leading-relaxed">
                        {feat.description}
                      </p>

                      {feat.business_impact && (
                        <div className="flex items-start gap-1.5 text-xs text-emerald-800 bg-emerald-50/80 px-2.5 py-1 rounded-lg border border-emerald-200/60 w-fit mt-1">
                          <Sparkles className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                          <span>
                            <strong className="font-semibold">Business & Clinical Value:</strong> {feat.business_impact}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Financial Attribution & Status Badges */}
                    <div className="flex flex-row lg:flex-col items-end justify-between lg:justify-center gap-2 shrink-0 border-t lg:border-t-0 pt-2 lg:pt-0 border-stone-100">
                      <div className="text-right">
                        <div className="text-xs font-mono font-black text-stone-900">
                          SAR {feat.financial_impact_sar?.toLocaleString() || "0"}
                        </div>
                        <div className="text-[10px] text-stone-500 font-medium">
                          {feat.time_saved_hrs || 0} hrs saved
                        </div>
                      </div>
                      <div>{getStatusBadge(feat.status)}</div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
export default ProjectSummaryTab;
