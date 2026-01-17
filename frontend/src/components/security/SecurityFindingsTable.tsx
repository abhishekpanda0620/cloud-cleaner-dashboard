import { Eye, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { Skeleton } from '@/components/Skeleton';
import { SecurityFinding } from '@/types/security';

interface SecurityFindingsTableProps {
  findings: SecurityFinding[];
  loading: boolean;
  onViewDetails: (finding: SecurityFinding) => void;
  emptyMessage?: string;
}

export function SecurityFindingsTable({ findings, loading, onViewDetails, emptyMessage }: SecurityFindingsTableProps) {
  
  const getSeverityColor = (severity: string) => {
    switch(severity) {
      case 'Critical': return 'text-red-700 bg-red-50 border-red-200';
      case 'High': return 'text-orange-700 bg-orange-50 border-orange-200';
      case 'Medium': return 'text-amber-700 bg-amber-50 border-amber-200';
      case 'Low': return 'text-blue-700 bg-blue-50 border-blue-200';
      default: return 'text-slate-700 bg-slate-50 border-slate-200';
    }
  };

  return (
    <div className="flex-1 overflow-y-auto">
      <table className="w-full text-sm text-left">
        <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200 sticky top-0 z-10">
          <tr>
            <th className="px-6 py-3 bg-slate-50">Status</th>
            <th className="px-6 py-3 bg-slate-50">Control / Check</th>
            <th className="px-6 py-3 bg-slate-50">Severity</th>
            <th className="px-6 py-3 bg-slate-50">Resource</th>
            <th className="px-6 py-3 bg-slate-50 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {loading ? (
            Array.from({ length: 5 }).map((_, i) => (
              <tr key={i}>
                <td className="px-6 py-4"><Skeleton className="h-6 w-16 rounded-full" /></td>
                <td className="px-6 py-4">
                  <Skeleton className="h-5 w-48 mb-1" />
                  <Skeleton className="h-3 w-24" />
                </td>
                <td className="px-6 py-4"><Skeleton className="h-5 w-20" /></td>
                <td className="px-6 py-4">
                  <Skeleton className="h-5 w-40 mb-1" />
                  <Skeleton className="h-3 w-24" />
                </td>
                <td className="px-6 py-4"><Skeleton className="h-8 w-8 rounded-full ml-auto" /></td>
              </tr>
            ))
          ) : findings.length === 0 ? (
            <tr>
              <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                {emptyMessage || 'No findings found.'}
              </td>
            </tr>
          ) : (
            findings.map((finding) => (
              <tr key={finding.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4">
                  {finding.status === 'PASS' ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200">
                      <CheckCircle className="w-3.5 h-3.5" />
                      Pass
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200">
                      <XCircle className="w-3.5 h-3.5" />
                      Fail
                    </span>
                  )}
                </td>
                <td className="px-6 py-4">
                  <div className="font-medium text-slate-900">{finding.check_name}</div>
                  <code className="text-xs text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded mt-1 inline-block">
                    {finding.check_id}
                  </code>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex px-2 py-0.5 rounded text-xs font-medium border ${getSeverityColor(finding.severity)}`}>
                    {finding.severity}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="font-medium text-slate-900 truncate max-w-[200px]" title={finding.resource_id}>
                    {finding.resource_id}
                  </div>
                  <div className="text-xs text-slate-500">{finding.resource_type}</div>
                </td>
                <td className="px-6 py-4 text-right">
                  <button 
                    onClick={() => onViewDetails(finding)}
                    className="text-slate-400 hover:text-blue-600 transition-colors p-2 hover:bg-blue-50 rounded-lg"
                    title="View Details"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
