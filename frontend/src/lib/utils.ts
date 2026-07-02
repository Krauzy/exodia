import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(value?: string | null) {
  if (!value) return "-";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

export function severityClass(severity: string) {
  switch (severity) {
    case "critical":
      return "border-red-500/50 bg-red-500/10 text-red-200";
    case "high":
      return "border-orange-500/50 bg-orange-500/10 text-orange-200";
    case "medium":
      return "border-amber-500/50 bg-amber-500/10 text-amber-200";
    case "low":
      return "border-emerald-500/50 bg-emerald-500/10 text-emerald-200";
    default:
      return "border-cyan-500/50 bg-cyan-500/10 text-cyan-200";
  }
}
