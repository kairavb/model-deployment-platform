type StatusBadgeProps = {
  status: string;
};

const STATUS_STYLES: Record<string, string> = {
  running: "bg-emerald-500/20 text-emerald-300",
  healthy: "bg-emerald-500/20 text-emerald-300",
  pending: "bg-amber-500/20 text-amber-300",
  starting: "bg-amber-500/20 text-amber-300",
  stopping: "bg-amber-500/20 text-amber-300",
  stopped: "bg-slate-500/20 text-slate-300",
  failed: "bg-rose-500/20 text-rose-300",
  unhealthy: "bg-rose-500/20 text-rose-300",
  unknown: "bg-slate-500/20 text-slate-300",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const style = STATUS_STYLES[status] ?? "bg-slate-500/20 text-slate-300";
  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium capitalize ${style}`}>
      {status}
    </span>
  );
}
