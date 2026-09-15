"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getCallerDetail } from "@/lib/api";
import { getRiskColors, formatTimestamp, formatDuration, getScamCategoryLabel } from "@/lib/utils";
import Link from "next/link";

export default function CallerDetailPage() {
  const { number } = useParams<{ number: string }>();
  const router = useRouter();
  const decoded = decodeURIComponent(number);
  const [detail, setDetail] = useState<Awaited<ReturnType<typeof getCallerDetail>> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (decoded) {
      getCallerDetail(decoded)
        .then(setDetail)
        .catch(() => router.push("/callers"))
        .finally(() => setLoading(false));
    }
  }, [decoded, router]);

  if (loading) return <div className="p-8 text-slate-400 text-sm">Loading caller profile...</div>;
  if (!detail) return null;

  const overallRisk =
    detail.avg_risk_score !== null
      ? detail.avg_risk_score >= 75 ? "HIGH" : detail.avg_risk_score >= 45 ? "CAUTION" : "LOW"
      : null;
  const colors = getRiskColors(overallRisk);

  return (
    <div className="p-8 max-w-3xl space-y-5">
      <button onClick={() => router.back()} className="text-sm text-slate-500 hover:text-slate-800 flex items-center gap-1">
        ← Back to Callers
      </button>

      {/* Profile header */}
      <div className={`rounded-xl border-2 p-5 ${colors.bg} ${colors.border}`}>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900">Caller Risk Profile</h1>
            <p className="text-2xl font-mono font-semibold text-slate-800 mt-1">{detail.phone_number}</p>
            <div className="flex flex-wrap gap-2 mt-3">
              {detail.alert_count >= 3 && (
                <span className="text-xs bg-red-100 text-red-700 border border-red-200 px-2.5 py-1 rounded-full font-medium">
                  ⚠ Repeated High-Risk Caller
                </span>
              )}
              {detail.most_common_category && (
                <span className="text-xs bg-white border border-slate-200 text-slate-600 px-2.5 py-1 rounded-full">
                  Most Common: {getScamCategoryLabel(detail.most_common_category)}
                </span>
              )}
            </div>
          </div>
          <div className="text-right">
            <div className={`text-4xl font-bold ${colors.text}`}>
              {detail.avg_risk_score !== null ? Math.round(detail.avg_risk_score) : "—"}
            </div>
            <div className="text-xs text-slate-400">avg risk score</div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-white/50">
          <div>
            <p className="text-2xl font-bold text-slate-800">{detail.total_calls}</p>
            <p className="text-xs text-slate-500">Total Calls</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-red-600">{detail.alert_count}</p>
            <p className="text-xs text-slate-500">Alerts Triggered</p>
          </div>
          <div>
            <p className={`text-sm font-semibold mt-1 ${colors.text}`}>{overallRisk || "—"}</p>
            <p className="text-xs text-slate-500">Risk Status</p>
          </div>
        </div>
      </div>

      {/* Call list */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-100">
          <h2 className="font-semibold text-slate-900 text-sm">Call History with This Number</h2>
        </div>
        <div className="divide-y divide-slate-50">
          {detail.calls.map((call) => {
            const rc = getRiskColors(call.risk_level);
            return (
              <Link
                key={call.id}
                href={`/call-history/${call.id}`}
                className="flex items-center justify-between px-5 py-3 hover:bg-slate-50 transition-colors"
              >
                <div>
                  <p className="text-sm text-slate-800">{formatTimestamp(call.timestamp)}</p>
                  <p className="text-xs text-slate-400">
                    {formatDuration(call.duration_seconds)} · {getScamCategoryLabel(call.scam_category)}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${rc.badge}`}>
                    {rc.icon} {call.risk_level || "—"}
                  </span>
                  <span className="text-xs text-slate-400">→</span>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
