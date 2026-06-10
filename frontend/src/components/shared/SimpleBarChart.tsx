interface BarChartSeries {
  label: string;
  values: number[];
  colorClass: string;
}

interface SimpleBarChartProps {
  labels: string[];
  series: BarChartSeries[];
  emptyMessage?: string;
}

export function SimpleBarChart({ labels, series, emptyMessage }: SimpleBarChartProps) {
  if (labels.length === 0) {
    return <p className="text-sm text-slate-400">{emptyMessage ?? "No data yet."}</p>;
  }

  const maxValue = Math.max(
    1,
    ...series.flatMap((item) => item.values),
  );

  return (
    <div className="space-y-4">
      <div className="flex gap-4 text-xs text-slate-400">
        {series.map((item) => (
          <span key={item.label} className="flex items-center gap-2">
            <span className={`inline-block h-2 w-2 rounded-full ${item.colorClass}`} />
            {item.label}
          </span>
        ))}
      </div>
      <div className="flex items-end gap-2 overflow-x-auto pb-2">
        {labels.map((label, index) => (
          <div key={label} className="flex min-w-[3rem] flex-1 flex-col items-center gap-1">
            <div className="flex h-32 w-full items-end justify-center gap-1">
              {series.map((item) => {
                const value = item.values[index] ?? 0;
                const height = `${Math.max((value / maxValue) * 100, value > 0 ? 4 : 0)}%`;
                return (
                  <div
                    key={item.label}
                    title={`${item.label}: ${value}`}
                    className={`w-3 rounded-t ${item.colorClass}`}
                    style={{ height }}
                  />
                );
              })}
            </div>
            <span className="text-[10px] text-slate-500">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
