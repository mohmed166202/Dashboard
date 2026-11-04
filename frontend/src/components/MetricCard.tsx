import type { FC } from "react";
import { TrendingUp, Layers, Hash, PieChart, Shield } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle: string;
  badge?: string;
  trend?: string;
  icon: "domains" | "tokens" | "coverage" | "repos";
}

export const MetricCard: FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  badge,
  trend,
  icon,
}) => {
  const getIcon = () => {
    switch (icon) {
      case "domains":
        return <Layers className="w-5 h-5 text-[#4A3426]" />;
      case "tokens":
        return <Hash className="w-5 h-5 text-[#4A3426]" />;
      case "coverage":
        return <PieChart className="w-5 h-5 text-[#4A3426]" />;
      case "repos":
        return <Shield className="w-5 h-5 text-[#4A3426]" />;
    }
  };

  return (
    <div
      className="rounded-xl p-5 border shadow-subtle hover:shadow-card transition-all duration-200 relative overflow-hidden"
      style={{
        backgroundColor: "var(--row-odd)",
        borderColor: "var(--border)",
        color: "var(--text)",
      }}
    >
      {/* Accent corner banner */}
      <div
        className="absolute top-0 right-0 w-24 h-24 -mr-8 -mt-8 rounded-full opacity-30 pointer-events-none"
        style={{ backgroundColor: "var(--highlight)" }}
      />

      <div className="flex items-start justify-between">
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center border shadow-xs"
          style={{
            backgroundColor: "var(--row-even)",
            borderColor: "var(--border)",
          }}
        >
          {getIcon()}
        </div>

        {badge && (
          <span
            className="text-[11px] font-semibold px-2 py-0.5 rounded-full border"
            style={{
              backgroundColor: "var(--highlight)",
              borderColor: "var(--border)",
              color: "var(--text)",
            }}
          >
            {badge}
          </span>
        )}
      </div>

      <div className="mt-4">
        <p className="text-xs font-semibold uppercase tracking-wider text-stone-600">
          {title}
        </p>
        <div className="flex items-baseline gap-2 mt-1">
          <span className="text-2xl font-extrabold tracking-tight" style={{ color: "var(--text)" }}>
            {value}
          </span>
          {trend && (
            <div className="flex items-center text-xs font-semibold text-emerald-700">
              <TrendingUp className="w-3.5 h-3.5 mr-0.5" />
              <span>{trend}</span>
            </div>
          )}
        </div>
        <p className="text-xs text-stone-600 mt-1">{subtitle}</p>
      </div>
    </div>
  );
};

