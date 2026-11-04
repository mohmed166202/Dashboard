"""
Main CLI entrypoint for Phase 2: Targeted Asynchronous Document & Asset Extraction.
Usage:
    python run_phase2.py
    python run_phase2.py --limit 10
    python run_phase2.py --repo "MyOrg/his-patient-service"
    python run_phase2.py --workers 12
"""

import argparse
import sys
from pathlib import Path

from config import Config
from extractor import Phase2ExtractorOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="Phase 2: Targeted Asynchronous Document & Asset Extraction for Healthcare Portfolios"
    )
    parser.add_argument(
        "--repo",
        type=str,
        default=None,
        help="Filter and extract a specific repository (name or name_with_owner)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of repositories to process (e.g. for testing)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Number of concurrent repository extraction workers (default: 8)"
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="GitHub Personal Access Token (overrides .env)"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help="Custom SQLite catalog database path"
    )

    args = parser.parse_args()

    effective_token = args.token or Config.GITHUB_TOKEN
    if not effective_token or effective_token == "your_github_token_here":
        print("\n" + "=" * 65)
        print("[!] GITHUB_PERSONAL_ACCESS_TOKEN NOT CONFIGURED")
        print("=" * 65)
        print("Please configure your token in the '.env' file or pass via --token.")
        sys.exit(1)

    orchestrator = Phase2ExtractorOrchestrator(
        db_path=args.db or Config.DATABASE_PATH,
        token=effective_token,
        max_workers=args.workers
    )

    result = orchestrator.run_all(
        limit=args.limit,
        repo_filter=args.repo
    )

    if result.get("status") == "empty":
        print("\n[!] Please run Phase 1 first to discover repositories:")
        print("    python run_phase1.py\n")


if __name__ == "__main__":
    main()

