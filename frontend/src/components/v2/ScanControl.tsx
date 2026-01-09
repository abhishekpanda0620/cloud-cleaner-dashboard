'use client';

import { useScan } from '@/hooks/useScan';
import { useState, useRef, useEffect } from 'react';
import { Loader2, Play, ChevronDown, RefreshCw } from 'lucide-react';
import RegionSelector from '../RegionSelector';

export default function ScanControl({ onScanComplete }: { onScanComplete?: () => void }) {
  const { status, loading, error, triggerScan } = useScan();
  const [scanning, setScanning] = useState(false);
  const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  
  const dropdownRef = useRef<HTMLDivElement>(null);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084/api';

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleScan = async (force: boolean = false) => {
    try {
      setScanning(true);
      setShowDropdown(false);
      // Pass selected regions (empty array implies all) and force flag
      await triggerScan(selectedRegions, force);
      if (onScanComplete) {
        onScanComplete();
      }
    } catch (err) {
      console.error('Failed to trigger scan:', err);
    } finally {
      setScanning(false);
    }
  };

  const handleRegionChange = (regions: string | string[]) => {
    if (Array.isArray(regions)) {
        setSelectedRegions(regions);
    } else {
        setSelectedRegions([regions]);
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
      <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="flex-1 w-full sm:w-auto">
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
                <p>Start a new scan to discover resources.</p>
                {status?.started_at && (
                  <p className="text-xs text-slate-400">
                    Last scan: {new Date(status.started_at).toLocaleString()}
                  </p>
                )}
              </div>
            )}
          </div>
          
          {error && (
             <p className="text-xs text-red-600 mt-2">{error}</p>
          )}
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
            <div className="w-full sm:w-auto">
                <RegionSelector 
                    selectedRegion={selectedRegions}
                    onRegionChange={handleRegionChange}
                    apiUrl={apiUrl}
                    multiSelect={true}
                />
            </div>
            
            <div className="relative flex shadow-sm rounded-lg" ref={dropdownRef}>
                <button
                    onClick={() => handleScan(false)}
                    disabled={isScanning}
                    className={`flex items-center justify-center gap-2 px-4 py-2 rounded-l-lg text-sm font-medium transition-all w-full sm:w-auto whitespace-nowrap border-r border-blue-700/30
                    ${isScanning
                        ? 'bg-slate-100 text-slate-400 cursor-not-allowed border-none'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }
                    `}
                >
                    {isScanning ? (
                    <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Scanning...
                    </>
                    ) : (
                    <>
                        <Play className="w-4 h-4" />
                        Start Scan
                    </>
                    )}
                </button>
                <button
                    onClick={() => !isScanning && setShowDropdown(!showDropdown)}
                    disabled={isScanning}
                    className={`px-2 py-2 rounded-r-lg text-sm font-medium transition-all
                    ${isScanning
                        ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }
                    `}
                >
                    <ChevronDown className="w-4 h-4" />
                </button>
                
                {showDropdown && !isScanning && (
                    <div className="absolute right-0 top-full mt-1 w-56 bg-white rounded-lg border border-slate-200 shadow-xl z-20 py-1">
                        <button
                            onClick={() => handleScan(true)}
                            className="w-full text-left px-4 py-3 text-sm text-slate-700 hover:bg-slate-50 flex items-start gap-3 group"
                        >
                            <RefreshCw className="w-4 h-4 mt-0.5 text-slate-400 group-hover:text-blue-600" />
                            <div>
                                <span className="font-medium block text-slate-900">Force Deep Scan</span>
                                <span className="text-xs text-slate-500 mt-0.5 block">
                                    Bypasses cost checks to find newly created resources immediately.
                                </span>
                            </div>
                        </button>
                    </div>
                )}
            </div>
        </div>
      </div>
    </div>
  );
}