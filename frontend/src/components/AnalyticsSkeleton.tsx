/**
 * AnalyticsSkeleton.tsx
 * ───────────────────────────────────────────────────────────────────────────
 * Pulsing shimmer placeholder shown while Recharts components lazy-load.
 * Matches the exact layout of the analytics tab (2-col top + full heatmap)
 * to prevent cumulative layout shift (CLS = 0).
 */

import type { FC } from "react";

const ShimmerBlock: FC<{ className?: string }> = ({ className = "" }) => (
  <div
    className={`animate-pulse rounded-xl border ${className}`}
    style={{
      backgroundColor: "var(--row-even)",
      borderColor: "var(--border)",
    }}
  />
);

const ChartCardSkeleton: FC = () => (
  <div
    className="rounded-xl border p-5 space-y-4"
    style={{
      backgroundColor: "var(--row-odd)",
      borderColor: "var(--border)",
    }}
  >
    {/* Header line */}
    <div className="flex items-center justify-between">
      <div className="space-y-2">
        <ShimmerBlock className="h-3.5 w-40 border-0" />
        <ShimmerBlock className="h-2.5 w-56 border-0" />
      </div>
    </div>
    {/* Chart area */}
    <ShimmerBlock className="w-full h-64 border-0" />
    {/* Footer line */}
    <ShimmerBlock className="h-2 w-48 mx-auto border-0" />
  </div>
);

const HeatmapSkeleton: FC = () => (
  <div
    className="rounded-xl border p-5 space-y-4"
    style={{
      backgroundColor: "var(--row-odd)",
      borderColor: "var(--border)",
    }}
  >
    {/* Header */}
    <div className="flex items-center justify-between">
      <div className="space-y-2">
        <ShimmerBlock className="h-3.5 w-64 border-0" />
        <ShimmerBlock className="h-2.5 w-80 border-0" />
      </div>
      <div className="flex gap-2">
        <ShimmerBlock className="h-4 w-10 rounded-full border-0" />
        <ShimmerBlock className="h-4 w-10 rounded-full border-0" />
        <ShimmerBlock className="h-4 w-10 rounded-full border-0" />
      </div>
    </div>
    {/* Grid shimmer — 9 rows × 10 cols approximation */}
    <div className="overflow-hidden space-y-1.5">
      {Array.from({ length: 9 }).map((_, r) => (
        <div key={r} className="flex gap-1.5">
          <ShimmerBlock className="h-7 w-32 shrink-0 border-0" />
          {Array.from({ length: 9 }).map((_, c) => (
            <ShimmerBlock key={c} className="h-7 flex-1 border-0" />
          ))}
        </div>
      ))}
    </div>
    {/* Footer */}
    <ShimmerBlock className="h-2 w-96 mx-auto border-0" />
  </div>
);

export const AnalyticsSkeleton: FC = () => (
  <section className="space-y-6" aria-label="Loading analytics…">
    {/* Top 2-col row */}
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ChartCardSkeleton />
      <ChartCardSkeleton />
    </div>
    {/* Full-width heatmap */}
    <HeatmapSkeleton />
  </section>
);

