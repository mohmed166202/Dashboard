"""
Andalusia Healthcare Portfolio — FastAPI Backend
Phase 2: Data Service & API Integration Layer

Exposes live SQLite data from healthcare_portfolio_catalog.db and
the parsed XLSX matrix through versioned REST endpoints.
Designed for high-performance: WAL SQLite, response caching,
CORS pre-configured for the Vite dev server.
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Any, Generator

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ─── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
ROOT_DIR = BASE_DIR.parent.parent

# Check data directory first, fallback to current dir or root dir
def _resolve_path(filename: str) -> Path:
    candidates = [
        ROOT_DIR / "data" / filename,
        ROOT_DIR / filename,
        BASE_DIR / filename,
    ]
    for p in candidates:
        if p.exists():
            return p
    return ROOT_DIR / "data" / filename

DB_PATH  = _resolve_path("healthcare_portfolio_catalog.db")
XLSX_PATH = _resolve_path("andalusia_healthcare_domains_matrix.xlsx")

# ─── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Andalusia Healthcare Portfolio API",
    version="2.0.0",
    description="Phase 2 — Data service for the React dashboard.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── DB Helpers ──────────────────────────────────────────────────────────────
@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA query_only=ON;")
    try:
        yield conn
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def parse_json_field(value: str | None) -> list:
    """
    Handles both proper JSON arrays ("[\"a\",\"b\"]") and
    legacy space-separated strings ("FHIR ICD-10 EMR").
    """
    if not value:
        return []
    stripped = value.strip()
    if not stripped:
        return []
    # Proper JSON array
    if stripped.startswith("["):
        try:
            result = json.loads(stripped)
            return result if isinstance(result, list) else [str(result)]
        except (json.JSONDecodeError, TypeError):
            pass
    # Space-separated fallback (legacy DB values)
    return [v.strip() for v in stripped.split() if v.strip()]


# ─── XLSX Matrix Parser (cached) ─────────────────────────────────────────────
@lru_cache(maxsize=1)
def load_matrix_data() -> list[dict[str, Any]]:
    """
    Parses the XLSX matrix into a list of normalized row dicts.
    Result is LRU-cached so the file is read only once per process lifetime.
    """
    if not XLSX_PATH.exists():
        return []
    try:
        import openpyxl
        wb = openpyxl.load_workbook(str(XLSX_PATH), read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        wb.close()

        if not rows:
            return []

        headers = [str(h).strip() if h is not None else f"col_{i}" for i, h in enumerate(rows[0])]
        result = []
        for row in rows[1:]:
            if all(v is None for v in row):
                continue
            item: dict[str, Any] = {}
            for h, v in zip(headers, row):
                item[h] = v
            result.append(item)
        return result
    except Exception as e:
        return [{"error": str(e)}]


# ═══════════════════════════════════════════════════════════════════════════════
#  ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
def health_check():
    db_ok = DB_PATH.exists()
    xlsx_ok = XLSX_PATH.exists()
    return {
        "status": "ok",
        "db_connected": db_ok,
        "xlsx_loaded": xlsx_ok,
        "api_version": "2.0.0",
    }


# ── Dashboard Summary ─────────────────────────────────────────────────────────
@app.get("/api/summary")
def get_summary():
    """High-level KPI metrics for the dashboard metric cards."""
    with get_db() as conn:
        total_repos = conn.execute("SELECT COUNT(*) FROM repositories").fetchone()[0]
        active_repos = conn.execute(
            "SELECT COUNT(*) FROM repositories WHERE is_archived = 0"
        ).fetchone()[0]
        total_classified = conn.execute(
            "SELECT COUNT(*) FROM domain_classifications"
        ).fetchone()[0]
        avg_confidence = conn.execute(
            "SELECT AVG(confidence_score) FROM domain_classifications"
        ).fetchone()[0]
        total_dossiers = conn.execute(
            "SELECT COUNT(*) FROM repo_dossiers"
        ).fetchone()[0]

        # Count unique detected standards across all classifications
        all_standards_rows = conn.execute(
            "SELECT detected_standards FROM domain_classifications WHERE detected_standards IS NOT NULL"
        ).fetchall()
        unique_standards: set[str] = set()
        for r in all_standards_rows:
            unique_standards.update(parse_json_field(r[0]))

        # Language breakdown
        lang_rows = conn.execute("""
            SELECT primary_language, COUNT(*) as cnt
            FROM repositories
            WHERE primary_language IS NOT NULL
            GROUP BY primary_language ORDER BY cnt DESC LIMIT 8
        """).fetchall()

    return {
        "total_repositories": total_repos,
        "active_repositories": active_repos,
        "total_classified": total_classified,
        "total_dossiers": total_dossiers,
        "avg_confidence_score": round((avg_confidence or 0.0) * 100, 1),
        "unique_standards_detected": len(unique_standards),
        "top_languages": {r["primary_language"]: r["cnt"] for r in lang_rows},
        "matrix_coverage_pct": round((total_classified / total_repos) * 100, 1) if total_repos else 0,
    }


# ── Domain Distribution ───────────────────────────────────────────────────────
@app.get("/api/domains")
def get_domain_distribution():
    """
    Returns per-domain stats: repo count, avg confidence, detected standards.
    Used for the DomainFilterBar, charts, and metric cards.
    """
    with get_db() as conn:
        rows = conn.execute("""
            SELECT
                primary_domain,
                COUNT(*) as repo_count,
                ROUND(AVG(confidence_score) * 100, 1) as avg_confidence_pct,
                GROUP_CONCAT(detected_standards, '|||') as all_standards_raw
            FROM domain_classifications
            GROUP BY primary_domain
            ORDER BY repo_count DESC
        """).fetchall()

    result = []
    for r in rows:
        # Merge and deduplicate standards across all repos in domain
        raw = r["all_standards_raw"] or ""
        all_stds: set[str] = set()
        for chunk in raw.split("|||"):
            all_stds.update(parse_json_field(chunk))

        result.append({
            "domain": r["primary_domain"],
            "repo_count": r["repo_count"],
            "avg_confidence_pct": r["avg_confidence_pct"],
            "detected_standards": sorted(all_stds),
        })

    return {"domains": result, "total_domains": len(result)}


# ── Repositories ──────────────────────────────────────────────────────────────
@app.get("/api/repositories")
def get_repositories(
    domain: str | None = Query(None, description="Filter by primary domain"),
    language: str | None = Query(None, description="Filter by primary language"),
    status: str | None = Query(None, description="Filter by project_status"),
    search: str | None = Query(None, description="Fuzzy search on name and description"),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Paginated, filterable list of repositories with their domain classification.
    """
    base_query = """
        SELECT
            r.id, r.name, r.name_with_owner, r.owner, r.description,
            r.url, r.primary_language, r.languages, r.topics,
            r.is_archived, r.is_private, r.pushed_at, r.disk_usage_kb,
            r.open_issues_count, r.has_readme,
            c.primary_domain, c.secondary_domains, c.confidence_score,
            c.detected_standards, c.project_status, c.key_technologies,
            c.domain_justification
        FROM repositories r
        LEFT JOIN domain_classifications c ON r.name_with_owner = c.name_with_owner
        WHERE 1=1
    """
    params: list[Any] = []

    if domain:
        base_query += " AND c.primary_domain = ?"
        params.append(domain)
    if language:
        base_query += " AND r.primary_language = ?"
        params.append(language)
    if status:
        base_query += " AND c.project_status LIKE ?"
        params.append(f"%{status}%")
    if search:
        base_query += " AND (r.name LIKE ? OR r.description LIKE ? OR c.domain_justification LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])

    count_query = f"SELECT COUNT(*) FROM ({base_query}) t"
    data_query = base_query + " ORDER BY c.confidence_score DESC LIMIT ? OFFSET ?"

    with get_db() as conn:
        total = conn.execute(count_query, params).fetchone()[0]
        rows = conn.execute(data_query, params + [limit, offset]).fetchall()

    items = []
    for r in rows:
        item = row_to_dict(r)
        item["languages"] = parse_json_field(item.get("languages"))
        item["topics"] = parse_json_field(item.get("topics"))
        item["secondary_domains"] = parse_json_field(item.get("secondary_domains"))
        item["detected_standards"] = parse_json_field(item.get("detected_standards"))
        item["key_technologies"] = parse_json_field(item.get("key_technologies"))
        items.append(item)

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total,
    }


# ── Single Repository Detail ──────────────────────────────────────────────────
@app.get("/api/repositories/{name_with_owner:path}")
def get_repository_detail(name_with_owner: str):
    with get_db() as conn:
        repo_row = conn.execute(
            "SELECT * FROM repositories WHERE name_with_owner = ?",
            (name_with_owner,)
        ).fetchone()
        if not repo_row:
            raise HTTPException(status_code=404, detail="Repository not found")

        cls_row = conn.execute(
            "SELECT * FROM domain_classifications WHERE name_with_owner = ?",
            (name_with_owner,)
        ).fetchone()

        dos_row = conn.execute(
            "SELECT repo_name, priority_files_count, priority_files_list, extracted_entities, extracted_dependencies, extracted_apis, dossier_size_bytes, extracted_at FROM repo_dossiers WHERE name_with_owner = ?",
            (name_with_owner,)
        ).fetchone()

    repo = row_to_dict(repo_row)
    repo["languages"] = parse_json_field(repo.get("languages"))
    repo["topics"] = parse_json_field(repo.get("topics"))

    classification = None
    if cls_row:
        classification = row_to_dict(cls_row)
        classification["secondary_domains"] = parse_json_field(classification.get("secondary_domains"))
        classification["detected_standards"] = parse_json_field(classification.get("detected_standards"))
        classification["key_technologies"] = parse_json_field(classification.get("key_technologies"))

    dossier_meta = None
    if dos_row:
        dossier_meta = row_to_dict(dos_row)
        dossier_meta["priority_files_list"] = parse_json_field(dossier_meta.get("priority_files_list"))
        dossier_meta["extracted_entities"] = parse_json_field(dossier_meta.get("extracted_entities"))
        dossier_meta["extracted_dependencies"] = parse_json_field(dossier_meta.get("extracted_dependencies"))
        dossier_meta["extracted_apis"] = parse_json_field(dossier_meta.get("extracted_apis"))

    return {"repository": repo, "classification": classification, "dossier_meta": dossier_meta}


# ── Domain Taxonomy (from domain_taxonomy.py) ─────────────────────────────────
@app.get("/api/taxonomy")
def get_taxonomy():
    """Returns the full domain taxonomy from domain_taxonomy.py."""
    from domain_taxonomy import HEALTHCARE_DOMAINS
    result = []
    for domain_name, defn in HEALTHCARE_DOMAINS.items():
        result.append({
            "id": domain_name.lower().replace(" ", "-").replace("&", "and"),
            "name": defn.name,
            "description": defn.description,
            "token_count": len(defn.high_precision_tokens),
            "high_precision_tokens": defn.high_precision_tokens,
            "specialized_standards": defn.specialized_standards,
            "semantic_profile_text": defn.semantic_profile_text,
        })
    return {"domains": result, "total": len(result)}


# ── Matrix XLSX ───────────────────────────────────────────────────────────────
@app.get("/api/matrix")
def get_matrix(limit: int = Query(500, ge=1, le=2000), offset: int = Query(0, ge=0)):
    """Returns parsed rows from the XLSX matrix file with pagination."""
    data = load_matrix_data()
    total = len(data)
    page = data[offset : offset + limit]
    return {
        "rows": page,
        "total": total,
        "limit": limit,
        "offset": offset,
        "headers": list(page[0].keys()) if page else [],
    }


# ── Confidence Distribution ───────────────────────────────────────────────────
@app.get("/api/analytics/confidence")
def get_confidence_distribution():
    """
    Confidence score distribution bucketed into ranges for the histogram chart.
    """
    with get_db() as conn:
        rows = conn.execute("""
            SELECT primary_domain, confidence_score
            FROM domain_classifications
            ORDER BY confidence_score DESC
        """).fetchall()

    buckets = {"0.9–1.0": 0, "0.8–0.9": 0, "0.7–0.8": 0, "0.6–0.7": 0, "<0.6": 0}
    domain_scores: dict[str, list[float]] = {}
    for r in rows:
        score = r["confidence_score"] or 0.0
        domain = r["primary_domain"]
        domain_scores.setdefault(domain, []).append(score)

        if score >= 0.9:
            buckets["0.9–1.0"] += 1
        elif score >= 0.8:
            buckets["0.8–0.9"] += 1
        elif score >= 0.7:
            buckets["0.7–0.8"] += 1
        elif score >= 0.6:
            buckets["0.6–0.7"] += 1
        else:
            buckets["<0.6"] += 1

    per_domain_avg = {
        domain: round(sum(scores) / len(scores) * 100, 1)
        for domain, scores in domain_scores.items()
    }

    return {
        "distribution_buckets": [
            {"range": k, "count": v} for k, v in buckets.items()
        ],
        "per_domain_avg_pct": per_domain_avg,
    }


# ── Standards Analytics ───────────────────────────────────────────────────────
@app.get("/api/analytics/standards")
def get_standards_analytics():
    """
    Frequency of each detected standard across the classified portfolio.
    """
    with get_db() as conn:
        rows = conn.execute(
            "SELECT detected_standards FROM domain_classifications WHERE detected_standards IS NOT NULL"
        ).fetchall()

    counter: dict[str, int] = {}
    for r in rows:
        for std in parse_json_field(r[0]):
            counter[std] = counter.get(std, 0) + 1

    sorted_stds = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    return {
        "standards": [{"name": s, "count": c} for s, c in sorted_stds],
        "total_unique": len(sorted_stds),
    }

