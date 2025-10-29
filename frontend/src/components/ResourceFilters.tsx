'use client';

import { Search, X, Filter } from 'lucide-react';
import { useState } from 'react';

interface FilterOption {
  label: string;
  value: string;
}

interface ResourceFiltersProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  filters?: {
    name: string;
    label: string;
    options: FilterOption[];
    value: string;
    onChange: (value: string) => void;
  }[];
  onClearAll: () => void;
  resultCount: number;
  totalCount: number;
}

export default function ResourceFilters({
  searchTerm,
  onSearchChange,
  filters = [],
  onClearAll,
  resultCount,
  totalCount,
}: ResourceFiltersProps) {
  const [showFilters, setShowFilters] = useState(false);
  const hasActiveFilters = searchTerm || filters.some(f => f.value !== 'all');

  return (
    <div className="space-y-4">
      {/* Search Bar and Filter Toggle */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Search Input */}
        <div className="flex-1 relative group">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-slate-400 group-focus-within:text-blue-500 transition-colors duration-200" />
          </div>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search resources..."
            className="block w-full pl-12 pr-12 py-3 border-2 border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm font-medium placeholder:text-slate-400 bg-white shadow-sm hover:border-slate-300 transition-all duration-200"
          />
          {searchTerm && (
            <button
              onClick={() => onSearchChange('')}
              className="absolute inset-y-0 right-0 pr-4 flex items-center group/clear"
            >
              <div className="h-6 w-6 rounded-lg bg-slate-100 group-hover/clear:bg-slate-200 flex items-center justify-center transition-colors duration-200">
                <X className="h-4 w-4 text-slate-500 group-hover/clear:text-slate-700" />
              </div>
            </button>
          )}
        </div>

        {/* Filter Toggle Button */}
        {filters.length > 0 && (
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`group relative overflow-hidden inline-flex items-center gap-2 px-5 py-3 border-2 rounded-xl text-sm font-semibold transition-all duration-300 shadow-sm hover:shadow-md transform hover:-translate-y-0.5 ${
              showFilters || hasActiveFilters
                ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700'
                : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300'
            }`}
          >
            <Filter className={`h-4 w-4 transition-transform duration-300 ${showFilters ? 'rotate-180' : ''}`} />
            Filters
            {hasActiveFilters && (
              <span className="inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 text-xs font-bold text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full shadow-md">
                {filters.filter(f => f.value !== 'all').length + (searchTerm ? 1 : 0)}
              </span>
            )}
          </button>
        )}

        {/* Clear All Button */}
        {hasActiveFilters && (
          <button
            onClick={onClearAll}
            className="group inline-flex items-center gap-2 px-5 py-3 border-2 border-slate-200 rounded-xl text-sm font-semibold text-slate-700 bg-white hover:bg-slate-50 hover:border-slate-300 transition-all duration-300 shadow-sm hover:shadow-md transform hover:-translate-y-0.5"
          >
            <X className="h-4 w-4 group-hover:rotate-90 transition-transform duration-300" />
            Clear All
          </button>
        )}
      </div>

      {/* Filter Dropdowns */}
      {showFilters && filters.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-6 bg-gradient-to-br from-slate-50 to-blue-50 border-2 border-slate-200 rounded-xl shadow-inner animate-in fade-in duration-300">
          {filters.map((filter) => (
            <div key={filter.name} className="group">
              <label className="block text-sm font-bold text-slate-700 mb-2 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600"></span>
                {filter.label}
              </label>
              <select
                value={filter.value}
                onChange={(e) => filter.onChange(e.target.value)}
                className="block w-full px-4 py-2.5 border-2 border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm font-medium bg-white shadow-sm hover:border-slate-300 transition-all duration-200"
              >
                <option value="all">All {filter.label}</option>
                {filter.options.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </div>
      )}

      {/* Results Count */}
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-slate-600">Showing</span>
          <span className="inline-flex items-center px-3 py-1 rounded-lg bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-bold text-sm shadow-md">
            {resultCount}
          </span>
          <span className="text-slate-600">of</span>
          <span className="inline-flex items-center px-3 py-1 rounded-lg bg-slate-200 text-slate-900 font-bold text-sm">
            {totalCount}
          </span>
          <span className="text-slate-600">resources</span>
        </div>
        {hasActiveFilters && resultCount < totalCount && (
          <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200">
            <span className="h-2 w-2 rounded-full bg-amber-500 animate-pulse"></span>
            <span className="text-amber-700 font-semibold text-sm">
              {totalCount - resultCount} filtered out
            </span>
          </div>
        )}
      </div>
    </div>
  );
}