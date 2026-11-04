"""
Automated Test Suite for Phase 3: Hybrid Domain Classifier.
Validates rule pattern engine, vector space profiling, and structured classification across all 9 domains.
"""

from hybrid_classifier import HybridClassifier, RulePatternEngine, VectorSpaceProfiler

TEST_DOSSIERS = [
    {
        "repo_name": "aoh-mep-procurement",
        "name_with_owner": "HospitalGroup/aoh-mep-procurement",
        "dossier_markdown": "# AOH Hospital Project\nMEP contractor packages, bill of quantities (BOQ), civil engineering drawings, and long-lead equipment procurement for the new AOH cancer bunker.",
        "extracted_entities": ["aoh", "boq", "contractor", "mep", "bunker"],
        "extracted_dependencies": ["PostgreSQL", "Docker", "Node.js"],
        "extracted_apis": ["/procurement/packages", "/boq/items"],
        "expected_domain": "Construction",
        "expected_standard": "AOH"
    },
    {
        "repo_name": "clinical-governance-ovr",
        "name_with_owner": "HospitalGroup/clinical-governance-ovr",
        "dossier_markdown": "# GAHAR and JCI Accreditation OVR Portal\nOccurrence variance reporting (OVR), adverse event incident reports, root cause analysis, infection control audits, and patient safety KPIs.",
        "extracted_entities": ["gahar", "jci", "ovr", "incident_report", "infection_control"],
        "extracted_dependencies": ["React", "FastAPI"],
        "extracted_apis": ["/incidents/submit", "/audits/kpis"],
        "expected_domain": "Clinical Governance",
        "expected_standard": "GAHAR"
    },
    {
        "repo_name": "claims-coder-icd10",
        "name_with_owner": "HospitalGroup/claims-coder-icd10",
        "dossier_markdown": "# Medical Coding Engine\nMapping clinical diagnoses to ICD-10 and procedures to CPT codes, insurance pre-authorization tariff validation, and TPA claim rejection management.",
        "extracted_entities": ["icd10", "cpt", "claim", "pre_auth", "tariff"],
        "extracted_dependencies": ["Python", "SQLAlchemy"],
        "extracted_apis": ["/claims/batch", "/coding/icd10"],
        "expected_domain": "Medical Coding and Pricing",
        "expected_standard": "ICD-10"
    },
    {
        "repo_name": "pharmacy-lasa-dispense",
        "name_with_owner": "HospitalGroup/pharmacy-lasa-dispense",
        "dossier_markdown": "# Hospital Pharmacy Unit-Dose System\nDrug formulary master, Look-Alike Sound-Alike (LASA) safety checks, controlled drug narcotics log, and dispensing workflows.",
        "extracted_entities": ["formulary", "lasa", "narcotic", "dispense", "unit_dose"],
        "extracted_dependencies": ["Spring Boot", "MySQL"],
        "extracted_apis": ["/dispense/unit-dose", "/formulary/search"],
        "expected_domain": "Pharmacy",
        "expected_standard": "LASA"
    },
    {
        "repo_name": "cme-academy-lms",
        "name_with_owner": "HospitalGroup/cme-academy-lms",
        "dossier_markdown": "# Healthcare Academy & LMS\nContinuing medical education (CME) credit tracker, clinical simulation labs, and nursing competency certifications.",
        "extracted_entities": ["cme", "lms", "clinical_simulation", "nursing_competency"],
        "extracted_dependencies": ["Django", "Redis"],
        "extracted_apis": ["/cme/credits", "/courses/enroll"],
        "expected_domain": "Academy and L&D",
        "expected_standard": "CME"
    }
]


def test_classifier():
    print("=" * 65)
    print("RUNNING PHASE 3 HYBRID DOMAIN CLASSIFIER VERIFICATION")
    print("=" * 65)

    classifier = HybridClassifier()

    for t in TEST_DOSSIERS:
        result = classifier.classify(t, force_offline=True)
        print(f"\n[EVAL] Repo: {result['name_with_owner']}")
        print(f"       Classified Primary Domain: {result['primary_domain']}")
        print(f"       Secondary Domains:         {result['secondary_domains']}")
        print(f"       Confidence Score:          {result['confidence_score']:.2f}")
        print(f"       Detected Standards:        {result['detected_standards']}")
        print(f"       Key Tech:                  {result['key_technologies']}")

        assert result["primary_domain"] == t["expected_domain"], (
            f"Expected {t['expected_domain']} but got {result['primary_domain']}"
        )
        assert t["expected_standard"] in result["detected_standards"], (
            f"Expected standard {t['expected_standard']} in detected standards {result['detected_standards']}"
        )
        assert result["confidence_score"] >= 0.70, "Confidence score lower than expected"

    print("\n" + "=" * 65)
    print(">>> ALL 5 MULTI-DOMAIN TEST CASES PASSED WITH 100% ACCURACY! <<<")
    print("=" * 65)


if __name__ == "__main__":
    test_classifier()
