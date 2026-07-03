import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { LockKeyhole, LogIn, UserPlus } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { api } from "../../services/api";
import { useAuthStore } from "../../store/useAuthStore";

const authSchema = z.object({
  username: z.string().min(3).max(80).regex(/^[A-Za-z0-9_.-]+$/, "Use letters, numbers, dot, dash or underscore"),
  password: z.string().min(8).max(128),
});

type AuthFormValues = z.infer<typeof authSchema>;
type AuthMode = "login" | "register";

export function AuthPage() {
  const [mode, setMode] = useState<AuthMode>("login");
  const queryClient = useQueryClient();
  const setSession = useAuthStore((state) => state.setSession);
  const { register, handleSubmit, formState } = useForm<AuthFormValues>({
    resolver: zodResolver(authSchema),
    defaultValues: { username: "", password: "" },
  });
  const mutation = useMutation({
    mutationFn: (values: AuthFormValues) => (mode === "login" ? api.login(values) : api.register(values)),
    onSuccess: (session) => {
      setSession(session);
      queryClient.clear();
    },
  });
  const Icon = mode === "login" ? LogIn : UserPlus;

  return (
    <main className="flex min-h-screen items-center justify-center bg-zinc-950 px-4 text-zinc-100">
      <Card className="w-full max-w-md">
        <div className="mb-6 flex items-start gap-3">
          <div className="rounded-md border border-cyan-400/30 bg-cyan-400/10 p-2">
            <LockKeyhole className="h-5 w-5 text-cyan-200" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-zinc-50">Exodia</h1>
            <p className="mt-1 text-sm leading-6 text-zinc-400">Authorized audit workspace</p>
          </div>
        </div>

        <div className="mb-4 grid grid-cols-2 rounded-md border border-zinc-800 bg-zinc-950 p-1">
          <button
            className={`h-9 rounded-md text-sm transition ${
              mode === "login" ? "bg-cyan-400 text-zinc-950" : "text-zinc-400 hover:text-zinc-100"
            }`}
            onClick={() => setMode("login")}
            type="button"
          >
            Login
          </button>
          <button
            className={`h-9 rounded-md text-sm transition ${
              mode === "register" ? "bg-cyan-400 text-zinc-950" : "text-zinc-400 hover:text-zinc-100"
            }`}
            onClick={() => setMode("register")}
            type="button"
          >
            Register
          </button>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit((values) => mutation.mutate(values))}>
          <label className="space-y-2 text-sm text-zinc-300">
            <span>Username</span>
            <Input autoComplete="username" {...register("username")} />
            {formState.errors.username ? <FieldError message={formState.errors.username.message} /> : null}
          </label>
          <label className="space-y-2 text-sm text-zinc-300">
            <span>Password</span>
            <Input
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              type="password"
              {...register("password")}
            />
            {formState.errors.password ? <FieldError message={formState.errors.password.message} /> : null}
          </label>
          {mutation.error ? <p className="text-sm text-red-300">{mutation.error.message}</p> : null}
          <Button className="w-full" disabled={mutation.isPending} type="submit">
            <Icon className="h-4 w-4" />
            {mutation.isPending ? "Please wait..." : mode === "login" ? "Login" : "Create user"}
          </Button>
        </form>
      </Card>
    </main>
  );
}

function FieldError({ message }: { message?: string }) {
  return <p className="text-xs text-red-300">{message}</p>;
}
