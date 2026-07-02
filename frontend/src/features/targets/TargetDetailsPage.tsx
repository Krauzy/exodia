import { Edit3, PlayCircle } from "lucide-react";

import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { useTargets } from "../../hooks/useApiQueries";
import { formatDate } from "../../lib/utils";
import { useAppStore } from "../../store/useAppStore";
import { TargetForm } from "./TargetForm";

export function TargetDetailsPage() {
  const selectedTargetId = useAppStore((state) => state.selectedTargetId);
  const setView = useAppStore((state) => state.setView);
  const targets = useTargets();
  const target = targets.data?.find((item) => item.id === selectedTargetId);

  if (!target) {
    return (
      <>
        <SectionHeader title="Target Details" />
        <Card>
          <p className="text-sm text-zinc-400">Select a target from the target list.</p>
        </Card>
      </>
    );
  }

  return (
    <>
      <SectionHeader
        title={target.name}
        description={target.value}
        actions={
          <Button onClick={() => setView("new-scan")}>
            <PlayCircle className="h-4 w-4" />
            Scan target
          </Button>
        }
      />
      <div className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-zinc-50">Target Profile</h2>
            <Badge>{target.active ? "active" : "inactive"}</Badge>
          </div>
          <dl className="space-y-3 text-sm">
            <InfoRow label="Type" value={target.target_type} />
            <InfoRow label="Created" value={formatDate(target.created_at)} />
            <InfoRow label="Updated" value={formatDate(target.updated_at)} />
            <div>
              <dt className="text-zinc-500">Tags</dt>
              <dd className="mt-2 flex flex-wrap gap-2">
                {target.tags.map((tag) => <Badge key={tag}>{tag}</Badge>)}
                {!target.tags.length ? <span className="text-zinc-400">No tags</span> : null}
              </dd>
            </div>
            <div>
              <dt className="text-zinc-500">Authorized scope</dt>
              <dd className="mt-1 whitespace-pre-wrap text-zinc-200">{target.authorization_scope}</dd>
            </div>
          </dl>
        </Card>
        <Card>
          <div className="mb-4 flex items-center gap-2">
            <Edit3 className="h-4 w-4 text-cyan-300" />
            <h2 className="text-lg font-semibold text-zinc-50">Edit Target</h2>
          </div>
          <TargetForm target={target} />
        </Card>
      </div>
    </>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-zinc-800 pb-3">
      <dt className="text-zinc-500">{label}</dt>
      <dd className="truncate font-mono text-zinc-200">{value}</dd>
    </div>
  );
}

