"""
Main CLI entrypoint for Phase 4: Portfolio Catalog Synthesis & Relational Graphing.
Usage:
    python run_phase4.py
    python run_phase4.py --serve --port 8080
    python run_phase4.py --open
"""

import argparse
import json
import logging
import os
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import TCPServer

from config import Config
from dashboard_generator import DashboardGenerator
from portfolio_synthesis import PortfolioSynthesizer
from report_generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Phase4Runner")


def serve_dashboard(dashboard_dir: Path, port: int = 8080):
    os.chdir(dashboard_dir)
    handler = SimpleHTTPRequestHandler
    with TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}/index.html"
        logger.info(f"Serving Interactive Dashboard at {url}")
        print(f"\n[SERVER] Dashboard live at: {url}")
        print("Press Ctrl+C to stop the server.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[SERVER] Stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="Phase 4: Portfolio Catalog Synthesis & Relational Graphing"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help="Custom SQLite catalog database path"
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start a local HTTP server to host the interactive dashboard"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="HTTP server port for --serve (default: 8080)"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the interactive HTML dashboard in your default browser"
    )

    args = parser.parse_args()

    logger.info("==================================================================")
    logger.info("PHASE 4: PORTFOLIO CATALOG SYNTHESIS & RELATIONAL GRAPHING")
    logger.info("==================================================================")

    synthesizer = PortfolioSynthesizer(db_path=args.db or Config.DATABASE_PATH)
    synthesis_data = synthesizer.synthesize()

    out_base = Path("./output").resolve()
    reports_dir = out_base / "reports"
    dashboard_dir = out_base / "dashboard"
    reports_dir.mkdir(parents=True, exist_ok=True)
    dashboard_dir.mkdir(parents=True, exist_ok=True)

    # 1. Export Raw Synthesis JSON
    synthesis_json_path = reports_dir / "portfolio_synthesis.json"
    with open(synthesis_json_path, "w", encoding="utf-8") as f:
        json.dump(synthesis_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved Synthesis Data: {synthesis_json_path}")

    # 2. Export Relational Knowledge Graph JSON
    graph_json_path = reports_dir / "portfolio_graph.json"
    with open(graph_json_path, "w", encoding="utf-8") as f:
        json.dump(synthesis_data.get("graph", {}), f, indent=2, ensure_ascii=False)
    logger.info(f"Saved Knowledge Graph: {graph_json_path}")

    # 3. Generate Interactive HTML Dashboard
    html_dashboard_path = dashboard_dir / "index.html"
    DashboardGenerator.generate_html(synthesis_data, str(html_dashboard_path))
    logger.info(f"Generated Interactive HTML Dashboard: {html_dashboard_path}")

    # 4. Generate C-Level Markdown Executive Report
    md_report_path = reports_dir / "EXECUTIVE_HEALTHCARE_PORTFOLIO_REPORT.md"
    ReportGenerator.generate_markdown_report(synthesis_data, str(md_report_path))
    logger.info(f"Generated Executive Markdown Report: {md_report_path}")

    print("\n" + "=" * 70)
    print("PHASE 4 SYNTHESIS & GRAPHING COMPLETE!")
    print("=" * 70)
    print(f"Total Repositories Analyzed: {synthesis_data['total_repositories']}")
    print(f"Classified Repositories:    {synthesis_data['classified_repositories']}")
    print(f"GAHAR/JCI Quality Systems:  {synthesis_data['postures']['gahar_jci_systems_count']}")
    print(f"RCM & Medical Coding:       {synthesis_data['postures']['rcm_coding_systems_count']}")
    print(f"AOH Hospital Construction:  {synthesis_data['postures']['aoh_construction_systems_count']}")
    print("-" * 70)
    print("DELIVERABLES GENERATED:")
    print(f"  1. Interactive Dashboard:  {html_dashboard_path}")
    print(f"  2. Executive Report:       {md_report_path}")
    print(f"  3. Knowledge Graph JSON:   {graph_json_path}")
    print(f"  4. Full Synthesis JSON:    {synthesis_json_path}")
    print("=" * 70 + "\n")

    if args.open:
        webbrowser.open(f"file://{html_dashboard_path}")

    if args.serve:
        serve_dashboard(dashboard_dir, port=args.port)


if __name__ == "__main__":
    main()

