import type { FC } from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { DomainStat } from "../types/api";

interface DomainRadarChartProps {
  data: DomainStat[];
  onSelectDomain?: (domainName: string) => void;
  selectedDomain?: string | null;
}

export const DomainRadarChart: FC<DomainRadarChartProps> = ({
  data,
  onSelectDomain,
  selectedDomain,
}) => {
  // Format data for radar
  const chartData = data.map((d) => ({
    domain: d.domain.length > 18 ? d.domain.slice(0, 16) + "..." : d.domain,
    fullName: d.domain,
    repoCount: d.repo_count,
    confidence: d.avg_confidence_pct,
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div
          className="p-3 rounded-lg border shadow-card text-xs"
          style={{
            backgroundColor: "var(--row-odd)",
            borderColor: "var(--border)",
            color: "var(--text)",
          }}
        >
          <p className="font-bold text-stone-900">{item.fullName}</p>
          <div className="mt-1.5 space-y-1">
            <p className="text-stone-700 flex justify-between gap-4">
              <span>Repositories:</span>
              <strong className="font-mono text-[#4A3426]">{item.repoCount}</strong>
            </p>
            <p className="text-stone-700 flex justify-between gap-4">
              <span>Avg Confidence:</span>
              <strong className="font-mono text-[#785F4B]">{item.confidence}%</strong>
            </p>
          </div>
          <p className="text-[10px] text-stone-500 mt-2 italic">
            Click to isolate domain
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div
      className="rounded-xl border p-5 shadow-card flex flex-col justify-between"
      style={{
        backgroundColor: "var(--row-odd)",
        borderColor: "var(--border)",
      }}
    >
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-stone-800">
            Domain Coverage Radar
          </h3>
          <p className="text-xs text-stone-600">
            Portfolio distribution across healthcare domains
          </p>
        </div>
        {selectedDomain && (
          <span
            className="text-[11px] font-semibold px-2 py-0.5 rounded-full border"
            style={{
              backgroundColor: "var(--highlight)",
              borderColor: "var(--border)",
            }}
          >
            {selectedDomain}
          </span>
        )}
      </div>

      <div className="w-full h-72">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="75%" data={chartData}>
            <PolarGrid stroke="#785F4B" strokeOpacity={0.25} />
            <PolarAngleAxis
              dataKey="domain"
              tick={{ fill: "#1E140F", fontSize: 11, fontWeight: 500 }}
            />
            <PolarRadiusAxis
              angle={30}
              domain={[0, "auto"]}
              tick={{ fill: "#785F4B", fontSize: 10 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Radar
              name="Repositories"
              dataKey="repoCount"
              stroke="#4A3426"
              strokeWidth={2}
              fill="#ECDDC8"
              fillOpacity={0.65}
              onClick={(e: any) => onSelectDomain?.(e.fullName)}
              cursor="pointer"
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      <p className="text-[11px] text-center text-stone-500 mt-1">
        Displays repository density normalized across the clinical sectors
      </p>
    </div>
  );
};

export default DomainRadarChart;

