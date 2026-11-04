# Healthcare Portfolio Intelligence: Phase 1 Guide

## Phase 1: High-Speed Discovery & Repository Cataloging

This module implements **Phase 1** of the healthcare portfolio intelligence pipeline. It discovers and catalogs 150+ GitHub repositories in seconds using GitHub GraphQL v4, extracts rich operational metadata, monitors rate limits, and persists the results in an indexed SQLite database and CSV export.

---

### Project Structure

```text
Dashboard/
├── .env                  <-- Put your GitHub Personal Access Token here
├── .env.example          <-- Configuration reference
├── config.py             <-- Configuration loader and validator
├── db.py                 <-- SQLite schema, WAL-mode connection pool, and indexing
├── github_client.py      <-- GraphQL v4 client (100 repos/page) + rate-limit tracker
├── discovery.py          <-- Phase 1 discovery and cataloging orchestrator
├── run_phase1.py         <-- CLI runner and CSV exporter
└── test_credentials.py   <-- Quick token & connectivity diagnostic tool
```

---

### Harvested Attributes (Per Repository)

| Attribute | Source | Description |
|---|---|---|
| `name` / `name_with_owner` | GraphQL | Unique repository identifier (e.g. `HospitalGroup/emr-core`) |
| `owner` | GraphQL | Organization or user handle |
| `description` | GraphQL | Project description |
| `primary_language` | GraphQL | Main programming language detected |
| `languages` | GraphQL | Top 5 languages with size weighting |
| `topics` | GraphQL | All GitHub repository topics / tags |
| `default_branch` | GraphQL | Default branch reference (e.g. `main` or `master`) |
| `is_private` / `is_fork` | GraphQL | Visibility flags |
| `is_archived` | GraphQL | Determines if project is retired or active |
| `pushed_at` / `updated_at` | GraphQL | Activity timestamps |
| `disk_usage_kb` | GraphQL | Size of the codebase |
| `open_issues_count` | GraphQL | Outstanding bug / task count |
| `stargazers_count` / `forks` | GraphQL | Community/internal engagement metrics |
| `has_readme` / `readme_file` | GraphQL Blob | Checks for `README.md`, `readme.md`, `README.rst`, `README.txt` |

---

### How to Run

#### Step 1: Add your GitHub Personal Access Token
Open `.env` in this directory and paste your token:
```ini
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
GITHUB_TARGET_TYPE=viewer
```
*(If you want to target a specific organization like `AOH-Group`, set `GITHUB_TARGET_TYPE=org` and `GITHUB_TARGET_OWNER=AOH-Group`)*.

#### Step 2: Test Credentials & Rate Limits
```bash
python test_credentials.py
```

#### Step 3: Run Full Catalog Discovery
```bash
python run_phase1.py
```

#### Step 4: Export to CSV (Automatic)
The discovered portfolio is automatically saved to:
* SQLite DB: `healthcare_portfolio_catalog.db`
* CSV Spreadsheet: `./output/discovered_repositories.csv`

