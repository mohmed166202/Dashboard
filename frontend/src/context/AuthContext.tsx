// ─────────────────────────────────────────────────────────────────────────────
// AuthContext — Andalusia Healthcare AI Portfolio Dashboard
// Provides global auth state: user, token, role, login/logout/register actions.
// On mount, hydrates from localStorage and validates token against /api/auth/me.
// ─────────────────────────────────────────────────────────────────────────────

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useReducer,
} from "react";
import type { FC, ReactNode } from "react";
import { authApi, authStorage } from "../services/authApiClient";
import type { User, UserRole, LoginPayload, RegisterPayload } from "../types/auth";
import { ROLE_HIERARCHY } from "../types/auth";

// ── State & Actions ──────────────────────────────────────────────────────────

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean; // true during initial hydration
  error: string | null;
}

type AuthAction =
  | { type: "HYDRATION_START" }
  | { type: "HYDRATION_DONE"; user: User; token: string }
  | { type: "HYDRATION_FAILED" }
  | { type: "AUTH_SUCCESS"; user: User; token: string }
  | { type: "AUTH_ERROR"; error: string }
  | { type: "LOGOUT" }
  | { type: "CLEAR_ERROR" }
  | { type: "USER_UPDATED"; user: User };

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case "HYDRATION_START":
      return { ...state, isLoading: true, error: null };
    case "HYDRATION_DONE":
      return {
        ...state,
        isLoading: false,
        isAuthenticated: true,
        user: action.user,
        token: action.token,
        error: null,
      };
    case "HYDRATION_FAILED":
      return { ...state, isLoading: false, isAuthenticated: false, user: null, token: null };
    case "AUTH_SUCCESS":
      return {
        ...state,
        isLoading: false,
        isAuthenticated: true,
        user: action.user,
        token: action.token,
        error: null,
      };
    case "AUTH_ERROR":
      return { ...state, isLoading: false, error: action.error };
    case "LOGOUT":
      return { user: null, token: null, isAuthenticated: false, isLoading: false, error: null };
    case "CLEAR_ERROR":
      return { ...state, error: null };
    case "USER_UPDATED":
      return { ...state, user: action.user };
    default:
      return state;
  }
}

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true, // start loading until hydration completes
  error: null,
};

// ── Context Shape ────────────────────────────────────────────────────────────

interface AuthContextValue extends AuthState {
  /** Login with email + password. Throws on failure. */
  login: (payload: LoginPayload) => Promise<void>;
  /** Register a new account. Auto-login on success. */
  register: (payload: RegisterPayload) => Promise<void>;
  /** Clear session and localStorage. */
  logout: () => void;
  /** Clear any pending auth error. */
  clearError: () => void;
  /** Update the in-memory user (after admin changes role, etc.). */
  updateUser: (user: User) => void;
  /** Convenience: check if current user has at least `role` permission. */
  hasRole: (role: UserRole) => boolean;
  /** True when user is an admin. */
  isAdmin: boolean;
  /** True when user is an editor or admin. */
  isEditor: boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// ── Provider ─────────────────────────────────────────────────────────────────

export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Hydrate from localStorage on mount
  useEffect(() => {
    const hydrate = async () => {
      dispatch({ type: "HYDRATION_START" });
      const token = authStorage.getToken();
      const cachedUser = authStorage.getUser();

      if (!token) {
        dispatch({ type: "HYDRATION_FAILED" });
        return;
      }

      // Optimistically show cached user immediately (fast paint)
      if (cachedUser) {
        dispatch({ type: "HYDRATION_DONE", user: cachedUser, token });
      }

      // Then validate token server-side in background
      try {
        const freshUser = await authApi.me(token);
        authStorage.set(token, freshUser); // refresh cached user
        dispatch({ type: "HYDRATION_DONE", user: freshUser, token });
      } catch {
        // Token is invalid/expired — clear everything
        authStorage.clear();
        dispatch({ type: "HYDRATION_FAILED" });
      }
    };

    hydrate();
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    try {
      const response = await authApi.login(payload);
      dispatch({ type: "AUTH_SUCCESS", user: response.user, token: response.access_token });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed";
      dispatch({ type: "AUTH_ERROR", error: message });
      throw err; // re-throw so the modal can handle it too
    }
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    try {
      const response = await authApi.register(payload);
      // Auto-login: store token from register response and persist
      authStorage.set(response.access_token, response.user);
      dispatch({ type: "AUTH_SUCCESS", user: response.user, token: response.access_token });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Registration failed";
      dispatch({ type: "AUTH_ERROR", error: message });
      throw err;
    }
  }, []);

  const logout = useCallback(() => {
    authApi.logout();
    dispatch({ type: "LOGOUT" });
  }, []);

  const clearError = useCallback(() => {
    dispatch({ type: "CLEAR_ERROR" });
  }, []);

  const updateUser = useCallback((user: User) => {
    authStorage.set(state.token ?? "", user);
    dispatch({ type: "USER_UPDATED", user });
  }, [state.token]);

  const hasRole = useCallback(
    (role: UserRole): boolean => {
      if (!state.user) return false;
      return ROLE_HIERARCHY[state.user.role] >= ROLE_HIERARCHY[role];
    },
    [state.user]
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      ...state,
      login,
      register,
      logout,
      clearError,
      updateUser,
      hasRole,
      isAdmin: state.user?.role === "admin",
      isEditor: state.user ? ROLE_HIERARCHY[state.user.role] >= ROLE_HIERARCHY["editor"] : false,
    }),
    [state, login, register, logout, clearError, updateUser, hasRole]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// ── Hook ─────────────────────────────────────────────────────────────────────

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within <AuthProvider>");
  }
  return ctx;
}

