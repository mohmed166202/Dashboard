"""
Main CLI entrypoint for Phase 3: Semantic Embeddings & Multi-Label LLM Domain Classifier.
Usage:
    python run_phase3.py
    python run_phase3.py --limit 10
    python run_phase3.py --offline
    python run_phase3.py --repo "his-emr-core"
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import Config
from db import DatabaseManager
from hybrid_classifier import HybridClassifier

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Phase3Runner")


def export_classifications(classifications: List[Dict[str, Any]], out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Export JSON
    json_path = out_dir / "domain_classifications.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(classifications, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved full JSON classifications: {json_path}")

    # 2. Export CSV Matrix
    csv_path = out_dir / "domain_matrix.csv"
    fieldnames = [
        "repo_name", "name_with_owner", "primary_domain", "secondary_domains",
        "confidence_score", "detected_standards", "project_status",
        "key_technologies", "domain_justification"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for c in classifications:
            row = dict(c)
            row["secondary_domains"] = ", ".join(row.get("secondary_domains", []))
            row["detected_standards"] = ", ".join(row.get("detected_standards", []))
            row["key_technologies"] = ", ".join(row.get("key_technologies", []))
            writer.writerow(row)
    logger.info(f"Saved Domain Matrix CSV: {csv_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Phase 3: Semantic Embeddings & Multi-Label LLM Domain Classifier"
    )
    parser.add_argument(
        "--repo",
        type=str,
        default=None,
        help="Classify a specific repository"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of dossiers to classify"
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Force offline mode (uses Rule + Vector space profiling without calling LLM API)"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help="Custom SQLite catalog database path"
    )

    args = parser.parse_args()

    db = DatabaseManager(args.db or Config.DATABASE_PATH)
    classifier = HybridClassifier()

    logger.info("==================================================================")
    logger.info("PHASE 3: SEMANTIC EMBEDDINGS & MULTI-LABEL DOMAIN CLASSIFIER")
    logger.info(f"LLM Provider: {'Gemini API (' + Config.GEMINI_MODEL + ')' if Config.GEMINI_API_KEY and not args.offline else 'Deterministic Rule+Vector Engine'}")
    logger.info("==================================================================")

    # Fetch dossiers from database
    with db.get_connection() as conn:
        query = "SELECT * FROM repo_dossiers"
        if args.repo:
            query += f" WHERE name_with_owner LIKE '%{args.repo}%' OR repo_name LIKE '%{args.repo}%'"
        query += " ORDER BY id ASC"
        if args.limit:
            query += f" LIMIT {int(args.limit)}"

        rows = conn.execute(query).fetchall()

    if not rows:
        print("\n[!] No dossiers found in catalog to classify.")
        print("Please run Phase 2 first to generate dossiers:")
        print("    python run_phase2.py\n")
        return

    logger.info(f"Classifying {len(rows)} repository dossiers against the 9 Healthcare Domains...")

    start_time = time.time()
    results = []

    for idx, row in enumerate(rows, 1):
        item = dict(row)
        item["extracted_entities"] = json.loads(item["extracted_entities"]) if item.get("extracted_entities") else []
        item["extracted_dependencies"] = json.loads(item["extracted_dependencies"]) if item.get("extracted_dependencies") else []
        item["extracted_apis"] = json.loads(item["extracted_apis"]) if item.get("extracted_apis") else []

        classification = classifier.classify(item, force_offline=args.offline)
        db.upsert_classification(classification)
        results.append(classification)

        logger.info(
            f"[{idx}/{len(rows)}] {classification['name_with_owner']} -> "
            f"Domain: [{classification['primary_domain']}] "
            f"(Conf: {classification['confidence_score']:.2f}, Standards: {classification['detected_standards']})"
        )

    duration = time.time() - start_time
    dist = db.get_domain_distribution()

    # Export deliverables
    out_dir = Path("./output").resolve()
    export_classifications(results, out_dir)

    # Print Summary Report
    print("\n" + "=" * 70)
    print(f"PHASE 3 COMPLETE: {len(results)} REPOSITORIES CLASSIFIED ({duration:.2f}s)")
    print("=" * 70)
    print(f"{'DOMAIN':<30} | {'REPOS':<8} | {'AVG CONFIDENCE'}")
    print("-" * 70)
    for d in dist.get("domains", []):
        print(f"{d['domain']:<30} | {d['count']:<8} | {d['avg_confidence'] * 100:.1f}%")
    print("=" * 70)
    print(f"Deliverables exported to: {out_dir}")
    print("  - output/domain_classifications.json")
    print("  - output/domain_matrix.csv\n")


if __name__ == "__main__":
    main()

