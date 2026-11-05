import type { FC, ReactNode } from "react";
import { Activity, RefreshCw, LayoutGrid, BarChart2, ShieldCheck } from "lucide-react";

interface NavbarProps {
  onRefresh?: () => void;
  isRefreshing?: boolean;
  statusBadge?: ReactNode;
  activeTab?: "TRACKER" | "ANALYTICS" | "MATRIX";
  onTabChange?: (tab: "TRACKER" | "ANALYTICS" | "MATRIX") => void;
}

export const Navbar: FC<NavbarProps> = ({
  onRefresh,
  isRefreshing = false,
  statusBadge,
  activeTab = "TRACKER",
  onTabChange,
}) => {
  return (
    <header
      className="sticky top-0 z-50 w-full px-6 py-3 shadow-md border-b bg-[#4A3426] text-amber-50"
    >
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        {/* Brand & Project Identity */}
        <div className="flex items-center gap-3.5">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center bg-white/10 border border-white/20 backdrop-blur-sm shadow-inner">
            <Activity className="w-5 h-5 text-amber-300" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold tracking-tight text-white leading-tight">
                Andalusia AI Portfolio & Governance
              </h1>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider bg-amber-400 text-stone-900">
                Live System
              </span>
            </div>
            <p className="text-[11px] text-amber-200/70">
              Interactive Project Tracker, Requirements & Clinical Benchmarks
            </p>
          </div>
        </div>

        {/* Navigation Tabs Switcher */}
        {onTabChange && (
          <nav className="flex items-center gap-1 bg-stone-900/40 p-1 rounded-xl border border-white/10 text-xs">
            <button
              onClick={() => onTabChange("TRACKER")}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg font-bold transition-all ${
                activeTab === "TRACKER"
                  ? "bg-amber-100 text-amber-950 shadow-sm"
                  : "text-amber-100/80 hover:text-white hover:bg-white/5"
              }`}
            >
              <LayoutGrid className="w-3.5 h-3.5" />
              Tab 1: Project Tracker
            </button>

            <button
              onClick={() => onTabChange("ANALYTICS")}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg font-bold transition-all ${
                activeTab === "ANALYTICS"
                  ? "bg-amber-100 text-amber-950 shadow-sm"
                  : "text-amber-100/80 hover:text-white hover:bg-white/5"
              }`}
            >
              <BarChart2 className="w-3.5 h-3.5" />
              Tab 2: Analytics & Benchmarks
            </button>
          </nav>
        )}

        {/* Global Controls & Status */}
        <div className="flex items-center gap-2.5">
          {statusBadge}

          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white/10 hover:bg-white/20 text-white border border-white/15 transition-all disabled:opacity-50"
              title="Refresh Portfolio"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin" : ""}`} />
              <span className="hidden sm:inline">Refresh</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
