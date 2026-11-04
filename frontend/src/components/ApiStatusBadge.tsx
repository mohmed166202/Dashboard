/**
 * ApiStatusBadge — displayed in the Navbar.
 * Uses useHealth() to show real-time API connectivity status.
 */

import { Wifi, WifiOff, Loader2 } from "lucide-react";
import { useHealth } from "../hooks/useApiQueries";

export function ApiStatusBadge() {
  const { data, isLoading, isError } = useHealth();

  if (isLoading) {
    return (
      <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1.5 rounded-md bg-white/10 text-xs text-white/70 border border-white/15">
        <Loader2 className="w-3.5 h-3.5 animate-spin text-amber-200" />
        <span>Connecting...</span>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1.5 rounded-md bg-red-900/40 text-xs text-red-200 border border-red-700/50">
        <WifiOff className="w-3.5 h-3.5" />
        <span>API Offline</span>
      </div>
    );
  }

  return (
    <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1.5 rounded-md bg-white/10 text-xs text-emerald-200 border border-white/15">
      <Wifi className="w-3.5 h-3.5" />
      <span>API v{data.api_version}</span>
      {data.db_connected && (
        <span className="text-white/50">· DB ✓</span>
      )}
    </div>
  );
}

