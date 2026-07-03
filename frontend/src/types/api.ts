export type TargetType = "web" | "api" | "host";
export type ScanStatus = "pending" | "running" | "completed" | "failed" | "canceled";
export type Severity = "info" | "low" | "medium" | "high" | "critical";
export type PentestModuleId =
  | "rate_limit"
  | "cors_reflection"
  | "jwt_in_url"
  | "entity_enumeration"
  | "clickjacking"
  | "sql_injection"
  | "idor";

export interface HealthStatus {
  status: string;
  app: string;
  version: string;
}

export interface User {
  id: string;
  username: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: "bearer";
  user: User;
}

export interface Target {
  id: string;
  user_id: string | null;
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
  tags: string[];
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

export interface CustomModule {
  id: string;
  module_id: string;
  name: string;
  title: string;
  description: string;
  severity: Severity;
  tags: string[];
  code: string;
  active: boolean;
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
  user_id: string | null;
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
  user_id: string | null;
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

export interface PentestFinding {
  title: string;
  severity: Severity;
  detail: string;
  evidence: Record<string, unknown>;
  recommendation: string;
}

export interface PentestProbe {
  id: PentestModuleId;
  name: string;
  status: "pass" | "warn" | "fail";
  severity: Severity;
  summary: string;
  latency_ms: number;
  evidence: Record<string, unknown>;
  findings: PentestFinding[];
}

export interface PentestCheckResponse {
  url: string;
  checked_at: string;
  score: number;
  overall_risk: Severity;
  probes: PentestProbe[];
}

declare global {
  interface Window {
    exodia?: {
      apiBaseUrl: string;
      platform: string;
    };
  }
}
