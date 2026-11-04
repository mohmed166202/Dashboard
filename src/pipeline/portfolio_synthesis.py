"""
Portfolio Synthesis & Relational Graphing Engine for Phase 4.
Aggregates catalog repositories, dossiers, and classifications into:
  1. Domain Matrix Breakdown & Cross-cutting overlaps
  2. Executive Summaries per Domain (GAHAR/JCI, RCM/Coding, AOH Project)
  3. Gap Analysis (documentation, domain coverage, regulatory posture)
  4. Relational Knowledge Graph (Nodes & Edges)
"""

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from config import Config
from db import DatabaseManager
from domain_taxonomy import HEALTHCARE_DOMAINS

logger = logging.getLogger("PortfolioSynthesis")


class PortfolioSynthesizer:
    def __init__(self, db_path: Optional[str] = None):
        self.db = DatabaseManager(db_path or Config.DATABASE_PATH)

    def synthesize(self) -> Dict[str, Any]:
        """Performs full portfolio synthesis and relational analysis."""
        all_repos = self.db.get_all_repositories()
        classifications = self.db.get_all_classifications()

        # Index classifications by name_with_owner
        class_map = {c["name_with_owner"]: c for c in classifications}

        # 1. Domain Matrix Breakdown
        domain_counts = Counter()
        domain_repos: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        cross_cutting_matrix: Dict[str, Dict[str, int]] = {
            d: {other: 0 for other in HEALTHCARE_DOMAINS.keys()}
            for d in HEALTHCARE_DOMAINS.keys()
        }

        standards_summary: Dict[str, List[str]] = defaultdict(list)
        tech_counter = Counter()

        for c in classifications:
            p_domain = c["primary_domain"]
            domain_counts[p_domain] += 1
            domain_repos[p_domain].append(c)

            # Standards
            for std in c.get("detected_standards", []):
                standards_summary[std].append(c["name_with_owner"])

            # Tech
            for t in c.get("key_technologies", []):
                tech_counter[t] += 1

            # Cross-cutting secondary domains
            for s_domain in c.get("secondary_domains", []):
                if s_domain in cross_cutting_matrix.get(p_domain, {}):
                    cross_cutting_matrix[p_domain][s_domain] += 1
                    cross_cutting_matrix[s_domain][p_domain] += 1

        # 2. Key Healthcare Operational Postures
        # A) Clinical Governance: GAHAR & JCI Accreditation systems
        gahar_jci_systems = [
            c for c in classifications
            if any(s in c.get("detected_standards", []) for s in ["GAHAR", "JCI", "OVR", "Patient Safety", "Clinical Audit"])
            or c["primary_domain"] == "Clinical Governance"
        ]

        # B) Revenue Cycle Management & Medical Coding systems
        rcm_coding_systems = [
            c for c in classifications
            if any(s in c.get("detected_standards", []) for s in ["ICD-10", "ICD-11", "CPT", "DRG", "RCM", "TPA", "Pre-Auth"])
            or c["primary_domain"] in ["Medical Coding and Pricing", "Finance"]
        ]

        # C) AOH Hospital Project & Construction systems
        aoh_construction_systems = [
            c for c in classifications
            if any(s in c.get("detected_standards", []) for s in ["AOH", "AOH Project", "BOQ", "MEP", "Long-Lead Equipment"])
            or c["primary_domain"] == "Construction"
        ]

        # 3. Domain Executive Summaries
        domain_summaries = {}
        for d_name, d_def in HEALTHCARE_DOMAINS.items():
            repos_in_domain = domain_repos.get(d_name, [])
            tech_in_domain = Counter()
            standards_in_domain = Counter()

            for r in repos_in_domain:
                for t in r.get("key_technologies", []):
                    tech_in_domain[t] += 1
                for s in r.get("detected_standards", []):
                    standards_in_domain[s] += 1

            domain_summaries[d_name] = {
                "name": d_name,
                "description": d_def.description,
                "repository_count": len(repos_in_domain),
                "repositories": [
                    {
                        "name_with_owner": r["name_with_owner"],
                        "confidence": r["confidence_score"],
                        "status": r.get("project_status", "Active"),
                        "standards": r.get("detected_standards", []),
                        "tech": r.get("key_technologies", [])
                    }
                    for r in repos_in_domain
                ],
                "top_technologies": [t for t, _ in tech_in_domain.most_common(5)],
                "top_standards": [s for s, _ in standards_in_domain.most_common(5)],
            }

        # 4. Gap Analysis
        missing_readme = [r["name_with_owner"] for r in all_repos if not r.get("has_readme")]
        unclassified_repos = [r["name_with_owner"] for r in all_repos if r["name_with_owner"] not in class_map]

        uncovered_domains = [d for d in HEALTHCARE_DOMAINS.keys() if domain_counts[d] == 0]
        underrepresented_domains = [d for d in HEALTHCARE_DOMAINS.keys() if 0 < domain_counts[d] <= 2]

        gap_recommendations = []
        if uncovered_domains:
            gap_recommendations.append({
                "severity": "HIGH",
                "area": "Domain Coverage",
                "finding": f"Zero repositories detected for: {', '.join(uncovered_domains)}.",
                "action": "Audit whether systems for these domains reside in legacy on-premise servers, 3rd-party SaaS, or are unmanaged."
            })
        if not gahar_jci_systems:
            gap_recommendations.append({
                "severity": "CRITICAL",
                "area": "Accreditation Readiness",
                "finding": "No repositories currently implement GAHAR or JCI quality/incident reporting (OVR).",
                "action": "Prioritize deploying an Occurrence Variance Reporting (OVR) and clinical audit module to meet hospital accreditation mandates."
            })
        if not rcm_coding_systems:
            gap_recommendations.append({
                "severity": "HIGH",
                "area": "Revenue Integrity",
                "finding": "Lack of dedicated medical coding (ICD-10/CPT) or claims pre-auth engines in the codebase.",
                "action": "Automate claims validation and tariff pricing to minimize insurer denial rates."
            })
        if missing_readme:
            gap_recommendations.append({
                "severity": "MEDIUM",
                "area": "Documentation Debt",
                "finding": f"{len(missing_readme)} repositories lack a README file.",
                "action": "Institute a baseline documentation requirement across development teams."
            })

        # 5. Relational Knowledge Graph Construction
        graph = self._build_knowledge_graph(classifications, domain_counts)

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_repositories": len(all_repos),
            "classified_repositories": len(classifications),
            "unclassified_count": len(unclassified_repos),
            "domain_counts": dict(domain_counts),
            "cross_cutting_matrix": cross_cutting_matrix,
            "domain_summaries": domain_summaries,
            "postures": {
                "gahar_jci_systems_count": len(gahar_jci_systems),
                "gahar_jci_repos": [r["name_with_owner"] for r in gahar_jci_systems],
                "rcm_coding_systems_count": len(rcm_coding_systems),
                "rcm_coding_repos": [r["name_with_owner"] for r in rcm_coding_systems],
                "aoh_construction_systems_count": len(aoh_construction_systems),
                "aoh_construction_repos": [r["name_with_owner"] for r in aoh_construction_systems],
            },
            "gap_analysis": {
                "missing_readme_count": len(missing_readme),
                "missing_readme_repos": missing_readme[:20],
                "uncovered_domains": uncovered_domains,
                "underrepresented_domains": underrepresented_domains,
                "recommendations": gap_recommendations
            },
            "technologies": [t for t, _ in tech_counter.most_common(12)],
            "standards_summary": {k: len(v) for k, v in standards_summary.items()},
            "graph": graph
        }

    def _build_knowledge_graph(self, classifications: List[Dict[str, Any]], domain_counts: Counter) -> Dict[str, Any]:
        """Creates nodes and edges for network graphing."""
        nodes = []
        edges = []
        seen_nodes: Set[str] = set()

        # Domain Nodes
        for d_name in HEALTHCARE_DOMAINS.keys():
            nodes.append({
                "id": f"domain:{d_name}",
                "label": d_name,
                "type": "domain",
                "size": max(15, domain_counts[d_name] * 4),
                "group": "domain"
            })
            seen_nodes.add(f"domain:{d_name}")

        # Repo & Standard Nodes and Edges
        for c in classifications:
            repo_id = f"repo:{c['name_with_owner']}"
            if repo_id not in seen_nodes:
                nodes.append({
                    "id": repo_id,
                    "label": c["repo_name"],
                    "full_name": c["name_with_owner"],
                    "type": "repository",
                    "confidence": c["confidence_score"],
                    "primary_domain": c["primary_domain"],
                    "group": "repository"
                })
                seen_nodes.add(repo_id)

            # Edge: Repo -> Primary Domain
            edges.append({
                "source": repo_id,
                "target": f"domain:{c['primary_domain']}",
                "relation": "PRIMARY_DOMAIN",
                "weight": 2.0
            })

            # Edge: Repo -> Secondary Domains
            for s_domain in c.get("secondary_domains", []):
                edges.append({
                    "source": repo_id,
                    "target": f"domain:{s_domain}",
                    "relation": "SECONDARY_DOMAIN",
                    "weight": 1.0
                })

            # Standard Nodes & Edges
            for std in c.get("detected_standards", []):
                std_id = f"standard:{std}"
                if std_id not in seen_nodes:
                    nodes.append({
                        "id": std_id,
                        "label": std,
                        "type": "standard",
                        "group": "standard"
                    })
                    seen_nodes.add(std_id)
                edges.append({
                    "source": repo_id,
                    "target": std_id,
                    "relation": "IMPLEMENTS",
                    "weight": 1.5
                })

        return {"nodes": nodes, "edges": edges}

