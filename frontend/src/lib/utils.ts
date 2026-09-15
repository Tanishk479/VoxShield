// VoxShield — UI Utility Helpers

/**
 * Return Tailwind color classes for a risk level string.
 */
export function getRiskColors(level: string | null | undefined) {
  switch (level?.toUpperCase()) {
    case "CRITICAL":
      return {
        bg: "bg-red-50",
        border: "border-red-200",
        text: "text-red-700",
        badge: "bg-red-100 text-red-800",
        dot: "bg-red-500",
        icon: "🔴",
      };
    case "HIGH":
      return {
        bg: "bg-orange-50",
        border: "border-orange-200",
        text: "text-orange-700",
        badge: "bg-orange-100 text-orange-800",
        dot: "bg-orange-500",
        icon: "🟠",
      };
    case "CAUTION":
      return {
        bg: "bg-amber-50",
        border: "border-amber-200",
        text: "text-amber-700",
        badge: "bg-amber-100 text-amber-800",
        dot: "bg-amber-400",
        icon: "🟡",
      };
    case "LOW":
    default:
      return {
        bg: "bg-green-50",
        border: "border-green-200",
        text: "text-green-700",
        badge: "bg-green-100 text-green-800",
        dot: "bg-green-500",
        icon: "🟢",
      };
  }
}

export function getRiskLabel(level: string | null | undefined): string {
  return level?.toUpperCase() || "UNKNOWN";
}

export function formatProbability(prob: number | null | undefined, decimals = 0): string {
  if (prob === null || prob === undefined) return "—";
  return `${Math.round(prob * 100)}%`;
}

export function formatDuration(seconds: number | null | undefined): string {
  if (!seconds) return "—";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function formatTimestamp(ts: string | null | undefined): string {
  if (!ts) return "—";
  const d = new Date(ts);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffDays === 0) return `Today ${d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}`;
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

export function getLanguageName(code: string | null | undefined): string {
  const map: Record<string, string> = {
    en: "English", hi: "Hindi", pa: "Punjabi", ta: "Tamil",
    te: "Telugu", bn: "Bengali", mr: "Marathi", gu: "Gujarati",
    kn: "Kannada", ml: "Malayalam", or: "Odia", as: "Assamese",
  };
  if (!code) return "—";
  return map[code] || code.toUpperCase();
}

export function getScamCategoryLabel(cat: string | null | undefined): string {
  const map: Record<string, string> = {
    BANKING: "Bank Impersonation",
    UPI: "UPI Scam",
    KYC: "KYC Scam",
    OTP: "OTP Request",
    DIGITAL_ARREST: "Digital Arrest",
    POLICE_IMPERSONATION: "Police Impersonation",
    FAMILY_IMPERSONATION: "Family Impersonation",
    COURIER: "Courier Scam",
    JOB: "Fake Job",
    INVESTMENT: "Investment Scam",
    LOAN: "Loan Scam",
    LOTTERY: "Lottery Scam",
    SIM_BLOCK: "SIM Block",
    ACCOUNT_BLOCK: "Account Block",
    TECH_SUPPORT: "Tech Support",
    BLACKMAIL: "Blackmail",
    IDENTITY_THEFT: "Identity Theft",
    UNKNOWN: "Unknown / Suspicious",
  };
  return cat ? (map[cat] || cat) : "—";
}

export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(" ");
}
