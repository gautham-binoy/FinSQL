import React from 'react';
import { QueryResponse } from '../types';
import { CheckCircle2, TrendingUp, AlertTriangle, FileText, Info } from 'lucide-react';

interface AnswerSectionProps {
  data: QueryResponse;
}

export const AnswerSection: React.FC<AnswerSectionProps> = ({ data }) => {
  const { answer, detailed_analysis, key_metrics, assumptions, verification } = data;
  const warnings = verification?.warnings || [];

  return (
    <div className="bg-gray-900/80 border border-white/10 rounded-2xl p-6 shadow-xl backdrop-blur-md">
      
      {/* Executive Summary Header */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-cyan-400 mb-1">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Executive Financial Answer</span>
          </div>
          <p className="text-lg sm:text-xl font-semibold text-gray-100 leading-snug">
            {answer}
          </p>
        </div>
      </div>

      {/* KPI Highlight Cards */}
      {key_metrics && key_metrics.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 my-5">
          {key_metrics.map((kpi, idx) => (
            <div
              key={idx}
              className="bg-gray-950/70 border border-white/10 rounded-xl p-3.5 flex flex-col justify-center"
            >
              <span className="text-xs text-gray-400 font-medium truncate mb-1">
                {kpi.label}
              </span>
              <span className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-white via-cyan-100 to-cyan-300 bg-clip-text text-transparent font-mono">
                {kpi.value}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Detailed Analysis Breakdown */}
      {detailed_analysis && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
            <FileText className="w-3.5 h-3.5 text-gray-400" />
            <span>Detailed Breakdown</span>
          </div>
          <div className="text-sm text-gray-300 space-y-1.5 leading-relaxed whitespace-pre-line font-sans">
            {detailed_analysis}
          </div>
        </div>
      )}

      {/* Assumptions & Financial Caveats */}
      {assumptions && assumptions.length > 0 && (
        <div className="mt-4 pt-3 border-t border-white/5 flex flex-wrap items-center gap-2">
          <span className="text-[11px] text-gray-500 font-medium flex items-center space-x-1">
            <Info className="w-3 h-3" />
            <span>Assumptions:</span>
          </span>
          {assumptions.map((assump, idx) => (
            <span
              key={idx}
              className="text-[11px] px-2.5 py-0.5 rounded-full bg-gray-800/80 text-gray-400 border border-white/5"
            >
              {assump}
            </span>
          ))}
        </div>
      )}

      {/* Verification Warnings (if any) */}
      {warnings.length > 0 && (
        <div className="mt-4 p-3 rounded-xl bg-amber-950/40 border border-amber-500/30 flex items-start space-x-2.5 text-xs text-amber-300">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-semibold">Financial Verification Notice:</span>
            {warnings.map((w, i) => (
              <p key={i} className="text-amber-200/90">{w}</p>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};
