import React, { useEffect, useState } from 'react';
import { History, Package } from 'lucide-react';

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
    // Only fetch history, summary is handled by parent page now
    const [history, setHistory] = useState<SavingsItem[]>([]);
    const [loading, setLoading] = useState(true);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084/api';

    useEffect(() => {
        const fetchData = async () => {
            try {
                const historyRes = await fetch(`${apiUrl}/savings/history`);
                if (historyRes.ok) setHistory(await historyRes.json());
            } catch (error) {
                console.error("Error fetching savings history:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [apiUrl]);

    if (loading) {
        return <div className="animate-pulse h-48 bg-slate-50 rounded-lg border border-slate-200"></div>;
    }

    return (
        <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/50 flex items-center gap-2">
                <History className="w-4 h-4 text-slate-500" />
                <h3 className="text-sm font-semibold text-slate-900">Recent Cleanups</h3>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-slate-100">
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Resource</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Type</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Savings</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Date</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 bg-white">
                        {history.length > 0 ? (
                            history.map((item) => (
                                <tr key={item.id} className="hover:bg-slate-50/50 transition-colors">
                                    <td className="px-6 py-4 text-sm">
                                        <div className="font-mono text-slate-700 text-xs">{item.resource_id}</div>
                                        <div className="text-[10px] text-slate-400 mt-0.5">{item.region}</div>
                                    </td>
                                    <td className="px-6 py-4 text-sm">
                                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
                                            {item.resource_type.split('::').pop()}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-right">
                                        <span className="font-medium text-emerald-600">+${item.estimated_monthly_cost.toFixed(2)}</span>
                                        <span className="text-xs text-slate-400 ml-1">/mo</span>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-right text-slate-500">
                                        {new Date(item.deleted_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={4} className="px-6 py-12 text-center text-slate-500">
                                    <div className="flex flex-col items-center gap-2">
                                        <Package className="w-8 h-8 text-slate-300" />
                                        <p className="text-sm">No resources cleaned yet</p>
                                    </div>
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default SavingsTracker;
