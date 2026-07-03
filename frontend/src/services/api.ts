import type {
  HealthStatus,
  AuthResponse,
  CustomModule,
  ModuleInfo,
  PentestCheckResponse,
  PentestModuleId,
  Report,
  Scan,
  ScanEvent,
  SreCheckResponse,
  Target,
  User,
} from "../types/api";

const RAW_API_BASE = window.exodia?.apiBaseUrl || import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8765";
const API_BASE = RAW_API_BASE.replace(/\/$/, "");
export const AUTH_STORAGE_KEY = "exodia.auth";

interface StoredAuthSession {
  token: string;
  user: User;
}

export function getStoredAuthSession(): StoredAuthSession | undefined {
  const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
  if (!raw) return undefined;
  try {
    return JSON.parse(raw) as StoredAuthSession;
  } catch {
    window.localStorage.removeItem(AUTH_STORAGE_KEY);
    return undefined;
  }
}

export function saveAuthSession(session: StoredAuthSession) {
  window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session));
}

export function clearAuthSession() {
  window.localStorage.removeItem(AUTH_STORAGE_KEY);
}

export function getAuthToken() {
  return getStoredAuthSession()?.token;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers || {}),
    },
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || response.statusText);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const api = {
  baseUrl: API_BASE,
  health: () => request<HealthStatus>("/health"),
  register: (payload: { username: string; password: string }) =>
    request<AuthResponse>("/auth/register", { method: "POST", body: JSON.stringify(payload) }),
  login: (payload: { username: string; password: string }) =>
    request<AuthResponse>("/auth/login", { method: "POST", body: JSON.stringify(payload) }),
  me: () => request<User>("/auth/me"),
  modules: () => request<ModuleInfo[]>("/modules"),
  createModule: (payload: {
    name: string;
    title: string;
    description: string;
    severity: string;
    tags: string[];
    code: string;
  }) => request<CustomModule>("/modules", { method: "POST", body: JSON.stringify(payload) }),
  targets: () => request<Target[]>("/targets"),
  createTarget: (payload: Partial<Target>) =>
    request<Target>("/targets", { method: "POST", body: JSON.stringify(payload) }),
  updateTarget: (id: string, payload: Partial<Target>) =>
    request<Target>(`/targets/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  scans: () => request<Scan[]>("/scans"),
  createScan: (payload: { target_id: string; modules: string[]; authorization_confirmed: boolean }) =>
    request<Scan>("/scans", { method: "POST", body: JSON.stringify(payload) }),
  scan: (id: string) => request<Scan>(`/scans/${id}`),
  cancelScan: (id: string) => request<{ canceled: boolean }>(`/scans/${id}/cancel`, { method: "POST" }),
  reports: () => request<Report[]>("/reports"),
  generateReport: (scanId: string, format: "html" | "markdown" | "json") =>
    request<Report>(`/reports/${scanId}/generate`, {
      method: "POST",
      body: JSON.stringify({ format }),
    }),
  settings: () =>
    request<{
      safe_mode: boolean;
      plugins_dir: string;
      http_timeout_seconds: number;
      max_concurrent_modules: number;
    }>("/settings"),
  updateSettings: (payload: unknown) =>
    request("/settings", { method: "PUT", body: JSON.stringify(payload) }),
  sreCheck: (payload: {
    url: string;
    timeout_seconds: number;
    latency_warning_ms: number;
    authorization_confirmed: boolean;
  }) => request<SreCheckResponse>("/sre/check", { method: "POST", body: JSON.stringify(payload) }),
  pentestCheck: (payload: {
    url: string;
    modules: PentestModuleId[];
    timeout_seconds: number;
    rate_limit_requests: number;
    rate_limit_delay_ms: number;
    cors_probe_origin: string;
    origin_allowlist: string[];
    entity_probe_url?: string;
    entity_control_url?: string;
    authorization_confirmed: boolean;
  }) => request<PentestCheckResponse>("/pentest/check", { method: "POST", body: JSON.stringify(payload) }),
};

export function subscribeScanEvents(scanId: string, onEvent: (event: ScanEvent) => void) {
  const token = getAuthToken();
  const url = new URL(`${API_BASE}/events/scans/${scanId}`);
  if (token) {
    url.searchParams.set("token", token);
  }
  const source = new EventSource(url.toString());
  source.onmessage = (message) => {
    onEvent(JSON.parse(message.data) as ScanEvent);
  };
  const eventTypes = [
    "scan_started",
    "scan_log",
    "module_started",
    "module_completed",
    "finding_detected",
    "scan_completed",
    "scan_failed",
    "scan_canceled",
  ];
  for (const type of eventTypes) {
    source.addEventListener(type, (message) => {
      onEvent(JSON.parse((message as MessageEvent).data) as ScanEvent);
    });
  }
  return () => source.close();
}
