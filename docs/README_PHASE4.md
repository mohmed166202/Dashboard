# Healthcare Portfolio Intelligence: Phase 4 Guide

## Phase 4: Portfolio Catalog Synthesis & Relational Graphing

Phase 4 synthesizes all repository classifications, discovered architecture files, and database schemas into an actionable knowledge base and interactive executive dashboard.

---

### Phase 4 Deliverables

| Deliverable | Location | Description |
|---|---|---|
| **Interactive Dashboard** | `output/dashboard/index.html` | Self-contained Single-Page Application (HTML5 / Tailwind / Chart.js) with live filters, domain charts, cross-cutting heatmaps, and repository directory. |
| **Executive Markdown Report** | `output/reports/EXECUTIVE_HEALTHCARE_PORTFOLIO_REPORT.md` | Strategic report ready for C-suite / CMIO / Board of Directors highlighting accreditation readiness and revenue integrity. |
| **Relational Knowledge Graph** | `output/reports/portfolio_graph.json` | Network graph containing Nodes (`domains`, `repositories`, `standards`) and Edges (`PRIMARY_DOMAIN`, `SECONDARY_DOMAIN`, `IMPLEMENTS`). |
| **Full Synthesis Data** | `output/reports/portfolio_synthesis.json` | Machine-readable JSON of all domain counts, cross-cutting matrices, and gap recommendations. |

---

### Core Analytical Capabilities

1. **Domain Matrix Breakdown:**
   - Tracks portfolio volume and percentages across each of the 9 healthcare disciplines.
   - Computes the **Cross-Cutting Overlap Matrix** to discover multi-domain systems (e.g. Pharmacy systems bridging into Supply Chain inventory, Medical Coding systems feeding Finance RCM).
2. **Strategic Healthcare Pillars Deep-Dive:**
   - **GAHAR & JCI Quality & Governance Posture:** Detects Occurrence Variance Reporting (OVR), infection control, and audit compliance modules.
   - **Medical Coding & RCM Posture:** Pinpoints ICD-10, CPT, pre-authorization, and claims pricing automation.
   - **AOH Hospital Expansion Project:** Aggregates MEP engineering packages, bill of quantities (BOQ), contractor tools, and bunker long-lead equipment.
3. **Gap Analysis & Risk Advisory:**
   - Highlights uncovered or under-represented domains across the enterprise.
   - Flags missing documentation debt (repositories lacking README or API specs).
   - Generates actionable executive recommendations categorized by severity (Critical / High / Medium).

---

### How to Run Phase 4

#### 1. Generate All Deliverables (Dashboard + Reports + Graph)
```bash
python run_phase4.py
```

#### 2. Open Interactive Dashboard Directly in Your Web Browser
```bash
python run_phase4.py --open
```
*(Or simply double-click `output/dashboard/index.html` in your file explorer!)*

#### 3. Host Dashboard on a Local Web Server
```bash
python run_phase4.py --serve --port 8080
```
*(Access via `http://localhost:8080/index.html`)*

