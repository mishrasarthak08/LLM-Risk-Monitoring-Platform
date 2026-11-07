"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Activity,
  FileCode2,
  Database,
  GitCompare,
  Waves,
  Scale,
  ShieldCheck,
  FileText,
  Settings,
  Building2,
  ChevronRight,
  Globe,
  Sparkles,
  Key,
  FolderKanban,
} from "lucide-react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  badge?: string;
}

const navItems: NavItem[] = [
  { label: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { label: "Projects & Keys", href: "/projects", icon: FolderKanban },
  { label: "Trace Explorer", href: "/traces", icon: Activity },
  { label: "Evaluation Studio", href: "/evaluations", icon: Sparkles },
  { label: "Prompt Registry", href: "/prompts", icon: FileCode2 },
  { label: "Golden Datasets", href: "/datasets", icon: Database },
  { label: "Regression CI Gate", href: "/regressions", icon: GitCompare },
  { label: "Drift Monitor", href: "/drift", icon: Waves, badge: "1 Alert" },
  { label: "Judge Calibration", href: "/calibration", icon: Scale },
  { label: "Cryptographic Audit", href: "/audit", icon: ShieldCheck },
  { label: "Governance Dossier", href: "/reports", icon: FileText },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col h-screen fixed left-0 top-0 z-40 select-none">
      {/* Brand Header */}
      <div className="h-16 px-5 border-b border-slate-800 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold tracking-tight text-white text-base">VERITAS AI</span>
            <span className="block text-[10px] text-slate-400 font-medium uppercase tracking-wider">Model Governance</span>
          </div>
        </Link>
      </div>

      {/* Project Switcher Pill */}
      <div className="px-3 pt-4 pb-2">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-2.5 flex items-center justify-between text-xs text-slate-300">
          <div className="flex items-center space-x-2 truncate">
            <Building2 className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
            <span className="truncate font-medium text-slate-200">Credit Memo Underwriting</span>
          </div>
          <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded font-mono">PROD</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
        <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider px-2 pt-2 pb-1">
          Operations & Gating
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center justify-between px-2.5 py-2 rounded-md text-xs font-medium transition-colors ${
                isActive
                  ? "bg-indigo-600/15 text-indigo-400 border border-indigo-500/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
              }`}
            >
              <div className="flex items-center space-x-2.5">
                <Icon className={`w-4 h-4 ${isActive ? "text-indigo-400" : "text-slate-400"}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] bg-amber-500/20 text-amber-400 border border-amber-500/30 px-1.5 py-0.5 rounded-full font-medium">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Public Marketing Link */}
      <div className="px-3 py-2 border-t border-slate-900">
        <Link
          href="/"
          className="flex items-center justify-between px-3 py-2 text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 rounded-lg transition-colors group"
        >
          <div className="flex items-center space-x-2">
            <Globe className="w-3.5 h-3.5 text-indigo-400" />
            <span>Public Website</span>
          </div>
          <ChevronRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-slate-400 transition-colors" />
        </Link>
      </div>

      {/* Footer System Status */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/50">
        <div className="flex items-center justify-between text-[11px] text-slate-400 px-2 py-1.5">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-medium text-slate-300">SR 11-7 Controls</span>
          </div>
          <span className="font-mono text-[10px] text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-1.5 py-0.5 rounded">
            ACTIVE
          </span>
        </div>
      </div>
    </aside>
  );
}

