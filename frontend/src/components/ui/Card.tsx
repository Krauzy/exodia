import { HTMLAttributes } from "react";

import { cn } from "../../lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("rounded-lg border border-zinc-800 bg-zinc-950/70 p-4 shadow-sm shadow-black/20", className)}
      {...props}
    />
  );
}

