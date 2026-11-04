import type { FC } from "react";

// Generic domain shape accepted by filter bar — works with both mock & live API data
export interface FilterDomain {
  id: string;
  name: string;
  description: string;
  standards: string[];
  tokenCount: number;
  coveragePercentage: number;
  repoCount?: number;
}

interface DomainFilterBarProps {
  domains: FilterDomain[];
  selectedDomainId: string | null;
  onSelectDomain: (domainId: string | null) => void;
}

export const DomainFilterBar: FC<DomainFilterBarProps> = ({
  domains,
  selectedDomainId,
  onSelectDomain,
}) => {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <label className="text-xs font-bold uppercase tracking-wider text-stone-700">
          Domain Scope Filter ({domains.length} Operational Domains)
        </label>
        {selectedDomainId && (
          <button
            onClick={() => onSelectDomain(null)}
            className="text-xs underline font-semibold text-stone-700 hover:text-stone-900"
          >
            Clear Filter
          </button>
        )}
      </div>

      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {/* All Domains Pill */}
        <button
          onClick={() => onSelectDomain(null)}
          className="whitespace-nowrap px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all duration-150 flex items-center gap-1.5 shrink-0"
          style={{
            backgroundColor: selectedDomainId === null ? "var(--header-bg)" : "var(--row-odd)",
            color: selectedDomainId === null ? "var(--header-text)" : "var(--text)",
            borderColor: "var(--border)",
          }}
        >
          <span>All Domains</span>
          <span
            className="text-[10px] px-1.5 rounded-full font-mono"
            style={{
              backgroundColor: selectedDomainId === null ? "var(--highlight)" : "var(--row-even)",
              color: "var(--text)",
            }}
          >
            {domains.length}
          </span>
        </button>

        {/* Domain-Specific Pills */}
        {domains.map((domain) => {
          const isSelected = selectedDomainId === domain.id;
          return (
            <button
              key={domain.id}
              onClick={() => onSelectDomain(isSelected ? null : domain.id)}
              className="whitespace-nowrap px-3 py-1.5 rounded-lg text-xs border transition-all duration-150 flex items-center gap-1.5 shrink-0 hover:border-[#4A3426]"
              style={{
                backgroundColor: isSelected ? "var(--highlight)" : "var(--row-odd)",
                borderColor: "var(--border)",
                color: "var(--text)",
                fontWeight: isSelected ? 700 : 500,
              }}
            >
              <span>{domain.name}</span>
              {/* Show repo count from live API when available, else token count */}
              <span
                className="text-[10px] px-1.5 rounded-full font-mono border"
                style={{ backgroundColor: "var(--row-even)", borderColor: "var(--border)" }}
              >
                {domain.repoCount ?? domain.tokenCount}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
