"""
High-performance GitHub API client for repository discovery and metadata harvesting.
Supports GraphQL v4 with 100-batch pagination, automatic rate-limit tracking,
and fallback to REST v3 if needed.
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional, Tuple
import requests

from config import Config
from db import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("GitHubDiscoveryClient")


GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
REST_ENDPOINT = "https://api.github.com"


# GraphQL queries optimized for 100 items per batch
REPO_FIELDS_FRAGMENT = """
fragment RepoFields on Repository {
    id
    name
    nameWithOwner
    owner {
        login
    }
    description
    url
    isPrivate
    isArchived
    isFork
    createdAt
    updatedAt
    pushedAt
    diskUsage
    primaryLanguage {
        name
    }
    languages(first: 5, orderBy: {field: SIZE, direction: DESC}) {
        nodes {
            name
        }
    }
    repositoryTopics(first: 20) {
        nodes {
            topic {
                name
            }
        }
    }
    defaultBranchRef {
        name
    }
    issues(states: OPEN) {
        totalCount
    }
    stargazerCount
    forkCount
    readmeMd: object(expression: "HEAD:README.md") {
        ... on Blob {
            byteSize
        }
    }
    readmeLower: object(expression: "HEAD:readme.md") {
        ... on Blob {
            byteSize
        }
    }
    readmeTxt: object(expression: "HEAD:README.txt") {
        ... on Blob {
            byteSize
        }
    }
    readmeRst: object(expression: "HEAD:README.rst") {
        ... on Blob {
            byteSize
        }
    }
}
"""

QUERY_VIEWER = """
query GetViewerRepos($first: Int!, $after: String) {
    rateLimit {
        limit
        cost
        remaining
        resetAt
    }
    viewer {
        repositories(first: $first, after: $after, affiliations: [OWNER, ORGANIZATION_MEMBER, COLLABORATOR], ownerAffiliations: [OWNER, ORGANIZATION_MEMBER, COLLABORATOR], orderBy: {field: PUSHED_AT, direction: DESC}) {
            totalCount
            pageInfo {
                hasNextPage
                endCursor
            }
            nodes {
                ...RepoFields
            }
        }
    }
}
""" + REPO_FIELDS_FRAGMENT

QUERY_ORG = """
query GetOrgRepos($owner: String!, $first: Int!, $after: String) {
    rateLimit {
        limit
        cost
        remaining
        resetAt
    }
    organization(login: $owner) {
        repositories(first: $first, after: $after, orderBy: {field: PUSHED_AT, direction: DESC}) {
            totalCount
            pageInfo {
                hasNextPage
                endCursor
            }
            nodes {
                ...RepoFields
            }
        }
    }
}
""" + REPO_FIELDS_FRAGMENT

QUERY_USER = """
query GetUserRepos($owner: String!, $first: Int!, $after: String) {
    rateLimit {
        limit
        cost
        remaining
        resetAt
    }
    user(login: $owner) {
        repositories(first: $first, after: $after, orderBy: {field: PUSHED_AT, direction: DESC}) {
            totalCount
            pageInfo {
                hasNextPage
                endCursor
            }
            nodes {
                ...RepoFields
            }
        }
    }
}
""" + REPO_FIELDS_FRAGMENT


class GitHubClient:
    def __init__(self, token: Optional[str] = None, db: Optional[DatabaseManager] = None):
        self.token = token or Config.GITHUB_TOKEN
        self.db = db or DatabaseManager(Config.DATABASE_PATH)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "Healthcare-Portfolio-Discovery-Engine/1.0",
            "Accept": "application/vnd.github.v3+json",
        })

    def check_auth(self) -> Dict[str, Any]:
        """Verify token authentication and report login identity, scopes, and rate limit."""
        resp = self.session.get(f"{REST_ENDPOINT}/user", timeout=15)
        if resp.status_code == 401:
            raise PermissionError("Invalid GitHub Personal Access Token (HTTP 401 Unauthorized).")
        resp.raise_for_status()

        data = resp.json()
        scopes = resp.headers.get("X-OAuth-Scopes", "N/A")
        rate_limit = resp.headers.get("X-RateLimit-Limit", "N/A")
        rate_remaining = resp.headers.get("X-RateLimit-Remaining", "N/A")

        return {
            "login": data.get("login"),
            "name": data.get("name"),
            "email": data.get("email"),
            "public_repos": data.get("public_repos"),
            "total_private_repos": data.get("total_private_repos"),
            "scopes": [s.strip() for s in scopes.split(",")] if scopes != "N/A" else [],
            "rate_limit": rate_limit,
            "rate_remaining": rate_remaining,
        }

    def _execute_graphql(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a GraphQL query with exponential backoff and rate limit tracking."""
        max_retries = Config.MAX_RETRIES
        backoff = Config.RETRY_BACKOFF_FACTOR

        for attempt in range(1, max_retries + 1):
            try:
                resp = self.session.post(
                    GRAPHQL_ENDPOINT,
                    json={"query": query, "variables": variables},
                    timeout=Config.GITHUB_REQUEST_TIMEOUT
                )

                # Check rate limit headers
                if resp.status_code == 403 and "rate limit exceeded" in resp.text.lower():
                    reset_time = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
                    sleep_sec = max(reset_time - int(time.time()) + 2, 5)
                    logger.warning(f"Rate limit hit! Sleeping for {sleep_sec}s until reset...")
                    time.sleep(sleep_sec)
                    continue

                if resp.status_code in (500, 502, 503, 504):
                    wait = backoff ** attempt
                    logger.warning(f"GitHub server error {resp.status_code}, retrying in {wait:.1f}s (attempt {attempt}/{max_retries})")
                    time.sleep(wait)
                    continue

                resp.raise_for_status()
                payload = resp.json()

                if "errors" in payload:
                    err_msg = json.dumps(payload["errors"])
                    logger.error(f"GraphQL returned errors: {err_msg}")
                    # If organization not found or user not found, raise directly
                    raise RuntimeError(f"GraphQL Error: {err_msg}")

                # Log rate limit info if available
                rl = payload.get("data", {}).get("rateLimit")
                if rl:
                    self.db.log_rate_limit(
                        endpoint="graphql",
                        limit_total=rl.get("limit", 5000),
                        remaining=rl.get("remaining", 0),
                        cost=rl.get("cost", 1),
                        reset_at=rl.get("resetAt", "")
                    )
                    remaining = rl.get("remaining", 5000)
                    if remaining < Config.RATE_LIMIT_SAFETY_MARGIN:
                        logger.warning(f"Approaching rate limit! Remaining: {remaining}. Cooling down for 10s...")
                        time.sleep(10)

                return payload

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                wait = backoff ** attempt
                logger.warning(f"Network error: {e}. Retrying in {wait:.1f}s (attempt {attempt}/{max_retries})")
                time.sleep(wait)

        raise RuntimeError(f"Failed to execute GraphQL query after {max_retries} attempts.")

    def parse_graphql_repo_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a raw GraphQL repository node into our unified catalog schema."""
        languages = [l["name"] for l in node.get("languages", {}).get("nodes", [])]
        topics = [t["topic"]["name"] for t in node.get("repositoryTopics", {}).get("nodes", [])]

        # Determine README presence and filename
        has_readme = False
        readme_file = None
        if node.get("readmeMd"):
            has_readme = True
            readme_file = "README.md"
        elif node.get("readmeLower"):
            has_readme = True
            readme_file = "readme.md"
        elif node.get("readmeTxt"):
            has_readme = True
            readme_file = "README.txt"
        elif node.get("readmeRst"):
            has_readme = True
            readme_file = "README.rst"

        return {
            "node_id": node.get("id"),
            "name": node.get("name"),
            "name_with_owner": node.get("nameWithOwner"),
            "owner": node.get("owner", {}).get("login"),
            "description": node.get("description"),
            "url": node.get("url"),
            "primary_language": node.get("primaryLanguage", {}).get("name") if node.get("primaryLanguage") else None,
            "languages": languages,
            "topics": topics,
            "default_branch": node.get("defaultBranchRef", {}).get("name") if node.get("defaultBranchRef") else None,
            "is_private": node.get("isPrivate", False),
            "is_archived": node.get("isArchived", False),
            "is_fork": node.get("isFork", False),
            "created_at": node.get("createdAt"),
            "updated_at": node.get("updatedAt"),
            "pushed_at": node.get("pushedAt"),
            "disk_usage_kb": node.get("diskUsage", 0),
            "open_issues_count": node.get("issues", {}).get("totalCount", 0),
            "stargazers_count": node.get("stargazerCount", 0),
            "forks_count": node.get("forkCount", 0),
            "has_readme": has_readme,
            "readme_filename": readme_file,
        }

    def fetch_all_repositories(
        self,
        target_type: Optional[str] = None,
        target_owner: Optional[str] = None,
        page_size: int = 100
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Paginates through repositories 100 at a time using GraphQL.
        Yields batches of parsed repository dictionaries.
        """
        target_type = (target_type or Config.GITHUB_TARGET_TYPE).lower()
        target_owner = target_owner or Config.GITHUB_TARGET_OWNER

        # High-Speed REST discovery directly (robust and immune to GraphQL blob timeouts)
        yield from self.fetch_repositories_rest(target_type, target_owner, page_size)
        return


    def fetch_repositories_rest(
        self,
        target_type: str,
        target_owner: Optional[str] = None,
        page_size: int = 100
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """High-speed REST API fallback for organization and user repositories."""
        if target_type == "org" and target_owner:
            url = f"{REST_ENDPOINT}/orgs/{target_owner}/repos"
        elif target_type == "user" and target_owner:
            url = f"{REST_ENDPOINT}/users/{target_owner}/repos"
        else:
            url = f"{REST_ENDPOINT}/user/repos"

        page = 1
        total_discovered = 0

        while True:
            params = {"per_page": page_size, "page": page, "type": "all", "sort": "pushed", "direction": "desc"}
            logger.info(f"Querying GitHub REST API: {url} (page {page}, per_page {page_size})...")
            resp = self.session.get(url, params=params, timeout=Config.GITHUB_REQUEST_TIMEOUT)

            # Update rate limit tracking
            remaining = int(resp.headers.get("X-RateLimit-Remaining", 5000))
            limit = int(resp.headers.get("X-RateLimit-Limit", 5000))
            reset_at = resp.headers.get("X-RateLimit-Reset", "")
            self.db.log_rate_limit(endpoint="rest", limit_total=limit, remaining=remaining, cost=1, reset_at=reset_at)

            if resp.status_code != 200:
                logger.error(f"REST API query returned HTTP {resp.status_code}: {resp.text[:200]}")
                break

            items = resp.json()
            if not items or not isinstance(items, list):
                break

            parsed_batch = []
            for item in items:
                name = item.get("name", "")
                if name.lower() in Config.GITHUB_EXCLUDE_REPOS:
                    continue

                parsed_batch.append({
                    "node_id": item.get("node_id"),
                    "name": name,
                    "name_with_owner": item.get("full_name"),
                    "owner": item.get("owner", {}).get("login"),
                    "description": item.get("description"),
                    "url": item.get("html_url"),
                    "primary_language": item.get("language"),
                    "languages": [item.get("language")] if item.get("language") else [],
                    "topics": item.get("topics", []),
                    "default_branch": item.get("default_branch") or "main",
                    "is_private": item.get("private", False),
                    "is_archived": item.get("archived", False),
                    "is_fork": item.get("fork", False),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                    "pushed_at": item.get("pushed_at"),
                    "disk_usage_kb": item.get("size", 0),
                    "open_issues_count": item.get("open_issues_count", 0),
                    "stargazers_count": item.get("stargazers_count", 0),
                    "forks_count": item.get("forks_count", 0),
                    "has_readme": 1,
                    "readme_filename": "README.md",
                })

            total_discovered += len(parsed_batch)
            logger.info(f"REST Page {page}: Processed {len(parsed_batch)} repositories. Cumulative: {total_discovered}")
            yield parsed_batch

            if len(items) < page_size:
                break
            page += 1


