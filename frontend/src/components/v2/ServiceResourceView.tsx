'use client';

import { useState, useEffect } from 'react';
import { Service, ResourceFilters } from '@/lib/api/types';
import { servicesAPI } from '@/lib/api/v2';
import DynamicResourceTable from './DynamicResourceTable';
import { ArrowLeft, Box, CheckCircle2, AlertTriangle, Filter } from 'lucide-react';

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
      <div className="flex flex-col gap-4">
          <button
            onClick={onBack}
            className="flex items-center space-x-2 text-sm text-slate-500 hover:text-slate-900 transition-colors w-fit group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            <span>Back to Services</span>
          </button>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
                <div className="p-3 bg-white border border-slate-200 rounded-lg shadow-sm">
                    <Box className="w-6 h-6 text-slate-700" />
                </div>
                <div>
                   <h2 className="text-2xl font-bold text-slate-900 tracking-tight">{service.service_name}</h2>
                   <div className="flex items-center gap-2 mt-1">
                      <code className="text-xs bg-slate-100 px-1.5 py-0.5 rounded text-slate-500 font-mono">
                         {service.service_code}
                      </code>
                      {service.service_category && (
                        <span className="text-xs text-slate-500">• {service.service_category}</span>
                      )}
                   </div>
                </div>
            </div>
            
             <div className="flex gap-3">
                 <div className="bg-white border border-slate-200 rounded-lg px-4 py-2 flex items-center gap-3 shadow-sm">
                     <div className="flex flex-col">
                        <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Active</span>
                        <span className="text-lg font-bold text-slate-900 leading-none">{activeCount}</span>
                     </div>
                     <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                 </div>
                 <div className="bg-white border border-slate-200 rounded-lg px-4 py-2 flex items-center gap-3 shadow-sm">
                     <div className="flex flex-col">
                        <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Unused</span>
                        <span className="text-lg font-bold text-slate-900 leading-none">{unusedCount}</span>
                     </div>
                     <AlertTriangle className="w-5 h-5 text-amber-500" />
                 </div>
             </div>
          </div>
      </div>

      {/* Content Card */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
         {/* Toolbar */}
         <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
             <div className="flex items-center gap-2">
                 <Filter className="w-4 h-4 text-slate-500" />
                 <span className="text-sm font-medium text-slate-700">Filter Resources</span>
             </div>
             
             <div className="flex p-1 bg-slate-200/50 rounded-lg border border-slate-200">
                {(['all', 'active', 'unused'] as const).map((f) => (
                    <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all capitalize ${
                        filter === f
                            ? 'bg-white text-slate-900 shadow-sm ring-1 ring-black/5'
                            : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'
                        }`}
                    >
                        {f}
                    </button>
                ))}
             </div>
         </div>

         {/* Table */}
         <div className="p-0">
            <DynamicResourceTable
                resources={resources}
                loading={loading}
                error={error}
                onViewDetails={onViewDetails}
                onDelete={onDelete}
            />
         </div>
      </div>
    </div>
  );
}