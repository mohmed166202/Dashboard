import React, { useState } from "react";
import type { Project, DropdownLists } from "../types/tracker";
import { Plus, X } from "lucide-react";
import { useCreateProject } from "../hooks/useTrackerQueries";

interface NewProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  dropdowns?: DropdownLists;
  existingCount: number;
}

export const NewProjectModal: React.FC<NewProjectModalProps> = ({
  isOpen,
  onClose,
  dropdowns,
  existingCount,
}) => {
  const nextId = `AI-${String(existingCount + 1).padStart(3, "0")}`;
  const [formData, setFormData] = useState({
    id: nextId,
    project: "",
    team: "AI 02",
    type: "AI Product",
    domain: "1. Clinical Informatics",
    phase: "Idea",
    status: "On Track",
    priority: "Medium",
    percent_complete: 0.0,
    description: "",
    business_owner: "",
    technical_owner: "",
  });

  const createMutation = useCreateProject();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.project.trim()) return;

    await createMutation.mutateAsync({
      ...formData,
      percent_complete: Number(formData.percent_complete) / 100,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-xl shadow-2xl border border-stone-200 max-w-xl w-full p-6 animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between pb-3 border-b border-stone-200 mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center text-amber-800 font-bold">
              +
            </div>
            <div>
              <h3 className="text-base font-bold text-stone-800">Add New AI Project</h3>
              <p className="text-xs text-stone-500">Create a tracked project with automatic catalog ID</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-stone-100 text-stone-400">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-stone-700 mb-1">Project ID</label>
              <input
                type="text"
                required
                value={formData.id}
                onChange={(e) => setFormData({ ...formData, id: e.target.value })}
                className="w-full p-2 rounded-lg border border-stone-300 font-mono bg-stone-50"
              />
            </div>
            <div>
              <label className="block font-semibold text-stone-700 mb-1">Project Name *</label>
              <input
                type="text"
                required
                placeholder="e.g. Clinical Voice Copilot"
                value={formData.project}
                onChange={(e) => setFormData({ ...formData, project: e.target.value })}
                className="w-full p-2 rounded-lg border border-stone-300 focus:outline-none focus:border-amber-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block font-semibold text-stone-700 mb-1">Domain</label>
              <select
                value={formData.domain}
                onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                className="w-full p-2 rounded-lg border border-stone-300 bg-white"
              >
                {dropdowns?.domains.map((d) => (
                  <option key={d.code} value={d.code}>
                    {d.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block font-semibold text-stone-700 mb-1">Phase</label>
              <select
                value={formData.phase}
                onChange={(e) => setFormData({ ...formData, phase: e.target.value })}
                className="w-full p-2 rounded-lg border border-stone-300 bg-white"
              >
                {dropdowns?.phases.map((p) => (
                  <option key={p.code} value={p.code}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block font-semibold text-stone-700 mb-1">Status</label>
              <select
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                className="w-full p-2 rounded-lg border border-stone-300 bg-white"
              >
                {dropdowns?.statuses.map((s) => (
                  <option key={s.code} value={s.code}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block font-semibold text-stone-700 mb-1">Type</label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                className="w-full p-2 rounded-lg border border-stone-300 bg-white"
              >
                {dropdowns?.types.map((t) => (
                  <option key={t.code} value={t.code}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block font-semibold text-stone-700 mb-1">Priority</label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                className="w-full p-2 rounded-lg border border-stone-300 bg-white"
              >
                {dropdowns?.priorities.map((p) => (
                  <option key={p.code} value={p.code}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block font-semibold text-stone-700 mb-1">Progress (%)</label>
              <input
                type="number"
                min="0"
                max="100"
                value={formData.percent_complete}
                onChange={(e) => setFormData({ ...formData, percent_complete: Number(e.target.value) })}
                className="w-full p-2 rounded-lg border border-stone-300"
              />
            </div>
          </div>

          <div>
            <label className="block font-semibold text-stone-700 mb-1">Description</label>
            <textarea
              rows={2}
              placeholder="Summary of scope, clinical utility and workflow..."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full p-2 rounded-lg border border-stone-300 focus:outline-none focus:border-amber-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-stone-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg border border-stone-300 font-semibold text-stone-700 hover:bg-stone-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-5 py-2 rounded-lg bg-amber-800 text-white font-bold hover:bg-amber-900 shadow transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-4 h-4" />
              {createMutation.isPending ? "Creating..." : "Save Project"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

