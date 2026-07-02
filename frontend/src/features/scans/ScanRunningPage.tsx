import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Ban, CheckCircle2, Terminal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { formatDate } from "../../lib/utils";
import { api, subscribeScanEvents } from "../../services/api";
import { useAppStore } from "../../store/useAppStore";
import type { ScanEvent } from "../../types/api";

export function ScanRunningPage() {
  const queryClient = useQueryClient();
  const selectedScanId = useAppStore((state) => state.selectedScanId);
  const openScan = useAppStore((state) => state.openScan);
  const [events, setEvents] = useState<ScanEvent[]>([]);
  const scan = useQuery({
    queryKey: ["scan", selectedScanId],
    queryFn: () => api.scan(selectedScanId!),
    enabled: Boolean(selectedScanId),
    refetchInterval: 3_000,
  });
  const cancel = useMutation({
    mutationFn: () => api.cancelScan(selectedScanId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scans"] });
      queryClient.invalidateQueries({ queryKey: ["scan", selectedScanId] });
    },
  });

  useEffect(() => {
    if (!selectedScanId) return;
    setEvents([]);
    return subscribeScanEvents(selectedScanId, (event) => {
      setEvents((current) => [...current.slice(-200), event]);
      queryClient.invalidateQueries({ queryKey: ["scan", selectedScanId] });
      queryClient.invalidateQueries({ queryKey: ["scans"] });
    });
  }, [queryClient, selectedScanId]);

  const completedModules = useMemo(
    () => new Set(events.filter((event) => event.type === "module_completed").map((event) => event.module_id)).size,
    [events],
  );
  const totalModules = scan.data?.modules.length ?? 0;
  const progress = totalModules ? Math.min(100, Math.round((completedModules / totalModules) * 100)) : 0;
  const done = scan.data && ["completed", "failed", "canceled"].includes(scan.data.status);

  if (!selectedScanId) {
    return (
      <>
        <SectionHeader title="Scan Running" />
        <Card><p className="text-sm text-zinc-400">No scan selected.</p></Card>
      </>
    );
  }

  return (
    <>
      <SectionHeader
        title="Scan Running"
        description={`Scan ${selectedScanId}`}
        actions={
          <>
            {done ? (
              <Button onClick={() => openScan(selectedScanId)}>
                <CheckCircle2 className="h-4 w-4" />
                View results
              </Button>
            ) : (
              <Button variant="danger" onClick={() => cancel.mutate()} disabled={cancel.isPending}>
                <Ban className="h-4 w-4" />
                Cancel scan
              </Button>
            )}
          </>
        }
      />
      <div className="grid gap-4 xl:grid-cols-[0.7fr_1.3fr]">
        <Card>
          <h2 className="mb-4 text-lg font-semibold text-zinc-50">Progress</h2>
          <div className="mb-3 flex items-center justify-between text-sm">
            <span className="text-zinc-400">Status</span>
            <Badge>{scan.data?.status ?? "loading"}</Badge>
          </div>
          <div className="mb-3 flex items-center justify-between text-sm">
            <span className="text-zinc-400">Current module</span>
            <span className="font-mono text-zinc-200">{scan.data?.current_module ?? "-"}</span>
          </div>
          <div className="mb-4 h-3 overflow-hidden rounded-md bg-zinc-900">
            <div className="h-full bg-cyan-400 transition-all" style={{ width: `${progress}%` }} />
          </div>
          <div className="text-sm text-zinc-400">{completedModules} of {totalModules} modules completed</div>
          <div className="mt-5 border-t border-zinc-800 pt-4">
            <h3 className="mb-3 text-sm font-medium text-zinc-100">Findings</h3>
            <div className="space-y-2">
              {scan.data?.findings.map((finding) => (
                <div key={finding.id} className="rounded-md border border-zinc-800 bg-zinc-950 p-3">
                  <div className="mb-2 flex items-start justify-between gap-2">
                    <span className="text-sm font-medium text-zinc-100">{finding.title}</span>
                    <Badge severity={finding.severity}>{finding.severity}</Badge>
                  </div>
                  <p className="text-xs text-zinc-500">{finding.module_id} - {formatDate(finding.created_at)}</p>
                </div>
              ))}
              {!scan.data?.findings.length ? <p className="text-sm text-zinc-500">No findings detected yet.</p> : null}
            </div>
          </div>
        </Card>

        <Card className="min-h-[520px]">
          <div className="mb-3 flex items-center gap-2">
            <Terminal className="h-4 w-4 text-cyan-300" />
            <h2 className="text-lg font-semibold text-zinc-50">Live Logs</h2>
          </div>
          <div className="h-[460px] overflow-y-auto rounded-md border border-zinc-800 bg-black p-3 font-mono text-[13px] leading-5 tracking-normal text-emerald-100">
            {events.map((event, index) => (
              <div
                key={`${event.timestamp}-${index}`}
                className="grid gap-2 border-b border-zinc-900/80 py-1.5 md:grid-cols-[150px_140px_110px_minmax(0,1fr)]"
              >
                <span className="whitespace-nowrap text-zinc-500">{formatDate(event.timestamp)}</span>
                <span className="whitespace-nowrap text-cyan-200">{event.type}</span>
                <span className="truncate text-zinc-400">{event.module_id ?? "scan"}</span>
                <span className="break-words text-zinc-200">{event.message}</span>
              </div>
            ))}
            {!events.length ? <div className="text-zinc-500">Waiting for scan events...</div> : null}
          </div>
        </Card>
      </div>
    </>
  );
}
