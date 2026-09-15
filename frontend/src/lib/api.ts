// VoxShield — API Client
// All requests go through this module. Never hardcode base URLs.

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

function getAuthHeader(): Record<string, string> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("voxshield_token") : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
      ...(options.headers || {}),
    },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

// ─── Auth ────────────────────────────────────────────────────────────────────

export interface LoginResponse {
  access_token: string;
  user_id: string;
  full_name: string;
  email: string;
  token_type: string;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const form = new URLSearchParams({ username: email, password });
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form.toString(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Login failed" }));
    throw new Error(err.detail);
  }
  return res.json();
}

export async function register(data: {
  email: string;
  full_name: string;
  phone?: string;
  password: string;
}): Promise<LoginResponse> {
  return request("/api/auth/register", { method: "POST", body: JSON.stringify(data) });
}

export async function getMe() {
  return request<{ id: string; email: string; full_name: string; phone?: string }>("/api/auth/me");
}

// ─── Dashboard ───────────────────────────────────────────────────────────────

export async function getDashboardStats() {
  return request<{
    calls_analyzed: number;
    scam_attempts: number;
    high_risk_calls: number;
    calls_blocked: number;
    risk_trend: {
      this_week: number;
      last_week: number;
      change_percent: number;
      direction: string;
    } | null;
  }>("/api/dashboard/stats");
}

export async function getWeeklyActivity(days: 7 | 30 | 90 = 7) {
  return request<{
    days: number;
    data: { date: string; total: number; scam: number; high_risk: number }[];
  }>(`/api/dashboard/weekly-activity?days=${days}`);
}

export async function getScamCategories() {
  return request<{
    categories: { category: string; count: number; percentage: number }[];
    total: number;
  }>("/api/dashboard/scam-categories");
}

export async function getLanguageBreakdown() {
  return request<{
    languages: { code: string; name: string; count: number; percentage: number }[];
    total: number;
  }>("/api/dashboard/language-breakdown");
}

export async function getTimeHeatmap() {
  return request<{
    periods: { period: string; total: number; scam: number }[];
  }>("/api/dashboard/time-heatmap");
}

export async function getSafetyScore() {
  return request<{
    score: number | null;
    factors: string[];
    total_calls: number;
  }>("/api/dashboard/safety-score");
}

// ─── Calls ───────────────────────────────────────────────────────────────────

export async function getCallHistory(limit = 20, offset = 0) {
  return request<{
    calls: {
      id: string;
      caller_number: string | null;
      timestamp: string | null;
      duration_seconds: number | null;
      language: string | null;
      action_taken: string | null;
      is_demo: boolean;
      risk_score: number | null;
      risk_level: string | null;
      scam_category: string | null;
      voice_fake_probability: number | null;
    }[];
    total: number;
  }>(`/api/calls/history?limit=${limit}&offset=${offset}`);
}

export async function getCallDetail(callId: string) {
  return request<{
    call: {
      id: string;
      caller_number: string | null;
      timestamp: string | null;
      duration_seconds: number | null;
      language: string | null;
      action_taken: string | null;
      is_demo: boolean;
    };
    analysis: {
      transcript: string | null;
      voice_fake_probability: number | null;
      voice_label: string | null;
      scam_probability: number | null;
      scam_category: string | null;
      scam_signals: string[];
      financial_request: boolean;
      urgency_detected: boolean;
      risk_score: number | null;
      risk_level: string | null;
      risk_reasons: string[];
      risk_actions: string[];
      risk_components: Record<string, number>;
      total_latency_ms: number | null;
      asr_model: string | null;
      deepfake_model: string | null;
    } | null;
  }>(`/api/calls/${callId}`);
}

export async function analyzeAudio(audioBlob: Blob, callerNumber?: string) {
  const form = new FormData();
  form.append("audio", audioBlob, "recording.wav");
  if (callerNumber) form.append("caller_number", callerNumber);

  const res = await fetch(`${API_BASE}/api/calls/analyze`, {
    method: "POST",
    headers: getAuthHeader(),
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(err.detail);
  }
  return res.json();
}

// ─── Callers ─────────────────────────────────────────────────────────────────

export async function getCallers(limit = 20) {
  return request<{
    callers: {
      caller_number: string;
      total_calls: number;
      last_seen: string | null;
      avg_risk_score: number;
      alert_count: number;
      is_trusted: boolean;
      risk_status: string;
    }[];
  }>(`/api/callers/?limit=${limit}`);
}

export async function getCallerDetail(phoneNumber: string) {
  return request<{
    phone_number: string;
    total_calls: number;
    alert_count: number;
    avg_risk_score: number | null;
    most_common_category: string | null;
    calls: {
      id: string;
      timestamp: string | null;
      duration_seconds: number | null;
      language: string | null;
      action_taken: string | null;
      risk_score: number | null;
      risk_level: string | null;
      scam_category: string | null;
    }[];
  }>(`/api/callers/${encodeURIComponent(phoneNumber)}`);
}

// ─── Health ──────────────────────────────────────────────────────────────────

export async function getHealth() {
  return request<{
    status: string;
    version: string;
    services: Record<string, string | Record<string, string>>;
  }>("/api/health");
}

// ─── WebSocket ───────────────────────────────────────────────────────────────

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export function createAnalysisWebSocket(token: string): WebSocket {
  return new WebSocket(`${WS_BASE}/ws/analyze?token=${token}`);
}
