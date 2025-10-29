'use client';

import { useScan } from '@/hooks/useScan';
import { useState } from 'react';

export default function ScanControl() {
  const { status, loading, error, triggerScan } = useScan();
  const [scanning, setScanning] = useState(false);

  const handleScan = async () => {
    try {
      setScanning(true);
      await triggerScan();
    } catch (err) {
      console.error('Failed to trigger scan:', err);
    } finally {
      setScanning(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-slate-200 rounded w-1/4 mb-4"></div>
          <div className="h-8 bg-slate-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  const isScanning = status?.is_scanning || scanning;
  const progress = status?.progress_percent || 0;

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl shadow-sm border border-blue-200 p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-slate-900 mb-2">
            Resource Scanner
          </h3>
          
          {isScanning ? (
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <div className="h-5 w-5 rounded-full border-2 border-blue-200"></div>
                  <div className="absolute top-0 left-0 h-5 w-5 rounded-full border-2 border-blue-600 border-t-transparent animate-spin"></div>
                </div>
                <span className="text-sm font-medium text-blue-700">
                  Scanning in progress...
                </span>
              </div>
              
              {/* Progress Bar */}
              <div className="w-full bg-blue-100 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              
              {/* Progress Details */}
              <div className="flex items-center justify-between text-xs text-slate-600">
                <span>
                  {status?.services_scanned || 0} / {status?.total_services || 0} services
                </span>
                <span>{progress}%</span>
              </div>
              
              {status?.current_service && (
                <p className="text-xs text-slate-600">
                  Current: {status.current_service}
                </p>
              )}
              
              {status?.resources_found !== undefined && (
                <p className="text-xs text-slate-600">
                  Resources found: {status.resources_found}
                </p>
              )}
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-slate-600">
                Scan your AWS account to discover resources and identify unused ones
              </p>
              {status?.started_at && (
                <p className="text-xs text-slate-500">
                  Last scan: {new Date(status.started_at).toLocaleString()}
                </p>
              )}
            </div>
          )}
          
          {error && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}
        </div>

        <button
          onClick={handleScan}
          disabled={isScanning}
          className={`ml-6 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
            isScanning
              ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-lg transform hover:scale-105'
          }`}
        >
          {isScanning ? (
            <span className="flex items-center space-x-2">
              <div className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin"></div>
              <span>Scanning... (30-60s)</span>
            </span>
          ) : (
            <span className="flex items-center space-x-2">
              <span>🔍</span>
              <span>Start Scan</span>
            </span>
          )}
        </button>
      </div>
    </div>
  );
}