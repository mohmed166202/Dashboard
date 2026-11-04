# Healthcare Portfolio Intelligence: Phase 3 Guide

## Phase 3: Semantic Embeddings & Multi-Label LLM Domain Classifier

Phase 3 maps repository dossiers across the **9 Healthcare and Operational Domains** using a three-tier **Hybrid Classification Architecture**:
1. **Rule & Regex Pattern Engine:** Scans for high-precision clinical and operational tokens and standard certifications.
2. **Vector Space Profiler:** Computes cosine similarity against canonical domain semantic profiles.
3. **Structured LLM Assessment:** Synthesizes the signals and outputs strict JSON schemas via Gemini (or fallback deterministic engine).

---

### The 9 Healthcare Domains & Recognized Standards

| # | Domain | Primary Focus | Recognized Standards & Tokens |
|---|---|---|---|
| **1** | **Clinical Informatics** | Hospital Information Systems (HIS), EMR/EHR, doctor/nurse UX | `FHIR`, `HL7`, `DICOM`, `PACS`, `CPOE`, `HIS`, `EMR`, `vitals`, `triage` |
| **2** | **Clinical Governance** | Patient safety, clinical audit, quality KPIs | `GAHAR`, `JCI`, `OVR`, `incident reports`, `infection control`, `clinical audit` |
| **3** | **Medical Coding & Pricing** | Clinical diagnosis & procedure coding, claims, tariffs | `ICD-10`, `ICD-11`, `CPT`, `ACHI`, `DRG`, `claims`, `pre-auth`, `TPA tariffs` |
| **4** | **Human Resources** | Workforce scheduling, doctor privileging, payroll | `Credentialing`, `Privileging`, `Shift Rota`, `Payroll`, `HRMS`, `staffing levels` |
| **5** | **Academy and L&D** | Training, doctor CME, nursing competencies, simulations | `CME`, `CPD`, `LMS`, `Clinical Simulation`, `Residency`, `certifications` |
| **6** | **Pharmacy** | Formulary, drug dispensing, LASA safety, controlled substances | `Formulary`, `LASA`, `Unit-Dose`, `Narcotics`, `ADR`, `pharmacovigilance` |
| **7** | **Supply Chain** | Procurement, vendor bids, warehouse inventory, equipment | `Procurement`, `CMMS`, `Cold Chain`, `Consignment`, `PO Management`, `biomedical` |
| **8** | **Finance** | Multi-hospital RCM, EBITDA, AR aging, cash collections | `RCM`, `AR Aging`, `EBITDA`, `General Ledger`, `Cost Accounting`, `billing` |
| **9** | **Construction** | Hospital expansions, MEP, cleanrooms, AOH hospital project | `AOH Project`, `BOQ`, `MEP`, `Long-Lead Equipment`, `Linac/MRI Bunker`, `Cleanroom` |

---

### Output Schema Generated for Every Repository

```json
{
  "repo_name": "aoh-mep-procurement",
  "name_with_owner": "HospitalGroup/aoh-mep-procurement",
  "primary_domain": "Construction",
  "secondary_domains": ["Supply Chain", "Finance"],
  "confidence_score": 0.95,
  "domain_justification": "Repository contains MEP subcontractor packages, bill of quantities (BOQ), and long-lead equipment procurement for the AOH hospital project.",
  "detected_standards": ["AOH", "BOQ", "Long-Lead Equipment", "MEP", "Procurement"],
  "project_status": "Active / In Development",
  "key_technologies": ["PostgreSQL", "Docker", "Node.js"]
}
```

---

### How to Run Phase 3

#### 1. Classify All Extracted Dossiers
```bash
python run_phase3.py
```

#### 2. Run in Offline / Deterministic Mode (No LLM API Key Required)
```bash
python run_phase3.py --offline
```

#### 3. Classify a Specific Repository
```bash
python run_phase3.py --repo "claims-coder-icd10"
```

#### 4. Outputs Generated
* **SQLite Database:** Table `domain_classifications` in `healthcare_portfolio_catalog.db`.
* **JSON Portfolio File:** `./output/domain_classifications.json` (Structured JSON of all classified repositories).
* **CSV Matrix:** `./output/domain_matrix.csv` (Spreadsheet with domain distribution, confidence, and standards).

