import React, { useState } from 'react';
import {
  CheckCircle2,
  Clock,
  Search,
  Database,
  Terminal,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  Cpu,
} from 'lucide-react';
import { TraceStep, RetrievedSchemaItem } from '../types';

interface AgentTraceProps {
  trace: TraceStep[] | undefined;
  retrievedSchema: RetrievedSchemaItem[] | undefined;
  totalLatency: number;
}

export const AgentTrace: React.FC<AgentTraceProps> = ({ trace, retrievedSchema, totalLatency }) => {
  const [isOpen, setIsOpen] = useState(true);

  if (!trace || trace.length === 0) {
    return null;
  }

  const getStepIcon = (step: string) => {
    switch (step) {
      case 'question_analysis':
        return <Search className="w-3.5 h-3.5 text-blue-400" />;
      case 'schema_retrieval':
        return <Database className="w-3.5 h-3.5 text-cyan-400" />;
      case 'sql_generation':
        return <Terminal className="w-3.5 h-3.5 text-purple-400" />;
      case 'sql_execution':
        return <Cpu className="w-3.5 h-3.5 text-emerald-400" />;
      case 'answer_generation':
        return <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />;
      default:
        return <CheckCircle2 className="w-3.5 h-3.5 text-gray-400" />;
    }
  };

  return (
    <div className="bg-gray-900/80 border border-white/10 rounded-2xl p-6 shadow-xl backdrop-blur-md">
      {/* Header */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between cursor-pointer select-none"
      >
        <div className="flex items-center space-x-2">
          <Clock className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
            Agent Reasoning & Execution Trace
          </span>
          <span className="text-xs text-gray-500">•</span>
          <span className="text-xs font-mono text-gray-400">
            {totalLatency} ms Total
          </span>
        </div>

        <button className="text-gray-400 hover:text-white transition-colors">
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {/* Timeline view */}
      {isOpen && (
        <div className="mt-5 space-y-3 relative before:absolute before:left-3.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-white/10">
          {trace.map((item, idx) => (
            <div key={idx} className="relative flex items-start space-x-3.5 pl-1 text-xs">
              {/* Node Icon */}
              <div className="z-10 w-7 h-7 rounded-full bg-gray-950 border border-white/15 flex items-center justify-center shrink-0">
                {getStepIcon(item.step)}
              </div>

              {/* Step Content */}
              <div className="flex-1 bg-gray-950/60 border border-white/5 rounded-xl p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-gray-200">
                    {item.title}
                  </span>
                  <span className="text-[11px] font-mono text-cyan-400/80 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-500/20">
                    {item.latency_ms} ms
                  </span>
                </div>

                {/* Details snippet */}
                {item.details && (
                  <div className="text-[11px] text-gray-400 space-y-0.5 font-mono">
                    {item.step === 'question_analysis' && (
                      <p>
                        Entities: <span className="text-gray-200">{item.details.entities?.join(', ') || 'None'}</span> | 
                        Metrics: <span className="text-gray-200">{item.details.metrics?.join(', ') || 'Revenue'}</span> | 
                        Op: <span className="text-gray-200">{item.details.operation}</span>
                      </p>
                    )}
                    {item.step === 'schema_retrieval' && (
                      <p>
                        Retrieved {item.details.item_count} schema items ({item.details.relevant_tables?.join(', ')})
                      </p>
                    )}
                    {item.step === 'sql_generation' && (
                      <p>
                        AST Validated: <span className="text-emerald-400">Read-Only</span> | Retries: {item.details.retries}
                      </p>
                    )}
                    {item.step === 'sql_execution' && (
                      <p>
                        Returned {item.details.row_count} rows | Verified: <span className="text-emerald-400">Pass</span>
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Retrieved Schema drawer inside Trace */}
          {retrievedSchema && retrievedSchema.length > 0 && (
            <div className="mt-4 pt-3 border-t border-white/5">
              <span className="text-xs font-semibold text-gray-400 block mb-2">
                Dynamically Injected Schema Context (pgvector top-K):
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {retrievedSchema.slice(0, 6).map((s, i) => (
                  <div key={i} className="p-2 rounded-lg bg-gray-950/40 border border-white/5 text-[11px]">
                    <div className="flex items-center justify-between text-cyan-300 font-mono">
                      <span>{s.display_name}</span>
                      <span className="text-gray-500">score: {s.score}</span>
                    </div>
                    <p className="text-gray-400 truncate mt-0.5">{s.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
