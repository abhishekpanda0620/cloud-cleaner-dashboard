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
}

export default function ResourceTab({
  loading,
  error,
  data,
  columns,
  icon,
  emptyTitle,
  emptyDescription
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

  return <ResourceTable columns={columns} data={data} icon={icon} />;
}