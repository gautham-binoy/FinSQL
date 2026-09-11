import { QueryResponse, SystemHealth, ExampleQuestion, EvaluationBenchmarkReport } from '../types';

const API_BASE = '/api';

export async function submitQuery(question: string, mode: 'agent' | 'baseline' = 'agent'): Promise<QueryResponse> {
  const res = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, mode }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Query failed with status ${res.status}`);
  }
  return res.json();
}

export async function fetchHealth(): Promise<SystemHealth> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to fetch system health');
  return res.json();
}

export async function fetchExamples(): Promise<{ count: number; examples: ExampleQuestion[] }> {
  const res = await fetch(`${API_BASE}/examples`);
  if (!res.ok) throw new Error('Failed to fetch examples');
  return res.json();
}

export async function fetchMetrics(): Promise<EvaluationBenchmarkReport> {
  const res = await fetch(`${API_BASE}/metrics`);
  if (!res.ok) throw new Error('Failed to fetch evaluation metrics');
  return res.json();
}

export async function fetchSchema(): Promise<any> {
  const res = await fetch(`${API_BASE}/schema`);
  if (!res.ok) throw new Error('Failed to fetch schema metadata');
  return res.json();
}
