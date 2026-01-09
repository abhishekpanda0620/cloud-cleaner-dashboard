'use client';

import { 
  Box, 
  Trash2, 
  ExternalLink, 
  HardDrive, 
  Database, 
  Server, 
  Lock, 
  Users, 
  Key
} from 'lucide-react';

import { Resource } from '@/lib/api/types';

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
    return (
      <div className="p-12 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900 mb-4"></div>
        <p className="text-slate-500 text-sm">Loading resources...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-12 text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-100 text-red-600 mb-4">
            <AlertTriangle className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-medium text-slate-900">Failed to load resources</h3>
        <p className="text-slate-500 mt-1 max-w-sm mx-auto">{error}</p>
      </div>
    );
  }

  if (!resources || resources.length === 0) {
    return (
      <div className="p-16 text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-100 text-slate-400 mb-4">
             <Box className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-medium text-slate-900">No resources found</h3>
        <p className="text-slate-500 mt-1">Try adjusting your filters or running a new scan.</p>
      </div>
    );
  }

  const getResourceIcon = (type: string) => {
    switch (type) {
        case 'ec2': return <Server className="w-4 h-4" />;
        case 'ebs': return <HardDrive className="w-4 h-4" />;
        case 's3': return <Database className="w-4 h-4" />;
        case 'iam-role': return <Lock className="w-4 h-4" />;
        case 'iam-user': return <Users className="w-4 h-4" />;
        case 'access-key': return <Key className="w-4 h-4" />;
        default: return <Box className="w-4 h-4" />;
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
              Resource
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
              Type
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
              Region
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
              Status
            </th>
            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
              Monthly Cost
            </th>
            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-slate-200">
          {resources.map((resource) => (
            <tr key={resource.id} className="hover:bg-slate-50 transition-colors group">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <div className="shrink-0 h-8 w-8 rounded bg-slate-100 flex items-center justify-center text-slate-500 border border-slate-200 mr-3">
                     {getResourceIcon(resource.resource_type)}
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-900 max-w-xs truncate" title={resource.resource_name || resource.resource_id}>
                      {resource.resource_name || resource.resource_id}
                    </div>
                    {resource.resource_name && resource.resource_name !== resource.resource_id && (
                        <div className="text-xs text-slate-500 font-mono truncate max-w-xs">{resource.resource_id}</div>
                    )}
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-800 border border-slate-200">
                  {resource.resource_type}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                {resource.region}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {resource.is_unused ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
                        Unused
                    </span>
                ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                        Active
                    </span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-slate-900">
                ${(resource.estimated_monthly_cost || 0).toFixed(2)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                        onClick={() => onViewDetails?.(resource)}
                        className="p-1.5 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded"
                        title="View Details"
                    >
                        <ExternalLink className="w-4 h-4" />
                    </button>
                    {onDelete && resource.is_unused && (
                         <button
                            onClick={() => onDelete(resource)}
                            className="p-1.5 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded"
                            title="Delete Resource"
                        >
                            <Trash2 className="w-4 h-4" />
                        </button>
                    )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Helper import for error state
import { AlertTriangle } from 'lucide-react';