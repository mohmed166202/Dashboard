import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * vite.config.ts — Phase 5 Production-Optimized Build
 * ─────────────────────────────────────────────────────────────────────────────
 * Key optimizations:
 *  • manualChunks splits Recharts (async), TanStack Table/Virtual, TanStack Query,
 *    React core, and Lucide icons into independent cached chunks.
 *  • Web Workers bundled as ES modules via ?worker import — Vite handles this
 *    automatically when new URL('../workers/filterWorker.ts', import.meta.url) is used.
 *  • target: 'esnext' — no legacy transpilation overhead
 *  • cssMinify: true (default in prod, explicit here for clarity)
 *  • reportCompressedSize: true — shows gzip sizes in build output
 */
export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      '@': import.meta.dirname + '/src',
    },
  },

  server: {
    port: 5173,
    open: true,
  },

  worker: {
    // Bundle workers as ES modules so Vite can tree-shake and type-check them
    format: 'es',
  },

  build: {
    outDir: 'dist',
    sourcemap: true,
    target: 'esnext',          // modern browsers — no polyfill bloat
    cssMinify: true,
    reportCompressedSize: true,

    rollupOptions: {
      output: {
        /**
         * manualChunks — deterministic chunk splitting for optimal long-term caching.
         * Each vendor chunk gets its own content-hash filename.
         * Recharts is the heaviest dep (~380 kB min) → isolated so it only loads
         * when the analytics tab is first clicked (via React.lazy).
         */
        manualChunks(id: string) {
          // ── Core React runtime ────────────────────────────────────────────
          if (
            id.includes('node_modules/react/') ||
            id.includes('node_modules/react-dom/') ||
            id.includes('node_modules/scheduler/')
          ) {
            return 'vendor-react';
          }

          // ── Recharts + its D3 sub-dependencies (lazy-loaded) ─────────────
          if (
            id.includes('node_modules/recharts') ||
            id.includes('node_modules/d3-') ||
            id.includes('node_modules/victory-vendor') ||
            id.includes('node_modules/eventemitter3')
          ) {
            return 'vendor-recharts';
          }

          // ── TanStack Table + Virtual (used in Phase 3 table) ─────────────
          if (
            id.includes('node_modules/@tanstack/react-table') ||
            id.includes('node_modules/@tanstack/react-virtual') ||
            id.includes('node_modules/@tanstack/table-core') ||
            id.includes('node_modules/@tanstack/virtual-core')
          ) {
            return 'vendor-tanstack-table';
          }

          // ── TanStack Query (data fetching) ────────────────────────────────
          if (
            id.includes('node_modules/@tanstack/react-query') ||
            id.includes('node_modules/@tanstack/query-core') ||
            id.includes('node_modules/@tanstack/react-query-devtools')
          ) {
            return 'vendor-tanstack-query';
          }

          // ── Lucide icons ──────────────────────────────────────────────────
          if (id.includes('node_modules/lucide-react')) {
            return 'vendor-icons';
          }

          // ── Tailwind utilities (clsx, tailwind-merge) ─────────────────────
          if (
            id.includes('node_modules/clsx') ||
            id.includes('node_modules/tailwind-merge')
          ) {
            return 'vendor-utils';
          }
        },
      },
    },
  },
})
