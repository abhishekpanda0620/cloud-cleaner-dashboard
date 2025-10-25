import { ReactNode } from 'react';

interface Column {
  header: string;
  accessor: string;
  render?: (value: any, row: any) => ReactNode;
  align?: 'left' | 'right';
  width?: string;
}

interface ResourceTableProps {
  columns: Column[];
  data: any[];
  icon: string;
  onViewDetails?: (row: any) => void;
  onDelete?: (row: any) => void;
}

export default function ResourceTable({
  columns,
  data,
  icon,
  onViewDetails,
  onDelete
}: ResourceTableProps) {
  return (
    <div className="space-y-4">
      {data.map((row, rowIndex) => {
        // Separate actions from other columns
        const actionColumn = columns.find((col) => col.accessor === 'actions');
        const dataColumns = columns.filter((col) => col.accessor !== 'actions');

        return (
          <div
            key={rowIndex}
            className="bg-gradient-to-r from-slate-50  to-slate-100 border border-slate-200 rounded-lg p-6 hover:shadow-md transition-shadow"
          >
            {/* Data Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {dataColumns.map((column, colIndex) => (
                <div key={colIndex} className="flex flex-col">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                    {column.header}
                  </span>
                  <div className="flex items-center space-x-2">
                    {colIndex === 0 && <span className="text-2xl">{icon}</span>}
                    <div className="flex-1">
                      {column.render ? (
                        column.render(row[column.accessor], row)
                      ) : (
                        <span className="text-sm font-medium text-slate-900">
                          {row[column.accessor]}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Actions Row */}
            <div className="mt-6 pt-6 border-t border-slate-200 flex justify-end gap-3">
              {actionColumn && actionColumn.render?.(null, row)}
              
              {/* Default action buttons if handlers are provided */}
              {(onViewDetails || onDelete) && (
                <>
                  {onViewDetails && (
                    <button
                      onClick={() => onViewDetails(row)}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      View Details
                    </button>
                  )}
                  
                  {onDelete && (
                    <button
                      onClick={() => onDelete(row)}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      Delete
                    </button>
                  )}
                </>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}