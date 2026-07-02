import { SelectHTMLAttributes, forwardRef } from "react";

import { cn } from "../../lib/utils";

export const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement>>(
  ({ className, ...props }, ref) => (
    <select
      ref={ref}
      className={cn(
        "h-10 w-full rounded-md border border-zinc-800 bg-zinc-950 px-3 text-sm text-zinc-100 outline-none transition focus:border-cyan-400/70",
        className,
      )}
      {...props}
    />
  ),
);
Select.displayName = "Select";

