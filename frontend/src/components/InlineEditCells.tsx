import React, { useState, useEffect } from "react";
import { Check, X } from "lucide-react";

interface InlineSelectCellProps {
  value: string | null;
  options: { code: string; label: string }[];
  onSave: (val: string) => Promise<void> | void;
  badgeStyle?: boolean;
  colorMap?: Record<string, { bg: string; text: string; border: string }>;
  disabled?: boolean;
}

export const InlineSelectCell: React.FC<InlineSelectCellProps> = ({
  value,
  options,
  onSave,
  badgeStyle = false,
  colorMap,
  disabled = false,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [currentVal, setCurrentVal] = useState(value || "");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    setCurrentVal(value || "");
  }, [value]);

  const handleSelectChange = async (newVal: string) => {
    setCurrentVal(newVal);
    setIsSaving(true);
    try {
      await onSave(newVal);
    } finally {
      setIsSaving(false);
      setIsEditing(false);
    }
  };

  if (isEditing && !disabled) {
    return (
      <select
        autoFocus
        value={currentVal}
        disabled={isSaving}
        onChange={(e) => handleSelectChange(e.target.value)}
        onBlur={() => setIsEditing(false)}
        className="w-full text-xs py-1 px-1.5 rounded border border-amber-500 bg-white shadow-sm focus:outline-none focus:ring-1 focus:ring-amber-500"
      >
        <option value="">-- Select --</option>
        {options.map((opt) => (
          <option key={opt.code} value={opt.code}>
            {opt.label}
          </option>
        ))}
      </select>
    );
  }

  const color = value && colorMap && colorMap[value];

  return (
    <div
      onClick={() => { if (!disabled) setIsEditing(true); }}
      title={disabled ? "Read-only (Sign in as Editor or Admin to modify)" : "Click to change"}
      className={`transition-all rounded px-1.5 py-0.5 inline-flex items-center gap-1 ${
        disabled ? "cursor-default opacity-85" : "cursor-pointer hover:ring-1 hover:ring-amber-400"
      } ${
        badgeStyle ? "border text-xs font-medium" : "text-sm text-stone-800"
      }`}
      style={
        color
          ? { backgroundColor: color.bg, color: color.text, borderColor: color.border }
          : undefined
      }
    >
      <span className="truncate">{value || <span className="text-stone-400 italic">None</span>}</span>
    </div>
  );
};

interface InlineTextCellProps {
  value: string | null;
  onSave: (val: string) => Promise<void> | void;
  multiline?: boolean;
  disabled?: boolean;
}

export const InlineTextCell: React.FC<InlineTextCellProps> = ({
  value,
  onSave,
  multiline = false,
  disabled = false,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [val, setVal] = useState(value || "");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    setVal(value || "");
  }, [value]);

  const handleSubmit = async () => {
    if (val === (value || "")) {
      setIsEditing(false);
      return;
    }
    setIsSaving(true);
    try {
      await onSave(val);
      setIsEditing(false);
    } finally {
      setIsSaving(false);
    }
  };

  if (isEditing && !disabled) {
    return (
      <div className="flex items-center gap-1 w-full" onClick={(e) => e.stopPropagation()}>
        {multiline ? (
          <textarea
            autoFocus
            rows={2}
            value={val}
            disabled={isSaving}
            onChange={(e) => setVal(e.target.value)}
            className="w-full text-xs p-1 rounded border border-amber-500 bg-white focus:outline-none"
          />
        ) : (
          <input
            autoFocus
            type="text"
            value={val}
            disabled={isSaving}
            onChange={(e) => setVal(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSubmit();
              if (e.key === "Escape") setIsEditing(false);
            }}
            className="w-full text-xs p-1 rounded border border-amber-500 bg-white focus:outline-none"
          />
        )}
        <button
          onClick={handleSubmit}
          disabled={isSaving}
          className="p-1 text-emerald-600 hover:bg-emerald-50 rounded"
        >
          <Check className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => setIsEditing(false)}
          className="p-1 text-stone-500 hover:bg-stone-100 rounded"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  }

  return (
    <div
      onClick={() => { if (!disabled) setIsEditing(true); }}
      title={disabled ? "Read-only (Sign in as Editor or Admin to modify)" : "Click to edit"}
      className={`rounded px-1.5 py-0.5 truncate transition-colors text-sm text-stone-800 ${
        disabled ? "cursor-default" : "cursor-pointer hover:bg-amber-50/60"
      }`}
    >
      {value ? value : <span className="text-stone-300 italic">Empty</span>}
    </div>
  );
};

interface InlineProgressCellProps {
  value: number | null;
  onSave: (val: number) => Promise<void> | void;
  disabled?: boolean;
}

export const InlineProgressCell: React.FC<InlineProgressCellProps> = ({ value, onSave, disabled = false }) => {
  const [isEditing, setIsEditing] = useState(false);
  const pct = value !== null && value !== undefined ? Math.round(value * 100) : 0;
  const [val, setVal] = useState(pct);

  useEffect(() => {
    setVal(value !== null && value !== undefined ? Math.round(value * 100) : 0);
  }, [value]);

  const handleCommit = async () => {
    setIsEditing(false);
    await onSave(val / 100);
  };

  if (isEditing && !disabled) {
    return (
      <div
        className="flex items-center gap-2 p-1 bg-white rounded border border-amber-500 shadow-sm"
        onClick={(e) => e.stopPropagation()}
      >
        <input
          type="range"
          min="0"
          max="100"
          step="5"
          value={val}
          onChange={(e) => setVal(Number(e.target.value))}
          className="w-20 accent-amber-600"
        />
        <span className="text-xs font-semibold w-8 text-right">{val}%</span>
        <button
          onClick={handleCommit}
          className="text-xs px-1.5 py-0.5 bg-emerald-600 text-white rounded font-medium hover:bg-emerald-700"
        >
          Save
        </button>
      </div>
    );
  }

  return (
    <div
      onClick={() => { if (!disabled) setIsEditing(true); }}
      title={disabled ? "Read-only (Sign in as Editor or Admin to modify)" : "Click to adjust %"}
      className={`flex items-center gap-2 w-full max-w-[130px] rounded p-1 transition-all ${
        disabled ? "cursor-default" : "cursor-pointer hover:ring-1 hover:ring-amber-400"
      }`}
    >
      <div className="flex-1 h-2 bg-stone-200 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-300"
          style={{
            width: `${pct}%`,
            backgroundColor:
              pct >= 80 ? "#16a34a" : pct >= 40 ? "#d97706" : "#dc2626",
          }}
        />
      </div>
      <span className="text-xs font-semibold text-stone-700 w-8 text-right">
        {value !== null ? `${pct}%` : "--"}
      </span>
    </div>
  );
};

