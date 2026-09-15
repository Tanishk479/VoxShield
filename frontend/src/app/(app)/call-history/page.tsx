"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getCallHistory } from "@/lib/api";
import { getRiskColors, formatDuration, formatTimestamp, getScamCategoryLabel, getLanguageName } from "@/lib/utils";

export default function CallHistoryPage() {
  const [calls, setCalls] = useState<Awaited<ReturnType<typeof getCallHistory>>["calls"]>([]);
  const [loading, setLoading] = useState(true);
  const [filterLevel, setFilterLevel] = useState("ALL");

  useEffect(() => {
    getCallHistory(50, 0).then((r) => setCalls(r.calls)).finally(() => setLoading(false));
  }, []);

  const filtered = filterLevel === "ALL"
    ? calls
    : calls.filter((c) => c.risk_level === filterLevel);

  const filters = ["ALL", "CRITICAL", "HIGH", "CAUTION", "LOW"];

  return (
    <div className="p-6 md:p-10 max-w-6xl space-y-6 font-sans text-slate-100 selection:bg-blue-500/30">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Call History</h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1">All analyzed calls, newest first</p>
        </div>
        <div className="inline-flex items-center gap-1.5 bg-amber-950/60 border border-amber-500/40 px-3 py-1 rounded-full text-xs font-mono text-amber-400">
          ⚠ Includes demo data
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {filters.map((f) => {
          const colors = getRiskColors(f === "ALL" ? null : f);
          const isActive = filterLevel === f;

          return (
            <button
              key={f}
              onClick={() => setFilterLevel(f)}
              className={`px-3.5 py-1.5 text-xs rounded-lg font-bold transition-all ${
                isActive
                  ? f === "ALL"
                    ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30 border border-blue-400/30"
                    : `${colors.bg} ${colors.text} border ${colors.border}`
                  : "bg-slate-900/80 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
              }`}
            >
              {f === "ALL" ? "All Calls" : f}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="text-slate-500 font-mono text-xs py-16 text-center">Loading call records from database...</div>
      ) : filtered.length === 0 ? (
        <div className="text-slate-400 text-sm py-16 text-center bg-slate-900/40 border border-slate-800 rounded-xl">
          No calls found.{" "}
          <Link href="/live-protection" className="text-blue-400 hover:underline font-semibold">
            Upload an audio file
          </Link>{" "}
          to analyze your first call.
        </div>
      ) : (
        <div className="bg-slate-900/60 rounded-xl border border-slate-800/90 overflow-hidden shadow-2xl backdrop-blur-xl">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/90 text-slate-400 uppercase font-mono text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-5 py-3.5">CALLER</th>
                <th className="px-5 py-3.5">DATE</th>
                <th className="px-5 py-3.5">DURATION</th>
                <th className="px-5 py-3.5">LANGUAGE</th>
                <th className="px-5 py-3.5">RISK</th>
                <th className="px-5 py-3.5">CATEGORY</th>
                <th className="px-5 py-3.5">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {filtered.map((call) => {
                const colors = getRiskColors(call.risk_level);
                return (
                  <tr
                    key={call.id}
                    className="hover:bg-slate-800/40 transition-colors"
                  >
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <Link href={`/call-history/${call.id}`} className="font-semibold text-white hover:text-blue-400 transition">
                          {call.caller_number || "Unknown"}
                        </Link>
                        {call.is_demo && (
                          <span className="text-[10px] font-mono bg-amber-950/80 text-amber-400 border border-amber-800/80 px-1.5 py-0.5 rounded">
                            DEMO
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-5 py-4 text-slate-400 font-mono text-[11px]">{formatTimestamp(call.timestamp)}</td>
                    <td className="px-5 py-4 text-slate-400 font-mono">{formatDuration(call.duration_seconds)}</td>
                    <td className="px-5 py-4 text-slate-300">{getLanguageName(call.language)}</td>
                    <td className="px-5 py-4">
                      {call.risk_level ? (
                        <span className={`text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full border ${colors.badge}`}>
                          {colors.icon} {call.risk_level}
                          {call.risk_score !== null ? ` ${call.risk_score}` : ""}
                        </span>
                      ) : (
                        <span className="text-slate-600 font-mono text-xs">—</span>
                      )}
                    </td>
                    <td className="px-5 py-4 text-slate-300">
                      <span className="bg-slate-950/80 border border-slate-800/80 px-2 py-1 rounded text-[11px]">
                        {getScamCategoryLabel(call.scam_category)}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                        call.action_taken === "BLOCKED"
                          ? "bg-rose-950/80 text-rose-400 border-rose-800"
                          : call.action_taken === "VERIFIED"
                          ? "bg-emerald-950/80 text-emerald-400 border-emerald-800"
                          : "bg-slate-950 text-slate-400 border-slate-800"
                      }`}>
                        {call.action_taken || "ANALYZED"}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}