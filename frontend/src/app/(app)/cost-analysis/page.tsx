'use client';

import NotificationCenter from "@/components/NotificationCenter";
import RightSizingRecommendations from "@/components/RightSizingRecommendations";
import SavingsTracker from "@/components/SavingsTracker";
import BudgetStatus from "@/components/BudgetStatus";
import { useCostAnalysis } from "@/hooks/useCostAnalysis";
import { CostAnalysisHeader } from "@/components/cost-analysis/CostAnalysisHeader";
import { CostAnalysisStats } from "@/components/cost-analysis/CostAnalysisStats";
import { CostBreakdown } from "@/components/cost-analysis/CostBreakdown";
import { CostTrends } from "@/components/cost-analysis/CostTrends";

export default function CostAnalysis() {
  const {
    data,
    savingsSummary,
    loading,
    isConnected,
    notifications,
    dismissNotification,
    handleExportPDF,
    handleExportCSV
  } = useCostAnalysis();

  return (
    <div className="min-h-screen bg-slate-50/50">
      <NotificationCenter notifications={notifications} onDismiss={dismissNotification} />

      {/* Header */}
      <CostAnalysisHeader 
        isConnected={isConnected} 
        onExportPDF={handleExportPDF} 
        onExportCSV={handleExportCSV} 
      />

      {/* Main Content */}
      <main className="px-6 py-8 space-y-8">
        
        {/* Consolidated Top Stats */}
        <CostAnalysisStats 
            data={data} 
            savingsSummary={savingsSummary} 
            loading={loading} 
        />

        {/* Right Sizing Opportunities - Full Width Row */}
        <div className="w-full">
            <RightSizingRecommendations />
        </div>

        {/* Main Grid: Breakdown vs Budget/Trends */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
            {/* Left Column (2/3 width) - Stretches to match height */}
            <div className="lg:col-span-2 flex flex-col">
                 {/* Cost Breakdown - Flex Grow to fill height if needed */}
                <CostBreakdown estimates={data.estimates} loading={loading} />
            </div>

            {/* Right Column (1/3 width) */}
            <div className="space-y-6 flex flex-col">
                 <div>
                     <BudgetStatus />
                 </div>
                 
                 {/* Cost Trends */}
                 <CostTrends trends={data.trends} />
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