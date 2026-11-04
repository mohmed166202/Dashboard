/**
 * useWorker.ts
 * ───────────────────────────────────────────────────────────────────────────
 * React hook that wraps the Web Worker lifecycle:
 *   • Spawns a new worker per message (terminate-and-replace pattern)
 *   • Prevents race conditions: stale worker results are discarded
 *   • Returns { filteredData, isFiltering, workerError }
 *
 * Usage:
 *   const { filteredData, isFiltering, workerError } = useFilterWorker({
 *     repos, query, useRegex, selectedStandards
 *   });
 */

import { useState, useEffect, useRef } from "react";
import type { Repository } from "../types/api";
import type { FilterWorkerInput, FilterWorkerOutput } from "../workers/filterWorker";

interface UseFilterWorkerOptions {
  repos: Repository[];
  query: string;
  useRegex: boolean;
  selectedStandards: string[];
  /** Skip worker and return all repos unchanged when false */
  enabled?: boolean;
}

interface UseFilterWorkerResult {
  filteredData: Repository[];
  isFiltering: boolean;
  workerError: string | null;
  /** Time taken by the last filter operation in ms */
  lastDurationMs: number;
}

export function useFilterWorker({
  repos,
  query,
  useRegex,
  selectedStandards,
  enabled = true,
}: UseFilterWorkerOptions): UseFilterWorkerResult {
  const [filteredData, setFilteredData] = useState<Repository[]>(repos);
  const [isFiltering, setIsFiltering] = useState(false);
  const [workerError, setWorkerError] = useState<string | null>(null);
  const [lastDurationMs, setLastDurationMs] = useState(0);

  // Ref to the currently active worker so we can terminate it on re-fire
  const workerRef = useRef<Worker | null>(null);
  // Generation counter — if the worker that replies is not current gen, discard
  const generationRef = useRef(0);

  useEffect(() => {
    // No filter needed: short-circuit, return all repos as-is
    if (!enabled || (!query && selectedStandards.length === 0)) {
      workerRef.current?.terminate();
      workerRef.current = null;
      setFilteredData(repos);
      setIsFiltering(false);
      setWorkerError(null);
      return;
    }

    // Terminate any previous in-flight worker
    if (workerRef.current) {
      workerRef.current.terminate();
      workerRef.current = null;
    }

    const gen = ++generationRef.current;
    setIsFiltering(true);
    setWorkerError(null);

    // Spawn new worker using Vite's ?worker import syntax
    // We use new URL() so Vite bundles filterWorker as a separate chunk
    const worker = new Worker(
      new URL("../workers/filterWorker.ts", import.meta.url),
      { type: "module" }
    );
    workerRef.current = worker;

    const payload: FilterWorkerInput = { repos, query, useRegex, selectedStandards };
    worker.postMessage(payload);

    worker.onmessage = (event: MessageEvent<FilterWorkerOutput>) => {
      // Discard if a newer generation has already fired
      if (gen !== generationRef.current) return;

      const { filtered, error, durationMs } = event.data;
      setFilteredData(filtered);
      setWorkerError(error);
      setLastDurationMs(durationMs);
      setIsFiltering(false);
      worker.terminate();
      workerRef.current = null;
    };

    worker.onerror = (err) => {
      if (gen !== generationRef.current) return;
      setWorkerError(`Worker error: ${err.message}`);
      setIsFiltering(false);
      worker.terminate();
      workerRef.current = null;
    };

    return () => {
      worker.terminate();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [repos, query, useRegex, selectedStandards, enabled]);

  return { filteredData, isFiltering, workerError, lastDurationMs };
}

