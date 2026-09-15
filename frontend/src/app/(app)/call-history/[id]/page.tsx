"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getCallDetail } from "@/lib/api";
import { getRiskColors, formatDuration, formatTimestamp, getScamCategoryLabel, getLanguageName, formatProbability } from "@/lib/utils";

type Detail = Awaited<ReturnType<typeof getCallDetail>>;

function ScoreBar({ label, value, color }: { label: string; value: number | null; color: string }) {
  const pct = value !== null ? Math.round(value * 100) : null;
  return (
    <div>
      <div className="flex justify-between text-sm mb-1.5">
        <span className="text-slate-600">{label}</span>
        <span className="font-semibold text-slate-900">{pct !== null ? `${pct}%` : "Unavailable"}</span>
      </div>
      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
        <div
          className="h-2 rounded-full"
          style={{ width: pct !== null ? `${pct}%` : "0%", background: color }}
        />
      </div>
    </div>
  );
}

export default function CallDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [detail, setDetail] = useState<Detail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      getCallDetail(id).then(setDetail).catch(() => router.push("/call-history")).finally(() => setLoading(false));
    }
  }, [id, router]);

  if (loading) return <div className="p-8 text-slate-400 text-sm">Loading call report...</div>;
  if (!detail) return null;

  const { call, analysis } = detail;
  const riskColors = getRiskColors(analysis?.risk_level);

  return (
    <div className="p-8 max-w-3xl space-y-6">
      {/* Back */}
      <button onClick={() => router.back()} className="text-sm text-slate-500 hover:text-slate-800 flex items-center gap-1">
        ← Back to Call History
      </button>

      {/* Header card */}
      <div className={`rounded-xl border-2 p-6 ${riskColors.bg} ${riskColors.border}`}>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900">Call Safety Report</h1>
            {call.is_demo && (
              <span className="text-xs bg-amber-50 text-amber-600 border border-amber-100 px-2 py-0.5 rounded-full ml-2">
                DEMO
              </span>
            )}
            <div className="mt-2 space-y-0.5 text-sm text-slate-600">
              <p><span className="font-medium">Caller:</span> {call.caller_number || "Unknown"}</p>
              <p><span className="font-medium">Date:</span> {formatTimestamp(call.timestamp)}</p>
              <p><span className="font-medium">Duration:</span> {formatDuration(call.duration_seconds)}</p>
              <p><span className="font-medium">Language:</span> {getLanguageName(call.language)}</p>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-4xl font-bold ${riskColors.text}`}>
              {analysis?.risk_score ?? "—"}
            </div>
            <div className="text-sm text-slate-500">/ 100</div>
            <div className={`mt-1 px-3 py-1 rounded-full text-sm font-bold ${riskColors.badge}`}>
              {riskColors.icon} {analysis?.risk_level || "UNKNOWN"}
            </div>
          </div>
        </div>
      </div>

      {/* Probability breakdown */}
      {analysis && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
          <h2 className="font-semibold text-slate-900">Analysis Breakdown</h2>
          <ScoreBar
            label={`Voice Authenticity — ${analysis.voice_label ? analysis.voice_label.toUpperCase() : "Unavailable"}`}
            value={analysis.voice_fake_probability}
            color="#ef4444"
          />
          <ScoreBar
            label={`Scam Probability — ${getScamCategoryLabel(analysis.scam_category)}`}
            value={analysis.scam_probability}
            color="#f97316"
          />

          <div className="flex gap-4 pt-2">
            <div className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full border ${analysis.financial_request ? "bg-red-50 text-red-700 border-red-200" : "bg-slate-50 text-slate-400 border-slate-200"}`}>
              {analysis.financial_request ? "🔴 Financial Request Detected" : "⚪ No Financial Request"}
            </div>
            <div className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full border ${analysis.urgency_detected ? "bg-orange-50 text-orange-700 border-orange-200" : "bg-slate-50 text-slate-400 border-slate-200"}`}>
              {analysis.urgency_detected ? "🟠 Urgency Detected" : "⚪ No Urgency"}
            </div>
          </div>
        </div>
      )}

      {/* Transcript */}
      {analysis?.transcript && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h2 className="font-semibold text-slate-900 mb-3">Transcript</h2>
          <p className="text-sm text-slate-600 leading-relaxed">{analysis.transcript}</p>
        </div>
      )}

      {/* Detected signals */}
      {analysis?.scam_signals && analysis.scam_signals.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h2 className="font-semibold text-slate-900 mb-3">Detected Signals</h2>
          <div className="flex flex-wrap gap-2">
            {analysis.scam_signals.map((s, i) => (
              <span key={i} className="text-xs bg-red-50 text-red-700 border border-red-100 px-2.5 py-1 rounded-full">
                ✓ {s}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Risk reasons */}
      {analysis?.risk_reasons && analysis.risk_reasons.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h2 className="font-semibold text-slate-900 mb-3">Why This Call Was Flagged</h2>
          <div className="space-y-2">
            {analysis.risk_reasons.map((r, i) => (
              <p key={i} className="text-sm text-slate-700">{r}</p>
            ))}
          </div>
        </div>
      )}

      {/* Recommended actions */}
      {analysis?.risk_actions && analysis.risk_actions.length > 0 && (
        <div className={`rounded-xl border p-5 ${riskColors.bg} ${riskColors.border}`}>
          <h2 className="font-semibold text-slate-900 mb-3">Recommended Action</h2>
          {analysis.risk_actions.map((a, i) => (
            <p key={i} className="text-sm text-slate-700 mb-1 flex items-start gap-2">
              <span className="mt-0.5">→</span> {a}
            </p>
          ))}
        </div>
      )}

      {/* Technical info */}
      {analysis && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h2 className="font-semibold text-slate-900 mb-3 text-sm">Technical Details</h2>
          <div className="grid grid-cols-2 gap-2 text-xs text-slate-500">
            <div>ASR Model: <span className="text-slate-700">{analysis.asr_model || "—"}</span></div>
            <div>Deepfake Model: <span className="text-slate-700">{analysis.deepfake_model || "—"}</span></div>
            <div>Total Latency: <span className="text-slate-700">{analysis.total_latency_ms ? `${analysis.total_latency_ms.toFixed(0)}ms` : "—"}</span></div>
            <div>Action: <span className="text-slate-700">{call.action_taken || "—"}</span></div>
          </div>
        </div>
      )}
    </div>
  );
}
