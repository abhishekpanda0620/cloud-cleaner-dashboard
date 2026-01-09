'use client';

import { useState, useEffect } from 'react';
import { RightSizingSummary } from '@/lib/api/types';
import { AlertTriangle, ArrowRight, Gauge } from 'lucide-react';

export default function RightSizingRecommendations() {
  const [data, setData] = useState<RightSizingSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084'}/rightsizing/recommendations`);
        if (!res.ok) throw new Error('Failed to fetch recommendations');
        const json = await res.json();
        setData(json);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error loading data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return (
    <div className="bg-white rounded-lg border border-slate-200 p-6 animate-pulse">
      <div className="h-5 bg-slate-100 rounded w-1/3 mb-6"></div>
      <div className="space-y-4">
        <div className="h-16 bg-slate-50 rounded border border-slate-100"></div>
        <div className="h-16 bg-slate-50 rounded border border-slate-100"></div>
      </div>
    </div>
  );

  if (error) return (
    <div className="bg-white border border-red-200 rounded-lg p-4 flex items-center gap-3 text-red-700">
      <AlertTriangle className="w-5 h-5 flex-shrink-0" />
      <span className="text-sm">Error: {error}</span>
    </div>
  );

  if (!data || data.recommendations.length === 0) return null;

  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
      <div className="p-6 border-b border-slate-200 bg-slate-50/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Gauge className="w-5 h-5 text-slate-500" />
            <div>
              <h2 className="text-sm font-semibold text-slate-900">Right-Sizing Opportunities</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                {data.opportunities_found} optimization candidates
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider font-medium">Potential Savings</p>
            <p className="text-lg font-bold text-emerald-600">
              ${data.total_potential_savings.toFixed(2)}
              <span className="text-xs font-normal text-slate-400 ml-1">/mo</span>
            </p>
          </div>
        </div>
      </div>

      <div className="divide-y divide-slate-100">
        {data.recommendations.map((rec) => (
          <div key={rec.instance_id} className="p-4 hover:bg-slate-50 transition-colors group">
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0 mr-6">
                <div className="flex items-center gap-2 mb-1.5">
                  <h3 className="font-mono text-sm font-medium text-slate-900 truncate">
                    {rec.name || rec.instance_id}
                  </h3>
                </div>
                <div className="flex items-center gap-4 text-xs text-slate-500">
                  <div className="flex items-center gap-1.5">
                    <span className={`w-1.5 h-1.5 rounded-full ${rec.confidence === 'High' ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
                    <span>{rec.confidence} Confidence</span>
                  </div>
                  <span className="text-slate-300">|</span>
                  <span>Avg CPU: <span className="font-medium text-slate-700">{rec.avg_cpu}%</span></span>
                </div>
              </div>

              <div className="flex items-center gap-6 flex-shrink-0">
                <div className="text-right">
                  <div className="flex items-center gap-2 text-sm justify-end">
                    <span className="font-mono text-slate-400 decoration-slate-300 line-through text-xs">{rec.current_type}</span>
                    <ArrowRight className="w-3 h-3 text-slate-300" />
                    <span className="font-mono font-semibold text-indigo-600 text-xs bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-100">{rec.suggested_type}</span>
                  </div>
                </div>
                
                <div className="text-right min-w-[80px]">
                  <p className="font-medium text-emerald-600 text-sm">
                    +${rec.estimated_monthly_savings.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
