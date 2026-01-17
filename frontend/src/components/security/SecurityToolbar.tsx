import { Search, ListFilter, ArrowUpDown } from 'lucide-react';

interface SecurityToolbarProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  resultCount: number;
  statusFilter: 'ALL' | 'PASS' | 'FAIL';
  onFilterChange: (value: 'ALL' | 'PASS' | 'FAIL') => void;
  onSortToggle: () => void;
}

export function SecurityToolbar({
  searchQuery,
  onSearchChange,
  resultCount,
  statusFilter,
  onFilterChange,
  onSortToggle
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
        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <ListFilter className="w-4 h-4 text-slate-400" />
          <select 
            value={statusFilter}
            onChange={(e) => onFilterChange(e.target.value as 'ALL' | 'PASS' | 'FAIL')}
            className="text-sm border border-slate-300 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
          >
            <option value="ALL">All Status</option>
            <option value="FAIL">Failing</option>
            <option value="PASS">Passing</option>
          </select>
        </div>

        {/* Sort Toggle */}
        <button 
          onClick={onSortToggle}
          className="flex items-center gap-2 px-3 py-1.5 border border-slate-300 rounded-lg text-sm bg-white hover:bg-slate-50 transition-colors"
          title="Sort by Severity"
        >
          <ArrowUpDown className="w-4 h-4 text-slate-500" />
          <span className="text-slate-700">Severity</span>
        </button>

        <div className="text-xs text-slate-500 ml-2">
          {resultCount} results
        </div>
      </div>
    </div>
  );
}
