"""
Phase 2 Orchestrator: Targeted Asynchronous Document & Asset Extraction.
Processes 150+ repositories concurrently, querying recursive git trees,
extracting prioritized docs, schemas, and dependencies, and compiling
Project Synthesis Dossiers (<100KB markdown).
"""

import concurrent.futures
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import requests

from config import Config
from content_extractor import ContentExtractor
from db import DatabaseManager
from dossier_builder import DossierBuilder
from tree_scanner import TreeScanner

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Phase2Extractor")


class Phase2ExtractorOrchestrator:
    def __init__(self, db_path: Optional[str] = None, token: Optional[str] = None, max_workers: int = 8):
        self.db = DatabaseManager(db_path or Config.DATABASE_PATH)
        self.token = token or Config.GITHUB_TOKEN
        self.max_workers = max_workers
        self.output_dir = Path("./output/dossiers").resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_tree(self, session: requests.Session, owner: str, repo: str, branch: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch git tree recursively in a single request."""
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("tree", [])
            elif resp.status_code == 404:
                logger.warning(f"Repository {owner}/{repo} (branch {branch}) tree not found or empty.")
            elif resp.status_code == 409:
                logger.warning(f"Repository {owner}/{repo} is empty (Git 409 Conflict).")
            else:
                logger.warning(f"Tree fetch returned HTTP {resp.status_code} for {owner}/{repo}: {resp.text[:200]}")
        except Exception as e:
            logger.error(f"Error fetching tree for {owner}/{repo}: {e}")
        return None

    def process_single_repo(self, repo: Dict[str, Any], session: Optional[requests.Session] = None) -> Dict[str, Any]:
        """
        Extracts documentation, schemas, dependencies, and compiles dossier for a single repository.
        """
        owner = repo["owner"]
        repo_name = repo["name"]
        name_with_owner = repo["name_with_owner"]
        default_branch = repo.get("default_branch") or "main"

        logger.info(f"[{name_with_owner}] Starting Phase 2 targeted extraction...")

        sess = session or requests.Session()
        if self.token:
            sess.headers.update({
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "Healthcare-Portfolio-Extractor/1.0"
            })

        extractor = ContentExtractor(session=sess, token=self.token)

        # 1. Fetch Recursive Git Tree
        tree_nodes = self._get_tree(sess, owner, repo_name, default_branch)
        if tree_nodes is None and default_branch != "master":
            # Retry with 'master' fallback branch
            tree_nodes = self._get_tree(sess, owner, repo_name, "master")
            if tree_nodes:
                default_branch = "master"

        if not tree_nodes:
            logger.warning(f"[{name_with_owner}] No files in tree. Generating minimal dossier.")
            dossier_md = DossierBuilder.build_dossier(
                repo_metadata=repo,
                doc_contents=[],
                spec_contents=[],
                dependencies=[],
                database_tables=[],
                detected_entities=set(),
                detected_apis=[],
                priority_files_inspected=[]
            )
            dossier_record = {
                "repo_name": repo_name,
                "name_with_owner": name_with_owner,
                "default_branch": default_branch,
                "priority_files_count": 0,
                "priority_files_list": [],
                "extracted_entities": [],
                "extracted_dependencies": [],
                "extracted_apis": [],
                "dossier_markdown": dossier_md
            }
            self.db.upsert_dossier(dossier_record)
            return dossier_record

        # 2. Filter Priority Tiers
        categorized = TreeScanner.filter_tree(tree_nodes)
        p1_files = categorized.get(1, [])
        p2_files = categorized.get(2, [])
        p3_files = categorized.get(3, [])
        p4_files = categorized.get(4, [])

        inspected_paths = [f["path"] for f in (p1_files + p2_files + p3_files + p4_files)]
        logger.info(f"[{name_with_owner}] Tree scanned: {len(tree_nodes)} total objects. Target priority files: {len(inspected_paths)} (P1:{len(p1_files)}, P2:{len(p2_files)}, P3:{len(p3_files)}, P4:{len(p4_files)})")

        all_detected_entities: Set[str] = set()
        # Also check repo topics and description
        if repo.get("description"):
            all_detected_entities.update(extractor.extract_entities_from_text(repo["description"]))
        for t in repo.get("topics", []):
            all_detected_entities.update(extractor.extract_entities_from_text(t))

        # 3. Extract Priority 1: Docs & READMEs
        doc_contents = []
        for f in p1_files:
            c = extractor.fetch_file_content(owner, repo_name, default_branch, f)
            if c:
                doc_contents.append({"path": f["path"], "content": c})
                all_detected_entities.update(extractor.extract_entities_from_text(c))

        # 4. Extract Priority 2: Specs, ADRs & APIs
        spec_contents = []
        detected_apis = []
        for f in p2_files:
            c = extractor.fetch_file_content(owner, repo_name, default_branch, f)
            if c:
                spec_contents.append({"path": f["path"], "content": c})
                apis = extractor.extract_api_specs(f["path"], c)
                detected_apis.extend(apis)
                all_detected_entities.update(extractor.extract_entities_from_text(c))

        # 5. Extract Priority 3: Dependencies & Configs
        all_dependencies = []
        for f in p3_files:
            c = extractor.fetch_file_content(owner, repo_name, default_branch, f)
            if c:
                deps = extractor.extract_dependencies(f["path"], c)
                all_dependencies.extend(deps)
                all_detected_entities.update(extractor.extract_entities_from_text(c))

        # 6. Extract Priority 4: Database Schemas & Models
        database_tables = []
        for f in p4_files:
            c = extractor.fetch_file_content(owner, repo_name, default_branch, f)
            if c:
                tables = extractor.extract_database_tables(f["path"], c)
                database_tables.extend(tables)
                all_detected_entities.update(extractor.extract_entities_from_text(c))

        # Deduplicate
        all_dependencies = sorted(list(set(all_dependencies)))
        database_tables = sorted(list(set(database_tables)))
        detected_apis = sorted(list(set(detected_apis)))

        # 7. Build Project Synthesis Dossier (<100KB)
        dossier_md = DossierBuilder.build_dossier(
            repo_metadata=repo,
            doc_contents=doc_contents,
            spec_contents=spec_contents,
            dependencies=all_dependencies,
            database_tables=database_tables,
            detected_entities=all_detected_entities,
            detected_apis=detected_apis,
            priority_files_inspected=inspected_paths
        )

        dossier_record = {
            "repo_name": repo_name,
            "name_with_owner": name_with_owner,
            "default_branch": default_branch,
            "priority_files_count": len(inspected_paths),
            "priority_files_list": inspected_paths,
            "extracted_entities": sorted(list(all_detected_entities)),
            "extracted_dependencies": all_dependencies,
            "extracted_apis": detected_apis,
            "dossier_markdown": dossier_md
        }

        # Save to SQLite
        self.db.upsert_dossier(dossier_record)

        # Save standalone markdown file to output/dossiers/
        safe_filename = name_with_owner.replace("/", "__") + ".md"
        out_path = self.output_dir / safe_filename
        out_path.write_text(dossier_md, encoding="utf-8")

        size_kb = round(len(dossier_md.encode("utf-8")) / 1024, 2)
        logger.info(f"[{name_with_owner}] Dossier generated successfully: {size_kb} KB. Saved to DB & {out_path.name}")

        return dossier_record

    def run_all(self, limit: Optional[int] = None, repo_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs Phase 2 extraction across all discovered repositories in parallel.
        """
        start_time = time.time()
        logger.info("==================================================================")
        logger.info("PHASE 2: TARGETED ASYNCHRONOUS DOCUMENT & ASSET EXTRACTION")
        logger.info(f"Max Concurrent Workers: {self.max_workers}")
        logger.info("==================================================================")

        all_repos = self.db.get_all_repositories()
        if not all_repos:
            logger.warning("No repositories found in catalog. Please run Phase 1 first (python run_phase1.py)")
            return {"status": "empty", "message": "No repositories in database. Run Phase 1 first."}

        # Filter if requested
        if repo_filter:
            target_repos = [r for r in all_repos if repo_filter.lower() in r["name_with_owner"].lower()]
        else:
            target_repos = all_repos

        if limit:
            target_repos = target_repos[:limit]

        total_to_process = len(target_repos)
        logger.info(f"Repositories queued for targeted extraction: {total_to_process}")

        completed_count = 0
        failed_count = 0

        # Execute concurrently across worker pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.process_single_repo, repo): repo for repo in target_repos}
            for future in concurrent.futures.as_completed(futures):
                repo = futures[future]
                try:
                    future.result()
                    completed_count += 1
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed processing {repo['name_with_owner']}: {e}", exc_info=True)

        duration = time.time() - start_time
        stats = self.db.get_dossier_stats()

        logger.info("==================================================================")
        logger.info(f"PHASE 2 COMPLETE in {duration:.2f} seconds!")
        logger.info(f"Dossiers Generated: {completed_count} (Failed: {failed_count})")
        logger.info(f"Total Dossiers in DB: {stats.get('total_dossiers', 0)}")
        logger.info(f"Average Dossier Size: {stats.get('avg_size_kb', 0)} KB (< 100 KB target)")
        logger.info(f"Max Dossier Size: {stats.get('max_size_kb', 0)} KB")
        logger.info(f"Total Priority Files Analyzed: {stats.get('total_priority_files_analyzed', 0)}")
        logger.info(f"Markdown Dossiers Directory: {self.output_dir}")
        logger.info("==================================================================")

        return {
            "status": "success",
            "duration_seconds": round(duration, 2),
            "completed": completed_count,
            "failed": failed_count,
            "dossier_stats": stats,
            "output_directory": str(self.output_dir)
        }

