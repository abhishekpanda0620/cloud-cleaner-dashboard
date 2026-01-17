import { LineChart } from 'lucide-react';
import { CostTrend } from '@/types/cost-analysis';

interface CostTrendsProps {
  trends: CostTrend[];
}

export function CostTrends({ trends }: CostTrendsProps) {
  if (trends.length === 0) return null;

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6 flex-1">
      <h2 className="text-sm font-semibold text-slate-900 flex items-center gap-2 mb-4">
        <LineChart className="w-4 h-4 text-slate-500" />
        7-Day Trend
      </h2>
      <div className="space-y-0 divide-y divide-slate-100 border-t border-slate-100">
        {trends.slice(0, 5).map((trend, index) => (
          <div key={index} className="flex items-center justify-between py-2.5">
            <p className="text-xs font-mono text-slate-500">{new Date(trend.date).toLocaleDateString(undefined, {weekday:'short', day:'numeric'})}</p>
            <div className="flex items-center gap-2">
               <span className="text-xs font-semibold text-slate-900">${trend.totalCost.toFixed(2)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
