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

  if (!data || data.recommendations.length === 0) return (
    <div className="bg-white rounded-lg border border-slate-200 p-8 text-center">
      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-emerald-50 mb-4">
        <Gauge className="w-6 h-6 text-emerald-500" />
      </div>
      <h3 className="text-sm font-semibold text-slate-900 mb-1">Your Resources are Optimized!</h3>
      <p className="text-sm text-slate-500">
        No right-sizing opportunities found. Your fleet is running efficiently.
      </p>
    </div>
  );

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
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="font-mono text-sm font-medium text-slate-900 truncate">
                    {rec.name || rec.instance_id}
                  </h3>
                  <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium ${
                    rec.confidence === 'High' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
                  }`}>
                    {rec.confidence} Confidence
                  </span>
                </div>
                
                <div className="flex items-center gap-4 text-xs text-slate-500 mb-2">
                  <div className="flex items-center gap-2 flex-1 max-w-xs">
                    <span className="whitespace-nowrap">CPU Usage:</span>
                    <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${rec.max_cpu > 50 ? 'bg-amber-500' : 'bg-green-500'}`} 
                        style={{ width: `${Math.min(rec.max_cpu, 100)}%` }}
                      />
                    </div>
                    <span className="font-medium text-slate-700 w-12 text-right">{rec.max_cpu}% Max</span>
                  </div>
                  <span className="text-slate-300">|</span>
                  <span>Avg: <span className="font-medium text-slate-700">{rec.avg_cpu}%</span></span>
                </div>
              </div>

              <div className="flex items-center justify-between md:justify-end gap-6 flex-shrink-0 border-t md:border-t-0 border-slate-100 pt-3 md:pt-0">
                <div className="flex items-center gap-3 text-sm">
                  <div className="text-right">
                    <p className="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">Current</p>
                    <span className="font-mono text-slate-500 line-through decoration-slate-300 text-xs block">{rec.current_type}</span>
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-300" />
                  <div>
                     <p className="text-[10px] text-indigo-500 uppercase tracking-wide mb-0.5 font-medium">Suggested</p>
                    <span className="font-mono font-semibold text-indigo-600 text-xs bg-indigo-50 px-2 py-1 rounded border border-indigo-100 block">
                      {rec.suggested_type}
                    </span>
                  </div>
                </div>
                
                <div className="text-right pl-4 border-l border-slate-100 min-w-[100px]">
                  <p className="text-[10px] text-emerald-600 uppercase tracking-wide font-medium mb-0.5">Save</p>
                  <p className="font-bold text-emerald-600 text-lg leading-none">
                    ${rec.estimated_monthly_savings.toFixed(2)}
                  </p>
                  <p className="text-[10px] text-slate-400">/month</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
