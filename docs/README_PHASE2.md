# Healthcare Portfolio Intelligence: Phase 2 Guide

## Phase 2: Targeted Asynchronous Document & Asset Extraction

Phase 2 extracts deep context from 150+ repositories **at 10x the speed of git cloning** by querying recursive Git Trees directly (`/git/trees/{branch}?recursive=1`) and downloading only the files relevant to the 9 healthcare domains.

---

### Priority Extraction Strategy

| Tier | Focus Area | File Patterns Matched | Purpose in Healthcare Scope |
|---|---|---|---|
| **Priority 1** | **Core Documentation** | `README*`, `docs/**/*.md`, `wiki/**/*.md`, `architecture.md` | Provides high-level operational intent, user manuals, and clinical guidelines. |
| **Priority 2** | **Architecture & API Specs** | `swagger.*`, `openapi.*`, `*.postman_collection.json`, `docs/adr/*.md` | Discovers exposed HTTP endpoints, FHIR/HL7 interfaces, and system integrations. |
| **Priority 3** | **Dependencies & Services** | `package.json`, `requirements.txt`, `pom.xml`, `docker-compose.yml`, `Chart.yaml` | Identifies software libraries, message queues (Kafka, RabbitMQ), and microservices. |
| **Priority 4** | **Data Models & Schemas** | `schema.prisma`, `*.sql`, `models/**/*.py`, `entities/**/*.ts` | Uncovers core data structures: encounters, claims, vitals, drug batches, payroll. |

---

### Project Synthesis Dossier (<100KB)

For every repository, Phase 2 generates a unified markdown dossier containing:
1. **Executive Profile:** Language, branch, size, activity, topics, and description.
2. **Detected Healthcare Domain Entities:** Signatures matching GAHAR, JCI, ICD-10, CPT, AOH construction, pharmacy formulary, etc.
3. **Discovered Data Models:** Relational tables and schema models.
4. **Dependencies & Frameworks:** Parsed package manifests and Docker services.
5. **Contract Interfaces:** Discovered REST routes and API paths.
6. **Sanitized Document Excerpts:** Key sections from READMEs and ADRs.
7. **Audit Manifest:** Full list of prioritized files analyzed.

---

### How to Run Phase 2

#### 1. Process All Discovered Repositories (Concurrent Workers)
```bash
python run_phase2.py --workers 8
```

#### 2. Test on a Subset (e.g. First 5 Repositories)
```bash
python run_phase2.py --limit 5
```

#### 3. Extract a Specific Repository
```bash
python run_phase2.py --repo "my-repo-name"
```

#### 4. Outputs
* **SQLite Database:** Table `repo_dossiers` in `healthcare_portfolio_catalog.db`.
* **Markdown Files:** Saved to `./output/dossiers/{repo_name}.md` for immediate inspection or LLM ingestion.

