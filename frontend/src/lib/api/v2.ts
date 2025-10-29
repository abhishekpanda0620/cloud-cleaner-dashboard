/**
 * V2 API Client for Cloud Cleaner Dashboard
 * 
 * This client provides access to the new dynamic service discovery APIs.
 */

import {
  Service,
  ServiceDetails,
  Resource,
  ScanStatus,
  ScanHistory,
  ResourceSummary,
  ResourceFilters,
  ServiceFilters,
  PaginatedResponse,
  ApiError,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Base fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        message: `HTTP ${response.status}: ${response.statusText}`,
      }));
      throw new Error(error.message || 'API request failed');
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

/**
 * Build query string from params object
 */
function buildQueryString(params: Record<string, any>): string {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value));
    }
  });
  
  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
}

// ============================================================================
// Scan API
// ============================================================================

export const scanAPI = {
  /**
   * Trigger a new resource scan
   */
  async trigger(): Promise<{ message: string; scan_id: number }> {
    return apiFetch('/v2/scan', {
      method: 'POST',
    });
  },

  /**
   * Get current scan status
   */
  async getStatus(): Promise<ScanStatus> {
    return apiFetch('/v2/scan/status');
  },

  /**
   * Get scan history
   */
  async getHistory(limit: number = 10): Promise<ScanHistory[]> {
    const response: { scans: ScanHistory[] } = await apiFetch(`/v2/scan/history?limit=${limit}`);
    return response.scans;
  },
};

// ============================================================================
// Services API
// ============================================================================

export const servicesAPI = {
  /**
   * List all services
   */
  async list(filters?: ServiceFilters): Promise<Service[]> {
    const queryString = filters ? buildQueryString(filters) : '';
    const response: { services: Service[] } = await apiFetch(`/v2/services${queryString}`);
    return response.services;
  },

  /**
   * Get service details
   */
  async get(serviceCode: string): Promise<ServiceDetails> {
    return apiFetch(`/v2/services/${serviceCode}`);
  },

  /**
   * Get resources for a service
   */
  async getResources(
    serviceCode: string,
    filters?: ResourceFilters
  ): Promise<Resource[]> {
    const queryString = filters ? buildQueryString(filters) : '';
    const response: { resources: Resource[] } = await apiFetch(`/v2/services/${serviceCode}/resources${queryString}`);
    return response.resources;
  },

  /**
   * Get cost history for a service
   */
  async getCosts(
    serviceCode: string,
    days: number = 30
  ): Promise<{ date: string; cost: number }[]> {
    return apiFetch(`/v2/services/${serviceCode}/costs?days=${days}`);
  },
};

// ============================================================================
// Resources API
// ============================================================================

export const resourcesAPI = {
  /**
   * List all resources with optional filtering
   */
  async list(
    filters?: ResourceFilters,
    page: number = 1,
    pageSize: number = 50
  ): Promise<PaginatedResponse<Resource>> {
    const params = {
      ...filters,
      page,
      page_size: pageSize,
    };
    const queryString = buildQueryString(params);
    return apiFetch(`/v2/resources${queryString}`);
  },

  /**
   * Get resource details
   */
  async get(resourceId: number): Promise<Resource> {
    return apiFetch(`/v2/resources/${resourceId}`);
  },

  /**
   * Delete a resource
   */
  async delete(resourceId: number): Promise<{ message: string }> {
    return apiFetch(`/v2/resources/${resourceId}`, {
      method: 'DELETE',
    });
  },

  /**
   * Get resource summary statistics
   */
  async getSummary(filters?: ResourceFilters): Promise<ResourceSummary> {
    const queryString = filters ? buildQueryString(filters) : '';
    return apiFetch(`/v2/resources/summary${queryString}`);
  },
};

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Check if API is reachable
 */
export async function checkHealth(): Promise<boolean> {
  try {
    await apiFetch('/health');
    return true;
  } catch {
    return false;
  }
}

/**
 * Get API version info
 */
export async function getVersion(): Promise<{
  name: string;
  version: string;
  api_versions: Record<string, any>;
}> {
  return apiFetch('/');
}