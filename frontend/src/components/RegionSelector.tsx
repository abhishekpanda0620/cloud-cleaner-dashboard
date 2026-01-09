"use client";

import { useEffect, useState, useCallback } from 'react';
import { Check, ChevronDown, MapPin } from 'lucide-react';

interface Region {
  code: string;
  name: string;
  endpoint?: string;
}

interface RegionSelectorProps {
  selectedRegion: string | string[];
  onRegionChange: (region: string | string[]) => void;
  apiUrl: string;
  multiSelect?: boolean;
}

export default function RegionSelector({ selectedRegion, onRegionChange, apiUrl, multiSelect = false }: RegionSelectorProps) {
  const [regions, setRegions] = useState<Region[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchRegions = useCallback(async () => {
    try {
      const response = await fetch(`${apiUrl}/regions`);
      if (response.ok) {
        const data = await response.json();
        setRegions(data.regions || []);
        
        // Only set default if nothing selected
        if (!selectedRegion || (Array.isArray(selectedRegion) && selectedRegion.length === 0)) {
           if (!multiSelect && data.default_region) {
             onRegionChange(data.default_region);
           }
        }
      }
    } catch (error) {
      console.error('Error fetching regions:', error);
    } finally {
      setLoading(false);
    }
  }, [apiUrl, multiSelect, onRegionChange, selectedRegion]);

  useEffect(() => {
    fetchRegions();
  }, [fetchRegions]);

  const toggleRegion = (regionCode: string) => {
    if (multiSelect) {
      const current = Array.isArray(selectedRegion) ? selectedRegion : [];
      const isSelected = current.includes(regionCode);
      let newSelection: string[];
      
      if (isSelected) {
        newSelection = current.filter(r => r !== regionCode);
      } else {
        newSelection = [...current, regionCode];
      }
      onRegionChange(newSelection);
    } else {
      onRegionChange(regionCode);
      setIsOpen(false);
    }
  };

  if (loading) {
     return (
        <div className="h-10 w-48 bg-slate-100 rounded-lg animate-pulse" />
     );
  }

  // Display text logic
  let displayText = "Select Region";
  if (multiSelect) { 
    const selectedCount = Array.isArray(selectedRegion) ? selectedRegion.length : 0;
    if (selectedCount === 0) displayText = "All Regions";
    else if (selectedCount === 1) {
       const code = Array.isArray(selectedRegion) ? selectedRegion[0] : '';
       displayText = regions.find(r => r.code === code)?.name || code;
    } else {
       displayText = `${selectedCount} Regions Selected`;
    }
  } else {
     const code = typeof selectedRegion === 'string' ? selectedRegion : '';
     displayText = regions.find(r => r.code === code)?.name || code;
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500/20 active:bg-slate-100 transition-colors min-w-[200px] justify-between"
      >
        <div className="flex items-center gap-2 truncate">
          <MapPin className="w-4 h-4 text-slate-400" />
          <span className="truncate max-w-[150px]">{displayText}</span>
        </div>
        <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full right-0 mt-1 w-64 bg-white rounded-lg border border-slate-200 shadow-xl z-20 max-h-80 overflow-y-auto py-1">
            {multiSelect && (
              <div 
                  className="px-3 py-2 text-xs font-semibold text-slate-500 border-b border-slate-100 flex justify-between items-center cursor-pointer hover:bg-slate-50"
                  onClick={() => onRegionChange([])}
              >
                 <span>Clear Selection (Select All)</span>
              </div>
            )}
            
            {regions.map((region) => {
              const isSelected = multiSelect 
                ? Array.isArray(selectedRegion) && selectedRegion.includes(region.code)
                : selectedRegion === region.code;

              return (
                <button
                  key={region.code}
                  onClick={() => toggleRegion(region.code)}
                  className={`w-full text-left px-3 py-2 text-sm flex items-center justify-between hover:bg-slate-50 transition-colors
                    ${isSelected ? 'bg-blue-50/50 text-blue-700' : 'text-slate-700'}
                  `}
                >
                  <span className="truncate">{region.name}</span>
                  {isSelected && <Check className="w-4 h-4 text-blue-600" />}
                </button>
              );
            })}
             {regions.length === 0 && (
                <div className="px-3 py-4 text-center text-sm text-slate-500">
                  No regions found
                </div>
              )}
          </div>
        </>
      )}
    </div>
  );
}