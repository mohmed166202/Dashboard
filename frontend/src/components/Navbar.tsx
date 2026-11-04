import type { FC, ReactNode } from "react";
import { Activity, GitBranch, RefreshCw, ShieldCheck } from "lucide-react";

interface NavbarProps {
  onRefresh?: () => void;
  isRefreshing?: boolean;
  statusBadge?: ReactNode;
}

export const Navbar: FC<NavbarProps> = ({ onRefresh, isRefreshing = false, statusBadge }) => {
  return (
    <header
      className="sticky top-0 z-50 w-full px-6 py-3.5 shadow-md border-b"
      style={{
        backgroundColor: "var(--header-bg)",
        borderColor: "var(--border)",
        color: "var(--header-text)",
      }}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand & Project Identity */}
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-white/10 border border-white/20 backdrop-blur-sm shadow-inner">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-white leading-tight">
                Andalusia Healthcare Portfolio
              </h1>
              <span
                className="text-[11px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider text-stone-900 border"
                style={{
                  backgroundColor: "var(--highlight)",
                  borderColor: "var(--border)",
                }}
              >
                V2 Matrix
              </span>
            </div>
            <p className="text-xs text-white/70">
              Taxonomy Mapping & Multi-Domain Classifier Engine
            </p>
          </div>
        </div>

        {/* Global Controls & Status */}
        <div className="flex items-center gap-2.5">
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-md bg-white/10 text-xs font-medium text-white/85 border border-white/15">
            <ShieldCheck className="w-4 h-4 text-emerald-300" />
            <span>GAHAR / JCI Compliant</span>
          </div>

          <div className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-white/10 text-xs font-mono text-white/85 border border-white/15">
            <GitBranch className="w-3.5 h-3.5 text-amber-200" />
            <span>branch: main</span>
          </div>

          {/* Live API Status Badge injected from ApiStatusBadge */}
          {statusBadge}

          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-white/15 hover:bg-white/25 active:bg-white/30 text-white transition-all border border-white/20 shadow-sm disabled:opacity-50"
            title="Invalidate cache & refresh all data"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin text-amber-200" : ""}`}
            />
            <span>{isRefreshing ? "Syncing..." : "Sync Matrix"}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
