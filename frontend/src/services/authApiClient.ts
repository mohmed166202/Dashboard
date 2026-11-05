// ─────────────────────────────────────────────────────────────────────────────
// Auth API Client — Andalusia Healthcare AI Portfolio Dashboard
// All auth requests target the FastAPI backend auth endpoints.
// ─────────────────────────────────────────────────────────────────────────────

import type { User, AuthResponse, RegisterPayload, LoginPayload, UserRole } from "../types/auth";

const BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "";

function getBaseUrl(): string {
  return BASE_URL || (typeof window !== "undefined" ? window.location.origin : "http://localhost:8055");
}

async function authFetch<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const url = `${getBaseUrl()}${path}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
    ...(options.headers as Record<string, string> ?? {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(url, { ...options, headers });

  if (!res.ok) {
    let errorMsg: string;
    try {
      const body = await res.json();
      errorMsg = body?.detail ?? body?.message ?? JSON.stringify(body);
    } catch {
      errorMsg = await res.text().catch(() => `HTTP ${res.status}`);
    }
    throw new Error(errorMsg);
  }

  return res.json() as Promise<T>;
}

// ── Storage helpers ──────────────────────────────────────────────────────────
const TOKEN_KEY = "auth_token";
const USER_KEY = "auth_user";

export const authStorage = {
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },
  getUser(): User | null {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as User;
    } catch {
      return null;
    }
  },
  set(token: string, user: User): void {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clear(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
};

// ── API Methods ──────────────────────────────────────────────────────────────
export const authApi = {
  /**
   * Register a new user. First user becomes admin, subsequent users become viewer.
   */
  async register(payload: RegisterPayload): Promise<AuthResponse> {
    return authFetch<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Login with email + password, returns JWT + user profile.
   * Automatically persists token and user to localStorage.
   */
  async login(payload: LoginPayload): Promise<AuthResponse> {
    const response = await authFetch<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    authStorage.set(response.access_token, response.user);
    return response;
  },

  /**
   * Validate the current token against /api/auth/me.
   * Returns the current user or throws if the token is invalid/expired.
   */
  async me(token: string): Promise<User> {
    const res = await authFetch<{ user: User }>("/api/auth/me", { method: "GET" }, token);
    return res.user;
  },

  /**
   * Clear local auth state (logout is client-side only — no token blacklist).
   */
  logout(): void {
    authStorage.clear();
  },

  // ── Admin endpoints ────────────────────────────────────────────────────────

  /**
   * List all registered users. Requires admin role.
   */
  async listUsers(token: string): Promise<User[]> {
    const res = await authFetch<{ total: number; users: User[] }>("/api/admin/users", { method: "GET" }, token);
    return res.users || [];
  },

  /**
   * Update a user's role. Requires admin role.
   */
  async updateUserRole(token: string, userId: number, role: UserRole): Promise<User> {
    const res = await authFetch<{ success: boolean; user: User }>(
      `/api/admin/users/${userId}/role`,
      { method: "PUT", body: JSON.stringify({ role }) },
      token
    );
    return res.user;
  },
};

// ── Token injection helper for trackerApiClient ──────────────────────────────
/**
 * Returns auth headers to inject into mutating tracker API requests.
 * Reads from localStorage so it works outside React context.
 */
export function getAuthHeaders(): Record<string, string> {
  const token = authStorage.getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

