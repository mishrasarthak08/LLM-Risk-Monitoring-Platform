"use client";

import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { api } from "@/lib/api";
import {
  Waves,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  FileText,
  Clock,
  ShieldAlert,
  Send,
  Save,
} from "lucide-react";

export default function DriftPage() {
  const [driftEvents, setDriftEvents] = useState<any[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<any | null>(null);
  const [newStatus, setNewStatus] = useState<string>("INVESTIGATING");
  const [triageNotes, setTriageNotes] = useState<string>("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [statusBanner, setStatusBanner] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    async function loadDrift() {
      try {
        const data = await api.getDriftEvents();
        setDriftEvents(data);
        if (data.length > 0) {
          setSelectedEvent(data[0]);
          setNewStatus(data[0].triage_status);
          setTriageNotes(data[0].resolution_notes || "");
        }
      } catch (err) {
        console.error("Failed to load drift events", err);
      } finally {
        setLoading(false);
      }
    }
    loadDrift();
  }, []);

  const handleSaveTriage = async () => {
    if (!selectedEvent) return;
    setSaving(true);
    setStatusBanner(null);
    try {
      const updated = await api.triageDriftEvent(selectedEvent.id, newStatus, triageNotes);
      setSelectedEvent(updated);
      const refreshed = await api.getDriftEvents();
      setDriftEvents(refreshed);
      setStatusBanner({ type: "success", text: "Triage status updated and cryptographically committed to audit ledger." });
    } catch (err: any) {
      setStatusBanner({ type: "error", text: "Failed to update triage status: " + (err.message || err) });
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <Header
        title="Continuous Drift Monitoring & Incident Desk"
        subtitle="Distributional shift detection (PSI, KS test, Two-proportion Z) across rolling production traffic."
      />

      <main className="p-8 space-y-8">
        {statusBanner && (
          <div
            className={`p-3.5 rounded-xl border flex items-center justify-between text-xs animate-in fade-in ${
              statusBanner.type === "success"
                ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-300"
                : "bg-rose-950/40 border-rose-500/40 text-rose-300"
            }`}
          >
            <div className="flex items-center space-x-2">
              {statusBanner.type === "success" ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <AlertTriangle className="w-4 h-4 text-rose-400" />}
              <span>{statusBanner.text}</span>
            </div>
            <button onClick={() => setStatusBanner(null)} className="text-slate-400 hover:text-slate-200">
              ✕
            </button>
          </div>
        )}

        {/* Active Incidents & Triage Bench */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Incidents Table (7 cols) */}
          <div className="lg:col-span-7 bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
                <Waves className="w-4 h-4 text-cyan-400" />
                <span>Detected Production Drift Events</span>
              </h2>
              <span className="text-xs text-slate-400 font-mono">Rolling Window: 24 Hours</span>
            </div>

            <div className="space-y-3">
              {driftEvents.map((evt) => {
                const isSelected = selectedEvent?.id === evt.id;
                const isCritical = evt.severity === "CRITICAL";
                return (
                  <div
                    key={evt.id}
                    onClick={() => {
                      setSelectedEvent(evt);
                      setNewStatus(evt.triage_status);
                      setTriageNotes(evt.resolution_notes || "");
                    }}
                    className={`p-4 rounded-xl border cursor-pointer transition-colors text-xs ${
                      isSelected
                        ? "bg-indigo-950/30 border-indigo-500/50"
                        : "bg-slate-950 border-slate-800 hover:bg-slate-900/40"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span
                          className={`w-2 h-2 rounded-full ${
                            isCritical ? "bg-rose-500 animate-ping" : "bg-amber-400"
                          }`}
                        />
                        <span className="font-mono font-bold text-slate-200 uppercase">
                          {evt.metric_name} ({evt.test_type})
                        </span>
                      </div>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          isCritical
                            ? "bg-rose-950/60 text-rose-400 border border-rose-800/40"
                            : "bg-amber-950/60 text-amber-400 border border-amber-800/40"
                        }`}
                      >
                        {evt.severity}
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-800/60 font-mono text-[11px] text-slate-400">
                      <div>
                        <span className="block text-[10px] text-slate-500 uppercase">Statistic</span>
                        <span className="text-slate-200 font-bold">{evt.statistic_value.toFixed(4)}</span>
                      </div>
                      <div>
                        <span className="block text-[10px] text-slate-500 uppercase">p-value</span>
                        <span className="text-rose-400 font-bold">{evt.p_value?.toFixed(4) || "N/A"}</span>
                      </div>
                      <div>
                        <span className="block text-[10px] text-slate-500 uppercase">Sample (N)</span>
                        <span className="text-slate-200">{evt.sample_size}</span>
                      </div>
                    </div>

                    <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500">
                      <span>Status: <strong className="text-amber-400">{evt.triage_status}</strong></span>
                      <span>Assigned: {evt.acknowledged_by || "Unassigned"}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Incident Triage Workbench (5 cols) */}
          <div className="lg:col-span-5 bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-5">
            <h3 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              <span>Incident Triage & Human Review</span>
            </h3>

            {selectedEvent ? (
              <div className="space-y-4 text-xs">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block font-mono">Incident Target</span>
                  <div className="font-mono text-slate-200 font-bold mt-0.5">
                    {selectedEvent.metric_name} on {selectedEvent.feature_name}
                  </div>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-slate-300 block mb-1.5">
                    Triage Disposition
                  </label>
                  <div className="space-y-1.5">
                    {[
                      { val: "INVESTIGATING", label: "Investigating Root Cause" },
                      { val: "CONFIRMED_ISSUE", label: "Confirmed Quality Issue (Rollback candidate)" },
                      { val: "BENIGN_SHIFT", label: "Benign Population Shift (Approve baseline rebuild)" },
                      { val: "FALSE_POSITIVE", label: "False Positive (Tune threshold)" },
                      { val: "RESOLVED", label: "Resolved (Mitigation complete)" },
                    ].map((opt) => (
                      <label
                        key={opt.val}
                        className={`flex items-center space-x-2 p-2 rounded-lg border cursor-pointer transition-colors ${
                          newStatus === opt.val
                            ? "bg-indigo-950/40 border-indigo-500/50 text-indigo-200"
                            : "bg-slate-950 border-slate-800 text-slate-400"
                        }`}
                      >
                        <input
                          type="radio"
                          name="triage_status"
                          value={opt.val}
                          checked={newStatus === opt.val}
                          onChange={(e) => setNewStatus(e.target.value)}
                          className="text-indigo-600 focus:ring-0"
                        />
                        <span className="text-xs">{opt.label}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-slate-300 block mb-1">
                    Triage Notes & Root Cause Analysis
                  </label>
                  <textarea
                    rows={4}
                    value={triageNotes}
                    onChange={(e) => setTriageNotes(e.target.value)}
                    placeholder="Enter diagnostic details, pipeline issues, or resolution notes..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-sans"
                  />
                </div>

                <button
                  onClick={handleSaveTriage}
                  disabled={saving}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 rounded-lg text-xs flex items-center justify-center space-x-2 transition-colors disabled:opacity-50"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>{saving ? "Saving to Audit Trail..." : "Save Triage Disposition"}</span>
                </button>
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-slate-500">
                Select an incident from the left to view triage controls.
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  );
}

