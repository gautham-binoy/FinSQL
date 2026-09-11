import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  Cell,
} from 'recharts';
import { ChartRecommendation } from '../types';
import { BarChart3, LineChart as LineIcon } from 'lucide-react';

interface VisualizerProps {
  chart: ChartRecommendation | undefined;
  rows: Array<Record<string, any>> | undefined;
}

const COLORS = ['#3b82f6', '#06b6d4', '#10b981', '#8b5cf6', '#f59e0b', '#ec4899', '#6366f1'];

function formatAxisCurrency(val: any): string {
  if (typeof val !== 'number') return String(val);
  const abs = Math.abs(val);
  if (abs >= 1e12) return `$${(val / 1e12).toFixed(1)}T`;
  if (abs >= 1e9) return `$${(val / 1e9).toFixed(1)}B`;
  if (abs >= 1e6) return `$${(val / 1e6).toFixed(1)}M`;
  if (abs >= 1e3) return `$${(val / 1e3).toFixed(1)}K`;
  return `$${val}`;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-gray-950/95 border border-white/15 p-3 rounded-xl shadow-2xl backdrop-blur-md text-xs">
        <p className="font-semibold text-gray-200 mb-1.5">{label}</p>
        {payload.map((entry: any, index: number) => {
          const val = entry.value;
          let displayVal = val;
          if (typeof val === 'number') {
            if (entry.dataKey.includes('pct') || entry.dataKey.includes('percentage') || entry.dataKey.includes('margin')) {
              displayVal = `${val.toFixed(2)}%`;
            } else {
              displayVal = formatAxisCurrency(val);
            }
          }
          return (
            <p key={index} style={{ color: entry.color }} className="font-mono flex items-center justify-between gap-4">
              <span className="capitalize">{entry.name}:</span>
              <span className="font-bold">{displayVal}</span>
            </p>
          );
        })}
      </div>
    );
  }
  return null;
};

export const Visualizer: React.FC<VisualizerProps> = ({ chart, rows }) => {
  if (!chart || chart.type === 'none' || !rows || rows.length <= 1) {
    return null;
  }

  // Determine X key
  const xKey =
    chart.x_key && rows[0] && rows[0][chart.x_key] !== undefined
      ? chart.x_key
      : rows[0]?.fiscal_year !== undefined
      ? 'fiscal_year'
      : rows[0]?.company_name !== undefined
      ? 'company_name'
      : rows[0]?.ticker !== undefined
      ? 'ticker'
      : Object.keys(rows[0] || {})[0];

  // Determine Y key
  const yKey =
    chart.y_keys && chart.y_keys[0] && rows[0] && rows[0][chart.y_keys[0]] !== undefined
      ? chart.y_keys[0]
      : rows[0]?.value !== undefined
      ? 'value'
      : rows[0]?.revenue !== undefined
      ? 'revenue'
      : rows[0]?.net_income_margin_pct !== undefined
      ? 'net_income_margin_pct'
      : 'value';

  const isPercentage = yKey.includes('pct') || yKey.includes('margin') || yKey.includes('percentage');

  return (
    <div className="bg-gray-900/80 border border-white/10 rounded-2xl p-6 shadow-xl backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-cyan-400 mb-1">
            {chart.type === 'line' ? <LineIcon className="w-4 h-4" /> : <BarChart3 className="w-4 h-4" />}
            <span>Visualization</span>
          </div>
          <h3 className="text-base font-semibold text-gray-200">{chart.title}</h3>
        </div>
      </div>

      <div className="w-full h-72">
        <ResponsiveContainer width="100%" height="100%">
          {chart.type === 'line' ? (
            <LineChart data={rows} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis
                dataKey={xKey}
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 12 }}
                dy={10}
              />
              <YAxis
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 12 }}
                tickFormatter={isPercentage ? (v) => `${v}%` : formatAxisCurrency}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey={yKey}
                stroke="#06b6d4"
                strokeWidth={3}
                dot={{ fill: '#06b6d4', r: 5, strokeWidth: 2, stroke: '#083344' }}
                activeDot={{ r: 8, stroke: '#ecfeff', strokeWidth: 2 }}
              />
            </LineChart>
          ) : (
            <BarChart data={rows} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis
                dataKey={xKey}
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 12 }}
                dy={10}
              />
              <YAxis
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 12 }}
                tickFormatter={isPercentage ? (v) => `${v}%` : formatAxisCurrency}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey={yKey} radius={[6, 6, 0, 0]}>
                {rows.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
};
