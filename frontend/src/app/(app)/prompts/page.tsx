"use client";

import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { api } from "@/lib/api";
import {
  FileCode2,
  GitBranch,
  GitCommit,
  GitCompare,
  CheckCircle2,
  Plus,
  ArrowRight,
  ShieldCheck,
  Eye,
  History,
} from "lucide-react";

export default function PromptsPage() {
  const [prompts, setPrompts] = useState<any[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<any | null>(null);
  const [diffResult, setDiffResult] = useState<any | null>(null);
  const [newTemplate, setNewTemplate] = useState<string>("");
  const [newSummary, setNewSummary] = useState<string>("");
  const [publishing, setPublishing] = useState<boolean>(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadPrompts() {
      try {
        const data = await api.getPrompts();
        setPrompts(data);
        if (data.length > 0) {
          const detail = await api.getPromptDetail(data[0].id);
          setSelectedPrompt(detail);
          if (detail.versions && detail.versions.length >= 2) {
            // Load diff between v1 and v2
            const d = await api.diffPrompts(detail.versions[0].id, detail.versions[1].id);
            setDiffResult(d);
          }
        }
      } catch (err) {
        console.error("Failed to load prompts", err);
      } finally {
        setLoading(false);
      }
    }
    loadPrompts();
  }, []);

  return (
    <>
      <Header
        title="Prompt Registry & Version Control"
        subtitle="Content-addressed immutable prompt templates, version diffs, and publication governance."
      />

      <main className="p-8 space-y-8">
        {/* Prompts list & details */}
        {selectedPrompt && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Prompt Info & Version History */}
            <div className="lg:col-span-5 bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-6">
              <div>
                <span className="text-[10px] text-indigo-400 font-mono uppercase tracking-wider font-semibold">
                  Prompt Entity
                </span>
                <h2 className="text-base font-bold text-slate-100 mt-1">{selectedPrompt.name}</h2>
                <p className="text-xs text-slate-400 mt-1">{selectedPrompt.description}</p>
              </div>

              {/* Version History List */}
              <div className="space-y-3">
                <h3 className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
                  <History className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Immutable Version History</span>
                </h3>

                <div className="space-y-2">
                  {selectedPrompt.versions?.map((ver: any) => (
                    <div
                      key={ver.id}
                      className={`p-3 rounded-lg border text-xs transition-colors ${
                        ver.is_published
                          ? "bg-indigo-950/20 border-indigo-500/40"
                          : "bg-slate-950 border-slate-800"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono font-bold text-slate-200">{ver.version_label}</span>
                          {ver.is_published && (
                            <span className="bg-emerald-950/60 text-emerald-400 border border-emerald-800/40 px-1.5 py-0.5 rounded text-[10px] font-semibold">
                              PUBLISHED ACTIVE
                            </span>
                          )}
                        </div>
                        <span className="text-[10px] text-slate-500 font-mono">
                          {new Date(ver.created_at).toLocaleDateString()}
                        </span>
                      </div>

                      <p className="text-[11px] text-slate-400 mt-1.5">{ver.change_summary}</p>

                      <div className="mt-2 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                        <span>SHA: {ver.content_hash.slice(0, 16)}...</span>
                        <span>By: {ver.author_email}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right: Active Template & Unified Diff Viewer */}
            <div className="lg:col-span-7 space-y-6">
              {/* Active Prompt Template View */}
              {(() => {
                const published = selectedPrompt.versions?.find((v: any) => v.is_published) || selectedPrompt.versions?.[0];
                return (
                  <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
                        <Eye className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Active Published Template ({published?.version_label || "v1.0.0"})</span>
                      </h3>
                      <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2 py-0.5 rounded">
                        PRODUCTION
                      </span>
                    </div>

                    <pre className="bg-slate-950 border border-slate-800 rounded-lg p-4 text-xs text-slate-200 font-mono whitespace-pre-wrap leading-relaxed overflow-x-auto">
                      {published?.prompt_template || "No template defined."}
                    </pre>
                  </div>
                );
              })()}

              {/* Version Comparison Diff Viewer */}
              {diffResult && (
                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <GitCompare className="w-4 h-4 text-cyan-400" />
                      <h3 className="text-xs font-semibold text-slate-200">
                        Version Diff ({diffResult.version_a.label} vs. {diffResult.version_b.label})
                      </h3>
                    </div>
                    <span className="text-[10px] font-mono text-rose-400 bg-rose-950/60 border border-rose-800/40 px-2 py-0.5 rounded">
                      CANDIDATE REGRESSION TEST
                    </span>
                  </div>

                  <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 font-mono text-xs overflow-x-auto max-h-[350px] space-y-0.5">
                    {diffResult.diff_text ? (
                      diffResult.diff_text.split("\n").map((line: string, i: number) => {
                        const isAdd = line.startsWith("+") && !line.startsWith("+++");
                        const isDel = line.startsWith("-") && !line.startsWith("---");
                        const isMeta = line.startsWith("@@") || line.startsWith("---") || line.startsWith("+++");
                        return (
                          <div
                            key={i}
                            className={`px-1 py-0.5 rounded text-[11px] font-mono ${
                              isAdd
                                ? "bg-emerald-950/40 text-emerald-400"
                                : isDel
                                ? "bg-rose-950/40 text-rose-400"
                                : isMeta
                                ? "text-cyan-400 font-semibold"
                                : "text-slate-400"
                            }`}
                          >
                            {line || " "}
                          </div>
                        );
                      })
                    ) : (
                      <div className="text-slate-500 italic p-2">Versions are identical. No textual diff detected.</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </>
  );
}
