
export enum EvidenceType {
  IMAGE = 'IMAGE',
  VIDEO = 'VIDEO',
  AUDIO = 'AUDIO',
  DOCUMENT = 'DOCUMENT',
  TEXT = 'TEXT'
}

export enum ConfidenceLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  VERIFIED = 'VERIFIED'
}

export interface Evidence {
  id: string;
  name: string;
  type: EvidenceType;
  timestamp: string;
  description: string;
  hash: string;
  metadata: Record<string, string | number>;
  source: string;
  confidence: ConfidenceLevel;
  tags: string[];
}

export interface TimelineEvent {
  id: string;
  title: string;
  description: string;
  startTime: string;
  endTime?: string;
  linkedEvidenceIds: string[];
  location?: string;
  participants: string[];
}

export interface Case {
  id: string;
  caseNumber: string;
  title: string;
  summary: string;
  leadInvestigator: string;
  status: 'OPEN' | 'CLOSED' | 'ARCHIVED';
  createdAt: string;
  evidence: Evidence[];
  events: TimelineEvent[];
}

export interface BiasAlert {
  type: 'CONFIRMATION' | 'AVAILABILITY' | 'REASONING_GAP' | 'OVERRELIANCE';
  title: string;
  description: string;
  severity: 'WARNING' | 'CRITICAL';
  suggestedAction: string;
}

export interface AIReasoningLog {
  step: number;
  thought: string;
  supportingEvidence: string[];
  alternatives: string[];
}
