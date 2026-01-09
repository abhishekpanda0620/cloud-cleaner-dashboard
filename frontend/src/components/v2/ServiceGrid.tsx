'use client';

import { Service } from '@/lib/api/types';
import ServiceCard from './ServiceCard';
import ServiceCardSkeleton from './ServiceCardSkeleton';
import { AlertTriangle, Search } from 'lucide-react';

interface ServiceGridProps {
  services: Service[];
  loading?: boolean;
  error?: string | null;
  onServiceClick?: (service: Service) => void;
}

export default function ServiceGrid({ 
  services, 
  loading = false, 
  error = null,
  onServiceClick 
}: ServiceGridProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {[...Array(8)].map((_, i) => (
          <ServiceCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-100 text-red-600 mb-4">
             <AlertTriangle className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-semibold text-red-900">Error Loading Services</h3>
        <p className="text-sm text-red-700 mt-1 max-w-sm mx-auto">{error}</p>
      </div>
    );
  }

  if (services.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg border border-slate-200 border-dashed">
         <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-slate-100 text-slate-400 mb-4">
            <Search className="w-6 h-6" />
         </div>
         <h3 className="text-lg font-medium text-slate-900">No Services Found</h3>
         <p className="text-slate-500 max-w-sm mx-auto mt-1">
            No AWS services with costs detected. Try running a scan or checking your filters.
         </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {services.map((service) => (
        <ServiceCard
          key={service.service_code}
          service={service}
          onClick={onServiceClick ? () => onServiceClick(service) : undefined}
        />
      ))}
    </div>
  );
}