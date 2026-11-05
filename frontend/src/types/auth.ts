// ─────────────────────────────────────────────────────────────────────────────
// Auth Types — Andalusia Healthcare AI Portfolio Dashboard
// ─────────────────────────────────────────────────────────────────────────────

export type UserRole = "viewer" | "editor" | "admin";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at?: string;
  last_login?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

export interface LoginPayload {
  username_or_email?: string;
  email?: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  full_name: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RoleUpdatePayload {
  role: UserRole;
}

// Role hierarchy: viewer(1) < editor(2) < admin(3)
export const ROLE_HIERARCHY: Record<UserRole, number> = {
  viewer: 1,
  editor: 2,
  admin: 3,
};

export const ROLE_LABELS: Record<UserRole, string> = {
  viewer: "Viewer",
  editor: "Editor",
  admin: "Admin",
};

export const ROLE_COLORS: Record<UserRole, { bg: string; text: string; border: string }> = {
  viewer: { bg: "bg-stone-100", text: "text-stone-700", border: "border-stone-300" },
  editor: { bg: "bg-blue-100", text: "text-blue-700", border: "border-blue-300" },
  admin: { bg: "bg-amber-100", text: "text-amber-800", border: "border-amber-400" },
};

