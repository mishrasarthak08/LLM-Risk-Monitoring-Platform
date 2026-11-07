"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  Activity,
  GitCompare,
  Waves,
  Scale,
  FileText,
  Database,
  Lock,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Code2,
  Terminal,
  Cpu,
  Server,
  Layers,
  ChevronRight,
  ExternalLink,
  Sliders,
  Copy,
  Check,
  Eye,
  FileCode2,
} from "lucide-react";

export default function MarketingPage() {
  const [activeTab, setActiveTab] = useState<"trace" | "regression" | "drift" | "audit">("trace");
  const [copiedCli, setCopiedCli] = useState(false);

  const handleCopyCli = () => {
    navigator.clipboard.writeText("make ci-regression");
    setCopiedCli(true);
    setTimeout(() => setCopiedCli(false), 2000);
  };

  return (
    <div className="bg-slate-950 text-slate-100 min-h-screen flex flex-col selection:bg-indigo-500/30 selection:text-indigo-200">
      {/* 1. Global Navigation Bar */}
      <nav className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-6 lg:px-12 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/" className="flex items-center space-x-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold tracking-tight text-white text-base">VERITAS AI</span>
              <span className="hidden sm:inline-block ml-2 text-[10px] text-indigo-400 font-mono uppercase bg-indigo-950/60 border border-indigo-800/40 px-1.5 py-0.5 rounded">
                SR 11-7 COMPLIANT
              </span>
            </div>
          </Link>

          <div className="hidden md:flex items-center space-x-6 text-sm text-slate-400">
            <a href="#capabilities" className="hover:text-slate-100 transition-colors">Capabilities</a>
            <a href="#problem-solution" className="hover:text-slate-100 transition-colors">The Problem</a>
            <a href="#how-it-works" className="hover:text-slate-100 transition-colors">How It Works</a>
            <a href="#architecture" className="hover:text-slate-100 transition-colors">Architecture</a>
            <a href="#security" className="hover:text-slate-100 transition-colors">Trust & Security</a>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            href="/login"
            className="text-xs text-slate-300 hover:text-white px-3 py-2 rounded-lg transition-colors font-medium"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="inline-flex items-center space-x-2 text-xs font-semibold bg-gradient-to-r from-indigo-500 to-cyan-500 hover:from-indigo-600 hover:to-cyan-600 text-white px-4 py-2 rounded-lg shadow-lg shadow-indigo-500/25 transition-all hover:shadow-indigo-500/40"
          >
            <span>Get Started</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </nav>

      {/* 2. Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 lg:pt-24 lg:pb-32 px-6 lg:px-12 border-b border-slate-900">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(99,102,241,0.15),rgba(255,255,255,0))]" />
        
        <div className="max-w-5xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center space-x-2 bg-slate-900/90 border border-indigo-500/30 px-3.5 py-1.5 rounded-full text-xs font-medium text-indigo-300 mb-8 backdrop-blur shadow-sm">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span>Federal Reserve SR 11-7 & OCC 2011-12 Model Risk Standard</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.12]">
            The Defense-Grade Reliability Platform for{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-cyan-300 to-indigo-200">
              Enterprise Generative AI
            </span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed font-normal">
            Detect silent prompt regressions before release, monitor production distribution drift in real time, and enforce regulatory compliance with cryptographic audit hash-chains and paired Wilcoxon statistical gates.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/register"
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3.5 rounded-xl shadow-xl shadow-indigo-600/30 transition-all hover:scale-[1.02]"
            >
              <span>Start Building Free</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/dashboard"
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 text-sm font-medium bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700/80 px-6 py-3.5 rounded-xl transition-all hover:border-slate-600"
            >
              <Eye className="w-4 h-4 text-cyan-400" />
              <span>Explore Live Console</span>
            </Link>

            <button
              onClick={handleCopyCli}
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 text-xs font-mono bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800 px-4 py-3.5 rounded-xl transition-colors group"
            >
              <Terminal className="w-4 h-4 text-indigo-400" />
              <span>make ci-regression</span>
              {copiedCli ? (
                <Check className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <Copy className="w-3.5 h-3.5 text-slate-600 group-hover:text-slate-400" />
              )}
            </button>
          </div>

          {/* Social Proof & Metrics Bar */}
          <div className="mt-14 pt-10 border-t border-slate-900 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div>
              <span className="block text-2xl lg:text-3xl font-extrabold text-white tracking-tight">100%</span>
              <span className="text-xs text-slate-400 mt-1 block">Deterministic Auditability</span>
            </div>
            <div>
              <span className="block text-2xl lg:text-3xl font-extrabold text-indigo-400 tracking-tight">p &lt; 0.05</span>
              <span className="text-xs text-slate-400 mt-1 block">Wilcoxon Parity Enforcement</span>
            </div>
            <div>
              <span className="block text-2xl lg:text-3xl font-extrabold text-cyan-400 tracking-tight">SHA-256</span>
              <span className="text-xs text-slate-400 mt-1 block">Cryptographic Hash Chaining</span>
            </div>
            <div>
              <span className="block text-2xl lg:text-3xl font-extrabold text-emerald-400 tracking-tight">SR 11-7</span>
              <span className="text-xs text-slate-400 mt-1 block">OCC 2011-12 Alignment</span>
            </div>
          </div>
        </div>

        {/* 3. Live Product Interface Showcase */}
        <div className="max-w-6xl mx-auto mt-14 relative z-10">
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden backdrop-blur">
            {/* Window Topbar */}
            <div className="px-5 py-3.5 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between flex-wrap gap-3">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                <span className="text-xs font-mono text-slate-400 ml-2">VERITAS AI — Live Telemetry Engine</span>
              </div>

              {/* Module Switcher Tabs */}
              <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs">
                <button
                  onClick={() => setActiveTab("trace")}
                  className={`px-3 py-1 rounded-md font-medium transition-all ${
                    activeTab === "trace"
                      ? "bg-indigo-600 text-white shadow"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  Trace Explorer
                </button>
                <button
                  onClick={() => setActiveTab("regression")}
                  className={`px-3 py-1 rounded-md font-medium transition-all ${
                    activeTab === "regression"
                      ? "bg-indigo-600 text-white shadow"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  CI Regression Gate
                </button>
                <button
                  onClick={() => setActiveTab("drift")}
                  className={`px-3 py-1 rounded-md font-medium transition-all ${
                    activeTab === "drift"
                      ? "bg-indigo-600 text-white shadow"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  Drift Monitor
                </button>
                <button
                  onClick={() => setActiveTab("audit")}
                  className={`px-3 py-1 rounded-md font-medium transition-all ${
                    activeTab === "audit"
                      ? "bg-indigo-600 text-white shadow"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  Audit Ledger
                </button>
              </div>
            </div>

            {/* Interactive Preview Content */}
            <div className="p-6 lg:p-8 font-sans">
              {activeTab === "trace" && (
                <div className="space-y-6">
                  <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-mono text-indigo-400">TRC-4ef98412</span>
                        <span className="text-xs bg-emerald-950/60 border border-emerald-800/40 text-emerald-400 px-2 py-0.5 rounded font-mono">
                          STATUS: 200 OK
                        </span>
                        <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">
                          credit_memo_v1
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1">
                        Commercial Loan Package Underwriting • Monotonic Clock: 750ms • Gemini 2.5 Flash
                      </p>
                    </div>
                    <div className="flex items-center space-x-6 text-xs font-mono">
                      <div>
                        <span className="text-slate-500 block">TOTAL TOKENS</span>
                        <span className="text-slate-200 font-semibold">240 tok (150 in / 90 out)</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">ESTIMATED COST</span>
                        <span className="text-emerald-400 font-semibold">$0.000038 USD</span>
                      </div>
                    </div>
                  </div>

                  {/* Redacted Payload vs Output */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
                          <Lock className="w-3.5 h-3.5 text-indigo-400" />
                          <span>Sanitized Input Payload</span>
                        </span>
                        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-1.5 py-0.5 rounded">
                          PII REDACTED
                        </span>
                      </div>
                      <pre className="text-xs font-mono text-slate-300 bg-slate-900/60 p-3 rounded-lg overflow-x-auto">
{`{
  "borrower": "Precision Machining Corp",
  "requested_amount": 1250000,
  "debt_service": 80000,
  "ssn": "[REDACTED_SSN]",
  "guarantor_fico": 745
}`}
                      </pre>
                    </div>

                    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                          <span>Generated Credit Memorandum</span>
                        </span>
                        <span className="text-[10px] font-mono text-indigo-400 bg-indigo-950/40 border border-indigo-800/40 px-1.5 py-0.5 rounded">
                          EVAL: 100/100
                        </span>
                      </div>
                      <div className="text-xs text-slate-300 bg-slate-900/60 p-3 rounded-lg leading-relaxed font-sans">
                        "Recommendation: APPROVE loan request of $1,250,000. Debt Service Coverage Ratio (DSCR) calculated at 1.45x, satisfying policy minimum of 1.25x. All required covenants, including personal guarantee and annual audited financials, are enforced."
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "regression" && (
                <div className="space-y-6">
                  <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-semibold text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2 py-0.5 rounded font-mono">
                          CI GATE: ALLOW
                        </span>
                        <span className="text-xs text-slate-300 font-mono">
                          credit_memo_v1.yaml (Baseline) vs candidate_v2.yaml (Candidate)
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1">
                        Paired Non-Parametric Wilcoxon Signed-Rank Evaluation across 5 Golden Benchmark Cases
                      </p>
                    </div>
                    <div className="flex items-center space-x-6 text-xs font-mono">
                      <div>
                        <span className="text-slate-500 block">WILCOXON P-VALUE</span>
                        <span className="text-indigo-400 font-semibold">p = 1.0000 (No Deterioration)</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">CLIFF'S DELTA</span>
                        <span className="text-slate-300 font-semibold">δ = 0.00 (Zero Effect Size)</span>
                      </div>
                    </div>
                  </div>

                  <div className="overflow-x-auto border border-slate-800 rounded-xl">
                    <table className="w-full text-left text-xs font-sans">
                      <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800 font-mono text-[11px]">
                        <tr>
                          <th className="py-2.5 px-4">Case ID</th>
                          <th className="py-2.5 px-4">Category</th>
                          <th className="py-2.5 px-4">Baseline Score</th>
                          <th className="py-2.5 px-4">Candidate Score</th>
                          <th className="py-2.5 px-4">Delta</th>
                          <th className="py-2.5 px-4">Gate Decision</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
                        <tr>
                          <td className="py-2.5 px-4 text-indigo-400">CASE #1</td>
                          <td className="py-2.5 px-4 font-sans text-slate-400">Happy path commercial loan</td>
                          <td className="py-2.5 px-4">1.00</td>
                          <td className="py-2.5 px-4">1.00</td>
                          <td className="py-2.5 px-4 text-slate-500">+0.00</td>
                          <td className="py-2.5 px-4 text-emerald-400">PASS</td>
                        </tr>
                        <tr>
                          <td className="py-2.5 px-4 text-indigo-400">CASE #2</td>
                          <td className="py-2.5 px-4 font-sans text-slate-400">Missing financial docs</td>
                          <td className="py-2.5 px-4">1.00</td>
                          <td className="py-2.5 px-4">1.00</td>
                          <td className="py-2.5 px-4 text-slate-500">+0.00</td>
                          <td className="py-2.5 px-4 text-emerald-400">PASS</td>
                        </tr>
                        <tr>
                          <td className="py-2.5 px-4 text-indigo-400">CASE #3</td>
                          <td className="py-2.5 px-4 font-sans text-slate-400">Seasonal revenue volatility</td>
                          <td className="py-2.5 px-4">1.00</td>
                          <td className="py-2.5 px-4">1.00</td>
                          <td className="py-2.5 px-4 text-slate-500">+0.00</td>
                          <td className="py-2.5 px-4 text-emerald-400">PASS</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {activeTab === "drift" && (
                <div className="space-y-6">
                  <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-semibold text-rose-400 bg-rose-950/60 border border-rose-800/40 px-2 py-0.5 rounded font-mono">
                          ACTIVE INCIDENT #DRF-001
                        </span>
                        <span className="text-xs text-slate-300 font-mono">refusal_rate Spike Detected</span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1">
                        Two-Proportion Z-Test confirmed statistically significant shift in model rejection behavior
                      </p>
                    </div>
                    <div className="flex items-center space-x-6 text-xs font-mono">
                      <div>
                        <span className="text-slate-500 block">Z-TEST P-VALUE</span>
                        <span className="text-rose-400 font-semibold">p = 0.0012 (CRITICAL)</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">POPULATION STABILITY (PSI)</span>
                        <span className="text-amber-400 font-semibold">PSI = 0.342 (&gt; 0.25 threshold)</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-slate-950 border border-rose-900/40 rounded-xl p-5">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-2">
                        <AlertTriangle className="w-4 h-4 text-rose-400" />
                        <h4 className="text-sm font-semibold text-slate-200">Incident Triage Desk Action Required</h4>
                      </div>
                      <span className="text-xs font-mono text-rose-400 bg-rose-950/80 border border-rose-800 px-2 py-0.5 rounded">
                        SEVERITY: CRITICAL
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                      Baseline refusal rate was 2.1% (N=1,200). Current 24h rolling production refusal rate is 9.8% (N=350). The two-sample test exceeds the critical decision boundary with effect size +7.7%.
                    </p>
                    <div className="mt-4 flex items-center space-x-3">
                      <Link
                        href="/drift"
                        className="text-xs font-medium bg-rose-600 hover:bg-rose-500 text-white px-3.5 py-1.5 rounded-lg transition-colors inline-flex items-center space-x-1"
                      >
                        <span>Open Incident Desk</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "audit" && (
                <div className="space-y-6">
                  <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-semibold text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2 py-0.5 rounded font-mono">
                          LEDGER: UNBROKEN / VALID
                        </span>
                        <span className="text-xs text-slate-300 font-mono">4 Total Chained Records</span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1">
                        Cryptographic SHA-256 State Hashing ensuring Non-Repudiation for Regulatory Examiners
                      </p>
                    </div>
                    <div className="text-xs font-mono">
                      <span className="text-slate-500 block">HEAD HASH</span>
                      <span className="text-emerald-400 font-semibold">5389003b6331590684...050b300</span>
                    </div>
                  </div>

                  <div className="space-y-2.5 font-mono text-xs">
                    <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-indigo-400">#004</span>
                        <span className="text-slate-200">CALIBRATION_COMPLETED</span>
                        <span className="text-slate-500 font-sans text-[11px]">Judge κ=0.825 calibrated</span>
                      </div>
                      <span className="text-slate-400 text-[11px]">2026-11-07 10:56:45</span>
                    </div>
                    <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-indigo-400">#003</span>
                        <span className="text-slate-200">REGRESSION_GATE_PASSED</span>
                        <span className="text-slate-500 font-sans text-[11px]">Wilcoxon p=1.000 ALLOW</span>
                      </div>
                      <span className="text-slate-400 text-[11px]">2026-11-07 10:56:45</span>
                    </div>
                    <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-indigo-400">#002</span>
                        <span className="text-slate-200">DATASET_VERSION_COMMITTED</span>
                        <span className="text-slate-500 font-sans text-[11px]">5 verified cases locked</span>
                      </div>
                      <span className="text-slate-400 text-[11px]">2026-11-07 10:56:45</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* 4. The Problem & Solution Section */}
      <section id="problem-solution" className="py-20 lg:py-28 px-6 lg:px-12 border-b border-slate-900 bg-slate-950">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-mono uppercase tracking-wider text-indigo-400 mb-2">The AI Governance Deficit</h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Why Mission-Critical AI Fails Without Defense-Grade Infrastructure
            </h3>
            <p className="mt-4 text-slate-400 text-sm sm:text-base leading-relaxed">
              Modern generative AI applications are deployed into sensitive business workflows, but traditional software APMs and logging stacks cannot detect semantic failure modes.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* The Problem */}
            <div className="bg-rose-950/20 border border-rose-900/30 rounded-2xl p-8 relative overflow-hidden">
              <div className="flex items-center space-x-3 text-rose-400 font-semibold mb-6">
                <AlertTriangle className="w-5 h-5" />
                <h4 className="text-lg text-white">The Status Quo: Unmonitored AI Risk</h4>
              </div>

              <ul className="space-y-4 text-sm text-slate-300">
                <li className="flex items-start space-x-3">
                  <span className="text-rose-400 font-bold">•</span>
                  <div>
                    <strong className="text-white">Silent Prompt Regressions:</strong> Minor prompt edits unintentionally violate regulatory covenants while continuing to return HTTP 200 OK.
                  </div>
                </li>
                <li className="flex items-start space-x-3">
                  <span className="text-rose-400 font-bold">•</span>
                  <div>
                    <strong className="text-white">Stochastic Production Drift:</strong> Upstream model provider updates shift output distributions, token lengths, or refusal rates without notification.
                  </div>
                </li>
                <li className="flex items-start space-x-3">
                  <span className="text-rose-400 font-bold">•</span>
                  <div>
                    <strong className="text-white">Uncalibrated LLM Judges:</strong> Automated evaluation models exhibit bias, lenient scoring, and lack of alignment with institutional subject matter experts.
                  </div>
                </li>
                <li className="flex items-start space-x-3">
                  <span className="text-rose-400 font-bold">•</span>
                  <div>
                    <strong className="text-white">Regulatory Examination Failure:</strong> Inability to prove to bank examiners (SR 11-7 / OCC 2011-12) what prompt, model, dataset, and evaluator generated a credit decision.
                  </div>
                </li>
              </ul>
            </div>

            {/* The Solution */}
            <div className="bg-indigo-950/20 border border-indigo-900/30 rounded-2xl p-8 relative overflow-hidden">
              <div className="flex items-center space-x-3 text-indigo-400 font-semibold mb-6">
                <CheckCircle2 className="w-5 h-5 text-indigo-400" />
                <h4 className="text-lg text-white">The VERITAS AI Architecture</h4>
              </div>

              <ul className="space-y-4 text-sm text-slate-300">
                <li className="flex items-start space-x-3">
                  <span className="text-indigo-400 font-bold">•</span>
                  <div>
                    <strong className="text-white">Wilcoxon CI/CD Gates:</strong> Non-parametric paired tests and Cliff's Delta effect sizes mathematically enforce quality parity before deployment.
                  </div>
                </li>
                <li className="flex items-start space-x-3">
                  <span className="text-indigo-400 font-bold">•</span>
                  <div>
                    <strong className="text-white">Continuous Statistical Surveillance:</strong> Quantile-binned Population Stability Index (PSI) and 2-sample tests flag real drift with zero noise.
                  </div>
                </li>
                <li className="flex items-start space-x-3">
                  <span className="text-indigo-400 font-bold">•</span>
                  <div>
                    <strong className="text-white">Calibrated Evaluator Framework:</strong> Cohen's Kappa ($\kappa \ge 0.70$) locks uncalibrated LLM judges from gating production releases until human consensus is proven.
                  </div>
                </li>
                <li className="flex items-start space-x-3">
                  <span className="text-indigo-400 font-bold">•</span>
                  <div>
                    <strong className="text-white">Cryptographic Audit Ledger:</strong> Tamper-evident SHA-256 hash chains guarantee non-repudiation and instant one-click SR 11-7 regulatory dossier generation.
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* 5. Core Platform Capabilities */}
      <section id="capabilities" className="py-20 lg:py-28 px-6 lg:px-12 border-b border-slate-900 bg-slate-950/60">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-mono uppercase tracking-wider text-indigo-400 mb-2">Engineered Modules</h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Modular Capabilities Designed for Model Risk & Engineering Teams
            </h3>
            <p className="mt-4 text-slate-400 text-sm sm:text-base leading-relaxed">
              Every capability is built upon rigorous statistical mathematics, content-addressed storage, and immutable ledgers.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Card 1 */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
                <Activity className="w-5 h-5" />
              </div>
              <h4 className="text-base font-semibold text-white">Observability & Distributed Traces</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Captures microsecond-resolution monotonic latencies, hierarchical parent-child spans, granular token consumption, token cost accounting, and regex PII redaction.
              </p>
            </div>

            {/* Card 2 */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-4">
                <FileCode2 className="w-5 h-5" />
              </div>
              <h4 className="text-base font-semibold text-white">Content-Addressed Prompt Registry</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Immutable SHA-256 hashed releases with variable schema validation, template parameter checking, and one-click rollback by re-publishing previous historical states.
              </p>
            </div>

            {/* Card 3 */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4">
                <GitCompare className="w-5 h-5" />
              </div>
              <h4 className="text-base font-semibold text-white">CI/CD Regression Gatekeeper</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Headless CLI integration enforcing Wilcoxon signed-rank paired tests, Cliff's Delta effect sizes, and sample sufficiency rules ($N \ge 10$) in GitHub Actions.
              </p>
            </div>

            {/* Card 4 */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4">
                <Waves className="w-5 h-5" />
              </div>
              <h4 className="text-base font-semibold text-white">Continuous Statistical Drift Engine</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Monitors quantile-binned Population Stability Index (PSI), two-sample Kolmogorov-Smirnov continuous distributions, and 2-proportion refusal rate shifts with incident desk triage.
              </p>
            </div>

            {/* Card 5 */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-4">
                <Scale className="w-5 h-5" />
              </div>
              <h4 className="text-base font-semibold text-white">Judge Calibration & Inter-Rater Reliability</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Computes unweighted and quadratic weighted Cohen's Kappa against double-blind human expert annotations, automatically locking uncalibrated judges from production gates.
              </p>
            </div>

            {/* Card 6 */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mb-4">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h4 className="text-base font-semibold text-white">Cryptographic Audit Ledger</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Merkle-style SHA-256 hash chaining across every model governance event, providing provable non-repudiation and instant SR 11-7 compliance export.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 6. How It Works: The 7-Step Reliability Lifecycle */}
      <section id="how-it-works" className="py-20 lg:py-28 px-6 lg:px-12 border-b border-slate-900 bg-slate-950">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-mono uppercase tracking-wider text-indigo-400 mb-2">The Operational Workflow</h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              The 7-Step Defense-Grade AI Reliability Lifecycle
            </h3>
            <p className="mt-4 text-slate-400 text-sm sm:text-base leading-relaxed">
              From developer commit to live production surveillance, VERITAS AI standardizes every phase of model risk governance.
            </p>
          </div>

          <div className="relative">
            <div className="hidden lg:block absolute left-1/2 top-0 bottom-0 w-0.5 bg-slate-800 -translate-x-1/2" />

            <div className="space-y-12">
              {/* Step 1 */}
              <div className="flex flex-col lg:flex-row items-center justify-between gap-8">
                <div className="lg:w-1/2 lg:text-right">
                  <span className="text-xs font-mono text-indigo-400">STEP 01</span>
                  <h4 className="text-lg font-bold text-white mt-1">Instrument Application</h4>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    Embed the lightweight Python `@veritas_trace` decorator or call the async REST ingestion API to capture prompts, model configs, and input/output payloads.
                  </p>
                </div>
                <div className="w-10 h-10 rounded-full bg-indigo-600 border-4 border-slate-950 flex items-center justify-center text-xs font-bold text-white z-10">
                  1
                </div>
                <div className="lg:w-1/2 bg-slate-900 border border-slate-800 p-4 rounded-xl text-xs font-mono text-slate-300">
                  <code>@veritas_trace(feature_name="credit_memo")</code>
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex flex-col lg:flex-row-reverse items-center justify-between gap-8">
                <div className="lg:w-1/2 lg:text-left">
                  <span className="text-xs font-mono text-indigo-400">STEP 02</span>
                  <h4 className="text-lg font-bold text-white mt-1">Observe & Redact PII</h4>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    Sanitize sensitive data (SSNs, account numbers, credentials) in-flight. Track monotonic latency, span hierarchies, and precise token pricing.
                  </p>
                </div>
                <div className="w-10 h-10 rounded-full bg-indigo-600 border-4 border-slate-950 flex items-center justify-center text-xs font-bold text-white z-10">
                  2
                </div>
                <div className="lg:w-1/2 bg-slate-900 border border-slate-800 p-4 rounded-xl text-xs font-mono text-slate-300">
                  <code>"ssn": "[REDACTED_SSN]", "cost_usd": 0.000038</code>
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex flex-col lg:flex-row items-center justify-between gap-8">
                <div className="lg:w-1/2 lg:text-right">
                  <span className="text-xs font-mono text-indigo-400">STEP 03</span>
                  <h4 className="text-lg font-bold text-white mt-1">Multi-Dimensional Evaluation</h4>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    Evaluate outputs against deterministic covenant rules and calibrated LLM-as-a-Judge rubrics with structured JSON reasoning.
                  </p>
                </div>
                <div className="w-10 h-10 rounded-full bg-indigo-600 border-4 border-slate-950 flex items-center justify-center text-xs font-bold text-white z-10">
                  3
                </div>
                <div className="lg:w-1/2 bg-slate-900 border border-slate-800 p-4 rounded-xl text-xs font-mono text-slate-300">
                  <code>rubrics: [factual_accuracy, policy_compliance]</code>
                </div>
              </div>

              {/* Step 4 */}
              <div className="flex flex-col lg:flex-row-reverse items-center justify-between gap-8">
                <div className="lg:w-1/2 lg:text-left">
                  <span className="text-xs font-mono text-indigo-400">STEP 04</span>
                  <h4 className="text-lg font-bold text-white mt-1">Detect Regressions in CI</h4>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    Run paired comparisons across immutable golden datasets. Wilcoxon signed-rank tests block merging degraded prompts.
                  </p>
                </div>
                <div className="w-10 h-10 rounded-full bg-indigo-600 border-4 border-slate-950 flex items-center justify-center text-xs font-bold text-white z-10">
                  4
                </div>
                <div className="lg:w-1/2 bg-slate-900 border border-slate-800 p-4 rounded-xl text-xs font-mono text-slate-300">
                  <code>python ci/veritas_ci.py --candidate v2.yaml</code>
                </div>
              </div>

              {/* Step 5 */}
              <div className="flex flex-col lg:flex-row items-center justify-between gap-8">
                <div className="lg:w-1/2 lg:text-right">
                  <span className="text-xs font-mono text-indigo-400">STEP 05</span>
                  <h4 className="text-lg font-bold text-white mt-1">Surveil Production Drift</h4>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    Continuously measure Population Stability Index (PSI) and Kolmogorov-Smirnov distance on rolling production windows.
                  </p>
                </div>
                <div className="w-10 h-10 rounded-full bg-indigo-600 border-4 border-slate-950 flex items-center justify-center text-xs font-bold text-white z-10">
                  5
                </div>
                <div className="lg:w-1/2 bg-slate-900 border border-slate-800 p-4 rounded-xl text-xs font-mono text-slate-300">
                  <code>PSI = 0.342 &gt; 0.25 (Trigger Incident Desk)</code>
                </div>
              </div>

              {/* Step 6 */}
              <div className="flex flex-col lg:flex-row-reverse items-center justify-between gap-8">
                <div className="lg:w-1/2 lg:text-left">
                  <span className="text-xs font-mono text-indigo-400">STEP 06</span>
                  <h4 className="text-lg font-bold text-white mt-1">Investigate & Triage</h4>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    Engineers and risk officers investigate affected traces, categorize root causes, and record defensible remediation notes.
                  </p>
                </div>
                <div className="w-10 h-10 rounded-full bg-indigo-600 border-4 border-slate-950 flex items-center justify-center text-xs font-bold text-white z-10">
                  6
                </div>
                <div className="lg:w-1/2 bg-slate-900 border border-slate-800 p-4 rounded-xl text-xs font-mono text-slate-300">
                  <code>incident.status = "RESOLVED" (Root Cause: Policy Update)</code>
                </div>
              </div>

              {/* Step 7 */}
              <div className="flex flex-col lg:flex-row items-center justify-between gap-8">
                <div className="lg:w-1/2 lg:text-right">
                  <span className="text-xs font-mono text-indigo-400">STEP 07</span>
                  <h4 className="text-lg font-bold text-white mt-1">Generate Cryptographic Evidence</h4>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    Verify SHA-256 ledger integrity and generate formal regulatory compliance packages ready for OCC / Fed examiners.
                  </p>
                </div>
                <div className="w-10 h-10 rounded-full bg-emerald-500 border-4 border-slate-950 flex items-center justify-center text-xs font-bold text-white z-10">
                  7
                </div>
                <div className="lg:w-1/2 bg-slate-900 border border-slate-800 p-4 rounded-xl text-xs font-mono text-slate-300">
                  <code>GET /api/v1/reports/governance (SR 11-7 Approved)</code>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 7. Technical Credibility & Architecture */}
      <section id="architecture" className="py-20 lg:py-28 px-6 lg:px-12 border-b border-slate-900 bg-slate-950/60">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-mono uppercase tracking-wider text-indigo-400 mb-2">Technical Foundations</h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              A High-Performance, Modular Monolith
            </h3>
            <p className="mt-4 text-slate-400 text-sm sm:text-base leading-relaxed">
              No bloated microservices or fragile dependencies. A modern stack built for low overhead, strong typing, and deterministic reproducibility.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <Server className="w-8 h-8 text-indigo-400 mb-4" />
              <h4 className="text-base font-semibold text-white">Backend & Database</h4>
              <ul className="mt-3 space-y-2 text-xs text-slate-400 font-mono">
                <li>• Python 3.12+ & FastAPI</li>
                <li>• SQLAlchemy 2.0 (Strict Async Mappings)</li>
                <li>• PostgreSQL (28 Multi-Tenant Tables)</li>
                <li>• Alembic Migration Management</li>
                <li>• Redis Distributed Queue</li>
              </ul>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <Cpu className="w-8 h-8 text-cyan-400 mb-4" />
              <h4 className="text-base font-semibold text-white">AI & Statistical Rigor</h4>
              <ul className="mt-3 space-y-2 text-xs text-slate-400 font-mono">
                <li>• Google Gemini SDK (gemini-2.5-flash)</li>
                <li>• Deterministic Simulation Engine</li>
                <li>• SciPy Wilcoxon Signed-Rank Test</li>
                <li>• Cliff's Delta Effect Sizes</li>
                <li>• Cohen's Kappa Inter-Rater Reliability</li>
              </ul>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <Layers className="w-8 h-8 text-emerald-400 mb-4" />
              <h4 className="text-base font-semibold text-white">Frontend & Developer Experience</h4>
              <ul className="mt-3 space-y-2 text-xs text-slate-400 font-mono">
                <li>• Next.js 14 (App Router & Server Actions)</li>
                <li>• TypeScript Strict Mode</li>
                <li>• Tailwind CSS & Lucide Icons</li>
                <li>• Headless CI CLI Tools</li>
                <li>• Playwright End-to-End Verification</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* 8. Trust, Security & Regulatory Defensibility */}
      <section id="security" className="py-20 lg:py-28 px-6 lg:px-12 border-b border-slate-900 bg-slate-950">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-mono uppercase tracking-wider text-emerald-400 mb-2">Zero-Trust Architecture</h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Bank-Grade Security & Non-Repudiation
            </h3>
            <p className="mt-4 text-slate-400 text-sm sm:text-base leading-relaxed">
              Designed specifically to withstand scrutiny from internal model-risk audit teams and federal bank examiners.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-xl">
              <Lock className="w-6 h-6 text-indigo-400 mb-3" />
              <h4 className="text-sm font-semibold text-white">In-Flight PII Redaction</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Automated regex sanitization for SSNs, credit cards, and tokens before persistence to disk or DB.
              </p>
            </div>

            <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-xl">
              <ShieldCheck className="w-6 h-6 text-emerald-400 mb-3" />
              <h4 className="text-sm font-semibold text-white">Cryptographic Hash Chains</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Every prompt commit, gate decision, and drift event is linked via SHA-256 for mathematical non-repudiation.
              </p>
            </div>

            <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-xl">
              <Server className="w-6 h-6 text-cyan-400 mb-3" />
              <h4 className="text-sm font-semibold text-white">Air-Gapped Simulation</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Full deterministic local evaluation mode requiring zero external API keys for highly confidential networks.
              </p>
            </div>

            <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-xl">
              <FileText className="w-6 h-6 text-purple-400 mb-3" />
              <h4 className="text-sm font-semibold text-white">Defensible Audit Dossiers</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Export comprehensive compliance reports matching Federal Reserve SR 11-7 validation guidelines.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 9. Final Conversion Section */}
      <section className="py-20 lg:py-28 px-6 lg:px-12 bg-gradient-to-b from-slate-950 via-indigo-950/20 to-slate-950 text-center relative overflow-hidden">
        <div className="max-w-4xl mx-auto relative z-10">
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
            Ready to Enforce Defense-Grade Reliability on Your AI?
          </h2>
          <p className="mt-6 text-slate-300 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
            Experience how VERITAS AI provides mathematical certainty, prompt safety, and regulatory compliance for enterprise generative AI workflows.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 text-sm font-semibold bg-gradient-to-r from-indigo-500 to-cyan-500 hover:from-indigo-600 hover:to-cyan-600 text-white px-8 py-4 rounded-xl shadow-xl shadow-indigo-500/25 transition-all hover:scale-[1.02]"
            >
              <span>Launch Enterprise Console</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/traces"
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 text-sm font-medium bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 px-8 py-4 rounded-xl transition-all"
            >
              <span>Explore Live Telemetry</span>
            </Link>
          </div>
        </div>
      </section>

      {/* 10. Comprehensive Enterprise Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-14 px-6 lg:px-12 text-slate-400 text-xs">
        <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
          <div className="col-span-2">
            <div className="flex items-center space-x-2.5">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center">
                <ShieldCheck className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-white text-sm">VERITAS AI</span>
            </div>
            <p className="mt-3 text-slate-400 max-w-sm leading-relaxed text-xs">
              Enterprise LLM Reliability, Evaluation, Observability, and Model Risk Governance Infrastructure. Built to satisfy Federal Reserve SR 11-7 and OCC 2011-12 standards.
            </p>
            <div className="mt-4 flex items-center space-x-2 text-[11px] text-slate-500">
              <span>Platform Version 2.0.0</span>
              <span>•</span>
              <span className="text-emerald-400">Cryptographically Audited</span>
            </div>
          </div>

          <div>
            <h5 className="font-semibold text-slate-200 mb-3 text-xs uppercase tracking-wider font-mono">Platform</h5>
            <ul className="space-y-2">
              <li><Link href="/dashboard" className="hover:text-slate-200 transition-colors">Overview</Link></li>
              <li><Link href="/traces" className="hover:text-slate-200 transition-colors">Trace Explorer</Link></li>
              <li><Link href="/prompts" className="hover:text-slate-200 transition-colors">Prompt Registry</Link></li>
              <li><Link href="/datasets" className="hover:text-slate-200 transition-colors">Golden Datasets</Link></li>
              <li><Link href="/regressions" className="hover:text-slate-200 transition-colors">Regression Gate</Link></li>
            </ul>
          </div>

          <div>
            <h5 className="font-semibold text-slate-200 mb-3 text-xs uppercase tracking-wider font-mono">Governance</h5>
            <ul className="space-y-2">
              <li><Link href="/drift" className="hover:text-slate-200 transition-colors">Drift Monitor</Link></li>
              <li><Link href="/calibration" className="hover:text-slate-200 transition-colors">Judge Calibration</Link></li>
              <li><Link href="/audit" className="hover:text-slate-200 transition-colors">Audit Ledger</Link></li>
              <li><Link href="/reports" className="hover:text-slate-200 transition-colors">SR 11-7 Dossier</Link></li>
            </ul>
          </div>

          <div>
            <h5 className="font-semibold text-slate-200 mb-3 text-xs uppercase tracking-wider font-mono">Developer</h5>
            <ul className="space-y-2">
              <li><a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer" className="hover:text-slate-200 transition-colors">OpenAPI Docs</a></li>
              <li><a href="http://127.0.0.1:8000/health" target="_blank" rel="noreferrer" className="hover:text-slate-200 transition-colors">System Health</a></li>
              <li><Link href="/dashboard" className="hover:text-slate-200 transition-colors">Enterprise Console</Link></li>
            </ul>
          </div>
        </div>

        <div className="max-w-6xl mx-auto pt-8 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between text-slate-500 text-[11px] gap-4">
          <p>© 2026 VERITAS AI Inc. Defense-grade generative AI governance infrastructure.</p>
          <div className="flex items-center space-x-6">
            <span>Non-Parametric Statistical Parity</span>
            <span>•</span>
            <span>SHA-256 Verifiable Non-Repudiation</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

