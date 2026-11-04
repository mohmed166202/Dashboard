"""
Main CLI entrypoint for Phase 5: Automated Sync & Webhook Integration.
Usage:
    python run_phase5.py --webhook --port 9000
    python run_phase5.py --sync-repo "HospitalOrg/his-emr-core"
    python run_phase5.py --poll --interval-hours 6
"""

import argparse
import logging
import sys
import time
from pathlib import Path

from config import Config
from incremental_sync import IncrementalSyncEngine
from webhook_server import start_webhook_server

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Phase5Runner")


def run_polling_daemon(interval_hours: int = 6):
    """Periodic continuous sync daemon for environments without external webhooks."""
    logger.info("==================================================================")
    logger.info(f"STARTING HEALTHCARE PORTFOLIO POLLING DAEMON (Interval: {interval_hours}h)")
    logger.info("==================================================================")

    import run_phase1
    import run_phase2
    import run_phase3
    import run_phase4

    cycle = 1
    while True:
        logger.info(f"\n--- Starting Automated Portfolio Sync Cycle #{cycle} ---")
        try:
            # 1. Discovery
            logger.info("Cycle Step 1: Discovering repositories...")
            run_phase1.main()

            # 2. Extraction
            logger.info("Cycle Step 2: Extracting priority assets...")
            run_phase2.main()

            # 3. Classification
            logger.info("Cycle Step 3: Classifying domains...")
            run_phase3.main()

            # 4. Synthesis & Dashboard
            logger.info("Cycle Step 4: Refreshing dashboard and reports...")
            run_phase4.main()

            logger.info(f"--- Cycle #{cycle} completed successfully! ---")
        except Exception as e:
            logger.error(f"Error during polling cycle #{cycle}: {e}", exc_info=True)

        cycle += 1
        sleep_sec = interval_hours * 3600
        logger.info(f"Next sync scheduled in {interval_hours} hours. Sleeping...")
        time.sleep(sleep_sec)


def main():
    parser = argparse.ArgumentParser(
        description="Phase 5: Automated Sync & Webhook Integration (Continuous Mode)"
    )
    parser.add_argument(
        "--webhook",
        action="store_true",
        help="Start the GitHub Webhook receiver server"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=Config.WEBHOOK_PORT or 9000,
        help="Port for the webhook receiver (default: 9000)"
    )
    parser.add_argument(
        "--sync-repo",
        type=str,
        default=None,
        help="Trigger incremental sync on a single repository (e.g. 'owner/repo')"
    )
    parser.add_argument(
        "--poll",
        action="store_true",
        help="Run continuous polling background daemon"
    )
    parser.add_argument(
        "--interval-hours",
        type=int,
        default=Config.SYNC_INTERVAL_HOURS or 6,
        help="Interval in hours for the polling daemon (default: 6)"
    )

    args = parser.parse_args()

    # Mode 1: Single repo incremental sync
    if args.sync_repo:
        logger.info(f"Triggering on-demand incremental sync for: '{args.sync_repo}'...")
        engine = IncrementalSyncEngine()
        result = engine.sync_repository(args.sync_repo, regenerate_dashboard=True)
        print("\n" + "=" * 65)
        print(f"[SUCCESS] Incremental sync complete for: {result['name_with_owner']}")
        print(f"  Primary Domain:     {result['primary_domain']}")
        print(f"  Secondary Domains:  {result.get('secondary_domains', [])}")
        print(f"  Confidence Score:   {result['confidence_score']}")
        print(f"  Detected Standards: {result.get('detected_standards', [])}")
        print("  Dashboard & reports refreshed: output/dashboard/index.html")
        print("=" * 65 + "\n")
        return

    # Mode 2: Polling Daemon
    if args.poll:
        run_polling_daemon(interval_hours=args.interval_hours)
        return

    # Mode 3: Webhook Server (Default if --webhook specified or default action)
    if args.webhook or not (args.sync_repo or args.poll):
        start_webhook_server(port=args.port)


if __name__ == "__main__":
    main()

