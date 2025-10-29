/**
 * Custom hook for managing AWS services
 */

import { useState, useEffect, useCallback } from 'react';
import { servicesAPI } from '@/lib/api/v2';
import { Service, ServiceDetails, ServiceFilters } from '@/lib/api/types';

interface UseServicesResult {
  services: Service[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Hook to fetch and manage list of services
 */
export function useServices(filters?: ServiceFilters): UseServicesResult {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchServices = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await servicesAPI.list(filters);
      setServices(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch services');
      console.error('Error fetching services:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchServices();
  }, [fetchServices]);

  return {
    services,
    loading,
    error,
    refetch: fetchServices,
  };
}

interface UseServiceResult {
  service: ServiceDetails | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Hook to fetch details for a specific service
 */
export function useService(serviceCode: string | null): UseServiceResult {
  const [service, setService] = useState<ServiceDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchService = useCallback(async () => {
    if (!serviceCode) {
      setService(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await servicesAPI.get(serviceCode);
      setService(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch service');
      console.error('Error fetching service:', err);
    } finally {
      setLoading(false);
    }
  }, [serviceCode]);

  useEffect(() => {
    fetchService();
  }, [fetchService]);

  return {
    service,
    loading,
    error,
    refetch: fetchService,
  };
}