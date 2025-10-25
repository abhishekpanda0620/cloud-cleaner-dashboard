import LoadingSpinner from './LoadingSpinner';
import ErrorAlert from './ErrorAlert';
import EmptyState from './EmptyState';
import ResourceTable from './ResourceTable';

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
  onDelete
}: ResourceTabProps) {
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
    <div className="space-y-4">
      {/* Info Note */}
      {infoNote && (
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                <span className="font-semibold">Why are these resources shown?</span>
                <br />
                {infoNote}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Resource Table */}
      <ResourceTable
        columns={columns}
        data={data}
        icon={icon}
        onViewDetails={onViewDetails}
        onDelete={onDelete}
      />
    </div>
  );
}