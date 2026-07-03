import {
  Activity,
  BarChart3,
  FileText,
  Info,
  LayoutDashboard,
  ListChecks,
  LogOut,
  PlayCircle,
  Plus,
  Settings,
  ShieldCheck,
  Target,
} from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

import { Button } from "../ui/Button";
import type { AppView } from "../../store/useAppStore";
import { useAppStore } from "../../store/useAppStore";
import { useAuthStore } from "../../store/useAuthStore";
import { cn } from "../../lib/utils";

type NavItem = { view: AppView; label: string; icon: typeof LayoutDashboard };

const navGroups: Array<{ label: string; items: NavItem[] }> = [
  {
    label: "Overview",
    items: [{ view: "dashboard", label: "Dashboard", icon: LayoutDashboard }],
  },
  {
    label: "Targets",
    items: [
      { view: "targets", label: "Targets", icon: Target },
      { view: "new-target", label: "New Target", icon: Plus },
    ],
  },
  {
    label: "Scans",
    items: [
      { view: "new-scan", label: "New Scan", icon: PlayCircle },
      { view: "scan-running", label: "Live Scan", icon: Activity },
      { view: "scan-results", label: "Scan Results", icon: ListChecks },
      { view: "reports", label: "Reports", icon: FileText },
    ],
  },
  {
    label: "Operations",
    items: [{ view: "modules", label: "Modules", icon: ShieldCheck }],
  },
  {
    label: "System",
    items: [
      { view: "settings", label: "Settings", icon: Settings },
      { view: "about", label: "About", icon: Info },
    ],
  },
];

export function Sidebar() {
  const queryClient = useQueryClient();
  const view = useAppStore((state) => state.view);
  const setView = useAppStore((state) => state.setView);
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  function handleLogout() {
    logout();
    queryClient.clear();
    setView("dashboard");
  }

  return (
    <aside className="flex h-screen w-72 shrink-0 flex-col border-r border-zinc-800 bg-zinc-950/95 px-4 py-5">
      <div className="mb-6 flex items-center gap-3 px-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-md border border-cyan-400/40 bg-cyan-400/10">
          <Activity className="h-5 w-5 text-cyan-300" />
        </div>
        <div>
          <div className="text-lg font-semibold text-zinc-50">Exodia</div>
          <div className="text-xs uppercase tracking-normal text-zinc-500">Authorized Audit Console</div>
        </div>
      </div>
      <nav className="flex flex-1 flex-col gap-4 overflow-y-auto pr-1">
        {navGroups.map((group) => (
          <div key={group.label}>
            <div className="mb-2 px-3 text-[11px] font-medium uppercase text-zinc-600">{group.label}</div>
            <div className="flex flex-col gap-1">
              {group.items.map((item) => {
                const Icon = item.icon;
                const active = view === item.view;
                return (
                  <button
                    key={item.view}
                    onClick={() => setView(item.view)}
                    className={cn(
                      "flex h-10 items-center gap-3 rounded-md px-3 text-left text-sm transition",
                      active
                        ? "border border-cyan-400/30 bg-cyan-400/10 text-cyan-100"
                        : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100",
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </nav>
      <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3">
        <div className="mb-3 border-b border-zinc-800 pb-3">
          <div className="text-xs uppercase text-zinc-500">User</div>
          <div className="mt-1 truncate text-sm font-medium text-zinc-100">{user?.username ?? "unknown"}</div>
        </div>
        <div className="mb-2 flex items-center gap-2 text-sm font-medium text-zinc-100">
          <BarChart3 className="h-4 w-4 text-emerald-300" />
          Safe mode
        </div>
        <p className="text-xs leading-5 text-zinc-400">
          Passive checks, explicit authorization, low-rate probes, and local-only plugins.
        </p>
        <Button className="mt-3 w-full" variant="secondary" onClick={() => setView("new-scan")}>
          <PlayCircle className="h-4 w-4" />
          Start scan
        </Button>
        <Button className="mt-2 w-full" variant="ghost" onClick={handleLogout}>
          <LogOut className="h-4 w-4" />
          Logout
        </Button>
      </div>
    </aside>
  );
}
