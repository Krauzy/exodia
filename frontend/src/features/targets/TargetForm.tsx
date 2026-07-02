import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Save } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "../../components/ui/Button";
import { Input, Textarea } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { api } from "../../services/api";
import { useAppStore } from "../../store/useAppStore";
import type { Target } from "../../types/api";

const targetSchema = z.object({
  name: z.string().min(2).max(160),
  target_type: z.enum(["web", "api", "host"]),
  value: z.string().min(2).max(512),
  description: z.string().max(1000).optional(),
  authorization_scope: z.string().min(8).max(2000),
  tags: z.string().optional(),
  active: z.boolean().default(true),
});

type TargetFormValues = z.infer<typeof targetSchema>;

export function TargetForm({ target }: { target?: Target }) {
  const queryClient = useQueryClient();
  const openTarget = useAppStore((state) => state.openTarget);
  const { register, handleSubmit, formState } = useForm<TargetFormValues>({
    resolver: zodResolver(targetSchema),
    defaultValues: {
      name: target?.name ?? "",
      target_type: target?.target_type ?? "web",
      value: target?.value ?? "",
      description: target?.description ?? "",
      authorization_scope: target?.authorization_scope ?? "",
      tags: target?.tags.join(", ") ?? "",
      active: target?.active ?? true,
    },
  });
  const mutation = useMutation({
    mutationFn: async (values: TargetFormValues) => {
      const payload = {
        ...values,
        description: values.description ?? "",
        tags: (values.tags ?? "")
          .split(",")
          .map((tag) => tag.trim())
          .filter(Boolean),
      };
      return target ? api.updateTarget(target.id, payload) : api.createTarget(payload);
    },
    onSuccess: (saved) => {
      queryClient.invalidateQueries({ queryKey: ["targets"] });
      openTarget(saved.id);
    },
  });

  return (
    <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit((values) => mutation.mutate(values))}>
      <label className="space-y-2 text-sm text-zinc-300">
        <span>Name</span>
        <Input {...register("name")} placeholder="Production API" />
        {formState.errors.name ? <FieldError message={formState.errors.name.message} /> : null}
      </label>
      <label className="space-y-2 text-sm text-zinc-300">
        <span>Type</span>
        <Select {...register("target_type")}>
          <option value="web">Web</option>
          <option value="api">API</option>
          <option value="host">Host</option>
        </Select>
      </label>
      <label className="space-y-2 text-sm text-zinc-300 md:col-span-2">
        <span>URL or host</span>
        <Input {...register("value")} placeholder="https://app.example.test or 10.10.0.5" />
        {formState.errors.value ? <FieldError message={formState.errors.value.message} /> : null}
      </label>
      <label className="space-y-2 text-sm text-zinc-300 md:col-span-2">
        <span>Authorized scope</span>
        <Textarea {...register("authorization_scope")} placeholder="Document the approval, environment, and boundaries." />
        {formState.errors.authorization_scope ? <FieldError message={formState.errors.authorization_scope.message} /> : null}
      </label>
      <label className="space-y-2 text-sm text-zinc-300 md:col-span-2">
        <span>Description</span>
        <Textarea {...register("description")} placeholder="Business context, owner, or notes." />
      </label>
      <label className="space-y-2 text-sm text-zinc-300">
        <span>Tags</span>
        <Input {...register("tags")} placeholder="internal, staging, api" />
      </label>
      <label className="flex items-center gap-3 rounded-md border border-zinc-800 bg-zinc-950 p-3 text-sm text-zinc-300">
        <input type="checkbox" className="h-4 w-4 accent-cyan-400" {...register("active")} />
        Active target
      </label>
      {mutation.error ? <p className="text-sm text-red-300 md:col-span-2">{mutation.error.message}</p> : null}
      <div className="md:col-span-2">
        <Button type="submit" disabled={mutation.isPending}>
          <Save className="h-4 w-4" />
          {target ? "Update target" : "Create target"}
        </Button>
      </div>
    </form>
  );
}

function FieldError({ message }: { message?: string }) {
  return <p className="text-xs text-red-300">{message}</p>;
}

