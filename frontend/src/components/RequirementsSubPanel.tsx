import React, { useState } from "react";
import type { Requirement, DropdownLists } from "../types/tracker";
import { InlineSelectCell, InlineTextCell } from "./InlineEditCells";
import { useCreateRequirement, useUpdateRequirement } from "../hooks/useTrackerQueries";
import { Plus, CheckCircle2, Clock, AlertTriangle, FileCode } from "lucide-react";
import { useAuth } from "../context/AuthContext";

interface RequirementsSubPanelProps {
  projectId: string;
  projectName: string;
  requirements: Requirement[];
  dropdowns?: DropdownLists;
}

export const RequirementsSubPanel: React.FC<RequirementsSubPanelProps> = ({
  projectId,
  projectName,
  requirements,
  dropdowns,
}) => {
  const { isEditor, user } = useAuth();
  const [activeTab, setActiveTab] = useState<"ALL" | "Functional" | "Non-Functional">("ALL");
  const [isAdding, setIsAdding] = useState(false);
  const [newCat, setNewCat] = useState<"Functional" | "Non-Functional">("Functional");
  const [newReqText, setNewReqText] = useState("");
  const [newNfrArea, setNewNfrArea] = useState("");

  const updateReqMutation = useUpdateRequirement();
  const createReqMutation = useCreateRequirement();

  const filteredReqs = requirements.filter((r) => {
    if (activeTab === "ALL") return true;
    return r.category === activeTab;
  });

  const handleUpdate = async (reqId: string, updates: Partial<Requirement>) => {
    await updateReqMutation.mutateAsync({
      reqId,
      updates: { ...updates, user: user?.full_name || user?.email || "WebUser" },
    });
  };

  const handleCreate = async () => {
    if (!newReqText.trim()) return;

    // Generate next requirement ID based on project
    const prefix = newCat === "Functional" ? "FR" : "NFR";
    const existingCount = requirements.filter((r) => r.category === newCat).length;
    const nextNum = String(existingCount + 1).padStart(2, "0");
    const generatedId = `${projectId}-${prefix}-${nextNum}`;

    await createReqMutation.mutateAsync({
      req_id: generatedId,
      project_id: projectId,
      category: newCat,
      nfr_area: newCat === "Non-Functional" ? newNfrArea : null,
      requirement: newReqText.trim(),
      status: "Proposed",
      priority: "Medium",
      user: user?.full_name || user?.email || "WebUser",
    });

    setNewReqText("");
    setIsAdding(false);
  };

  const statusColors: Record<string, { bg: string; text: string; border: string }> = {
    Implemented: { bg: "#ECFDF5", text: "#065F46", border: "#A7F3D0" },
    Verified: { bg: "#F0FDF4", text: "#166534", border: "#BBF7D0" },
    "In Progress": { bg: "#EFF6FF", text: "#1E40AF", border: "#BFDBFE" },
    Approved: { bg: "#FEF3C7", text: "#92400E", border: "#FDE68A" },
    Proposed: { bg: "#F3F4F6", text: "#374151", border: "#E5E7EB" },
  };

  return (
    <div className="bg-stone-50 border-t border-b border-amber-200/60 p-4 shadow-inner">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-3 pb-2 border-b border-stone-200">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-amber-700" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-stone-700">
            Requirements for {projectName} ({projectId})
          </h4>
          <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold">
            {requirements.length} Total
          </span>
        </div>

        {/* Tab switcher & Add buttons */}
        <div className="flex items-center gap-2">
          <div className="inline-flex rounded-lg p-0.5 bg-stone-200 text-xs">
            {(["ALL", "Functional", "Non-Functional"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                  activeTab === tab
                    ? "bg-white text-stone-900 shadow-sm"
                    : "text-stone-600 hover:text-stone-900"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {isEditor ? (
            <>
              <button
                onClick={() => {
                  setNewCat("Functional");
                  setIsAdding(true);
                }}
                className="inline-flex items-center gap-1 text-xs px-2.5 py-1 bg-amber-700 text-white font-medium rounded-lg hover:bg-amber-800 shadow-sm transition-colors"
              >
                <Plus className="w-3.5 h-3.5" /> Add FR
              </button>
              <button
                onClick={() => {
                  setNewCat("Non-Functional");
                  setIsAdding(true);
                }}
                className="inline-flex items-center gap-1 text-xs px-2.5 py-1 bg-stone-700 text-white font-medium rounded-lg hover:bg-stone-800 shadow-sm transition-colors"
              >
                <Plus className="w-3.5 h-3.5" /> Add NFR
              </button>
            </>
          ) : (
            <span
              className="text-[11px] text-stone-500 italic bg-stone-200/60 px-2 py-0.5 rounded cursor-help"
              title="Read-only mode. Contact Admin for Editor permissions"
            >
              Read-only mode
            </span>
          )}
        </div>
      </div>

      {/* Inline Add Requirement Form */}
      {isAdding && (
        <div className="mb-4 p-3 bg-white border border-amber-300 rounded-lg shadow-sm flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold text-amber-800 uppercase px-2 py-0.5 bg-amber-50 rounded border border-amber-200">
            New {newCat} Requirement
          </span>
          {newCat === "Non-Functional" && dropdowns && (
            <select
              value={newNfrArea}
              onChange={(e) => setNewNfrArea(e.target.value)}
              className="text-xs p-1.5 rounded border border-stone-300 bg-white"
            >
              <option value="">-- NFR Area --</option>
              {dropdowns.nfr_areas.map((a) => (
                <option key={a.code} value={a.code}>
                  {a.label}
                </option>
              ))}
            </select>
          )}
          <input
            type="text"
            placeholder="Requirement description or title..."
            value={newReqText}
            onChange={(e) => setNewReqText(e.target.value)}
            className="flex-1 text-xs p-1.5 rounded border border-stone-300 bg-white focus:outline-none focus:border-amber-500"
          />
          <button
            onClick={handleCreate}
            className="text-xs px-3 py-1 bg-emerald-600 text-white font-semibold rounded hover:bg-emerald-700"
          >
            Save
          </button>
          <button
            onClick={() => setIsAdding(false)}
            className="text-xs px-2.5 py-1 text-stone-600 hover:bg-stone-100 rounded"
          >
            Cancel
          </button>
        </div>
      )}

      {/* Requirements Table */}
      {filteredReqs.length === 0 ? (
        <div className="py-6 text-center text-xs text-stone-500 bg-white/60 rounded-lg border border-dashed border-stone-300">
          No requirements found in this category. Click &quot;Add FR&quot; or &quot;Add NFR&quot; above to create one.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-stone-200 bg-white shadow-sm max-h-[360px] overflow-y-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="sticky top-0 bg-stone-100 text-stone-700 font-semibold border-b border-stone-200">
              <tr>
                <th className="py-2 px-3 w-28">Req ID</th>
                <th className="py-2 px-3 w-28">Category</th>
                <th className="py-2 px-3 w-32">NFR Area</th>
                <th className="py-2 px-3">Requirement</th>
                <th className="py-2 px-3 w-32">Status</th>
                <th className="py-2 px-3 w-24">Priority</th>
                <th className="py-2 px-3 w-32">Owner</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {filteredReqs.map((req) => (
                <tr key={req.req_id} className="hover:bg-amber-50/30 transition-colors">
                  <td className="py-1.5 px-3 font-mono font-medium text-stone-800">
                    {req.req_id}
                  </td>
                  <td className="py-1.5 px-3">
                    <span
                      className={`inline-block px-1.5 py-0.5 rounded text-[11px] font-medium ${
                        req.category === "Functional"
                          ? "bg-blue-50 text-blue-700 border border-blue-200"
                          : "bg-purple-50 text-purple-700 border border-purple-200"
                      }`}
                    >
                      {req.category}
                    </span>
                  </td>
                  <td className="py-1.5 px-3 text-stone-600">
                    {req.nfr_area || <span className="text-stone-300">--</span>}
                  </td>
                  <td className="py-1.5 px-3">
                    <InlineTextCell
                      value={req.requirement}
                      onSave={(val) => handleUpdate(req.req_id, { requirement: val })}
                      disabled={!isEditor}
                    />
                  </td>
                  <td className="py-1.5 px-3">
                    <InlineSelectCell
                      value={req.status}
                      options={dropdowns?.req_statuses || []}
                      onSave={(val) => handleUpdate(req.req_id, { status: val })}
                      badgeStyle
                      colorMap={statusColors}
                      disabled={!isEditor}
                    />
                  </td>
                  <td className="py-1.5 px-3">
                    <InlineSelectCell
                      value={req.priority}
                      options={dropdowns?.req_priorities || []}
                      onSave={(val) => handleUpdate(req.req_id, { priority: val })}
                      disabled={!isEditor}
                    />
                  </td>
                  <td className="py-1.5 px-3">
                    <InlineTextCell
                      value={req.owner}
                      onSave={(val) => handleUpdate(req.req_id, { owner: val })}
                      disabled={!isEditor}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

