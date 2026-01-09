'use client';

import { useState, useEffect } from 'react';
import { RightSizingSummary } from '@/lib/api/types';

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
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 animate-pulse">
      <div className="h-6 bg-slate-100 rounded w-1/3 mb-4"></div>
      <div className="space-y-3">
        <div className="h-20 bg-slate-50 rounded"></div>
        <div className="h-20 bg-slate-50 rounded"></div>
      </div>
    </div>
  );

  if (error) return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700">
      Error: {error}
    </div>
  );

  if (!data || data.recommendations.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="p-6 border-b border-slate-100 bg-gradient-to-r from-green-50 to-emerald-50">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Right-Sizing Opportunities</h2>
            <p className="text-sm text-slate-600">
              Found {data.opportunities_found} instances to optimize
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-slate-600">Potential Monthly Savings</p>
            <p className="text-2xl font-bold text-green-600">
              ${data.total_potential_savings.toFixed(2)}
            </p>
          </div>
        </div>
      </div>

      <div className="divide-y divide-slate-100">
        {data.recommendations.map((rec) => (
          <div key={rec.instance_id} className="p-6 hover:bg-slate-50 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-medium text-slate-900">
                    {rec.name || rec.instance_id}
                  </h3>
                  <span className="px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs rounded-full font-medium">
                    {rec.confidence} Confidence
                  </span>
                </div>
                <div className="flex items-center gap-4 text-sm text-slate-500">
                  <span>CPU Avg: {rec.avg_cpu}%</span>
                  <span>Max: {rec.max_cpu}%</span>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="text-right">
                  <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Downgrade</div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-slate-400 line-through">{rec.current_type}</span>
                    <span className="text-slate-400">→</span>
                    <span className="font-mono font-bold text-indigo-600">{rec.suggested_type}</span>
                  </div>
                </div>
                
                <div className="pl-6 border-l border-slate-200 text-right min-w-[100px]">
                  <p className="text-xs text-slate-500 mb-1">Save</p>
                  <p className="font-bold text-green-600">
                    ${rec.estimated_monthly_savings.toFixed(2)}
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
