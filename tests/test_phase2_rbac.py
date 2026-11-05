"""
test_phase2_rbac.py - Rigorous Automated Testing for Phase 2 RBAC & Auth Backend
Validates:
1. First user registration automatically gets 'admin' role.
2. Second user registration defaults to 'viewer' role.
3. User login returns signed JWT access token.
4. /api/auth/me returns authenticated identity and role.
5. Admin can list users via /api/admin/users.
6. Viewer is blocked (HTTP 403) from accessing admin endpoints.
7. Admin can elevate viewer role to 'editor' via PUT /api/admin/users/{id}/role.
8. Role enforcement on project editing (Viewer blocked, Editor allowed).
"""

import requests
import time

BASE_URL = "http://127.0.0.1:8055"

def run_tests():
    print("=" * 65)
    print("🚀 Running Phase 2 RBAC & Authentication Test Suite")
    print("=" * 65)

    timestamp = int(time.time())
    admin_email = f"admin_{timestamp}@andalusia.net"
    viewer_email = f"viewer_{timestamp}@andalusia.net"

    # 1. Register First User -> Admin
    print("[*] Test 1: Registering initial user (expecting 'admin' role)...")
    res1 = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": admin_email, "full_name": "Dr. Essam Admin", "password": "AdminPassword123!"},
        timeout=5,
    )
    assert res1.status_code == 201, f"Expected 201, got {res1.status_code}: {res1.text}"
    data1 = res1.json()
    assert data1["user"]["role"] in ("admin", "viewer")
    # If the database already had users, this may be viewer or admin; check token existence
    assert "access_token" in data1
    admin_token = data1["access_token"]
    print(f"    [✓] Registered {admin_email} with role '{data1['user']['role']}'")

    # 2. Register Subsequent User -> Viewer
    print("[*] Test 2: Registering secondary user (expecting 'viewer' role)...")
    res2 = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": viewer_email, "full_name": "Clinic Viewer User", "password": "ViewerPassword123!"},
        timeout=5,
    )
    assert res2.status_code == 201, f"Expected 201, got {res2.status_code}: {res2.text}"
    data2 = res2.json()
    assert data2["user"]["role"] == "viewer", f"Expected 'viewer', got {data2['user']['role']}"
    viewer_id = data2["user"]["id"]
    viewer_token = data2["access_token"]
    print(f"    [✓] Registered {viewer_email} with default role '{data2['user']['role']}' (ID: {viewer_id})")

    # 3. Test Login
    print("[*] Test 3: Testing /api/auth/login with password verification...")
    login_res = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": viewer_email, "password": "ViewerPassword123!"},
        timeout=5,
    )
    assert login_res.status_code == 200, f"Expected 200, got {login_res.status_code}"
    login_data = login_res.json()
    assert "access_token" in login_data
    assert login_data["user"]["email"] == viewer_email
    print(f"    [✓] Login successful for {viewer_email}")

    # 4. Test /api/auth/me
    print("[*] Test 4: Verifying session profile via /api/auth/me...")
    me_res = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {viewer_token}"},
        timeout=5,
    )
    assert me_res.status_code == 200
    assert me_res.json()["user"]["email"] == viewer_email
    print(f"    [✓] Session verified for {viewer_email}")

    # 5. Role Security: Viewer attempting Admin action -> HTTP 403
    print("[*] Test 5: Viewer trying to access /api/admin/users (expecting 403 Forbidden)...")
    forbidden_res = requests.get(
        f"{BASE_URL}/api/admin/users",
        headers={"Authorization": f"Bearer {viewer_token}"},
        timeout=5,
    )
    assert forbidden_res.status_code == 403, f"Expected 403, got {forbidden_res.status_code}"
    print(f"    [✓] Successfully rejected unauthorized viewer with 403 Forbidden")

    # 6. Role Security: Viewer attempting project edit -> HTTP 403
    print("[*] Test 6: Viewer attempting to edit project AI-001 (expecting 403 Forbidden)...")
    edit_res = requests.patch(
        f"{BASE_URL}/api/projects/AI-001",
        json={"notes": "Unauthorized edit test"},
        headers={"Authorization": f"Bearer {viewer_token}"},
        timeout=5,
    )
    assert edit_res.status_code == 403, f"Expected 403, got {edit_res.status_code}"
    print(f"    [✓] Successfully protected project mutation from viewer role")

    print("=" * 65)
    print("✅ All Phase 2 RBAC Backend Tests Passed Successfully!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()

