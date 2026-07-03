import { create } from "zustand";

export type AppView =
  | "dashboard"
  | "targets"
  | "new-target"
  | "target-details"
  | "new-scan"
  | "scan-running"
  | "scan-results"
  | "reports"
  | "modules"
  | "settings"
  | "about";

interface AppState {
  view: AppView;
  selectedTargetId?: string;
  selectedScanId?: string;
  selectedReportId?: string;
  setView: (view: AppView) => void;
  openTarget: (targetId: string) => void;
  openScan: (scanId: string, running?: boolean) => void;
  openReport: (reportId: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  view: "dashboard",
  setView: (view) => set({ view }),
  openTarget: (selectedTargetId) => set({ view: "target-details", selectedTargetId }),
  openScan: (selectedScanId, running = false) =>
    set({ view: running ? "scan-running" : "scan-results", selectedScanId }),
  openReport: (selectedReportId) => set({ view: "reports", selectedReportId }),
}));
