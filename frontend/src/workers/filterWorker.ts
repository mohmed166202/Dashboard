/**
 * filterWorker.ts
 * ───────────────────────────────────────────────────────────────────────────
 * Dedicated Web Worker that runs repository filtering and regex matching
 * entirely off the main thread. Prevents UI jank during large dataset ops.
 *
 * Message protocol:
 *   INPUT  (main → worker): FilterWorkerInput
 *   OUTPUT (worker → main): FilterWorkerOutput
 */

import type { Repository } from "../types/api";

// ── Message Types ─────────────────────────────────────────────────────────────

export interface FilterWorkerInput {
  repos: Repository[];
  query: string;
  useRegex: boolean;
  selectedStandards: string[];
}

export interface FilterWorkerOutput {
  filtered: Repository[];
  error: string | null;
  durationMs: number;
}

// ── Core Filter Logic ─────────────────────────────────────────────────────────

function buildSearchableBag(repo: Repository): string {
  return [
    repo.name,
    repo.owner,
    repo.description ?? "",
    repo.primary_domain ?? "",
    repo.secondary_domains.join(" "),
    repo.detected_standards.join(" "),
    repo.primary_language ?? "",
    repo.project_status ?? "",
    repo.key_technologies.join(" "),
  ]
    .join(" ")
    .toLowerCase();
}

function applyFilters(input: FilterWorkerInput): FilterWorkerOutput {
  const t0 = performance.now();
  const { repos, query, useRegex, selectedStandards } = input;

  let regex: RegExp | null = null;
  if (query && useRegex) {
    try {
      regex = new RegExp(query, "i");
    } catch {
      return { filtered: [], error: `Invalid regex: ${query}`, durationMs: 0 };
    }
  }

  const normalQuery = query.trim().toLowerCase();

  const filtered = repos.filter((repo) => {
    // ── Standards cross-filter (AND/OR: any selected standard must match) ──
    if (selectedStandards.length > 0) {
      const hasStandard = selectedStandards.some((s) =>
        repo.detected_standards.includes(s)
      );
      if (!hasStandard) return false;
    }

    // ── Text / Regex filter ────────────────────────────────────────────────
    if (!query) return true;

    const bag = buildSearchableBag(repo);

    if (useRegex && regex) {
      return regex.test(bag);
    }

    // Plain text: support multi-word AND search (all tokens must match)
    const tokens = normalQuery.split(/\s+/).filter(Boolean);
    return tokens.every((tok) => bag.includes(tok));
  });

  return {
    filtered,
    error: null,
    durationMs: performance.now() - t0,
  };
}

// ── Worker Message Handler ────────────────────────────────────────────────────

self.onmessage = (event: MessageEvent<FilterWorkerInput>) => {
  const result = applyFilters(event.data);
  self.postMessage(result);
};

