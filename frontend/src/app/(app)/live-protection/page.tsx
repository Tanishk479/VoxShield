"use client";

import { useEffect, useRef, useState } from "react";
import { analyzeAudio } from "@/lib/api";
import { getRiskColors, getScamCategoryLabel, getLanguageName } from "@/lib/utils";

type AnalysisResult = {
  type: string;
  chunk?: number;
  transcript?: { text: string; language: string | null; latency_ms: number; model_available: boolean };
  deepfake?: { fake_probability: number | null; real_probability: number | null; label: string; latency_ms: number; model_available: boolean };
  scam?: { scam_probability: number | null; category: string; category_name: string; signals: string[]; financial_request: boolean; urgency_detected: boolean };
  risk?: { risk_score: number | null; risk_level: string; reasons: string[]; recommended_actions: string[] };
  accumulated_transcript?: string;
  chunk_latency_ms?: number;
  error?: string;
};

function RiskMeter({ score, level }: { score: number | null; level: string }) {
  const colors = getRiskColors(level);
  const displayScore = score ?? 0;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Current Composite Risk</span>
        <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${colors.badge}`}>
          {colors.icon} {level || "UNKNOWN"}
        </span>
      </div>
      <div className="h-2.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
        <div
          className="h-2.5 rounded-full transition-all duration-700"
          style={{
            width: `${displayScore}%`,
            background:
              level === "CRITICAL" ? "#ef4444" :
              level === "HIGH" ? "#f97316" :
              level === "CAUTION" ? "#f59e0b" : "#22c55e",
          }}
        />
      </div>
      <div className="flex justify-between text-xs text-slate-500 font-mono">
        <span>Safe</span>
        <span className="font-bold text-white text-sm">{displayScore} / 100</span>
        <span>Critical</span>
      </div>
    </div>
  );
}

function ProbBar({
  label, value, color,
}: { label: string; value: number | null; color: string }) {
  const pct = value !== null ? Math.round(value * 100) : null;
  return (
    <div>
      <div className="flex justify-between text-xs mb-1.5 font-medium">
        <span className="text-slate-300">{label}</span>
        <span className="font-mono text-white font-bold">{pct !== null ? `${pct}%` : "—"}</span>
      </div>
      <div className="h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
        <div
          className="h-2 rounded-full transition-all duration-700"
          style={{ width: pct !== null ? `${pct}%` : "0%", background: color }}
        />
      </div>
    </div>
  );
}

export default function LiveProtectionPage() {
  const [status, setStatus] = useState<"idle" | "analyzing" | "complete">("idle");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [showAlert, setShowAlert] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (result?.risk?.risk_level === "CRITICAL") {
      setShowAlert(true);
    }
  }, [result?.risk?.risk_level]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;

    setUploadError(null);
    setShowAlert(false);
    setStatus("analyzing");

    try {
      const res = await analyzeAudio(file);
      const analysis = res.analysis;
      const mapped: AnalysisResult = {
        type: "analysis",
        transcript: {
          text: analysis.transcript?.text || "",
          language: analysis.transcript?.language ?? null,
          latency_ms: analysis.transcript?.latency_ms ?? 0,
          model_available: Boolean(analysis.transcript?.model_available),
        },
        deepfake: {
          fake_probability: analysis.deepfake?.fake_probability ?? null,
          real_probability: analysis.deepfake?.real_probability ?? null,
          label: analysis.deepfake?.label || "unavailable",
          latency_ms: analysis.deepfake?.latency_ms ?? 0,
          model_available: Boolean(analysis.deepfake?.model_available),
        },
        scam: {
          scam_probability: analysis.scam?.scam_probability ?? null,
          category: analysis.scam?.category || "UNKNOWN",
          category_name: analysis.scam?.category_name || "",
          signals: analysis.scam?.signals || [],
          financial_request: Boolean(analysis.scam?.financial_request),
          urgency_detected: Boolean(analysis.scam?.urgency_detected),
        },
        risk: {
          risk_score: analysis.risk?.risk_score ?? null,
          risk_level: analysis.risk?.risk_level || "UNKNOWN",
          reasons: analysis.risk?.reasons || [],
          recommended_actions: analysis.risk?.recommended_actions || [],
        },
        accumulated_transcript: analysis.transcript?.text || "",
        chunk_latency_ms: analysis.total_latency_ms,
      };
      setResult(mapped);
      setStatus("complete");
    } catch (err) {
      setStatus(result ? "complete" : "idle");
      setUploadError(err instanceof Error ? err.message : "Analysis failed");
    }
  };

  const display = result;
  const analyzing = status === "analyzing";
  const riskLevel = display?.risk?.risk_level || "LOW";
  const riskColors = getRiskColors(riskLevel);

  return (
    <div className="p-6 md:p-10 max-w-5xl space-y-6 font-sans text-slate-100 selection:bg-blue-500/30">
      {/* Header */}
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white flex items-center gap-2.5 tracking-tight">
          <span>🎙️</span> Live Protection & Audio Inspection
        </h1>
        <p className="text-slate-400 text-xs md:text-sm mt-1">
          Upload telephony streams for real-time acoustic synthesis and extortion intent parsing
        </p>
      </div>

      {/* Status bar */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4 shadow-xl backdrop-blur-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className={`w-2.5 h-2.5 rounded-full ${status === "analyzing" ? "bg-amber-400 animate-ping" : riskColors.dot} ${riskLevel === "CRITICAL" ? "animate-pulse" : ""}`} />
            <span className="font-semibold text-xs md:text-sm text-slate-200">
              {status === "idle" ? "Ready — Upload audio to analyze" :
               status === "analyzing" ? "Running VoxShield analysis pipeline..." :
               "Analysis complete"}
            </span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => fileRef.current?.click()}
              disabled={analyzing}
              className="px-4 py-2 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-500 transition shadow-lg shadow-blue-600/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {analyzing ? "Analyzing..." : "📂 Upload Audio"}
            </button>
            <input ref={fileRef} type="file" accept="audio/*,.wav,.mp3,.m4a,.flac,.ogg" className="hidden" onChange={handleFileUpload} />
          </div>
        </div>
      </div>

      {/* CRITICAL ALERT */}
      {showAlert && riskLevel === "CRITICAL" && (
        <div className="rounded-xl border border-rose-600/80 bg-rose-950/40 backdrop-blur-xl p-5 shadow-2xl">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="font-extrabold text-rose-400 text-base md:text-lg flex items-center gap-2">
                🚨 VOXSHIELD ALERT — CRITICAL RISK DETECTED
              </h2>
              <p className="text-rose-200/90 text-xs md:text-sm mt-1">
                This conversation may involve synthetic voice impersonation and a coercive financial scam.
              </p>
            </div>
            <button onClick={() => setShowAlert(false)} className="text-rose-400 hover:text-rose-200 text-sm font-bold">✕</button>
          </div>
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-2">
            <div className="bg-rose-950/80 border border-rose-800/80 rounded-lg p-2.5 text-center text-xs font-bold text-rose-300">
              ❌ Do NOT share OTP
            </div>
            <div className="bg-rose-950/80 border border-rose-800/80 rounded-lg p-2.5 text-center text-xs font-bold text-rose-300">
              ❌ Do NOT share PIN
            </div>
            <div className="bg-rose-950/80 border border-rose-800/80 rounded-lg p-2.5 text-center text-xs font-bold text-rose-300">
              ❌ Do NOT transfer money
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button className="flex-1 py-2 bg-rose-600 text-white text-xs font-bold rounded-lg hover:bg-rose-500 transition">
              Verify Caller
            </button>
            <button className="flex-1 py-2 bg-slate-900 border border-rose-800 text-rose-300 text-xs font-bold rounded-lg hover:bg-slate-800 transition">
              Block Call
            </button>
          </div>
        </div>
      )}

      {uploadError && (
        <div className="rounded-xl border border-rose-800 bg-rose-950/70 p-4 text-xs font-semibold text-rose-300">
          Analysis failed: {uploadError}
        </div>
      )}

      {analyzing && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-8 text-center backdrop-blur-xl">
          <div className="text-blue-400 text-xs font-mono animate-pulse">Running VoxShield multimodal inference pipeline...</div>
        </div>
      )}

      {/* Analysis Results */}
      {display && (
        <div className="space-y-4">
          {/* Risk Meter */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-xl backdrop-blur-xl">
            <RiskMeter score={display.risk?.risk_score ?? null} level={display.risk?.risk_level || "UNKNOWN"} />
            {display.chunk_latency_ms && (
              <p className="text-[11px] font-mono text-slate-500 mt-2 text-right">
                Pipeline latency: {display.chunk_latency_ms.toFixed(0)}ms
              </p>
            )}
          </div>

          {/* Probability bars */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 space-y-4 shadow-xl backdrop-blur-xl">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Signal Breakdown</h3>
            <ProbBar
              label={`Voice Authenticity — ${display.deepfake?.model_available ? display.deepfake.label?.toUpperCase() : "Model unavailable"}`}
              value={display.deepfake?.fake_probability ?? null}
              color="#ef4444"
            />
            <ProbBar
              label="Scam Intent"
              value={display.scam?.scam_probability ?? null}
              color="#f97316"
            />
            <div className="flex flex-wrap gap-2 pt-1">
              <div className={`flex items-center gap-1.5 text-xs px-3 py-1 rounded-full border ${display.scam?.financial_request ? "bg-rose-950/80 text-rose-400 border-rose-800" : "bg-slate-950 text-slate-500 border-slate-800"}`}>
                {display.scam?.financial_request ? "🔴" : "⚪"} Financial Request
              </div>
              <div className={`flex items-center gap-1.5 text-xs px-3 py-1 rounded-full border ${display.scam?.urgency_detected ? "bg-amber-950/80 text-amber-400 border-amber-800" : "bg-slate-950 text-slate-500 border-slate-800"}`}>
                {display.scam?.urgency_detected ? "🟠" : "⚪"} Urgency Detected
              </div>
            </div>
          </div>

          {/* Transcript */}
          {display.accumulated_transcript && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-xl backdrop-blur-xl">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Recognized Transcript</h3>
                {display.transcript?.language && (
                  <span className="text-[11px] font-mono bg-blue-950/80 text-blue-400 border border-blue-800 px-2.5 py-0.5 rounded-full">
                    {getLanguageName(display.transcript.language)}
                  </span>
                )}
              </div>
              <p className="text-xs md:text-sm text-slate-200 font-mono leading-relaxed bg-slate-950/80 p-3.5 rounded-lg border border-slate-800/60 italic">
                &quot;{display.accumulated_transcript}&quot;
              </p>
            </div>
          )}

          {/* Risk Reasons */}
          {display.risk?.reasons && display.risk.reasons.length > 0 && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-xl backdrop-blur-xl">
              <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 mb-3">Why This Call Was Flagged</h3>
              <div className="space-y-2">
                {display.risk.reasons.map((r, i) => (
                  <p key={i} className="text-xs md:text-sm text-slate-300 flex items-start gap-2">
                    <span className="text-amber-400">⚠</span> {r}
                  </p>
                ))}
              </div>
            </div>
          )}

          {/* Scam category */}
          {display.scam?.category && display.scam.category !== "UNKNOWN" && (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-xl backdrop-blur-xl">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                Detected Taxonomy: <span className="text-rose-400 font-mono">{getScamCategoryLabel(display.scam.category)}</span>
              </h3>
              {display.scam.signals.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {display.scam.signals.map((s, i) => (
                    <span key={i} className="text-xs bg-rose-950/60 text-rose-400 border border-rose-800/80 px-2.5 py-0.5 rounded-full font-mono">
                      ✓ {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Recommended Actions */}
          {display.risk?.recommended_actions && display.risk.recommended_actions.length > 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl backdrop-blur-xl">
              <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-2">Recommended Safety Protocols</h3>
              <div className="space-y-1.5">
                {display.risk.recommended_actions.map((a, i) => (
                  <p key={i} className="text-xs md:text-sm text-slate-300 flex items-start gap-2">
                    <span className="text-emerald-400 font-bold">→</span> {a}
                  </p>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Demo scenarios */}
      {!display && !analyzing && (
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-xl backdrop-blur-xl">
          <h3 className="text-xs font-bold uppercase tracking-wider text-white mb-1">Demo Scenarios</h3>
          <p className="text-xs text-slate-400 mb-4">
            Upload any of these scenario audio files from <code className="text-blue-400 font-mono">backend/test_samples/</code> to evaluate the pipeline:
          </p>
          <div className="space-y-2">
            {[
              { name: "Scenario 1 — Safe Call", expected: "Risk: LOW", color: "text-emerald-400 border-emerald-800/60 bg-emerald-950/40" },
              { name: "Scenario 2 — AI Voice Only", expected: "Voice authenticity warning", color: "text-amber-400 border-amber-800/60 bg-amber-950/40" },
              { name: "Scenario 3 — Real Voice + Scam", expected: "Risk: HIGH", color: "text-orange-400 border-orange-800/60 bg-orange-950/40" },
              { name: 'Scenario 4 — "Beta main hospital mein hoon..."', expected: "Risk: CRITICAL 🚨", color: "text-rose-400 border-rose-800/60 bg-rose-950/40" },
            ].map((s) => (
              <div key={s.name} className="flex items-center justify-between text-xs md:text-sm p-3 rounded-lg bg-slate-950/60 border border-slate-800/60 hover:border-slate-700 transition">
                <span className="text-slate-200 font-medium">{s.name}</span>
                <span className={`text-[11px] font-mono px-2 py-0.5 rounded border ${s.color}`}>
                  Expected: {s.expected}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}