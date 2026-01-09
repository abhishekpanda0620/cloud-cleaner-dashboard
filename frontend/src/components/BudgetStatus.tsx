import React, { useEffect, useState } from 'react';

interface Budget {
    name: string;
    limit: number;
    unit: string;
    current_spend: number;
    percent_used: number;
    status: 'OK' | 'WARNING' | 'ALARM';
    time_period_start: string;
    time_period_end: string;
}

const BudgetStatus: React.FC = () => {
    const [budgets, setBudgets] = useState<Budget[]>([]);
    const [loading, setLoading] = useState(true);
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084/api';

    useEffect(() => {
        const fetchBudgets = async () => {
            try {
                const response = await fetch(`${apiUrl}/budgets`);
                if (response.ok) {
                    const data = await response.json();
                    setBudgets(data);
                }
            } catch (error) {
                console.error("Error fetching budgets:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchBudgets();
    }, [apiUrl]);

    if (loading) return <div className="h-48 bg-slate-100 rounded-xl animate-pulse"></div>;
    
    if (budgets.length === 0) {
        return (
            <div className="bg-white rounded-2xl shadow-xl border border-slate-200/50 p-8">
                <div className="flex items-center gap-3 mb-6">
                    <span className="h-10 w-10 bg-gradient-to-br from-amber-500 to-orange-600 rounded-lg flex items-center justify-center text-white">
                        ⚠️
                    </span>
                    <h2 className="text-xl font-bold text-slate-900">AWS Budgets</h2>
                </div>
                <div className="text-center py-8 text-slate-500">
                    <p>No budgets configured or permission denied.</p>
                    <p className="text-xs mt-2">Set up budgets in AWS Console to see alerts here.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-2xl shadow-xl border border-slate-200/50 p-8 hover:shadow-2xl transition-shadow duration-300">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
                    <span className="h-10 w-10 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-lg flex items-center justify-center text-white">
                        📉
                    </span>
                    Budget Status
                </h2>
                <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                    {budgets.length} Active
                </span>
            </div>
            
            <div className="space-y-6">
                {budgets.map((budget, index) => (
                    <div key={index} className="space-y-2">
                        <div className="flex justify-between items-end">
                            <div>
                                <h3 className="font-semibold text-slate-900">{budget.name}</h3>
                                <p className="text-xs text-slate-500">
                                    {new Date(budget.time_period_start).toLocaleDateString()} - {new Date(budget.time_period_end).toLocaleDateString()}
                                </p>
                            </div>
                            <div className="text-right">
                                <p className="font-bold text-slate-900">
                                    ${budget.current_spend.toFixed(2)} <span className="text-slate-400 font-normal">/ ${budget.limit.toFixed(2)}</span>
                                </p>
                                <p className={`text-xs font-semibold ${
                                    budget.status === 'ALARM' ? 'text-red-600' : 
                                    budget.status === 'WARNING' ? 'text-amber-600' : 'text-emerald-600'
                                }`}>
                                    {budget.percent_used.toFixed(1)}% Used
                                </p>
                            </div>
                        </div>
                        
                        <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden">
                            <div 
                                className={`h-full rounded-full transition-all duration-1000 ${
                                    budget.status === 'ALARM' ? 'bg-red-500' : 
                                    budget.status === 'WARNING' ? 'bg-amber-500' : 'bg-emerald-500'
                                }`}
                                style={{ width: `${Math.min(budget.percent_used, 100)}%` }}
                            ></div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default BudgetStatus;
