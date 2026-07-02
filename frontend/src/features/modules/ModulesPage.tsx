import { ShieldCheck } from "lucide-react";

import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { useModules } from "../../hooks/useApiQueries";

export function ModulesPage() {
  const modules = useModules();

  return (
    <>
      <SectionHeader
        title="Modules"
        description="Registered defensive checks. The built-in modules avoid exploitation, evasion, stealth, and destructive behavior."
      />
      <div className="grid gap-4 lg:grid-cols-2">
        {modules.data?.map((module) => (
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
              {module.parameters.map((parameter) => (
                <Badge key={parameter.name}>{parameter.name}</Badge>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </>
  );
}

