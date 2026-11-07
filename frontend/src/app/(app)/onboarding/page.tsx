"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ShieldCheck,
  CheckCircle2,
  Copy,
  Check,
  ArrowRight,
  Terminal,
  Code2,
  Sparkles,
  RefreshCw,
  FolderPlus,
  Key,
  Layers,
  AlertCircle,
} from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

export default function OnboardingPage() {
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [projectName, setProjectName] = useState("AI Support & Risk Agent");
  const [projectSlug, setProjectSlug] = useState("ai-support-risk-agent");
  const [projectId, setProjectId] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [selectedSdk, setSelectedSdk] = useState<"python" | "typescript" | "curl">("python");
  const [copiedKey, setCopiedKey] = useState(false);
  const [copiedCode, setCopiedCode] = useState(false);
  const [verifiedTrace, setVerifiedTrace] = useState<any | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Step 1: Create Project
  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("veritas_token") : null;
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const res = await fetch(`${API_BASE_URL}/projects`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          name: projectName,
          slug: projectSlug || projectName.toLowerCase().replace(/[^a-z0-9]/g, "-"),
          description: "Production LLM Application monitored by VERITAS AI",
        }),
      });

      if (!res.ok) throw new Error("Failed to create project.");
      const proj = await res.json();
      setProjectId(proj.id);

      // Immediately mint initial API key for project
      const keyRes = await fetch(`${API_BASE_URL}/projects/${proj.id}/api-keys`, {
        method: "POST",
        headers,
        body: JSON.stringify({ name: "Primary Production Key" }),
      });
      if (!keyRes.ok) throw new Error("Failed to generate project API key.");
      const keyData = await keyRes.json();
      setApiKey(keyData.raw_key);

      setStep(2);
    } catch (err: any) {
      setError(err.message || "Failed to initialize project.");
    }
  };

  // Step 4: Send Test Ping & Verify Trace
  const handleSendTestPing = async () => {
    if (!projectId) return;
    setVerifying(true);
    setError(null);

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("veritas_token") : null;
      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const res = await fetch(`${API_BASE_URL}/projects/${projectId}/test-event`, {
        method: "POST",
        headers,
      });

      if (!res.ok) throw new Error("Test trace failed to register.");
      const trace = await res.json();
      setVerifiedTrace(trace);
      setStep(4);
    } catch (err: any) {
      setError(err.message || "Failed to verify connection.");
    } finally {
      setVerifying(false);
    }
  };

  const pythonSnippet = `from veritas import Veritas

client = Veritas(
    api_key="${apiKey || "vai_live_your_api_key_here"}",
    base_url="http://localhost:8000/api/v1"
)

# Instrument your production LLM call
with client.trace(name="${projectSlug || "my_feature"}") as trace:
    prompt_input = {"question": "What is our enterprise refund window?"}
    trace.log_input(prompt_input)

    # Call your model (OpenAI, Gemini, Anthropic, or internal model)
    response = "Enterprise contracts allow 30-day billing disputes."
    
    trace.log_output(response)
    trace.log_tokens(input_tokens=45, output_tokens=18)`;

  const tsSnippet = `import { Veritas } from "@veritas-ai/sdk";

const client = new Veritas({
  apiKey: "${apiKey || "vai_live_your_api_key_here"}",
  baseUrl: "http://localhost:8000/api/v1"
});

// Trace your AI agent workflow
await client.trace("${projectSlug || "my_feature"}", async ({ logInput, logOutput, logTokens }) => {
  logInput({ question: "Calculate debt service coverage ratio." });
  
  // Execute LLM call...
  const response = "Calculated DSCR is 1.45x satisfying policy covenant.";
  
  logOutput(response);
  logTokens(60, 22);
});`;

  const curlSnippet = `curl -X POST "http://localhost:8000/api/v1/traces/ingest" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: ${apiKey || "vai_live_your_api_key_here"}" \\
  -d '{
    "feature_name": "${projectSlug || "my_feature"}",
    "input_payload": {"query": "Test trace handshake"},
    "output_text": "Connection confirmed.",
    "input_tokens": 10,
    "output_tokens": 5,
    "latency_ms": 120,
    "status": "SUCCESS"
  }'`;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col p-6 lg:p-12">
      {/* Top Header */}
      <div className="max-w-4xl mx-auto w-full flex items-center justify-between pb-8 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight">VERITAS AI Quickstart</h1>
            <p className="text-xs text-slate-400">Connect your application and start observing in 5 minutes</p>
          </div>
        </div>

        <Link
          href="/dashboard"
          className="text-xs text-slate-400 hover:text-slate-200 transition-colors"
        >
          Skip to Console →
        </Link>
      </div>

      {/* Step Indicator */}
      <div className="max-w-4xl mx-auto w-full my-8">
        <div className="grid grid-cols-4 gap-3 text-center text-xs">
          <div className={`p-2.5 rounded-lg border font-medium ${step >= 1 ? "bg-indigo-950/40 border-indigo-500/50 text-indigo-300" : "bg-slate-900/40 border-slate-800 text-slate-500"}`}>
            1. Create Project
          </div>
          <div className={`p-2.5 rounded-lg border font-medium ${step >= 2 ? "bg-indigo-950/40 border-indigo-500/50 text-indigo-300" : "bg-slate-900/40 border-slate-800 text-slate-500"}`}>
            2. Mint API Key
          </div>
          <div className={`p-2.5 rounded-lg border font-medium ${step >= 3 ? "bg-indigo-950/40 border-indigo-500/50 text-indigo-300" : "bg-slate-900/40 border-slate-800 text-slate-500"}`}>
            3. Integrate SDK
          </div>
          <div className={`p-2.5 rounded-lg border font-medium ${step >= 4 ? "bg-emerald-950/40 border-emerald-500/50 text-emerald-300" : "bg-slate-900/40 border-slate-800 text-slate-500"}`}>
            4. Verify Telemetry
          </div>
        </div>
      </div>

      {/* Main Wizard Card */}
      <div className="max-w-4xl mx-auto w-full bg-slate-900/70 border border-slate-800 rounded-2xl p-8 shadow-2xl backdrop-blur">
        {error && (
          <div className="mb-6 p-3.5 bg-rose-950/60 border border-rose-800/80 rounded-xl flex items-center space-x-2.5 text-xs text-rose-300">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* STEP 1: Project Setup */}
        {step === 1 && (
          <form onSubmit={handleCreateProject} className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight flex items-center space-x-2">
                <FolderPlus className="w-5 h-5 text-indigo-400" />
                <span>Name Your AI Application Project</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                A project isolates your traces, prompts, evaluation rubrics, and regression test suites.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Project Display Name
                </label>
                <input
                  type="text"
                  required
                  value={projectName}
                  onChange={(e) => {
                    setProjectName(e.target.value);
                    setProjectSlug(e.target.value.toLowerCase().replace(/[^a-z0-9]/g, "-"));
                  }}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-sans"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Project Identifier (Slug)
                </label>
                <input
                  type="text"
                  required
                  value={projectSlug}
                  onChange={(e) => setProjectSlug(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-300 font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <button
              type="submit"
              className="inline-flex items-center space-x-2 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-xl shadow-lg shadow-indigo-600/30 transition-all"
            >
              <span>Generate API Key & Continue</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}

        {/* STEP 2: API Key Display */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight flex items-center space-x-2">
                <Key className="w-5 h-5 text-cyan-400" />
                <span>Your Production Ingestion API Key</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Use this secret key to authenticate your SDK or HTTP ingestion requests.
              </p>
            </div>

            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
              <span className="font-mono text-xs text-cyan-400 break-all select-all">
                {apiKey}
              </span>
              <button
                onClick={() => {
                  if (apiKey) navigator.clipboard.writeText(apiKey);
                  setCopiedKey(true);
                  setTimeout(() => setCopiedKey(false), 2000);
                }}
                className="ml-4 p-2 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-lg border border-slate-800 transition-colors shrink-0"
              >
                {copiedKey ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>

            <div className="p-3 bg-amber-950/30 border border-amber-800/40 rounded-xl text-xs text-amber-300 flex items-start space-x-2">
              <span className="font-bold">⚠️ Warning:</span>
              <span>This secret key will not be shown again. Store it in your secrets manager or <code>.env</code> file.</span>
            </div>

            <button
              onClick={() => setStep(3)}
              className="inline-flex items-center space-x-2 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-xl shadow-lg shadow-indigo-600/30 transition-all"
            >
              <span>View Code Examples</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* STEP 3: Integration Code Snippets */}
        {step === 3 && (
          <div className="space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold text-white tracking-tight flex items-center space-x-2">
                  <Code2 className="w-5 h-5 text-indigo-400" />
                  <span>Connect Your Application</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Choose your preferred language SDK to instrument your LLM functions.
                </p>
              </div>

              {/* Language Switcher */}
              <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
                <button
                  onClick={() => setSelectedSdk("python")}
                  className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                    selectedSdk === "python" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  Python SDK
                </button>
                <button
                  onClick={() => setSelectedSdk("typescript")}
                  className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                    selectedSdk === "typescript" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  TypeScript / Node
                </button>
                <button
                  onClick={() => setSelectedSdk("curl")}
                  className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                    selectedSdk === "curl" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  cURL / REST API
                </button>
              </div>
            </div>

            {/* Code Box */}
            <div className="relative">
              <pre className="bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-200 overflow-x-auto leading-relaxed">
                {selectedSdk === "python" && pythonSnippet}
                {selectedSdk === "typescript" && tsSnippet}
                {selectedSdk === "curl" && curlSnippet}
              </pre>
              <button
                onClick={() => {
                  const textToCopy =
                    selectedSdk === "python"
                      ? pythonSnippet
                      : selectedSdk === "typescript"
                      ? tsSnippet
                      : curlSnippet;
                  navigator.clipboard.writeText(textToCopy);
                  setCopiedCode(true);
                  setTimeout(() => setCopiedCode(false), 2000);
                }}
                className="absolute right-3 top-3 p-1.5 bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded-lg border border-slate-800 text-xs flex items-center space-x-1"
              >
                {copiedCode ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span className="text-[10px]">{copiedCode ? "Copied" : "Copy"}</span>
              </button>
            </div>

            <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
              <span className="text-xs text-slate-400">
                Ready to test? Send a verification handshake ping to confirm backend ingestion.
              </span>
              <button
                onClick={handleSendTestPing}
                disabled={verifying}
                className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 text-xs font-semibold bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white px-5 py-2.5 rounded-xl shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${verifying ? "animate-spin" : ""}`} />
                <span>{verifying ? "Verifying Ingestion..." : "Send Test Ping & Verify"}</span>
              </button>
            </div>
          </div>
        )}

        {/* STEP 4: Success State */}
        {step === 4 && (
          <div className="space-y-6 text-center py-4">
            <div className="w-14 h-14 rounded-2xl bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 flex items-center justify-center mx-auto shadow-xl shadow-emerald-500/20 animate-in zoom-in-75 duration-200">
              <CheckCircle2 className="w-8 h-8" />
            </div>

            <div>
              <h2 className="text-xl font-bold text-white tracking-tight">
                Handshake Successful! First Trace Received
              </h2>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                Your project <strong>{projectName}</strong> is actively receiving and processing traces with PII redaction and latency attribution.
              </p>
            </div>

            {verifiedTrace && (
              <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 max-w-lg mx-auto text-left font-mono text-xs space-y-2">
                <div className="flex items-center justify-between text-slate-400">
                  <span>TRACE ID:</span>
                  <span className="text-indigo-400">{verifiedTrace.id}</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>STATUS:</span>
                  <span className="text-emerald-400 font-bold">{verifiedTrace.status}</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>LATENCY:</span>
                  <span className="text-slate-200">{verifiedTrace.latency_ms} ms</span>
                </div>
              </div>
            )}

            <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/traces"
                className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl shadow-lg shadow-indigo-600/30 transition-all"
              >
                <span>Open Trace Explorer</span>
                <ArrowRight className="w-4 h-4" />
              </Link>

              <Link
                href="/dashboard"
                className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 text-xs font-medium bg-slate-950 hover:bg-slate-900 border border-slate-800 text-slate-300 px-6 py-3 rounded-xl transition-colors"
              >
                <span>Go to Dashboard</span>
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
