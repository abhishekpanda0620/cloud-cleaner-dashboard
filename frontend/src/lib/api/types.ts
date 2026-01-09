/**
 * TypeScript types for Cloud Cleaner Dashboard API
 */

// Service Types
export interface Service {
  id: number;
  service_code: string;
  service_name: string;
  service_category?: string;
  is_active: boolean;
  total_cost_30d: number;
  monthly_cost?: number;
  resource_count: number;
  unused_count?: number;
  first_seen: string;
  last_seen: string;
  created_at: string;
  updated_at?: string;
}

export interface ServiceDetails extends Service {
  resources?: Resource[];
  cost_history?: CostHistory[];
}

// Resource Types
export interface Resource {
  id: number;
  service_id: number;
  resource_id: string;
  resource_type: string;
  resource_name: string;
  region: string;
  is_unused: boolean;
  unused_reason?: string;
  estimated_monthly_cost: number;
  resource_config: Record<string, any>;
  tags: Record<string, string>;
  first_seen: string;
  last_seen: string;
  created_at: string;
  updated_at?: string;
}

// Cost History Types
export interface CostHistory {
  id: number;
  service_id: number;
  date: string;
  cost: number;
  created_at: string;
}

// Scan Types
export interface ScanStatus {
  is_scanning: boolean;
  current_service?: string;
  progress_percent: number;
  services_scanned: number;
  total_services: number;
  resources_found: number;
  started_at?: string;
  estimated_completion?: string;
}

export interface ScanHistory {
  id: number;
  scan_type: string;
  status: 'running' | 'success' | 'failed';
  services_found?: number;
  resources_found?: number;
  unused_resources?: number;
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  error_message?: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Filter Types
export interface ResourceFilters {
  status?: 'all' | 'active' | 'unused';
  service_code?: string;
  region?: string;
  tags?: Record<string, string>;
  min_cost?: number;
  max_cost?: number;
  search?: string;
}

export interface ServiceFilters {
  is_active?: boolean;
  min_cost?: number;
  max_cost?: number;
  has_unused?: boolean;
}

// Summary Types
export interface ResourceSummary {
  total_resources: number;
  unused_resources: number;
  unused_percentage: number;
  total_cost_monthly: number;
  potential_savings: number;
  by_type: {
    resource_type: string;
    count: number;
    cost: number;
  }[];
  by_region: {
    region: string;
    count: number;
    cost: number;
  }[];
}

// Right-Sizing Types
export interface RightSizingRecommendation {
  instance_id: string;
  name?: string;
  current_type: string;
  suggested_type: string;
  avg_cpu: number;
  max_cpu: number;
  estimated_monthly_savings: number;
  confidence: 'High' | 'Low';
}

export interface RightSizingSummary {
  total_analyzed: number;
  opportunities_found: number;
  total_potential_savings: number;
  recommendations: RightSizingRecommendation[];
}

export interface ApiError {
  message: string;
  code?: string;
  details?: any;
}