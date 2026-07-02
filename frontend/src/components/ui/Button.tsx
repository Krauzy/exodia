import { ButtonHTMLAttributes, forwardRef } from "react";

import { cn } from "../../lib/utils";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", ...props }, ref) => {
    const variants = {
      primary: "border-cyan-400/40 bg-cyan-400 text-zinc-950 hover:bg-cyan-300",
      secondary: "border-zinc-700 bg-zinc-900 text-zinc-100 hover:bg-zinc-800",
      ghost: "border-transparent bg-transparent text-zinc-300 hover:bg-zinc-900 hover:text-zinc-50",
      danger: "border-red-500/50 bg-red-500/15 text-red-100 hover:bg-red-500/25",
    };
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex h-10 items-center justify-center gap-2 rounded-md border px-3 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50",
          variants[variant],
          className,
        )}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";

