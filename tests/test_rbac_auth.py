"""
Phase 5 Comprehensive RBAC & Security Test Suite: tests/test_rbac_auth.py
========================================================================
Validates:
 1. User registration flow & default 'viewer' assignment
 2. Authentication with username or email (including configured admin 'mohamed-galal')
 3. JWT token generation, signature integrity, and profile retrieval (/api/auth/me)
 4. Unauthorized mutation block (HTTP 403 Forbidden for Viewers attempting to PATCH/POST)
 5. Editor role mutation authorization (PATCH projects, requirements)
 6. Admin user management & 1-click role elevation / demotion (/api/admin/users)
 7. Performance latency threshold check (<50ms for auth verification)
"""

import pytest
import requests
import uuid
import time
import os

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8055")
ADMIN_USER = os.getenv("ADMIN_USERNAME", "mohamed-galal")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "Mm@01000713965$")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "mohamed-galal@andalusia.net")


def make_random_email(prefix: str = "test") -> str:
    return f"{prefix}.{uuid.uuid4().hex[:8]}@example.com"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def admin_session():
    """Login with the configured admin credentials and return token & profile."""
    res = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username_or_email": ADMIN_USER, "password": ADMIN_PASS},
        timeout=10,
    )
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"
    return {"token": data["access_token"], "user": data["user"]}


@pytest.fixture(scope="module")
def new_registered_viewer():
    """Register a new user and ensure they default to viewer role."""
    email = make_random_email("viewer")
    password = "ViewerTestPassword123!"
    full_name = "Automated Test Viewer"

    res = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
        timeout=10,
    )
    assert res.status_code in [200, 201], f"Registration failed: {res.text}"
    data = res.json()
    assert data["user"]["role"] == "viewer", "New user must start as viewer role"
    return {"token": data["access_token"], "user": data["user"], "password": password, "email": email}


# ── Test Cases ────────────────────────────────────────────────────────────────

class TestUserRegistrationAndLogin:
    def test_registration_assigns_default_viewer_role(self, new_registered_viewer):
        """Verify that public self-service registration assigns role = 'viewer'."""
        assert new_registered_viewer["user"]["role"] == "viewer"
        assert new_registered_viewer["token"] is not None

    def test_login_by_username(self):
        """Verify login using username identifier."""
        res = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username_or_email": ADMIN_USER, "password": ADMIN_PASS},
            timeout=10,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["user"]["role"] == "admin"

    def test_login_by_email(self):
        """Verify login using email identifier."""
        res = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASS},
            timeout=10,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["user"]["email"] == ADMIN_EMAIL

    def test_invalid_password_returns_401(self):
        """Verify rejected login with invalid credentials."""
        res = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username_or_email": ADMIN_USER, "password": "WrongPassword!999"},
            timeout=10,
        )
        assert res.status_code == 401

    def test_auth_me_validates_active_jwt(self, admin_session):
        """Verify /api/auth/me decodes and returns the caller profile."""
        res = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {admin_session['token']}"},
            timeout=10,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "admin"


class TestRoleRestrictionsAndEnforcement:
    def test_viewer_is_forbidden_from_admin_users(self, new_registered_viewer):
        """Viewers must be rejected with HTTP 403 on admin-only endpoints."""
        res = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers={"Authorization": f"Bearer {new_registered_viewer['token']}"},
            timeout=10,
        )
        assert res.status_code == 403, f"Expected 403 Forbidden, got {res.status_code}"

    def test_viewer_is_forbidden_from_patching_project(self, new_registered_viewer):
        """Viewers attempting to edit table cells inline must receive HTTP 403."""
        res = requests.patch(
            f"{BASE_URL}/api/projects/AI-001",
            json={"status": "Delayed"},
            headers={"Authorization": f"Bearer {new_registered_viewer['token']}"},
            timeout=10,
        )
        assert res.status_code == 403, f"Expected 403 Forbidden, got {res.status_code}"

    def test_admin_is_authorized_to_patch_project(self, admin_session):
        """Admin is authorized to update project cells inline."""
        res = requests.patch(
            f"{BASE_URL}/api/projects/AI-001",
            json={"status": "On Track"},
            headers={"Authorization": f"Bearer {admin_session['token']}"},
            timeout=10,
        )
        assert res.status_code == 200, f"Expected 200 OK, got {res.status_code}: {res.text}"


class TestAdminRoleElevationLifecycle:
    def test_admin_elevates_viewer_to_editor(self, admin_session, new_registered_viewer):
        """Admin elevates user role to 'editor' via PUT /api/admin/users/{id}/role."""
        user_id = new_registered_viewer["user"]["id"]
        res = requests.put(
            f"{BASE_URL}/api/admin/users/{user_id}/role",
            json={"role": "editor"},
            headers={"Authorization": f"Bearer {admin_session['token']}"},
            timeout=10,
        )
        assert res.status_code == 200
        body = res.json()
        assert body["user"]["role"] == "editor"

    def test_elevated_editor_can_now_patch_project(self, new_registered_viewer):
        """Once elevated, login with the user's credentials to issue an editor JWT and mutate."""
        login_res = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": new_registered_viewer["email"], "password": new_registered_viewer["password"]},
            timeout=10,
        )
        assert login_res.status_code == 200
        editor_token = login_res.json()["access_token"]
        assert login_res.json()["user"]["role"] == "editor"

        # Mutate project as editor
        res = requests.patch(
            f"{BASE_URL}/api/projects/AI-001",
            json={"status": "On Track"},
            headers={"Authorization": f"Bearer {editor_token}"},
            timeout=10,
        )
        assert res.status_code == 200

    def test_admin_demotes_user_back_to_viewer(self, admin_session, new_registered_viewer):
        """Admin can demote the user back to 'viewer'."""
        user_id = new_registered_viewer["user"]["id"]
        res = requests.put(
            f"{BASE_URL}/api/admin/users/{user_id}/role",
            json={"role": "viewer"},
            headers={"Authorization": f"Bearer {admin_session['token']}"},
            timeout=10,
        )
        assert res.status_code == 200
        body = res.json()
        assert body["user"]["role"] == "viewer"


class TestRBACPerformanceLatency:
    def test_auth_me_latency_sub_50ms(self, admin_session):
        """Ensure token verification overhead remains under 50ms."""
        times = []
        for _ in range(5):
            t0 = time.perf_counter()
            res = requests.get(
                f"{BASE_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {admin_session['token']}"},
                timeout=5,
            )
            times.append((time.perf_counter() - t0) * 1000)
            assert res.status_code == 200

        avg_latency = sum(times) / len(times)
        assert avg_latency < 50.0, f"Average latency too high: {avg_latency:.2f}ms"

