"use client";

export default function ContactsPage() {
  const RELATIONSHIP_OPTIONS = [
    { id: "father", label: "Father", emoji: "👨" },
    { id: "mother", label: "Mother", emoji: "👩" },
    { id: "brother", label: "Brother", emoji: "👦" },
    { id: "sister", label: "Sister", emoji: "👧" },
    { id: "spouse", label: "Spouse", emoji: "💑" },
    { id: "friend", label: "Friend", emoji: "🤝" },
    { id: "bank", label: "Bank", emoji: "🏦" },
    { id: "emergency", label: "Emergency", emoji: "🚨" },
  ];

  return (
    <div className="p-6 md:p-10 max-w-4xl space-y-6 font-sans text-slate-100 selection:bg-blue-500/30">
      {/* Header */}
      <div className="border-b border-slate-800/80 pb-6">
        <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
          Trusted Contacts
        </h1>
        <p className="text-xs md:text-sm text-slate-400 mt-1">
          Add trusted numbers — VoxShield will apply lower risk scoring to these callers
        </p>
      </div>

      {/* Speaker verification notice */}
      <div className="bg-blue-950/40 border border-blue-800/60 rounded-xl p-4 text-xs backdrop-blur-xl shadow-lg">
        <p className="font-bold text-blue-300 mb-1 flex items-center gap-1.5">
          <span>🔬</span> Speaker Verification — Coming Soon
        </p>
        <p className="text-slate-300 leading-relaxed">
          In a future update, you can record your trusted contacts&apos; voices. VoxShield will
          compare incoming callers against enrolled voiceprints.
        </p>
        <p className="text-blue-400 mt-1.5 text-[11px] font-mono">
          Current status: Identity verification not configured — no fake similarity scores shown.
        </p>
      </div>

      {/* Empty state */}
      <div className="bg-slate-900/60 rounded-xl border border-slate-800/90 p-8 text-center backdrop-blur-xl shadow-2xl">
        <p className="text-3xl mb-3 text-amber-400">★</p>
        <h2 className="font-bold text-base text-white mb-1">No trusted contacts yet</h2>
        <p className="text-xs text-slate-400 mb-5">
          Add contacts like family members or your bank&apos;s verified number.
        </p>
        <div className="flex flex-wrap gap-2 justify-center mb-6 max-w-md mx-auto">
          {RELATIONSHIP_OPTIONS.map((r) => (
            <span
              key={r.id}
              className="text-xs bg-slate-950/80 border border-slate-800 text-slate-300 px-3 py-1.5 rounded-full font-medium"
            >
              {r.emoji} {r.label}
            </span>
          ))}
        </div>
        <button className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-lg transition shadow-lg shadow-blue-600/25">
          + Add Trusted Contact
        </button>
      </div>

      {/* How it works */}
      <div className="bg-slate-900/60 rounded-xl border border-slate-800/90 p-6 backdrop-blur-xl shadow-xl">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-4">
          How Trusted Contacts Work
        </h2>
        <div className="space-y-3.5">
          {[
            { step: "1", text: "Add a phone number and relationship classification" },
            { step: "2", text: "VoxShield applies a trust bonus — reducing overall algorithmic risk" },
            { step: "3", text: "Future: Enroll their voice for AI-powered acoustic verification" },
          ].map((item) => (
            <div key={item.step} className="flex items-start gap-3 text-xs">
              <span className="w-6 h-6 rounded-full bg-blue-950 border border-blue-700/80 text-blue-400 font-mono font-bold flex items-center justify-center shrink-0">
                {item.step}
              </span>
              <p className="text-slate-300 mt-0.5 font-medium">{item.text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}