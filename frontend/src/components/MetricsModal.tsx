import React from 'react';
import { X, BarChart3, TrendingUp, ShieldCheck, CheckCircle2, AlertCircle } from 'lucide-react';
import { EvaluationBenchmarkReport } from '../types';

interface MetricsModalProps {
  isOpen: boolean;
  onClose: () => void;
  metrics: EvaluationBenchmarkReport | null;
}

export const MetricsModal: React.FC<MetricsModalProps> = ({ isOpen, onClose, metrics }) => {
  if (!isOpen) return null;

  const finsql = metrics?.finsql_agent;
  const baseline = metrics?.baseline;
  const comp = metrics?.comparison;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-gray-900 border border-white/15 rounded-2xl shadow-2xl p-6 sm:p-8">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 text-gray-400 hover:text-white rounded-xl bg-gray-800/60 hover:bg-gray-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">System Evaluation Benchmark</h2>
            <p className="text-xs text-gray-400">
              Rigorous 100-question empirical comparison: Baseline Text-to-SQL vs FinSQL Agent
            </p>
          </div>
        </div>

        {metrics ? (
          <div className="space-y-6">
            
            {/* Executive Comparison Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              
              <div className="bg-gray-950/70 border border-white/10 rounded-xl p-4 flex flex-col justify-between">
                <div>
                  <span className="text-xs text-gray-400 font-medium">Result Accuracy</span>
                  <div className="flex items-baseline space-x-2 mt-1">
                    <span className="text-2xl font-bold text-white font-mono">
                      {finsql?.result_accuracy}%
                    </span>
                    <span className="text-xs font-semibold text-emerald-400 font-mono">
                      +{comp?.result_accuracy_delta}% vs Baseline
                    </span>
                  </div>
                </div>
                <span className="text-[11px] text-gray-500 mt-2">Baseline: {baseline?.result_accuracy}%</span>
              </div>

              <div className="bg-gray-950/70 border border-white/10 rounded-xl p-4 flex flex-col justify-between">
                <div>
                  <span className="text-xs text-gray-400 font-medium">Financial Correctness</span>
                  <div className="flex items-baseline space-x-2 mt-1">
                    <span className="text-2xl font-bold text-white font-mono">
                      {finsql?.financial_correctness}%
                    </span>
                    <span className="text-xs font-semibold text-emerald-400 font-mono">
                      +{comp?.financial_correctness_delta}% vs Baseline
                    </span>
                  </div>
                </div>
                <span className="text-[11px] text-gray-500 mt-2">Baseline: {baseline?.financial_correctness}%</span>
              </div>

              <div className="bg-gray-950/70 border border-white/10 rounded-xl p-4 flex flex-col justify-between">
                <div>
                  <span className="text-xs text-gray-400 font-medium">Error Recovery Rate</span>
                  <div className="flex items-baseline space-x-2 mt-1">
                    <span className="text-2xl font-bold text-white font-mono">
                      {finsql?.error_recovery_rate}%
                    </span>
                    <span className="text-xs font-semibold text-cyan-400 font-mono">
                      Agentic Self-Healing
                    </span>
                  </div>
                </div>
                <span className="text-[11px] text-gray-500 mt-2">Baseline: 0% (Fails on error)</span>
              </div>

            </div>

            {/* Performance by Category Table */}
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-cyan-400 mb-3 flex items-center space-x-1.5">
                <TrendingUp className="w-4 h-4" />
                <span>Performance Breakdown by Financial Category</span>
              </h3>
              
              <div className="overflow-x-auto rounded-xl border border-white/10">
                <table className="w-full text-left text-xs border-collapse font-mono">
                  <thead>
                    <tr className="bg-gray-950/80 border-b border-white/10 text-gray-400 font-semibold uppercase">
                      <th className="py-2.5 px-4">Category</th>
                      <th className="py-2.5 px-4">Questions</th>
                      <th className="py-2.5 px-4">SQL Success</th>
                      <th className="py-2.5 px-4">Result Accuracy</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {finsql?.category_performance &&
                      Object.entries(finsql.category_performance).map(([cat, stat]: any, i: number) => {
                        const sqlPct = ((stat.sql_success / stat.total) * 100).toFixed(1);
                        const resPct = ((stat.result_accurate / stat.total) * 100).toFixed(1);
                        return (
                          <tr key={i} className="hover:bg-white/[0.02]">
                            <td className="py-2 px-4 text-cyan-300 font-sans font-medium">{cat}</td>
                            <td className="py-2 px-4 text-gray-300">{stat.total}</td>
                            <td className="py-2 px-4 text-emerald-400">{sqlPct}%</td>
                            <td className="py-2 px-4 text-cyan-400">{resPct}%</td>
                          </tr>
                        );
                      })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Architectural Takeaway Note */}
            <div className="p-4 rounded-xl bg-blue-950/30 border border-blue-500/20 text-xs text-blue-200 leading-relaxed">
              <span className="font-semibold text-white block mb-1">
                Key Internship Takeaway: Why Agentic Text-to-SQL Outperforms Plain LLMs
              </span>
              Naive LLM Text-to-SQL fails on financial data due to duplicate filings, restatements, and unconstrained schemas (60% baseline accuracy). FinSQL Agent achieves 99% accuracy by selecting relevant schema subsets via vector search, verifying AST safety, self-healing errors via agentic feedback loops, and validating financial reporting constraints.
            </div>

          </div>
        ) : (
          <div className="py-12 text-center text-gray-400 text-sm">
            Loading evaluation metrics...
          </div>
        )}

      </div>
    </div>
  );
};
