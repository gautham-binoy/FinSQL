import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { QuestionInput } from './components/QuestionInput';
import { AnswerSection } from './components/AnswerSection';
import { Visualizer } from './components/Visualizer';
import { SqlViewer } from './components/SqlViewer';
import { DataTable } from './components/DataTable';
import { AgentTrace } from './components/AgentTrace';
import { ProvenanceCard } from './components/ProvenanceCard';
import { MetricsModal } from './components/MetricsModal';
import {
  submitQuery,
  fetchHealth,
  fetchExamples,
  fetchMetrics,
} from './services/api';
import {
  QueryResponse,
  SystemHealth,
  ExampleQuestion,
  EvaluationBenchmarkReport,
} from './types';
import { AlertCircle, Sparkles } from 'lucide-react';

export function App() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [examples, setExamples] = useState<ExampleQuestion[]>([]);
  const [metrics, setMetrics] = useState<EvaluationBenchmarkReport | null>(null);
  const [isMetricsOpen, setIsMetricsOpen] = useState(false);

  const [mode, setMode] = useState<'agent' | 'baseline'>('agent');
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load health, examples, metrics on start
  useEffect(() => {
    fetchHealth().then(setHealth).catch(console.error);
    fetchExamples().then((d) => setExamples(d.examples)).catch(console.error);
    fetchMetrics().then(setMetrics).catch(console.error);

    // Run initial demo question
    handleSearch("Compare Apple's revenue with Microsoft's revenue in 2023.", 'agent');
  }, []);

  const handleSearch = async (question: string, queryMode = mode) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await submitQuery(question, queryMode);
      setQueryResult(res);
    } catch (err: any) {
      setError(err.message || 'An error occurred while executing the query.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-950 text-gray-100 font-sans">
      {/* Header */}
      <Header
        health={health}
        mode={mode}
        setMode={(newMode) => {
          setMode(newMode);
          if (queryResult) {
            handleSearch(queryResult.question, newMode);
          }
        }}
        onOpenMetrics={() => setIsMetricsOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Question Search Box & Suggestions */}
        <section>
          <QuestionInput
            onSearch={(q) => handleSearch(q, mode)}
            isLoading={isLoading}
            examples={examples}
          />
        </section>

        {/* Global Error Notice */}
        {error && (
          <div className="p-4 rounded-xl bg-rose-950/50 border border-rose-500/30 text-rose-300 text-sm flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {/* Query Results Display */}
        {queryResult && (
          <div className="space-y-8 animate-fadeIn">
            
            {/* Mode Indicator Banner if in Baseline */}
            {queryResult.mode === 'Baseline Text-to-SQL' && (
              <div className="p-3.5 rounded-xl bg-amber-950/40 border border-amber-500/30 flex items-center justify-between text-xs text-amber-300">
                <span className="font-semibold">
                  Running in Baseline Text-to-SQL Mode (No schema retrieval, no AST validation, no repair loop)
                </span>
                <button
                  onClick={() => {
                    setMode('agent');
                    handleSearch(queryResult.question, 'agent');
                  }}
                  className="px-3 py-1 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium cursor-pointer transition-colors"
                >
                  Switch to FinSQL Agent
                </button>
              </div>
            )}

            {/* Answer Section */}
            <AnswerSection data={queryResult} />

            {/* Dynamic Visualization (Bar / Line / KPI) */}
            <Visualizer
              chart={queryResult.chart}
              rows={queryResult.execution?.rows}
            />

            {/* Generated SQL Section */}
            <SqlViewer
              sql={queryResult.sql}
              explanation={queryResult.sql_explanation}
              validation={queryResult.validation}
              attempts={queryResult.attempts}
              retryCount={queryResult.retry_count}
            />

            {/* Data Table */}
            <DataTable execution={queryResult.execution} />

            {/* Agent Observability Pipeline Trace */}
            <AgentTrace
              trace={queryResult.trace}
              retrievedSchema={queryResult.retrieved_schema}
              totalLatency={queryResult.latency_ms}
            />

            {/* Provenance and Integrity Metadata */}
            <ProvenanceCard provenance={queryResult.provenance} />

          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-gray-950/90 py-6 text-center text-xs text-gray-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>FinSQL Agent — Production-Style Agentic Text-to-SQL for Financial Intelligence</span>
          <span>Calibrated against SEC EDGAR 10-K Filings • Extensible to BigQuery</span>
        </div>
      </footer>

      {/* Benchmark Evaluation Modal */}
      <MetricsModal
        isOpen={isMetricsOpen}
        onClose={() => setIsMetricsOpen(false)}
        metrics={metrics}
      />
    </div>
  );
}

export default App;
