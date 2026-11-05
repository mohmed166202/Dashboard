// ─────────────────────────────────────────────────────────────────────────────
// AdminUsersModal — User Management Panel (Admin Only)
// Lists all users, allows role promotion/demotion with 1-click.
// ─────────────────────────────────────────────────────────────────────────────

import React, { useState, useEffect, useCallback } from "react";
import {
  X,
  Users,
  RefreshCw,
  ShieldCheck,
  Shield,
  Eye,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Crown,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { authApi } from "../services/authApiClient";
import type { User, UserRole } from "../types/auth";
import { ROLE_COLORS } from "../types/auth";

interface AdminUsersModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ROLE_ICONS: Record<UserRole, React.ReactNode> = {
  admin: <Crown className="w-3 h-3" />,
  editor: <Shield className="w-3 h-3" />,
  viewer: <Eye className="w-3 h-3" />,
};

const ROLE_ORDER: UserRole[] = ["viewer", "editor", "admin"];

export const AdminUsersModal: React.FC<AdminUsersModalProps> = ({ isOpen, onClose }) => {
  const { token, user: currentUser, updateUser } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<number | null>(null);
  const [successId, setSuccessId] = useState<number | null>(null);

  const fetchUsers = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const data = await authApi.listUsers(token);
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load users");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (isOpen) fetchUsers();
  }, [isOpen, fetchUsers]);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    if (isOpen) window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleRoleChange = async (targetUser: User, newRole: UserRole) => {
    if (!token || newRole === targetUser.role) return;
    setUpdatingId(targetUser.id);
    setError(null);
    try {
      const updated = await authApi.updateUserRole(token, targetUser.id, newRole);
      setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
      // If the admin changed their own role, update context too
      if (currentUser && targetUser.id === currentUser.id) {
        updateUser(updated);
      }
      setSuccessId(targetUser.id);
      setTimeout(() => setSuccessId(null), 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update role");
    } finally {
      setUpdatingId(null);
    }
  };

  const formatDate = (d?: string) => {
    if (!d) return "—";
    try {
      return new Date(d).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
    } catch { return d; }
  };

  return (
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-stone-200 overflow-hidden">
        {/* Header */}
        <div className="bg-[#4A3426] px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center border border-white/20">
              <Users className="w-4 h-4 text-amber-300" />
            </div>
            <div>
              <h2 className="text-white text-sm font-bold leading-tight">Admin — User Management</h2>
              <p className="text-amber-200/70 text-[11px]">{users.length} registered user{users.length !== 1 ? "s" : ""}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchUsers}
              disabled={loading}
              className="text-white/60 hover:text-white hover:bg-white/10 p-1.5 rounded-lg transition-all"
              title="Refresh user list"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
            <button
              onClick={onClose}
              className="text-white/60 hover:text-white hover:bg-white/10 p-1.5 rounded-lg transition-all"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="p-4 max-h-[70vh] overflow-y-auto">
          {/* Error */}
          {error && (
            <div className="mb-3 flex items-start gap-2 p-3 rounded-lg bg-red-50 border border-red-200 text-xs text-red-700">
              <AlertCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Loading Skeleton */}
          {loading && users.length === 0 && (
            <div className="space-y-2 py-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-14 bg-stone-100 rounded-xl animate-pulse" />
              ))}
            </div>
          )}

          {/* User List */}
          {!loading || users.length > 0 ? (
            <div className="space-y-2">
              {users.map((u) => {
                const colors = ROLE_COLORS[u.role];
                const isUpdating = updatingId === u.id;
                const isSuccess = successId === u.id;
                const isSelf = currentUser?.id === u.id;

                return (
                  <div
                    key={u.id}
                    className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${
                      isSelf
                        ? "border-amber-300 bg-amber-50/50"
                        : "border-stone-200 bg-stone-50 hover:bg-white hover:border-stone-300"
                    }`}
                  >
                    {/* Avatar */}
                    <div className="w-9 h-9 rounded-full bg-[#4A3426]/10 flex items-center justify-center shrink-0 border border-[#4A3426]/20">
                      <span className="text-sm font-bold text-[#4A3426]">
                        {u.full_name.charAt(0).toUpperCase()}
                      </span>
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-stone-800 truncate">
                          {u.full_name}
                        </span>
                        {isSelf && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-200 text-amber-800 font-bold">
                            You
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-stone-500 truncate">{u.email}</p>
                      <p className="text-[10px] text-stone-400">Joined {formatDate(u.created_at)}</p>
                    </div>

                    {/* Current Role Badge */}
                    <div className={`flex items-center gap-1 px-2 py-1 rounded-full border text-xs font-semibold ${colors.bg} ${colors.text} ${colors.border}`}>
                      {ROLE_ICONS[u.role]}
                      {u.role.charAt(0).toUpperCase() + u.role.slice(1)}
                    </div>

                    {/* Role Change Buttons */}
                    {!isSelf && (
                      <div className="flex items-center gap-1">
                        {isUpdating && <Loader2 className="w-4 h-4 animate-spin text-amber-600" />}
                        {isSuccess && <CheckCircle2 className="w-4 h-4 text-emerald-600" />}
                        {!isUpdating && !isSuccess && (
                          <div className="flex items-center gap-1">
                            {ROLE_ORDER.filter((r) => r !== u.role).map((role) => (
                              <button
                                key={role}
                                onClick={() => handleRoleChange(u, role)}
                                title={`Set to ${role}`}
                                className={`text-[10px] px-2 py-1 rounded-lg font-semibold border transition-all hover:shadow-sm ${
                                  role === "admin"
                                    ? "border-amber-300 text-amber-700 hover:bg-amber-50"
                                    : role === "editor"
                                    ? "border-blue-300 text-blue-700 hover:bg-blue-50"
                                    : "border-stone-300 text-stone-600 hover:bg-stone-100"
                                }`}
                              >
                                → {role.charAt(0).toUpperCase() + role.slice(1)}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}

              {users.length === 0 && !loading && (
                <div className="text-center py-8 text-stone-400">
                  <Users className="w-10 h-10 mx-auto mb-2 opacity-30" />
                  <p className="text-sm">No users registered yet.</p>
                </div>
              )}
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="border-t border-stone-200 px-6 py-3 bg-stone-50 flex items-center justify-between">
          <div className="flex items-center gap-3 text-[11px] text-stone-500">
            <span className="flex items-center gap-1"><Crown className="w-3 h-3 text-amber-600" /> Admin</span>
            <span className="flex items-center gap-1"><Shield className="w-3 h-3 text-blue-600" /> Editor</span>
            <span className="flex items-center gap-1"><Eye className="w-3 h-3 text-stone-500" /> Viewer</span>
          </div>
          <div className="flex items-center gap-1 text-[11px] text-emerald-700">
            <ShieldCheck className="w-3 h-3" />
            <span>Server-side enforced</span>
          </div>
        </div>
      </div>
    </div>
  );
};

