"""
Content Extractor and Entity Analyzer for Phase 2.
Fetches prioritized file contents and extracts domain entities, database schemas,
dependencies, and API routes.
"""

import base64
import json
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import requests

from config import Config

logger = logging.getLogger("ContentExtractor")

# Known healthcare and operational entity keywords across the 9 domains
DOMAIN_ENTITY_PATTERNS = [
    # 1. Clinical Informatics & EMR
    r"\b(patient|patient_id|encounter|vital|triage|clinical_note|soap_note|emr|his|ehr|fhir|hl7|dicom|pacs|cpoe|doctor_order|nursing_assessment)\b",
    # 2. Clinical Governance & Accreditation
    r"\b(gahar|jci|accreditation|ovr|incident_report|clinical_audit|infection_control|hand_hygiene|adverse_event|root_cause|kpi_metric|clinical_indicator)\b",
    # 3. Medical Coding & Pricing
    r"\b(icd10|icd_10|icd11|cpt|achi|drg|claim|claims|pre_auth|preauthorization|insurance_tariff|price_master|service_package|rejection_code|payer)\b",
    # 4. Human Resources & Credentialing
    r"\b(credential|privilege|medical_license|rota|doctor_shift|nurse_shift|payroll|employee_master|attendance|retention|staffing_ratio)\b",
    # 5. Academy & L&D
    r"\b(cme|cme_credit|residency|fellowship|clinical_simulation|training_program|curriculum|exam|lms|nursing_competency|certification)\b",
    # 6. Pharmacy
    r"\b(formulary|prescription|rx|dispense|unit_dose|lasa|narcotic|controlled_drug|adr|adverse_drug|drug_interaction|batch_expiry|medication_safety)\b",
    # 7. Supply Chain & Equipment
    r"\b(procurement|rfp|rfq|vendor|supplier|purchase_order|po_item|warehouse|consignment|biomedical|cmms|cold_chain|safety_stock)\b",
    # 8. Finance & Revenue Cycle
    r"\b(rcm|revenue_cycle|accounts_receivable|ar_aging|cost_center|general_ledger|invoice|billing|copay|cash_collection|ebitda|profitability)\b",
    # 9. Construction & Infrastructure
    r"\b(aoh|aoh_project|boq|bill_of_quantities|contractor|subcontractor|mep|long_lead|cleanroom|hvac|bunker|linac|mri_suite|site_milestone)\b"
]

COMPILED_ENTITY_REGEXES = [re.compile(p, re.IGNORECASE) for p in DOMAIN_ENTITY_PATTERNS]


class ContentExtractor:
    def __init__(self, session: Optional[requests.Session] = None, token: Optional[str] = None):
        self.token = token or Config.GITHUB_TOKEN
        self.session = session or requests.Session()
        if self.token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "Healthcare-Portfolio-Extractor/1.0"
            })

    def fetch_file_content(self, owner: str, repo: str, default_branch: str, file_node: Dict[str, Any], max_bytes: int = 150000) -> Optional[str]:
        """
        Fetches file content using GitHub Git Blobs API or raw content endpoint.
        Returns decoded text or None if binary/failed.
        """
        # 1. Try Git Blob API using sha
        sha = file_node.get("sha")
        path = file_node.get("path", "")
        size = file_node.get("size", 0)

        # Skip oversized files
        if size > max_bytes:
            logger.debug(f"Skipping oversized file {path} ({size} bytes)")
            return None

        if sha:
            url = f"https://api.github.com/repos/{owner}/{repo}/git/blobs/{sha}"
            try:
                resp = self.session.get(url, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    encoding = data.get("encoding")
                    content_raw = data.get("content", "")
                    if encoding == "base64":
                        decoded_bytes = base64.b64decode(content_raw)
                        return decoded_bytes.decode("utf-8", errors="replace")
            except Exception as e:
                logger.debug(f"Git blob fetch failed for {path}: {e}")

        # 2. Fallback to raw content
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{path}"
        try:
            resp = self.session.get(raw_url, timeout=20)
            if resp.status_code == 200:
                return resp.text
        except Exception as e:
            logger.debug(f"Raw fetch failed for {path}: {e}")

        return None

    def extract_entities_from_text(self, text: str) -> Set[str]:
        """Identifies domain and healthcare entities in the document or schema text."""
        detected = set()
        for regex in COMPILED_ENTITY_REGEXES:
            matches = regex.findall(text)
            for m in matches:
                if isinstance(m, tuple):
                    m = m[0]
                detected.add(m.lower())
        return detected

    def extract_database_tables(self, filename: str, content: str) -> List[str]:
        """Extracts SQL table names or Prisma models."""
        tables = []
        lower_fn = filename.lower()

        if "prisma" in lower_fn:
            matches = re.findall(r"model\s+([A-Za-z0-9_]+)\s*\{", content)
            tables.extend(matches)
        elif lower_fn.endswith(".sql"):
            matches = re.findall(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:[\"`\[]?\w+[\"`\]]?\.)?[\"`\[]?([A-Za-z0-9_]+)[\"`\]]?", content, re.IGNORECASE)
            tables.extend(matches)
        elif lower_fn.endswith((".py", ".ts", ".js")):
            # TypeORM, Django, SQLAlchemy models
            matches = re.findall(r"class\s+([A-Za-z0-9_]+)\s*\((?:models\.Model|Base|Entity)\)", content)
            tables.extend(matches)
            matches_dec = re.findall(r"@Entity\s*\(\s*(?:[\"'](\w+)[\"'])?\s*\)\s*(?:export\s+)?class\s+([A-Za-z0-9_]+)", content)
            for m in matches_dec:
                tables.append(m[0] or m[1])

        return sorted(list(set(tables)))[:30]

    def extract_dependencies(self, filename: str, content: str) -> List[str]:
        """Extracts key library dependencies and frameworks from manifest files."""
        deps = []
        lower_fn = filename.lower().split("/")[-1]

        try:
            if lower_fn == "package.json":
                data = json.loads(content)
                all_deps = list(data.get("dependencies", {}).keys()) + list(data.get("devDependencies", {}).keys())
                deps.extend(all_deps[:40])
            elif lower_fn == "requirements.txt":
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        dep_name = re.split(r"[=<>~;]", line)[0].strip()
                        if dep_name:
                            deps.append(dep_name)
            elif lower_fn in ("docker-compose.yml", "docker-compose.yaml"):
                # Extract service names and images
                services = re.findall(r"^\s{2}([A-Za-z0-9_-]+):\s*$", content, re.MULTILINE)
                images = re.findall(r"image:\s*([^\s]+)", content)
                deps.extend([f"service:{s}" for s in services[:15]])
                deps.extend([f"image:{i}" for i in images[:15]])
        except Exception:
            pass

        return deps[:30]

    def extract_api_specs(self, filename: str, content: str) -> List[str]:
        """Extracts high-level API paths, tags, or operations from OpenAPI / Swagger / Postman."""
        apis = []
        lower_fn = filename.lower()

        if "swagger" in lower_fn or "openapi" in lower_fn:
            try:
                # If json
                if content.strip().startswith("{"):
                    spec = json.loads(content)
                    paths = list(spec.get("paths", {}).keys())[:25]
                    apis.extend(paths)
                else:
                    # Regex for YAML paths
                    paths = re.findall(r"^\s{2}(/[A-Za-z0-9_{}/-]+):", content, re.MULTILINE)[:25]
                    apis.extend(paths)
            except Exception:
                pass
        elif "postman_collection" in lower_fn:
            try:
                col = json.loads(content)
                items = col.get("item", [])
                for it in items[:25]:
                    if "name" in it:
                        apis.append(it["name"])
            except Exception:
                pass

        return apis[:25]

