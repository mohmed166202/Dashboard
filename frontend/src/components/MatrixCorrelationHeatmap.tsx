import type { FC } from "react";
import type { Repository } from "../types/api";

interface MatrixCorrelationHeatmapProps {
  repositories: Repository[];
  domains: string[];
  onSelectDomainPair?: (primary: string, secondary: string) => void;
}

export const MatrixCorrelationHeatmap: FC<MatrixCorrelationHeatmapProps> = ({
  repositories,
  domains,
  onSelectDomainPair,
}) => {
  // Build a co-occurrence matrix between primary domains and secondary domains
  const matrix: Record<string, Record<string, number>> = {};
  domains.forEach((d1) => {
    matrix[d1] = {};
    domains.forEach((d2) => {
      matrix[d1][d2] = 0;
    });
  });

  let maxCount = 1;
  repositories.forEach((repo) => {
    const primary = repo.primary_domain;
    if (primary && matrix[primary]) {
      // Primary self-count
      matrix[primary][primary] = (matrix[primary][primary] || 0) + 1;
      if (matrix[primary][primary] > maxCount) maxCount = matrix[primary][primary];

      // Secondary overlap
      repo.secondary_domains.forEach((sec) => {
        if (matrix[primary][sec] !== undefined) {
          matrix[primary][sec] += 1;
          if (matrix[primary][sec] > maxCount) maxCount = matrix[primary][sec];
        }
      });
    }
  });

  // Color generator based on intensity
  const getCellBg = (count: number) => {
    if (count === 0) return "rgba(247, 241, 233, 0.4)"; // --row-even with opacity
    const ratio = Math.min(count / maxCount, 1);
    if (ratio < 0.2) return "#ECDDC8"; // --highlight
    if (ratio < 0.5) return "rgba(120, 95, 75, 0.5)"; // mid brown
    return "#4A3426"; // --header-bg
  };

  const getTextColor = (count: number) => {
    if (count === 0) return "text-stone-300";
    const ratio = Math.min(count / maxCount, 1);
    return ratio >= 0.5 ? "text-white" : "text-[#1E140F]";
  };

  return (
    <div
      className="rounded-xl border p-5 shadow-card"
      style={{
        backgroundColor: "var(--row-odd)",
        borderColor: "var(--border)",
      }}
    >
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-stone-800">
            Domain Co-Occurrence & Cross-Domain Heatmap
          </h3>
          <p className="text-xs text-stone-600">
            Intersection between primary classifications and secondary domain signatures
          </p>
        </div>
        <div className="flex items-center gap-2 text-[11px] font-mono text-stone-600">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded bg-[#F7F1E9] border border-stone-300 inline-block" />
            0
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded bg-[#ECDDC8] border border-stone-400 inline-block" />
            Low
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded bg-[#4A3426] inline-block" />
            High
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-center border-collapse">
          <thead>
            <tr>
              <th className="p-2 text-left text-xs font-bold text-stone-700 uppercase tracking-wider w-40">
                Primary \ Secondary
              </th>
              {domains.map((d) => (
                <th
                  key={d}
                  className="p-1.5 text-[10px] font-bold text-stone-700 tracking-tight text-center max-w-[80px] truncate"
                  title={d}
                >
                  {d.split(" ")[0]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {domains.map((primary) => (
              <tr key={primary}>
                <td className="p-2 text-left text-xs font-semibold text-stone-800 truncate max-w-[160px] border-b border-stone-200">
                  {primary}
                </td>
                {domains.map((secondary) => {
                  const count = matrix[primary]?.[secondary] || 0;
                  return (
                    <td
                      key={secondary}
                      onClick={() => onSelectDomainPair?.(primary, secondary)}
                      className={`p-2 text-xs font-mono font-bold cursor-pointer transition-transform hover:scale-110 border border-stone-200/60 ${getTextColor(
                        count
                      )}`}
                      style={{ backgroundColor: getCellBg(count) }}
                      title={`${primary} & ${secondary}: ${count} matches`}
                    >
                      {count > 0 ? count : "·"}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="text-[11px] text-center text-stone-500 mt-3">
        Diagonal cells reflect primary domain counts; off-diagonal cells represent multi-domain overlap
      </p>
    </div>
  );
};

export default MatrixCorrelationHeatmap;

