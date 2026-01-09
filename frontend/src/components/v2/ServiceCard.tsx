'use client';

import { Service } from '@/lib/api/types';
import { ArrowRight } from 'lucide-react';

interface ServiceCardProps {
  service: Service;
  onClick?: () => void;
}

export default function ServiceCard({ service, onClick }: ServiceCardProps) {
  const unusedPercent = service.resource_count > 0 
    ? Math.round(((service.unused_count || 0) / service.resource_count) * 100)
    : 0;

  const getStatusBadge = () => {
    if (unusedPercent === 0) return 'bg-emerald-50 text-emerald-700 border-emerald-100';
    if (unusedPercent < 30) return 'bg-amber-50 text-amber-700 border-amber-100';
    return 'bg-red-50 text-red-700 border-red-100';
  };

  return (
    <div
      className={`group bg-white rounded-lg border border-slate-200 p-6 transition-all duration-200 hover:border-slate-300 hover:shadow-sm ${
        onClick ? 'cursor-pointer' : ''
      }`}
      onClick={onClick}
    >
      {/* Service Name */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-slate-900">
              {service.service_name}
            </h3>
            {service.service_category && (
              <span className="px-2 py-0.5 text-[10px] uppercase tracking-wider font-semibold bg-slate-50 text-slate-500 rounded border border-slate-100">
                {service.service_category}
              </span>
            )}
          </div>
          <p className="text-sm text-slate-500 mt-1 font-mono">{service.service_code}</p>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <p className="text-xs font-medium text-slate-500 mb-1">Resources</p>
          <p className="text-2xl font-semibold text-slate-900 tracking-tight">{service.resource_count}</p>
        </div>
        <div>
          <p className="text-xs font-medium text-slate-500 mb-1">Cost (30d)</p>
          <p className="text-2xl font-semibold text-slate-900 tracking-tight">
            ${service.total_cost_30d.toFixed(2)}
          </p>
        </div>
      </div>

      {/* Status Badge */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-100">
        {service.resource_count > 0 ? (
          <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${getStatusBadge()}`}>
            {service.unused_count || 0} unused ({unusedPercent}%)
          </span>
        ) : (
          <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-50 text-slate-500 border border-slate-100">
            No resources
          </span>
        )}
        
        {onClick && (
          <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-slate-600 transition-colors" />
        )}
      </div>
    </div>
  );
}