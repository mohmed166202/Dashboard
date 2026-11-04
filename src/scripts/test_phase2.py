"""
Verification test for Phase 2: Tree scanner, content extractor, and dossier builder.
"""

from tree_scanner import TreeScanner
from dossier_builder import DossierBuilder
from content_extractor import ContentExtractor

sample_tree = [
    {"type": "blob", "path": "README.md", "size": 1200},
    {"type": "blob", "path": "docs/architecture.md", "size": 4500},
    {"type": "blob", "path": "swagger.json", "size": 8900},
    {"type": "blob", "path": "package.json", "size": 2100},
    {"type": "blob", "path": "prisma/schema.prisma", "size": 3200},
    {"type": "blob", "path": "node_modules/express/index.js", "size": 900},
]

filtered = TreeScanner.filter_tree(sample_tree)
print("[TEST] TreeScanner P1:", [f["path"] for f in filtered[1]])
print("[TEST] TreeScanner P2:", [f["path"] for f in filtered[2]])
print("[TEST] TreeScanner P3:", [f["path"] for f in filtered[3]])
print("[TEST] TreeScanner P4:", [f["path"] for f in filtered[4]])

assert "README.md" in [f["path"] for f in filtered[1]]
assert "swagger.json" in [f["path"] for f in filtered[2]]
assert "package.json" in [f["path"] for f in filtered[3]]
assert "prisma/schema.prisma" in [f["path"] for f in filtered[4]]
assert "node_modules/express/index.js" not in [f["path"] for tier in filtered.values() for f in tier]

# Test entity extractor
ext = ContentExtractor(token="")
entities = ext.extract_entities_from_text("This system manages patient triage, encounter vitals, GAHAR audits, and ICD-10 medical coding.")
print("[TEST] Detected Entities:", sorted(list(entities)))
assert "patient" in entities
assert "encounter" in entities
assert "gahar" in entities

dossier = DossierBuilder.build_dossier(
    repo_metadata={
        "name": "his-emr-core",
        "name_with_owner": "HealthOrg/his-emr-core",
        "primary_language": "TypeScript",
        "topics": ["emr", "gahar-compliant"],
        "description": "Hospital Information System Core EMR"
    },
    doc_contents=[{"path": "README.md", "content": "# EMR Core\nClinical triage and patient vitals"}],
    spec_contents=[{"path": "swagger.json", "content": '{"paths": {"/patients": {}}}'}],
    dependencies=["@nestjs/core", "prisma"],
    database_tables=["Patient", "Encounter", "VitalSign", "Claim"],
    detected_entities=entities,
    detected_apis=["/patients"],
    priority_files_inspected=["README.md", "swagger.json", "package.json", "prisma/schema.prisma"]
)

size_bytes = len(dossier.encode("utf-8"))
print(f"[TEST] Dossier generated successfully! Size: {size_bytes} bytes ({round(size_bytes/1024, 2)} KB)")
assert size_bytes < 100 * 1024, "Dossier exceeds 100KB limit!"
print("\n>>> ALL PHASE 2 ENGINE TESTS PASSED SUCCESSFULLY! <<<\n")

