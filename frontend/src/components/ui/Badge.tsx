import { HTMLAttributes } from "react";

import { cn, severityClass } from "../../lib/utils";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  severity?: string;
}

export function Badge({ className, severity, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2 py-1 text-xs font-medium uppercase tracking-normal",
        severity ? severityClass(severity) : "border-zinc-700 bg-zinc-900 text-zinc-300",
        className,
      )}
      {...props}
    />
  );
}

