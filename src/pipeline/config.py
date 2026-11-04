"""
Configuration manager for Healthcare Portfolio Intelligence.
Loads settings from .env and environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import List, Optional


def load_dotenv(env_path: Optional[Path] = None) -> dict:
    """Lightweight built-in .env parser without external dependencies."""
    if env_path is None:
        env_path = Path(__file__).resolve().parent / ".env"
    
    loaded = {}
    if not env_path.exists():
        return loaded

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    # Set into os.environ if not already set
                    if key not in os.environ:
                        os.environ[key] = val
                    loaded[key] = val
    except Exception as e:
        print(f"[WARN] Error reading .env file: {e}")
    return loaded


# Preload .env on import
load_dotenv()


class Config:
    # GitHub Authentication
    GITHUB_TOKEN: str = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()
    GITHUB_TARGET_TYPE: str = os.getenv("GITHUB_TARGET_TYPE", "viewer").strip().lower()
    GITHUB_TARGET_OWNER: str = os.getenv("GITHUB_TARGET_OWNER", "").strip()
    
    # Excluded repos
    _exclude_raw = os.getenv("GITHUB_EXCLUDE_REPOS", ".github,sandbox-test")
    GITHUB_EXCLUDE_REPOS: List[str] = [r.strip().lower() for r in _exclude_raw.split(",") if r.strip()]

    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "healthcare_portfolio_catalog.db").strip()

    # Performance
    GRAPHQL_PAGE_SIZE: int = int(os.getenv("GRAPHQL_PAGE_SIZE", "100"))
    GITHUB_REQUEST_TIMEOUT: int = int(os.getenv("GITHUB_REQUEST_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "5"))

    RETRY_BACKOFF_FACTOR: float = float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0"))
    RATE_LIMIT_SAFETY_MARGIN: int = int(os.getenv("RATE_LIMIT_SAFETY_MARGIN", "50"))

    # LLM (Phases 3+)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro").strip()

    # Continuous Sync & Webhooks (Phase 5)
    GITHUB_WEBHOOK_SECRET: str = os.getenv("GITHUB_WEBHOOK_SECRET", "").strip()
    WEBHOOK_PORT: int = int(os.getenv("WEBHOOK_PORT", "9000"))
    SYNC_INTERVAL_HOURS: int = int(os.getenv("SYNC_INTERVAL_HOURS", "6"))


    @classmethod
    def validate_github_creds(cls) -> bool:
        """Validates that a GitHub personal access token is present."""
        if not cls.GITHUB_TOKEN or cls.GITHUB_TOKEN == "your_github_token_here":
            return False
        return True

    @classmethod
    def get_summary(cls) -> dict:
        token_masked = f"{cls.GITHUB_TOKEN[:4]}...{cls.GITHUB_TOKEN[-4:]}" if len(cls.GITHUB_TOKEN) > 8 else ("Set" if cls.GITHUB_TOKEN else "Missing")
        return {
            "github_token": token_masked,
            "target_type": cls.GITHUB_TARGET_TYPE,
            "target_owner": cls.GITHUB_TARGET_OWNER or "(Viewer / All accessible repos)",
            "database_path": cls.DATABASE_PATH,
            "graphql_page_size": cls.GRAPHQL_PAGE_SIZE,
            "excluded_repos": cls.GITHUB_EXCLUDE_REPOS,
        }

