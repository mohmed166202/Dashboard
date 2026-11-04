import { useState, useMemo, useRef, useCallback } from "react";
import type { FC } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  createColumnHelper,
  flexRender,
} from "@tanstack/react-table";
import type { SortingState, ColumnDef } from "@tanstack/react-table";
import { useVirtualizer } from "@tanstack/react-virtual";
import type { Repository } from "../types/api";
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Download,
  ExternalLink,
  Code2,
  SlidersHorizontal,
  FileSpreadsheet,
  Eye,
} from "lucide-react";
import { exportToCSV, exportToJSON } from "../utils/exportUtils";

interface VirtualizedMatrixTableProps {
  data: Repository[];
  isLoading?: boolean;
  onSelectStandard?: (standard: string) => void;
  onSelectRepository?: (repo: Repository) => void;
}

const columnHelper = createColumnHelper<Repository>();

export const VirtualizedMatrixTable: FC<VirtualizedMatrixTableProps> = ({
  data,
  isLoading = false,
  onSelectStandard,
  onSelectRepository,
}) => {
  const [sorting, setSorting] = useState<SortingState>([
    { id: "confidence_score", desc: true },
  ]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [useRegex, setUseRegex] = useState(false);
  const [regexError, setRegexError] = useState<string | null>(null);

  // Custom filter logic supporting standard text & safe Regex matching
  const customGlobalFilterFn = useMemo(() => {
    return (row: any, _columnId: string, filterValue: string) => {
      if (!filterValue) return true;
      const repo: Repository = row.original;
      const searchTargets = [
        repo.name,
        repo.description || "",
        repo.primary_domain || "",
        repo.secondary_domains.join(" "),
        repo.detected_standards.join(" "),
        repo.primary_language || "",
        repo.project_status || "",
        repo.domain_justification || "",
      ].join(" ");

      if (useRegex) {
        try {
          const reg = new RegExp(filterValue, "i");
          return reg.test(searchTargets);
        } catch {
          return true;
        }
      } else {
        return searchTargets.toLowerCase().includes(filterValue.toLowerCase());
      }
    };
  }, [useRegex]);

  // Validate Regex on input change
  const handleFilterChange = (val: string) => {
    setGlobalFilter(val);
    if (useRegex && val) {
      try {
        new RegExp(val, "i");
        setRegexError(null);
      } catch (err: any) {
        setRegexError(err.message);
      }
    } else {
      setRegexError(null);
    }
  };

  // Define table columns
  const columns = useMemo<ColumnDef<Repository, any>[]>(
    () => [
      columnHelper.accessor("name", {
        header: "Repository Name",
        size: 260,
        cell: (info) => {
          const repo = info.row.original;
          return (
            <div className="flex flex-col py-1">
              <div className="flex items-center gap-1.5 font-bold text-stone-900 group">
                <button
                  type="button"
                  onClick={() => onSelectRepository?.(repo)}
                  className="truncate text-left hover:underline hover:text-[#4A3426] flex items-center gap-1"
                >
                  <span>{info.getValue()}</span>
                  <Eye className="w-3 h-3 text-stone-400 group-hover:text-[#4A3426] opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                </button>
                {repo.url && (
                  <a
                    href={repo.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-stone-400 hover:text-stone-700 inline-flex items-center shrink-0 ml-1"
                    title="View GitHub Repository"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
              {repo.description && (
                <span className="text-xs text-stone-600 line-clamp-1 truncate max-w-xs mt-0.5">
                  {repo.description}
                </span>
              )}
            </div>
          );
        },
      }),

      columnHelper.accessor("primary_domain", {
        header: "Primary Domain",
        size: 190,
        cell: (info) => {
          const val = info.getValue() || "Unclassified";
          return (
            <span
              className="inline-block text-xs font-semibold px-2.5 py-1 rounded-md border text-stone-900 shadow-xs"
              style={{
                backgroundColor: "var(--row-even)",
                borderColor: "var(--border)",
              }}
            >
              {val}
            </span>
          );
        },
      }),

      // TARGET V2 COLUMN: Styled with custom --highlight token (#ECDDC8)
      columnHelper.accessor("confidence_score", {
        id: "confidence_score",
        header: "V2 Confidence",
        size: 140,
        cell: (info) => {
          const score = info.getValue();
          const pct = score !== null ? Math.round(score * 100) : 0;
          return (
            <div
              className="h-full w-full py-1.5 px-3 rounded-md font-mono font-bold text-xs flex items-center justify-between border"
              style={{
                backgroundColor: "var(--highlight)",
                borderColor: "var(--border)",
                color: "var(--text)",
              }}
            >
              <span>{pct}%</span>
              <span className="text-[10px] font-sans px-1.5 py-0.2 rounded bg-white/70 border border-stone-400">
                V2 Match
              </span>
            </div>
          );
        },
      }),

      columnHelper.accessor("detected_standards", {
        header: "Standards & Frameworks",
        size: 200,
        enableSorting: false,
        cell: (info) => {
          const standards: string[] = info.getValue() || [];
          if (!standards || standards.length === 0) {
            return <span className="text-stone-400 text-xs italic">—</span>;
          }
          return (
            <div className="flex flex-wrap gap-1">
              {standards.map((std) => (
                <button
                  key={std}
                  type="button"
                  onClick={() => onSelectStandard?.(std)}
                  className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-white border border-stone-300 text-stone-800 hover:border-stone-800 transition-colors shadow-xs"
                  title={`Filter by ${std}`}
                >
                  {std}
                </button>
              ))}
            </div>
          );
        },
      }),

      columnHelper.accessor("primary_language", {
        header: "Tech Stack",
        size: 130,
        cell: (info) => {
          const lang = info.getValue();
          if (!lang) return <span className="text-stone-400 text-xs">—</span>;
          return (
            <div className="flex items-center gap-1 text-xs font-mono text-stone-700">
              <Code2 className="w-3.5 h-3.5 text-stone-500" />
              <span>{lang}</span>
            </div>
          );
        },
      }),

      columnHelper.accessor("project_status", {
        header: "Status",
        size: 160,
        cell: (info) => {
          const status = info.getValue() || "Active";
          return (
            <span className="text-xs text-stone-700 font-medium">
              {status}
            </span>
          );
        },
      }),
    ],
    [onSelectStandard, onSelectRepository]
  );

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    globalFilterFn: customGlobalFilterFn,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  const { rows } = table.getRowModel();

  // Virtualization container ref
  const tableContainerRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => tableContainerRef.current,
    estimateSize: () => 56,
    overscan: 8,
  });

  const virtualRows = rowVirtualizer.getVirtualItems();
  const totalSize = rowVirtualizer.getTotalSize();

  const paddingTop = virtualRows.length > 0 ? virtualRows[0]?.start || 0 : 0;
  const paddingBottom =
    virtualRows.length > 0
      ? totalSize - (virtualRows[virtualRows.length - 1]?.end || 0)
      : 0;

  // Handlers for exporting data
  const handleExportCSV = () => {
    const exportData = rows.map((r) => r.original);
    exportToCSV(exportData, `andalusia_healthcare_matrix_${Date.now()}`);
  };

  const handleExportJSON = () => {
    const exportData = rows.map((r) => r.original);
    exportToJSON(exportData, `andalusia_healthcare_matrix_${Date.now()}`);
  };

  return (
    <div
      className="rounded-xl border shadow-card overflow-hidden"
      style={{
        backgroundColor: "var(--row-odd)",
        borderColor: "var(--border)",
      }}
    >
      {/* Table Toolbar */}
      <div
        className="px-5 py-3.5 border-b flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between"
        style={{
          backgroundColor: "var(--row-even)",
          borderColor: "var(--border)",
        }}
      >
        <div className="flex items-center gap-3 flex-1">
          <div className="relative flex-1 max-w-md">
            <input
              type="text"
              value={globalFilter}
              onChange={(e) => handleFilterChange(e.target.value)}
              placeholder={
                useRegex
                  ? "Regex Search (e.g. ^(his|emr).*fhir)"
                  : "Filter matrix by keyword, domain, standard..."
              }
              className={`w-full px-3.5 py-1.5 rounded-lg text-xs border bg-white focus:outline-none focus:ring-2 focus:ring-[#785F4B] transition-all font-mono ${
                regexError ? "border-red-500 text-red-900 bg-red-50" : ""
              }`}
              style={{
                borderColor: regexError ? "#EF4444" : "var(--border)",
                color: "var(--text)",
              }}
            />
            {regexError && (
              <span className="absolute -bottom-4 left-1 text-[10px] text-red-600 font-sans">
                {regexError}
              </span>
            )}
          </div>

          {/* Toggle Regex Mode */}
          <button
            type="button"
            onClick={() => setUseRegex(!useRegex)}
            className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold border flex items-center gap-1.5 transition-all shadow-xs ${
              useRegex
                ? "bg-[#4A3426] text-white border-[#4A3426]"
                : "bg-white text-stone-700 hover:bg-stone-50"
            }`}
            style={{
              borderColor: useRegex ? "#4A3426" : "var(--border)",
            }}
            title="Toggle regular expression search"
          >
            <SlidersHorizontal className="w-3 h-3" />
            <span>Regex Mode</span>
          </button>
        </div>

        {/* Counter & Export Controls */}
        <div className="flex items-center gap-2 self-end md:self-auto">
          <span className="text-xs font-semibold text-stone-600 mr-2">
            Showing <strong className="text-stone-900">{rows.length}</strong> of{" "}
            {data.length} records
          </span>

          <button
            type="button"
            onClick={handleExportCSV}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold border bg-white hover:bg-stone-50 text-stone-800 transition-colors flex items-center gap-1.5 shadow-xs"
            style={{ borderColor: "var(--border)" }}
            title="Download CSV spreadsheet"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-700" />
            <span>CSV</span>
          </button>

          <button
            type="button"
            onClick={handleExportJSON}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold border bg-white hover:bg-stone-50 text-stone-800 transition-colors flex items-center gap-1.5 shadow-xs"
            style={{ borderColor: "var(--border)" }}
            title="Download raw JSON"
          >
            <Download className="w-3.5 h-3.5 text-stone-600" />
            <span>JSON</span>
          </button>
        </div>
      </div>

      {/* High-Performance Virtual Scroll Container with CSS Containment */}
      <div
        ref={tableContainerRef}
        className="max-h-[580px] overflow-auto relative scrollbar-thin virtual-table-container"
        style={{ scrollBehavior: "smooth" }}
      >
        <table className="w-full text-left border-collapse table-fixed">
          {/* Sticky Header with --header-bg */}
          <thead
            className="sticky top-0 z-20 shadow-xs"
            style={{
              backgroundColor: "var(--header-bg)",
              color: "var(--header-text)",
            }}
          >
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  const isV2 = header.column.id === "confidence_score";
                  const canSort = header.column.getCanSort();
                  const isSorted = header.column.getIsSorted();

                  return (
                    <th
                      key={header.id}
                      style={{
                        width: header.getSize(),
                        backgroundColor: isV2 ? "var(--highlight)" : undefined,
                        color: isV2 ? "var(--text)" : "var(--header-text)",
                      }}
                      className={`px-4 py-3.5 text-xs font-bold uppercase tracking-wider select-none border-b border-stone-700/30 ${
                        canSort ? "cursor-pointer hover:bg-black/15" : ""
                      }`}
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      <div className="flex items-center justify-between gap-1">
                        <span>
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                        </span>
                        {canSort && (
                          <span className="shrink-0">
                            {isSorted === "asc" ? (
                              <ArrowUp className="w-3.5 h-3.5 text-amber-300" />
                            ) : isSorted === "desc" ? (
                              <ArrowDown className="w-3.5 h-3.5 text-amber-300" />
                            ) : (
                              <ArrowUpDown className="w-3 h-3 opacity-40" />
                            )}
                          </span>
                        )}
                      </div>
                    </th>
                  );
                })}
              </tr>
            ))}
          </thead>

          {/* Virtual Body with Alternating Rows */}
          <tbody>
            {paddingTop > 0 && (
              <tr>
                <td style={{ height: `${paddingTop}px` }} />
              </tr>
            )}

            {virtualRows.map((virtualRow) => {
              const row = rows[virtualRow.index];
              const isEven = virtualRow.index % 2 === 1;

              return (
                <tr
                  key={row.id}
                  data-index={virtualRow.index}
                  ref={rowVirtualizer.measureElement}
                  className="border-b transition-colors duration-100 hover:bg-[#ECDDC8]/25"
                  style={{
                    backgroundColor: isEven
                      ? "var(--row-even)"
                      : "var(--row-odd)",
                    borderColor: "var(--border)",
                  }}
                >
                  {row.getVisibleCells().map((cell) => {
                    const isV2 = cell.column.id === "confidence_score";
                    return (
                      <td
                        key={cell.id}
                        className="px-4 py-2.5 text-xs align-middle"
                        style={{
                          backgroundColor: isV2 ? "rgba(236, 221, 200, 0.45)" : undefined,
                        }}
                      >
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </td>
                    );
                  })}
                </tr>
              );
            })}

            {paddingBottom > 0 && (
              <tr>
                <td style={{ height: `${paddingBottom}px` }} />
              </tr>
            )}

            {rows.length === 0 && !isLoading && (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-6 py-12 text-center text-stone-500 text-sm"
                >
                  No records match the current filter or search criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
