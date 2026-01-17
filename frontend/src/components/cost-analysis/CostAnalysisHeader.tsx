import { Wallet, FileText, Table } from 'lucide-react';

interface CostAnalysisHeaderProps {
  isConnected: boolean;
  onExportPDF: () => void;
  onExportCSV: () => void;
}

export function CostAnalysisHeader({ isConnected, onExportPDF, onExportCSV }: CostAnalysisHeaderProps) {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-slate-100 p-2 rounded-lg border border-slate-200">
              <Wallet className="w-5 h-5 text-slate-900" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-slate-900 leading-tight">Cost Analysis</h1>
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <span className={`inline-block w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
                {isConnected ? 'System Online' : 'System Offline'}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={onExportPDF} className="p-2 text-slate-600 hover:bg-slate-100 rounded-md border border-slate-200 transition-colors" title="Export PDF">
              <FileText className="w-4 h-4" />
            </button>
            <button onClick={onExportCSV} className="p-2 text-slate-600 hover:bg-slate-100 rounded-md border border-slate-200 transition-colors" title="Export CSV">
              <Table className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
