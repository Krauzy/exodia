import { ColumnDef, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { Eye, Plus } from "lucide-react";
import { useMemo } from "react";

import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { useTargets } from "../../hooks/useApiQueries";
import { formatDate } from "../../lib/utils";
import { useAppStore } from "../../store/useAppStore";
import type { Target } from "../../types/api";

export function TargetsPage() {
  const targets = useTargets();
  const openTarget = useAppStore((state) => state.openTarget);
  const setView = useAppStore((state) => state.setView);
  const columns = useMemo<ColumnDef<Target>[]>(
    () => [
      {
        header: "Name",
        accessorKey: "name",
        cell: ({ row }) => (
          <button className="text-left font-medium text-zinc-100 hover:text-cyan-200" onClick={() => openTarget(row.original.id)}>
            {row.original.name}
          </button>
        ),
      },
      { header: "Type", accessorKey: "target_type" },
      { header: "Value", accessorKey: "value" },
      {
        id: "status",
        header: "Status",
        cell: ({ row }) => <Badge>{row.original.active ? "active" : "inactive"}</Badge>,
      },
      {
        id: "created",
        header: "Created",
        cell: ({ row }) => formatDate(row.original.created_at),
      },
      {
        id: "actions",
        header: "",
        cell: ({ row }) => (
          <Button variant="ghost" className="h-8 w-8 px-0" title="Open target" onClick={() => openTarget(row.original.id)}>
            <Eye className="h-4 w-4" />
          </Button>
        ),
      },
    ],
    [openTarget],
  );
  const table = useReactTable({
    data: targets.data ?? [],
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <>
      <SectionHeader
        title="Targets"
        description="Authorized assets that can be scanned by defensive modules."
        actions={
          <Button onClick={() => setView("new-target")}>
            <Plus className="h-4 w-4" />
            New target
          </Button>
        }
      />
      <Card>
        <div className="overflow-hidden rounded-md border border-zinc-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-zinc-900 text-xs uppercase text-zinc-500">
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <th key={header.id} className="px-3 py-2 font-medium">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row) => (
                <tr key={row.id} className="border-t border-zinc-800 text-zinc-300">
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="max-w-md truncate px-3 py-2">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
              {!table.getRowModel().rows.length ? (
                <tr>
                  <td colSpan={columns.length} className="px-3 py-8 text-center text-zinc-500">
                    No targets registered.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </Card>
    </>
  );
}
