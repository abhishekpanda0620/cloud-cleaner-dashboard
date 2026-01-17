import { Search, ListFilter, AlertTriangle } from 'lucide-react';
import { Select } from '@/components/ui/Select';

interface SecurityToolbarProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  resultCount: number;
  statusFilter: 'ALL' | 'PASS' | 'FAIL';
  onFilterChange: (value: 'ALL' | 'PASS' | 'FAIL') => void;
  severityFilter: 'ALL' | 'Critical' | 'High' | 'Medium' | 'Low';
  onSeverityFilterChange: (value: 'ALL' | 'Critical' | 'High' | 'Medium' | 'Low') => void;
}

export function SecurityToolbar({
  searchQuery,
  onSearchChange,
  resultCount,
  statusFilter,
  onFilterChange,
  severityFilter,
  onSeverityFilterChange
}: SecurityToolbarProps) {
  return (
    <div className="px-6 py-4 border-b border-slate-200 flex flex-col sm:flex-row justify-between items-center bg-slate-50 shrink-0 gap-4">
      <div className="flex items-center gap-4 w-full sm:w-auto">
        <h3 className="font-semibold text-slate-900">Findings</h3>
        <div className="relative flex-1 sm:flex-none">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search findings..." 
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-9 pr-4 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 w-full sm:w-64"
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Severity Filter */}
        <div className="w-40">
           <Select
             value={severityFilter}
             onChange={(val) => onSeverityFilterChange(val as any)}
             icon={<AlertTriangle className="w-4 h-4" />}
             options={[
               { value: 'ALL', label: 'All Severities' },
               { value: 'Critical', label: 'Critical' },
               { value: 'High', label: 'High' },
               { value: 'Medium', label: 'Medium' },
               { value: 'Low', label: 'Low' }
             ]}
           />
        </div>

        {/* Status Filter */}
        <div className="w-40">
           <Select
             value={statusFilter}
             onChange={(val) => onFilterChange(val as 'ALL' | 'PASS' | 'FAIL')}
             icon={<ListFilter className="w-4 h-4" />}
             options={[
               { value: 'ALL', label: 'All Status' },
               { value: 'FAIL', label: 'Failing' },
               { value: 'PASS', label: 'Passing' }
             ]}
           />
        </div>

        <div className="text-xs text-slate-500 ml-2">
          {resultCount} results
        </div>
      </div>
    </div>
  );
}
