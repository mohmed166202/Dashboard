"""
Database layer for Healthcare Portfolio Intelligence.
Manages SQLite connection, schema initialization, indices, and upsert operations.
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS repositories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT UNIQUE,
    name TEXT NOT NULL,
    name_with_owner TEXT NOT NULL UNIQUE,
    owner TEXT NOT NULL,
    description TEXT,
    url TEXT,
    primary_language TEXT,
    languages TEXT,          -- JSON array of top languages
    topics TEXT,             -- JSON array of topic strings
    default_branch TEXT,
    is_private INTEGER NOT NULL DEFAULT 0,
    is_archived INTEGER NOT NULL DEFAULT 0,
    is_fork INTEGER NOT NULL DEFAULT 0,
    created_at TEXT,
    updated_at TEXT,
    pushed_at TEXT,
    disk_usage_kb INTEGER DEFAULT 0,
    open_issues_count INTEGER DEFAULT 0,
    stargazers_count INTEGER DEFAULT 0,
    forks_count INTEGER DEFAULT 0,
    has_readme INTEGER DEFAULT 0,
    readme_filename TEXT,
    phase1_status TEXT DEFAULT 'discovered',
    discovered_at TEXT NOT NULL,
    last_synced_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_repo_name ON repositories(name);
CREATE INDEX IF NOT EXISTS idx_repo_owner ON repositories(owner);
CREATE INDEX IF NOT EXISTS idx_repo_lang ON repositories(primary_language);
CREATE INDEX IF NOT EXISTS idx_repo_archived ON repositories(is_archived);
CREATE INDEX IF NOT EXISTS idx_repo_pushed ON repositories(pushed_at);

CREATE TABLE IF NOT EXISTS rate_limit_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    limit_total INTEGER,
    remaining INTEGER,
    cost INTEGER,
    reset_at TEXT
);

CREATE TABLE IF NOT EXISTS discovery_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    target_type TEXT,
    target_owner TEXT,
    total_discovered INTEGER DEFAULT 0,
    active_count INTEGER DEFAULT 0,
    archived_count INTEGER DEFAULT 0,
    private_count INTEGER DEFAULT 0,
    public_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS repo_dossiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_name TEXT NOT NULL,
    name_with_owner TEXT NOT NULL UNIQUE,
    default_branch TEXT,
    priority_files_count INTEGER DEFAULT 0,
    priority_files_list TEXT,       -- JSON array of file paths analyzed
    extracted_entities TEXT,        -- JSON array of healthcare & business entities detected
    extracted_dependencies TEXT,    -- JSON array of dependencies/frameworks
    extracted_apis TEXT,            -- JSON array of API paths/specs
    dossier_markdown TEXT NOT NULL, -- Combined Project Synthesis Dossier (<100KB)
    dossier_size_bytes INTEGER DEFAULT 0,
    extracted_at TEXT NOT NULL,
    FOREIGN KEY(name_with_owner) REFERENCES repositories(name_with_owner)
);

CREATE INDEX IF NOT EXISTS idx_dossier_repo ON repo_dossiers(repo_name);
CREATE INDEX IF NOT EXISTS idx_dossier_owner ON repo_dossiers(name_with_owner);

CREATE TABLE IF NOT EXISTS domain_classifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_name TEXT NOT NULL,
    name_with_owner TEXT NOT NULL UNIQUE,
    primary_domain TEXT NOT NULL,
    secondary_domains TEXT,        -- JSON array of secondary domains
    confidence_score REAL NOT NULL,
    domain_justification TEXT NOT NULL,
    detected_standards TEXT,       -- JSON array (e.g. GAHAR, JCI, ICD-10, CPT, AOH, etc.)
    project_status TEXT,           -- e.g. "Active / In Development", "Production", "Legacy"
    key_technologies TEXT,         -- JSON array
    classified_at TEXT NOT NULL,
    FOREIGN KEY(name_with_owner) REFERENCES repositories(name_with_owner)
);

CREATE INDEX IF NOT EXISTS idx_class_primary ON domain_classifications(primary_domain);
CREATE INDEX IF NOT EXISTS idx_class_confidence ON domain_classifications(confidence_score);
CREATE INDEX IF NOT EXISTS idx_class_owner ON domain_classifications(name_with_owner);


"""


class DatabaseManager:
    def __init__(self, db_path: str = "healthcare_portfolio_catalog.db"):
        self.db_path = Path(db_path).resolve()
        # Ensure parent folder exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")  # Write-Ahead Logging for high-concurrency performance
        conn.execute("PRAGMA synchronous=NORMAL;")
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Initializes tables and indexes."""
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

    def upsert_repository(self, data: Dict[str, Any]) -> None:
        """Insert or update a repository record."""
        now = datetime.utcnow().isoformat() + "Z"
        languages_json = json.dumps(data.get("languages", []))
        topics_json = json.dumps(data.get("topics", []))

        query = """
        INSERT INTO repositories (
            node_id, name, name_with_owner, owner, description, url,
            primary_language, languages, topics, default_branch,
            is_private, is_archived, is_fork, created_at, updated_at,
            pushed_at, disk_usage_kb, open_issues_count, stargazers_count,
            forks_count, has_readme, readme_filename, phase1_status,
            discovered_at, last_synced_at
        ) VALUES (
            :node_id, :name, :name_with_owner, :owner, :description, :url,
            :primary_language, :languages, :topics, :default_branch,
            :is_private, :is_archived, :is_fork, :created_at, :updated_at,
            :pushed_at, :disk_usage_kb, :open_issues_count, :stargazers_count,
            :forks_count, :has_readme, :readme_filename, :phase1_status,
            :discovered_at, :last_synced_at
        )
        ON CONFLICT(name_with_owner) DO UPDATE SET
            node_id = excluded.node_id,
            name = excluded.name,
            owner = excluded.owner,
            description = excluded.description,
            url = excluded.url,
            primary_language = excluded.primary_language,
            languages = excluded.languages,
            topics = excluded.topics,
            default_branch = excluded.default_branch,
            is_private = excluded.is_private,
            is_archived = excluded.is_archived,
            is_fork = excluded.is_fork,
            updated_at = excluded.updated_at,
            pushed_at = excluded.pushed_at,
            disk_usage_kb = excluded.disk_usage_kb,
            open_issues_count = excluded.open_issues_count,
            stargazers_count = excluded.stargazers_count,
            forks_count = excluded.forks_count,
            has_readme = excluded.has_readme,
            readme_filename = excluded.readme_filename,
            last_synced_at = excluded.last_synced_at;
        """

        params = {
            "node_id": data.get("node_id"),
            "name": data.get("name"),
            "name_with_owner": data.get("name_with_owner"),
            "owner": data.get("owner"),
            "description": data.get("description"),
            "url": data.get("url"),
            "primary_language": data.get("primary_language"),
            "languages": languages_json,
            "topics": topics_json,
            "default_branch": data.get("default_branch"),
            "is_private": 1 if data.get("is_private") else 0,
            "is_archived": 1 if data.get("is_archived") else 0,
            "is_fork": 1 if data.get("is_fork") else 0,
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "pushed_at": data.get("pushed_at"),
            "disk_usage_kb": data.get("disk_usage_kb", 0),
            "open_issues_count": data.get("open_issues_count", 0),
            "stargazers_count": data.get("stargazers_count", 0),
            "forks_count": data.get("forks_count", 0),
            "has_readme": 1 if data.get("has_readme") else 0,
            "readme_filename": data.get("readme_filename"),
            "phase1_status": "discovered",
            "discovered_at": now,
            "last_synced_at": now,
        }

        with self.get_connection() as conn:
            conn.execute(query, params)
            conn.commit()

    def batch_upsert_repositories(self, repo_list: List[Dict[str, Any]]) -> int:
        """Batch upsert multiple repositories within a single transaction for maximum speed."""
        now = datetime.utcnow().isoformat() + "Z"
        query = """
        INSERT INTO repositories (
            node_id, name, name_with_owner, owner, description, url,
            primary_language, languages, topics, default_branch,
            is_private, is_archived, is_fork, created_at, updated_at,
            pushed_at, disk_usage_kb, open_issues_count, stargazers_count,
            forks_count, has_readme, readme_filename, phase1_status,
            discovered_at, last_synced_at
        ) VALUES (
            :node_id, :name, :name_with_owner, :owner, :description, :url,
            :primary_language, :languages, :topics, :default_branch,
            :is_private, :is_archived, :is_fork, :created_at, :updated_at,
            :pushed_at, :disk_usage_kb, :open_issues_count, :stargazers_count,
            :forks_count, :has_readme, :readme_filename, :phase1_status,
            :discovered_at, :last_synced_at
        )
        ON CONFLICT(name_with_owner) DO UPDATE SET
            node_id = excluded.node_id,
            name = excluded.name,
            owner = excluded.owner,
            description = excluded.description,
            url = excluded.url,
            primary_language = excluded.primary_language,
            languages = excluded.languages,
            topics = excluded.topics,
            default_branch = excluded.default_branch,
            is_private = excluded.is_private,
            is_archived = excluded.is_archived,
            is_fork = excluded.is_fork,
            updated_at = excluded.updated_at,
            pushed_at = excluded.pushed_at,
            disk_usage_kb = excluded.disk_usage_kb,
            open_issues_count = excluded.open_issues_count,
            stargazers_count = excluded.stargazers_count,
            forks_count = excluded.forks_count,
            has_readme = excluded.has_readme,
            readme_filename = excluded.readme_filename,
            last_synced_at = excluded.last_synced_at;
        """

        params_list = []
        for data in repo_list:
            params_list.append({
                "node_id": data.get("node_id"),
                "name": data.get("name"),
                "name_with_owner": data.get("name_with_owner"),
                "owner": data.get("owner"),
                "description": data.get("description"),
                "url": data.get("url"),
                "primary_language": data.get("primary_language"),
                "languages": json.dumps(data.get("languages", [])),
                "topics": json.dumps(data.get("topics", [])),
                "default_branch": data.get("default_branch"),
                "is_private": 1 if data.get("is_private") else 0,
                "is_archived": 1 if data.get("is_archived") else 0,
                "is_fork": 1 if data.get("is_fork") else 0,
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "pushed_at": data.get("pushed_at"),
                "disk_usage_kb": data.get("disk_usage_kb", 0),
                "open_issues_count": data.get("open_issues_count", 0),
                "stargazers_count": data.get("stargazers_count", 0),
                "forks_count": data.get("forks_count", 0),
                "has_readme": 1 if data.get("has_readme") else 0,
                "readme_filename": data.get("readme_filename"),
                "phase1_status": "discovered",
                "discovered_at": now,
                "last_synced_at": now,
            })

        with self.get_connection() as conn:
            conn.executemany(query, params_list)
            conn.commit()
        return len(params_list)

    def log_rate_limit(self, endpoint: str, limit_total: int, remaining: int, cost: int, reset_at: str) -> None:
        """Keep an audit record of rate limits."""
        now = datetime.utcnow().isoformat() + "Z"
        query = """
        INSERT INTO rate_limit_history (timestamp, endpoint, limit_total, remaining, cost, reset_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            conn.execute(query, (now, endpoint, limit_total, remaining, cost, reset_at))
            conn.commit()

    def start_discovery_run(self, target_type: str, target_owner: str) -> int:
        now = datetime.utcnow().isoformat() + "Z"
        query = """
        INSERT INTO discovery_runs (started_at, target_type, target_owner, status)
        VALUES (?, ?, ?, 'running')
        """
        with self.get_connection() as conn:
            cur = conn.execute(query, (now, target_type, target_owner))
            conn.commit()
            return cur.lastrowid

    def finish_discovery_run(self, run_id: int, total: int, active: int, archived: int, private: int, public: int, notes: str = ""):
        now = datetime.utcnow().isoformat() + "Z"
        query = """
        UPDATE discovery_runs
        SET completed_at = ?, total_discovered = ?, active_count = ?,
            archived_count = ?, private_count = ?, public_count = ?,
            status = 'completed', notes = ?
        WHERE id = ?
        """
        with self.get_connection() as conn:
            conn.execute(query, (now, total, active, archived, private, public, notes, run_id))
            conn.commit()

    def get_summary_stats(self) -> Dict[str, Any]:
        """Returns statistics of the catalog for reporting and Phase 1 completion walkthrough."""
        with self.get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM repositories").fetchone()[0]
            if total == 0:
                return {"total": 0}

            active = conn.execute("SELECT COUNT(*) FROM repositories WHERE is_archived = 0").fetchone()[0]
            archived = conn.execute("SELECT COUNT(*) FROM repositories WHERE is_archived = 1").fetchone()[0]
            private_count = conn.execute("SELECT COUNT(*) FROM repositories WHERE is_private = 1").fetchone()[0]
            public_count = conn.execute("SELECT COUNT(*) FROM repositories WHERE is_private = 0").fetchone()[0]
            with_readme = conn.execute("SELECT COUNT(*) FROM repositories WHERE has_readme = 1").fetchone()[0]

            # Language breakdown
            lang_rows = conn.execute("""
                SELECT primary_language, COUNT(*) as cnt 
                FROM repositories 
                WHERE primary_language IS NOT NULL 
                GROUP BY primary_language 
                ORDER BY cnt DESC LIMIT 10
            """).fetchall()
            languages = {r["primary_language"]: r["cnt"] for r in lang_rows}

            return {
                "total": total,
                "active": active,
                "archived": archived,
                "private": private_count,
                "public": public_count,
                "with_readme": with_readme,
                "readme_ratio_pct": round((with_readme / total) * 100, 1) if total else 0,
                "top_languages": languages,
            }

    def get_all_repositories(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM repositories ORDER BY pushed_at DESC").fetchall()
            result = []
            for r in rows:
                item = dict(r)
                item["languages"] = json.loads(item["languages"]) if item["languages"] else []
                item["topics"] = json.loads(item["topics"]) if item["topics"] else []
                result.append(item)
            return result

    def get_pending_dossier_repositories(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns repositories from the catalog that do not yet have an extracted dossier."""
        query = """
        SELECT r.* FROM repositories r
        LEFT JOIN repo_dossiers d ON r.name_with_owner = d.name_with_owner
        WHERE d.id IS NULL
        ORDER BY r.pushed_at DESC
        """
        if limit:
            query += f" LIMIT {int(limit)}"
        
        with self.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            result = []
            for r in rows:
                item = dict(r)
                item["languages"] = json.loads(item["languages"]) if item["languages"] else []
                item["topics"] = json.loads(item["topics"]) if item["topics"] else []
                result.append(item)
            return result

    def upsert_dossier(self, data: Dict[str, Any]) -> None:
        """Insert or replace a repository synthesis dossier."""
        now = datetime.utcnow().isoformat() + "Z"
        query = """
        INSERT INTO repo_dossiers (
            repo_name, name_with_owner, default_branch,
            priority_files_count, priority_files_list, extracted_entities,
            extracted_dependencies, extracted_apis, dossier_markdown,
            dossier_size_bytes, extracted_at
        ) VALUES (
            :repo_name, :name_with_owner, :default_branch,
            :priority_files_count, :priority_files_list, :extracted_entities,
            :extracted_dependencies, :extracted_apis, :dossier_markdown,
            :dossier_size_bytes, :extracted_at
        )
        ON CONFLICT(name_with_owner) DO UPDATE SET
            default_branch = excluded.default_branch,
            priority_files_count = excluded.priority_files_count,
            priority_files_list = excluded.priority_files_list,
            extracted_entities = excluded.extracted_entities,
            extracted_dependencies = excluded.extracted_dependencies,
            extracted_apis = excluded.extracted_apis,
            dossier_markdown = excluded.dossier_markdown,
            dossier_size_bytes = excluded.dossier_size_bytes,
            extracted_at = excluded.extracted_at;
        """
        params = {
            "repo_name": data.get("repo_name"),
            "name_with_owner": data.get("name_with_owner"),
            "default_branch": data.get("default_branch"),
            "priority_files_count": data.get("priority_files_count", 0),
            "priority_files_list": json.dumps(data.get("priority_files_list", [])),
            "extracted_entities": json.dumps(data.get("extracted_entities", [])),
            "extracted_dependencies": json.dumps(data.get("extracted_dependencies", [])),
            "extracted_apis": json.dumps(data.get("extracted_apis", [])),
            "dossier_markdown": data.get("dossier_markdown", ""),
            "dossier_size_bytes": len(data.get("dossier_markdown", "").encode("utf-8")),
            "extracted_at": now,
        }
        with self.get_connection() as conn:
            conn.execute(query, params)
            conn.execute(
                "UPDATE repositories SET phase1_status = 'dossier_extracted' WHERE name_with_owner = ?",
                (data.get("name_with_owner"),)
            )
            conn.commit()

    def get_dossier(self, name_with_owner: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM repo_dossiers WHERE name_with_owner = ?",
                (name_with_owner,)
            ).fetchone()
            if not row:
                return None
            res = dict(row)
            res["priority_files_list"] = json.loads(res["priority_files_list"]) if res["priority_files_list"] else []
            res["extracted_entities"] = json.loads(res["extracted_entities"]) if res["extracted_entities"] else []
            res["extracted_dependencies"] = json.loads(res["extracted_dependencies"]) if res["extracted_dependencies"] else []
            res["extracted_apis"] = json.loads(res["extracted_apis"]) if res["extracted_apis"] else []
            return res

    def get_dossier_stats(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            total_dossiers = conn.execute("SELECT COUNT(*) FROM repo_dossiers").fetchone()[0]
            if total_dossiers == 0:
                return {"total_dossiers": 0}
            
            avg_size = conn.execute("SELECT AVG(dossier_size_bytes) FROM repo_dossiers").fetchone()[0]
            max_size = conn.execute("SELECT MAX(dossier_size_bytes) FROM repo_dossiers").fetchone()[0]
            total_priority_files = conn.execute("SELECT SUM(priority_files_count) FROM repo_dossiers").fetchone()[0]
            
            return {
                "total_dossiers": total_dossiers,
                "avg_size_kb": round((avg_size or 0) / 1024, 2),
                "max_size_kb": round((max_size or 0) / 1024, 2),
                "total_priority_files_analyzed": total_priority_files or 0,
            }

    def upsert_classification(self, data: Dict[str, Any]) -> None:
        """Insert or replace a domain classification result."""
        now = datetime.utcnow().isoformat() + "Z"
        query = """
        INSERT INTO domain_classifications (
            repo_name, name_with_owner, primary_domain, secondary_domains,
            confidence_score, domain_justification, detected_standards,
            project_status, key_technologies, classified_at
        ) VALUES (
            :repo_name, :name_with_owner, :primary_domain, :secondary_domains,
            :confidence_score, :domain_justification, :detected_standards,
            :project_status, :key_technologies, :classified_at
        )
        ON CONFLICT(name_with_owner) DO UPDATE SET
            primary_domain = excluded.primary_domain,
            secondary_domains = excluded.secondary_domains,
            confidence_score = excluded.confidence_score,
            domain_justification = excluded.domain_justification,
            detected_standards = excluded.detected_standards,
            project_status = excluded.project_status,
            key_technologies = excluded.key_technologies,
            classified_at = excluded.classified_at;
        """
        params = {
            "repo_name": data.get("repo_name"),
            "name_with_owner": data.get("name_with_owner"),
            "primary_domain": data.get("primary_domain"),
            "secondary_domains": json.dumps(data.get("secondary_domains", [])),
            "confidence_score": float(data.get("confidence_score", 0.0)),
            "domain_justification": data.get("domain_justification", ""),
            "detected_standards": json.dumps(data.get("detected_standards", [])),
            "project_status": data.get("project_status", "Active"),
            "key_technologies": json.dumps(data.get("key_technologies", [])),
            "classified_at": now,
        }
        with self.get_connection() as conn:
            conn.execute(query, params)
            conn.execute(
                "UPDATE repositories SET phase1_status = 'classified' WHERE name_with_owner = ?",
                (data.get("name_with_owner"),)
            )
            conn.commit()

    def get_classification(self, name_with_owner: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM domain_classifications WHERE name_with_owner = ?",
                (name_with_owner,)
            ).fetchone()
            if not row:
                return None
            res = dict(row)
            res["secondary_domains"] = json.loads(res["secondary_domains"]) if res["secondary_domains"] else []
            res["detected_standards"] = json.loads(res["detected_standards"]) if res["detected_standards"] else []
            res["key_technologies"] = json.loads(res["key_technologies"]) if res["key_technologies"] else []
            return res

    def get_all_classifications(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT c.*, r.description, r.primary_language, r.pushed_at, r.is_archived, r.is_private
                FROM domain_classifications c
                LEFT JOIN repositories r ON c.name_with_owner = r.name_with_owner
                ORDER BY c.confidence_score DESC
            """).fetchall()
            result = []
            for r in rows:
                item = dict(r)
                item["secondary_domains"] = json.loads(item["secondary_domains"]) if item["secondary_domains"] else []
                item["detected_standards"] = json.loads(item["detected_standards"]) if item["detected_standards"] else []
                item["key_technologies"] = json.loads(item["key_technologies"]) if item["key_technologies"] else []
                result.append(item)
            return result

    def get_domain_distribution(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            primary_counts = conn.execute("""
                SELECT primary_domain, COUNT(*) as cnt, AVG(confidence_score) as avg_conf
                FROM domain_classifications
                GROUP BY primary_domain
                ORDER BY cnt DESC
            """).fetchall()
            
            total_classified = conn.execute("SELECT COUNT(*) FROM domain_classifications").fetchone()[0]

            return {
                "total_classified": total_classified,
                "domains": [
                    {
                        "domain": row["primary_domain"],
                        "count": row["cnt"],
                        "avg_confidence": round(row["avg_conf"] or 0.0, 2)
                    }
                    for row in primary_counts
                ]
            }

