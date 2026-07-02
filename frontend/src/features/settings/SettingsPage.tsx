import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Save } from "lucide-react";
import { useForm } from "react-hook-form";

import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { api } from "../../services/api";

interface SettingsForm {
  safe_mode: boolean;
  plugins_dir: string;
  http_timeout_seconds: number;
  max_concurrent_modules: number;
}

export function SettingsPage() {
  const queryClient = useQueryClient();
  const settings = useQuery({ queryKey: ["settings"], queryFn: api.settings });
  const { register, handleSubmit, reset } = useForm<SettingsForm>({
    values: settings.data,
  });
  const mutation = useMutation({
    mutationFn: (payload: SettingsForm) => api.updateSettings(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["settings"] }),
  });

  return (
    <>
      <SectionHeader
        title="Settings"
        description="Local runtime controls. Plugins are loaded only from a configured local folder."
        actions={
          <Button variant="secondary" onClick={() => settings.data && reset(settings.data)}>
            Reset
          </Button>
        }
      />
      <Card>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit((data) => mutation.mutate(data))}>
          <label className="space-y-2 text-sm text-zinc-300">
            <span>Plugins directory</span>
            <Input {...register("plugins_dir")} />
          </label>
          <label className="space-y-2 text-sm text-zinc-300">
            <span>HTTP timeout seconds</span>
            <Input type="number" step="0.5" {...register("http_timeout_seconds", { valueAsNumber: true })} />
          </label>
          <label className="space-y-2 text-sm text-zinc-300">
            <span>Max concurrent modules</span>
            <Input type="number" {...register("max_concurrent_modules", { valueAsNumber: true })} />
          </label>
          <label className="flex items-center gap-3 rounded-md border border-zinc-800 bg-zinc-950 p-3 text-sm text-zinc-300">
            <input type="checkbox" className="h-4 w-4 accent-cyan-400" {...register("safe_mode")} />
            Safe mode enabled
          </label>
          <div className="md:col-span-2">
            <Button type="submit" disabled={mutation.isPending}>
              <Save className="h-4 w-4" />
              Save settings
            </Button>
          </div>
        </form>
      </Card>
    </>
  );
}

