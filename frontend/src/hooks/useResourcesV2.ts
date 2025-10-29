/**
 * Custom hook for managing resources (V2 API)
 */

import { useState, useEffect, useCallback } from 'react';
import { resourcesAPI } from '@/lib/api/v2';
import { Resource, ResourceFilters, ResourceSummary, PaginatedResponse } from '@/lib/api/types';

interface UseResourcesResult {
  resources: Resource[];
  total: number;
  page: number;
  totalPages: number;
  loading: boolean;
  error: string | null;
  setPage: (page: number) => void;
  setFilters: (filters: ResourceFilters) => void;
  refetch: () => Promise<void>;
  deleteResource: (id: number) => Promise<void>;
}

/**
 * Hook to fetch and manage resources with pagination and filtering
 */
export function useResourcesV2(
  initialFilters?: ResourceFilters,
  pageSize: number = 50
): UseResourcesResult {
  const [resources, setResources] = useState<Resource[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [filters, setFilters] = useState<ResourceFilters | undefined>(initialFilters);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchResources = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data: PaginatedResponse<Resource> = await resourcesAPI.list(
        filters,
        page,
        pageSize
      );
      setResources(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch resources');
      console.error('Error fetching resources:', err);
    } finally {
      setLoading(false);
    }
  }, [filters, page, pageSize]);

  useEffect(() => {
    fetchResources();
  }, [fetchResources]);

  const deleteResource = useCallback(async (id: number) => {
    try {
      await resourcesAPI.delete(id);
      // Refetch after deletion
      await fetchResources();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete resource');
      console.error('Error deleting resource:', err);
      throw err;
    }
  }, [fetchResources]);

  return {
    resources,
    total,
    page,
    totalPages,
    loading,
    error,
    setPage,
    setFilters,
    refetch: fetchResources,
    deleteResource,
  };
}

interface UseResourceSummaryResult {
  summary: ResourceSummary | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Hook to fetch resource summary statistics
 */
export function useResourceSummary(filters?: ResourceFilters): UseResourceSummaryResult {
  const [summary, setSummary] = useState<ResourceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await resourcesAPI.getSummary(filters);
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch summary');
      console.error('Error fetching summary:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  return {
    summary,
    loading,
    error,
    refetch: fetchSummary,
  };
}

interface UseResourceResult {
  resource: Resource | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Hook to fetch a single resource by ID
 */
export function useResource(resourceId: number | null): UseResourceResult {
  const [resource, setResource] = useState<Resource | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchResource = useCallback(async () => {
    if (!resourceId) {
      setResource(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await resourcesAPI.get(resourceId);
      setResource(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch resource');
      console.error('Error fetching resource:', err);
    } finally {
      setLoading(false);
    }
  }, [resourceId]);

  useEffect(() => {
    fetchResource();
  }, [fetchResource]);

  return {
    resource,
    loading,
    error,
    refetch: fetchResource,
  };
}