"use client";

const SCAM_TYPES = [
  {
    id: "ai-voice",
    emoji: "🤖",
    title: "AI Voice Scam",
    description: "Criminals use AI to clone voices of family members, officials, or celebrities.",
    signs: [
      "Urgent money requests from a 'family member'",
      "Caller claiming emergency but number is unknown",
      "Voice sounds slightly robotic or unnatural",
      "Caller refuses to video call or meet",
    ],
    action: "Hang up. Call the person back on their saved number.",
  },
  {
    id: "upi",
    emoji: "💳",
    title: "UPI / Payment Scam",
    description: "Caller asks you to share UPI PIN, click a payment link, or accept a 'collect request'.",
    signs: [
      "Request to share UPI PIN",
      "Sending Re.1 to 'verify' account",
      "Accepting collect requests",
      "Clicking unknown payment links",
    ],
    action: "Never share UPI PIN. Block collect requests from unknown numbers.",
  },
  {
    id: "digital-arrest",
    emoji: "🚔",
    title: "Digital Arrest Scam",
    description: "Caller impersonates CBI/police and threatens 'digital arrest' for fake crimes.",
    signs: [
      "Call from fake 'CBI', 'Interpol', 'Cyber Cell'",
      "Threats of arrest or FIR",
      "Demands for money to 'settle' the case",
      "Keeping you on call for hours",
    ],
    action: "Digital arrest does not exist. Hang up. Real officers never demand money via call.",
  },
  {
    id: "kyc",
    emoji: "📋",
    title: "KYC Scam",
    description: "Caller claims your KYC is expired and account will be blocked without immediate update.",
    signs: [
      "Claim that KYC is pending",
      "Asking for government ID details or PAN over phone",
      "Threat of SIM or account deactivation",
    ],
    action: "KYC is never done over phone. Visit your bank or telecom store in person.",
  },
  {
    id: "family-impersonation",
    emoji: "👨‍👩‍👧",
    title: "Family Impersonation",
    description: "Caller claims to be a relative in an emergency needing immediate money.",
    signs: [
      "Caller says 'Beta/Papa/Bhai main hoon'",
      "Claims to be in hospital, jail, or accident",
      "Urgent request for money transfer",
      "Asks you not to tell other family members",
    ],
    action: "Hang up. Directly call the family member on their real number to verify.",
  },
  {
    id: "investment",
    emoji: "📈",
    title: "Investment Scam",
    description: "Promise of guaranteed high returns on stock trading, crypto, or app investments.",
    signs: [
      "Guaranteed returns of 30-40%+ monthly",
      "Pressure to invest immediately",
      "Invitation to exclusive WhatsApp/Telegram groups",
      "'Expert trader' will manage your funds",
    ],
    action: "No investment guarantees returns. Verify SEBI registration at sebi.gov.in.",
  },
  {
    id: "courier",
    emoji: "📦",
    title: "Courier Scam",
    description: "Call claiming your parcel contains illegal items or customs duty is due.",
    signs: [
      "'Your parcel has been stopped at customs'",
      "Claims of drugs or illegal items found",
      "Demands payment to release parcel",
      "Threat of police case",
    ],
    action: "Track parcels only on official courier websites. Customs never calls individuals.",
  },
];

const NEVER_SHARE = ["OTP", "UPI PIN", "ATM PIN", "Password", "CVV", "Government ID Details", "PAN Card"];

export default function SafetyCenterPage() {
  return (
    <div className="p-6 md:p-10 max-w-5xl space-y-8 font-sans text-slate-100 selection:bg-blue-500/30">
      {/* Header */}
      <div className="border-b border-slate-800/80 pb-6">
        <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
          <span>🛡️</span> Scam Safety Center
        </h1>
        <p className="text-slate-400 text-xs md:text-sm mt-1">
          Learn to recognize and protect yourself from sophisticated voice extortion
        </p>
      </div>

      {/* Never Share Banner */}
      <div className="rounded-xl bg-rose-950/40 border border-rose-800/80 p-6 backdrop-blur-xl shadow-2xl">
        <h2 className="font-extrabold text-rose-400 text-sm md:text-base uppercase tracking-wider mb-3">
          Things VoxShield Will NEVER Ask You to Share
        </h2>
        <div className="flex flex-wrap gap-2.5">
          {NEVER_SHARE.map((item) => (
            <span
              key={item}
              className="px-3 py-1.5 bg-slate-950/80 border border-rose-800/60 text-rose-300 text-xs font-semibold rounded-full shadow-inner"
            >
              ❌ {item}
            </span>
          ))}
        </div>
        <p className="text-[11px] font-mono text-rose-300/80 mt-4 leading-relaxed">
          No legitimate organization — bank, police, or central agency — will ever demand these over an unverified telephony stream.
        </p>
      </div>

      {/* Scam Type Cards */}
      <div className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Know Your Scam Vectors
        </h2>
        <div className="grid grid-cols-1 gap-4">
          {SCAM_TYPES.map((scam) => (
            <div
              key={scam.id}
              className="bg-slate-900/60 rounded-xl border border-slate-800/90 p-5 shadow-xl backdrop-blur-xl"
            >
              <div className="flex items-start gap-4">
                <span className="text-3xl p-2 rounded-lg bg-slate-950/80 border border-slate-800 shrink-0">
                  {scam.emoji}
                </span>
                <div className="flex-1">
                  <h3 className="font-bold text-white text-base tracking-tight">{scam.title}</h3>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">{scam.description}</p>

                  <div className="mt-4">
                    <p className="text-[10px] font-mono font-bold text-amber-400 uppercase tracking-wider mb-2">
                      Warning Signs
                    </p>
                    <ul className="space-y-1.5">
                      {scam.signs.map((s, i) => (
                        <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
                          <span className="text-amber-400 shrink-0">⚠</span>
                          <span>{s}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="mt-4 p-3 bg-emerald-950/30 border border-emerald-800/60 rounded-lg">
                    <p className="text-[10px] font-mono font-bold text-emerald-400 uppercase tracking-wider mb-1">
                      Countermeasure Action
                    </p>
                    <p className="text-xs text-emerald-200 font-medium">{scam.action}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Report Section */}
      <div className="bg-slate-900/60 border border-slate-800/90 rounded-xl p-6 backdrop-blur-xl shadow-xl">
        <h2 className="text-sm font-bold uppercase tracking-wider text-blue-400 mb-2">
          Report Extortion Calls
        </h2>
        <p className="text-xs text-slate-300 leading-relaxed">
          Report cybercrime at <span className="font-mono text-white underline">cybercrime.gov.in</span> or dial the National Cybercrime Helpline <span className="font-mono text-emerald-400 font-bold">1930</span> immediately.
        </p>
      </div>
    </div>
  );
}