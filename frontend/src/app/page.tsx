"use client";

import React from "react";
import Link from "next/link";
import {
  Shield,
  ArrowRight,
  Radio,
  Lock,
  Sparkles,
  PhoneCall,
  Activity,
  Mic,
  AlertTriangle,
  FileAudio,
  CheckCircle,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#06080F] text-slate-100 font-sans selection:bg-blue-500/30 overflow-x-hidden relative flex flex-col justify-between">
      {/* 1. TOP SPOTLIGHT & CONIC GLOW BEAMS */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[520px] pointer-events-none overflow-hidden z-0">
        {/* Angular Apex Beam */}
        <div
          className="absolute -top-32 left-1/2 -translate-x-1/2 w-[900px] h-[550px] opacity-40 blur-3xl"
          style={{
            background:
              "conic-gradient(from 180deg at 50% 0%, #a855f7 0deg, #3b82f6 55deg, transparent 90deg, transparent 270deg, #ec4899 320deg, #a855f7 360deg)",
          }}
        />
        {/* Subtle Perspective Grid */}
        <div
          className="absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage:
              "linear-gradient(#38bdf8 1px, transparent 1px), linear-gradient(90deg, #38bdf8 1px, transparent 1px)",
            backgroundSize: "48px 48px",
            maskImage: "radial-gradient(ellipse at 50% 0%, black 40%, transparent 80%)",
          }}
        />
      </div>

      {/* NAVIGATION BAR */}
      <header className="relative z-20 w-full max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 shadow-md shadow-blue-500/20">
            <Shield size={16} />
          </div>
          <span className="text-base font-extrabold tracking-tight text-white">VoxShield</span>
        </div>

        <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 border border-slate-800/80 rounded-full px-4 py-1.5 backdrop-blur-md shadow-inner text-xs font-medium text-slate-400">
          <Link href="#features" className="px-3 py-1 hover:text-white transition">Defense Mesh</Link>
          <Link href="#architecture" className="px-3 py-1 hover:text-white transition">Taxonomy</Link>
          <Link href="#capabilities" className="px-3 py-1 hover:text-white transition">Explainable AI</Link>
          <Link href="/live-protection" className="px-3 py-1 hover:text-white transition">Interception SOC</Link>
        </nav>

        <div className="flex items-center gap-3">
          <Link
            href="/login"
            className="text-xs font-semibold text-slate-300 hover:text-white transition px-3 py-1.5"
          >
            Log In
          </Link>
          <Link
            href="/dashboard"
            className="text-xs font-bold text-slate-950 bg-white hover:bg-slate-200 transition px-4 py-2 rounded-full shadow-lg shadow-white/10"
          >
            Access Shield
          </Link>
        </div>
      </header>

      {/* HERO CONTENT SECTION */}
      <main className="relative z-10 w-full max-w-5xl mx-auto px-6 pt-10 pb-20 text-center flex flex-col items-center">
        {/* Floating AI Pill Tag */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-blue-500/30 bg-blue-950/40 backdrop-blur-md text-[11px] font-mono text-blue-300 shadow-lg shadow-blue-500/10 mb-6">
          <Radio size={12} className="text-blue-400 animate-pulse" />
          <span>Real-Time Voice Cloning & Indian Scam Protection</span>
        </div>

        {/* Hero Title */}
        <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-white max-w-4xl leading-[1.1] mb-6">
          Don&apos;t Trust the Voice. <br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-200 to-purple-400">
            Verify the Identity.
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-sm sm:text-base text-slate-400 max-w-2xl leading-relaxed mb-8">
          Next-generation telemetry defense that continuously analyzes telephony streams, flags synthetic audio characteristics in milliseconds, and uncovers extortion intent before transactions occur.
        </p>

        {/* Primary CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-3.5 mb-16">
          <Link
            href="/live-protection"
            className="flex items-center gap-2 px-6 py-3 rounded-full text-xs font-bold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:opacity-95 transition shadow-lg shadow-indigo-600/30 border border-white/20"
          >
            <Mic size={14} /> Start Call Protection
          </Link>
          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-6 py-3 rounded-full text-xs font-bold text-slate-300 bg-slate-900/80 hover:bg-slate-800 hover:text-white transition border border-slate-800"
          >
            Explore SOC Threat Log <ArrowRight size={13} />
          </Link>
        </div>

        {/* 2. THE CONCENTRIC ARC HORIZON WITH FLOATING SENSORS */}
        <div className="relative w-full max-w-4xl h-[420px] flex items-center justify-center">
          {/* Orbital Horizon Arcs */}
          <div className="absolute bottom-[-180px] w-[850px] h-[450px] rounded-[100%] border-t border-purple-500/30 bg-gradient-to-b from-purple-950/20 via-[#06080F]/90 to-[#06080F] pointer-events-none" />
          <div className="absolute bottom-[-120px] w-[650px] h-[340px] rounded-[100%] border-t border-blue-500/40 bg-gradient-to-b from-blue-950/30 via-[#06080F]/90 to-[#06080F] pointer-events-none" />
          <div className="absolute bottom-[-60px] w-[450px] h-[240px] rounded-[100%] border-t border-indigo-400/50 pointer-events-none" />

          {/* Floating Pill Badges Arranged Along Arc Rings */}
          <div className="absolute top-2 left-16 sm:left-28 z-20 flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-purple-500/30 bg-slate-900/80 backdrop-blur-md text-[11px] font-medium text-slate-200 shadow-xl shadow-purple-900/20">
            <Sparkles size={11} className="text-purple-400" />
            <span>Spectra-0 Acoustic Verification</span>
          </div>

          <div className="absolute top-0 right-16 sm:right-28 z-20 flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-blue-500/30 bg-slate-900/80 backdrop-blur-md text-[11px] font-medium text-slate-200 shadow-xl shadow-blue-900/20">
            <Radio size={11} className="text-blue-400" />
            <span>Multilingual Whisper ASR</span>
          </div>

          <div className="absolute top-28 left-4 sm:left-12 z-20 flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-emerald-500/30 bg-slate-900/80 backdrop-blur-md text-[11px] font-medium text-slate-200 shadow-xl shadow-emerald-900/20">
            <CheckCircle size={11} className="text-emerald-400" />
            <span>Digital Arrest Intercept</span>
          </div>

          <div className="absolute top-28 right-4 sm:right-12 z-20 flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-amber-500/30 bg-slate-900/80 backdrop-blur-md text-[11px] font-medium text-slate-200 shadow-xl shadow-amber-900/20">
            <AlertTriangle size={11} className="text-amber-400" />
            <span>UPI Coercion Traps</span>
          </div>

          {/* Central Animated Audio Stream Sphere */}
          <div className="relative z-10 w-28 h-28 rounded-full border border-blue-400/40 bg-gradient-to-tr from-indigo-950 via-slate-950 to-blue-950 flex flex-col items-center justify-center shadow-2xl shadow-blue-500/20">
            <div className="w-20 h-20 rounded-full border border-purple-500/30 flex items-center justify-center animate-pulse">
              <div className="flex items-end gap-1 h-6">
                <span className="w-1 h-3 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-1 h-6 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-1 h-4 bg-indigo-300 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                <span className="w-1 h-7 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: "200ms" }} />
                <span className="w-1 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: "100ms" }} />
              </div>
            </div>
            <span className="text-[9px] font-mono uppercase tracking-widest text-slate-300 mt-1">STREAM SECURE</span>
          </div>

          {/* 3. FROSTED GLASS METRIC CARDS AT THE HORIZON BASE */}
          <div className="absolute -bottom-6 left-6 sm:left-14 w-60 rounded-xl border border-slate-800/90 bg-slate-950/80 backdrop-blur-xl p-3.5 text-left shadow-2xl z-20 hidden sm:block">
            <div className="flex items-center justify-between text-slate-400 text-[11px] mb-1">
              <span>Synthetic Probability</span>
              <span className="text-rose-400 font-mono font-bold">94.2%</span>
            </div>
            <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-amber-500 to-rose-500 w-[94%]" />
            </div>
            <p className="text-[10px] text-slate-500 mt-1.5 font-mono">Signal: Pitch Variance Mismatch</p>
          </div>

          <div className="absolute -bottom-6 right-6 sm:right-14 w-60 rounded-xl border border-slate-800/90 bg-slate-950/80 backdrop-blur-xl p-3.5 text-left shadow-2xl z-20 hidden sm:block">
            <div className="flex items-center justify-between text-slate-400 text-[11px] mb-1">
              <span>Extortion Heuristic</span>
              <span className="text-amber-400 font-mono font-bold">HIGH RISK</span>
            </div>
            <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-blue-500 to-amber-500 w-[78%]" />
            </div>
            <p className="text-[10px] text-slate-500 mt-1.5 font-mono">Matched: &quot;Hospital Urgent UPI&quot;</p>
          </div>
        </div>
      </main>

      {/* BOTTOM FEATURE MATRIX */}
      <footer className="relative z-10 w-full border-t border-slate-900 bg-[#04060A]/80 backdrop-blur-md py-8">
        <div className="max-w-6xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-6 text-left">
          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-white mb-1">
              <Activity size={14} className="text-blue-400" />
              <span>Inference Latency</span>
            </div>
            <p className="text-[11px] text-slate-500">&lt;140ms on standard client hardware</p>
          </div>

          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-white mb-1">
              <Shield size={14} className="text-purple-400" />
              <span>Multilingual Detection</span>
            </div>
            <p className="text-[11px] text-slate-500">Optimized for Hindi, Hinglish & English</p>
          </div>

          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-white mb-1">
              <Lock size={14} className="text-emerald-400" />
              <span>Zero Leakage</span>
            </div>
            <p className="text-[11px] text-slate-500">Isolated edge-first audio computation</p>
          </div>

          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-white mb-1">
              <Sparkles size={14} className="text-amber-400" />
              <span>Explainable AI</span>
            </div>
            <p className="text-[11px] text-slate-500">Contextual warnings and intervention advice</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
