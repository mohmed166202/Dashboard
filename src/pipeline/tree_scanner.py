"""
Tree Scanner for Phase 2.
Fetches repository git tree via GitHub Trees API (recursive=1) and prioritizes
target documentation, specs, configurations, and database schemas.
"""

import fnmatch
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("TreeScanner")

# Directories to skip immediately during tree inspection
IGNORE_DIR_PATTERNS = {
    "node_modules", "vendor", "dist", "build", "target", ".git", ".github",
    ".idea", ".vscode", "venv", ".venv", "env", "__pycache__", "coverage",
    ".next", ".nuxt", "out", "bin", "obj", ".pytest_cache", ".mypy_cache"
}

# Priority 1: Core Documentation
P1_PATTERNS = [
    "readme*", "read_me*", "docs/**/*.md", "doc/**/*.md", "documentation/**/*.md",
    "wiki/**/*.md", "architecture.md", "specs/**/*.md", "overview.md", "design.md"
]

# Priority 2: Architecture, ADRs, and API Specifications
P2_PATTERNS = [
    "*swagger*.json", "*swagger*.yaml", "*swagger*.yml",
    "*openapi*.json", "*openapi*.yaml", "*openapi*.yml",
    "*postman_collection*.json", "docs/adr/*.md", "adr/*.md",
    "architecture/**/*.md", "api-spec*.*"
]

# Priority 3: Configuration, Dependencies, and Container Orchestration
P3_PATTERNS = [
    "package.json", "requirements.txt", "pyproject.toml", "pipfile",
    "pom.xml", "build.gradle", "build.gradle.kts", "go.mod", "cargo.toml",
    "composer.json", "gemfile", "docker-compose*.yml", "docker-compose*.yaml",
    "dockerfile*", "chart.yaml", "values.yaml", ".env.example"
]

# Priority 4: Database Schemas, Migrations, and Domain Models
P4_PATTERNS = [
    "*schema.prisma", "*schema.sql", "*init.sql", "migrations/**/*.sql",
    "db/migrate/**/*.rb", "models/**/*.py", "models/**/*.ts", "models/**/*.js",
    "entities/**/*.ts", "entities/**/*.java", "entities/**/*.cs"
]


class TreeScanner:
    @staticmethod
    def is_ignored_path(path: str) -> bool:
        """Check if path falls under vendor or build artifacts."""
        parts = path.lower().replace("\\", "/").split("/")
        for p in parts[:-1]:  # check directories
            if p in IGNORE_DIR_PATTERNS:
                return True
        return False

    @classmethod
    def match_priority(cls, path: str) -> Optional[int]:
        """Classify a tree path into Priority 1, 2, 3, 4, or None."""
        lower_path = path.lower().replace("\\", "/")
        
        # Priority 1
        for pat in P1_PATTERNS:
            if fnmatch.fnmatch(lower_path, pat) or fnmatch.fnmatch(lower_path.split("/")[-1], pat):
                return 1

        # Priority 2
        for pat in P2_PATTERNS:
            if fnmatch.fnmatch(lower_path, pat) or fnmatch.fnmatch(lower_path.split("/")[-1], pat):
                return 2

        # Priority 3
        for pat in P3_PATTERNS:
            if fnmatch.fnmatch(lower_path, pat) or fnmatch.fnmatch(lower_path.split("/")[-1], pat):
                return 3

        # Priority 4
        for pat in P4_PATTERNS:
            if fnmatch.fnmatch(lower_path, pat) or fnmatch.fnmatch(lower_path.split("/")[-1], pat):
                return 4

        return None

    @classmethod
    def filter_tree(cls, tree_nodes: List[Dict[str, Any]], max_files_per_priority: int = 15) -> Dict[int, List[Dict[str, Any]]]:
        """
        Filters and groups git tree nodes into prioritized tiers,
        pruning unwanted directories and capping file counts.
        """
        categorized: Dict[int, List[Dict[str, Any]]] = {1: [], 2: [], 3: [], 4: []}

        for node in tree_nodes:
            # Only consider blobs (files), ignore sub-trees
            if node.get("type") != "blob":
                continue

            path = node.get("path", "")
            if cls.is_ignored_path(path):
                continue

            priority = cls.match_priority(path)
            if priority and len(categorized[priority]) < max_files_per_priority:
                categorized[priority].append(node)

        return categorized

