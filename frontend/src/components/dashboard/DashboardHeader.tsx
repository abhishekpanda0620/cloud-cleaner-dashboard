import { LayoutGrid } from 'lucide-react';

interface DashboardHeaderProps {
  selectedRegions: string[];
}

export function DashboardHeader({ selectedRegions }: DashboardHeaderProps) {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-10 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-slate-100 p-2 rounded-lg border border-slate-200">
            <LayoutGrid className="w-5 h-5 text-slate-900" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-slate-900 leading-tight">
              Resource Dashboard
            </h1>
            <p className="text-sm text-slate-500">
              Dynamic AWS Discovery
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="px-2 py-1 text-xs font-medium bg-slate-100 text-slate-600 rounded border border-slate-200">
            {selectedRegions.length === 0 ? 'All Regions' : 
             selectedRegions.length === 1 ? selectedRegions[0] : 
             `${selectedRegions.length} Regions`}
          </span>
        </div>
      </div>
    </header>
  );
}
