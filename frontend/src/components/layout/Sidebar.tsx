import {
  Activity,
  BarChart3,
  FileText,
  Info,
  LayoutDashboard,
  ListChecks,
  Radar,
  PlayCircle,
  Plus,
  Settings,
  ShieldCheck,
  Target,
} from "lucide-react";

import { Button } from "../ui/Button";
import { AppView, useAppStore } from "../../store/useAppStore";
import { cn } from "../../lib/utils";

const navItems: Array<{ view: AppView; label: string; icon: typeof LayoutDashboard }> = [
  { view: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { view: "targets", label: "Targets", icon: Target },
  { view: "new-target", label: "New Target", icon: Plus },
  { view: "new-scan", label: "New Scan", icon: PlayCircle },
  { view: "scan-results", label: "Scan Results", icon: ListChecks },
  { view: "reports", label: "Reports", icon: FileText },
  { view: "sre", label: "SRE Check", icon: Radar },
  { view: "modules", label: "Modules", icon: ShieldCheck },
  { view: "settings", label: "Settings", icon: Settings },
  { view: "about", label: "About", icon: Info },
];

export function Sidebar() {
  const view = useAppStore((state) => state.view);
  const setView = useAppStore((state) => state.setView);

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
      <nav className="flex flex-1 flex-col gap-1">
        {navItems.map((item) => {
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
      </nav>
      <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3">
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
      </div>
    </aside>
  );
}
