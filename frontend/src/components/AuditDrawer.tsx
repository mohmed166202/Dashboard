import React from "react";
import type { AuditRecord } from "../types/tracker";
import { X, Clock, User, ArrowRight } from "lucide-react";

interface AuditDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  entityId: string | null;
  history: AuditRecord[];
  isLoading: boolean;
}

export const AuditDrawer: React.FC<AuditDrawerProps> = ({
  isOpen,
  onClose,
  entityId,
  history,
  isLoading,
}) => {
  if (!isOpen || !entityId) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-stone-900/30 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-md bg-white shadow-2xl h-full flex flex-col animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="p-4 border-b border-stone-200 flex items-center justify-between bg-stone-50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center text-amber-800">
              <Clock className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-stone-800">Audit Revision History</h3>
              <p className="text-xs text-stone-500 font-mono">Entity: {entityId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded hover:bg-stone-200 text-stone-500">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {isLoading ? (
            <div className="py-12 text-center text-xs text-stone-500">Loading audit log...</div>
          ) : history.length === 0 ? (
            <div className="py-12 text-center text-xs text-stone-400">
              No previous audit records recorded for this entity.
            </div>
          ) : (
            history.map((record) => (
              <div
                key={record.id}
                className="p-3 rounded-lg border border-stone-200 bg-stone-50/60 text-xs space-y-1.5 hover:bg-amber-50/20 transition-colors"
              >
                <div className="flex items-center justify-between text-stone-500 text-[11px]">
                  <span className="font-semibold text-amber-800 uppercase tracking-wider">
                    {record.action}
                  </span>
                  <span>{record.timestamp}</span>
                </div>

                <div className="font-medium text-stone-800">
                  Field: <code className="bg-stone-200 px-1 py-0.5 rounded">{record.field_name || "Record"}</code>
                </div>

                {record.old_value !== null && record.new_value !== null && (
                  <div className="flex items-center gap-1.5 text-stone-600 bg-white p-2 rounded border border-stone-200 font-mono text-[11px]">
                    <span className="text-red-600 line-through truncate max-w-[140px]">
                      {record.old_value || "None"}
                    </span>
                    <ArrowRight className="w-3 h-3 text-stone-400 shrink-0" />
                    <span className="text-emerald-700 font-semibold truncate max-w-[140px]">
                      {record.new_value || "None"}
                    </span>
                  </div>
                )}

                <div className="flex items-center gap-1 text-[11px] text-stone-400 pt-0.5">
                  <User className="w-3 h-3" />
                  <span>Changed by: {record.user || "System"}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

