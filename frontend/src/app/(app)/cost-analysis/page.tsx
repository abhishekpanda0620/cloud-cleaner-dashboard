'use client';

import { useEffect, useState } from "react";
import StatCard from "@/components/StatCard";
import NotificationCenter from "@/components/NotificationCenter";
import { useNotifications } from "@/hooks/useNotifications";
import RightSizingRecommendations from "@/components/RightSizingRecommendations";
import SavingsTracker from "@/components/SavingsTracker";
import BudgetStatus from "@/components/BudgetStatus";
import { 
  Wallet, 
  FileText, 
  Table, 
  DollarSign, 
  TrendingUp, 
   
  Package, 
  PieChart,
  LineChart,
  HardDrive,
  Database,
  Key,
  Users,
  Lock,
  Server,
  Trash2,
  CheckCircle2
} from 'lucide-react';

interface CostEstimate {
  resourceType: string;
  currentCost: number;
  potentialSavings: number;
  estimatedMonthly: number;
  resourceCount: number;
}

interface CostTrend {
  date: string;
  totalCost: number;
  savings: number;
  resourceCount: number;
}

interface CostAnalysisData {
  estimates: CostEstimate[];
  trends: CostTrend[];
  totalCurrentCost: number;
  totalPotentialSavings: number;
  totalResources: number;
}

interface SavingsSummary {
  total_monthly_savings: number;
  projected_yearly_savings: number;
  total_items_deleted: number;
  savings_last_30_days: number;
}

export default function CostAnalysis() {
  const [data, setData] = useState<CostAnalysisData>({
    estimates: [],
    trends: [],
    totalCurrentCost: 0,
    totalPotentialSavings: 0,
    totalResources: 0
  });
  const [savingsSummary, setSavingsSummary] = useState<SavingsSummary | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8084/api";
  const { notifications, addNotification, dismissNotification } = useNotifications();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const [costRes, savingsRes] = await Promise.all([
          fetch(`${apiUrl}/cost-analysis`),
          fetch(`${apiUrl}/savings/summary`)
        ]);
        
        if (costRes.ok) {
          const costData = await costRes.json();
          setData(costData);
          setIsConnected(true);
        } else {
          throw new Error(`Failed to load cost data: ${costRes.statusText}`);
        }

        if (savingsRes.ok) {
          setSavingsSummary(await savingsRes.json());
        }

      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Failed to fetch data";
        setIsConnected(false);
        addNotification({
          type: 'error',
          title: 'Data Load Failed',
          message: errorMsg,
          duration: 6000
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [apiUrl, addNotification]);

  const handleExportPDF = async () => {
    try {
      const response = await fetch(`${apiUrl}/cost-analysis/export/pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ format: 'pdf' })
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cost-analysis-${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        addNotification({
          type: 'success',
          title: 'PDF Exported',
          message: 'Cost analysis report has been downloaded',
          duration: 4000
        });
      }
    } catch {
      addNotification({ type: 'error', title: 'Export Failed', message: 'Failed', duration: 3000 });
    }
  };

  const handleExportCSV = async () => {
    try {
        const response = await fetch(`${apiUrl}/cost-analysis/export/csv`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `cost-analysis-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            addNotification({ type: 'success', title: 'CSV Exported', message: 'Done', duration: 3000 });
        }
    } catch(e) { console.error(e); }
  };


  const getResourceIcon = (type: string) => {
    switch(type) {
      case 'ec2': return <Server className="w-5 h-5 text-slate-500" />;
      case 'ebs': return <HardDrive className="w-5 h-5 text-slate-500" />;
      case 's3': return <Database className="w-5 h-5 text-slate-500" />;
      case 'iam': return <Lock className="w-5 h-5 text-slate-500" />;
      case 'iam_users': return <Users className="w-5 h-5 text-slate-500" />;
      case 'access_keys': return <Key className="w-5 h-5 text-slate-500" />;
      default: return <Package className="w-5 h-5 text-slate-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50/50">
      <NotificationCenter notifications={notifications} onDismiss={dismissNotification} />

      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-slate-100 p-2 rounded-lg border border-slate-200">
                <Wallet className="w-5 h-5 text-slate-900" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900 leading-tight">Cost Analysis</h1>
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <span className={`inline-block w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
                  {isConnected ? 'System Online' : 'System Offline'}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={handleExportPDF} className="p-2 text-slate-600 hover:bg-slate-100 rounded-md border border-slate-200 transition-colors" title="Export PDF">
                <FileText className="w-4 h-4" />
              </button>
              <button onClick={handleExportCSV} className="p-2 text-slate-600 hover:bg-slate-100 rounded-md border border-slate-200 transition-colors" title="Export CSV">
                <Table className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="px-6 py-8 space-y-8">
        
        {/* Consolidated Top Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
                title="Monthly Spend"
                value={loading ? "..." : `$${data.totalCurrentCost.toFixed(2)}`}
                icon={<DollarSign className="w-5 h-5" />}
                loading={loading}
            />
            <StatCard
                title="Potential Savings"
                value={loading ? "..." : `$${data.totalPotentialSavings.toFixed(2)}`}
                icon={<TrendingUp className="w-5 h-5" />}
                loading={loading}
            />
            <StatCard
                title="Realized Savings"
                value={loading ? "..." : `$${savingsSummary?.total_monthly_savings.toFixed(2) || '0.00'}`}
                icon={<CheckCircle2 className="w-5 h-5" />}
                loading={loading}
            />
             <StatCard
                title="Resources Cleaned"
                value={loading ? "..." : (savingsSummary?.total_items_deleted || 0).toString()}
                icon={<Trash2 className="w-5 h-5" />}
                loading={loading}
            />
        </div>

        {/* Right Sizing Opportunities - Full Width Row */}
        <div className="w-full">
            <RightSizingRecommendations />
        </div>

        {/* Main Grid: Breakdown vs Budget/Trends */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
            {/* Left Column (2/3 width) - Stretches to match height */}
            <div className="lg:col-span-2 flex flex-col">
                 {/* Cost Breakdown - Flex Grow to fill height if needed */}
                <div className="bg-white rounded-lg border border-slate-200 p-6 flex-1 flex flex-col">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                            <PieChart className="w-4 h-4 text-slate-500" />
                            Resource Cost Breakdown
                        </h2>
                    </div>
                    {loading ? (
                        <div className="animate-pulse space-y-2"><div className="h-8 bg-slate-50 rounded"></div><div className="h-8 bg-slate-50 rounded"></div></div>
                    ) : data.estimates.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 auto-rows-min">
                         {data.estimates.map((estimate, index) => (
                            <div key={index} className="flex items-center justify-between p-3 rounded-md border border-slate-100 bg-slate-50/50">
                                <div className="flex items-center space-x-3">
                                    <div className="p-1.5 bg-white rounded border border-slate-200">
                                        {getResourceIcon(estimate.resourceType)}
                                    </div>
                                    <div>
                                        <p className="font-medium text-slate-900 text-xs uppercase tracking-wide">
                                            {estimate.resourceType.split('::').pop()}
                                        </p>
                                        <p className="text-[10px] text-slate-500">
                                            {estimate.resourceCount} items
                                        </p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="font-mono text-sm font-medium text-slate-900">
                                        ${estimate.currentCost.toFixed(2)}
                                    </p>
                                    <p className="text-[10px] text-emerald-600">
                                        -${estimate.potentialSavings.toFixed(2)} possible
                                    </p>
                                </div>
                            </div>
                        ))}
                        </div>
                    ) : (
                         <div className="text-center py-8 text-slate-400 text-sm flex-1 flex items-center justify-center border border-dashed border-slate-100 rounded-lg">
                            No cost data available
                         </div>
                    )}
                </div>
            </div>

            {/* Right Column (1/3 width) */}
            <div className="space-y-6 flex flex-col">
                 <div>
                     <BudgetStatus />
                 </div>
                 
                 {/* Cost Trends */}
                 {data.trends.length > 0 && (
                  <div className="bg-white rounded-lg border border-slate-200 p-6 flex-1">
                    <h2 className="text-sm font-semibold text-slate-900 flex items-center gap-2 mb-4">
                        <LineChart className="w-4 h-4 text-slate-500" />
                         7-Day Trend
                    </h2>
                    <div className="space-y-0 divide-y divide-slate-100 border-t border-slate-100">
                      {data.trends.slice(0, 5).map((trend, index) => (
                        <div key={index} className="flex items-center justify-between py-2.5">
                          <p className="text-xs font-mono text-slate-500">{new Date(trend.date).toLocaleDateString(undefined, {weekday:'short', day:'numeric'})}</p>
                          <div className="flex items-center gap-2">
                             <span className="text-xs font-semibold text-slate-900">${trend.totalCost.toFixed(2)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
            </div>
        </div>

        {/* Realized Savings History Table - Full Width */}
        <div className="pt-2">
           <SavingsTracker />
        </div>
      </main>
    </div>
  );
}