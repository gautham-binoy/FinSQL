import React, { useState } from 'react';
import { Table, ChevronLeft, ChevronRight } from 'lucide-react';
import { ExecutionResult } from '../types';

interface DataTableProps {
  execution: ExecutionResult | undefined;
}

function formatCell(val: any): string {
  if (val === null || val === undefined) return '-';
  if (typeof val === 'number') {
    if (Math.abs(val) >= 1e9) return `$${(val / 1e9).toFixed(2)}B`;
    if (Math.abs(val) >= 1e6) return `$${(val / 1e6).toFixed(2)}M`;
    if (Number.isInteger(val)) return val.toLocaleString();
    return val.toFixed(2);
  }
  return String(val);
}

export const DataTable: React.FC<DataTableProps> = ({ execution }) => {
  const [page, setPage] = useState(0);
  const rowsPerPage = 10;

  if (!execution || !execution.rows || execution.rows.length === 0) {
    return null;
  }

  const columns = execution.columns || Object.keys(execution.rows[0] || {});
  const totalRows = execution.rows.length;
  const totalPages = Math.ceil(totalRows / rowsPerPage);
  const displayedRows = execution.rows.slice(page * rowsPerPage, (page + 1) * rowsPerPage);

  return (
    <div className="bg-gray-900/80 border border-white/10 rounded-2xl p-6 shadow-xl backdrop-blur-md">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Table className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
            Database Result Set
          </span>
          <span className="text-xs text-gray-500">•</span>
          <span className="text-xs text-gray-400 font-mono">
            {totalRows} {totalRows === 1 ? 'record' : 'records'} ({execution.execution_time_ms} ms)
          </span>
        </div>

        {/* Pagination controls if needed */}
        {totalPages > 1 && (
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-gray-400">
              Page {page + 1} of {totalPages}
            </span>
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="p-1 rounded bg-gray-800 disabled:opacity-40 text-gray-300 hover:text-white"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
              disabled={page === totalPages - 1}
              className="p-1 rounded bg-gray-800 disabled:opacity-40 text-gray-300 hover:text-white"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>

      {/* Table grid */}
      <div className="overflow-x-auto rounded-xl border border-white/10">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-gray-950/80 border-b border-white/10 text-gray-400 font-semibold uppercase tracking-wider">
              {columns.map((col, idx) => (
                <th key={idx} className="py-3 px-4">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 font-mono">
            {displayedRows.map((row, rIdx) => (
              <tr
                key={rIdx}
                className="hover:bg-white/[0.02] transition-colors odd:bg-gray-950/30"
              >
                {columns.map((col, cIdx) => (
                  <td key={cIdx} className="py-2.5 px-4 text-gray-200">
                    {formatCell(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
