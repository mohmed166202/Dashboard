"""
Main CLI entrypoint for Phase 1: High-Speed Discovery & Repository Cataloging.
Usage:
    python run_phase1.py
    python run_phase1.py --target-type org --owner MyHospitalOrg
    python run_phase1.py --export-csv repos.csv
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

from config import Config
from db import DatabaseManager
from discovery import Phase1DiscoveryOrchestrator


def export_catalog_to_csv(db: DatabaseManager, output_csv_path: str):
    repos = db.get_all_repositories()
    if not repos:
        print("[!] No repositories found in catalog to export.")
        return

    fieldnames = [
        "name", "name_with_owner", "owner", "primary_language",
        "is_private", "is_archived", "has_readme", "pushed_at",
        "open_issues_count", "stargazers_count", "disk_usage_kb",
        "topics", "url", "description"
    ]

    path = Path(output_csv_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in repos:
            # Flatten topics list for CSV
            r_copy = dict(r)
            if isinstance(r_copy.get("topics"), list):
                r_copy["topics"] = ", ".join(r_copy["topics"])
            writer.writerow(r_copy)

    print(f"[EXPORT] Successfully exported {len(repos)} repositories to CSV: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Phase 1: High-Speed Discovery & Repository Cataloging for 150+ Healthcare Repositories"
    )
    parser.add_argument(
        "--target-type",
        choices=["viewer", "org", "user"],
        default=None,
        help="Target scope: 'viewer' (all repos accessible to your token), 'org' (GitHub Organization), or 'user'"
    )
    parser.add_argument(
        "--owner",
        type=str,
        default=None,
        help="GitHub organization or user handle (if target-type is org or user)"
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="GitHub Personal Access Token (overrides .env)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="GraphQL pagination batch size (default: 100)"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help="Custom SQLite catalog database path"
    )
    parser.add_argument(
        "--export-csv",
        type=str,
        default=None,
        help="Optional path to export discovered repositories to a CSV spreadsheet"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only verify credentials and connectivity without running cataloging"
    )

    args = parser.parse_args()

    # If --check-only is specified, delegate to test_credentials
    if args.check_only:
        from test_credentials import main as test_creds_main
        test_creds_main()
        return

    # Check token presence
    effective_token = args.token or Config.GITHUB_TOKEN
    if not effective_token or effective_token == "your_github_token_here":
        print("\n" + "=" * 65)
        print("[!] GITHUB_PERSONAL_ACCESS_TOKEN NOT CONFIGURED")
        print("=" * 65)
        print("To proceed with Phase 1:")
        print("1. Open the '.env' file in this folder:")
        print(f"   {Path('.env').resolve()}")
        print("2. Set your GitHub token:")
        print("   GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx")
        print("3. (Optional) Set target organization if applicable:")
        print("   GITHUB_TARGET_TYPE=org")
        print("   GITHUB_TARGET_OWNER=YourOrgName")
        print("\nOr pass it directly in the terminal:")
        print("   python run_phase1.py --token ghp_xxxx\n")
        sys.exit(1)

    orchestrator = Phase1DiscoveryOrchestrator(
        db_path=args.db or Config.DATABASE_PATH,
        token=effective_token
    )

    result = orchestrator.run(
        target_type=args.target_type,
        target_owner=args.owner,
        page_size=args.batch_size
    )

    if result.get("status") == "success":
        # Export default CSV into output folder
        default_csv = Path("./output/discovered_repositories.csv")
        export_catalog_to_csv(orchestrator.db, str(default_csv))

        if args.export_csv:
            export_catalog_to_csv(orchestrator.db, args.export_csv)


if __name__ == "__main__":
    main()

