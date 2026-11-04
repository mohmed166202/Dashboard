"""
Incremental Sync Engine for Phase 5.
Synchronizes a single repository through Phases 1, 2, 3, and updates Phase 4 deliverables
without having to re-scan the entire 150+ repository portfolio.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import requests

from config import Config
from dashboard_generator import DashboardGenerator
from db import DatabaseManager
from extractor import Phase2ExtractorOrchestrator
from github_client import GitHubClient
from hybrid_classifier import HybridClassifier
from portfolio_synthesis import PortfolioSynthesizer
from report_generator import ReportGenerator

logger = logging.getLogger("IncrementalSync")


class IncrementalSyncEngine:
    def __init__(self, db_path: Optional[str] = None, token: Optional[str] = None):
        self.db = DatabaseManager(db_path or Config.DATABASE_PATH)
        self.token = token or Config.GITHUB_TOKEN
        self.client = GitHubClient(token=self.token, db=self.db)
        self.extractor = Phase2ExtractorOrchestrator(db_path=db_path, token=self.token, max_workers=1)
        self.classifier = HybridClassifier(gemini_api_key=Config.GEMINI_API_KEY)
        self.synthesizer = PortfolioSynthesizer(db_path=db_path)

    def fetch_repo_metadata(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Fetch real-time metadata for a single repository via REST API."""
        url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "Healthcare-Incremental-Sync/1.0",
            "Accept": "application/vnd.github.v3+json"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "node_id": data.get("node_id"),
                    "name": data.get("name"),
                    "name_with_owner": data.get("full_name"),
                    "owner": data.get("owner", {}).get("login"),
                    "description": data.get("description"),
                    "url": data.get("html_url"),
                    "primary_language": data.get("language"),
                    "languages": [data.get("language")] if data.get("language") else [],
                    "topics": data.get("topics", []),
                    "default_branch": data.get("default_branch") or "main",
                    "is_private": data.get("private", False),
                    "is_archived": data.get("archived", False),
                    "is_fork": data.get("fork", False),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "pushed_at": data.get("pushed_at"),
                    "disk_usage_kb": data.get("size", 0),
                    "open_issues_count": data.get("open_issues_count", 0),
                    "stargazers_count": data.get("stargazers_count", 0),
                    "forks_count": data.get("forks_count", 0),
                    "has_readme": 1,
                    "readme_filename": "README.md"
                }
            else:
                logger.warning(f"Failed to fetch repo {owner}/{repo}: HTTP {resp.status_code}")
        except Exception as e:
            logger.error(f"Error fetching {owner}/{repo}: {e}")
        return None

    def sync_repository(self, name_with_owner: str, regenerate_dashboard: bool = True) -> Dict[str, Any]:
        """
        Executes end-to-end incremental synchronization for a single repository:
          Step 1: Update repository catalog entry (Phase 1)
          Step 2: Targeted tree extraction & dossier generation (Phase 2)
          Step 3: Multi-label healthcare domain classification (Phase 3)
          Step 4: Regenerate interactive dashboard & executive reports (Phase 4)
        """
        parts = name_with_owner.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid repository full name: '{name_with_owner}'. Expected format: 'owner/repo'")

        owner, repo_name = parts[0], parts[1]
        logger.info(f"[INCREMENTAL SYNC] Starting sync for '{name_with_owner}'...")

        # 1. Update Catalog
        repo_data = self.fetch_repo_metadata(owner, repo_name)
        if not repo_data:
            # Fallback to local DB record if exists
            with self.db.get_connection() as conn:
                row = conn.execute("SELECT * FROM repositories WHERE name_with_owner = ?", (name_with_owner,)).fetchone()
                if row:
                    repo_data = dict(row)
                    repo_data["languages"] = json.loads(repo_data["languages"]) if repo_data.get("languages") else []
                    repo_data["topics"] = json.loads(repo_data["topics"]) if repo_data.get("topics") else []
        
        if not repo_data:
            raise RuntimeError(f"Repository '{name_with_owner}' not found on GitHub or in local catalog.")

        self.db.upsert_repository(repo_data)
        logger.info(f"[{name_with_owner}] Catalog metadata updated in SQLite.")

        # 2. Targeted Extraction & Dossier Generation
        dossier_record = self.extractor.process_single_repo(repo_data)
        logger.info(f"[{name_with_owner}] Priority assets extracted. Dossier size: {len(dossier_record['dossier_markdown'])} bytes.")

        # 3. Domain Classification
        classification = self.classifier.classify(dossier_record)
        self.db.upsert_classification(classification)
        logger.info(f"[{name_with_owner}] Re-classified as [{classification['primary_domain']}] (Confidence: {classification['confidence_score']})")

        # 4. Regenerate Phase 4 Deliverables
        if regenerate_dashboard:
            synthesis_data = self.synthesizer.synthesize()
            out_base = Path("./output").resolve()
            dashboard_path = out_base / "dashboard" / "index.html"
            report_path = out_base / "reports" / "EXECUTIVE_HEALTHCARE_PORTFOLIO_REPORT.md"
            synthesis_path = out_base / "reports" / "portfolio_synthesis.json"
            graph_path = out_base / "reports" / "portfolio_graph.json"

            DashboardGenerator.generate_html(synthesis_data, str(dashboard_path))
            ReportGenerator.generate_markdown_report(synthesis_data, str(report_path))
            with open(synthesis_path, "w", encoding="utf-8") as f:
                json.dump(synthesis_data, f, indent=2, ensure_ascii=False)
            with open(graph_path, "w", encoding="utf-8") as f:
                json.dump(synthesis_data.get("graph", {}), f, indent=2, ensure_ascii=False)
            logger.info("[INCREMENTAL SYNC] Dashboard and Executive Reports refreshed successfully.")

        return {
            "status": "success",
            "name_with_owner": name_with_owner,
            "primary_domain": classification["primary_domain"],
            "secondary_domains": classification.get("secondary_domains", []),
            "confidence_score": classification["confidence_score"],
            "detected_standards": classification.get("detected_standards", []),
            "synced_at": datetime.utcnow().isoformat() + "Z"
        }

