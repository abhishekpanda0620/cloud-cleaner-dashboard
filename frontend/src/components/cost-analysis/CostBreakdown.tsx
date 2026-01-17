import { PieChart, Server, HardDrive, Database, Lock, Users, Key, Package } from 'lucide-react';
import { CostEstimate } from '@/types/cost-analysis';

interface CostBreakdownProps {
  estimates: CostEstimate[];
  loading: boolean;
}

export function CostBreakdown({ estimates, loading }: CostBreakdownProps) {
  
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
    <div className="bg-white rounded-lg border border-slate-200 p-6 flex-1 flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
          <PieChart className="w-4 h-4 text-slate-500" />
          Resource Cost Breakdown
        </h2>
      </div>
      {loading ? (
        <div className="animate-pulse space-y-2"><div className="h-8 bg-slate-50 rounded"></div><div className="h-8 bg-slate-50 rounded"></div></div>
      ) : estimates.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 auto-rows-min">
          {estimates.map((estimate, index) => (
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
  );
}
