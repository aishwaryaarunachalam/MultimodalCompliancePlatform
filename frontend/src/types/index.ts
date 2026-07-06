// ── Enums ─────────────────────────────────────────────────────────────────────
export type FileType      = 'pdf' | 'image' | 'video';
export type DocumentStatus = 'uploaded' | 'processing' | 'completed' | 'failed';
export type RiskLevel     = 'none' | 'low' | 'medium' | 'high' | 'critical';
export type FindingType   = 'pii' | 'policy_violation';
export type Severity      = 'low' | 'medium' | 'high' | 'critical';
export type FindingStatus = 'pending' | 'approved' | 'dismissed' | 'escalated' | 'redacted';
export type ReviewDecision = 'approve' | 'dismiss' | 'escalate' | 'redact';
export type RuleType      = 'keyword' | 'regex' | 'semantic';

// ── Document ──────────────────────────────────────────────────────────────────
export interface Document {
  id: string;
  filename: string;
  original_name: string;
  file_type: FileType;
  mime_type?: string;
  file_size_bytes?: number;
  storage_url?: string;
  page_count?: number;
  status: DocumentStatus;
  risk_level: RiskLevel;
  pii_count: number;
  violation_count: number;
  error_msg?: string;
  uploaded_at: string;
  processed_at?: string;
}

export interface DocumentPage {
  id: string;
  document_id: string;
  page_num: number;
  image_url?: string;
  extracted_text?: string;
  ocr_confidence?: number;
  ocr_engine?: string;
  created_at: string;
}

export interface DocumentStatus {
  document_id: string;
  status: DocumentStatus;
  job_status?: string;
  total_pages?: number;
  processed_pages?: number;
  risk_level: RiskLevel;
  pii_count: number;
  violation_count: number;
}

// ── Finding ───────────────────────────────────────────────────────────────────
export interface Finding {
  id: string;
  document_id: string;
  page_id?: string;
  finding_type: FindingType;
  category: string;
  severity: Severity;
  confidence?: number;
  evidence_text?: string;
  explanation?: string;
  bounding_box?: { x: number; y: number; w: number; h: number };
  status: FindingStatus;
  created_at: string;
}

// ── Review ────────────────────────────────────────────────────────────────────
export interface Review {
  id: string;
  finding_id: string;
  document_id: string;
  reviewer_id: string;
  decision: ReviewDecision;
  notes?: string;
  reviewed_at: string;
}

// ── Policy ────────────────────────────────────────────────────────────────────
export interface PolicyRule {
  type: RuleType;
  value: string;
  severity: Severity;
  description?: string;
}

export interface Policy {
  id: string;
  name: string;
  description?: string;
  rules: PolicyRule[];
  is_active: boolean;
  created_at: string;
}

// ── Analytics ─────────────────────────────────────────────────────────────────
export interface DashboardStats {
  period_days: number;
  total_documents: number;
  total_pii: number;
  total_violations: number;
  severity_breakdown: Record<string, number>;
  top_pii_categories: Array<{ category: string; count: number }>;
}
