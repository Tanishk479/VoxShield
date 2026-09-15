"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getCallers } from "@/lib/api";
import { getRiskColors, formatTimestamp } from "@/lib/utils";

type CallerRow = Awaited<ReturnType<typeof getCallers>>["callers"][number];

export default function CallersPage() {
  const [callers, setCallers] = useState<CallerRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCallers(50).then((r) => setCallers(r.callers)).finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 md:p-10 max-w-5xl space-y-6 font-sans text-slate-100 selection:bg-blue-500/30">
      {/* Header */}
      <div className="border-b border-slate-800/80 pb-6">
        <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
          Caller Intelligence
        </h1>
        <p className="text-xs md:text-sm text-slate-400 mt-1">
          Historical risk profiles and threat persistence for numbers that have called you
        </p>
      </div>

      {loading ? (
        <div className="text-slate-500 font-mono text-xs py-16 text-center">
          Loading caller intelligence telemetry...
        </div>
      ) : callers.length === 0 ? (
        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-12 text-center">
          <p className="text-slate-300 font-medium text-sm">No caller data recorded yet.</p>
          <p className="text-slate-500 text-xs mt-1">
            Intercept or analyze calls in{" "}
            <Link href="/live-protection" className="text-blue-400 hover:underline">
              Live Protection
            </Link>{" "}
            to automatically generate intelligence dossiers.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {callers.map((caller) => {
            const colors = getRiskColors(
              caller.risk_status === "HIGH_RISK" ? "HIGH" :
              caller.risk_status === "CAUTION" ? "CAUTION" :
              caller.risk_status === "TRUSTED" ? "LOW" : null
            );

            return (
              <Link
                key={caller.caller_number}
                href={`/callers/${encodeURIComponent(caller.caller_number)}`}
                className="block bg-slate-900/60 rounded-xl border border-slate-800/80 p-4 hover:border-blue-500/50 hover:bg-slate-800/40 backdrop-blur-xl transition-all shadow-lg"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3.5">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center border ${colors.border} ${colors.bg}`}>
                      <span className="text-lg">{colors.icon}</span>
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white text-sm">
                          {caller.caller_number}
                        </span>
                        {caller.is_trusted && (
                          <span className="text-[10px] font-mono bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 px-2 py-0.5 rounded-full">
                            ★ Trusted
                          </span>
                        )}
                        {caller.alert_count >= 3 && (
                          <span className="text-[10px] font-mono bg-rose-950/80 text-rose-400 border border-rose-800/80 px-2 py-0.5 rounded-full animate-pulse">
                            ⚠ Repeated High-Risk
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-400 mt-1 font-mono">
                        {caller.total_calls} call{caller.total_calls !== 1 ? "s" : ""} ·{" "}
                        {caller.alert_count} alert{caller.alert_count !== 1 ? "s" : ""} ·{" "}
                        Last intercepted: {formatTimestamp(caller.last_seen)}
                      </p>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className={`text-2xl font-black ${colors.text}`}>
                      {Math.round(caller.avg_risk_score)}
                    </div>
                    <div className="text-[10px] font-mono uppercase text-slate-500">
                      avg risk
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}