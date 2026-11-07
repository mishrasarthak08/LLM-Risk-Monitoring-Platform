"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  LayoutDashboard,
  Activity,
  FileCode2,
  Database,
  GitCompare,
  Waves,
  Scale,
  ShieldCheck,
  FileText,
  Globe,
  ArrowRight,
  Sparkles,
  FolderKanban,
  Key,
} from "lucide-react";

interface CommandItem {
  id: string;
  title: string;
  category: "Navigation" | "Quick Action";
  icon: React.ElementType;
  href: string;
  shortcut?: string;
}

const commands: CommandItem[] = [
  { id: "dash", title: "Overview Dashboard", category: "Navigation", icon: LayoutDashboard, href: "/dashboard" },
  { id: "projects", title: "Projects & Ingestion API Keys", category: "Navigation", icon: FolderKanban, href: "/projects" },
  { id: "evals", title: "Evaluation Studio & Rubrics", category: "Navigation", icon: Sparkles, href: "/evaluations" },
  { id: "traces", title: "Trace Explorer & PII Redactor", category: "Navigation", icon: Activity, href: "/traces" },
  { id: "prompts", title: "Prompt Version Registry", category: "Navigation", icon: FileCode2, href: "/prompts" },
  { id: "datasets", title: "Golden Benchmark Datasets", category: "Navigation", icon: Database, href: "/datasets" },
  { id: "reg", title: "CI Regression Gatekeeper", category: "Navigation", icon: GitCompare, href: "/regressions" },
  { id: "drift", title: "Continuous Drift Monitor", category: "Navigation", icon: Waves, href: "/drift" },
  { id: "cal", title: "LLM Judge Calibration", category: "Navigation", icon: Scale, href: "/calibration" },
  { id: "audit", title: "Cryptographic Audit Ledger", category: "Navigation", icon: ShieldCheck, href: "/audit" },
  { id: "rep", title: "SR 11-7 Governance Dossier", category: "Navigation", icon: FileText, href: "/reports" },
  { id: "mkt", title: "Public Marketing Website", category: "Quick Action", icon: Globe, href: "/" },
  { id: "onboard", title: "Launch Quickstart Onboarding Wizard", category: "Quick Action", icon: ArrowRight, href: "/onboarding" },
  { id: "audit-action", title: "Verify Audit Chain Integrity", category: "Quick Action", icon: Sparkles, href: "/audit" },
  { id: "export-action", title: "Download Compliance Package", category: "Quick Action", icon: FileText, href: "/reports" },
];

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const router = useRouter();

  const filtered = commands.filter((cmd) =>
    cmd.title.toLowerCase().includes(query.toLowerCase()) ||
    cmd.category.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (href: string) => {
    setOpen(false);
    setQuery("");
    router.push(href);
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
      if (!open) return;

      if (e.key === "Escape") {
        setOpen(false);
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => (filtered.length > 0 ? (prev + 1) % filtered.length : 0));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => (filtered.length > 0 ? (prev - 1 + filtered.length) % filtered.length : 0));
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (filtered[selectedIndex]) {
          handleSelect(filtered[selectedIndex].href);
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, filtered, selectedIndex]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="w-full max-w-xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input */}
        <div className="px-4 py-3.5 border-b border-slate-800 flex items-center space-x-3 bg-slate-950/60">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Type a command or jump to page... (Esc to close)"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            autoFocus
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
          />
          <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-mono text-slate-400 bg-slate-800 rounded border border-slate-700">
            ESC
          </kbd>
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? (
            <div className="py-8 text-center text-xs text-slate-500">
              No matching commands or pages found.
            </div>
          ) : (
            filtered.map((item, index) => {
              const Icon = item.icon;
              const isSelected = index === selectedIndex;
              return (
                <div
                  key={item.id}
                  onClick={() => handleSelect(item.href)}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={`px-3 py-2.5 rounded-xl cursor-pointer flex items-center justify-between text-xs transition-colors ${
                    isSelected ? "bg-indigo-600 text-white" : "text-slate-300 hover:bg-slate-800/60"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-4 h-4 ${isSelected ? "text-white" : "text-slate-400"}`} />
                    <span className="font-medium">{item.title}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`text-[10px] font-mono uppercase ${isSelected ? "text-indigo-200" : "text-slate-500"}`}>
                      {item.category}
                    </span>
                    <ArrowRight className={`w-3.5 h-3.5 opacity-60 ${isSelected ? "opacity-100" : ""}`} />
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-slate-800/80 bg-slate-950/60 flex items-center justify-between text-[11px] text-slate-500">
          <div className="flex items-center space-x-3">
            <span>↑↓ Navigate</span>
            <span>↵ Select</span>
          </div>
          <span className="font-mono text-[10px]">VERITAS AI v2.0</span>
        </div>
      </div>
    </div>
  );
}

