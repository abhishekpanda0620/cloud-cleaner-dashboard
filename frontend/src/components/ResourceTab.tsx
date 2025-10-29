import LoadingSpinner from './LoadingSpinner';
import ErrorAlert from './ErrorAlert';
import EmptyState from './EmptyState';
import ResourceTable from './ResourceTable';
import ResourceFilters from './ResourceFilters';
import { useResourceFilters } from '@/hooks/useResourceFilters';

interface FilterConfig {
  name: string;
  label: string;
  options: { label: string; value: string }[];
  filterFn: (item: any, value: string) => boolean;
}

interface ResourceTabProps {
  loading: boolean;
  error: string | null;
  data: any[];
  columns: any[];
  icon: string;
  emptyTitle: string;
  emptyDescription: string;
  infoNote?: string;
  onViewDetails?: (row: any) => void;
  onDelete?: (row: any) => void;
  searchFields?: string[];
  filterConfigs?: FilterConfig[];
}

export default function ResourceTab({
  loading,
  error,
  data,
  columns,
  icon,
  emptyTitle,
  emptyDescription,
  infoNote,
  onViewDetails,
  onDelete,
  searchFields = [],
  filterConfigs = [],
}: ResourceTabProps) {
  // Use filtering hook
  const {
    searchTerm,
    setSearchTerm,
    filterValues,
    updateFilter,
    filteredData,
    clearAllFilters,
    resultCount,
    totalCount,
  } = useResourceFilters({
    data,
    searchFields,
    filterConfigs,
  });

  if (loading) {
    return <LoadingSpinner message="Loading resources..." />;
  }

  if (error) {
    return <ErrorAlert message={error} />;
  }

  if (data.length === 0) {
    return <EmptyState icon="✨" title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div className="space-y-6">
      {/* Info Note */}
      {infoNote && (
        <div className="group relative overflow-hidden bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 border-2 border-blue-200 rounded-xl p-6 shadow-md hover:shadow-lg transition-all duration-300">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-200 to-indigo-200 rounded-full blur-2xl opacity-30"></div>
          <div className="relative flex items-start gap-4">
            <div className="flex-shrink-0">
              <div className="h-10 w-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg transform group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
                <svg className="h-6 w-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <p className="text-sm text-blue-900 leading-relaxed">
                <span className="font-bold text-base block mb-2 bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent">
                  💡 Why are these resources shown?
                </span>
                <span className="text-slate-700">{infoNote}</span>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      {(searchFields.length > 0 || filterConfigs.length > 0) && (
        <ResourceFilters
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          filters={filterConfigs.map((config) => ({
            ...config,
            value: filterValues[config.name] || 'all',
            onChange: (value: string) => updateFilter(config.name, value),
          }))}
          onClearAll={clearAllFilters}
          resultCount={resultCount}
          totalCount={totalCount}
        />
      )}

      {/* Resource Table */}
      {filteredData.length === 0 ? (
        <EmptyState
          icon="🔍"
          title="No matching resources"
          description="Try adjusting your search or filters to find what you're looking for."
        />
      ) : (
        <ResourceTable
          columns={columns}
          data={filteredData}
          icon={icon}
          onViewDetails={onViewDetails}
          onDelete={onDelete}
        />
      )}
    </div>
  );
}