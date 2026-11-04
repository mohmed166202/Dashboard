/**
 * QueryProvider — wraps the app with TanStack QueryClient.
 *
 * Config:
 *  - defaultOptions mirrors the per-query CACHE_CONFIG in useApiQueries.ts
 *  - ReactQueryDevtools is included only in development builds (tree-shaken in prod)
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import type { ReactNode } from "react";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      gcTime:    10 * 60 * 1000,
      retry: 2,
      refetchOnWindowFocus: false, // Don't refetch just because user switched tabs
    },
  },
});

interface QueryProviderProps {
  children: ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {import.meta.env.DEV && (
        <ReactQueryDevtools
          initialIsOpen={false}
          buttonPosition="bottom-left"
        />
      )}
    </QueryClientProvider>
  );
}

// Export for cache invalidation use in Sync button
export { queryClient };

