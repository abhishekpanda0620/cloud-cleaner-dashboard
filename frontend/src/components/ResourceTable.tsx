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
}

export default function ResourceTable({ columns, data, icon }: ResourceTableProps) {
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
            {actionColumn && (
              <div className="mt-6 pt-6 border-t border-slate-200 flex justify-end gap-3">
                {actionColumn.render?.(null, row)}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}