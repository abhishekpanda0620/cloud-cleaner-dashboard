'use client';

import { useScan } from '@/hooks/useScan';
import { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

export default function ScanControl({ onScanComplete }: { onScanComplete?: () => void }) {
  const { status, loading, error, triggerScan } = useScan();
  const [scanning, setScanning] = useState(false);

  const handleScan = async () => {
    try {
      setScanning(true);
      await triggerScan();
      if (onScanComplete) {
        onScanComplete();
      }
    } catch (err) {
      console.error('Failed to trigger scan:', err);
    } finally {
      setScanning(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-slate-100 rounded w-1/4"></div>
          <div className="h-8 bg-slate-100 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  const isScanning = status?.is_scanning || scanning;

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center justify-between gap-6">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-sm font-semibold text-slate-900">
              Resource Scanner
            </h3>
            {isScanning && (
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                <Loader2 className="w-3 h-3 animate-spin" />
                Scanning...
              </span>
            )}
          </div>
          
          <div className="text-sm text-slate-500">
            {isScanning ? (
              <p>
                Analysing your AWS environment. This may take up to a minute.
              </p>
            ) : (
              <div className="space-y-1">
                <p>
                  Scan your AWS account to discover resources and identify unused ones.
                </p>
                {status?.started_at && (
                   <p className="text-xs text-slate-400">
                    Last scan: {new Date(status.started_at).toLocaleString()}
                   </p>
                )}
              </div>
            )}
          </div>
          
          {error && (
            <div className="mt-3 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-md border border-red-100">
              Error: {error}
            </div>
          )}
        </div>

        <button
          onClick={handleScan}
          disabled={isScanning}
          className={`shrink-0 flex items-center gap-2 px-4 py-2 rounded-md font-medium text-sm transition-all focus:ring-2 focus:ring-offset-2 ${
            isScanning
              ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow focus:ring-blue-500'
          }`}
        >
          {isScanning ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Scanning...</span>
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              <span>Start New Scan</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}