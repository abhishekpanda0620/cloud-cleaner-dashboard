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
            className="group relative overflow-hidden bg-white border-2 border-slate-200 rounded-xl p-6 hover:shadow-xl hover:border-blue-300 transition-all duration-300 transform hover:-translate-y-1"
          >
            {/* Decorative gradient overlay */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full blur-2xl opacity-0 group-hover:opacity-30 transition-opacity duration-300 -z-10"></div>
            
            {/* Icon Badge */}
            <div className="absolute top-4 right-4 h-12 w-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg transform group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
              <span className="text-2xl">{icon}</span>
            </div>

            {/* Data Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pr-16">
              {dataColumns.map((column, colIndex) => (
                <div key={colIndex} className="flex flex-col">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                    <span className="h-1 w-1 rounded-full bg-slate-400"></span>
                    {column.header}
                  </span>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1">
                      {column.render ? (
                        column.render(row[column.accessor], row)
                      ) : (
                        <span className="text-sm font-semibold text-slate-900">
                          {row[column.accessor]}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Actions Row */}
            <div className="mt-6 pt-6 border-t-2 border-slate-200 flex justify-end gap-3">
              {actionColumn && actionColumn.render?.(null, row)}
              
              {/* Default action buttons if handlers are provided */}
              {(onViewDetails || onDelete) && (
                <>
                  {onViewDetails && (
                    <button
                      onClick={() => onViewDetails(row)}
                      className="group/btn relative overflow-hidden inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-sm font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-indigo-400 opacity-0 group-hover/btn:opacity-20 transition-opacity duration-300"></div>
                      <svg className="w-4 h-4 relative group-hover/btn:scale-110 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      <span className="relative">View Details</span>
                    </button>
                  )}
                  
                  {onDelete && (
                    <button
                      onClick={() => onDelete(row)}
                      className="group/btn relative overflow-hidden inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-red-600 to-rose-600 text-white text-sm font-semibold rounded-lg hover:from-red-700 hover:to-rose-700 transition-all duration-300 shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-red-400 to-rose-400 opacity-0 group-hover/btn:opacity-20 transition-opacity duration-300"></div>
                      <svg className="w-4 h-4 relative group-hover/btn:scale-110 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      <span className="relative">Delete</span>
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