"""
Phase 3 RBAC Frontend Auth Integration Tests
==============================================
API-level verification of:
 - Register, Login, Me flow
 - JWT token is returned and valid
 - Viewer is blocked from mutation endpoints
 - Editor can mutate
 - Admin can list/change users
 - Auth headers injected in PATCH/POST requests work

NOTE: These tests mirror what the frontend AuthContext, AuthModal, and
      AdminUsersModal do under the hood via authApiClient.ts.
"""

import pytest
import requests
import uuid
import time

BASE = "http://127.0.0.1:8055"

# Configured admin credentials from .env / secrets
ADMIN_USERNAME = "mohamed-galal"
ADMIN_EMAIL = "mohamed-galal@andalusia.net"
ADMIN_PASS = "Mm@01000713965$"


def unique_email(prefix="user") -> str:
    return f"{prefix}.{uuid.uuid4().hex[:8]}@example.com"


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def admin_token():
    """Login as configured admin using username and return token."""
    r = requests.post(f"{BASE}/api/auth/login", json={
        "username_or_email": ADMIN_USERNAME, "password": ADMIN_PASS
    })
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def admin_user(admin_token):
    """Return the admin user object."""
    r = requests.get(f"{BASE}/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    return r.json()


@pytest.fixture(scope="module")
def fresh_viewer(admin_token):
    """Register a brand-new viewer user and return credentials."""
    email = unique_email("viewer")
    password = "ViewerPass123!"
    r = requests.post(f"{BASE}/api/auth/register", json={
        "email": email, "full_name": "Phase3 Test Viewer", "password": password
    })
    # Backend returns 201 for successful registration
    assert r.status_code in [200, 201], f"Viewer register failed: {r.text}"
    data = r.json()
    return {
        "email": email,
        "password": password,
        "user": data["user"],
        "token": data["access_token"]
    }


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestAuthFlow:
    def test_register_new_user_returns_token(self, fresh_viewer):
        """Registration response includes access_token and user profile."""
        assert fresh_viewer["token"] != ""
        assert fresh_viewer["user"]["email"] == fresh_viewer["email"]
        assert fresh_viewer["user"]["role"] == "viewer"  # all new users start as viewer

    def test_login_returns_valid_token(self):
        """Login with correct credentials returns a JWT token."""
        r = requests.post(f"{BASE}/api/auth/login", json={
            "email": ADMIN_EMAIL, "password": ADMIN_PASS
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["user"]["email"] == ADMIN_EMAIL

    def test_me_validates_token(self, admin_token):
        """GET /api/auth/me returns current user when given a valid token."""
        r = requests.get(
            f"{BASE}/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert r.status_code == 200
        data = r.json()
        assert data["user"]["email"] == ADMIN_EMAIL

    def test_me_rejects_invalid_token(self):
        """GET /api/auth/me with garbage token returns 401."""
        r = requests.get(
            f"{BASE}/api/auth/me",
            headers={"Authorization": "Bearer totallyinvalidtoken"}
        )
        assert r.status_code == 401

    def test_login_wrong_password_rejected(self):
        """Login with wrong password returns 401."""
        r = requests.post(f"{BASE}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": "totallyWrongPassword!"
        })
        assert r.status_code == 401

    def test_duplicate_email_rejected(self, fresh_viewer):
        """Registering with an already-used email returns 400/409/422."""
        r = requests.post(f"{BASE}/api/auth/register", json={
            "email": fresh_viewer["email"],
            "full_name": "Duplicate User",
            "password": "AnotherPass123!"
        })
        assert r.status_code in [400, 409, 422], f"Expected conflict error, got {r.status_code}"


class TestRoleEnforcement:
    def test_viewer_blocked_from_admin_users_list(self, fresh_viewer):
        """Viewer cannot access GET /api/admin/users."""
        r = requests.get(
            f"{BASE}/api/admin/users",
            headers={"Authorization": f"Bearer {fresh_viewer['token']}"}
        )
        assert r.status_code == 403

    def test_admin_can_list_users(self, admin_token):
        """Admin can access GET /api/admin/users."""
        r = requests.get(
            f"{BASE}/api/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert r.status_code == 200
        res = r.json()
        users = res.get("users", [])
        assert isinstance(users, list)
        assert len(users) >= 1

    def test_viewer_blocked_from_patch_project(self, fresh_viewer):
        """Authenticated viewer cannot PATCH a project (mimics inline edit in table)."""
        r = requests.patch(
            f"{BASE}/api/projects/AI-001",
            json={"status": "On Track"},
            headers={
                "Authorization": f"Bearer {fresh_viewer['token']}",
                "Content-Type": "application/json"
            }
        )
        assert r.status_code == 403, f"Expected 403, got {r.status_code}: {r.text}"

    def test_admin_can_patch_project(self, admin_token):
        """Admin can PATCH a project (inline cell edit)."""
        r = requests.patch(
            f"{BASE}/api/projects/AI-001",
            json={"status": "On Track"},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
        )
        assert r.status_code == 200


class TestAdminRoleDelegation:
    def test_admin_promotes_viewer_to_editor(self, admin_token, fresh_viewer):
        """Admin can promote a viewer to editor via PUT /api/admin/users/{id}/role."""
        viewer_id = fresh_viewer["user"]["id"]
        r = requests.put(
            f"{BASE}/api/admin/users/{viewer_id}/role",
            json={"role": "editor"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert r.status_code == 200
        updated = r.json()
        assert updated["user"]["role"] == "editor"

    def test_promoted_editor_can_patch_project(self, fresh_viewer):
        """After promotion to editor, the user can PATCH projects."""
        # Login again to get a fresh token reflecting new role
        r = requests.post(f"{BASE}/api/auth/login", json={
            "email": fresh_viewer["email"],
            "password": fresh_viewer["password"]
        })
        assert r.status_code == 200
        new_token = r.json()["access_token"]
        new_role = r.json()["user"]["role"]
        assert new_role == "editor"

        r2 = requests.patch(
            f"{BASE}/api/projects/AI-001",
            json={"status": "In Progress"},
            headers={"Authorization": f"Bearer {new_token}"}
        )
        assert r2.status_code == 200

    def test_admin_demotes_editor_back_to_viewer(self, admin_token, fresh_viewer):
        """Admin can demote an editor back to viewer."""
        viewer_id = fresh_viewer["user"]["id"]
        r = requests.put(
            f"{BASE}/api/admin/users/{viewer_id}/role",
            json={"role": "viewer"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert r.status_code == 200
        assert r.json()["user"]["role"] == "viewer"


class TestNoAuthGuests:
    def test_guest_can_read_projects(self):
        """Unauthenticated GET /api/projects still works (read-only public)."""
        r = requests.get(f"{BASE}/api/projects")
        assert r.status_code == 200

    def test_guest_cannot_read_admin_users(self):
        """Unauthenticated access to /api/admin/users is blocked."""
        r = requests.get(f"{BASE}/api/admin/users")
        assert r.status_code in [401, 403]

    def test_latency_auth_me_under_50ms(self, admin_token):
        """GET /api/auth/me should respond in under 50ms."""
        t0 = time.perf_counter()
        r = requests.get(
            f"{BASE}/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert r.status_code == 200
        assert elapsed_ms < 50, f"Response too slow: {elapsed_ms:.1f}ms"
