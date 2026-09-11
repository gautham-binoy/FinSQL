export interface KeyMetric {
  label: string;
  value: string;
}

export interface ChartRecommendation {
  type: 'bar' | 'line' | 'kpi' | 'table' | 'none';
  title: string;
  x_key: string;
  y_keys: string[];
  description?: string;
}

export interface ExecutionResult {
  success: boolean;
  rows: Array<Record<string, any>>;
  columns: string[];
  row_count: number;
  execution_time_ms: number;
  truncated?: boolean;
  error_type?: string;
  message?: string;
}

export interface ValidationResult {
  valid: boolean;
  reason: string;
  error_type?: string | null;
  ast_tables: string[];
  ast_columns: string[];
  has_limit: boolean;
}

export interface VerificationResult {
  valid: boolean;
  needs_repair?: boolean;
  warnings: string[];
  checks: {
    empty_result?: boolean;
    duplicate_rows?: boolean;
    unit_consistency?: boolean;
    restatement_conflict?: boolean;
    reporting_type_conflict?: boolean;
    company_match?: boolean;
    period_match?: boolean;
    value_plausibility?: boolean;
  };
  repair_reason?: string | null;
}

export interface RetrievedSchemaItem {
  id: number;
  item_type: string;
  table_name: string | null;
  column_name: string | null;
  concept_name: string | null;
  display_name: string;
  description: string;
  score: number;
  sample_values?: string;
}

export interface TraceStep {
  step: string;
  title: string;
  status: 'completed' | 'failed' | 'pending';
  latency_ms: number;
  details: Record<string, any>;
}

export interface QueryAttempt {
  attempt: number;
  sql: string;
  validation?: ValidationResult;
  execution?: ExecutionResult;
  verification?: VerificationResult;
  error?: string;
  repaired?: boolean;
}

export interface QueryResponse {
  request_id: string;
  timestamp?: string;
  question: string;
  mode: string;
  sql: string;
  sql_explanation?: string;
  assumptions?: string[];
  answer: string;
  detailed_analysis?: string;
  key_metrics?: KeyMetric[];
  chart?: ChartRecommendation;
  analysis?: {
    entities: string[];
    tickers: string[];
    metrics: string[];
    time_period: {
      type: string;
      start_year: number;
      end_year: number;
      years: number[];
    };
    operation: string;
  };
  retrieved_schema?: RetrievedSchemaItem[];
  validation?: ValidationResult;
  execution?: ExecutionResult;
  verification?: VerificationResult;
  provenance?: Record<string, any>;
  attempts?: QueryAttempt[];
  retry_count?: number;
  trace?: TraceStep[];
  latency_ms: number;
  model?: string;
}

export interface ExampleQuestion {
  id: string;
  category: string;
  question: string;
  description: string;
  difficulty: string;
}

export interface SystemHealth {
  status: string;
  database: {
    status: string;
    url_type: string;
    companies_count: number;
    financial_facts_count: number;
    financial_concepts_count: number;
    schema_embeddings_count: number;
  };
  ai: {
    gemini_configured: boolean;
    demo_mode: boolean;
    model_name: string;
    embedding_model: string;
  };
  version: string;
}

export interface EvaluationBenchmarkReport {
  timestamp: string;
  sample_size: number;
  finsql_agent: {
    sql_execution_accuracy: number;
    result_accuracy: number;
    schema_retrieval_accuracy: number;
    financial_correctness: number;
    error_recovery_rate: number;
    average_latency_ms: number;
    average_retry_count: number;
    category_performance: Record<string, { total: number; sql_success: number; result_accurate: number }>;
  };
  baseline: {
    sql_execution_accuracy: number;
    result_accuracy: number;
    financial_correctness: number;
    average_latency_ms: number;
  };
  comparison: {
    sql_execution_delta: number;
    result_accuracy_delta: number;
    financial_correctness_delta: number;
  };
}
