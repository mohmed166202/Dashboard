// ─────────────────────────────────────────────────────────────────────────────
// AuthModal — Sign In / Sign Up Modal
// Sleek animated modal matching the amber/stone theme.
// ─────────────────────────────────────────────────────────────────────────────

import React, { useState, useEffect, useRef } from "react";
import { X, Mail, Lock, User, Eye, EyeOff, Loader2, AlertCircle, ShieldCheck } from "lucide-react";
import { useAuth } from "../context/AuthContext";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialTab?: "signin" | "signup";
}

type ModalTab = "signin" | "signup";

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, initialTab = "signin" }) => {
  const { login, register, isLoading, error, clearError } = useAuth();
  const [tab, setTab] = useState<ModalTab>(initialTab);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  // Form fields
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const emailRef = useRef<HTMLInputElement>(null);

  // Reset state when modal opens/tab changes
  useEffect(() => {
    if (isOpen) {
      setEmail("");
      setFullName("");
      setPassword("");
      setConfirmPassword("");
      setLocalError(null);
      setShowPassword(false);
      setShowConfirm(false);
      clearError();
      setTimeout(() => emailRef.current?.focus(), 50);
    }
  }, [isOpen, tab]);

  useEffect(() => {
    setTab(initialTab);
  }, [initialTab]);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    if (isOpen) window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const switchTab = (t: ModalTab) => {
    setTab(t);
    setLocalError(null);
    clearError();
  };

  const validate = (): string | null => {
    if (!email.trim()) return tab === "signin" ? "Username or email is required." : "Email is required.";
    if (tab === "signup" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return "Enter a valid email address.";
    if (!password) return "Password is required.";
    if (password.length < 6) return "Password must be at least 6 characters.";
    if (tab === "signup") {
      if (!fullName.trim()) return "Full name is required.";
      if (password !== confirmPassword) return "Passwords do not match.";
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validationError = validate();
    if (validationError) { setLocalError(validationError); return; }
    setLocalError(null);
    setSubmitting(true);
    try {
      if (tab === "signin") {
        await login({ username_or_email: email.trim(), email: email.trim(), password });
      } else {
        await register({ email: email.trim(), full_name: fullName.trim(), password });
      }
      onClose();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "An error occurred. Please try again.";
      setLocalError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const displayError = localError ?? error;

  return (
    // Backdrop
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      {/* Modal Panel */}
      <div className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl border border-stone-200 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="bg-[#4A3426] px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center border border-white/20">
              <ShieldCheck className="w-4 h-4 text-amber-300" />
            </div>
            <div>
              <h2 className="text-white text-sm font-bold leading-tight">Andalusia AI Portfolio</h2>
              <p className="text-amber-200/70 text-[11px]">Secure Access Portal</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white/60 hover:text-white hover:bg-white/10 p-1.5 rounded-lg transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-stone-200 bg-stone-50">
          {(["signin", "signup"] as ModalTab[]).map((t) => (
            <button
              key={t}
              onClick={() => switchTab(t)}
              className={`flex-1 py-3 text-sm font-semibold transition-all border-b-2 ${
                tab === t
                  ? "border-amber-600 text-amber-800 bg-white"
                  : "border-transparent text-stone-500 hover:text-stone-700 hover:bg-stone-100"
              }`}
            >
              {t === "signin" ? "Sign In" : "Create Account"}
            </button>
          ))}
        </div>

        {/* Form Body */}
        <div className="px-6 py-5">
          {tab === "signup" && (
            <div className="mb-4 p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-800">
              <span className="font-semibold">Note:</span> New accounts start as{" "}
              <span className="font-bold">Viewer</span>. An Admin can promote your role.
              {" "}The first user registered becomes Admin automatically.
            </div>
          )}

          {/* Error Banner */}
          {displayError && (
            <div className="mb-4 flex items-start gap-2 p-3 rounded-lg bg-red-50 border border-red-200 text-xs text-red-700">
              <AlertCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
              <span>{displayError}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate className="space-y-3.5">
            {/* Full Name (signup only) */}
            {tab === "signup" && (
              <div>
                <label className="block text-xs font-semibold text-stone-600 mb-1.5">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-stone-400" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Your full name"
                    className="w-full pl-9 pr-3 py-2.5 text-sm rounded-lg border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all"
                    disabled={submitting}
                    autoComplete="name"
                  />
                </div>
              </div>
            )}

            {/* Email or Username */}
            <div>
              <label className="block text-xs font-semibold text-stone-600 mb-1.5">
                {tab === "signin" ? "Username or Email" : "Email Address"}
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-stone-400" />
                <input
                  ref={emailRef}
                  type={tab === "signin" ? "text" : "email"}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={tab === "signin" ? "mohamed-galal or email" : "you@example.com"}
                  className="w-full pl-9 pr-3 py-2.5 text-sm rounded-lg border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all"
                  disabled={submitting}
                  autoComplete={tab === "signin" ? "username" : "email"}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-semibold text-stone-600 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-stone-400" />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={tab === "signin" ? "Your password" : "Min. 6 characters"}
                  className="w-full pl-9 pr-10 py-2.5 text-sm rounded-lg border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all"
                  disabled={submitting}
                  autoComplete={tab === "signin" ? "current-password" : "new-password"}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-600"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>

            {/* Confirm Password (signup only) */}
            {tab === "signup" && (
              <div>
                <label className="block text-xs font-semibold text-stone-600 mb-1.5">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-stone-400" />
                  <input
                    type={showConfirm ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Repeat password"
                    className="w-full pl-9 pr-10 py-2.5 text-sm rounded-lg border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all"
                    disabled={submitting}
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirm((v) => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-600"
                    tabIndex={-1}
                  >
                    {showConfirm ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submitting || isLoading}
              className="w-full mt-1 py-2.5 px-4 rounded-lg text-sm font-bold bg-[#4A3426] text-white hover:bg-[#3a2819] disabled:opacity-60 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-sm"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  {tab === "signin" ? "Signing in…" : "Creating account…"}
                </>
              ) : (
                tab === "signin" ? "Sign In" : "Create Account"
              )}
            </button>

            {/* Footer switch */}
            <p className="text-center text-xs text-stone-500 pt-1">
              {tab === "signin" ? (
                <>
                  Don't have an account?{" "}
                  <button type="button" onClick={() => switchTab("signup")} className="text-amber-700 font-semibold hover:underline">
                    Sign up
                  </button>
                </>
              ) : (
                <>
                  Already have an account?{" "}
                  <button type="button" onClick={() => switchTab("signin")} className="text-amber-700 font-semibold hover:underline">
                    Sign in
                  </button>
                </>
              )}
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

