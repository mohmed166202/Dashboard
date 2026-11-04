"""
Dossier Builder for Phase 2.
Synthesizes extracted documentation, architecture specs, dependencies, and database models
into a unified 'Project Synthesis Dossier' under 100KB of clean markdown.
"""

import re
from typing import Any, Dict, List, Optional, Set

# Target max size: 85 KB (well under the 100 KB hard requirement)
MAX_DOSSIER_BYTES = 85 * 1024


class DossierBuilder:
    @staticmethod
    def sanitize_markdown(text: str) -> str:
        """Removes excessive whitespace, giant base64 strings, and cleans text."""
        # Remove data URIs and giant base64 blocks
        text = re.sub(r"data:image/[^;]+;base64,[A-Za-z0-9+/=]{100,}", "[IMAGE_DATA_REMOVED]", text)
        # Collapse excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @classmethod
    def truncate_to_limit(cls, text: str, max_bytes: int = MAX_DOSSIER_BYTES) -> str:
        """Ensures the text is under max_bytes, keeping the head and tail intact."""
        encoded = text.encode("utf-8")
        if len(encoded) <= max_bytes:
            return text

        # Preserve top 70% and bottom 20%
        head_bytes = int(max_bytes * 0.70)
        tail_bytes = int(max_bytes * 0.20)
        truncation_notice = "\n\n... [EXCERPT TRUNCATED TO MAINTAIN <100KB DOSSIER LIMIT] ...\n\n"

        head_part = encoded[:head_bytes].decode("utf-8", errors="ignore")
        tail_part = encoded[-tail_bytes:].decode("utf-8", errors="ignore")
        return head_part + truncation_notice + tail_part

    @classmethod
    def build_dossier(
        cls,
        repo_metadata: Dict[str, Any],
        doc_contents: List[Dict[str, str]],        # Priority 1: [{'path': p, 'content': c}]
        spec_contents: List[Dict[str, str]],       # Priority 2: [{'path': p, 'content': c}]
        dependencies: List[str],                   # Priority 3
        database_tables: List[str],                # Priority 4
        detected_entities: Set[str],               # Detected medical/operational entities
        detected_apis: List[str],                  # Discovered API endpoints
        priority_files_inspected: List[str]
    ) -> str:
        """Assembles the Project Synthesis Dossier."""
        repo_name = repo_metadata.get("name", "Unknown Repo")
        name_with_owner = repo_metadata.get("name_with_owner", repo_name)
        description = repo_metadata.get("description") or "No description provided."
        primary_lang = repo_metadata.get("primary_language") or "Not detected"
        topics = repo_metadata.get("topics", [])
        default_branch = repo_metadata.get("default_branch") or "main"
        pushed_at = repo_metadata.get("pushed_at") or "N/A"
        is_private = "Private" if repo_metadata.get("is_private") else "Public"
        is_archived = "Archived" if repo_metadata.get("is_archived") else "Active"
        disk_usage = f"{repo_metadata.get('disk_usage_kb', 0):,} KB"

        sections = []

        # Header
        sections.append(f"# Project Synthesis Dossier: `{name_with_owner}`\n")

        # 1. Executive Metadata
        topics_str = ", ".join([f"`{t}`" for t in topics]) if topics else "None"
        sections.append("## 1. Repository Executive Profile\n")
        sections.append(
            f"- **Repository:** `{name_with_owner}`\n"
            f"- **Status / Visibility:** {is_archived} | {is_private}\n"
            f"- **Primary Language:** {primary_lang}\n"
            f"- **Default Branch:** `{default_branch}`\n"
            f"- **Last Pushed:** `{pushed_at}`\n"
            f"- **Codebase Size:** {disk_usage}\n"
            f"- **Topics & Tags:** {topics_str}\n"
            f"- **Description:** {description}\n"
        )

        # 2. Healthcare & Operational Entity Highlights
        sections.append("## 2. Detected Domain Entities & Operational Keywords\n")
        if detected_entities:
            sorted_entities = sorted(list(detected_entities))
            chips = " ".join([f"`{e}`" for e in sorted_entities])
            sections.append(f"**Identified Domain Signatures ({len(sorted_entities)}):**\n{chips}\n")
        else:
            sections.append("*No specialized healthcare domain keywords detected in primary signatures.*\n")

        # 3. Database Schemas & Data Models (Priority 4)
        sections.append("## 3. Discovered Data Models & Schemas\n")
        if database_tables:
            table_list = ", ".join([f"`{t}`" for t in database_tables[:40]])
            sections.append(f"**Discovered Tables / Models ({len(database_tables)}):**\n{table_list}\n")
        else:
            sections.append("*No relational tables or schema definitions detected in inspected files.*\n")

        # 4. Dependencies, Frameworks & Services (Priority 3)
        sections.append("## 4. Dependencies, Frameworks & Services\n")
        if dependencies:
            dep_chips = ", ".join([f"`{d}`" for d in dependencies[:30]])
            sections.append(f"**Manifest Components ({len(dependencies)}):**\n{dep_chips}\n")
        else:
            sections.append("*No standard dependency manifests found in priority root paths.*\n")

        # 5. API Endpoints & Interfaces (Priority 2)
        sections.append("## 5. API Endpoints & Contract Interfaces\n")
        if detected_apis:
            api_list = "\n".join([f"- `{a}`" for a in detected_apis[:20]])
            sections.append(f"**Discovered API Paths / Operations ({len(detected_apis)}):**\n{api_list}\n")
        else:
            sections.append("*No OpenAPI/Swagger specs or Postman collections found.*\n")

        # 6. Core Documentation & Architectural Notes (Priority 1)
        sections.append("## 6. Core Documentation & Architectural Excerpts\n")
        if doc_contents:
            for item in doc_contents[:5]:
                path = item.get("path", "")
                raw_c = item.get("content", "")
                clean_c = cls.sanitize_markdown(raw_c)
                # Cap individual document excerpt to 25KB
                if len(clean_c.encode("utf-8")) > 25 * 1024:
                    clean_c = clean_c[:25000] + "\n... [Remaining doc content omitted for brevity] ...\n"
                sections.append(f"### Excerpt from `{path}`:\n\n{clean_c}\n")
        else:
            sections.append("*No markdown documentation or README found in priority tree scan.*\n")

        # 7. Priority Files Inspected
        sections.append("## 7. Audit Manifest: Inspected Priority Files\n")
        if priority_files_inspected:
            file_manifest = "\n".join([f"- `{f}`" for f in priority_files_inspected])
            sections.append(file_manifest + "\n")
        else:
            sections.append("*Zero prioritized files matched tree inspection filter.*\n")

        full_dossier = "\n".join(sections)
        return cls.truncate_to_limit(full_dossier, MAX_DOSSIER_BYTES)

