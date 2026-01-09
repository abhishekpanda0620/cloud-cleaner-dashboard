import React, { useEffect, useState } from 'react';

interface SavingsSummary {
  total_monthly_savings: number;
  projected_yearly_savings: number;
  total_items_deleted: number;
  savings_last_30_days: number;
}

interface SavingsItem {
  id: number;
  resource_id: string;
  resource_name: string | null;
  resource_type: string;
  region: string;
  estimated_monthly_cost: number;
  deleted_at: string;
}

const SavingsTracker: React.FC = () => {
    const [summary, setSummary] = useState<SavingsSummary | null>(null);
    const [history, setHistory] = useState<SavingsItem[]>([]);
    const [loading, setLoading] = useState(true);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084/api';

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [summaryRes, historyRes] = await Promise.all([
                    fetch(`${apiUrl}/savings/summary`),
                    fetch(`${apiUrl}/savings/history`)
                ]);

                if (summaryRes.ok) setSummary(await summaryRes.json());
                if (historyRes.ok) setHistory(await historyRes.json());
            } catch (error) {
                console.error("Error fetching savings data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [apiUrl]);

    if (loading) {
        return <div className="animate-pulse h-64 bg-slate-100 rounded-xl"></div>;
    }

    if (!summary) return null;

    return (
        <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl p-6 text-white shadow-lg transform hover:scale-105 transition-transform duration-300">
                    <div className="flex justify-between items-start mb-4">
                        <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                            <span className="text-2xl">💰</span>
                        </div>
                        <span className="text-sm font-medium bg-white/20 px-2 py-1 rounded-full">All Time</span>
                    </div>
                    <h3 className="text-white/80 text-sm font-medium uppercase tracking-wider">Total Monthly Savings</h3>
                    <div className="mt-2 flex items-baseline gap-2">
                        <span className="text-4xl font-bold">${summary.total_monthly_savings.toFixed(2)}</span>
                        <span className="text-sm text-white/70">/mo</span>
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-lg hover:shadow-xl transition-shadow duration-300">
                    <div className="flex justify-between items-start mb-4">
                        <div className="p-3 bg-indigo-50 rounded-xl">
                            <span className="text-2xl">📅</span>
                        </div>
                        <span className="text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-1 rounded-full">Projected</span>
                    </div>
                    <h3 className="text-slate-500 text-sm font-medium uppercase tracking-wider">Annual Savings</h3>
                    <div className="mt-2">
                        <span className="text-3xl font-bold text-slate-800">${summary.projected_yearly_savings.toFixed(2)}</span>
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-lg hover:shadow-xl transition-shadow duration-300">
                    <div className="flex justify-between items-start mb-4">
                        <div className="p-3 bg-orange-50 rounded-xl">
                            <span className="text-2xl">🗑️</span>
                        </div>
                        <span className="text-xs font-semibold text-orange-600 bg-orange-50 px-2 py-1 rounded-full">Actions</span>
                    </div>
                    <h3 className="text-slate-500 text-sm font-medium uppercase tracking-wider">Resources Cleaned</h3>
                    <div className="mt-2">
                        <span className="text-3xl font-bold text-slate-800">{summary.total_items_deleted}</span>
                    </div>
                </div>
            </div>

            {/* Recent Activity Table */}
            <div className="bg-white rounded-2xl shadow-xl border border-slate-200/50 overflow-hidden">
                <div className="p-6 border-b border-slate-100 bg-slate-50/50">
                    <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                        <span>📜</span> Recent Cleanups
                    </h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="bg-slate-50 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                                <th className="px-6 py-4">Resource</th>
                                <th className="px-6 py-4">Type</th>
                                <th className="px-6 py-4 text-right">Savings Realized</th>
                                <th className="px-6 py-4 text-right">Date</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {history.length > 0 ? (
                                history.map((item) => (
                                    <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4">
                                            <div className="font-medium text-slate-900">{item.resource_id}</div>
                                            <div className="text-xs text-slate-500">{item.region}</div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                {item.resource_type.split('::').pop()}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <span className="font-bold text-emerald-600">+${item.estimated_monthly_cost.toFixed(2)}</span>
                                            <span className="text-xs text-slate-400">/mo</span>
                                        </td>
                                        <td className="px-6 py-4 text-right text-sm text-slate-500">
                                            {new Date(item.deleted_at).toLocaleDateString()}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={4} className="px-6 py-12 text-center text-slate-400">
                                        <div className="text-4xl mb-2">🍃</div>
                                        <p>No resources cleaned yet</p>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default SavingsTracker;
