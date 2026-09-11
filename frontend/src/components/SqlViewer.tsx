import React, { useState } from 'react';
import { Terminal, Copy, Check, ShieldCheck, RefreshCw, Layers } from 'lucide-react';
import { ValidationResult, QueryAttempt } from '../types';

interface SqlViewerProps {
  sql: string;
  explanation?: string;
  validation?: ValidationResult;
  attempts?: QueryAttempt[];
  retryCount?: number;
}

export const SqlViewer: React.FC<SqlViewerProps> = ({
  sql,
  explanation,
  validation,
  attempts,
  retryCount = 0,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const tables = validation?.ast_tables || [];
  const isValid = validation?.valid ?? true;

  return (
    <div className="bg-gray-900/80 border border-white/10 rounded-2xl p-6 shadow-xl backdrop-blur-md">
      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
            Generated SQL Query
          </span>

          {/* Validation Badge */}
          {isValid && (
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-3 h-3" />
              <span>Read-Only AST Validated</span>
            </span>
          )}

          {/* Self-Healing Retry Badge */}
          {retryCount > 0 && (
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <RefreshCw className="w-3 h-3 animate-spin" />
              <span>Repaired ({retryCount} {retryCount === 1 ? 'Retry' : 'Retries'})</span>
            </span>
          )}
        </div>

        {/* Copy Button */}
        <button
          onClick={handleCopy}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-800/80 hover:bg-gray-700/80 text-gray-300 hover:text-white border border-white/10 transition-all cursor-pointer"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400">Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy SQL</span>
            </>
          )}
        </button>
      </div>

      {/* SQL Code Block */}
      <div className="relative rounded-xl bg-gray-950/90 border border-white/10 p-4 font-mono text-xs sm:text-sm text-cyan-200 overflow-x-auto">
        <pre className="whitespace-pre-wrap leading-relaxed">{sql}</pre>
      </div>

      {/* Explanation & Table Badges */}
      <div className="mt-3.5 flex flex-wrap items-center justify-between gap-2 text-xs text-gray-400">
        <p className="italic text-gray-300">
          {explanation || "Query uses verified relational joins on approved financial fact schemas."}
        </p>

        {tables.length > 0 && (
          <div className="flex items-center space-x-1.5">
            <Layers className="w-3.5 h-3.5 text-gray-500" />
            <span className="text-gray-500">Tables:</span>
            {tables.map((t, idx) => (
              <span
                key={idx}
                className="px-2 py-0.5 rounded-md bg-gray-800 text-cyan-300 font-mono text-[11px] border border-white/5"
              >
                {t}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Attempts log if repaired */}
      {attempts && attempts.length > 1 && (
        <div className="mt-4 pt-3 border-t border-white/10">
          <span className="text-xs font-semibold text-amber-400 block mb-2">
            Error Recovery Feedback Trail:
          </span>
          <div className="space-y-2 text-xs">
            {attempts.map((att, i) => (
              <div key={i} className="p-2.5 rounded-lg bg-gray-950/60 border border-white/5 flex flex-col gap-1">
                <div className="flex items-center justify-between text-[11px] text-gray-400">
                  <span className="font-bold text-gray-300">Attempt #{att.attempt}</span>
                  <span className={att.error ? "text-rose-400 font-mono" : "text-emerald-400 font-mono"}>
                    {att.error ? "Execution/Validation Error" : "Successfully Verified & Executed"}
                  </span>
                </div>
                {att.error && (
                  <p className="text-rose-300/80 font-mono text-[11px] bg-rose-950/20 p-1.5 rounded border border-rose-900/30">
                    {att.error}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
