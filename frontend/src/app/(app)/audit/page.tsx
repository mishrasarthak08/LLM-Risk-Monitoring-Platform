"use client";

import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { api } from "@/lib/api";
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Hash,
  Lock,
  FileCheck,
} from "lucide-react";

export default function AuditPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [verification, setVerification] = useState<any | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedAuditRecord, setSelectedAuditRecord] = useState<any | null>(null);
  const [verifyNotice, setVerifyNotice] = useState<string | null>(null);

  useEffect(() => {
    async function loadAudit() {
      try {
        const [evts, ver] = await Promise.all([
          api.getAuditEvents(),
          api.verifyAuditChain(),
        ]);
        setEvents(evts);
        setVerification(ver);
      } catch (err) {
        console.error("Failed to load audit records", err);
      } finally {
        setLoading(false);
      }
    }
    loadAudit();
  }, []);

  const handleVerifyNow = async () => {
    setVerifying(true);
    setVerifyNotice(null);
    try {
      const res = await api.verifyAuditChain();
      setVerification(res);
      setVerifyNotice(res.message);
    } catch (err: any) {
      setVerifyNotice("Verification failed: " + (err.message || err));
    } finally {
      setVerifying(false);
    }
  };

  return (
    <>
      <Header
        title="Cryptographic Audit Ledger & Chain Integrity"
        subtitle="Mathematically verifiable append-only SHA-256 hash chain providing non-repudiation."
      />

      <main className="p-8 space-y-8">
        {verifyNotice && (
          <div className="p-3.5 bg-indigo-950/40 border border-indigo-500/40 text-indigo-300 rounded-xl text-xs flex items-center justify-between animate-in fade-in">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>{verifyNotice}</span>
            </div>
            <button onClick={() => setVerifyNotice(null)} className="text-slate-400 hover:text-slate-200">
              ✕
            </button>
          </div>
        )}

        {/* Verification Status Card */}
        {verification && (
          <div
            className={`p-6 rounded-xl border flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
              verification.is_valid
                ? "bg-emerald-950/20 border-emerald-500/40"
                : "bg-rose-950/20 border-rose-500/40"
            }`}
          >
            <div>
              <div className="flex items-center space-x-2">
                {verification.is_valid ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                ) : (
                  <XCircle className="w-5 h-5 text-rose-400" />
                )}
                <span className="text-xs uppercase font-mono tracking-wider font-bold text-slate-300">
                  Cryptographic Ledger Status
                </span>
              </div>
              <h2 className="text-xl font-bold mt-1 text-slate-100">
                {verification.is_valid ? "Audit Chain Intact & Fully Verified" : "Tampering Detected"}
              </h2>
              <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
                {verification.message}
              </p>
              {verification.head_hash && (
                <div className="mt-2 text-xs font-mono text-slate-400">
                  Head Hash: <span className="text-emerald-400">{verification.head_hash}</span>
                </div>
              )}
            </div>

            <button
              onClick={handleVerifyNow}
              disabled={verifying}
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition-colors disabled:opacity-50 shrink-0"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${verifying ? "animate-spin" : ""}`} />
              <span>{verifying ? "Auditing Chain..." : "Verify Hash Chain Now"}</span>
            </button>
          </div>
        )}

        {/* Audit Events Ledger Table */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
              <Lock className="w-4 h-4 text-indigo-400" />
              <span>Immutable Event Ledger</span>
            </h3>
            <span className="text-xs text-slate-400 font-mono">
              Total Records: {events.length}
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/80 text-slate-400 font-medium border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Seq #</th>
                  <th className="py-2.5 px-3">Event Type</th>
                  <th className="py-2.5 px-3">Actor</th>
                  <th className="py-2.5 px-3">Record SHA-256 Hash</th>
                  <th className="py-2.5 px-3">Previous Hash Pointer</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                {events.map((evt) => (
                  <tr
                    key={evt.id}
                    onClick={() => setSelectedAuditRecord(evt)}
                    className="hover:bg-slate-900/60 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-3 text-slate-400 font-bold">#{evt.sequence_number}</td>
                    <td className="py-3 px-3 font-sans font-medium text-slate-200">
                      <span className="bg-slate-800/80 px-2 py-0.5 rounded text-[10px] font-mono">
                        {evt.event_type}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-400 font-sans">{evt.actor_email}</td>
                    <td className="py-3 px-3 text-emerald-400">
                      {(evt.record_hash || "").slice(0, 16)}...{(evt.record_hash || "").slice(-6)}
                    </td>
                    <td className="py-3 px-3 text-slate-500">
                      {(evt.previous_hash || "").slice(0, 16)}...{(evt.previous_hash || "").slice(-6)}
                    </td>
                    <td className="py-3 px-3 text-slate-500 font-sans">
                      {new Date(evt.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Payload Inspector Modal */}
        {selectedAuditRecord && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col shadow-2xl">
              <div className="p-5 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-indigo-400 font-mono uppercase tracking-wider font-semibold">
                    Audit Block #{selectedAuditRecord.sequence_number}
                  </span>
                  <h3 className="text-sm font-bold text-slate-100 font-mono mt-0.5">
                    {selectedAuditRecord.event_type}
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedAuditRecord(null)}
                  className="text-slate-400 hover:text-white p-1 rounded-lg text-sm"
                >
                  ✕
                </button>
              </div>

              <div className="p-6 overflow-y-auto space-y-4 text-xs font-mono">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">Actor</span>
                  <span className="text-slate-300 font-sans">{selectedAuditRecord.actor_email}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">SHA-256 Record Hash</span>
                  <span className="text-emerald-400 break-all">{selectedAuditRecord.record_hash}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">Previous Hash Pointer</span>
                  <span className="text-slate-400 break-all">{selectedAuditRecord.previous_hash}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block mb-1">Payload JSON</span>
                  <pre className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 overflow-x-auto text-[11px] leading-relaxed">
                    {JSON.stringify(selectedAuditRecord.payload_json, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </>
  );
}

