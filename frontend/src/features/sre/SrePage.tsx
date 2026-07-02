import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { Activity, Clock, Globe2, LockKeyhole, Radar, ShieldCheck } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { formatDate } from "../../lib/utils";
import { api } from "../../services/api";
import type { SreCheckResponse, SreProbe } from "../../types/api";

const sreSchema = z.object({
  url: z.string().url().refine((value) => value.startsWith("http://") || value.startsWith("https://"), {
    message: "Use http:// or https://",
  }),
  timeout_seconds: z.coerce.number().min(1).max(30),
  latency_warning_ms: z.coerce.number().min(100).max(10000),
  authorization_confirmed: z.boolean().refine(Boolean, {
    message: "Authorization confirmation is required.",
  }),
});

type SreFormValues = z.infer<typeof sreSchema>;

export function SrePage() {
  const { register, handleSubmit, formState } = useForm<SreFormValues>({
    resolver: zodResolver(sreSchema),
    defaultValues: {
      url: "https://example.com",
      timeout_seconds: 8,
      latency_warning_ms: 1000,
      authorization_confirmed: false,
    },
  });
  const mutation = useMutation({
    mutationFn: (values: SreFormValues) => api.sreCheck(values),
  });
  const result = mutation.data;

  return (
    <>
      <SectionHeader
        title="SRE Check"
        description="Passive availability, latency, DNS, redirect, and TLS verification for authorized sites."
      />
      <div className="grid gap-4 xl:grid-cols-[0.72fr_1.28fr]">
        <Card>
          <div className="mb-4 flex items-center gap-2">
            <Radar className="h-4 w-4 text-cyan-300" />
            <h2 className="text-lg font-semibold text-zinc-50">Site Probe</h2>
          </div>
          <form className="space-y-4" onSubmit={handleSubmit((values) => mutation.mutate(values))}>
            <label className="space-y-2 text-sm text-zinc-300">
              <span>Site URL</span>
              <Input {...register("url")} placeholder="https://status.example.com" />
              {formState.errors.url ? <FieldError message={formState.errors.url.message} /> : null}
            </label>
            <div className="grid gap-3 md:grid-cols-2">
              <label className="space-y-2 text-sm text-zinc-300">
                <span>Timeout seconds</span>
                <Input type="number" step="0.5" {...register("timeout_seconds")} />
              </label>
              <label className="space-y-2 text-sm text-zinc-300">
                <span>Latency warning ms</span>
                <Input type="number" step="50" {...register("latency_warning_ms")} />
              </label>
            </div>
            <label className="flex items-start gap-3 rounded-md border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-50">
              <input
                type="checkbox"
                className="mt-0.5 h-4 w-4 accent-amber-400"
                {...register("authorization_confirmed")}
              />
              Confirmo que tenho autorizacao para verificar este site ou sou responsavel pelo servico.
            </label>
            {formState.errors.authorization_confirmed ? (
              <FieldError message={formState.errors.authorization_confirmed.message} />
            ) : null}
            {mutation.error ? <p className="text-sm text-red-300">{mutation.error.message}</p> : null}
            <Button className="w-full" type="submit" disabled={mutation.isPending}>
              <Activity className="h-4 w-4" />
              {mutation.isPending ? "Checking..." : "Run SRE check"}
            </Button>
          </form>
        </Card>

        <div className="space-y-4">
          {result ? <Summary result={result} /> : <EmptyState />}
          {result ? <ProbeList probes={result.probes} /> : null}
        </div>
      </div>
    </>
  );
}

function EmptyState() {
  return (
    <Card>
      <div className="flex items-start gap-3">
        <div className="rounded-md border border-cyan-400/30 bg-cyan-400/10 p-2">
          <ShieldCheck className="h-5 w-5 text-cyan-200" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-zinc-50">No check executed</h2>
          <p className="mt-2 text-sm leading-6 text-zinc-400">
            The SRE check performs a single controlled request, DNS resolution, redirect observation,
            and TLS certificate health check for HTTP(S) services.
          </p>
        </div>
      </div>
    </Card>
  );
}

function Summary({ result }: { result: SreCheckResponse }) {
  return (
    <Card>
      <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-zinc-50">{result.url}</h2>
          <p className="text-xs text-zinc-500">{formatDate(result.checked_at)}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusBadge status={result.overall_status} />
          <Badge>score {result.score}</Badge>
        </div>
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        <SignalCard
          icon={Globe2}
          label="DNS"
          value={result.dns.resolved ? `${result.dns.addresses.length} address(es)` : "failed"}
          detail={`${result.dns.latency_ms} ms`}
        />
        <SignalCard
          icon={Clock}
          label="HTTP"
          value={result.http.status_code ? `HTTP ${result.http.status_code}` : "unreachable"}
          detail={`${result.http.latency_ms} ms`}
        />
        <SignalCard
          icon={LockKeyhole}
          label="TLS"
          value={result.tls ? (result.tls.valid ? result.tls.protocol ?? "valid" : "invalid") : "not https"}
          detail={
            result.tls?.days_remaining !== null && result.tls?.days_remaining !== undefined
              ? `${result.tls.days_remaining} days left`
              : result.tls?.issuer ?? "-"
          }
        />
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <InfoLine label="Final URL" value={result.http.final_url ?? "-"} />
        <InfoLine label="Redirects" value={String(result.http.redirect_count)} />
        <InfoLine label="Content-Type" value={result.http.content_type ?? "-"} />
        <InfoLine label="Server" value={result.http.server ?? "-"} />
      </div>
    </Card>
  );
}

function ProbeList({ probes }: { probes: SreProbe[] }) {
  return (
    <Card>
      <h2 className="mb-4 text-lg font-semibold text-zinc-50">Operational Probes</h2>
      <div className="space-y-3">
        {probes.map((probe) => (
          <div key={probe.name} className="rounded-md border border-zinc-800 bg-zinc-950 p-4">
            <div className="mb-2 flex items-start justify-between gap-3">
              <h3 className="font-medium text-zinc-100">{probe.name}</h3>
              <ProbeBadge status={probe.status} />
            </div>
            <p className="text-sm text-zinc-400">{probe.detail}</p>
            <p className="mt-2 text-sm text-emerald-200">{probe.recommendation}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}

function SignalCard({
  icon: Icon,
  label,
  value,
  detail,
}: {
  icon: typeof Globe2;
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="rounded-md border border-zinc-800 bg-zinc-950 p-4">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-[11px] font-medium uppercase text-zinc-500">{label}</span>
        <Icon className="h-4 w-4 text-cyan-300" />
      </div>
      <div className="truncate text-base font-semibold text-zinc-50">{value}</div>
      <div className="mt-1 truncate text-sm text-zinc-400">{detail}</div>
    </div>
  );
}

function InfoLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-zinc-800 bg-zinc-950 p-4">
      <div className="text-[11px] font-medium uppercase text-zinc-500">{label}</div>
      <div className="mt-1 break-words text-sm font-medium text-zinc-100">{value}</div>
    </div>
  );
}

function StatusBadge({ status }: { status: SreCheckResponse["overall_status"] }) {
  const styles = {
    healthy: "border-emerald-500/50 bg-emerald-500/10 text-emerald-200",
    degraded: "border-amber-500/50 bg-amber-500/10 text-amber-200",
    down: "border-red-500/50 bg-red-500/10 text-red-200",
  };
  return <Badge className={styles[status]}>{status}</Badge>;
}

function ProbeBadge({ status }: { status: SreProbe["status"] }) {
  const styles = {
    pass: "border-emerald-500/50 bg-emerald-500/10 text-emerald-200",
    warn: "border-amber-500/50 bg-amber-500/10 text-amber-200",
    fail: "border-red-500/50 bg-red-500/10 text-red-200",
  };
  return <Badge className={styles[status]}>{status}</Badge>;
}

function FieldError({ message }: { message?: string }) {
  return <p className="text-xs text-red-300">{message}</p>;
}
