import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, AlertOctagon, TrendingDown, Settings, Plus } from 'lucide-react';
import BudgetConfigModal from './BudgetConfigModal';

interface Budget {
    name: string;
    limit: number;
    unit: string;
    current_spend: number;
    percent_used: number;
    status: 'OK' | 'WARNING' | 'ALARM';
    time_period_start: string;
    time_period_end: string;
    type?: 'AWS' | 'NATIVE';
}

const BudgetStatus: React.FC = () => {
    const [budgets, setBudgets] = useState<Budget[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084/api';

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

    useEffect(() => {
        fetchBudgets();
    }, [apiUrl]);

    if (loading) return <div className="h-40 bg-slate-50 border border-slate-200 rounded-lg animate-pulse"></div>;
    
    // Check if we have a native budget to pre-fill the modal
    const nativeBudget = budgets.find(b => b.type === 'NATIVE');
    const hasAwsBudgets = budgets.some(b => b.type === 'AWS');

    if (budgets.length === 0) {
        return (
            <>
                <div className="bg-white rounded-lg border border-slate-200 p-6 flex flex-col items-center justify-center text-center">
                    <div className="p-3 bg-slate-50 rounded-full mb-3">
                        <TrendingDown className="w-5 h-5 text-slate-400" />
                    </div>
                    <h3 className="text-sm font-semibold text-slate-900">No Budgets Configured</h3>
                    <p className="text-xs text-slate-500 mt-1 max-w-xs mb-4">
                        Set a monthly spending limit to get alerts when you're over budget.
                    </p>
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors"
                    >
                        <Plus className="w-3 h-3" />
                        Set Monthly Budget
                    </button>
                </div>
                <BudgetConfigModal 
                    isOpen={isModalOpen} 
                    onClose={() => setIsModalOpen(false)} 
                    onSave={fetchBudgets}
                />
            </>
        );
    }

    return (
        <div className="bg-white rounded-lg border border-slate-200 p-6">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                    <TrendingDown className="w-4 h-4 text-slate-500" />
                    Budget Status
                </h2>
                <div className="flex items-center gap-2">
                    <span className="bg-slate-100 text-slate-600 text-[10px] font-medium px-2 py-0.5 rounded-full border border-slate-200">
                        {budgets.length} Active
                    </span>
                    {/* Only allow configuring if using Native budgets or if we want to override */}
                    {!hasAwsBudgets && (
                        <button 
                            onClick={() => setIsModalOpen(true)}
                            className="p-1 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors"
                            title="Configure Budget"
                        >
                            <Settings className="w-3.5 h-3.5" />
                        </button>
                    )}
                </div>
            </div>
            
            <div className="space-y-5">
                {budgets.map((budget, index) => {
                    const isAlarm = budget.status === 'ALARM';
                    const isWarning = budget.status === 'WARNING';
                    
                    let statusColor = 'text-emerald-600';
                    let barColor = 'bg-emerald-500';
                    let Icon = CheckCircle2;

                    if (isAlarm) {
                        statusColor = 'text-red-600';
                        barColor = 'bg-red-500';
                        Icon = AlertOctagon;
                    } else if (isWarning) {
                        statusColor = 'text-amber-600';
                        barColor = 'bg-amber-500';
                        Icon = AlertTriangle;
                    }

                    return (
                        <div key={index} className="space-y-2">
                            <div className="flex justify-between items-start">
                                <div>
                                    <div className="flex items-center gap-1.5">
                                        <h3 className="text-sm font-medium text-slate-900">{budget.name}</h3>
                                        {isAlarm && <AlertOctagon className="w-3 h-3 text-red-500" />}
                                        {budget.type === 'NATIVE' && (
                                            <span className="text-[9px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded border border-slate-200">
                                                NATIVE
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-[10px] text-slate-400 font-mono mt-0.5">
                                        {budget.time_period_start && new Date(budget.time_period_start).toLocaleDateString()} 
                                        {budget.time_period_end && budget.time_period_end !== 'N/A' 
                                            ? ` - ${new Date(budget.time_period_end).toLocaleDateString()}` 
                                            : ' (Recurring)'}
                                    </p>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm font-semibold text-slate-900">
                                        ${budget.current_spend.toFixed(2)} <span className="text-slate-400 font-normal text-xs">/ ${budget.limit.toFixed(2)}</span>
                                    </p>
                                </div>
                            </div>
                            
                            <div className="relative pt-1">
                                <div className="flex mb-1 items-center justify-between">
                                    <span className={`text-[10px] font-semibold inline-block ${statusColor} flex items-center gap-1`}>
                                        <Icon className="w-3 h-3" />
                                        {budget.status}
                                    </span>
                                    <span className="text-[10px] font-semibold inline-block text-slate-600">
                                        {budget.percent_used.toFixed(1)}%
                                    </span>
                                </div>
                                <div className="overflow-hidden h-1.5 text-xs flex rounded bg-slate-100">
                                    <div 
                                        style={{ width: `${Math.min(budget.percent_used, 100)}%` }} 
                                        className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${barColor} transition-all duration-500`}
                                    ></div>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
            
            <BudgetConfigModal 
                isOpen={isModalOpen} 
                onClose={() => setIsModalOpen(false)} 
                onSave={fetchBudgets}
                currentLimit={nativeBudget?.limit}
            />
        </div>
    );
};

export default BudgetStatus;
