/**
 * useDebouncedValue.ts
 * ───────────────────────────────────────────────────────────────────────────
 * Returns a debounced copy of `value` that only updates after `delayMs`
 * of silence. Used to prevent excessive worker invocations during fast typing.
 *
 * Uses React 18's useDeferredValue under the hood for concurrent-mode
 * compatibility, combined with a trailing timeout for the actual delay.
 *
 * Usage:
 *   const debouncedQuery = useDebouncedValue(searchQuery, 300);
 */

import { useState, useEffect, useDeferredValue } from "react";

export function useDebouncedValue<T>(value: T, delayMs = 300): T {
  const [debounced, setDebounced] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);

  // Also apply React's concurrent-mode deferral on top — this lets React
  // skip re-rendering the expensive table during rapid keystroke bursts
  return useDeferredValue(debounced);
}

