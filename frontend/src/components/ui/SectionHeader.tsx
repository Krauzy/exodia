import { ReactNode } from "react";

export function SectionHeader({
  title,
  description,
  actions,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-5 flex flex-col gap-3 border-b border-zinc-800 pb-4 md:flex-row md:items-end md:justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-zinc-50">{title}</h1>
        {description ? <p className="mt-1 max-w-3xl text-sm text-zinc-400">{description}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}

