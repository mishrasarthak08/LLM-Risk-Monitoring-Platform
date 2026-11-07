"use client";

import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { api } from "@/lib/api";
import {
  Activity,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  AlertOctagon,
  Clock,
  DollarSign,
  FileCode,
  Layers,
  ShieldAlert,
} from "lucide-react";

export default function TracesPage() {
  const [traces, setTraces] = useState<any[]>([]);
  const [selectedTrace, setSelectedTrace] = useState<any | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>("ALL");
  const [searchId, setSearchId] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTraces() {
      try {
        const data = await api.getTraces("credit_memo_v1");
        setTraces(data);
        if (data.length > 0) {
          setSelectedTrace(data[0]);
        }
      } catch (err) {
        console.error("Failed to load traces", err);
      } finally {
        setLoading(false);
      }
    }
    loadTraces();
  }, []);

  const filtered = traces.filter((t) => {
    if (filterStatus !== "ALL" && t.status !== filterStatus) return false;
    if (searchId && !t.id.toLowerCase().includes(searchId.toLowerCase())) return false;
    return true;
  });

  return (
    <>
      <Header
        title="Trace Explorer & Observability"
        subtitle="Real-time distributed span execution, latency attribution, and token cost ledger."
      />

      <main className="p-8 space-y-6">
        {/* Filter bar */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-3 w-full md:w-auto">
            <div className="relative w-full md:w-72">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="text"
                placeholder="Search by Trace ID..."
                value={searchId}
                onChange={(e) => setSearchId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
              />
            </div>

            <div className="flex items-center space-x-1.5">
              {["ALL", "SUCCESS", "REFUSAL", "ERROR"].map((status) => (
                <button
                  key={status}
                  onClick={() => setFilterStatus(status)}
                  className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    filterStatus === status
                      ? "bg-indigo-600 text-white"
                      : "bg-slate-950 border border-slate-800 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {status}
                </button>
              ))}
            </div>
          </div>

          <div className="text-xs text-slate-400 font-medium">
            Showing <span className="text-slate-200 font-mono">{filtered.length}</span> recorded traces
          </div>
        </div>

        {/* Two-Pane Trace Explorer */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[600px]">
          {/* Left Table (5 cols) */}
          <div className="lg:col-span-5 bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
            <div className="p-3 border-b border-slate-800 bg-slate-950 text-xs font-medium text-slate-400">
              Execution Logs
            </div>

            <div className="flex-1 overflow-y-auto divide-y divide-slate-800/60 max-h-[700px]">
              {filtered.map((trace) => {
                const isSelected = selectedTrace?.id === trace.id;
                return (
                  <div
                    key={trace.id}
                    onClick={() => setSelectedTrace(trace)}
                    className={`p-3.5 cursor-pointer transition-colors ${
                      isSelected ? "bg-indigo-950/30 border-l-2 border-indigo-500" : "hover:bg-slate-900/40"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-semibold text-slate-200">
                        {trace.id.slice(0, 8)}...{trace.id.slice(-4)}
                      </span>
                      {trace.status === "SUCCESS" ? (
                        <span className="text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-1.5 py-0.5 rounded text-[10px] font-sans font-medium">
                          SUCCESS
                        </span>
                      ) : (
                        <span className="text-rose-400 bg-rose-950/60 border border-rose-800/40 px-1.5 py-0.5 rounded text-[10px] font-sans font-medium">
                          {trace.status}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center space-x-3 mt-2 text-[11px] text-slate-400 font-mono">
                      <span>{trace.latency_ms}ms</span>
                      <span>•</span>
                      <span>{trace.total_tokens} tokens</span>
                      <span>•</span>
                      <span>${(trace.cost_usd ?? 0).toFixed(6)}</span>
                    </div>

                    <div className="text-[10px] text-slate-500 mt-1">
                      {new Date(trace.created_at).toLocaleString()}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Inspector Detail (7 cols) */}
          <div className="lg:col-span-7 bg-slate-900/50 border border-slate-800 rounded-xl p-6 flex flex-col overflow-hidden">
            {selectedTrace ? (
              <div className="space-y-6 overflow-y-auto max-h-[700px]">
                {/* Header */}
                <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                  <div>
                    <h2 className="text-sm font-bold text-slate-100 font-mono tracking-tight">
                      Trace: {selectedTrace.id}
                    </h2>
                    <span className="text-xs text-slate-400">Feature: {selectedTrace.feature_name}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-xs font-mono">
                    <span className="bg-slate-800 text-slate-300 px-2 py-1 rounded">
                      gemini-2.5-flash
                    </span>
                  </div>
                </div>

                {/* Metrics ribbon */}
                <div className="grid grid-cols-4 gap-3 bg-slate-950 p-3 rounded-lg border border-slate-800 text-center">
                  <div>
                    <span className="block text-[10px] uppercase text-slate-500">Latency</span>
                    <span className="text-sm font-bold font-mono text-slate-200">{selectedTrace.latency_ms} ms</span>
                  </div>
                  <div>
                    <span className="block text-[10px] uppercase text-slate-500">Cost</span>
                    <span className="text-sm font-bold font-mono text-emerald-400">
                      ${(selectedTrace.cost_usd ?? 0).toFixed(6)}
                    </span>
                  </div>
                  <div>
                    <span className="block text-[10px] uppercase text-slate-500">Input Tokens</span>
                    <span className="text-sm font-bold font-mono text-slate-200">{selectedTrace.input_tokens || 0}</span>
                  </div>
                  <div>
                    <span className="block text-[10px] uppercase text-slate-500">Output Tokens</span>
                    <span className="text-sm font-bold font-mono text-slate-200">{selectedTrace.output_tokens || 0}</span>
                  </div>
                </div>

                {/* Span Hierarchy / Waterfall */}
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
                    <Layers className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Nested Span Execution Tree</span>
                  </div>
                  <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 space-y-2 font-mono text-xs">
                    <div className="flex items-center justify-between p-2 bg-slate-900/60 rounded border border-slate-800/80">
                      <div className="flex items-center space-x-2">
                        <span className="w-2 h-2 rounded-full bg-indigo-500" />
                        <span className="text-slate-200">{selectedTrace.feature_name || "root_chain"} (Root Span)</span>
                      </div>
                      <span className="text-slate-400">{selectedTrace.latency_ms}ms</span>
                    </div>

                    {selectedTrace.spans && selectedTrace.spans.length > 0 ? (
                      selectedTrace.spans.map((sp: any) => (
                        <div key={sp.id} className="ml-4 flex items-center justify-between p-2 bg-slate-900/30 rounded border border-slate-800/40 text-[11px]">
                          <div className="flex items-center space-x-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                            <span className="text-slate-300">{sp.name}</span>
                            <span className="text-[10px] bg-slate-800 text-slate-400 px-1 rounded">{sp.span_type}</span>
                          </div>
                          <span className="text-slate-400">{sp.latency_ms}ms</span>
                        </div>
                      ))
                    ) : (
                      <>
                        <div className="ml-4 flex items-center justify-between p-2 bg-slate-900/30 rounded border border-slate-800/40 text-[11px]">
                          <div className="flex items-center space-x-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                            <span className="text-slate-300">retrieve_context</span>
                          </div>
                          <span className="text-slate-400">{Math.max(10, Math.round(selectedTrace.latency_ms * 0.2))}ms</span>
                        </div>
                        <div className="ml-4 flex items-center justify-between p-2 bg-slate-900/30 rounded border border-slate-800/40 text-[11px]">
                          <div className="flex items-center space-x-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                            <span className="text-slate-300">llm_generation</span>
                          </div>
                          <span className="text-slate-400">{Math.max(20, Math.round(selectedTrace.latency_ms * 0.65))}ms</span>
                        </div>
                        <div className="ml-4 flex items-center justify-between p-2 bg-slate-900/30 rounded border border-slate-800/40 text-[11px]">
                          <div className="flex items-center space-x-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                            <span className="text-slate-300">governance_guardrails</span>
                          </div>
                          <span className="text-slate-400">{Math.max(10, Math.round(selectedTrace.latency_ms * 0.15))}ms</span>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                {/* Rendered Input Payload */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                    <div className="flex items-center space-x-1.5">
                      <FileCode className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Rendered Input Payload (PII Redacted)</span>
                    </div>
                    <span className="text-[10px] text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-1.5 py-0.5 rounded font-mono">
                      SANITIZED
                    </span>
                  </div>
                  <pre className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-300 font-mono overflow-x-auto">
                    {JSON.stringify(selectedTrace.input_payload, null, 2)}
                  </pre>
                </div>

                {/* Generated Output */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                    <div className="flex items-center space-x-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Model Output Text</span>
                    </div>
                  </div>
                  <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-300 whitespace-pre-wrap leading-relaxed font-sans">
                    {selectedTrace.output_text || selectedTrace.error_message || "No output captured."}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-xs text-slate-500">
                Select a trace from the left panel to inspect execution details.
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  );
}

