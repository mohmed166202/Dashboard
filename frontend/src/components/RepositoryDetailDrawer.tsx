import type { FC } from "react";
import type { Repository } from "../types/api";
import {
  X,
  ExternalLink,
  Code2,
  GitBranch,
  ShieldCheck,
  Calendar,
  Layers,
  FileCode,
} from "lucide-react";

interface RepositoryDetailDrawerProps {
  repository: Repository | null;
  onClose: () => void;
}

export const RepositoryDetailDrawer: FC<RepositoryDetailDrawerProps> = ({
  repository,
  onClose,
}) => {
  if (!repository) return null;

  const confidencePct = Math.round((repository.confidence_score ?? 0) * 100);

  return (
    <div className="fixed inset-0 z-50 overflow-hidden flex justify-end">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-stone-900/40 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />

      {/* Slide-over Panel */}
      <aside
        className="relative w-full max-w-xl h-full shadow-2xl flex flex-col z-10 overflow-y-auto"
        style={{
          backgroundColor: "var(--row-odd)",
          color: "var(--text)",
          borderLeft: "1px solid var(--border)",
        }}
      >
        {/* Drawer Header with --header-bg */}
        <div
          className="p-5 flex items-start justify-between border-b"
          style={{
            backgroundColor: "var(--header-bg)",
            color: "var(--header-text)",
            borderColor: "var(--border)",
          }}
        >
          <div>
            <div className="flex items-center gap-2">
              <span
                className="text-[11px] font-bold px-2 py-0.5 rounded-full border text-stone-900"
                style={{
                  backgroundColor: "var(--highlight)",
                  borderColor: "var(--border)",
                }}
              >
                {confidencePct}% V2 Match
              </span>
              <span className="text-xs text-white/70 font-mono">
                {repository.owner}
              </span>
            </div>
            <h2 className="text-lg font-bold text-white mt-1 leading-snug">
              {repository.name}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-white/10 text-white/80 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Body */}
        <div className="p-6 space-y-6 flex-1 text-sm">
          {/* Quick Links & Meta */}
          <div className="flex flex-wrap gap-2 items-center justify-between">
            {repository.url && (
              <a
                href={repository.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-white shadow-xs"
                style={{ backgroundColor: "var(--header-bg)" }}
              >
                <span>View on GitHub</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            )}

            <div className="flex items-center gap-2 text-xs text-stone-600 font-mono">
              <Calendar className="w-3.5 h-3.5" />
              <span>
                Pushed:{" "}
                {repository.pushed_at
                  ? new Date(repository.pushed_at).toLocaleDateString()
                  : "N/A"}
              </span>
            </div>
          </div>

          {/* Description */}
          {repository.description && (
            <div
              className="p-4 rounded-xl border"
              style={{
                backgroundColor: "var(--row-even)",
                borderColor: "var(--border)",
              }}
            >
              <h4 className="text-xs font-bold uppercase tracking-wider text-stone-700 mb-1">
                Project Synopsis
              </h4>
              <p className="text-stone-800 leading-relaxed text-xs">
                {repository.description}
              </p>
            </div>
          )}

          {/* Domain Classification Details */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-stone-700 flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-[#4A3426]" />
              <span>Healthcare Taxonomy Classification</span>
            </h4>

            <div
              className="p-4 rounded-xl border space-y-2.5"
              style={{
                backgroundColor: "var(--row-even)",
                borderColor: "var(--border)",
              }}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs text-stone-600">Primary Domain:</span>
                <span className="font-bold text-xs text-stone-900 px-2 py-0.5 rounded bg-white border border-stone-300">
                  {repository.primary_domain || "Unassigned"}
                </span>
              </div>

              {repository.secondary_domains.length > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-stone-600">
                    Secondary Overlap:
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {repository.secondary_domains.map((sec) => (
                      <span
                        key={sec}
                        className="text-[11px] px-2 py-0.5 rounded bg-white border border-stone-300 text-stone-800"
                      >
                        {sec}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {repository.domain_justification && (
                <div className="pt-2 border-t border-stone-300/60 mt-2">
                  <span className="text-[11px] font-semibold text-stone-600 uppercase tracking-wider">
                    Classifier Reasoning:
                  </span>
                  <p className="text-xs text-stone-700 mt-1 italic">
                    "{repository.domain_justification}"
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Detected Standards */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-stone-700 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-700" />
              <span>Detected Standards & Regulations</span>
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {repository.detected_standards.length > 0 ? (
                repository.detected_standards.map((std) => (
                  <span
                    key={std}
                    className="text-xs font-mono font-bold px-2.5 py-1 rounded-md border"
                    style={{
                      backgroundColor: "var(--highlight)",
                      borderColor: "var(--border)",
                      color: "var(--text)",
                    }}
                  >
                    {std}
                  </span>
                ))
              ) : (
                <span className="text-xs text-stone-500 italic">
                  No strict regulatory standards explicitly tagged
                </span>
              )}
            </div>
          </div>

          {/* Technologies & Languages */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-stone-700 flex items-center gap-1.5">
              <Code2 className="w-4 h-4 text-stone-700" />
              <span>Key Technologies & Libraries</span>
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {repository.key_technologies.length > 0 ? (
                repository.key_technologies.map((tech) => (
                  <span
                    key={tech}
                    className="text-[11px] font-mono px-2 py-0.5 rounded bg-stone-100 border border-stone-300 text-stone-800"
                  >
                    {tech}
                  </span>
                ))
              ) : (
                <span className="text-xs text-stone-500 italic">
                  {repository.primary_language || "General Codebase"}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div
          className="p-4 border-t text-xs text-stone-500 flex items-center justify-between"
          style={{
            backgroundColor: "var(--row-even)",
            borderColor: "var(--border)",
          }}
        >
          <span>Repository ID #{repository.id}</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg border bg-white font-semibold text-stone-800 hover:bg-stone-50 shadow-xs"
            style={{ borderColor: "var(--border)" }}
          >
            Close
          </button>
        </div>
      </aside>
    </div>
  );
};

export default RepositoryDetailDrawer;

