import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { ClassProbability } from '../api/client';

interface PredictionPanelProps {
  label: string;
  confidence: number;
  probabilities: ClassProbability[];
}

export default function PredictionPanel({
  label,
  confidence,
  probabilities,
}: PredictionPanelProps) {
  const chartData = probabilities.map((p) => ({
    label: p.label,
    value: +(p.probability * 100).toFixed(1),
  }));

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5">
      <h2 className="mb-1 text-sm font-semibold uppercase tracking-wider text-slate-400">
        Prediction
      </h2>
      <div className="mb-5 flex items-baseline gap-3">
        <span className="text-2xl font-bold text-cyan-400">{label}</span>
        <span className="text-sm text-slate-400">
          {(confidence * 100).toFixed(1)}% confidence
        </span>
      </div>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ left: 8, right: 24 }}
          >
            <XAxis type="number" domain={[0, 100]} hide />
            <YAxis
              type="category"
              dataKey="label"
              width={110}
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              cursor={{ fill: 'rgba(148,163,184,0.08)' }}
              contentStyle={{
                background: '#0f172a',
                border: '1px solid #334155',
                borderRadius: 8,
                color: '#e2e8f0',
              }}
              formatter={(v: number) => [`${v}%`, 'Probability']}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {chartData.map((entry, i) => (
                <Cell
                  key={entry.label}
                  fill={i === 0 ? '#22d3ee' : '#475569'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
