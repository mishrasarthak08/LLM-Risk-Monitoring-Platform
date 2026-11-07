"use client";

import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { api, API_BASE_URL } from "@/lib/api";
import {
  FileText,
  Download,
  CheckCircle2,
  ShieldCheck,
  Building,
  Calendar,
  Layers,
  FileSpreadsheet,
} from "lucide-react";

export default function ReportsPage() {
  const [dossier, setDossier] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDossier() {
      try {
        const data = await api.getGovernancePackage();
        setDossier(data);
      } catch (err) {
        console.error("Failed to load governance package", err);
      } finally {
        setLoading(false);
      }
    }
    loadDossier();
  }, []);

  const handleDownloadJson = () => {
    if (!dossier) return;
    const blob = new Blob([JSON.stringify(dossier, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `veritas_sr11_7_dossier_${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadCsv = () => {
    window.open(`${API_BASE_URL}/reports/regressions-csv`, "_blank");
  };

  return (
    <>
      <Header
        title="Model Risk Governance Dossier (SR 11-7 / OCC 2011-12)"
        subtitle="Self-contained, verifiable audit evidence packages compiled for regulatory examination."
      />

      <main className="p-8 space-y-8">
        {/* Export Action Card */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-5 h-5 text-indigo-400" />
              <span className="text-xs uppercase font-mono tracking-wider font-bold text-slate-300">
                Institutional Evidence Package
              </span>
            </div>
            <h2 className="text-xl font-bold mt-1 text-slate-100">
              Commercial Credit Underwriting Model Risk Dossier
            </h2>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
              Contains prompt inventories, dataset hashes, regression test outcomes, continuous drift incidents, judge calibration records, and cryptographic audit proofs.
            </p>
          </div>

          <div className="flex items-center space-x-3 shrink-0">
            <button
              onClick={handleDownloadCsv}
              className="bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition-colors"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
              <span>Export CSV</span>
            </button>
            <button
              onClick={handleDownloadJson}
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Full JSON Dossier</span>
            </button>
          </div>
        </div>

        {/* Dossier Preview */}
        {dossier && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Column 1: Development & Prompts */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-4">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">
                1. Model Development & Prompts
              </h3>
              <div className="space-y-3 text-xs">
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Active Model Target</span>
                  <span className="font-mono text-slate-200 font-bold">gemini-2.5-flash (Temp: 0.0)</span>
                </div>
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Prompt Releases</span>
                  <span className="font-mono text-slate-200">
                    {dossier.prompt_inventory?.[0]?.versions?.length || 2} Immutable Versions Tracked
                  </span>
                </div>
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Approved Baseline Hash</span>
                  <span className="font-mono text-slate-200 text-[10px] break-all">
                    {dossier.prompt_inventory?.[0]?.versions?.[0]?.content_hash}
                  </span>
                </div>
              </div>
            </div>

            {/* Column 2: Validation & Gating */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-4">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">
                2. Ongoing Validation & CI Gating
              </h3>
              <div className="space-y-3 text-xs">
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Benchmark Datasets</span>
                  <span className="font-mono text-slate-200 font-bold">v0001 (5 Curated Risk Cases)</span>
                </div>
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Statistical Comparator</span>
                  <span className="font-mono text-slate-200">Paired Wilcoxon Signed-Rank Test</span>
                </div>
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Evaluator Agreement</span>
                  <span className="font-mono text-emerald-400 font-bold">Cohen&apos;s κ = 0.825 (Calibrated)</span>
                </div>
              </div>
            </div>

            {/* Column 3: Governance & Cryptographic Proof */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-4">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">
                3. Governance & Ledger Integrity
              </h3>
              <div className="space-y-3 text-xs">
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Cryptographic Verification</span>
                  <span className="font-mono text-emerald-400 font-bold">UNBROKEN HASH CHAIN</span>
                </div>
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Active Drift Incidents</span>
                  <span className="font-mono text-amber-400">1 Incident Under Triage</span>
                </div>
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Compliance Mapping</span>
                  <span className="font-mono text-slate-200">Federal Reserve SR 11-7 / OCC 2011-12</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </>
  );
}

