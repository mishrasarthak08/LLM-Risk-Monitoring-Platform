"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldCheck, CheckCircle2, User, Key, Bell, ExternalLink, Search, LogOut } from "lucide-react";

interface HeaderProps {
  title: string;
  subtitle?: string;
}

export function Header({ title, subtitle }: HeaderProps) {
  const [userName, setUserName] = useState("Sarah Jenkins");
  const [userRole, setUserRole] = useState("Model Risk Officer");
  const [initials, setInitials] = useState("SJ");
  const [showMenu, setShowMenu] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (typeof window !== "undefined") {
      try {
        const stored = localStorage.getItem("veritas_user");
        if (stored) {
          const user = JSON.parse(stored);
          if (user.full_name) {
            setUserName(user.full_name);
            const parts = user.full_name.trim().split(/\s+/);
            const init = parts.length >= 2 ? `${parts[0][0]}${parts[1][0]}`.toUpperCase() : user.full_name.slice(0, 2).toUpperCase();
            setInitials(init);
          }
          if (user.email) {
            setUserRole(user.email);
          }
        }
      } catch {
        // Fallback default
      }
    }
  }, []);

  const handleSignOut = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("veritas_token");
      localStorage.removeItem("veritas_user");
    }
    router.push("/login");
  };

  const triggerCommandPalette = () => {
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "k", metaKey: true }));
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-30 px-8 flex items-center justify-between">
      <div>
        <h1 className="text-base font-semibold text-slate-100 tracking-tight">{title}</h1>
        {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
      </div>

      <div className="flex items-center space-x-4">
        {/* Quick Search / Command Palette Trigger */}
        <button
          onClick={triggerCommandPalette}
          className="hidden md:flex items-center space-x-2 text-xs text-slate-400 bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
        >
          <Search className="w-3.5 h-3.5 text-slate-500" />
          <span>Search console...</span>
          <kbd className="text-[10px] font-mono text-slate-500 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800">
            ⌘K
          </kbd>
        </button>

        {/* Verification Status Pill */}
        <div className="hidden sm:flex items-center space-x-1.5 bg-emerald-950/40 border border-emerald-800/40 text-emerald-400 px-2.5 py-1 rounded-full text-xs font-medium">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>Audit Ledger Verified</span>
        </div>

        {/* Evaluator Status */}
        <div className="hidden md:flex items-center space-x-1.5 bg-indigo-950/40 border border-indigo-800/40 text-indigo-300 px-2.5 py-1 rounded-full text-xs font-medium">
          <span className="font-mono text-[10px]">JUDGE κ: 0.825</span>
          <span className="text-[10px] text-indigo-400 font-semibold">(CALIBRATED)</span>
        </div>

        {/* User Badge with Logout Dropdown */}
        <div className="relative pl-2 border-l border-slate-800">
          <button
            onClick={() => setShowMenu((prev) => !prev)}
            className="flex items-center space-x-2 hover:opacity-80 transition-opacity cursor-pointer focus:outline-none"
          >
            <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-indigo-600 to-indigo-800 border border-indigo-500/50 flex items-center justify-center text-xs font-bold text-white shadow-sm">
              {initials}
            </div>
            <div className="hidden lg:block text-left">
              <span className="block text-xs font-medium text-slate-200">{userName}</span>
              <span className="block text-[10px] text-slate-400 truncate max-w-[120px]">{userRole}</span>
            </div>
          </button>

          {showMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-1 z-50 animate-in fade-in duration-100">
              <div className="px-3 py-2 border-b border-slate-800 text-xs">
                <span className="block font-medium text-slate-200 truncate">{userName}</span>
                <span className="block text-[10px] text-slate-400 truncate">{userRole}</span>
              </div>
              <button
                onClick={handleSignOut}
                className="w-full text-left flex items-center space-x-2 px-3 py-2 text-xs text-rose-400 hover:bg-slate-800/80 rounded-lg transition-colors cursor-pointer mt-1"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Sign Out of Console</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

