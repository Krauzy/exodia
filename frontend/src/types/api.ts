export type TargetType = "web" | "api" | "host";
export type ScanStatus = "pending" | "running" | "completed" | "failed" | "canceled";
export type Severity = "info" | "low" | "medium" | "high" | "critical";

export interface HealthStatus {
  status: string;
  app: string;
  version: string;
}

export interface Target {
  id: string;
  name: string;
  target_type: TargetType;
  value: string;
  description: string;
  authorization_scope: string;
  tags: string[];
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ModuleInfo {
  id: string;
  name: string;
  description: string;
  category: string;
  default_severity: Severity;
  parameters: Array<{
    name: string;
    label: string;
    type: string;
    required: boolean;
    default: unknown;
    description: string;
  }>;
}

export interface Finding {
  id: string;
  scan_id: string;
  module_id: string;
  title: string;
  description: string;
  severity: Severity;
  evidence: Record<string, unknown>;
  recommendation: string;
  created_at: string;
}

export interface Scan {
  id: string;
  target_id: string;
  modules: string[];
  status: ScanStatus;
  started_at: string | null;
  finished_at: string | null;
  current_module: string | null;
  risk_score: number;
  authorization_confirmed: boolean;
  created_at: string;
  findings: Finding[];
}

export interface Report {
  id: string;
  scan_id: string;
  format: "html" | "markdown" | "json";
  content: string;
  created_at: string;
}

export interface ScanEvent {
  type: string;
  scan_id: string;
  message: string;
  module_id: string | null;
  payload: Record<string, unknown>;
  timestamp: string;
}

export interface SreProbe {
  name: string;
  status: "pass" | "warn" | "fail";
  detail: string;
  recommendation: string;
}

export interface SreCheckResponse {
  url: string;
  checked_at: string;
  overall_status: "healthy" | "degraded" | "down";
  score: number;
  dns: {
    hostname: string;
    resolved: boolean;
    addresses: string[];
    latency_ms: number;
    error: string | null;
  };
  http: {
    reachable: boolean;
    status_code: number | null;
    final_url: string | null;
    latency_ms: number;
    redirect_count: number;
    content_type: string | null;
    server: string | null;
    error: string | null;
  };
  tls: {
    enabled: boolean;
    valid: boolean;
    protocol: string | null;
    issuer: string | null;
    expires_at: string | null;
    days_remaining: number | null;
    error: string | null;
  } | null;
  probes: SreProbe[];
}

declare global {
  interface Window {
    exodia?: {
      apiBaseUrl: string;
      platform: string;
    };
  }
}
