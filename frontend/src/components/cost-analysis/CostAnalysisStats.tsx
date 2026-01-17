import { DollarSign, TrendingUp, CheckCircle2, Trash2 } from 'lucide-react';
import StatCard from "@/components/StatCard";
import { CostAnalysisData, SavingsSummary } from '@/types/cost-analysis';

interface CostAnalysisStatsProps {
  data: CostAnalysisData;
  savingsSummary: SavingsSummary | null;
  loading: boolean;
}

export function CostAnalysisStats({ data, savingsSummary, loading }: CostAnalysisStatsProps) {
  return (
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
  );
}
