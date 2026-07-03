import { Sidebar } from "../components/layout/Sidebar";
import { AboutPage } from "../features/about/AboutPage";
import { AuthPage } from "../features/auth/AuthPage";
import { DashboardPage } from "../features/dashboard/DashboardPage";
import { ModulesPage } from "../features/modules/ModulesPage";
import { ReportsPage } from "../features/reports/ReportsPage";
import { NewScanPage } from "../features/scans/NewScanPage";
import { ScanResultsPage } from "../features/scans/ScanResultsPage";
import { ScanRunningPage } from "../features/scans/ScanRunningPage";
import { SettingsPage } from "../features/settings/SettingsPage";
import { NewTargetPage } from "../features/targets/NewTargetPage";
import { TargetDetailsPage } from "../features/targets/TargetDetailsPage";
import { TargetsPage } from "../features/targets/TargetsPage";
import { useAuthStore } from "../store/useAuthStore";
import { useAppStore } from "../store/useAppStore";

export function App() {
  const token = useAuthStore((state) => state.token);
  const view = useAppStore((state) => state.view);

  if (!token) {
    return <AuthPage />;
  }

  return (
    <div className="flex min-h-screen bg-transparent text-zinc-100">
      <Sidebar />
      <main className="h-screen flex-1 overflow-y-auto">
        <div className="mx-auto w-full max-w-7xl px-6 py-6">
          {view === "dashboard" && <DashboardPage />}
          {view === "targets" && <TargetsPage />}
          {view === "new-target" && <NewTargetPage />}
          {view === "target-details" && <TargetDetailsPage />}
          {view === "new-scan" && <NewScanPage />}
          {view === "scan-running" && <ScanRunningPage />}
          {view === "scan-results" && <ScanResultsPage />}
          {view === "reports" && <ReportsPage />}
          {view === "modules" && <ModulesPage />}
          {view === "settings" && <SettingsPage />}
          {view === "about" && <AboutPage />}
        </div>
      </main>
    </div>
  );
}
