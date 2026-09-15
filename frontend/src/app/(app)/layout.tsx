"use client";

import { ReactNode, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

interface NavItem {
  href: string;
  label: string;
  icon: string;
}

const NAV_ITEMS: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: "⊞" },
  { href: "/live-protection", label: "Live Protection", icon: "🎙️" },
  { href: "/call-history", label: "Call History", icon: "📞" },
  { href: "/analytics", label: "Analytics", icon: "📊" },
  { href: "/callers", label: "Callers", icon: "👥" },
  { href: "/contacts", label: "Contacts", icon: "★" },
  { href: "/safety-center", label: "Safety Center", icon: "🛡️" },
  { href: "/settings", label: "Settings", icon: "⚙" },
];

export default function AppLayout({ children }: { children: ReactNode }) {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading && !user) router.push("/login");
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#06080F] flex items-center justify-center font-mono">
        <div className="text-slate-500 text-xs">Loading VoxShield...</div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-[#06080F] flex font-sans">
      {/* Sidebar */}
      <aside className="w-56 bg-[#05070E] border-r border-slate-800/80 flex flex-col fixed h-full z-30">
        {/* Logo */}
        <div className="px-4 py-5 border-b border-slate-800/80">
          <div className="flex items-center gap-2">
            <span className="text-xl">🛡️</span>
            <span className="font-bold text-white text-base tracking-tight">VoxShield</span>
          </div>
          <p className="text-[10px] font-mono text-slate-500 mt-0.5"></p>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map((item) => {
            const active = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
                  active
                    ? "bg-blue-600/15 text-blue-400 border border-blue-500/30"
                    : "text-slate-400 hover:bg-slate-900/60 hover:text-slate-200 border border-transparent"
                }`}
              >
                <span className="text-sm w-5 text-center">{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* User footer */}
        <div className="px-4 py-4 border-t border-slate-800/80 bg-slate-950/40">
          <div className="text-xs font-bold text-slate-200 truncate">{user.full_name}</div>
          <div className="text-[10px] font-mono text-slate-500 truncate">{user.email}</div>
          <button
            onClick={logout}
            className="mt-2 text-[11px] text-slate-500 hover:text-rose-400 transition-colors"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 ml-56 min-h-screen bg-[#06080F]">
        {children}
      </main>
    </div>
  );
}