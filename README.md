# Andalusia Healthcare Portfolio & Intelligent Analytics Dashboard

> High-performance, production-grade React 19 + Vite dashboard paired with an asynchronous FastAPI backend for comprehensive healthcare domain classification, matrix visualization, and clinical standards analytics.

---

## 🏛️ Project Architecture

```
Dashboard/
├── src/
│   ├── backend/                # FastAPI REST data service
│   │   └── api.py              # Cache-backed endpoints, WAL SQLite connector, matrix queries
│   ├── pipeline/               # Data ingestion, classification, & synthesis engine
│   │   ├── config.py           # Configuration manager & environment variables
│   │   ├── db.py               # SQLite schema migrations & query utilities
│   │   ├── domain_taxonomy.py  # Healthcare domain taxonomy definitions
│   │   ├── hybrid_classifier.py# Hybrid rule-based & semantic classifier
│   │   ├── discovery.py        # GitHub repository discovery pipeline
│   │   ├── content_extractor.py# Source code and documentation extraction
│   │   ├── dossier_builder.py  # Repository portfolio dossier synthesis
│   │   └── report_generator.py # Executive report and synthesis generator
│   └── scripts/                # Execution & verification scripts (Phases 1–5)
│       ├── run_phase1.py ... run_phase5.py
│       └── test_phase2.py ... test_phase5.py
├── frontend/                   # High-Performance React 19 + Vite Single-Page Application
│   ├── src/
│   │   ├── components/         # Design-system compliant UI components
│   │   │   ├── VirtualizedMatrixTable.tsx  # TanStack Virtual 60 FPS table
│   │   │   ├── DomainRadarChart.tsx        # Recharts polar domain coverage
│   │   │   ├── StandardsBarChart.tsx       # Recharts horizontal standards density
│   │   │   ├── MatrixCorrelationHeatmap.tsx# 9x9 CSS co-occurrence matrix
│   │   │   ├── RepositoryDetailDrawer.tsx  # Slide-over repository inspector
│   │   │   └── AnalyticsSkeleton.tsx       # Zero-CLS pulsing layout shimmers
│   │   ├── hooks/              # Custom React hooks
│   │   │   ├── useApiQueries.ts            # TanStack Query hooks (5m stale cache)
│   │   │   ├── useWorker.ts                # Web Worker lifecycle & race-condition manager
│   │   │   └── useDebouncedValue.ts        # Trailing debounce + React deferred value
│   │   ├── workers/            # Multi-threaded Web Workers
│   │   │   └── filterWorker.ts # Off-main-thread search & regex processor
│   │   └── types/              # End-to-end typed API schemas
│   ├── vite.config.ts          # Deterministic vendor chunk splitting (Recharts async chunk)
│   └── tailwind.config.js      # Warm earth/cream design tokens
├── data/                       # Portfolio database & Excel taxonomy matrix
│   ├── healthcare_portfolio_catalog.db
│   └── andalusia_healthcare_domains_matrix.xlsx
├── docs/                       # Comprehensive phase walkthroughs & analysis reports
│   └── andalusia_portfolio_analysis_report.md
└── output/                     # Exported matrices, CSVs, and classifications
```

---

## 🎨 Warm Earth / Cream Design System

All components across the portfolio strictly follow the custom design token specification:

```css
:root {
  --header-bg:   #4A3426; /* Deep earthy brown header & primary badges */
  --header-text: #FFFFFF; /* High contrast text */
  --row-odd:     #FFFFFF; /* White alternating row & card surface */
  --row-even:    #F7F1E9; /* Warm cream alternating background */
  --highlight:   #ECDDC8; /* Tan target V2 confidence spotlight */
  --border:      #785F4B; /* Warm brown dividers & card outlines */
  --text:        #1E140F; /* Ultra-readable text */
}
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.10+ (FastAPI, Uvicorn, OpenPyXL, SQLite3)
- **Node.js**: 18+ / 22+ (npm or pnpm)

### 1. Start FastAPI Backend
```bash
# From repository root
python -m uvicorn src.backend.api:app --reload --port 8000
# Or using the root runner:
python -m uvicorn api:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### 2. Start Vite Frontend
```bash
cd frontend
npm install
npm run dev
```
- Live Dashboard: `http://localhost:5173`

### 3. Production Build & Audit
```bash
cd frontend
npm run build
```
- **0 TypeScript errors**
- **Main app chunk**: 39.76 kB (10.57 kB gzip) — 93% smaller than un-split bundle
- **Web Worker**: Dedicated `filterWorker.js` chunk offloading multi-token and regex search
- **Zero CLS**: Layout-stable shimmers matching Recharts geometry

---

## 📊 Live Portfolio Coverage
- **Total Repositories**: 156 (100% classified)
- **Average Confidence**: 63.7% V2 match
- **Top Detected Standards**: ICD-10, EMR, HIS, HL7, DICOM, FHIR
- **Primary Domain**: Clinical Informatics & Healthcare Management
