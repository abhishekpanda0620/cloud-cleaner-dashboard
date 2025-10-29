'use client';

import { Service } from '@/lib/api/types';
import ServiceCard from './ServiceCard';
import LoadingSpinner from '../LoadingSpinner';
import EmptyState from '../EmptyState';

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
    return <LoadingSpinner message="Loading services..." />;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-3">
          <span className="text-3xl">⚠️</span>
          <div>
            <h3 className="text-lg font-semibold text-red-900">Error Loading Services</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (services.length === 0) {
    return (
      <EmptyState
        icon="🔍"
        title="No Services Found"
        description="No AWS services with costs detected. Try running a scan to discover your resources."
      />
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