"use client";

import { useEffect, useState } from 'react';

interface Region {
  code: string;
  name: string;
  endpoint?: string;
}

interface RegionSelectorProps {
  selectedRegion: string;
  onRegionChange: (region: string) => void;
  apiUrl: string;
}

export default function RegionSelector({ selectedRegion, onRegionChange, apiUrl }: RegionSelectorProps) {
  const [regions, setRegions] = useState<Region[]>([]);
  const [defaultRegion, setDefaultRegion] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchRegions();
  }, [apiUrl]);

  const fetchRegions = async () => {
    try {
      const response = await fetch(`${apiUrl}/regions`);
      if (response.ok) {
        const data = await response.json();
        setRegions(data.regions || []);
        setDefaultRegion(data.default_region || '');
      }
    } catch (error) {
      console.error('Error fetching regions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRegionSelect = (regionCode: string) => {
    onRegionChange(regionCode);
    setIsOpen(false);
  };

  const selectedRegionName = regions.find(r => r.code === selectedRegion)?.name || selectedRegion;

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Loading regions...
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
      >
        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div className="flex flex-col items-start">
          <span className="text-xs text-gray-500">Region</span>
          <span className="text-sm font-medium text-gray-900">{selectedRegionName}</span>
        </div>
        <svg className={`w-4 h-4 text-gray-600 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-20 max-h-96 overflow-y-auto">
            <div className="p-2">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider border-b">
                Select AWS Region
              </div>
              <div className="mt-2 space-y-1">
                {regions.map((region) => (
                  <button
                    key={region.code}
                    onClick={() => handleRegionSelect(region.code)}
                    className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                      selectedRegion === region.code
                        ? 'bg-blue-50 text-blue-700 font-medium'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium">{region.name}</div>
                        <div className="text-xs text-gray-500">{region.code}</div>
                      </div>
                      {selectedRegion === region.code && (
                        <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                      {region.code === defaultRegion && selectedRegion !== region.code && (
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">Default</span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}