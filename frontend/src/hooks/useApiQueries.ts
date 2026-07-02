import { useQuery } from "@tanstack/react-query";

import { api } from "../services/api";

export function useHealth() {
  return useQuery({ queryKey: ["health"], queryFn: api.health, refetchInterval: 10_000 });
}

export function useTargets() {
  return useQuery({ queryKey: ["targets"], queryFn: api.targets });
}

export function useModules() {
  return useQuery({ queryKey: ["modules"], queryFn: api.modules });
}

export function useScans() {
  return useQuery({ queryKey: ["scans"], queryFn: api.scans, refetchInterval: 5_000 });
}

export function useReports() {
  return useQuery({ queryKey: ["reports"], queryFn: api.reports });
}

