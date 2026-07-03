import { useMutation, useQueryClient } from "@tanstack/react-query";
import { PlayCircle, Search } from "lucide-react";
import { useMemo, useState } from "react";

import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { useModules, useTargets } from "../../hooks/useApiQueries";
import { api } from "../../services/api";
import { useAppStore } from "../../store/useAppStore";

export function NewScanPage() {
  const queryClient = useQueryClient();
  const targets = useTargets();
  const modules = useModules();
  const selectedTargetId = useAppStore((state) => state.selectedTargetId);
  const openScan = useAppStore((state) => state.openScan);
  const [targetId, setTargetId] = useState(selectedTargetId ?? "");
  const [selectedModules, setSelectedModules] = useState<string[]>(["web_headers"]);
  const [moduleQuery, setModuleQuery] = useState("");
  const [authorized, setAuthorized] = useState(false);
  const activeTargets = useMemo(() => targets.data?.filter((target) => target.active) ?? [], [targets.data]);
  const filteredModules = useMemo(() => {
    const needle = moduleQuery.trim().toLowerCase();
    if (!needle) return modules.data ?? [];
    return (modules.data ?? []).filter((module) =>
      [
        module.id,
        module.name,
        module.description,
        module.category,
        module.default_severity,
        ...module.tags,
        ...module.parameters.map((parameter) => parameter.name),
      ]
        .join(" ")
        .toLowerCase()
        .includes(needle),
    );
  }, [moduleQuery, modules.data]);
  const mutation = useMutation({
    mutationFn: () =>
      api.createScan({
        target_id: targetId,
        modules: selectedModules,
        authorization_confirmed: authorized,
      }),
    onSuccess: (scan) => {
      queryClient.invalidateQueries({ queryKey: ["scans"] });
      openScan(scan.id, true);
    },
  });

  function toggleModule(moduleId: string) {
    setSelectedModules((current) =>
      current.includes(moduleId) ? current.filter((item) => item !== moduleId) : [...current, moduleId],
    );
  }

  return (
    <>
      <SectionHeader
        title="New Scan"
        description="Run selected defensive modules only after confirming authorization for the target scope."
      />
      <div className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <h2 className="mb-4 text-lg font-semibold text-zinc-50">Target</h2>
          <label className="space-y-2 text-sm text-zinc-300">
            <span>Authorized target</span>
            <Select value={targetId} onChange={(event) => setTargetId(event.target.value)}>
              <option value="">Select target</option>
              {activeTargets.map((target) => (
                <option key={target.id} value={target.id}>
                  {target.name} - {target.value}
                </option>
              ))}
            </Select>
          </label>
          <label className="mt-4 flex items-start gap-3 rounded-md border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-50">
            <input
              checked={authorized}
              onChange={(event) => setAuthorized(event.target.checked)}
              type="checkbox"
              className="mt-0.5 h-4 w-4 accent-amber-400"
            />
            Confirmo que tenho autorizacao para analisar este alvo.
          </label>
          {mutation.error ? <p className="mt-3 text-sm text-red-300">{mutation.error.message}</p> : null}
          <Button
            className="mt-5 w-full"
            disabled={!targetId || !authorized || selectedModules.length === 0 || mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            <PlayCircle className="h-4 w-4" />
            Start authorized scan
          </Button>
        </Card>

        <Card>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-zinc-50">Modules</h2>
            <Badge>{selectedModules.length} selected</Badge>
          </div>
          <div className="mb-4 flex items-center gap-2">
            <Search className="h-4 w-4 text-cyan-300" />
            <Input
              value={moduleQuery}
              onChange={(event) => setModuleQuery(event.target.value)}
              placeholder="Search modules by name, tag, category, severity, or parameter"
            />
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            {filteredModules.map((module) => {
              const checked = selectedModules.includes(module.id);
              return (
                <button
                  key={module.id}
                  onClick={() => toggleModule(module.id)}
                  className={`rounded-lg border p-4 text-left transition ${
                    checked
                      ? "border-cyan-400/50 bg-cyan-400/10"
                      : "border-zinc-800 bg-zinc-950 hover:border-zinc-700"
                  }`}
                >
                  <div className="mb-2 flex items-start justify-between gap-2">
                    <span className="font-medium text-zinc-100">{module.name}</span>
                    <input checked={checked} readOnly type="checkbox" className="h-4 w-4 accent-cyan-400" />
                  </div>
                  <p className="line-clamp-3 text-sm leading-6 text-zinc-400">{module.description}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Badge>{module.category}</Badge>
                    {module.tags.map((tag) => (
                      <Badge key={tag}>{tag}</Badge>
                    ))}
                    <Badge severity={module.default_severity}>{module.default_severity}</Badge>
                  </div>
                </button>
              );
            })}
            {!filteredModules.length ? (
              <p className="rounded-md border border-zinc-800 bg-zinc-950 p-4 text-sm text-zinc-500 md:col-span-2">
                No modules matched the current search.
              </p>
            ) : null}
          </div>
        </Card>
      </div>
    </>
  );
}
