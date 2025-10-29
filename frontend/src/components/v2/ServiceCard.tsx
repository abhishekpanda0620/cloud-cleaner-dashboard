'use client';

import { Service } from '@/lib/api/types';

interface ServiceCardProps {
  service: Service;
  onClick?: () => void;
}

export default function ServiceCard({ service, onClick }: ServiceCardProps) {
  const unusedPercent = service.resource_count > 0 
    ? Math.round(((service.unused_count || 0) / service.resource_count) * 100)
    : 0;

  // Determine color based on unused percentage
  const getStatusColor = () => {
    if (unusedPercent === 0) return 'bg-green-50 border-green-200';
    if (unusedPercent < 30) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const getStatusBadge = () => {
    if (unusedPercent === 0) return 'bg-green-100 text-green-700';
    if (unusedPercent < 30) return 'bg-yellow-100 text-yellow-700';
    return 'bg-red-100 text-red-700';
  };

  return (
    <div
      className={`${getStatusColor()} rounded-xl shadow-sm border-2 p-6 transition-all duration-200 hover:shadow-md ${
        onClick ? 'cursor-pointer hover:scale-105' : ''
      }`}
      onClick={onClick}
    >
      {/* Service Name */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-slate-900 line-clamp-2">
            {service.service_name}
          </h3>
          <p className="text-xs text-slate-500 mt-1">{service.service_code}</p>
        </div>
        {service.service_category && (
          <span className="ml-2 px-2 py-1 text-xs font-medium bg-slate-100 text-slate-700 rounded">
            {service.service_category}
          </span>
        )}
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-xs text-slate-600 mb-1">Resources</p>
          <p className="text-2xl font-bold text-slate-900">{service.resource_count}</p>
        </div>
        <div>
          <p className="text-xs text-slate-600 mb-1">Unused</p>
          <p className="text-2xl font-bold text-slate-900">{service.unused_count || 0}</p>
        </div>
      </div>

      {/* Status Badge */}
      {service.resource_count > 0 && (
        <div className="flex items-center justify-between">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge()}`}>
            {unusedPercent}% unused
          </span>
          {onClick && (
            <span className="text-blue-600 text-sm font-medium">
              View details →
            </span>
          )}
        </div>
      )}

      {/* Last Seen */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <p className="text-xs text-slate-500">
          Last seen: {new Date(service.last_seen).toLocaleDateString()}
        </p>
      </div>
    </div>
  );
}