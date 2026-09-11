import React from 'react';
import { SystemHealth } from '../types';
import { Database, Sparkles, Activity, ShieldCheck, BarChart3, Layers } from 'lucide-react';

interface HeaderProps {
  health: SystemHealth | null;
  mode: 'agent' | 'baseline';
  setMode: (mode: 'agent' | 'baseline') => void;
  onOpenMetrics: () => void;
}

export const Header: React.FC<HeaderProps> = ({ health, mode, setMode, onOpenMetrics }) => {
  const isDemo = health?.ai.demo_mode ?? true;
  const isConnected = health?.database.status === 'connected';
  const factsCount = health?.database.financial_facts_count ?? 380;
  const companiesCount = health?.database.companies_count ?? 7;

  return (
    <header className="border-b border-white/10 bg-gray-900/60 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        
        {/* Brand Logo & Title */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-cyan-500 to-emerald-400 p-0.5 shadow-lg shadow-cyan-500/20">
            <div className="w-full h-full bg-gray-950 rounded-[10px] flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-white bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-transparent">
                FinSQL Agent
              </h1>
              <span className="text-[11px] px-2 py-0.5 rounded-full font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
                v1.0
              </span>
            </div>
            <p className="text-xs text-gray-400 hidden sm:block">
              Ask questions. Query financial data. Get explainable answers.
            </p>
          </div>
        </div>

        {/* Status Indicators & Mode Toggle */}
        <div className="flex items-center flex-wrap gap-2.5">
          
          {/* Mode Selector */}
          <div className="flex items-center bg-gray-950/80 p-1 rounded-xl border border-white/10">
            <button
              onClick={() => setMode('agent')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                mode === 'agent'
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>FinSQL Agent</span>
            </button>
            <button
              onClick={() => setMode('baseline')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                mode === 'baseline'
                  ? 'bg-amber-600 text-white shadow-md shadow-amber-600/30'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Baseline</span>
            </button>
          </div>

          {/* Evaluation Benchmark Button */}
          <button
            onClick={onOpenMetrics}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-medium bg-cyan-950/50 hover:bg-cyan-900/60 text-cyan-300 border border-cyan-500/30 transition-all cursor-pointer"
          >
            <BarChart3 className="w-3.5 h-3.5 text-cyan-400" />
            <span>Benchmark Report</span>
          </button>

          {/* Live Status Badge */}
          <div className="flex items-center space-x-2 bg-gray-950/70 border border-white/10 px-3 py-1.5 rounded-xl text-xs">
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                isConnected ? 'bg-emerald-400' : 'bg-rose-400'
              }`} />
              <span className={`relative inline-flex rounded-full h-2 w-2 ${
                isConnected ? 'bg-emerald-500' : 'bg-rose-500'
              }`} />
            </span>
            <span className="text-gray-300 font-medium">
              {isConnected ? (isDemo ? 'Demo Mode' : 'Online') : 'Offline'}
            </span>
            <span className="text-gray-600">•</span>
            <span className="text-gray-400 font-mono text-[11px]">
              {companiesCount} Companies / {factsCount} Facts
            </span>
          </div>

        </div>

      </div>
    </header>
  );
};
