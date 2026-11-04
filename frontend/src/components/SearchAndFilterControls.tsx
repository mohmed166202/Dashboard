import { useState, useRef, useEffect } from "react";
import type { FC } from "react";
import { Search, ChevronDown, Check, X, Filter } from "lucide-react";

interface SearchAndFilterControlsProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  availableStandards: string[];
  selectedStandards: string[];
  onToggleStandard: (standard: string) => void;
  onClearStandards: () => void;
}

export const SearchAndFilterControls: FC<SearchAndFilterControlsProps> = ({
  searchQuery,
  onSearchChange,
  availableStandards,
  selectedStandards,
  onToggleStandard,
  onClearStandards,
}) => {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div
      className="p-4 rounded-xl border shadow-subtle mb-6 flex flex-col md:flex-row gap-4 items-stretch md:items-center justify-between"
      style={{
        backgroundColor: "var(--row-even)",
        borderColor: "var(--border)",
      }}
    >
      {/* Search Bar */}
      <div className="relative flex-1">
        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-500" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search by domain, token regex, clinical guideline, or repository..."
          className="w-full pl-10 pr-9 py-2 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-[#785F4B] transition-all bg-white"
          style={{
            borderColor: "var(--border)",
            color: "var(--text)",
          }}
        />
        {searchQuery && (
          <button
            onClick={() => onSearchChange("")}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-700"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Standards Multi-Select Dropdown */}
      <div className="relative" ref={dropdownRef}>
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="w-full md:w-auto flex items-center justify-between gap-2.5 px-3.5 py-2 rounded-lg text-sm font-medium border bg-white shadow-xs hover:bg-stone-50 transition-colors"
          style={{
            borderColor: "var(--border)",
            color: "var(--text)",
          }}
        >
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-stone-600" />
            <span>Standards & Frameworks</span>
            {selectedStandards.length > 0 && (
              <span
                className="text-xs font-bold px-1.5 py-0.2 rounded-full border"
                style={{
                  backgroundColor: "var(--highlight)",
                  borderColor: "var(--border)",
                }}
              >
                {selectedStandards.length}
              </span>
            )}
          </div>
          <ChevronDown
            className={`w-4 h-4 text-stone-500 transition-transform ${
              dropdownOpen ? "rotate-180" : ""
            }`}
          />
        </button>

        {/* Dropdown Menu */}
        {dropdownOpen && (
          <div
            className="absolute right-0 mt-2 w-72 rounded-xl border shadow-card z-30 p-2 max-h-80 overflow-y-auto"
            style={{
              backgroundColor: "var(--row-odd)",
              borderColor: "var(--border)",
            }}
          >
            <div className="flex items-center justify-between px-2 py-1.5 border-b border-stone-200 mb-1">
              <span className="text-xs font-bold uppercase tracking-wider text-stone-600">
                Healthcare Standards
              </span>
              {selectedStandards.length > 0 && (
                <button
                  onClick={onClearStandards}
                  className="text-xs text-stone-600 hover:text-stone-900 font-semibold"
                >
                  Clear all
                </button>
              )}
            </div>

            <div className="space-y-1 mt-1">
              {availableStandards.map((std) => {
                const isSelected = selectedStandards.includes(std);
                return (
                  <button
                    key={std}
                    onClick={() => onToggleStandard(std)}
                    className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-medium text-left transition-colors hover:bg-stone-100"
                    style={{
                      backgroundColor: isSelected
                        ? "var(--highlight)"
                        : "transparent",
                    }}
                  >
                    <span>{std}</span>
                    {isSelected && (
                      <Check className="w-4 h-4 text-[#4A3426]" />
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

