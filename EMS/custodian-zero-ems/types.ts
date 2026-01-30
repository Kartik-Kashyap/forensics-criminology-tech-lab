export enum UserRole {
  ADMIN = 'ADMIN',
  INVESTIGATOR = 'INVESTIGATOR',
  FORENSIC_ANALYST = 'FORENSIC_ANALYST',
  VIEWER = 'VIEWER'
}

export enum EvidenceType {
  DIGITAL = 'DIGITAL',
  PHYSICAL = 'PHYSICAL',
  MIXED = 'MIXED'
}

export enum IntegrityStatus {
  VERIFIED = 'VERIFIED',
  TAMPERED = 'TAMPERED',
  PENDING = 'PENDING',
  UNKNOWN = 'UNKNOWN'
}

export interface User {
  id: string;
  name: string;
  role: UserRole;
  badgeNumber: string;
  permissions: string[];
}

export interface CustodyEvent {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  reason: string;
  previousHash: string; // Simulating blockchain linkage
  newHash: string;
  signature: string;
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  userId: string;
  userRole: UserRole;
  action: string;
  resourceId: string;
  ipAddress: string;
  status: 'SUCCESS' | 'FAILURE' | 'DENIED';
  hash: string;
}

export interface AIAnalysis {
  id: string;
  evidenceId: string;
  model: string; // e.g., "LLaMA 3.2-Local"
  generatedAt: string;
  summary: string;
  anomalies: string[];
  confidenceScore: number;
  isAdvisory: boolean; // MUST always be true
}

export interface Evidence {
  id: string;
  caseId: string;
  name: string;
  type: EvidenceType;
  fileType: string;
  size: number;
  uploadTimestamp: string;
  uploader: string;
  hashSha256: string;
  hashSha3: string;
  integrityStatus: IntegrityStatus;
  encryptionKeyId: string;
  custodyChain: CustodyEvent[];
  aiAnalysis?: AIAnalysis;
  tags: string[];
  version: number;
  parentId?: string; // For versioning (e.g. enhanced video from original)
  isLatest: boolean;
}

export interface Case {
  id: string;
  title: string;
  description: string;
  investigator: string;
  status: 'OPEN' | 'CLOSED' | 'ARCHIVED' | 'PENDING_REVIEW';
  evidenceCount: number;
  createdDate: string;
  lastUpdate: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
}
