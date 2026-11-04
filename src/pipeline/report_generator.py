"""
Executive Markdown Report Generator for Phase 4.
Produces a C-level executive briefing markdown document ready for Board of Directors,
CMIO, and Healthcare Operations leadership.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class ReportGenerator:
    @staticmethod
    def generate_markdown_report(data: Dict[str, Any], output_path: str = "./output/reports/EXECUTIVE_HEALTHCARE_PORTFOLIO_REPORT.md") -> str:
        path = Path(output_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)

        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        total_repos = data.get("total_repositories", 0)
        classified_repos = data.get("classified_repositories", 0)
        postures = data.get("postures", {})
        gap_analysis = data.get("gap_analysis", {})

        lines = []

        # Title
        lines.append("# Executive Healthcare Portfolio Intelligence Report")
        lines.append(f"*Generated on {now_str} &bull; Strategic Scope: 9 Healthcare & Operational Domains*\n")

        # 1. Executive Summary
        lines.append("## 1. Executive Overview & Portfolio Vital Signs\n")
        lines.append(
            f"An automated audit was conducted across **{total_repos} repositories** in the healthcare technology portfolio. "
            f"Of these, **{classified_repos} repositories** were semantically synthesized and categorized across the 9 defined healthcare and operational domains.\n"
        )

        lines.append("| Vital Sign | Metric Value | Strategic Impact |")
        lines.append("|---|---|---|")
        lines.append(f"| **Total Repositories Analyzed** | `{total_repos}` | Full organization and user codebase scope |")
        lines.append(f"| **Classified against Scope** | `{classified_repos}` | Multi-label semantic taxonomy alignment |")
        lines.append(f"| **GAHAR / JCI Quality Modules** | `{postures.get('gahar_jci_systems_count', 0)}` | Accreditation, incident reporting (OVR) & clinical audits |")
        lines.append(f"| **Medical Coding & RCM Modules** | `{postures.get('rcm_coding_systems_count', 0)}` | ICD-10, CPT, pre-auth & insurance claim generation |")
        lines.append(f"| **AOH Hospital Construction** | `{postures.get('aoh_construction_systems_count', 0)}` | MEP packages, BOQ, bunker medical equipment & contractor tracking |")
        lines.append("")

        # 2. Domain Breakdown Table
        lines.append("## 2. The 9 Healthcare Domains: Operational Breakdown\n")
        lines.append("| # | Domain | Active Repos | Top Standards Detected | Primary Tech Stacks |")
        lines.append("|---|---|---|---|---|")

        summaries = data.get("domain_summaries", {})
        idx = 1
        for d_name, d_info in summaries.items():
            count = d_info.get("repository_count", 0)
            standards = ", ".join(d_info.get("top_standards", [])) or "None"
            tech = ", ".join(d_info.get("top_technologies", [])) or "Various"
            lines.append(f"| **{idx}** | **{d_name}** | `{count}` | {standards} | {tech} |")
            idx += 1
        lines.append("")

        # 3. Strategic Healthcare Pillars Deep-Dive
        lines.append("## 3. Strategic Healthcare Pillars Deep-Dive\n")

        # 3.1 Clinical Governance
        lines.append("### 3.1 Clinical Governance, Quality & Accreditation (GAHAR & JCI)")
        gahar_repos = postures.get("gahar_jci_repos", [])
        if gahar_repos:
            lines.append("The portfolio contains dedicated systems monitoring quality assurance, clinical audits, and accreditation readiness:")
            for r in gahar_repos:
                lines.append(f"- **`{r}`**: Tracks adverse events, occurrence variance reporting (OVR), infection control, or quality indicator KPIs.")
        else:
            lines.append("> [!WARNING]\n> **Accreditation Blind Spot:** No dedicated repositories currently manage GAHAR or JCI compliance, incident reporting (OVR), or infection audits. Prioritize deploying an incident management module to protect clinical accreditation status.")
        lines.append("")

        # 3.2 Medical Coding & RCM
        lines.append("### 3.2 Medical Coding, Pricing & Revenue Cycle Management")
        rcm_repos = postures.get("rcm_coding_repos", [])
        if rcm_repos:
            lines.append("Systems managing financial sustainability, insurance tariffs, and clinical classification:")
            for r in rcm_repos:
                lines.append(f"- **`{r}`**: Bridges diagnoses (ICD-10/11), procedure billing (CPT/ACHI), pre-authorization, and claims reconciliation.")
        else:
            lines.append("> [!IMPORTANT]\n> **Revenue Integrity Risk:** No dedicated medical coding or pre-auth automation engines detected. High reliance on manual billing increases insurer claim rejection rates.")
        lines.append("")

        # 3.3 AOH Hospital Project
        lines.append("### 3.3 Construction & Hospital Expansion (AOH Project)")
        aoh_repos = postures.get("aoh_construction_repos", [])
        if aoh_repos:
            lines.append("Capital infrastructure packages and engineering expansion modules:")
            for r in aoh_repos:
                lines.append(f"- **`{r}`**: Manages MEP engineering packages, bill of quantities (BOQ), contractor milestones, and long-lead clinical equipment (e.g. Linac/MRI bunkers).")
        else:
            lines.append("> [!NOTE]\n> Construction packages for the AOH project are currently managed through external procurement tools or offline engineering workflows.")
        lines.append("")

        # 4. Cross-Cutting Overlaps
        lines.append("## 4. Cross-Cutting Domain Matrix\n")
        lines.append("Healthcare systems rarely operate in silos. The matrix below highlights repositories providing bridging capabilities across multiple disciplines:\n")
        lines.append("| Domain Interconnection | Overlapping Repositories | Clinical / Operational Rationale |")
        lines.append("|---|---|---|")
        lines.append("| **Pharmacy &harr; Supply Chain** | Drug formulary & central store inventory | Ensures medication safety stock and prevents batch expirations |")
        lines.append("| **Medical Coding &harr; Finance** | Claims engine & AR aging | Links clinical ICD-10 coding to accounts receivable and revenue realization |")
        lines.append("| **Clinical Informatics &harr; Governance** | EHR notes & incident reports (OVR) | Ensures clinical documentation accuracy meets JCI/GAHAR audit standards |")
        lines.append("| **Construction &harr; Supply Chain** | AOH MEP & biomedical equipment | Coordinates long-lead medical equipment delivery with civil handover milestones |")
        lines.append("")

        # 5. Gap Analysis & Strategic Recommendations
        lines.append("## 5. Strategic Gap Analysis & Executive Recommendations\n")
        recs = gap_analysis.get("recommendations", [])
        if recs:
            for rec in recs:
                severity = rec.get("severity", "MEDIUM")
                area = rec.get("area", "General")
                finding = rec.get("finding", "")
                action = rec.get("action", "")
                lines.append(f"### [{severity}] {area}")
                lines.append(f"- **Finding:** {finding}")
                lines.append(f"- **Action Required:** {action}\n")
        else:
            lines.append("*All core operational and clinical domains meet baseline technical coverage.*\n")

        # Footer
        lines.append("---")
        lines.append("*Dashboard and full interactive analytics available at `output/dashboard/index.html`.*")

        full_md = "\n".join(lines)
        path.write_text(full_md, encoding="utf-8")
        return str(path)

