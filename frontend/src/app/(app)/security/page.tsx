'use client';

import { useState, useEffect, useMemo } from 'react';
import { ShieldCheck, RefreshCw, AlertTriangle, CheckCircle, XCircle, Search, ChevronLeft, ChevronRight, Eye } from 'lucide-react';
import { Skeleton } from '@/components/Skeleton';
import { FindingDetailsModal } from '@/components/FindingDetailsModal';

interface Finding {
  id: number;
  check_id: string;
  check_name: string;
  severity: string;
  status: 'PASS' | 'FAIL' | 'WARNING';
  resource_id: string;
  resource_type?: string; 
  region: string;
  evidence: any;
  last_updated: string;
}

interface Stats {
  pass: number;
  fail: number;
  total: number;
  score: number;
}

export default function SecurityPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  
  // UI State
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const itemsPerPage = 10;

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084/api';

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statsRes, findingsRes] = await Promise.all([
        fetch(`${apiUrl}/security/stats`),
        fetch(`${apiUrl}/security/findings`)
      ]);
      
      if (statsRes.ok) setStats(await statsRes.json());
      if (findingsRes.ok) setFindings(await findingsRes.json());
    } catch (error) {
      console.error("Failed to fetch security data", error);
    } finally {
      setLoading(false);
    }
  };

  const handleScan = async () => {
    try {
      setScanning(true);
      await fetch(`${apiUrl}/security/scan`, { method: 'POST' });
      await fetchData();
    } catch (error) {
      console.error("Scan failed", error);
    } finally {
      setScanning(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Filter and Pagination Logic
  const filteredFindings = useMemo(() => {
    return findings.filter(f => 
       f.check_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
       f.resource_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
       f.severity.toLowerCase().includes(searchQuery.toLowerCase()) ||
       f.check_id.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [findings, searchQuery]);

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
          
          <button
            onClick={handleScan}
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
      </header>

      {/* Main Content */}
      <main className="px-6 py-8 space-y-8">
        
        {/* Stats Row */}
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
                        {findings.filter(f => f.status === 'FAIL' && f.severity === 'Critical').length}
                    </span>
                </div>
            </div>
        </div>

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
            <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center bg-slate-50 shrink-0">
                <div className="flex items-center gap-4">
                    <h3 className="font-semibold text-slate-900">Findings</h3>
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input 
                            type="text" 
                            placeholder="Search findings..." 
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-9 pr-4 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 w-64"
                        />
                    </div>
                </div>
                <div className="text-xs text-slate-500">
                    {filteredFindings.length} results
                </div>
            </div>
            
            {/* Scrollable Table */}
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
                        ) : currentFindings.length === 0 ? (
                            <tr>
                                <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                                    {searchQuery ? 'No matching findings found.' : 'No findings yet. Click "Run New Scan".'}
                                </td>
                            </tr>
                        ) : (
                            currentFindings.map((finding) => (
                                <tr key={finding.id} className="hover:bg-slate-50 transition-colors">
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                                            finding.status === 'PASS' 
                                                ? 'bg-green-50 text-green-700 border-green-200' 
                                                : finding.status === 'FAIL'
                                                ? 'bg-red-50 text-red-700 border-red-200'
                                                : 'bg-yellow-50 text-yellow-700 border-yellow-200'
                                        }`}>
                                            {finding.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="font-medium text-slate-900">{finding.check_name}</div>
                                        <div className="text-slate-500 text-xs mt-0.5 font-mono">{finding.check_id}</div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`font-medium ${
                                            finding.severity === 'Critical' ? 'text-red-600' :
                                            finding.severity === 'High' ? 'text-orange-600' : 'text-slate-600'
                                        }`}>
                                            {finding.severity}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="text-slate-900 max-w-[200px] truncate" title={finding.resource_id}>
                                            {finding.resource_id}
                                        </div>
                                        <div className="text-xs text-slate-500">{finding.resource_type}</div>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <button 
                                            onClick={() => setSelectedFinding(finding)}
                                            className="p-2 hover:bg-slate-200 rounded-full transition-colors text-slate-500 hover:text-indigo-600"
                                            title="View Details"
                                        >
                                            <Eye className="w-5 h-5" />
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Pagination Footer */}
            {totalPages > 1 && (
                <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 shrink-0 flex items-center justify-between">
                    <span className="text-xs text-slate-500">
                        Page {currentPage} of {totalPages}
                    </span>
                    <div className="flex gap-2">
                         <button 
                            onClick={() => setCurrentPage(c => Math.max(1, c - 1))}
                            disabled={currentPage === 1}
                            className="p-1 rounded hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed"
                         >
                            <ChevronLeft className="w-5 h-5 text-slate-600" />
                         </button>
                         <button 
                            onClick={() => setCurrentPage(c => Math.min(totalPages, c + 1))}
                            disabled={currentPage === totalPages}
                            className="p-1 rounded hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed"
                         >
                            <ChevronRight className="w-5 h-5 text-slate-600" />
                         </button>
                    </div>
                </div>
            )}
        </div>
      </main>
    </div>
  );
}
