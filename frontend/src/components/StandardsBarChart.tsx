import type { FC } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { StandardFrequency } from "../types/api";

interface StandardsBarChartProps {
  data: StandardFrequency[];
  onSelectStandard?: (standardName: string) => void;
  selectedStandards?: string[];
}

export const StandardsBarChart: FC<StandardsBarChartProps> = ({
  data,
  onSelectStandard,
  selectedStandards = [],
}) => {
  const topStandards = data.slice(0, 10);

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
          <p className="font-bold text-stone-900">{item.name}</p>
          <p className="text-stone-700 mt-1">
            Detected across{" "}
            <strong className="font-mono text-[#4A3426]">{item.count}</strong>{" "}
            repositories
          </p>
          <p className="text-[10px] text-stone-500 mt-1.5 italic">
            Click to toggle standard filter
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
            Standards & Token Density
          </h3>
          <p className="text-xs text-stone-600">
            Top clinical standards & protocol matches detected
          </p>
        </div>
        {selectedStandards.length > 0 && (
          <span
            className="text-[11px] font-semibold px-2 py-0.5 rounded-full border"
            style={{
              backgroundColor: "var(--highlight)",
              borderColor: "var(--border)",
            }}
          >
            {selectedStandards.length} Filtered
          </span>
        )}
      </div>

      <div className="w-full h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={topStandards}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              horizontal={true}
              vertical={false}
              stroke="#785F4B"
              strokeOpacity={0.15}
            />
            <XAxis
              type="number"
              tick={{ fill: "#785F4B", fontSize: 11 }}
              axisLine={{ stroke: "#785F4B", strokeOpacity: 0.3 }}
            />
            <YAxis
              dataKey="name"
              type="category"
              tick={{ fill: "#1E140F", fontSize: 11, fontWeight: 600 }}
              axisLine={{ stroke: "#785F4B", strokeOpacity: 0.3 }}
              width={75}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey="count"
              radius={[0, 4, 4, 0]}
              cursor="pointer"
              onClick={(e: any) => onSelectStandard?.(e.name)}
            >
              {topStandards.map((entry) => {
                const isSelected = selectedStandards.includes(entry.name);
                return (
                  <Cell
                    key={`cell-${entry.name}`}
                    fill={isSelected ? "#4A3426" : "#785F4B"}
                    stroke={isSelected ? "#1E140F" : undefined}
                    strokeWidth={isSelected ? 2 : 0}
                  />
                );
              })}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="text-[11px] text-center text-stone-500 mt-1">
        Click any standard bar to cross-filter the repository matrix
      </p>
    </div>
  );
};

export default StandardsBarChart;

