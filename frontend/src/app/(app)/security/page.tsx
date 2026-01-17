'use client';

import { useState } from 'react';
import { ShieldCheck, RefreshCw, AlertTriangle, Download, ChevronLeft, ChevronRight } from 'lucide-react';
import { useSecurityFindings } from '@/hooks/useSecurityFindings';
import { SecurityStatsCards } from '@/components/security/SecurityStats';
import { SecurityToolbar } from '@/components/security/SecurityToolbar';
import { SecurityFindingsTable } from '@/components/security/SecurityFindingsTable';
import { FindingDetailsModal } from '@/components/FindingDetailsModal';
import { SecurityFinding } from '@/types/security';

export default function SecurityPage() {
  const { stats, findings, loading, scanning, triggerScan, useFilteredFindings, apiUrl } = useSecurityFindings();

  // UI State
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'PASS' | 'FAIL'>('ALL');
  const [severityFilter, setSeverityFilter] = useState<'ALL' | 'Critical' | 'High' | 'Medium' | 'Low'>('ALL');
  const [sortConfig, setSortConfig] = useState<{ key: string, direction: 'asc' | 'desc' }>({ key: 'severity', direction: 'desc' });
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedFinding, setSelectedFinding] = useState<SecurityFinding | null>(null);
  const itemsPerPage = 10;

  const filteredFindings = useFilteredFindings(searchQuery, statusFilter, severityFilter, sortConfig);

  const handleSort = (key: string) => {
    setSortConfig(current => ({
      key,
      direction: current.key === key && current.direction === 'desc' ? 'asc' : 'desc'
    }));
  };

  const totalPages = Math.ceil(filteredFindings.length / itemsPerPage);
  const currentFindings = filteredFindings.slice(
      (currentPage - 1) * itemsPerPage, 
      currentPage * itemsPerPage
  );

  return (
    <div className="min-h-full">
      <FindingDetailsModal 
        finding={selectedFinding} 
        isOpen={!!selectedFinding} 
        onClose={() => setSelectedFinding(null)} 
      />

      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-indigo-50 p-2 rounded-lg border border-indigo-100">
               <ShieldCheck className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900 leading-tight">
                Security & Compliance
              </h1>
              <p className="text-sm text-slate-500">
                CIS AWS Foundations Benchmark v1.4.0
              </p>
            </div>
          </div>
          
          <div className="flex gap-3">
            <button
               onClick={() => window.open(`${apiUrl}/security/export`, '_blank')}
               className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 shadow-sm transition-all"
            >
              <Download className="w-4 h-4" />
              Export Report
            </button>
            <button
                onClick={triggerScan}
                disabled={scanning}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                scanning 
                    ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
                }`}
            >
                <RefreshCw className={`w-4 h-4 ${scanning ? 'animate-spin' : ''}`} />
                {scanning ? 'Scanning...' : 'Run New Scan'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="px-6 py-8 space-y-8">
        
        {/* Stats Row */}
        <SecurityStatsCards stats={stats} findings={findings} />

        {/* Disclaimer */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="text-sm text-amber-800">
            <p className="font-semibold">Partial Scan Coverage</p>
            <p className="mt-1">
                This tool currently scans a subset of high-priority controls (approx. 20%) from the CIS AWS Foundations Benchmark v1.4.0. 
                It is intended for quick assessments and does not represent a complete compliance audit certification.
            </p>
            </div>
        </div>

        {/* Findings Section */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col h-[600px]">
            {/* Toolbar */}
            <SecurityToolbar 
                searchQuery={searchQuery}
                onSearchChange={setSearchQuery}
                resultCount={filteredFindings.length}
                statusFilter={statusFilter}
                onFilterChange={setStatusFilter}
                severityFilter={severityFilter}
                onSeverityFilterChange={setSeverityFilter}
            />
            
            {/* Table */}
            <SecurityFindingsTable 
                findings={currentFindings}
                loading={loading}
                onViewDetails={setSelectedFinding}
                emptyMessage={searchQuery ? 'No matching findings found.' : 'No findings yet. Click "Run New Scan".'}
                sortConfig={sortConfig}
                onSort={handleSort}
            />

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 shrink-0 flex items-center justify-between">
                    <div className="text-xs text-slate-500">
                        Page {currentPage} of {totalPages}
                    </div>
                    <div className="flex gap-2">
                        <button 
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            className="p-1.5 rounded hover:bg-slate-200 disabled:opacity-50"
                        >
                            <ChevronLeft className="w-4 h-4" />
                        </button>
                        <button 
                            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages}
                            className="p-1.5 rounded hover:bg-slate-200 disabled:opacity-50"
                        >
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            )}
        </div>
      </main>
    </div>
  );
}
