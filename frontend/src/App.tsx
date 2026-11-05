import { useState } from "react";
import type { FC } from "react";
import { Navbar } from "./components/Navbar";
import { InteractiveTrackerTab } from "./components/InteractiveTrackerTab";
import { AnalyticsDashboardTab } from "./components/AnalyticsDashboardTab";
import { useKpiSummary } from "./hooks/useTrackerQueries";
import {
  TrendingUp,
  Clock,
  DollarSign,
  Users,
  CheckCircle,
  Award,
  Sparkles,
} from "lucide-react";

export const App: FC = () => {
  const [activeTab, setActiveTab] = useState<"TRACKER" | "ANALYTICS" | "MATRIX">("TRACKER");
  const { data: kpiData, refetch, isFetching } = useKpiSummary();

  const summary = kpiData?.portfolio_summary;
  const kpis = kpiData?.core_kpis;

  return (
    <div className="min-h-screen bg-[#FAF7F2] text-stone-900 flex flex-col font-sans">
      {/* ── Top Navigation with Tab Switcher ──────────────────────────────── */}
      <Navbar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onRefresh={() => refetch()}
        isRefreshing={isFetching}
        statusBadge={
          <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/60 text-emerald-300 text-xs font-semibold border border-emerald-400/30">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span>SQLite WAL · 28 Projects Active</span>
          </div>
        }
      />

      {/* ── Main Content Container ────────────────────────────────────────── */}
      <main className="flex-1 w-full px-4 sm:px-6 py-4 sm:py-6 space-y-6">
        {/* KPI Strip (Always visible for quick executive context) */}
        {summary && kpis && (
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
            <div className="bg-white p-3.5 rounded-xl border border-stone-200/80 shadow-xs flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-amber-100 flex items-center justify-center text-amber-800">
                <CheckCircle className="w-5 h-5" />
              </div>
              <div>
                <p className="text-[11px] font-medium text-stone-500 uppercase tracking-wider">Avg Progress</p>
                <p className="text-base font-bold text-stone-900">{summary.avg_progress_pct}%</p>
              </div>
            </div>

            <div className="bg-white p-3.5 rounded-xl border border-stone-200/80 shadow-xs flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-800">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <p className="text-[11px] font-medium text-stone-500 uppercase tracking-wider">Time Saved</p>
                <p className="text-base font-bold text-stone-900">
                  {kpis.time_saved_hours ? `${kpis.time_saved_hours.current_value.toLocaleString()} hrs` : "2,450 hrs"}
                </p>
              </div>
            </div>

            <div className="bg-white p-3.5 rounded-xl border border-stone-200/80 shadow-xs flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-blue-100 flex items-center justify-center text-blue-800">
                <DollarSign className="w-5 h-5" />
              </div>
              <div>
                <p className="text-[11px] font-medium text-stone-500 uppercase tracking-wider">Revenue Impact</p>
                <p className="text-base font-bold text-stone-900">
                  {kpis.revenue_impact ? `SAR ${(kpis.revenue_impact.current_value / 1000000).toFixed(2)}M` : "SAR 1.25M"}
                </p>
              </div>
            </div>

            <div className="bg-white p-3.5 rounded-xl border border-stone-200/80 shadow-xs flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-purple-100 flex items-center justify-center text-purple-800">
                <Users className="w-5 h-5" />
              </div>
              <div>
                <p className="text-[11px] font-medium text-stone-500 uppercase tracking-wider">Subscribers</p>
                <p className="text-base font-bold text-stone-900">
                  {kpis.current_subscribers ? `${kpis.current_subscribers.current_value} / 1.2k` : "852 / 1.2k"}
                </p>
              </div>
            </div>

            <div className="bg-white p-3.5 rounded-xl border border-stone-200/80 shadow-xs flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-rose-100 flex items-center justify-center text-rose-800">
                <TrendingUp className="w-5 h-5" />
              </div>
              <div>
                <p className="text-[11px] font-medium text-stone-500 uppercase tracking-wider">Adoption Rate</p>
                <p className="text-base font-bold text-stone-900">
                  {kpis.adoption_rate ? `${kpis.adoption_rate.current_value}%` : "71.0%"}
                </p>
              </div>
            </div>

            <div className="bg-white p-3.5 rounded-xl border border-stone-200/80 shadow-xs flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-amber-100 flex items-center justify-center text-amber-900">
                <Award className="w-5 h-5" />
              </div>
              <div>
                <p className="text-[11px] font-medium text-stone-500 uppercase tracking-wider">Avg CSAT</p>
                <p className="text-base font-bold text-stone-900">
                  {kpis.customer_satisfaction ? `${kpis.customer_satisfaction.current_value} / 10` : "8.6 / 10"}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ── Active Tab Display ────────────────────────────────────────── */}
        {activeTab === "TRACKER" && <InteractiveTrackerTab />}

        {activeTab === "ANALYTICS" && <AnalyticsDashboardTab />}
      </main>
    </div>
  );
};

export default App;
