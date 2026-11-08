// ─────────────────────────────────────────────────────────────────────────────
// Navbar — Andalusia Healthcare AI Portfolio Dashboard
// Full-width layout | Auth-aware | Role badge | Admin Panel access
// ─────────────────────────────────────────────────────────────────────────────

import { useState } from "react";
import type { FC, ReactNode } from "react";
import {
  Activity,
  RefreshCw,
  LayoutGrid,
  BarChart2,
  Briefcase,
  LogIn,
  LogOut,
  Crown,
  Shield,
  Eye,
  Users,
  ChevronDown,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { AuthModal } from "./AuthModal";
import { AdminUsersModal } from "./AdminUsersModal";
import type { UserRole } from "../types/auth";

export type DashboardTab = "SUMMARY" | "TRACKER" | "ANALYTICS";

interface NavbarProps {
  onRefresh?: () => void;
  isRefreshing?: boolean;
  statusBadge?: ReactNode;
  activeTab?: DashboardTab;
  onTabChange?: (tab: DashboardTab) => void;
}

// Role visual config
const ROLE_CONFIG: Record<UserRole, { label: string; icon: ReactNode; classes: string }> = {
  admin: {
    label: "Admin",
    icon: <Crown className="w-3 h-3" />,
    classes: "bg-amber-400/20 text-amber-200 border-amber-400/40",
  },
  editor: {
    label: "Editor",
    icon: <Shield className="w-3 h-3" />,
    classes: "bg-blue-400/20 text-blue-200 border-blue-400/40",
  },
  viewer: {
    label: "Viewer",
    icon: <Eye className="w-3 h-3" />,
    classes: "bg-stone-400/20 text-stone-200 border-stone-400/40",
  },
};

export const Navbar: FC<NavbarProps> = ({
  onRefresh,
  isRefreshing = false,
  statusBadge,
  activeTab = "SUMMARY",
  onTabChange,
}) => {
  const { isAuthenticated, user, logout, isLoading } = useAuth();

  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalTab, setAuthModalTab] = useState<"signin" | "signup">("signin");
  const [adminModalOpen, setAdminModalOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const openSignIn = () => {
    setAuthModalTab("signin");
    setAuthModalOpen(true);
    setUserMenuOpen(false);
  };

  const handleLogout = () => {
    logout();
    setUserMenuOpen(false);
  };

  const roleConfig = user ? ROLE_CONFIG[user.role] : null;

  return (
    <>
      <header className="sticky top-0 z-50 w-full px-6 py-3 shadow-md border-b bg-[#4A3426] text-amber-50">
        {/* Full-width inner container */}
        <div className="w-full flex flex-wrap items-center justify-between gap-3">

          {/* ── Brand ──────────────────────────────────────────────────────── */}
          <div className="flex items-center gap-3.5">
            <div className="w-9 h-9 rounded-lg flex items-center justify-center bg-white/10 border border-white/20 backdrop-blur-sm shadow-inner">
              <Activity className="w-5 h-5 text-amber-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold tracking-tight text-white leading-tight">
                  Andalusia AI Portfolio & Governance
                </h1>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider bg-amber-400 text-stone-900">
                  Live System
                </span>
              </div>
              <p className="text-[11px] text-amber-200/70">
                Interactive Project Tracker, Requirements & Clinical Benchmarks
              </p>
            </div>
          </div>

          {/* ── Business-Friendly Tab Navigation ──────────────────────────── */}
          {onTabChange && (
            <nav className="flex items-center gap-1 bg-stone-900/40 p-1 rounded-xl border border-white/10 text-xs">
              <button
                onClick={() => onTabChange("SUMMARY")}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg font-bold transition-all ${
                  activeTab === "SUMMARY"
                    ? "bg-amber-100 text-amber-950 shadow-sm"
                    : "text-amber-100/80 hover:text-white hover:bg-white/5"
                }`}
                title="Executive Overview, Feature Impacts & Benchmarks"
              >
                <Briefcase className="w-3.5 h-3.5 text-amber-700" />
                <span>Executive Summary</span>
              </button>

              <button
                onClick={() => onTabChange("TRACKER")}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg font-bold transition-all ${
                  activeTab === "TRACKER"
                    ? "bg-amber-100 text-amber-950 shadow-sm"
                    : "text-amber-100/80 hover:text-white hover:bg-white/5"
                }`}
                title="Interactive Delivery Grid, Task Lists & Requirements"
              >
                <LayoutGrid className="w-3.5 h-3.5" />
                <span>Project Delivery Matrix</span>
              </button>

              <button
                onClick={() => onTabChange("ANALYTICS")}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg font-bold transition-all ${
                  activeTab === "ANALYTICS"
                    ? "bg-amber-100 text-amber-950 shadow-sm"
                    : "text-amber-100/80 hover:text-white hover:bg-white/5"
                }`}
                title="Comparative Benchmarks, Radar Models & Analytics"
              >
                <BarChart2 className="w-3.5 h-3.5" />
                <span>Analytics & Performance</span>
              </button>
            </nav>
          )}

          {/* ── Right Controls ─────────────────────────────────────────────── */}
          <div className="flex items-center gap-2.5">
            {statusBadge}

            {onRefresh && (
              <button
                onClick={onRefresh}
                disabled={isRefreshing}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white/10 hover:bg-white/20 text-white border border-white/15 transition-all disabled:opacity-50"
                title="Refresh Portfolio"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin" : ""}`} />
                <span className="hidden sm:inline">Refresh</span>
              </button>
            )}

            {/* Auth Section */}
            {isLoading ? (
              // Hydration skeleton
              <div className="w-24 h-7 bg-white/10 rounded-lg animate-pulse" />
            ) : isAuthenticated && user ? (
              // ── Authenticated: User Menu ─────────────────────────────────
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen((v) => !v)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 border border-white/15 text-xs font-semibold text-white transition-all"
                >
                  {/* Avatar initials */}
                  <div className="w-5 h-5 rounded-full bg-amber-400 flex items-center justify-center text-stone-900 text-[10px] font-black">
                    {user.full_name.charAt(0).toUpperCase()}
                  </div>
                  <span className="hidden sm:inline max-w-[100px] truncate">
                    {user.full_name.split(" ")[0]}
                  </span>
                  {/* Role badge */}
                  {roleConfig && (
                    <span
                      className={`hidden sm:flex items-center gap-1 px-1.5 py-0.5 rounded-full border text-[10px] font-bold ${roleConfig.classes}`}
                    >
                      {roleConfig.icon}
                      {roleConfig.label}
                    </span>
                  )}
                  <ChevronDown className={`w-3 h-3 transition-transform ${userMenuOpen ? "rotate-180" : ""}`} />
                </button>

                {/* Dropdown */}
                {userMenuOpen && (
                  <>
                    {/* Click-away overlay */}
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setUserMenuOpen(false)}
                    />
                    <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl shadow-xl border border-stone-200 overflow-hidden z-20">
                      {/* User info header */}
                      <div className="px-4 py-3 bg-stone-50 border-b border-stone-200">
                        <p className="text-sm font-bold text-stone-800 truncate">{user.full_name}</p>
                        <p className="text-xs text-stone-500 truncate">{user.email}</p>
                        {roleConfig && (
                          <div className={`mt-1.5 inline-flex items-center gap-1 px-2 py-0.5 rounded-full border text-[10px] font-bold ${
                            user.role === "admin"
                              ? "bg-amber-100 text-amber-800 border-amber-300"
                              : user.role === "editor"
                              ? "bg-blue-100 text-blue-700 border-blue-300"
                              : "bg-stone-100 text-stone-600 border-stone-300"
                          }`}>
                            {roleConfig.icon}
                            {roleConfig.label}
                          </div>
                        )}
                      </div>

                      <div className="py-1">
                        {/* Admin Panel (admin only) */}
                        {user.role === "admin" && (
                          <button
                            onClick={() => { setAdminModalOpen(true); setUserMenuOpen(false); }}
                            className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-stone-700 hover:bg-amber-50 hover:text-amber-800 transition-colors"
                          >
                            <Users className="w-4 h-4 text-amber-600" />
                            <span className="font-medium">Admin Panel</span>
                            <span className="ml-auto text-[10px] px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-700 font-bold">
                              Admin
                            </span>
                          </button>
                        )}

                        {/* Sign Out */}
                        <button
                          onClick={handleLogout}
                          className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-stone-700 hover:bg-red-50 hover:text-red-700 transition-colors"
                        >
                          <LogOut className="w-4 h-4" />
                          <span className="font-medium">Sign Out</span>
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            ) : (
              // ── Guest: Sign In button ─────────────────────────────────────
              <button
                onClick={openSignIn}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-400 hover:bg-amber-300 text-stone-900 border border-amber-300 transition-all shadow-sm"
              >
                <LogIn className="w-3.5 h-3.5" />
                Sign In
              </button>
            )}
          </div>
        </div>
      </header>

      {/* ── Modals (Portal-mounted) ─────────────────────────────────────────── */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        initialTab={authModalTab}
      />
      <AdminUsersModal
        isOpen={adminModalOpen}
        onClose={() => setAdminModalOpen(false)}
      />
    </>
  );
};
