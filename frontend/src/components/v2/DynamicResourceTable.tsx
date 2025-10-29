'use client';

import { Resource } from '@/lib/api/types';
import ResourceTable from '../ResourceTable';
import LoadingSpinner from '../LoadingSpinner';
import EmptyState from '../EmptyState';

interface DynamicResourceTableProps {
  resources: Resource[];
  loading?: boolean;
  error?: string | null;
  onViewDetails?: (resource: Resource) => void;
  onDelete?: (resource: Resource) => void;
}

export default function DynamicResourceTable({
  resources,
  loading = false,
  error = null,
  onViewDetails,
  onDelete,
}: DynamicResourceTableProps) {
  if (loading) {
    return <LoadingSpinner message="Loading resources..." />;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-3">
          <span className="text-3xl">⚠️</span>
          <div>
            <h3 className="text-lg font-semibold text-red-900">Error Loading Resources</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (resources.length === 0) {
    return (
      <EmptyState
        icon="📦"
        title="No Resources Found"
        description="No resources found for this service. Try adjusting your filters or running a new scan."
      />
    );
  }

  // Define columns for the resource table
  const columns = [
    {
      header: 'Resource ID',
      accessor: 'resource_id',
      render: (value: string) => (
        <span className="font-mono text-sm">{value}</span>
      ),
    },
    {
      header: 'Name',
      accessor: 'resource_name',
    },
    {
      header: 'Type',
      accessor: 'resource_type',
      render: (value: string) => (
        <span className="px-2 py-1 bg-slate-100 text-slate-700 rounded text-xs font-medium">
          {value}
        </span>
      ),
    },
    {
      header: 'Region',
      accessor: 'region',
      render: (value: string) => (
        <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">
          {value}
        </span>
      ),
    },
    {
      header: 'Status',
      accessor: 'is_unused',
      render: (value: boolean) => (
        <span
          className={`px-2 py-1 rounded text-xs font-medium ${
            value
              ? 'bg-red-100 text-red-700'
              : 'bg-green-100 text-green-700'
          }`}
        >
          {value ? 'Unused' : 'Active'}
        </span>
      ),
    },
    {
      header: 'Monthly Cost',
      accessor: 'estimated_monthly_cost',
      render: (value: number) => (
        <span className="font-semibold text-slate-900">
          ${value?.toFixed(2) || '0.00'}
        </span>
      ),
    },
  ];

  return (
    <ResourceTable
      columns={columns}
      data={resources}
      icon="📦"
      onViewDetails={onViewDetails}
      onDelete={onDelete}
    />
  );
}