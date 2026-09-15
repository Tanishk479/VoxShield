"use client";

export default function SettingsPage() {
  const models = [
    { name: "Whisper Tiny (ASR)", status: "Loaded", color: "text-emerald-400 bg-emerald-950/60 border-emerald-800/60" },
    { name: "Spectra-0 (Deepfake)", status: "Loaded", color: "text-emerald-400 bg-emerald-950/60 border-emerald-800/60" },
    { name: "Scam Classifier (Hybrid)", status: "Ready", color: "text-emerald-400 bg-emerald-950/60 border-emerald-800/60" },
    { name: "IndicConformer 600M", status: "Disabled (RAM constraint)", color: "text-amber-400 bg-amber-950/60 border-amber-800/60" },
    { name: "Speaker Verification", status: "Not configured", color: "text-slate-400 bg-slate-950/80 border-slate-800" },
  ];

  return (
    <div className="p-6 md:p-10 max-w-4xl space-y-6 font-sans text-slate-100 selection:bg-blue-500/30">
      {/* Header */}
      <div className="border-b border-slate-800/80 pb-6">
        <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
          <span>⚙</span> Settings & Privacy
        </h1>
        <p className="text-xs md:text-sm text-slate-400 mt-1">
          Control how VoxShield manages telemetry streams and system model resources
        </p>
      </div>

      {/* Privacy Mode */}
      <div className="bg-slate-900/60 rounded-xl border border-slate-800/90 p-6 space-y-4 shadow-xl backdrop-blur-xl">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <span>🔒</span> Privacy Configuration
        </h2>
        <div className="space-y-3 divide-y divide-slate-800/60">
          <div className="flex items-center justify-between py-2 pt-0">
            <div>
              <p className="text-xs md:text-sm font-semibold text-slate-200">Audio Processing</p>
              <p className="text-[11px] font-mono text-slate-500 mt-0.5">Audio is processed locally and not stored</p>
            </div>
            <span className="text-[10px] font-mono bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 px-2.5 py-1 rounded-full">
              Local / Secure
            </span>
          </div>

          <div className="flex items-center justify-between py-3">
            <div>
              <p className="text-xs md:text-sm font-semibold text-slate-200">Call Recordings</p>
              <p className="text-[11px] font-mono text-slate-500 mt-0.5">Audio files are not permanently stored by default</p>
            </div>
            <span className="text-[10px] font-mono bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 px-2.5 py-1 rounded-full">
              Not Stored
            </span>
          </div>

          <div className="flex items-center justify-between py-3">
            <div>
              <p className="text-xs md:text-sm font-semibold text-slate-200">Transcript Retention</p>
              <p className="text-[11px] font-mono text-slate-500 mt-0.5">Transcripts retained for 30 days by default</p>
            </div>
            <span className="text-[10px] font-mono bg-blue-950/80 text-blue-400 border border-blue-800/80 px-2.5 py-1 rounded-full">
              30 Days
            </span>
          </div>

          <div className="flex items-center justify-between py-3 pb-0">
            <div>
              <p className="text-xs md:text-sm font-semibold text-slate-200">Encryption Standard</p>
              <p className="text-[11px] font-mono text-slate-500 mt-0.5">Data encrypted in transit (HTTPS / WSS)</p>
            </div>
            <span className="text-[10px] font-mono bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 px-2.5 py-1 rounded-full">
              In Transit
            </span>
          </div>
        </div>
      </div>

      {/* Data Management */}
      <div className="bg-slate-900/60 rounded-xl border border-slate-800/90 p-6 space-y-3 shadow-xl backdrop-blur-xl">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">Data Management</h2>
        <div className="space-y-3 pt-1">
          <button className="w-full text-left px-4 py-3 rounded-lg border border-slate-800 bg-slate-950/60 hover:bg-slate-800/50 hover:border-slate-700 transition">
            <p className="text-xs md:text-sm font-semibold text-slate-200">Delete Call History</p>
            <p className="text-[11px] font-mono text-slate-500 mt-0.5">Remove all analyzed call records and telemetry metadata</p>
          </button>
          <button className="w-full text-left px-4 py-3 rounded-lg border border-rose-900/60 bg-rose-950/20 hover:bg-rose-950/40 hover:border-rose-700 transition">
            <p className="text-xs md:text-sm font-semibold text-rose-400">Delete All My Data</p>
            <p className="text-[11px] font-mono text-rose-300/60 mt-0.5">Permanently delete account and all associated threat dossiers</p>
          </button>
        </div>
      </div>

      {/* Model Status */}
      <div className="bg-slate-900/60 rounded-xl border border-slate-800/90 p-6 shadow-xl backdrop-blur-xl">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-4">AI Model Status</h2>
        <div className="space-y-2 divide-y divide-slate-800/60 text-xs">
          {models.map((m) => (
            <div key={m.name} className="flex items-center justify-between py-2.5 first:pt-0 last:pb-0">
              <span className="font-semibold text-slate-200">{m.name}</span>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded border font-semibold ${m.color}`}>
                {m.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* About */}
      <div className="bg-slate-950/60 rounded-xl border border-slate-800/80 p-5 text-xs text-slate-400 backdrop-blur-md">
        <p className="font-bold text-slate-200 mb-1">VoxShield v1.0.0</p>
        <p>AI-Powered Voice Scam Protection Platform</p>
        
        <p className="mt-3 text-amber-400 font-mono text-[11px]">
          ⚠ Demo environment — AI model outputs are real but demo call history is synthetic.
        </p>
      </div>
    </div>
  );
}