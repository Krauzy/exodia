import type { HealthStatus, ModuleInfo, Report, Scan, ScanEvent, SreCheckResponse, Target } from "../types/api";

const API_BASE =
  window.exodia?.apiBaseUrl || import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8765";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
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
  modules: () => request<ModuleInfo[]>("/modules"),
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
};

export function subscribeScanEvents(scanId: string, onEvent: (event: ScanEvent) => void) {
  const source = new EventSource(`${API_BASE}/events/scans/${scanId}`);
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
