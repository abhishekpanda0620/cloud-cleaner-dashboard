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
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      {/* Notification Center */}
      <NotificationCenter
        notifications={notifications}
        onDismiss={dismissNotification}
      />

      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/50 shadow-lg sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="h-12 w-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-2xl">💰</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                  Cost Analysis Dashboard
                </h1>
                <p className="mt-1 text-sm text-slate-600 flex items-center gap-2">
                  <span>Track costs and identify savings opportunities</span>
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    <span className={`h-1.5 w-1.5 rounded-full mr-1 ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
                    {isConnected ? 'Live' : 'Offline'}
                  </span>
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleExportPDF}
                className="group px-4 py-2.5 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-lg hover:from-red-700 hover:to-pink-700 transition-all duration-200 text-sm font-medium shadow-md hover:shadow-lg transform hover:-translate-y-0.5 flex items-center gap-2"
              >
                <span className="text-lg">📄</span>
                <span>Export PDF</span>
              </button>
              <button
                onClick={handleExportCSV}
                className="group px-4 py-2.5 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all duration-200 text-sm font-medium shadow-md hover:shadow-lg transform hover:-translate-y-0.5 flex items-center gap-2"
              >
                <span className="text-lg">📊</span>
                <span>Export CSV</span>
              </button>
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
        <div className="bg-white rounded-2xl shadow-xl border border-slate-200/50 p-8 hover:shadow-2xl transition-shadow duration-300">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
              <span className="h-10 w-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center text-white">
                💎
              </span>
              Cost Breakdown by Resource Type
            </h2>
          </div>
          
          {loading ? (
            <div className="animate-pulse space-y-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-16 bg-slate-200 rounded"></div>
              ))}
            </div>
          ) : data.estimates.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.estimates.map((estimate, index) => {
                const colors = [
                  { bg: 'from-blue-500 to-blue-600', light: 'bg-blue-50', border: 'border-blue-200' },
                  { bg: 'from-purple-500 to-purple-600', light: 'bg-purple-50', border: 'border-purple-200' },
                  { bg: 'from-orange-500 to-orange-600', light: 'bg-orange-50', border: 'border-orange-200' },
                  { bg: 'from-green-500 to-green-600', light: 'bg-green-50', border: 'border-green-200' },
                  { bg: 'from-indigo-500 to-indigo-600', light: 'bg-indigo-50', border: 'border-indigo-200' },
                  { bg: 'from-red-500 to-red-600', light: 'bg-red-50', border: 'border-red-200' }
                ];
                const color = colors[index % colors.length];
                
                return (
                  <div key={index} className={`group relative overflow-hidden rounded-xl border-2 ${color.border} ${color.light} p-5 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1`}>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-4">
                        <div className={`h-14 w-14 bg-gradient-to-br ${color.bg} rounded-xl flex items-center justify-center shadow-md group-hover:scale-110 transition-transform duration-300`}>
                          <span className="text-2xl">
                            {estimate.resourceType === 'ec2' && '🖥️'}
                            {estimate.resourceType === 'ebs' && '💾'}
                            {estimate.resourceType === 's3' && '🪣'}
                            {estimate.resourceType === 'iam' && '🔐'}
                            {estimate.resourceType === 'iam_users' && '👥'}
                            {estimate.resourceType === 'access_keys' && '🔑'}
                          </span>
                        </div>
                        <div>
                          <h3 className="font-bold text-slate-900 text-lg">
                            {estimate.resourceType.replace('_', ' ').toUpperCase()}
                          </h3>
                          <p className="text-sm text-slate-600 flex items-center gap-1">
                            <span className="font-semibold">{estimate.resourceCount}</span>
                            <span>unused resource{estimate.resourceCount !== 1 ? 's' : ''}</span>
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 pt-4 border-t border-slate-200">
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="text-xs text-slate-500 uppercase tracking-wide font-medium">Potential Savings</p>
                          <p className="text-2xl font-bold text-emerald-600">
                            ${estimate.potentialSavings.toFixed(2)}
                            <span className="text-sm font-normal text-slate-500">/mo</span>
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-slate-500 uppercase tracking-wide font-medium">Avg/Resource</p>
                          <p className="text-lg font-semibold text-slate-700">
                            ${estimate.estimatedMonthly.toFixed(2)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
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
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200/50 p-8 hover:shadow-2xl transition-shadow duration-300">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
                <span className="h-10 w-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center text-white">
                  📈
                </span>
                Cost Trends (Last 7 Days)
              </h2>
            </div>
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
        <div className="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl shadow-2xl p-8 text-white">
          <div className="flex items-center gap-3 mb-6">
            <span className="h-12 w-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center text-3xl">
              💡
            </span>
            <h2 className="text-2xl font-bold">
              Savings Calculator
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="group text-center p-8 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 hover:bg-white/20 transition-all duration-300 transform hover:scale-105">
              <div className="text-5xl mb-3 group-hover:scale-110 transition-transform duration-300">📅</div>
              <h3 className="font-semibold text-white/90 text-sm uppercase tracking-wide mb-2">Daily Savings</h3>
              <p className="text-4xl font-bold text-white drop-shadow-lg">
                ${(data.totalPotentialSavings / 30).toFixed(2)}
              </p>
              <p className="text-white/70 text-sm mt-2">per day</p>
            </div>
            <div className="group text-center p-8 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 hover:bg-white/20 transition-all duration-300 transform hover:scale-105">
              <div className="text-5xl mb-3 group-hover:scale-110 transition-transform duration-300">📊</div>
              <h3 className="font-semibold text-white/90 text-sm uppercase tracking-wide mb-2">Monthly Savings</h3>
              <p className="text-4xl font-bold text-white drop-shadow-lg">
                ${data.totalPotentialSavings.toFixed(2)}
              </p>
              <p className="text-white/70 text-sm mt-2">per month</p>
            </div>
            <div className="group text-center p-8 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 hover:bg-white/20 transition-all duration-300 transform hover:scale-105">
              <div className="text-5xl mb-3 group-hover:scale-110 transition-transform duration-300">🎯</div>
              <h3 className="font-semibold text-white/90 text-sm uppercase tracking-wide mb-2">Yearly Savings</h3>
              <p className="text-4xl font-bold text-white drop-shadow-lg">
                ${(data.totalPotentialSavings * 12).toFixed(2)}
              </p>
              <p className="text-white/70 text-sm mt-2">per year</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}