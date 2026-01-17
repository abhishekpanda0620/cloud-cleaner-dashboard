import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { SecurityStats, SecurityFinding } from '@/types/security';

interface SecurityStatsProps {
  stats: SecurityStats | null;
  findings: SecurityFinding[];
}

export function SecurityStatsCards({ stats, findings }: SecurityStatsProps) {
  const criticalCount = findings.filter(f => f.status === 'FAIL' && f.severity === 'Critical').length;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <p className="text-sm font-medium text-slate-500 mb-1">Compliance Score</p>
        <div className="flex items-baseline gap-2">
          <span className={`text-2xl font-bold ${
            (stats?.score || 0) >= 80 ? 'text-green-600' : 
            (stats?.score || 0) >= 50 ? 'text-amber-500' : 'text-red-500'
          }`}>
            {stats?.score || 0}%
          </span>
        </div>
      </div>
      
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <p className="text-sm font-medium text-slate-500 mb-1">Passing Checks</p>
        <div className="flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-green-500" />
          <span className="text-2xl font-bold text-slate-900">{stats?.pass || 0}</span>
        </div>
      </div>

      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <p className="text-sm font-medium text-slate-500 mb-1">Failing Checks</p>
        <div className="flex items-center gap-2">
          <XCircle className="w-5 h-5 text-red-500" />
          <span className="text-2xl font-bold text-slate-900">{stats?.fail || 0}</span>
        </div>
      </div>
      
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <p className="text-sm font-medium text-slate-500 mb-1">Critical Issues</p>
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          <span className="text-2xl font-bold text-slate-900">
            {criticalCount}
          </span>
        </div>
      </div>
    </div>
  );
}
