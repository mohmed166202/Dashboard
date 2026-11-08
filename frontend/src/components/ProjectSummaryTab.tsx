import React from "react";
import { Briefcase, ArrowRight, Layers, Sparkles, Target, Award, CheckCircle2 } from "lucide-react";

interface ProjectSummaryPlaceholderProps {
  onNavigateToTracker?: () => void;
  onNavigateToAnalytics?: () => void;
}

export const ProjectSummaryTab: React.FC<ProjectSummaryPlaceholderProps> = ({
  onNavigateToTracker,
  onNavigateToAnalytics,
}) => {
  return (
    <div className="space-y-6">
      {/* ── Welcome & Status Hero ────────────────────────────────────────── */}
      <div className="bg-gradient-to-r from-[#4A3426] via-[#5c4030] to-[#3a281e] text-amber-50 rounded-2xl p-6 sm:p-8 shadow-md border border-amber-900/30">
        <div className="max-w-4xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-400/20 text-amber-300 text-xs font-bold border border-amber-400/30 mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Executive Portfolio Overview · Live System</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white mb-2">
            Andalusia AI Strategic Portfolio Summary
          </h2>
          <p className="text-amber-100/80 text-sm leading-relaxed mb-6">
            Executive view consolidating 28 clinical, operational, and financial AI initiatives across all hospital clusters.
            Track strategic deliverables, financial return on investment (ROI), clinician adoption rates, and HIMSS/KLAS performance benchmarks.
          </p>

          <div className="flex flex-wrap items-center gap-3">
            {onNavigateToTracker && (
              <button
                onClick={onNavigateToTracker}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-400 hover:bg-amber-300 text-stone-900 font-bold text-xs shadow-sm transition-all"
              >
                <span>Open Project Delivery Matrix</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
            {onNavigateToAnalytics && (
              <button
                onClick={onNavigateToAnalytics}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs border border-white/20 transition-all"
              >
                <span>View Analytics & Performance</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Key Highlights Strip ─────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-stone-200 shadow-xs flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center shrink-0">
            <Briefcase className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-stone-900 mb-1">Executive Decision Support</h3>
            <p className="text-xs text-stone-600 leading-normal">
              High-level status tracking, scope verification, and resource allocation across active clinical informatics and generative AI deployments.
            </p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-stone-200 shadow-xs flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center shrink-0">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-stone-900 mb-1">Financial & Clinical Impact</h3>
            <p className="text-xs text-stone-600 leading-normal">
              Direct visibility into measurable physician time savings, SAR financial return on investment, and operational throughput gains.
            </p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-stone-200 shadow-xs flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-blue-100 text-blue-800 flex items-center justify-center shrink-0">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-stone-900 mb-1">Benchmarked Excellence</h3>
            <p className="text-xs text-stone-600 leading-normal">
              Continuously calibrated against international healthcare benchmarks (KLAS, HIMSS, Andalusia AI Target) for clinical accuracy and CSAT.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
