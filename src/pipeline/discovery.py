"""
Phase 1 Orchestrator: High-Speed Discovery & Repository Cataloging.
Enumerates all repositories across the target account/organization, harvests
metadata, tracks rate limits, and persists into the local SQLite catalog.
"""

import logging
import sys
import time
from typing import Any, Dict, Optional

from config import Config
from db import DatabaseManager
from github_client import GitHubClient

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Phase1Discovery")


class Phase1DiscoveryOrchestrator:
    def __init__(self, db_path: Optional[str] = None, token: Optional[str] = None):
        self.db = DatabaseManager(db_path or Config.DATABASE_PATH)
        self.token = token or Config.GITHUB_TOKEN
        self.client = GitHubClient(token=self.token, db=self.db)

    def run(
        self,
        target_type: Optional[str] = None,
        target_owner: Optional[str] = None,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        Executes Phase 1 discovery:
        1. Validates auth credentials and prints user identity & rate limits.
        2. Initiates catalog audit in SQLite.
        3. Paginates through all repos (100 per batch) via GraphQL.
        4. Batch upserts records to SQLite.
        5. Computes completion analytics and summary.
        """
        start_time = time.time()
        logger.info("==================================================================")
        logger.info("PHASE 1: HIGH-SPEED DISCOVERY & REPOSITORY CATALOGING")
        logger.info("==================================================================")

        # 1. Verify Authentication & Scopes
        try:
            auth_info = self.client.check_auth()
            logger.info(f"Authenticated as GitHub User: {auth_info['login']} ({auth_info.get('name') or 'N/A'})")
            logger.info(f"Token Scopes: {', '.join(auth_info['scopes']) or 'None specified'}")
            logger.info(f"GitHub Rate Limit Remaining: {auth_info['rate_remaining']} / {auth_info['rate_limit']}")
        except PermissionError as e:
            logger.error(f"Authentication Failed: {e}")
            logger.error("Please add a valid GITHUB_PERSONAL_ACCESS_TOKEN into .env")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"GitHub connection test failed: {e}")
            return {"status": "error", "message": str(e)}

        effective_type = (target_type or Config.GITHUB_TARGET_TYPE).lower()
        effective_owner = target_owner or Config.GITHUB_TARGET_OWNER
        logger.info(f"Discovery Mode: Type='{effective_type}', Target Owner='{effective_owner or '(authenticated viewer)'}'")

        # 2. Record run in DB
        run_id = self.db.start_discovery_run(effective_type, effective_owner)

        # 3. Stream and persist batches
        total_discovered = 0
        batch_count = 0

        try:
            for batch in self.client.fetch_all_repositories(
                target_type=effective_type,
                target_owner=effective_owner,
                page_size=page_size
            ):
                batch_count += 1
                if batch:
                    inserted = self.db.batch_upsert_repositories(batch)
                    total_discovered += inserted
                    logger.info(f"Saved batch {batch_count} ({inserted} repos) into catalog. Cumulative: {total_discovered} repos.")
        except Exception as e:
            logger.error(f"Discovery interrupted by error: {e}", exc_info=True)
            self.db.finish_discovery_run(run_id, total_discovered, 0, 0, 0, 0, notes=f"Error: {e}")
            return {"status": "failed", "error": str(e), "total_discovered": total_discovered}

        duration = time.time() - start_time

        # 4. Gather summary statistics
        stats = self.db.get_summary_stats()
        self.db.finish_discovery_run(
            run_id=run_id,
            total=stats.get("total", 0),
            active=stats.get("active", 0),
            archived=stats.get("archived", 0),
            private=stats.get("private", 0),
            public=stats.get("public", 0),
            notes=f"Completed in {duration:.2f}s across {batch_count} batches."
        )

        logger.info("==================================================================")
        logger.info(f"PHASE 1 COMPLETE in {duration:.2f} seconds!")
        logger.info(f"Total Repositories Discovered: {stats.get('total', 0)}")
        logger.info(f"  - Active: {stats.get('active', 0)}")
        logger.info(f"  - Archived: {stats.get('archived', 0)}")
        logger.info(f"  - Private: {stats.get('private', 0)}")
        logger.info(f"  - Public: {stats.get('public', 0)}")
        logger.info(f"  - Has README: {stats.get('with_readme', 0)} ({stats.get('readme_ratio_pct', 0)}%)")
        logger.info(f"Top Primary Languages: {stats.get('top_languages', {})}")
        logger.info(f"Catalog Database: {self.db.db_path}")
        logger.info("==================================================================")

        return {
            "status": "success",
            "duration_seconds": round(duration, 2),
            "batches_processed": batch_count,
            "stats": stats,
            "catalog_path": str(self.db.db_path),
        }

