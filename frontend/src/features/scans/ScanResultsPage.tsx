import { FileText, PlayCircle } from "lucide-react";

import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { useScans, useTargets } from "../../hooks/useApiQueries";
import { formatDate } from "../../lib/utils";
import { useAppStore } from "../../store/useAppStore";

export function ScanResultsPage() {
  const scans = useScans();
  const targets = useTargets();
  const selectedScanId = useAppStore((state) => state.selectedScanId);
  const openScan = useAppStore((state) => state.openScan);
  const setView = useAppStore((state) => state.setView);
  const scan = scans.data?.find((item) => item.id === selectedScanId) ?? scans.data?.[0];
  const target = targets.data?.find((item) => item.id === scan?.target_id);

  return (
    <>
      <SectionHeader
        title="Scan Results"
        description="Findings are grouped by scan and normalized with a simple defensive risk score."
        actions={
          <Button onClick={() => setView("new-scan")}>
            <PlayCircle className="h-4 w-4" />
            New scan
          </Button>
        }
      />
      <div className="grid gap-4 xl:grid-cols-[0.7fr_1.3fr]">
        <Card>
          <h2 className="mb-4 text-lg font-semibold text-zinc-50">Scans</h2>
          <div className="space-y-2">
            {scans.data?.map((item) => (
              <button
                key={item.id}
                onClick={() => openScan(item.id)}
                className={`w-full rounded-md border p-3 text-left text-sm transition ${
                  item.id === scan?.id ? "border-cyan-400/40 bg-cyan-400/10" : "border-zinc-800 bg-zinc-950 hover:bg-zinc-900"
                }`}
              >
                <div className="mb-2 flex items-center justify-between gap-2">
                  <span className="font-mono text-xs text-zinc-300">{item.id.slice(0, 8)}</span>
                  <Badge>{item.status}</Badge>
                </div>
                <div className="text-zinc-500">{formatDate(item.created_at)}</div>
              </button>
            ))}
            {!scans.data?.length ? <p className="text-sm text-zinc-500">No scans recorded.</p> : null}
          </div>
        </Card>

        <Card>
          {!scan ? (
            <p className="text-sm text-zinc-400">Run a scan to see results.</p>
          ) : (
            <>
              <div className="mb-4 flex flex-col gap-3 border-b border-zinc-800 pb-4 md:flex-row md:items-start md:justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-zinc-50">{target?.name ?? "Target"}</h2>
                  <p className="font-mono text-xs text-zinc-500">{scan.id}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Badge>{scan.status}</Badge>
                  <Badge>risk {scan.risk_score}</Badge>
                  <Button variant="secondary" onClick={() => setView("reports")}>
                    <FileText className="h-4 w-4" />
                    Reports
                  </Button>
                </div>
              </div>
              <div className="mb-4 grid gap-3 md:grid-cols-3">
                <Stat label="Modules" value={scan.modules.length.toString()} />
                <Stat label="Findings" value={scan.findings.length.toString()} />
                <Stat label="Finished" value={formatDate(scan.finished_at)} />
              </div>
              <div className="space-y-3">
                {scan.findings.map((finding) => (
                  <div key={finding.id} className="rounded-lg border border-zinc-800 bg-zinc-950 p-4">
                    <div className="mb-2 flex items-start justify-between gap-3">
                      <h3 className="font-medium text-zinc-50">{finding.title}</h3>
                      <Badge severity={finding.severity}>{finding.severity}</Badge>
                    </div>
                    <p className="text-sm leading-6 text-zinc-400">{finding.description}</p>
                    <pre className="mt-3 max-h-48 overflow-auto rounded-md border border-zinc-800 bg-black p-3 text-xs text-cyan-100">
                      {JSON.stringify(finding.evidence, null, 2)}
                    </pre>
                    <p className="mt-3 text-sm text-emerald-200">{finding.recommendation}</p>
                  </div>
                ))}
                {!scan.findings.length ? <p className="text-sm text-zinc-500">No findings for this scan.</p> : null}
              </div>
            </>
          )}
        </Card>
      </div>
    </>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-zinc-800 bg-zinc-950 p-3">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="mt-1 text-sm font-medium text-zinc-100">{value}</div>
    </div>
  );
}

