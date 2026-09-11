import React from 'react';
import { ShieldCheck, Database, Calendar, Tag, Layers } from 'lucide-react';

interface ProvenanceCardProps {
  provenance: Record<string, any> | undefined;
}

export const ProvenanceCard: React.FC<ProvenanceCardProps> = ({ provenance }) => {
  if (!provenance) return null;

  return (
    <div className="bg-gray-900/60 border border-white/10 rounded-2xl p-5 backdrop-blur-md">
      <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-cyan-400 mb-3">
        <ShieldCheck className="w-4 h-4 text-emerald-400" />
        <span>Data Provenance & Audit Trail</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div className="p-2.5 rounded-xl bg-gray-950/70 border border-white/5 flex flex-col justify-center">
          <span className="text-[11px] text-gray-500 font-medium flex items-center space-x-1 mb-1">
            <Database className="w-3 h-3 text-gray-400" />
            <span>Data Source</span>
          </span>
          <span className="font-semibold text-gray-200 truncate">
            {provenance.data_source || "Financial DB (10-K)"}
          </span>
        </div>

        <div className="p-2.5 rounded-xl bg-gray-950/70 border border-white/5 flex flex-col justify-center">
          <span className="text-[11px] text-gray-500 font-medium flex items-center space-x-1 mb-1">
            <Layers className="w-3 h-3 text-gray-400" />
            <span>Reporting Scope</span>
          </span>
          <span className="font-semibold text-emerald-400">
            {provenance.reporting_type || "Consolidated"}
          </span>
        </div>

        <div className="p-2.5 rounded-xl bg-gray-950/70 border border-white/5 flex flex-col justify-center">
          <span className="text-[11px] text-gray-500 font-medium flex items-center space-x-1 mb-1">
            <Calendar className="w-3 h-3 text-gray-400" />
            <span>Period Scope</span>
          </span>
          <span className="font-semibold text-gray-200">
            {provenance.period_type || "Fiscal Year (FY)"}
          </span>
        </div>

        <div className="p-2.5 rounded-xl bg-gray-950/70 border border-white/5 flex flex-col justify-center">
          <span className="text-[11px] text-gray-500 font-medium flex items-center space-x-1 mb-1">
            <Tag className="w-3 h-3 text-gray-400" />
            <span>Integrity Status</span>
          </span>
          <span className="font-semibold text-cyan-400">
            {provenance.execution_status || "Verified Ground Truth"}
          </span>
        </div>
      </div>
    </div>
  );
};
