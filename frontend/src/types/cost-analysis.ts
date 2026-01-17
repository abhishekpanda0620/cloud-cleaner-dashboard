export interface CostEstimate {
  resourceType: string;
  currentCost: number;
  potentialSavings: number;
  estimatedMonthly: number;
  resourceCount: number;
}

export interface CostTrend {
  date: string;
  totalCost: number;
  savings: number;
  resourceCount: number;
}

export interface CostAnalysisData {
  estimates: CostEstimate[];
  trends: CostTrend[];
  totalCurrentCost: number;
  totalPotentialSavings: number;
  totalResources: number;
}

export interface SavingsSummary {
  total_monthly_savings: number;
  projected_yearly_savings: number;
  total_items_deleted: number;
  savings_last_30_days: number;
}
