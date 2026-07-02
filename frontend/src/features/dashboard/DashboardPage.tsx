import { Activity, AlertTriangle, CheckCircle2, Server, Target } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { useHealth, useModules, useScans, useTargets } from "../../hooks/useApiQueries";
import { formatDate } from "../../lib/utils";

const severityOrder = ["critical", "high", "medium", "low", "info"];

export function DashboardPage() {
  const health = useHealth();
  const targets = useTargets();
  const scans = useScans();
  const modules = useModules();
  const findings = scans.data?.flatMap((scan) => scan.findings) ?? [];
  const severityData = severityOrder.map((severity) => ({
    severity,
    total: findings.filter((finding) => finding.severity === severity).length,
  }));
  const latestScans = scans.data?.slice(0, 5) ?? [];

  return (
    <>
      <SectionHeader
        title="Dashboard"
        description="Local status, authorized targets, scan activity, and defensive finding distribution."
      />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard icon={Target} label="Targets" value={targets.data?.length ?? 0} detail="registered assets" />
        <MetricCard icon={Activity} label="Scans" value={scans.data?.length ?? 0} detail="executions recorded" />
        <MetricCard icon={AlertTriangle} label="Findings" value={findings.length} detail="normalized results" />
        <MetricCard icon={Server} label="Modules" value={modules.data?.length ?? 0} detail="safe checks loaded" />
      </div>

      <div className="mt-5 grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="min-h-80">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-zinc-50">Severity Distribution</h2>
            <Badge>Risk score model</Badge>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={severityData}>
                <CartesianGrid stroke="#27272a" vertical={false} />
                <XAxis dataKey="severity" stroke="#a1a1aa" />
                <YAxis stroke="#a1a1aa" allowDecimals={false} />
                <Tooltip
                  cursor={{ fill: "rgba(34, 211, 238, 0.08)" }}
                  contentStyle={{ background: "#111113", border: "1px solid #3f3f46", borderRadius: 8 }}
                />
                <Bar dataKey="total" fill="#22d3ee" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-zinc-50">Backend</h2>
            <Badge className={health.data?.status === "ok" ? "border-emerald-500/40 text-emerald-200" : ""}>
              {health.data?.status ?? "unknown"}
            </Badge>
          </div>
          <div className="space-y-3 text-sm text-zinc-300">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <span>Application</span>
              <span className="font-mono text-zinc-100">{health.data?.app ?? "Exodia"}</span>
            </div>
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <span>Version</span>
              <span className="font-mono text-zinc-100">{health.data?.version ?? "0.1.0"}</span>
            </div>
            <div className="flex items-center gap-2 rounded-md border border-emerald-500/20 bg-emerald-500/10 p-3 text-emerald-100">
              <CheckCircle2 className="h-4 w-4" />
              Safe mode is the default operating posture.
            </div>
          </div>
        </Card>
      </div>

      <Card className="mt-5">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-zinc-50">Latest Scans</h2>
          <Badge>{latestScans.length} visible</Badge>
        </div>
        <div className="overflow-hidden rounded-md border border-zinc-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-zinc-900 text-xs uppercase text-zinc-500">
              <tr>
                <th className="px-3 py-2">Scan</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Modules</th>
                <th className="px-3 py-2">Risk</th>
                <th className="px-3 py-2">Created</th>
              </tr>
            </thead>
            <tbody>
              {latestScans.map((scan) => (
                <tr key={scan.id} className="border-t border-zinc-800">
                  <td className="px-3 py-2 font-mono text-xs text-zinc-300">{scan.id.slice(0, 8)}</td>
                  <td className="px-3 py-2"><Badge>{scan.status}</Badge></td>
                  <td className="px-3 py-2 text-zinc-400">{scan.modules.join(", ")}</td>
                  <td className="px-3 py-2 text-zinc-100">{scan.risk_score}</td>
                  <td className="px-3 py-2 text-zinc-400">{formatDate(scan.created_at)}</td>
                </tr>
              ))}
              {!latestScans.length ? (
                <tr>
                  <td className="px-3 py-6 text-center text-zinc-500" colSpan={5}>
                    No scans yet.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </Card>
    </>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  detail,
}: {
  icon: typeof Target;
  label: string;
  value: number;
  detail: string;
}) {
  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-zinc-400">{label}</p>
          <p className="mt-2 text-3xl font-semibold text-zinc-50">{value}</p>
          <p className="mt-1 text-xs text-zinc-500">{detail}</p>
        </div>
        <div className="rounded-md border border-zinc-800 bg-zinc-900 p-2">
          <Icon className="h-5 w-5 text-cyan-300" />
        </div>
      </div>
    </Card>
  );
}

