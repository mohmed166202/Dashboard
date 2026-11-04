"""
High-Performance Asynchronous GitHub Webhook Server for Phase 5.
Listens for GitHub webhook events (push, release, repository), validates HMAC-SHA256
signatures, and triggers incremental synchronization in the background.
"""

import concurrent.futures
import hashlib
import hmac
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional

from config import Config
from incremental_sync import IncrementalSyncEngine

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("WebhookServer")

# Thread pool for asynchronous background synchronization tasks
BACKGROUND_WORKERS = concurrent.futures.ThreadPoolExecutor(max_workers=2)

# File patterns that trigger re-extraction and re-classification on push events
RELEVANT_PUSH_PATTERNS = [
    "readme", "docs/", "doc/", "swagger", "openapi", "schema",
    "migrations/", "models/", "entities/", "package.json", "pom.xml",
    "requirements.txt", "docker-compose"
]


def verify_signature(payload_bytes: bytes, signature_header: Optional[str], secret: str) -> bool:
    """Validates the X-Hub-Signature-256 header using HMAC-SHA256."""
    if not secret:
        # If no secret configured, accept but log warning
        return True
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected_sig = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_sig, signature_header)


def should_trigger_on_push(payload: Dict[str, Any]) -> bool:
    """Examines git push commits to see if documentation or schemas were modified."""
    commits = payload.get("commits", [])
    for c in commits:
        modified_files = c.get("added", []) + c.get("modified", []) + c.get("removed", [])
        for file_path in modified_files:
            lower_fp = file_path.lower()
            for pattern in RELEVANT_PUSH_PATTERNS:
                if pattern in lower_fp:
                    return True
    return False


def run_background_sync(repo_full_name: str):
    """Background task executing single-repo incremental sync."""
    try:
        logger.info(f"[WEBHOOK WORKER] Dispatching incremental sync for: {repo_full_name}")
        engine = IncrementalSyncEngine()
        result = engine.sync_repository(repo_full_name, regenerate_dashboard=True)
        logger.info(f"[WEBHOOK WORKER] Finished sync for {repo_full_name}: Primary Domain -> [{result['primary_domain']}]")
    except Exception as e:
        logger.error(f"[WEBHOOK WORKER] Background sync failed for {repo_full_name}: {e}", exc_info=True)


class WebhookRequestHandler(BaseHTTPRequestHandler):
    def _send_response_json(self, status_code: int, data: Dict[str, Any]):
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_GET(self):
        """Health check endpoint."""
        if self.path in ("/", "/health"):
            self._send_response_json(200, {
                "status": "healthy",
                "service": "Healthcare Portfolio Webhook Receiver",
                "secret_configured": bool(Config.GITHUB_WEBHOOK_SECRET)
            })
        else:
            self._send_response_json(404, {"error": "Not Found"})

    def do_POST(self):
        """Processes GitHub Webhook events."""
        if self.path != "/webhook":
            self._send_response_json(404, {"error": "Webhook endpoint is /webhook"})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # 1. Verify HMAC Signature
        sig_header = self.headers.get("X-Hub-Signature-256")
        if not verify_signature(body, sig_header, Config.GITHUB_WEBHOOK_SECRET):
            logger.warning("Rejected webhook request: Invalid HMAC-SHA256 signature.")
            self._send_response_json(401, {"error": "Invalid signature"})
            return

        event_type = self.headers.get("X-GitHub-Event", "unknown")
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            self._send_response_json(400, {"error": "Invalid JSON body"})
            return

        logger.info(f"Received GitHub Webhook Event: '{event_type}'")

        # 2. Event Routing
        if event_type == "ping":
            self._send_response_json(200, {"message": "pong", "zen": payload.get("zen")})
            return

        repo_info = payload.get("repository", {})
        repo_full_name = repo_info.get("full_name")

        if not repo_full_name:
            self._send_response_json(200, {"status": "ignored", "reason": "No repository full_name in payload"})
            return

        # 3. Filter Actions
        trigger_sync = False
        reason = ""

        if event_type == "push":
            ref = payload.get("ref", "")
            default_branch = repo_info.get("default_branch", "main")
            if ref.endswith(f"/{default_branch}") and should_trigger_on_push(payload):
                trigger_sync = True
                reason = "Documentation or architectural schema updated on default branch"
            else:
                reason = "Push ignored (did not modify priority documentation/schema or not on default branch)"

        elif event_type == "release":
            action = payload.get("action")
            if action in ("published", "created"):
                trigger_sync = True
                reason = f"New release {action}: {payload.get('release', {}).get('tag_name')}"
            else:
                reason = f"Release action '{action}' ignored"

        elif event_type == "repository":
            action = payload.get("action")
            if action in ("created", "publicized", "privatized", "renamed"):
                trigger_sync = True
                reason = f"Repository event action '{action}'"
            else:
                reason = f"Repository action '{action}' ignored"

        # 4. Dispatch Async Sync
        if trigger_sync:
            logger.info(f"Queuing sync for '{repo_full_name}': {reason}")
            BACKGROUND_WORKERS.submit(run_background_sync, repo_full_name)
            self._send_response_json(202, {
                "status": "queued",
                "repository": repo_full_name,
                "event": event_type,
                "reason": reason
            })
        else:
            logger.info(f"Event ignored for '{repo_full_name}': {reason}")
            self._send_response_json(200, {
                "status": "ignored",
                "repository": repo_full_name,
                "reason": reason
            })


def start_webhook_server(port: int = 9000, host: str = "0.0.0.0"):
    server_address = (host, port)
    httpd = HTTPServer(server_address, WebhookRequestHandler)
    logger.info(f"Webhook receiver listening on http://{host}:{port}/webhook")
    logger.info(f"HMAC Authentication: {'ENABLED (Secret set)' if Config.GITHUB_WEBHOOK_SECRET else 'DISABLED (No secret set in .env)'}")
    print(f"\n[WEBHOOK SERVER] Ready to receive events on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping webhook server...")
        httpd.server_close()

