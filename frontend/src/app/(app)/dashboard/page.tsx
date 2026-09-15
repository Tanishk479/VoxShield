"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import {
  getDashboardStats,
  getWeeklyActivity,
  getScamCategories,
  getLanguageBreakdown,
  getTimeHeatmap,
  getSafetyScore,
} from "@/lib/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  CartesianGrid,
} from "recharts";
import { getScamCategoryLabel } from "@/lib/utils";
import {
  ShieldAlert,
  ShieldCheck,
  PhoneCall,
  AlertTriangle,
  Radio,
  ArrowUpRight,
  Sparkles,
  Zap,
  Users,
  BookOpen,
  Clock,
  Activity,
  CheckCircle2,
} from "lucide-react";

const CHART_COLORS = [
  "#3b82f6", // Electric Blue
  "#ef4444", // Crimson Red
  "#f59e0b", // Bright Amber
  "#10b981", // Emerald Green
  "#8b5cf6", // Violet
  "#ec4899", // Neon Pink
];

function StatCard({
  label,
  value,
  sub,
  icon: Icon,
  accentColor,
}: {
  label: string;
  value: number | string;
  sub?: string;
  icon: any;
  accentColor: "blue" | "amber" | "rose" | "emerald";
}) {
  const colorMap = {
    blue: "text-blue-400 border-blue-500/30 hover:border-blue-500/60 bg-blue-950/10",
    amber: "text-amber-400 border-amber-500/30 hover:border-amber-500/60 bg-amber-950/10",
    rose: "text-rose-400 border-rose-500/30 hover:border-rose-500/60 bg-rose-950/10",
    emerald: "text-emerald-400 border-emerald-500/30 hover:border-emerald-500/60 bg-emerald-950/10",
  };

  return (
    <div
      className={`relative group overflow-hidden rounded-xl border border-slate-800/80 backdrop-blur-xl p-5 transition-all duration-300 shadow-xl ${colorMap[accentColor]}`}
    >
      <div className="flex justify-between items-center text-slate-400 text-xs font-semibold mb-2">
        <span>{label}</span>
        <Icon
          size={16}
          className={`${colorMap[accentColor].split(" ")[0]} group-hover:scale-110 transition-transform`}
        />
      </div>
      <p className={`text-3xl font-black tracking-tight ${colorMap[accentColor].split(" ")[0]}`}>
        {value}
      </p>
      {sub && <p className="text-[11px] text-slate-500 mt-1 font-mono">{sub}</p>}
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<Awaited<ReturnType<typeof getDashboardStats>> | null>(null);
  const [weekly, setWeekly] = useState<Awaited<ReturnType<typeof getWeeklyActivity>> | null>(null);
  const [categories, setCategories] = useState<Awaited<ReturnType<typeof getScamCategories>> | null>(null);
  const [languages, setLanguages] = useState<Awaited<ReturnType<typeof getLanguageBreakdown>> | null>(null);
  const [heatmap, setHeatmap] = useState<Awaited<ReturnType<typeof getTimeHeatmap>> | null>(null);
  const [safetyScore, setSafetyScore] = useState<Awaited<ReturnType<typeof getSafetyScore>> | null>(null);
  const [weeklyDays, setWeeklyDays] = useState<7 | 30 | 90>(7);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getDashboardStats(),
      getWeeklyActivity(weeklyDays),
      getScamCategories(),
      getLanguageBreakdown(),
      getTimeHeatmap(),
      getSafetyScore(),
    ])
      .then(([s, w, c, l, h, ss]) => {
        setStats(s);
        setWeekly(w);
        setCategories(c);
        setLanguages(l);
        setHeatmap(h);
        setSafetyScore(ss);
      })
      .finally(() => setLoading(false));
  }, [weeklyDays]);

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  if (loading) {
    return (
      <div className="min-h-screen bg-[#06080F] flex items-center justify-center text-slate-400 text-sm font-mono">
        <Activity className="animate-spin text-blue-500 mr-2" size={18} /> Initializing VoxShield Operations Center...
      </div>
    );
  }

  const trend = stats?.risk_trend;

  return (
    <div className="min-h-screen bg-[#06080F] text-slate-100 p-4 md:p-8 font-sans relative overflow-hidden selection:bg-blue-500/30 space-y-8">
      {/* Background Animated Glow Mesh */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none animate-pulse" />
      <div className="absolute top-1/3 right-10 w-96 h-96 bg-rose-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800/80 pb-6 relative z-10">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-ping" />
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
              {greeting}, {user?.full_name?.split(" ")[0] || "Operator"} 👋
            </h1>
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800/80 text-amber-400 border border-amber-500/30 flex items-center gap-1">
              <Sparkles size={11} /> DEMO DATA
            </span>
          </div>
          <p className="text-xs md:text-sm text-slate-400 mt-1 flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-400" />
            VoxShield Real-Time Defense Interceptor Active
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-lg shadow-inner">
            <Radio size={14} className="text-emerald-400 animate-pulse" />
            <div className="flex items-end gap-0.5 h-3">
              <span className="w-0.5 h-1.5 bg-emerald-500 animate-bounce" style={{ animationDelay: "0ms" }} />
              <span className="w-0.5 h-3 bg-emerald-400 animate-bounce" style={{ animationDelay: "150ms" }} />
              <span className="w-0.5 h-2 bg-emerald-500 animate-bounce" style={{ animationDelay: "300ms" }} />
            </div>
            <span className="text-[11px] font-mono text-emerald-400 font-semibold uppercase ml-1">Live Engine</span>
          </div>

          <Link
            href="/live-protection"
            className="group relative inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 transition-all shadow-lg shadow-blue-500/25 border border-blue-400/20"
          >
            <Zap size={14} className="text-blue-200 fill-blue-200" />
            Start Live Protection
            <ArrowUpRight size={14} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
          </Link>
        </div>
      </header>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 relative z-10">
        <StatCard
          label="Calls Analyzed"
          value={stats?.calls_analyzed ?? 0}
          sub="All intercepted streams"
          icon={PhoneCall}
          accentColor="blue"
        />
        <StatCard
          label="Scam Attempts"
          value={stats?.scam_attempts ?? 0}
          sub="Caution or higher"
          icon={AlertTriangle}
          accentColor="amber"
        />
        <StatCard
          label="High Risk Calls"
          value={stats?.high_risk_calls ?? 0}
          sub="Critical extortion threats"
          icon={ShieldAlert}
          accentColor="rose"
        />
        <StatCard
          label="Threats Blocked"
          value={stats?.calls_blocked ?? 0}
          sub="Automated intervention"
          icon={ShieldCheck}
          accentColor="emerald"
        />
      </div>

      {/* Safety Score Radar + Risk Trend Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 relative z-10">
        {/* Safety Score Card with Radar Sweep */}
        <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 backdrop-blur-xl p-6 shadow-2xl flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center">
              <h2 className="text-sm font-bold text-white">VoxShield Safety Score</h2>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 border border-emerald-800/80 px-2 py-0.5 rounded-full">
                OPTIMAL
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">Composite telemetry safety level</p>
          </div>

          <div className="relative flex items-center justify-center my-6">
            <div className="w-40 h-40 rounded-full border border-slate-800 relative flex items-center justify-center">
              <div className="w-28 h-28 rounded-full border border-slate-800/60 flex items-center justify-center" />
              <div className="w-16 h-16 rounded-full border border-slate-800/40 flex items-center justify-center" />
              <div
                className="absolute inset-0 rounded-full pointer-events-none animate-spin"
                style={{
                  animationDuration: "4s",
                  background: "conic-gradient(from 0deg, transparent 70%, rgba(59, 130, 246, 0.3) 100%)",
                }}
              />
              <div className="absolute flex flex-col items-center justify-center z-10">
                <span className="text-4xl font-black tracking-tight text-white">
                  {safetyScore?.score !== null && safetyScore?.score !== undefined ? safetyScore.score : "--"}
                </span>
                <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">/ 100</span>
              </div>
            </div>
          </div>

          <div className="space-y-1.5 border-t border-slate-800/80 pt-4">
            {safetyScore?.factors && safetyScore.factors.length > 0 ? (
              safetyScore.factors.slice(0, 3).map((f, i) => (
                <p key={i} className="text-xs text-slate-300 flex items-center gap-1.5 font-medium">
                  <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                  <span className="truncate">{f}</span>
                </p>
              ))
            ) : (
              <p className="text-slate-500 text-xs font-mono">Run analysis to populate health factors</p>
            )}
          </div>
        </div>

        {/* Risk Trend Bar Chart */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800/80 bg-slate-900/50 backdrop-blur-xl p-6 shadow-2xl flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-sm font-bold text-white">Threat Activity Trajectory</h2>
                <p className="text-xs text-slate-400">Total volume vs. identified scam streams</p>
              </div>
              <div className="flex items-center bg-slate-950 border border-slate-800 p-0.5 rounded-lg text-xs font-semibold">
                {([7, 30, 90] as const).map((d) => (
                  <button
                    key={d}
                    onClick={() => setWeeklyDays(d)}
                    className={`px-3 py-1 rounded-md transition-all ${
                      weeklyDays === d ? "bg-blue-600 text-white shadow-md" : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {d}D
                  </button>
                ))}
              </div>
            </div>

            {trend && (
              <div className="flex gap-6 mb-4 bg-slate-950/60 border border-slate-800/80 p-3 rounded-lg">
                <div>
                  <p className="text-[10px] uppercase font-mono text-slate-500">This week</p>
                  <p className="text-lg font-bold text-white">{trend.this_week}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase font-mono text-slate-500">Last week</p>
                  <p className="text-lg font-bold text-slate-400">{trend.last_week}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase font-mono text-slate-500">Trajectory</p>
                  <p className={`text-lg font-bold ${trend.direction === "down" ? "text-emerald-400" : "text-rose-400"}`}>
                    {trend.direction === "down" ? "↓" : "↑"} {Math.abs(trend.change_percent)}%
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weekly?.data || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis
                  dataKey="date"
                  stroke="#64748b"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(v) => {
                    const parsed = new Date(v);
                    return isNaN(parsed.getTime()) ? v : parsed.toLocaleDateString("en-IN", { weekday: "short" });
                  }}
                />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} allowDecimals={false} />
                <Tooltip
                  cursor={{ fill: "rgba(255, 255, 255, 0.04)" }}
                  contentStyle={{
                    backgroundColor: "#0b0f19",
                    borderColor: "#1e293b",
                    borderRadius: "8px",
                    boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.5)",
                  }}
                  // @ts-ignore
                  formatter={(val: number, name: string) => [val, name === "scam" ? "Scam Calls" : "Total Calls"]}
                  // @ts-ignore
                  labelFormatter={(l) => {
                    const parsed = new Date(String(l));
                    return isNaN(parsed.getTime()) ? String(l) : parsed.toLocaleDateString("en-IN", { month: "short", day: "numeric" });
                  }}
                />
                <Bar
                  dataKey="total"
                  fill="#3b82f6"
                  radius={[4, 4, 0, 0]}
                  isAnimationActive={true}
                  animationDuration={1200}
                  animationEasing="ease-out"
                />
                <Bar
                  dataKey="scam"
                  fill="#ef4444"
                  radius={[4, 4, 0, 0]}
                  isAnimationActive={true}
                  animationDuration={1500}
                  animationEasing="ease-out"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Scam Categories + Language Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative z-10">
        {/* Scam Categories Pie */}
        <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 backdrop-blur-xl p-5 shadow-xl">
          <h2 className="text-sm font-semibold text-white mb-4">Indian Scam Taxonomy Breakdown</h2>
          {categories && categories.categories && categories.categories.length > 0 ? (
            <div className="flex items-center gap-4">
              <div className="w-[160px] h-[160px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categories.categories}
                      dataKey="count"
                      nameKey="category"
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={70}
                      paddingAngle={3}
                      isAnimationActive={true}
                      animationDuration={1400}
                      animationEasing="ease-out"
                    >
                      {categories.categories.map((_, i) => (
                        <Cell
                          key={`cell-${i}`}
                          fill={CHART_COLORS[i % CHART_COLORS.length]}
                          stroke="#0b0f19"
                          strokeWidth={2}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#0b0f19",
                        borderColor: "#1e293b",
                        borderRadius: "8px",
                      }}
                      // @ts-ignore
                      formatter={(val: number, name: string) => [val, getScamCategoryLabel(name)]}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="space-y-2 flex-1">
                {categories.categories.slice(0, 5).map((c, i) => (
                  <div key={c.category} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1.5 truncate">
                      <div
                        className="w-2.5 h-2.5 rounded-sm shrink-0"
                        style={{ background: CHART_COLORS[i % CHART_COLORS.length] }}
                      />
                      <span className="text-slate-300 truncate">{getScamCategoryLabel(c.category)}</span>
                    </div>
                    <span className="font-mono text-white font-semibold ml-2">{c.percentage}%</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-32 flex items-center justify-center">
              <p className="text-slate-500 text-xs font-mono">No category events captured</p>
            </div>
          )}
        </div>

        {/* Language Breakdown */}
        <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 backdrop-blur-xl p-5 shadow-xl">
          <h2 className="text-sm font-semibold text-white mb-4">Linguistic Ingestion Metrics</h2>
          {languages && languages.languages && languages.languages.length > 0 ? (
            <div className="space-y-3">
              {languages.languages.map((l, i) => (
                <div key={l.code}>
                  <div className="flex items-center justify-between mb-1 text-xs">
                    <span className="text-slate-300 font-medium">{l.name}</span>
                    <span className="font-mono text-white font-semibold">{l.percentage}%</span>
                  </div>
                  <div className="h-1.5 bg-slate-950 rounded-full border border-slate-800">
                    <div
                      className="h-1.5 rounded-full transition-all duration-700 ease-out"
                      style={{
                        width: `${l.percentage}%`,
                        background: CHART_COLORS[i % CHART_COLORS.length],
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="h-32 flex items-center justify-center">
              <p className="text-slate-500 text-xs font-mono">No linguistic data logged</p>
            </div>
          )}
        </div>
      </div>

      {/* Time Heatmap */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 backdrop-blur-xl p-5 shadow-xl relative z-10">
        <h2 className="text-sm font-semibold text-white mb-4">Extortion Attack Vectors by Hour</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {heatmap?.periods.map((p) => {
            const maxVal = Math.max(...(heatmap.periods.map((x) => x.scam) || [1]), 1);
            const intensity = p.scam > 0 ? Math.min(1, p.scam / maxVal) : 0;
            return (
              <div
                key={p.period}
                className="rounded-lg p-3 text-center border border-slate-800/60 transition-all hover:scale-[1.02]"
                style={{
                  background: `rgba(239, 68, 68, ${0.08 + intensity * 0.25})`,
                }}
              >
                <p className="text-xs font-semibold text-slate-300">{p.period}</p>
                <p className="text-2xl font-black text-rose-400 mt-1">{p.scam}</p>
                <p className="text-[10px] text-slate-400 font-mono">flagged calls</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Access Tiles */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 relative z-10">
        <Link
          href="/call-history"
          className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-4 hover:border-blue-500/50 hover:bg-slate-800/40 transition-all flex items-center gap-3"
        >
          <div className="p-2.5 rounded-lg bg-blue-950/80 border border-blue-800/60 text-blue-400">
            <Clock size={18} />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Call Records Archive</p>
            <p className="text-[11px] text-slate-400">Inspect deepfake confidence logs</p>
          </div>
        </Link>
        <Link
          href="/callers"
          className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-4 hover:border-amber-500/50 hover:bg-slate-800/40 transition-all flex items-center gap-3"
        >
          <div className="p-2.5 rounded-lg bg-amber-950/80 border border-amber-800/60 text-amber-400">
            <Users size={18} />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Caller Intelligence</p>
            <p className="text-[11px] text-slate-400">Scam profiling per telephone ID</p>
          </div>
        </Link>
        <Link
          href="/safety-center"
          className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-4 hover:border-emerald-500/50 hover:bg-slate-800/40 transition-all flex items-center gap-3"
        >
          <div className="p-2.5 rounded-lg bg-emerald-950/80 border border-emerald-800/60 text-emerald-400">
            <BookOpen size={18} />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Safety Intelligence</p>
            <p className="text-[11px] text-slate-400">Digital Arrest & UPI playbooks</p>
          </div>
        </Link>
      </div>
    </div>
  );
}