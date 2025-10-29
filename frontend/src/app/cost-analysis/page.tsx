"use client"
import { useEffect, useState } from "react";
import StatCard from "@/components/StatCard";
import NotificationCenter from "@/components/NotificationCenter";
import { useNotifications } from "@/hooks/useNotifications";

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

export default function CostAnalysis() {
  const [data, setData] = useState<CostAnalysisData>({
    estimates: [],
    trends: [],
    totalCurrentCost: 0,
    totalPotentialSavings: 0,
    totalResources: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8084/api";
  const { notifications, addNotification, dismissNotification } = useNotifications();

  useEffect(() => {
    const fetchCostData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`${apiUrl}/cost-analysis`);
        
        if (response.ok) {
          const costData = await response.json();
          setData(costData);
          setIsConnected(true);
          addNotification({
            type: 'success',
            title: 'Cost Analysis Loaded',
            message: `Found $${costData.totalPotentialSavings.toFixed(2)} in potential monthly savings`,
            duration: 4000
          });
        } else {
          throw new Error(`Failed to load cost data: ${response.statusText}`);
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Failed to fetch cost data";
        setError(errorMsg);
        setIsConnected(false);
        addNotification({
          type: 'error',
          title: 'Cost Analysis Failed',
          message: errorMsg,
          duration: 6000
        });
      } finally {
        setLoading(false);
      }
    };

    fetchCostData();
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
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Export Failed',
        message: 'Failed to generate PDF report',
        duration: 6000
      });
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
        
        addNotification({
          type: 'success',
          title: 'CSV Exported',
          message: 'Cost analysis data has been downloaded',
          duration: 4000
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Export Failed',
        message: 'Failed to export CSV data',
        duration: 6000
      });
    }
  };

  const savingsPercentage = data.totalCurrentCost > 0 
    ? ((data.totalPotentialSavings / data.totalCurrentCost) * 100).toFixed(1)
    : '0';

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50">
      {/* Notification Center */}
      <NotificationCenter
        notifications={notifications}
        onDismiss={dismissNotification}
      />

      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">
                💰 Cost Analysis Dashboard
              </h1>
              <p className="mt-1 text-sm text-slate-600">
                Track costs and identify potential savings opportunities
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex space-x-2">
                <button
                  onClick={handleExportPDF}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
                >
                  📄 Export PDF
                </button>
                <button
                  onClick={handleExportCSV}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                >
                  📊 Export CSV
                </button>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                <span className="text-sm text-slate-600">{isConnected ? 'Connected' : 'Not Connected'}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard
            title="Current Monthly Cost"
            value={loading ? "..." : `$${data.totalCurrentCost.toFixed(2)}`}
            icon="💸"
            bgColor="bg-blue-500"
            loading={loading}
          />
          <StatCard
            title="Potential Savings"
            value={loading ? "..." : `$${data.totalPotentialSavings.toFixed(2)}`}
            icon="💚"
            bgColor="bg-emerald-500"
            loading={loading}
          />
          <StatCard
            title="Savings Percentage"
            value={loading ? "..." : `${savingsPercentage}%`}
            icon="📈"
            bgColor="bg-purple-500"
            loading={loading}
          />
          <StatCard
            title="Unutilized Resources"
            value={loading ? "..." : data.totalResources.toString()}
            icon="📦"
            bgColor="bg-orange-500"
            loading={loading}
          />
        </div>

        {/* Cost Breakdown */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">
            Cost Breakdown by Resource Type
          </h2>
          
          {loading ? (
            <div className="animate-pulse space-y-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-16 bg-slate-200 rounded"></div>
              ))}
            </div>
          ) : data.estimates.length > 0 ? (
            <div className="space-y-4">
              {data.estimates.map((estimate, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 bg-blue-500 rounded-lg flex items-center justify-center">
                      <span className="text-white text-sm">
                        {estimate.resourceType === 'ec2' && '🖥️'}
                        {estimate.resourceType === 'ebs' && '💾'}
                        {estimate.resourceType === 's3' && '🪣'}
                        {estimate.resourceType === 'iam' && '🔐'}
                        {estimate.resourceType === 'iam_users' && '👥'}
                        {estimate.resourceType === 'access_keys' && '🔑'}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-medium text-slate-900">
                        {estimate.resourceType.replace('_', ' ').toUpperCase()}
                      </h3>
                      <p className="text-sm text-slate-600">
                        {estimate.resourceCount} unused resource{estimate.resourceCount !== 1 ? 's' : ''}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-slate-900">
                      ${estimate.potentialSavings.toFixed(2)}/mo
                    </div>
                    <div className="text-sm text-slate-600">
                      Est. ${estimate.estimatedMonthly.toFixed(2)}/resource
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">✨</div>
              <h3 className="text-lg font-medium text-slate-900 mb-2">
                No cost analysis available
              </h3>
              <p className="text-slate-600">
                Connect to AWS and scan your resources to see cost estimates
              </p>
            </div>
          )}
        </div>

        {/* Cost Trends */}
        {data.trends.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h2 className="text-xl font-semibold text-slate-900 mb-4">
              Cost Trends (Last 30 Days)
            </h2>
            <div className="space-y-4">
              {data.trends.slice(0, 7).map((trend, index) => (
                <div key={index} className="flex items-center justify-between p-4 border border-slate-200 rounded-lg">
                  <div>
                    <h3 className="font-medium text-slate-900">
                      {new Date(trend.date).toLocaleDateString()}
                    </h3>
                    <p className="text-sm text-slate-600">
                      {trend.resourceCount} resources
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-slate-900">
                      ${trend.totalCost.toFixed(2)}
                    </div>
                    <div className="text-sm text-emerald-600">
                      ${trend.savings.toFixed(2)} saved
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Savings Calculator */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">
            💡 Savings Calculator
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-emerald-50 rounded-lg">
              <div className="text-3xl mb-2">📅</div>
              <h3 className="font-semibold text-slate-900">Daily</h3>
              <p className="text-2xl font-bold text-emerald-600">
                ${(data.totalPotentialSavings / 30).toFixed(2)}
              </p>
            </div>
            <div className="text-center p-6 bg-blue-50 rounded-lg">
              <div className="text-3xl mb-2">📅</div>
              <h3 className="font-semibold text-slate-900">Monthly</h3>
              <p className="text-2xl font-bold text-blue-600">
                ${data.totalPotentialSavings.toFixed(2)}
              </p>
            </div>
            <div className="text-center p-6 bg-purple-50 rounded-lg">
              <div className="text-3xl mb-2">📅</div>
              <h3 className="font-semibold text-slate-900">Yearly</h3>
              <p className="text-2xl font-bold text-purple-600">
                ${(data.totalPotentialSavings * 12).toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}