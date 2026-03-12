export interface DashboardMetrics {
  workOrders: number;
  defects: number;
  suppliers: number;
  patternsFound: number;
  defectRate: number;
}

export interface DefectTypeCount {
  defect_type: string;
  defect_count: number;
}

export interface RootCause {
  defect_type: string;
  root_cause_type: string;
  entity_1: string;
  entity_2: string | null;
  correlation_strength: number;
  defect_count: number;
  total_defects_of_type: number;
  is_primary_root_cause: boolean;
}

export interface RiskScore {
  entity_type: string;
  entity_id: string;
  risk_score: number;
  defect_count: number;
  severity_weighted_score: number;
}

export interface SupplierBatchCorrelation {
  supplier_name: string;
  batch_id: string;
  defect_count: number;
  cumulative_defects: number;
  cumulative_pct: number;
}

export interface SupplierDefectHeatmap {
  defect_type: string;
  supplier_name: string;
  defect_count: number;
}

export interface StationCorrelation {
  defect_type: string;
  station_name: string;
  line_id: string;
  defect_count: number;
  expected_defects: number;
  lift_ratio: number;
}

export interface ProcessStepCorrelation {
  defect_type: string;
  step_name: string;
  defect_count: number;
  total_occurrences: number;
  defect_rate: number;
}

export interface SupplierDefectBubble {
  defect_type: string;
  supplier_name: string;
  material_type: string;
  defect_count: number;
}

export interface ParamStats {
  defect_type: string;
  param_name: string;
  mean_defect: number;
  mean_no_defect: number;
  shift_pct: number;
}

export interface PathEdge {
  source: string;
  target: string;
  value: number;
}

export interface ManufacturingFlow {
  nodes: string[];
  links: PathEdge[];
}

export interface NetworkNode {
  id: string;
  label: string;
  type: string;
  risk_score: number;
  defect_count: number;
  x: number;
  y: number;
}

export interface NetworkEdge {
  source: string;
  target: string;
  weight: number;
}

export interface NetworkGraph {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
}

export interface ConnectionStatus {
  connected: boolean;
  error: string | null;
  lastAttempt: string | null;
}

export interface Defect {
  defect_id: string;
  work_order_id: string;
  defect_type: string;
  severity: string;
  detected_at: string;
  station_name: string;
}

export interface WhyChain {
  why1: string;
  why2: string;
  why3: string;
  why4: string;
  why5: string;
  root_cause: string;
}

export interface IshikawaCategory {
  category: string;
  causes: WhyChain[];
}

export interface FiveWhysAnalysis {
  defect_type: string;
  problem_statement: string;
  categories: IshikawaCategory[];
  ai_confidence: number;
}
