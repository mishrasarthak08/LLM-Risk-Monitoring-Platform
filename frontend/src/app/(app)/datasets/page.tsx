"use client";

import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { api } from "@/lib/api";
import {
  Database,
  FileSpreadsheet,
  CheckCircle2,
  AlertOctagon,
  ShieldAlert,
  Code,
  Tag,
  UploadCloud,
} from "lucide-react";

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<any | null>(null);
  const [selectedCase, setSelectedCase] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDatasets() {
      try {
        const data = await api.getDatasets();
        setDatasets(data);
        if (data.length > 0) {
          const detail = await api.getDatasetDetail(data[0].id);
          setSelectedDataset(detail);
          if (detail.versions?.[0]?.cases?.length > 0) {
            setSelectedCase(detail.versions[0].cases[0]);
          }
        }
      } catch (err) {
        console.error("Failed to load datasets", err);
      } finally {
        setLoading(false);
      }
    }
    loadDatasets();
  }, []);

  const activeVersion = selectedDataset?.versions?.[0];
  const cases = activeVersion?.cases || [];

  return (
    <>
      <Header
        title="Golden Datasets & Benchmarks"
        subtitle="Version-controlled, immutable institutional test suites with ground truth criteria."
      />

      <main className="p-8 space-y-8">
        {selectedDataset && (
          <>
            {/* Header Info Banner */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center space-x-2">
                  <Database className="w-4 h-4 text-indigo-400" />
                  <h2 className="text-base font-bold text-slate-100">{selectedDataset.name}</h2>
                </div>
                <p className="text-xs text-slate-400 mt-1 max-w-2xl">{selectedDataset.description}</p>
                <div className="flex items-center space-x-4 mt-3 text-xs font-mono text-slate-400">
                  <span>Version: <strong className="text-slate-200">{activeVersion?.version_label}</strong></span>
                  <span>•</span>
                  <span>Cases: <strong className="text-slate-200">{activeVersion?.case_count}</strong></span>
                  <span>•</span>
                  <span>SHA: <strong className="text-slate-200">{(activeVersion?.content_hash || "").slice(0, 16)}...</strong></span>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <span className="bg-emerald-950/60 text-emerald-400 border border-emerald-800/40 px-3 py-1.5 rounded-lg text-xs font-medium">
                  Approved by {activeVersion?.approved_by}
                </span>
              </div>
            </div>

            {/* Test Case Grid & Inspector */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Cases List (6 cols) */}
              <div className="lg:col-span-6 bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="text-xs font-semibold text-slate-300">Curated Benchmark Cases</h3>

                <div className="space-y-2.5">
                  {cases.map((c: any) => {
                    const isSelected = selectedCase?.id === c.id;
                    const isBlocking = c.severity === "blocking";
                    return (
                      <div
                        key={c.id}
                        onClick={() => setSelectedCase(c)}
                        className={`p-3.5 rounded-lg border cursor-pointer transition-colors text-xs ${
                          isSelected
                            ? "bg-indigo-950/30 border-indigo-500/50"
                            : "bg-slate-950 border-slate-800 hover:bg-slate-900/40"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-xs font-semibold text-slate-200 capitalize">
                            {c.category.replace("_", " ")}
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase font-semibold ${
                              isBlocking
                                ? "bg-rose-950/60 text-rose-400 border border-rose-800/40"
                                : "bg-amber-950/60 text-amber-400 border border-amber-800/40"
                            }`}
                          >
                            {c.severity}
                          </span>
                        </div>

                        <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">{c.notes}</p>

                        <div className="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                          <span>Must mention: {c.expected_criteria?.must_mention?.join(", ") || "None"}</span>
                          <span>Hash: {(c.case_hash || "").slice(0, 10)}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Case Payload Inspector (6 cols) */}
              <div className="lg:col-span-6 bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="text-xs font-semibold text-slate-300">Case Input & Covenant Assertions</h3>

                {selectedCase ? (
                  <div className="space-y-4">
                    <div className="bg-slate-950 border border-slate-800 rounded-lg p-3">
                      <span className="text-[10px] text-slate-500 font-mono uppercase block mb-1">
                        Input Financials Payload
                      </span>
                      <pre className="text-xs text-slate-200 font-mono overflow-x-auto">
                        {JSON.stringify(selectedCase.input_payload, null, 2)}
                      </pre>
                    </div>

                    <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 space-y-2">
                      <span className="text-[10px] text-slate-500 font-mono uppercase block mb-1">
                        Deterministic Assertion Criteria
                      </span>
                      <div className="text-xs space-y-1">
                        <div>
                          <strong className="text-slate-300">Mandatory Terms (must_mention): </strong>
                          <span className="text-emerald-400 font-mono">
                            {selectedCase.expected_criteria?.must_mention?.join(", ") || "None"}
                          </span>
                        </div>
                        <div>
                          <strong className="text-slate-300">Prohibited Terms (must_not): </strong>
                          <span className="text-rose-400 font-mono">
                            {selectedCase.expected_criteria?.must_not?.join(", ") || "None"}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-8 text-center text-xs text-slate-500">
                    Select a test case to view payload and criteria.
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </main>
    </>
  );
}

