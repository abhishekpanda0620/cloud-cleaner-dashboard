'use client';

import { useState } from 'react';
import { Service, ResourceFilters } from '@/lib/api/types';
import { servicesAPI } from '@/lib/api/v2';
import DynamicResourceTable from './DynamicResourceTable';
import LoadingSpinner from '../LoadingSpinner';
import { useEffect } from 'react';

interface ServiceResourceViewProps {
  service: Service;
  onBack: () => void;
  onViewDetails?: (resource: any) => void;
  onDelete?: (resource: any) => void;
}

export default function ServiceResourceView({
  service,
  onBack,
  onViewDetails,
  onDelete,
}: ServiceResourceViewProps) {
  const [resources, setResources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'active' | 'unused'>('all');

  useEffect(() => {
    const fetchResources = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const filters: ResourceFilters = {};
        if (filter !== 'all') {
          filters.status = filter;
        }
        
        const data = await servicesAPI.getResources(service.service_code, filters);
        setResources(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch resources');
      } finally {
        setLoading(false);
      }
    };

    fetchResources();
  }, [service.service_code, filter]);

  const unusedCount = resources.filter(r => r.is_unused).length;
  const activeCount = resources.length - unusedCount;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={onBack}
            className="flex items-center space-x-2 text-slate-600 hover:text-slate-900 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span className="font-medium">Back to Services</span>
          </button>
        </div>

        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">{service.service_name}</h2>
            <p className="text-sm text-slate-500 mt-1">{service.service_code}</p>
          </div>
          {service.service_category && (
            <span className="px-3 py-1 text-sm font-medium bg-slate-100 text-slate-700 rounded-lg">
              {service.service_category}
            </span>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="bg-slate-50 rounded-lg p-4">
            <p className="text-xs text-slate-600 mb-1">Total Resources</p>
            <p className="text-2xl font-bold text-slate-900">{resources.length}</p>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-xs text-green-600 mb-1">Active</p>
            <p className="text-2xl font-bold text-green-700">{activeCount}</p>
          </div>
          <div className="bg-red-50 rounded-lg p-4">
            <p className="text-xs text-red-600 mb-1">Unused</p>
            <p className="text-2xl font-bold text-red-700">{unusedCount}</p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-slate-700">Filter:</span>
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            All ({resources.length})
          </button>
          <button
            onClick={() => setFilter('active')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'active'
                ? 'bg-green-600 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            Active ({activeCount})
          </button>
          <button
            onClick={() => setFilter('unused')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'unused'
                ? 'bg-red-600 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            Unused ({unusedCount})
          </button>
        </div>
      </div>

      {/* Resources Table */}
      <DynamicResourceTable
        resources={resources}
        loading={loading}
        error={error}
        onViewDetails={onViewDetails}
        onDelete={onDelete}
      />
    </div>
  );
}