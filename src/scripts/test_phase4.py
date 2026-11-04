"""
Automated Test Suite for Phase 4: Portfolio Catalog Synthesis & Relational Graphing.
Validates synthesis calculation, cross-cutting matrix, HTML dashboard creation,
and executive markdown report output.
"""

import json
from pathlib import Path

from dashboard_generator import DashboardGenerator
from db import DatabaseManager
from portfolio_synthesis import PortfolioSynthesizer
from report_generator import ReportGenerator


def test_phase4_pipeline():
    print("=" * 65)
    print("RUNNING PHASE 4 SYNTHESIS & DASHBOARD PIPELINE VERIFICATION")
    print("=" * 65)

    test_db_path = "test_phase4.db"
    db = DatabaseManager(test_db_path)

    # Insert sample repositories
    sample_repos = [
        {
            "node_id": "r1",
            "name": "aoh-mep-procurement",
            "name_with_owner": "HospitalOrg/aoh-mep-procurement",
            "owner": "HospitalOrg",
            "description": "AOH hospital construction MEP and BOQ management",
            "primary_language": "TypeScript",
            "default_branch": "main",
            "has_readme": 1
        },
        {
            "node_id": "r2",
            "name": "clinical-governance-ovr",
            "name_with_owner": "HospitalOrg/clinical-governance-ovr",
            "owner": "HospitalOrg",
            "description": "GAHAR and JCI incident reporting portal",
            "primary_language": "Python",
            "default_branch": "main",
            "has_readme": 1
        },
        {
            "node_id": "r3",
            "name": "claims-coder-icd10",
            "name_with_owner": "HospitalOrg/claims-coder-icd10",
            "owner": "HospitalOrg",
            "description": "ICD-10 and CPT coding claims reconciliation",
            "primary_language": "Python",
            "default_branch": "main",
            "has_readme": 0  # To trigger gap recommendation
        }
    ]
    db.batch_upsert_repositories(sample_repos)

    # Insert sample classifications
    classifications = [
        {
            "repo_name": "aoh-mep-procurement",
            "name_with_owner": "HospitalOrg/aoh-mep-procurement",
            "primary_domain": "Construction",
            "secondary_domains": ["Supply Chain", "Finance"],
            "confidence_score": 0.95,
            "domain_justification": "AOH MEP package and BOQ management.",
            "detected_standards": ["AOH", "BOQ", "MEP", "Long-Lead Equipment"],
            "project_status": "Active / In Development",
            "key_technologies": ["Node.js", "PostgreSQL", "Docker"]
        },
        {
            "repo_name": "clinical-governance-ovr",
            "name_with_owner": "HospitalOrg/clinical-governance-ovr",
            "primary_domain": "Clinical Governance",
            "secondary_domains": ["Clinical Informatics"],
            "confidence_score": 0.95,
            "domain_justification": "GAHAR incident reports (OVR) and audits.",
            "detected_standards": ["GAHAR", "JCI", "OVR", "Patient Safety"],
            "project_status": "Active / In Development",
            "key_technologies": ["React", "FastAPI"]
        },
        {
            "repo_name": "claims-coder-icd10",
            "name_with_owner": "HospitalOrg/claims-coder-icd10",
            "primary_domain": "Medical Coding and Pricing",
            "secondary_domains": ["Finance"],
            "confidence_score": 0.92,
            "domain_justification": "ICD-10 and CPT claims engine.",
            "detected_standards": ["ICD-10", "CPT", "TPA", "Pre-Auth"],
            "project_status": "Active / In Development",
            "key_technologies": ["Python", "SQLAlchemy"]
        }
    ]
    for c in classifications:
        db.upsert_classification(c)

    # 1. Test Synthesis
    synthesizer = PortfolioSynthesizer(test_db_path)
    synth = synthesizer.synthesize()

    print(f"[TEST] Synthesized repos: {synth['total_repositories']}")
    print(f"[TEST] Classified repos:  {synth['classified_repositories']}")
    print(f"[TEST] GAHAR/JCI systems: {synth['postures']['gahar_jci_systems_count']}")
    print(f"[TEST] RCM/Coding systems:{synth['postures']['rcm_coding_systems_count']}")
    print(f"[TEST] AOH modules:       {synth['postures']['aoh_construction_systems_count']}")
    print(f"[TEST] Missing READMEs:   {synth['gap_analysis']['missing_readme_count']}")

    assert synth["total_repositories"] == 3
    assert synth["classified_repositories"] == 3
    assert synth["postures"]["gahar_jci_systems_count"] == 1
    assert synth["postures"]["rcm_coding_systems_count"] == 1
    assert synth["postures"]["aoh_construction_systems_count"] == 1
    assert synth["gap_analysis"]["missing_readme_count"] == 1
    assert len(synth["graph"]["nodes"]) >= 12  # 9 domains + 3 repos + standards
    assert len(synth["graph"]["edges"]) >= 6

    # 2. Test HTML Dashboard Generation
    test_html = Path("test_dashboard.html")
    DashboardGenerator.generate_html(synth, str(test_html))
    assert test_html.exists()
    assert test_html.stat().st_size > 5000
    print(f"[TEST] HTML Dashboard generated successfully! Size: {test_html.stat().st_size} bytes")

    # 3. Test Markdown Report Generation
    test_report = Path("test_report.md")
    ReportGenerator.generate_markdown_report(synth, str(test_report))
    assert test_report.exists()
    assert test_report.stat().st_size > 1000
    print(f"[TEST] Markdown Report generated successfully! Size: {test_report.stat().st_size} bytes")

    # Cleanup test files
    test_html.unlink(missing_ok=True)
    test_report.unlink(missing_ok=True)
    Path(test_db_path).unlink(missing_ok=True)

    print("\n" + "=" * 65)
    print(">>> ALL PHASE 4 SYNTHESIS & DASHBOARD TESTS PASSED SUCCESSFULLY! <<<")
    print("=" * 65)


if __name__ == "__main__":
    test_phase4_pipeline()

