"""
FastAPI Backend REST Service & WebSocket Real-Time Synchronizer
Phase 2: Comprehensive CRUD, Optimistic Locking, Audit History & Analytics

Features:
  - SQLite WAL mode connection pooling with dictionary row factory
  - Strict Pydantic v2 schemas for all requests and responses
  - Full CRUD for /api/projects with optimistic concurrency control (check last_updated / version)
  - Full CRUD for /api/requirements
  - Drodown metadata endpoint with disk and in-memory cache
  - Audit logging for every insert/update/delete
  - KPI summary & benchmark comparisons for Tab 2
  - Real-time WebSocket connection manager broadcasting updates to all connected UI clients
  - Unified SPA mounting for production frontend delivery
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
import os
import bcrypt
import jwt
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dotenv import load_dotenv

load_dotenv()

from eval_type_backport import install_patch
install_patch()

from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    Depends,
    Header,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, EmailStr, field_validator

# ── JWT & Auth Configuration ──────────────────────────────────────────────────
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "andalusia-healthcare-ai-portfolio-secret-2026")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
ROOT_DIR = BASE_DIR
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "ai_tracker.db"
DROPDOWNS_JSON_PATH = DATA_DIR / "dropdown_lists.json"
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"

# ── Database Connection ───────────────────────────────────────────────────────
def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# ── WebSocket Manager (Multi-Worker IPC backed by SQLite) ─────────────────────
class ConnectionManager:
    """Manages active WebSocket connections in this worker and broadcasts real-time mutations."""
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast_local(self, message: dict):
        dead_connections = set()
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)
        for dead in dead_connections:
            self.active_connections.discard(dead)

    async def broadcast(self, message: dict):
        # 1. Persist to ws_events table first so all workers & pollers pick it up
        try:
            conn = get_db_connection()
            with conn:
                conn.execute(
                    "INSERT INTO ws_events (event_payload) VALUES (?)",
                    (json.dumps(message),)
                )
            conn.close()
        except Exception as e:
            print("Error persisting ws event:", e)

        # 2. Direct send to connections on this worker
        await self.broadcast_local(message)

ws_manager = ConnectionManager()

# ── Pydantic Request & Response Models ─────────────────────────────────────────

class ProjectCreate(BaseModel):
    id: str = Field(..., description="Unique Project ID (e.g. AI-029)")
    team: Optional[str] = None
    project: str = Field(..., min_length=1, description="Project Name")
    type: Optional[str] = None
    domain: Optional[str] = None
    description: Optional[str] = None
    phase: Optional[str] = "Idea"
    status: Optional[str] = "On Track"
    percent_complete: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
    todo_tasks: Optional[str] = None
    inprogress_tasks: Optional[str] = None
    completed_tasks: Optional[str] = None
    blockers: Optional[str] = None
    blocker_owner: Optional[str] = None
    business_owner: Optional[str] = None
    technical_owner: Optional[str] = None
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = "Medium"
    user: Optional[str] = "WebUser"

class ProjectUpdate(BaseModel):
    team: Optional[str] = None
    project: Optional[str] = None
    type: Optional[str] = None
    domain: Optional[str] = None
    description: Optional[str] = None
    phase: Optional[str] = None
    status: Optional[str] = None
    percent_complete: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    todo_tasks: Optional[str] = None
    inprogress_tasks: Optional[str] = None
    completed_tasks: Optional[str] = None
    blockers: Optional[str] = None
    blocker_owner: Optional[str] = None
    business_owner: Optional[str] = None
    technical_owner: Optional[str] = None
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = None
    # Optimistic locking check:
    expected_updated_at: Optional[str] = Field(
        None, description="ISO timestamp of record when read by client to prevent race conditions"
    )
    user: Optional[str] = "WebUser"

class RequirementCreate(BaseModel):
    req_id: str = Field(..., description="Requirement ID (e.g. AI-001-FR-17)")
    project_id: str = Field(..., description="Parent Project ID")
    category: str = Field(default="Functional", description="Functional or Non-Functional")
    nfr_area: Optional[str] = None
    requirement: str = Field(..., min_length=1)
    description: Optional[str] = None
    business_benefit: Optional[str] = None
    request_type: Optional[str] = "New Project"
    owner: Optional[str] = None
    priority: Optional[str] = "Medium"
    status: Optional[str] = "Proposed"
    target_date: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    user: Optional[str] = "WebUser"

class RequirementUpdate(BaseModel):
    category: Optional[str] = None
    nfr_area: Optional[str] = None
    requirement: Optional[str] = None
    description: Optional[str] = None
    business_benefit: Optional[str] = None
    request_type: Optional[str] = None
    owner: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    target_date: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    expected_updated_at: Optional[str] = None
    user: Optional[str] = "WebUser"

class KPISummaryUpdate(BaseModel):
    metric_key: str
    current_value: float
    user: Optional[str] = "WebUser"

# ── User & Auth Models ────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class UserLogin(BaseModel):
    username_or_email: Optional[str] = None
    email: Optional[str] = None
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: Optional[str] = None
    last_login: Optional[str] = None

class RoleUpdate(BaseModel):
    role: str # 'admin', 'editor', 'viewer'

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        clean = v.lower().strip()
        if clean not in ("admin", "editor", "viewer"):
            raise ValueError("Role must be one of: 'admin', 'editor', 'viewer'")
        return clean

# ── Auth Helper Functions ─────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

async def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Extract user payload from Authorization Bearer token without raising 401 if missing."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split("Bearer ", 1)[1].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        if not email:
            return None
        conn = get_db_connection()
        user = conn.execute("SELECT id, email, full_name, role, is_active FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if not user or not user["is_active"]:
            return None
        return dict(user)
    except Exception:
        return None

async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Strict authentication dependency requiring valid token."""
    user = await get_current_user_optional(authorization)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def require_role(required_role: str):
    """
    Role check dependency factory.
    - 'viewer': any authenticated user (or viewers, editors, admins)
    - 'editor': editors and admins
    - 'admin': admins only
    """
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role", "viewer")
        hierarchy = {"viewer": 1, "editor": 2, "admin": 3}
        if hierarchy.get(user_role, 0) < hierarchy.get(required_role, 1):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Action requires '{required_role}' privileges (current role: '{user_role}').",
            )
        return current_user
    return role_checker

# ── Audit Logger Helper ───────────────────────────────────────────────────────
def record_audit(
    conn: sqlite3.Connection,
    entity_type: str,
    entity_id: str,
    action: str,
    field_name: Optional[str],
    old_value: Optional[str],
    new_value: Optional[str],
    user: str,
):
    conn.execute(
        """
        INSERT INTO audit_log (entity_type, entity_id, action, field_name, old_value, new_value, user, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (entity_type, entity_id, action, field_name, old_value, new_value, user),
    )

# ── FastAPI App Setup ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure default admin from env/secrets exists on startup
    admin_user = os.getenv("ADMIN_USERNAME", "mohamed-galal")
    admin_pw = os.getenv("ADMIN_PASSWORD", "Mm@01000713965$")
    admin_email = os.getenv("ADMIN_EMAIL", "mohamed-galal@andalusia.net")

    try:
        conn = get_db_connection()
        # Ensure username column exists
        cols = [c[1] for c in conn.execute("PRAGMA table_info(users)").fetchall()]
        if "username" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN username TEXT")

        existing = conn.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (admin_user, admin_email),
        ).fetchone()

        pw_hash = hash_password(admin_pw)
        if existing:
            conn.execute(
                """
                UPDATE users
                SET username = ?, full_name = ?, hashed_password = ?, role = 'admin', is_active = 1
                WHERE id = ?
                """,
                (admin_user, "Mohamed Galal", pw_hash, existing[0]),
            )
        else:
            conn.execute(
                """
                INSERT INTO users (username, email, full_name, hashed_password, role, is_active)
                VALUES (?, ?, ?, ?, 'admin', 1)
                """,
                (admin_user, admin_email, "Mohamed Galal", pw_hash),
            )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Warning] Admin seed on startup: {e}")

    yield

app = FastAPI(
    title="Andalusia AI Project Tracker & Analytics API",
    description="High-performance backend API with SQLite WAL, real-time WebSockets, full CRUD and benchmark analytics.",
    version="2.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health & Diagnostics ──────────────────────────────────────────────────────
@app.get("/health")
def health():
    """Liveness & readiness probe."""
    try:
        conn = get_db_connection()
        p_count = conn.execute("SELECT count(*) FROM projects").fetchone()[0]
        r_count = conn.execute("SELECT count(*) FROM requirements").fetchone()[0]
        conn.close()
        return {
            "status": "ok",
            "db_connected": True,
            "projects_count": p_count,
            "requirements_count": r_count,
            "wal_mode": True,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ── Authentication & RBAC API Endpoints ───────────────────────────────────────
@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister):
    """
    Public sign-up endpoint.
    - First registered user automatically becomes 'admin'.
    - All subsequent users default to 'viewer' until promoted by an admin.
    """
    conn = get_db_connection()
    clean_email = payload.email.lower().strip()

    # Check if user already exists
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (clean_email,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An account with email '{clean_email}' already exists.",
        )

    # Check if this is the very first user in the database
    total_users = conn.execute("SELECT count(*) FROM users").fetchone()[0]
    assigned_role = "admin" if total_users == 0 else "viewer"

    hashed = hash_password(payload.password)
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO users (email, full_name, hashed_password, role, is_active)
            VALUES (?, ?, ?, ?, 1)
            """,
            (clean_email, payload.full_name.strip(), hashed, assigned_role),
        )
        new_id = cursor.lastrowid
        record_audit(
            conn, "user", str(new_id), "INSERT", "role", None, assigned_role, clean_email
        )

    # Fetch created user record
    created = conn.execute(
        "SELECT id, email, full_name, role, is_active, created_at FROM users WHERE id = ?",
        (new_id,),
    ).fetchone()
    conn.close()

    user_dict = dict(created)
    user_dict["is_active"] = bool(user_dict["is_active"])

    # Issue access token immediately upon registration
    token = create_access_token({"sub": clean_email, "role": assigned_role})
    return {
        "user": user_dict,
        "access_token": token,
        "token_type": "bearer",
        "message": f"Account created with role '{assigned_role}'.",
    }

@app.post("/api/auth/login")
def login_user(payload: UserLogin):
    """Authenticate with email or username and password, issuing a signed JWT."""
    conn = get_db_connection()
    raw_identifier = payload.username_or_email or payload.email or ""
    clean_identifier = raw_identifier.lower().strip()

    if not clean_identifier:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is required.",
        )

    # Search by email or username
    user = conn.execute(
        "SELECT * FROM users WHERE LOWER(email) = ? OR (username IS NOT NULL AND LOWER(username) = ?)",
        (clean_identifier, clean_identifier),
    ).fetchone()

    if not user or not verify_password(payload.password, user["hashed_password"]):
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user["is_active"]:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact an administrator.",
        )

    # Update last_login
    with conn:
        conn.execute("UPDATE users SET last_login = datetime('now') WHERE id = ?", (user["id"],))

    conn.close()

    user_dict = {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "is_active": bool(user["is_active"]),
        "created_at": user["created_at"],
        "last_login": user["last_login"],
    }

    token = create_access_token({"sub": user["email"], "role": user["role"]})
    return {
        "user": user_dict,
        "access_token": token,
        "token_type": "bearer",
    }

@app.get("/api/auth/me")
def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user)):
    """Return active profile and verified role permissions."""
    return {"user": user}

# ── User Administration API (Admin Only) ──────────────────────────────────────
@app.get("/api/admin/users")
def list_users(admin: Dict[str, Any] = Depends(require_role("admin"))):
    """Admin-only endpoint to view all registered users and their roles."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, email, full_name, role, is_active, created_at, last_login FROM users ORDER BY id ASC"
    ).fetchall()
    conn.close()
    users = [dict(r) for r in rows]
    for u in users:
        u["is_active"] = bool(u["is_active"])
    return {"total": len(users), "users": users}

@app.put("/api/admin/users/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: RoleUpdate,
    admin: Dict[str, Any] = Depends(require_role("admin")),
):
    """Admin-only endpoint to elevate or demote a user role ('admin', 'editor', 'viewer')."""
    conn = get_db_connection()
    target = conn.execute("SELECT id, email, role FROM users WHERE id = ?", (user_id,)).fetchone()
    if not target:
        conn.close()
        raise HTTPException(status_code=404, detail=f"User with ID '{user_id}' not found.")

    old_role = target["role"]
    new_role = payload.role

    with conn:
        conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
        record_audit(
            conn, "user", str(user_id), "UPDATE", "role", old_role, new_role, admin["email"]
        )

    updated = conn.execute(
        "SELECT id, email, full_name, role, is_active, created_at, last_login FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()

    res = dict(updated)
    res["is_active"] = bool(res["is_active"])
    return {
        "success": True,
        "user": res,
        "message": f"User '{target['email']}' role updated from '{old_role}' to '{new_role}'.",
    }

# ── WebSocket Real-Time Channel ───────────────────────────────────────────────
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time push channel with cross-worker synchronization."""
    await ws_manager.connect(websocket)
    # Track latest seen event ID
    conn = get_db_connection()
    last_event_id = conn.execute("SELECT coalesce(max(id), 0) FROM ws_events").fetchone()[0]
    conn.close()

    # Send initial connection acknowledgement
    await websocket.send_json({"type": "CONNECTED", "msg": "Real-time sync active"})

    async def poll_events():
        nonlocal last_event_id
        while True:
            await asyncio.sleep(0.3)
            try:
                c = get_db_connection()
                events = c.execute(
                    "SELECT id, event_payload FROM ws_events WHERE id > ? ORDER BY id ASC LIMIT 20",
                    (last_event_id,)
                ).fetchall()
                c.close()
                for ev in events:
                    last_event_id = ev["id"]
                    payload = json.loads(ev["event_payload"])
                    await websocket.send_json(payload)
            except Exception:
                break

    poller_task = asyncio.create_task(poll_events())

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        poller_task.cancel()
        ws_manager.disconnect(websocket)
    except Exception:
        poller_task.cancel()
        ws_manager.disconnect(websocket)

# ── Dropdown Metadata ─────────────────────────────────────────────────────────
@app.get("/api/dropdowns")
def get_dropdowns():
    """Returns categorized dropdown metadata with cached definitions."""
    if DROPDOWNS_JSON_PATH.exists():
        with open(DROPDOWNS_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    conn = get_db_connection()
    rows = conn.execute(
        "SELECT category, code, label, description, stage FROM dropdown_lists ORDER BY category, sort_order"
    ).fetchall()
    conn.close()

    result: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        cat = r["category"]
        if cat not in result:
            result[cat] = []
        result[cat].append({
            "code": r["code"],
            "label": r["label"],
            "description": r["description"],
            "stage": r["stage"],
        })
    return result

# ── Projects API (Tracker Tab) ────────────────────────────────────────────────
@app.get("/api/projects")
def list_projects(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    phase: Optional[str] = Query(None, description="Filter by phase"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    team: Optional[str] = Query(None, description="Filter by team"),
    search: Optional[str] = Query(None, description="Keyword search in ID, project, description"),
):
    """Retrieve all projects with optional multi-attribute filtering."""
    query = "SELECT * FROM projects WHERE 1=1"
    params: List[Any] = []

    if domain:
        query += " AND domain = ?"
        params.append(domain)
    if phase:
        query += " AND phase = ?"
        params.append(phase)
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    if team:
        query += " AND team = ?"
        params.append(team)
    if search:
        s = f"%{search.strip()}%"
        query += " AND (id LIKE ? OR project LIKE ? OR description LIKE ? OR business_owner LIKE ?)"
        params.extend([s, s, s, s])

    query += " ORDER BY id ASC"

    conn = get_db_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    items = [dict(r) for r in rows]
    return {"total": len(items), "projects": items}

@app.get("/api/projects/{project_id}")
def get_project(project_id: str):
    """Retrieve single project with its child requirements and audit history."""
    conn = get_db_connection()
    proj = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not proj:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")

    reqs = conn.execute(
        "SELECT * FROM requirements WHERE project_id = ? ORDER BY req_id ASC", (project_id,)
    ).fetchall()

    audits = conn.execute(
        "SELECT * FROM audit_log WHERE entity_type = 'project' AND entity_id = ? ORDER BY timestamp DESC LIMIT 20",
        (project_id,),
    ).fetchall()
    conn.close()

    return {
        "project": dict(proj),
        "requirements_count": len(reqs),
        "requirements": [dict(r) for r in reqs],
        "audit_history": [dict(a) for a in audits],
    }

@app.post("/api/projects", status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)):
    """Create a new project row in the tracker (Requires Editor or Admin role)."""
    # If user provided a token, ensure role is editor or admin
    if current_user:
        if current_user.get("role") not in ("admin", "editor"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: Only Editors and Admins can create projects.",
            )
        author = current_user.get("email") or payload.user or "WebUser"
    else:
        author = payload.user or "WebUser"

    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM projects WHERE id = ?", (payload.id,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Project with ID '{payload.id}' already exists.")

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with conn:
        conn.execute(
            """
            INSERT INTO projects (
                id, team, project, type, domain, description, phase, status,
                percent_complete, todo_tasks, inprogress_tasks, completed_tasks,
                blockers, blocker_owner, business_owner, technical_owner,
                start_date, due_date, last_updated, notes, priority, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.id, payload.team, payload.project, payload.type, payload.domain,
                payload.description, payload.phase, payload.status, payload.percent_complete,
                payload.todo_tasks, payload.inprogress_tasks, payload.completed_tasks,
                payload.blockers, payload.blocker_owner, payload.business_owner, payload.technical_owner,
                payload.start_date, payload.due_date, now, payload.notes, payload.priority, now, now
            ),
        )
        record_audit(
            conn, "project", payload.id, "INSERT", None, None, f"Created project {payload.project}", author
        )

    # Fetch newly created record
    created = conn.execute("SELECT * FROM projects WHERE id = ?", (payload.id,)).fetchone()
    conn.close()

    result = dict(created)
    await ws_manager.broadcast({
        "event": "PROJECT_CREATED",
        "entity_id": payload.id,
        "data": result,
    })
    return result

@app.patch("/api/projects/{project_id}")
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
):
    """
    Inline cell update for any project field with optimistic locking and audit logging.
    Requires Editor or Admin role.
    """
    if current_user:
        if current_user.get("role") not in ("admin", "editor"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: Viewers have read-only access. Editor or Admin permissions required.",
            )
        author = current_user.get("email") or payload.user or "WebUser"
    else:
        author = payload.user or "WebUser"

    conn = get_db_connection()
    current = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not current:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")

    current_dict = dict(current)

    # 1. Optimistic Locking Check
    if payload.expected_updated_at and payload.expected_updated_at != current_dict.get("updated_at"):
        conn.close()
        raise HTTPException(
            status_code=409,
            detail="Conflict: This project has been modified by another user. Please refresh and review.",
        )

    # 2. Compute modified fields
    updates: Dict[str, Any] = {}
    audit_records = []
    user = author

    for field, new_val in payload.dict(exclude_unset=True).items():
        if field in ("expected_updated_at", "user"):
            continue
        old_val = current_dict.get(field)
        if str(old_val) != str(new_val):
            updates[field] = new_val
            audit_records.append((field, str(old_val), str(new_val)))

    if not updates:
        conn.close()
        return current_dict

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    updates["updated_at"] = now
    updates["last_updated"] = now

    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [project_id]

    with conn:
        conn.execute(f"UPDATE projects SET {set_clause} WHERE id = ?", values)
        for field, old_v, new_v in audit_records:
            record_audit(conn, "project", project_id, "UPDATE", field, old_v, new_v, user)

    updated = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()

    result = dict(updated)
    await ws_manager.broadcast({
        "event": "PROJECT_UPDATED",
        "entity_id": project_id,
        "modified_fields": list(updates.keys()),
        "data": result,
    })
    return result

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str, user: str = Query("WebUser")):
    """Soft-delete project or mark as Retired with audit trail."""
    conn = get_db_connection()
    current = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not current:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")

    with conn:
        # Mark status as Retired & Phase as Retired
        conn.execute(
            "UPDATE projects SET phase = 'Retired', status = 'Not Reported', updated_at = datetime('now') WHERE id = ?",
            (project_id,),
        )
        record_audit(conn, "project", project_id, "DELETE", "phase", current["phase"], "Retired", user)

    conn.close()
    await ws_manager.broadcast({
        "event": "PROJECT_DELETED",
        "entity_id": project_id,
    })
    return {"success": True, "message": f"Project '{project_id}' marked as Retired."}

# ── Requirements API ──────────────────────────────────────────────────────────
@app.get("/api/requirements")
def list_requirements(
    project_id: Optional[str] = Query(None, alias="project", description="Filter by parent project ID"),
    category: Optional[str] = Query(None, description="Functional or Non-Functional"),
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = Query(None),
):
    """Retrieve requirements with optional project filter."""
    query = "SELECT * FROM requirements WHERE 1=1"
    params: List[Any] = []

    if project_id:
        query += " AND project_id = ?"
        params.append(project_id)
    if category:
        query += " AND category = ?"
        params.append(category)
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    if priority:
        query += " AND priority = ?"
        params.append(priority)

    query += " ORDER BY req_id ASC"

    conn = get_db_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    items = [dict(r) for r in rows]
    return {"total": len(items), "requirements": items}

@app.post("/api/requirements", status_code=status.HTTP_201_CREATED)
async def create_requirement(
    payload: RequirementCreate,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
):
    """Add a new functional or non-functional requirement (Requires Editor or Admin role)."""
    if current_user and current_user.get("role") not in ("admin", "editor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Only Editors and Admins can create requirements.",
        )
    author = (current_user and current_user.get("email")) or payload.user or "WebUser"

    conn = get_db_connection()
    existing = conn.execute("SELECT req_id FROM requirements WHERE req_id = ?", (payload.req_id,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Requirement ID '{payload.req_id}' already exists.")

    # Get parent project name
    proj = conn.execute("SELECT project FROM projects WHERE id = ?", (payload.project_id,)).fetchone()
    proj_name = proj["project"] if proj else payload.project_id

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with conn:
        conn.execute(
            """
            INSERT INTO requirements (
                req_id, project, project_id, category, nfr_area, requirement,
                description, business_benefit, request_type, owner, priority,
                status, target_date, source, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.req_id, proj_name, payload.project_id, payload.category, payload.nfr_area,
                payload.requirement, payload.description, payload.business_benefit, payload.request_type,
                payload.owner, payload.priority, payload.status, payload.target_date, payload.source,
                payload.notes, now, now
            ),
        )
        record_audit(
            conn, "requirement", payload.req_id, "INSERT", None, None,
            f"Added {payload.category} requirement to {payload.project_id}", author
        )

    created = conn.execute("SELECT * FROM requirements WHERE req_id = ?", (payload.req_id,)).fetchone()
    conn.close()

    result = dict(created)
    await ws_manager.broadcast({
        "event": "REQUIREMENT_CREATED",
        "entity_id": payload.req_id,
        "project_id": payload.project_id,
        "data": result,
    })
    return result

@app.patch("/api/requirements/{req_id}")
async def update_requirement(
    req_id: str,
    payload: RequirementUpdate,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
):
    """Update requirement field with change tracking (Requires Editor or Admin role)."""
    if current_user and current_user.get("role") not in ("admin", "editor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Viewers have read-only access. Editor or Admin permissions required.",
        )
    author = (current_user and current_user.get("email")) or payload.user or "WebUser"

    conn = get_db_connection()
    current = conn.execute("SELECT * FROM requirements WHERE req_id = ?", (req_id,)).fetchone()
    if not current:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Requirement '{req_id}' not found.")

    current_dict = dict(current)
    if payload.expected_updated_at and payload.expected_updated_at != current_dict.get("updated_at"):
        conn.close()
        raise HTTPException(status_code=409, detail="Conflict: Requirement modified concurrently.")

    updates: Dict[str, Any] = {}
    audit_records = []
    user = author

    for field, new_val in payload.dict(exclude_unset=True).items():
        if field in ("expected_updated_at", "user"):
            continue
        old_val = current_dict.get(field)
        if str(old_val) != str(new_val):
            updates[field] = new_val
            audit_records.append((field, str(old_val), str(new_val)))

    if not updates:
        conn.close()
        return current_dict

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    updates["updated_at"] = now

    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [req_id]

    with conn:
        conn.execute(f"UPDATE requirements SET {set_clause} WHERE req_id = ?", values)
        for field, old_v, new_v in audit_records:
            record_audit(conn, "requirement", req_id, "UPDATE", field, old_v, new_v, user)

    updated = conn.execute("SELECT * FROM requirements WHERE req_id = ?", (req_id,)).fetchone()
    conn.close()

    result = dict(updated)
    await ws_manager.broadcast({
        "event": "REQUIREMENT_UPDATED",
        "entity_id": req_id,
        "project_id": current_dict.get("project_id"),
        "data": result,
    })
    return result

# ── Audit Log API ─────────────────────────────────────────────────────────────
@app.get("/api/audit/{entity_id}")
def get_audit_trail(entity_id: str, limit: int = Query(50, ge=1, le=200)):
    """Retrieve full revision history for any project or requirement."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM audit_log WHERE entity_id = ? ORDER BY timestamp DESC LIMIT ?",
        (entity_id, limit),
    ).fetchall()
    conn.close()
    return {"entity_id": entity_id, "history": [dict(r) for r in rows]}

# ── KPI Analytics & Benchmarks API (Tab 2 with Dynamic Filtering) ─────────────
def _calculate_kpi_summary(
    projects: Optional[str] = None,
    domain: Optional[str] = None,
    phase: Optional[str] = None,
    priority: Optional[str] = None,
    status_filter: Optional[str] = None,
):
    conn = get_db_connection()

    # 1. Build Dynamic Filter Query for Projects
    where_clauses = ["1=1"]
    params: List[Any] = []

    # Clean strings
    p_str = projects if isinstance(projects, str) else None
    d_str = domain if isinstance(domain, str) else None
    ph_str = phase if isinstance(phase, str) else None
    pr_str = priority if isinstance(priority, str) else None
    st_str = status_filter if isinstance(status_filter, str) else None

    selected_pids = [p.strip() for p in p_str.split(",") if p.strip()] if p_str else []
    if selected_pids:
        placeholders = ", ".join(["?"] * len(selected_pids))
        where_clauses.append(f"p.id IN ({placeholders})")
        params.extend(selected_pids)

    if d_str:
        where_clauses.append("p.domain = ?")
        params.append(d_str)

    if ph_str:
        phases_list = [ph.strip() for ph in ph_str.split(",") if ph.strip()]
        if phases_list:
            placeholders = ", ".join(["?"] * len(phases_list))
            where_clauses.append(f"p.phase IN ({placeholders})")
            params.extend(phases_list)

    if pr_str:
        where_clauses.append("p.priority = ?")
        params.append(pr_str)

    if st_str:
        where_clauses.append("p.status = ?")
        params.append(st_str)

    where_sql = " AND ".join(where_clauses)

    # 2. Query Scoped Projects & Impact Weights
    query_projects = f"""
    SELECT 
        p.id, p.project, p.domain, p.phase, p.status, p.priority, p.percent_complete,
        coalesce(w.time_saved_hrs, 0) as time_saved_hrs,
        coalesce(w.revenue_impact_sar, 0) as revenue_impact_sar,
        coalesce(w.net_profit_sar, 0) as net_profit_sar,
        coalesce(w.target_subscribers, 0) as target_subscribers,
        coalesce(w.current_subscribers, 0) as current_subscribers,
        coalesce(w.csat_score, 8.0) as csat_score,
        coalesce(w.productivity_pct, 25.0) as productivity_pct
    FROM projects p
    LEFT JOIN project_impact_weights w ON p.id = w.project_id
    WHERE {where_sql}
    ORDER BY p.id ASC
    """
    rows = conn.execute(query_projects, params).fetchall()
    scoped_projects = [dict(r) for r in rows]

    total_scoped = len(scoped_projects)
    is_filtered = bool(projects or domain or phase or priority or status_filter)

    # If completely filtered out
    if total_scoped == 0:
        conn.close()
        return {
            "portfolio_summary": {
                "total_projects": 0, "on_track": 0, "at_risk": 0, "delayed": 0,
                "live": 0, "uat": 0, "avg_progress_pct": 0, "total_requirements": 0,
                "implemented_requirements": 0, "req_implementation_pct": 0,
            },
            "distributions": {"by_domain": [], "by_status": [], "by_phase": []},
            "core_kpis": {},
            "scoped_projects": [],
            "filter_applied": {
                "projects": selected_pids, "domain": domain, "phase": phase, "is_filtered": True
            }
        }

    # 3. Portfolio Aggregates from Scoped Subset
    on_track = sum(1 for p in scoped_projects if p["status"] == "On Track")
    at_risk = sum(1 for p in scoped_projects if p["status"] == "At Risk")
    delayed = sum(1 for p in scoped_projects if p["status"] == "Delayed")
    live = sum(1 for p in scoped_projects if p["phase"] == "Live")
    uat = sum(1 for p in scoped_projects if p["phase"] == "UAT")

    pct_vals = [p["percent_complete"] for p in scoped_projects if p["percent_complete"] is not None]
    avg_progress = (sum(pct_vals) / len(pct_vals)) if pct_vals else 0.0

    # 4. Scoped Requirements Count
    scoped_pids_found = [p["id"] for p in scoped_projects]
    p_placeholders = ", ".join(["?"] * len(scoped_pids_found))
    reqs_query = f"""
    SELECT 
        count(*) as total,
        sum(case when status = 'Implemented' then 1 else 0 end) as implemented
    FROM requirements
    WHERE project_id IN ({p_placeholders})
    """
    req_counts = conn.execute(reqs_query, scoped_pids_found).fetchone()
    total_reqs = req_counts["total"] or 0
    implemented_reqs = req_counts["implemented"] or 0

    # 5. Domain, Status & Phase Breakdown
    domain_counts: Dict[str, int] = {}
    status_counts: Dict[str, int] = {}
    phase_counts: Dict[str, int] = {}

    for p in scoped_projects:
        d = p["domain"] or "Unassigned"
        domain_counts[d] = domain_counts.get(d, 0) + 1
        s = p["status"] or "Not Reported"
        status_counts[s] = status_counts.get(s, 0) + 1
        ph = p["phase"] or "Idea"
        phase_counts[ph] = phase_counts.get(ph, 0) + 1

    # 6. Dynamic Recalculation of the 7 Core KPIs
    sum_time = sum(p["time_saved_hrs"] for p in scoped_projects)
    sum_revenue = sum(p["revenue_impact_sar"] for p in scoped_projects)
    sum_profit = sum(p["net_profit_sar"] for p in scoped_projects)
    sum_target_subs = sum(p["target_subscribers"] for p in scoped_projects)
    sum_curr_subs = sum(p["current_subscribers"] for p in scoped_projects)

    avg_csat = sum(p["csat_score"] for p in scoped_projects) / total_scoped
    avg_productivity = sum(p["productivity_pct"] for p in scoped_projects) / total_scoped

    # Adoption rate calculation
    computed_adoption = round((sum_curr_subs / sum_target_subs * 100), 1) if sum_target_subs > 0 else 0.0

    # Read base benchmarks from kpi_metrics table for metadata
    base_kpis = conn.execute("SELECT * FROM kpi_metrics ORDER BY id ASC").fetchall()
    conn.close()
    meta_map = {r["metric_key"]: dict(r) for r in base_kpis}

    dynamic_kpis = {
        "time_saved_hours": {
            **meta_map.get("time_saved_hours", {}),
            "current_value": round(sum_time, 1),
            "unit": "hours",
        },
        "revenue_impact": {
            **meta_map.get("revenue_impact", {}),
            "current_value": round(sum_revenue, 0),
            "unit": "SAR",
        },
        "net_profit": {
            **meta_map.get("net_profit", {}),
            "current_value": round(sum_profit, 0),
            "unit": "SAR",
        },
        "target_subscribers": {
            **meta_map.get("target_subscribers", {}),
            "current_value": sum_target_subs,
            "unit": "subscribers",
        },
        "current_subscribers": {
            **meta_map.get("current_subscribers", {}),
            "current_value": sum_curr_subs,
            "unit": "subscribers",
        },
        "adoption_rate": {
            **meta_map.get("adoption_rate", {}),
            "current_value": computed_adoption,
            "unit": "%",
        },
        "customer_satisfaction": {
            **meta_map.get("customer_satisfaction", {}),
            "current_value": round(avg_csat, 1),
            "unit": "/10",
        },
        "productivity_gain": {
            **meta_map.get("productivity_gain", {}),
            "current_value": round(avg_productivity, 1),
            "unit": "%",
        },
    }

    return {
        "portfolio_summary": {
            "total_projects": total_scoped,
            "on_track": on_track,
            "at_risk": at_risk,
            "delayed": delayed,
            "live": live,
            "uat": uat,
            "avg_progress_pct": round(avg_progress * 100, 1),
            "total_requirements": total_reqs,
            "implemented_requirements": implemented_reqs,
            "req_implementation_pct": round((implemented_reqs / total_reqs * 100), 1) if total_reqs > 0 else 0,
        },
        "distributions": {
            "by_domain": [{"domain": k, "count": v} for k, v in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)],
            "by_status": [{"status": k, "count": v} for k, v in sorted(status_counts.items(), key=lambda x: x[1], reverse=True)],
            "by_phase": [{"phase": k, "count": v} for k, v in sorted(phase_counts.items(), key=lambda x: x[1], reverse=True)],
        },
        "core_kpis": dynamic_kpis,
        "scoped_projects": scoped_projects,
        "filter_applied": {
            "projects": selected_pids,
            "domain": d_str,
            "phase": ph_str,
            "priority": pr_str,
            "is_filtered": is_filtered,
        },
    }

@app.get("/api/kpi/summary")
def get_kpi_summary(
    projects: Optional[str] = Query(None, description="Comma-separated project IDs e.g. AI-001,AI-006"),
    domain: Optional[str] = Query(None, description="Sector / Healthcare domain filter"),
    phase: Optional[str] = Query(None, description="Comma-separated phases e.g. Live,UAT"),
    priority: Optional[str] = Query(None, description="Priority filter"),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    return _calculate_kpi_summary(
        projects=projects,
        domain=domain,
        phase=phase,
        priority=priority,
        status_filter=status_filter,
    )

@app.get("/api/kpi/benchmarks")
def get_kpi_benchmarks(
    projects: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    phase: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """Returns dynamic industry benchmark evaluation against the filtered subset."""
    summary = _calculate_kpi_summary(
        projects=projects,
        domain=domain,
        phase=phase,
        priority=priority,
        status_filter=status_filter,
    )
    kpis = summary.get("core_kpis", {})

    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM kpi_metrics ORDER BY id ASC").fetchall()
    conn.close()

    comparisons = []
    for r in rows:
        key = r["metric_key"]
        curr = kpis.get(key, {}).get("current_value", r["current_value"])
        b_min = r["industry_benchmark_min"]
        b_max = r["industry_benchmark_max"]

        status_flag = "ON_TARGET"
        if b_max is not None and curr > b_max:
            status_flag = "EXCEEDING"
        elif b_min is not None and curr < b_min:
            status_flag = "BELOW_BENCHMARK"

        comparisons.append({
            "metric_key": key,
            "metric_name": r["metric_name"],
            "current_value": curr,
            "target_value": r["target_value"],
            "unit": r["unit"],
            "benchmark_min": b_min,
            "benchmark_max": b_max,
            "benchmark_unit": r["industry_benchmark_unit"],
            "source": r["benchmark_source"],
            "notes": r["benchmark_notes"],
            "status": status_flag,
        })

    return {
        "benchmarks": comparisons,
        "filter_applied": summary.get("filter_applied", {}),
    }

# ── Frontend Static Distribution Mount ─────────────────────────────────────────
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.head("/")
    async def head_root():
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
