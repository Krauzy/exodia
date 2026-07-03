import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Search, ShieldCheck } from "lucide-react";
import { useMemo, useState } from "react";

import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input, Textarea } from "../../components/ui/Input";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { Select } from "../../components/ui/Select";
import { useModules } from "../../hooks/useApiQueries";
import { api } from "../../services/api";
import type { Severity } from "../../types/api";

const defaultCode = `def analyze(request, response):
    findings = []
    if response.status_code >= 500:
        findings.append({
            "title": "Server error observed",
            "description": "The intercepted response returned a 5xx status code.",
            "severity": "medium",
            "evidence": {"status_code": response.status_code, "url": response.url},
            "recommendation": "Review application logs and upstream dependencies for this endpoint."
        })
    return findings
`;

const severities: Severity[] = ["info", "low", "medium", "high", "critical"];

interface CustomModuleForm {
  name: string;
  title: string;
  description: string;
  severity: Severity;
  tags: string;
  code: string;
}

const emptyForm: CustomModuleForm = {
  name: "",
  title: "",
  description: "",
  severity: "info",
  tags: "CUSTOM",
  code: defaultCode,
};

export function ModulesPage() {
  const queryClient = useQueryClient();
  const modules = useModules();
  const [query, setQuery] = useState("");
  const [form, setForm] = useState<CustomModuleForm>(emptyForm);
  const createModule = useMutation({
    mutationFn: () =>
      api.createModule({
        name: form.name,
        title: form.title,
        description: form.description,
        severity: form.severity,
        tags: parseTags(form.tags),
        code: form.code,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["modules"] });
      setForm(emptyForm);
    },
  });
  const filteredModules = useMemo(() => {
    const needle = query.trim().toLowerCase();
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
  }, [modules.data, query]);

  function updateForm<K extends keyof CustomModuleForm>(key: K, value: CustomModuleForm[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  return (
    <>
      <SectionHeader
        title="Modules"
        description="Registered defensive checks and user-defined interceptor modules."
      />
      <div className="mb-4 grid gap-4 xl:grid-cols-[0.78fr_1.22fr]">
        <Card>
          <div className="mb-4 flex items-center gap-2">
            <Plus className="h-4 w-4 text-cyan-300" />
            <h2 className="text-lg font-semibold text-zinc-50">Create Module</h2>
          </div>
          <div className="space-y-4">
            <div className="grid gap-3 md:grid-cols-2">
              <label className="space-y-2 text-sm text-zinc-300">
                <span>Name</span>
                <Input
                  value={form.name}
                  onChange={(event) => updateForm("name", event.target.value)}
                  placeholder="server-error-check"
                />
              </label>
              <label className="space-y-2 text-sm text-zinc-300">
                <span>Title</span>
                <Input
                  value={form.title}
                  onChange={(event) => updateForm("title", event.target.value)}
                  placeholder="Server Error Check"
                />
              </label>
            </div>
            <label className="space-y-2 text-sm text-zinc-300">
              <span>Description</span>
              <Textarea
                value={form.description}
                onChange={(event) => updateForm("description", event.target.value)}
                placeholder="Checks intercepted responses for application error signals."
              />
            </label>
            <div className="grid gap-3 md:grid-cols-2">
              <label className="space-y-2 text-sm text-zinc-300">
                <span>Severity</span>
                <Select value={form.severity} onChange={(event) => updateForm("severity", event.target.value as Severity)}>
                  {severities.map((severity) => (
                    <option key={severity} value={severity}>
                      {severity}
                    </option>
                  ))}
                </Select>
              </label>
              <label className="space-y-2 text-sm text-zinc-300">
                <span>Tags</span>
                <Input
                  value={form.tags}
                  onChange={(event) => updateForm("tags", event.target.value)}
                  placeholder="CUSTOM, API"
                />
              </label>
            </div>
            <label className="space-y-2 text-sm text-zinc-300">
              <span>Interceptor code</span>
              <Textarea
                className="min-h-64 font-mono text-[13px] leading-5"
                value={form.code}
                onChange={(event) => updateForm("code", event.target.value)}
                spellCheck={false}
              />
            </label>
            {createModule.error ? <p className="text-sm text-red-300">{createModule.error.message}</p> : null}
            <Button
              className="w-full"
              disabled={!form.name || !form.title || !form.description || !form.code || createModule.isPending}
              onClick={() => createModule.mutate()}
            >
              <Plus className="h-4 w-4" />
              {createModule.isPending ? "Creating..." : "Create interceptor module"}
            </Button>
          </div>
        </Card>

        <Card>
          <div className="mb-4 flex items-center gap-2">
            <Search className="h-4 w-4 text-cyan-300" />
            <h2 className="text-lg font-semibold text-zinc-50">Module Search</h2>
          </div>
          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search by name, tag, severity, category, or parameter"
          />
          <div className="mt-3 flex flex-wrap gap-2 text-sm text-zinc-400">
            <Badge>{filteredModules.length} visible</Badge>
            <Badge>{modules.data?.length ?? 0} registered</Badge>
          </div>
          <p className="mt-4 text-sm leading-6 text-zinc-400">
            Custom code must define <span className="font-mono text-zinc-200">analyze(request, response)</span> and
            return finding dictionaries. The backend validates the function before saving it.
          </p>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {filteredModules.map((module) => (
          <Card key={module.id}>
            <div className="mb-3 flex items-start justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="rounded-md border border-cyan-400/30 bg-cyan-400/10 p-2">
                  <ShieldCheck className="h-5 w-5 text-cyan-200" />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-zinc-50">{module.name}</h2>
                  <p className="font-mono text-xs text-zinc-500">{module.id}</p>
                </div>
              </div>
              <Badge severity={module.default_severity}>{module.default_severity}</Badge>
            </div>
            <p className="text-sm leading-6 text-zinc-400">{module.description}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Badge>{module.category}</Badge>
              {module.tags.map((tag) => (
                <Badge key={tag}>{tag}</Badge>
              ))}
              {module.parameters.map((parameter) => (
                <Badge key={parameter.name}>{parameter.name}</Badge>
              ))}
            </div>
          </Card>
        ))}
        {!filteredModules.length ? (
          <Card className="lg:col-span-2">
            <p className="text-center text-sm text-zinc-500">No modules matched the current search.</p>
          </Card>
        ) : null}
      </div>
    </>
  );
}

function parseTags(value: string) {
  return value
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}
