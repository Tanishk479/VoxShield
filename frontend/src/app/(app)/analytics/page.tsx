"use client";

import { useEffect, useState } from "react";
import {
  getWeeklyActivity,
  getScamCategories,
  getLanguageBreakdown,
  getTimeHeatmap,
} from "@/lib/api";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { getScamCategoryLabel } from "@/lib/utils";

const COLORS = ["#3b82f6", "#ef4444", "#f59e0b", "#10b981", "#8b5cf6", "#ec4899", "#06b6d4"];

export default function AnalyticsPage() {
  const [weekly, setWeekly] = useState<Awaited<ReturnType<typeof getWeeklyActivity>> | null>(null);
  const [categories, setCategories] = useState<Awaited<ReturnType<typeof getScamCategories>> | null>(null);
  const [languages, setLanguages] = useState<Awaited<ReturnType<typeof getLanguageBreakdown>> | null>(null);
  const [heatmap, setHeatmap] = useState<Awaited<ReturnType<typeof getTimeHeatmap>> | null>(null);
  const [days, setDays] = useState<7 | 30 | 90>(30);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getWeeklyActivity(days),
      getScamCategories(),
      getLanguageBreakdown(),
      getTimeHeatmap(),
    ]).then(([w, c, l, h]) => {
      setWeekly(w);
      setCategories(c);
      setLanguages(l);
      setHeatmap(h);
    }).finally(() => setLoading(false));
  }, [days]);

  return (
    <div className="p-6 md:p-10 max-w-6xl space-y-8 font-sans text-slate-100 selection:bg-blue-500/30">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Analytics & Intelligence</h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1">Detailed breakdown of your voice protection and threat taxonomy</p>
        </div>
        <div className="inline-flex items-center gap-1 bg-amber-950/60 border border-amber-500/40 px-3 py-1 rounded-full text-xs font-mono text-amber-400">
          ⚠ Includes demo data
        </div>
      </div>

      {/* Weekly Activity Card */}
      <div className="bg-slate-900/60 rounded-xl border border-slate-800/90 p-6 shadow-2xl backdrop-blur-xl">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Scam Attempts Over Time</h2>
            <p className="text-xs text-slate-400 mt-0.5">Call volume comparison against flagged extortion attempts</p>
          </div>
          <div className="flex bg-slate-950 border border-slate-800 p-0.5 rounded-lg text-xs font-semibold">
            {([7, 30, 90] as const).map((d) => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={`px-3 py-1 rounded-md transition-all ${
                  days === d
                    ? "bg-blue-600 text-white shadow-md font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {d === 7 ? "7 Days" : d === 30 ? "30 Days" : "90 Days"}
              </button>
            ))}
          </div>
        </div>

        {/* Dynamic Legend */}
        <div className="flex gap-5 mb-4 font-mono text-xs">
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]" />
            <span className="text-slate-300">Total Calls</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-1.5 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]" />
            <span className="text-rose-400 font-semibold">Scam Attempts</span>
          </div>
        </div>

        {loading ? (
          <div className="h-64 flex items-center justify-center text-slate-500 font-mono text-xs">
            Loading trajectory analysis...
          </div>
        ) : (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={weekly?.data || []}
                margin={{ top: 10, right: 10, left: -25, bottom: 0 }}
              >
                <defs>
                  {/* Total Calls Gradient (Electric Blue) */}
                  <linearGradient id="totalCallsGlow" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.0} />
                  </linearGradient>

                  {/* Scam Attempts Gradient (Vibrant Crimson) */}
                  <linearGradient id="scamAttemptsGlow" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#ef4444" stopOpacity={0.45} />
                    <stop offset="100%" stopColor="#ef4444" stopOpacity={0.0} />
                  </linearGradient>
                </defs>

                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />

                <XAxis
                  dataKey="date"
                  stroke="#64748b"
                  fontSize={10}
                  tickLine={false}
                  tickFormatter={(v) => {
                    const d = new Date(v);
                    return isNaN(d.getTime())
                      ? String(v)
                      : days === 7
                      ? d.toLocaleDateString("en-IN", { weekday: "short" })
                      : d.toLocaleDateString("en-IN", { month: "short", day: "numeric" });
                  }}
                  interval={days === 90 ? 6 : days === 30 ? 2 : 0}
                />
                <YAxis stroke="#64748b" fontSize={10} tickLine={false} allowDecimals={false} />

                <Tooltip
                  cursor={{ stroke: "#475569", strokeWidth: 1, strokeDasharray: "4 4" }}
                  contentStyle={{
                    backgroundColor: "#06080F",
                    borderColor: "#1e293b",
                    borderRadius: "10px",
                    boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.7)",
                    fontSize: "12px",
                  }}
                  labelFormatter={(l: any) => {
                    const d = new Date(l);
                    return isNaN(d.getTime())
                      ? String(l)
                      : d.toLocaleDateString("en-IN", { weekday: "short", month: "short", day: "numeric", year: "numeric" });
                  }}
                  formatter={(val: any, name: any) => [
                    val ?? 0,
                    name === "scam" ? "Scam Attempts" : "Total Calls",
                  ]}
                />

                {/* Total Calls Flow Line */}
                <Area
                  type="monotone"
                  dataKey="total"
                  stroke="#3b82f6"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#totalCallsGlow)"
                  isAnimationActive={true}
                  animationDuration={1500}
                  animationEasing="ease-out"
                  activeDot={{ r: 5, fill: "#3b82f6", stroke: "#ffffff", strokeWidth: 2 }}
                />

                {/* Scam Attempts High-Priority Alert Line */}
                <Area
                  type="monotone"
                  dataKey="scam"
                  stroke="#ef4444"
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#scamAttemptsGlow)"
                  isAnimationActive={true}
                  animationDuration={1800}
                  animationEasing="ease-out"
                  activeDot={{ r: 6, fill: "#ef4444", stroke: "#ffffff", strokeWidth: 2 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scam Categories */}
        <div className="bg-slate-900/60 rounded-xl border border-slate-800/90 p-6 shadow-xl backdrop-blur-xl">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Indian Scam Taxonomy Breakdown</h2>
          {categories && categories.categories && categories.categories.length > 0 ? (
            <div>
              <div className="w-[200px] h-[200px] mx-auto">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categories.categories}
                      dataKey="count"
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={85}
                      paddingAngle={3}
                      isAnimationActive={true}
                      animationDuration={1400}
                      animationEasing="ease-out"
                    >
                      {categories.categories.map((_, i) => (
                        <Cell
                          key={i}
                          fill={COLORS[i % COLORS.length]}
                          stroke="#0b0f19"
                          strokeWidth={2}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#06080F",
                        borderColor: "#334155",
                        borderRadius: "8px",
                        fontSize: "12px",
                      }}
                      formatter={(v: any, _n: any, props: any) => [
                        v ?? 0,
                        getScamCategoryLabel(props?.payload?.category ?? ""),
                      ]}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="space-y-2 mt-4">
                {categories.categories.slice(0, 6).map((c, i) => (
                  <div key={c.category} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2 truncate">
                      <div className="w-2 h-2 rounded-full shrink-0" style={{ background: COLORS[i % COLORS.length] }} />
                      <span className="text-slate-300 truncate">{getScamCategoryLabel(c.category)}</span>
                    </div>
                    <span className="font-mono text-white font-bold ml-2">{c.percentage}%</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-slate-500 text-xs font-mono py-12 text-center">No scam categories flagged yet.</p>
          )}
        </div>

        {/* Language & Time Distribution */}
        <div className="space-y-6">
          {/* Language Breakdown */}
          <div className="bg-slate-900/60 rounded-xl border border-slate-800/90 p-6 shadow-xl backdrop-blur-xl">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-3">Linguistic Telemetry</h2>
            {languages && languages.languages && languages.languages.length > 0 ? (
              <div className="space-y-3">
                {languages.languages.map((l, i) => (
                  <div key={l.code}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-300 font-medium">{l.name}</span>
                      <span className="font-mono text-white font-bold">{l.percentage}%</span>
                    </div>
                    <div className="h-1.5 bg-slate-950 rounded-full border border-slate-800">
                      <div
                        className="h-1.5 rounded-full transition-all duration-700 ease-out"
                        style={{ width: `${l.percentage}%`, background: COLORS[i % COLORS.length] }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-xs font-mono py-6 text-center">No language data logged yet.</p>
            )}
          </div>

          {/* Time Heatmap */}
          <div className="bg-slate-900/60 rounded-xl border border-slate-800/90 p-6 shadow-xl backdrop-blur-xl">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-3">Scam Call Timing Activity</h2>
            {heatmap ? (
              <div className="grid grid-cols-2 gap-3">
                {heatmap.periods.map((p) => {
                  const maxScam = Math.max(...heatmap.periods.map((x) => x.scam), 1);
                  const intensity = p.scam / maxScam;
                  return (
                    <div
                      key={p.period}
                      className="rounded-lg p-3 text-center border border-slate-800/70 transition-all hover:scale-[1.02]"
                      style={{ background: `rgba(239, 68, 68, ${0.08 + intensity * 0.25})` }}
                    >
                      <p className="text-xs font-semibold text-slate-300">{p.period}</p>
                      <p className="text-xl font-black text-rose-400 mt-1">{p.scam}</p>
                      <p className="text-[10px] text-slate-400 font-mono">flagged scams</p>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-slate-500 text-xs font-mono py-6 text-center">No timing data recorded.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}