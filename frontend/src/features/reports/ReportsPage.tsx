import Editor from "@monaco-editor/react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Download, FileJson, FileText } from "lucide-react";
import { useMemo, useState } from "react";

import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Select } from "../../components/ui/Select";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { useReports, useScans } from "../../hooks/useApiQueries";
import { formatDate } from "../../lib/utils";
import { api } from "../../services/api";
import { useAppStore } from "../../store/useAppStore";
import type { Report } from "../../types/api";

type ReportFormat = "html" | "markdown" | "json";

export function ReportsPage() {
  const queryClient = useQueryClient();
  const reports = useReports();
  const scans = useScans();
  const selectedReportId = useAppStore((state) => state.selectedReportId);
  const openReport = useAppStore((state) => state.openReport);
  const [scanId, setScanId] = useState("");
  const [format, setFormat] = useState<ReportFormat>("html");
  const selectedReport = useMemo(
    () => reports.data?.find((report) => report.id === selectedReportId) ?? reports.data?.[0],
    [reports.data, selectedReportId],
  );
  const completedScans = scans.data?.filter((scan) => ["completed", "failed", "canceled"].includes(scan.status)) ?? [];
  const mutation = useMutation({
    mutationFn: () => api.generateReport(scanId, format),
    onSuccess: (report) => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      openReport(report.id);
    },
  });

  return (
    <>
      <SectionHeader
        title="Reports"
        description="Generate authorized-use reports focused on impact, evidence, and mitigation."
      />
      <div className="grid gap-4 xl:grid-cols-[0.7fr_1.3fr]">
        <Card>
          <h2 className="mb-4 text-lg font-semibold text-zinc-50">Generate Report</h2>
          <div className="space-y-4">
            <label className="space-y-2 text-sm text-zinc-300">
              <span>Scan</span>
              <Select value={scanId} onChange={(event) => setScanId(event.target.value)}>
                <option value="">Select scan</option>
                {completedScans.map((scan) => (
                  <option key={scan.id} value={scan.id}>
                    {scan.id.slice(0, 8)} - {scan.status}
                  </option>
                ))}
              </Select>
            </label>
            <label className="space-y-2 text-sm text-zinc-300">
              <span>Format</span>
              <Select value={format} onChange={(event) => setFormat(event.target.value as ReportFormat)}>
                <option value="html">HTML</option>
                <option value="markdown">Markdown</option>
                <option value="json">JSON</option>
              </Select>
            </label>
            {mutation.error ? <p className="text-sm text-red-300">{mutation.error.message}</p> : null}
            <Button className="w-full" disabled={!scanId || mutation.isPending} onClick={() => mutation.mutate()}>
              <FileText className="h-4 w-4" />
              Generate
            </Button>
          </div>

          <div className="mt-6 border-t border-zinc-800 pt-4">
            <h2 className="mb-3 text-lg font-semibold text-zinc-50">History</h2>
            <div className="space-y-2">
              {reports.data?.map((report) => (
                <button
                  key={report.id}
                  onClick={() => openReport(report.id)}
                  className={`w-full rounded-md border p-3 text-left text-sm transition ${
                    report.id === selectedReport?.id
                      ? "border-cyan-400/40 bg-cyan-400/10"
                      : "border-zinc-800 bg-zinc-950 hover:bg-zinc-900"
                  }`}
                >
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-mono text-xs text-zinc-300">{report.id.slice(0, 8)}</span>
                    <Badge>{report.format}</Badge>
                  </div>
                  <div className="text-zinc-500">{formatDate(report.created_at)}</div>
                </button>
              ))}
              {!reports.data?.length ? <p className="text-sm text-zinc-500">No reports generated.</p> : null}
            </div>
          </div>
        </Card>

        <Card className="min-h-[640px]">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <FileJson className="h-4 w-4 text-cyan-300" />
              <h2 className="text-lg font-semibold text-zinc-50">Report Viewer</h2>
            </div>
            {selectedReport ? <DownloadButton report={selectedReport} /> : null}
          </div>
          {selectedReport ? (
            <div className="overflow-hidden rounded-md border border-zinc-800">
              <Editor
                height="560px"
                theme="vs-dark"
                language={selectedReport.format === "json" ? "json" : selectedReport.format === "html" ? "html" : "markdown"}
                value={selectedReport.content}
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  fontSize: 13,
                  wordWrap: "on",
                  scrollBeyondLastLine: false,
                }}
              />
            </div>
          ) : (
            <p className="text-sm text-zinc-400">Select or generate a report.</p>
          )}
        </Card>
      </div>
    </>
  );
}

function DownloadButton({ report }: { report: Report }) {
  function download() {
    const extension = report.format === "markdown" ? "md" : report.format;
    const blob = new Blob([report.content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `exodia-report-${report.id}.${extension}`;
    link.click();
    URL.revokeObjectURL(url);
  }
  return (
    <Button variant="secondary" onClick={download}>
      <Download className="h-4 w-4" />
      Export
    </Button>
  );
}

