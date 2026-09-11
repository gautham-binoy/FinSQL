import React, { useState } from 'react';
import { Search, Sparkles, CornerDownLeft, Loader2 } from 'lucide-react';
import { ExampleQuestion } from '../types';

interface QuestionInputProps {
  onSearch: (question: string) => void;
  isLoading: boolean;
  examples: ExampleQuestion[];
}

export const QuestionInput: React.FC<QuestionInputProps> = ({ onSearch, isLoading, examples }) => {
  const [inputVal, setInputVal] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputVal.trim() && !isLoading) {
      onSearch(inputVal.trim());
    }
  };

  const handleSelectExample = (q: string) => {
    setInputVal(q);
    onSearch(q);
  };

  // Top prompt chips
  const quickChips = [
    { label: "Apple Revenue 2023", q: "What was Apple's revenue in 2023?" },
    { label: "Apple vs Microsoft", q: "Compare Apple's revenue with Microsoft's revenue in 2023." },
    { label: "Apple Revenue Growth", q: "What was Apple's revenue growth between 2022 and 2023?" },
    { label: "Highest Revenue 2023", q: "Which company had the highest revenue in 2023?" },
    { label: "5-Year Apple Trend", q: "Show Apple's revenue from 2020 to 2025." },
    { label: "Top Margin Ranking", q: "Which company had the highest net income margin in 2023?" },
    { label: "5-Yr Revenue & Net Income", q: "Give me Apple's revenue and net income for the last five fiscal years." },
    { label: "Average 2023 Revenue", q: "What was the average revenue of the companies in 2023?" },
    { label: "Restated vs Original", q: "Show Apple's consolidated revenue in 2023 excluding restatements." },
  ];

  return (
    <div className="w-full">
      {/* Search Input Box */}
      <form onSubmit={handleSubmit} className="relative group">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 via-cyan-500 to-emerald-500 rounded-2xl blur opacity-30 group-hover:opacity-60 transition duration-300" />
        
        <div className="relative flex items-center bg-gray-900/95 border border-white/15 rounded-2xl shadow-2xl p-2 focus-within:border-cyan-500/50">
          <Search className="w-5 h-5 text-gray-400 ml-3 shrink-0" />
          
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="Ask a financial question (e.g. 'Compare Apple and Microsoft revenue in 2023' or 'Apple revenue growth')..."
            className="w-full bg-transparent px-4 py-3 text-sm sm:text-base text-gray-100 placeholder-gray-500 focus:outline-none"
            disabled={isLoading}
          />

          <button
            type="submit"
            disabled={!inputVal.trim() || isLoading}
            className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed text-white px-5 py-3 rounded-xl font-medium text-sm shadow-lg shadow-blue-600/30 transition-all cursor-pointer shrink-0"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="hidden sm:inline">Executing...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-cyan-200" />
                <span>Ask</span>
                <CornerDownLeft className="w-3.5 h-3.5 opacity-60 hidden sm:inline" />
              </>
            )}
          </button>
        </div>
      </form>

      {/* Suggested Prompt Chips */}
      <div className="mt-4">
        <div className="flex items-center space-x-2 mb-2 text-xs text-gray-400 font-medium">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Suggested Questions:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {quickChips.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleSelectExample(chip.q)}
              className="px-3 py-1.5 rounded-lg text-xs bg-gray-900/80 hover:bg-gray-800 text-gray-300 hover:text-white border border-white/10 hover:border-cyan-500/30 transition-all cursor-pointer shadow-sm hover:scale-[1.02] active:scale-[0.98]"
            >
              {chip.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
