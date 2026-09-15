"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const { login, user, isLoading } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!isLoading && user) router.push("/dashboard");
  }, [user, isLoading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  };

  const fillDemo = () => {
    setEmail("demo@voxshield.in");
    setPassword("VoxShieldDemo2026!");
  };

  return (
    <div className="min-h-screen bg-[#06080F] flex items-center justify-center p-4 relative overflow-hidden font-sans">
      {/* Background glow effects */}
      <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none animate-pulse" />
      <div className="absolute bottom-1/4 right-1/3 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-sm relative z-10">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-2">
            <span className="text-2xl">🛡️</span>
            <span className="text-2xl font-extrabold text-white tracking-tight">VoxShield</span>
          </div>
          <p className="text-xs text-slate-400">AI-Powered Voice Scam Protection</p>
        </div>

        {/* Card */}
        <div className="bg-slate-900/80 rounded-2xl shadow-2xl border border-slate-800 backdrop-blur-xl p-6">
          <h1 className="text-lg font-bold text-white mb-6">Sign in to your account</h1>

          {error && (
            <div className="mb-4 p-3 bg-rose-950/80 border border-rose-800 rounded-lg text-xs text-rose-300">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition"
                placeholder="you@example.com"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition font-mono"
                placeholder="••••••••"
                required
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-lg shadow-lg shadow-blue-600/20 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {submitting ? "Signing in..." : "Sign In"}
            </button>
          </form>

          {/* Demo login shortcut */}
          <div className="mt-5 pt-5 border-t border-slate-800">
            <button
              type="button"
              onClick={fillDemo}
              className="w-full py-2 px-4 bg-slate-800/80 border border-slate-700 text-slate-200 text-xs font-semibold rounded-lg hover:bg-slate-800 transition"
            >
              Fill Demo Credentials
            </button>
            <p className="text-[11px] text-slate-500 text-center mt-2 font-mono">
              Demo data — not real user activity
            </p>
          </div>
        </div>

        <p className="text-center text-xs text-slate-400 mt-4">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-blue-400 hover:underline font-medium">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}