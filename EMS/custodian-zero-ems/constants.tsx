import { Case, Evidence, IntegrityStatus, EvidenceType, UserRole, User, AuditLogEntry } from './types';

// --- USERS & RBAC ---

export const USERS: Record<string, User> = {
  INVESTIGATOR: {
    id: 'USR-7734-X',
    name: 'Det. R. Deckard',
    role: UserRole.INVESTIGATOR,
    badgeNumber: 'LAPD-2019',
    permissions: ['create_case', 'upload_evidence', 'view_evidence', 'run_ai']
  },
  ADMIN: {
    id: 'ADM-0001-Z',
    name: 'Cmdr. Adama',
    role: UserRole.ADMIN,
    badgeNumber: 'FLEET-01',
    permissions: ['all']
  },
  ANALYST: {
    id: 'ANA-9921-Q',
    name: 'Tech. K. Joi',
    role: UserRole.FORENSIC_ANALYST,
    badgeNumber: 'LAB-99',
    permissions: ['view_evidence', 'create_version', 'run_ai']
  },
  VIEWER: {
    id: 'VWR-1122-B',
    name: 'DA. H. Dent',
    role: UserRole.VIEWER,
    badgeNumber: 'DA-NY',
    permissions: ['view_evidence', 'view_case']
  }
};

export const CURRENT_USER = USERS.INVESTIGATOR; // Default start

// --- CASES ---

export const MOCK_CASES: Case[] = [
  {
    id: 'CASE-2024-089',
    title: 'Operation Blackout: Server Breach',
    description: 'Investigation into unauthorized root access of critical infrastructure servers.',
    investigator: 'Det. R. Deckard',
    status: 'OPEN',
    evidenceCount: 14,
    createdDate: '2024-05-15T08:00:00Z',
    lastUpdate: '2024-05-21T08:45:00Z',
    priority: 'HIGH'
  },
  {
    id: 'CASE-2024-102',
    title: 'Unauthorized Drone Surveillance',
    description: 'Recovery of drone footage near restricted airspace sector 7G.',
    investigator: 'Det. S. Connor',
    status: 'PENDING_REVIEW',
    evidenceCount: 3,
    createdDate: '2024-05-18T12:00:00Z',
    lastUpdate: '2024-05-20T14:30:00Z',
    priority: 'MEDIUM'
  }
];

// --- EVIDENCE (WITH VERSIONING) ---

export const MOCK_EVIDENCE: Evidence[] = [
  {
    id: 'EVD-9921-A',
    caseId: 'CASE-2024-089',
    name: 'server_access_logs_raw.log',
    type: EvidenceType.DIGITAL,
    fileType: 'text/plain',
    size: 450921, 
    uploadTimestamp: '2024-05-19T09:00:00Z',
    uploader: 'Ofc. K. Joi',
    hashSha256: 'a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890',
    hashSha3: '1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
    integrityStatus: IntegrityStatus.VERIFIED,
    encryptionKeyId: 'KEY-X12-99',
    version: 1,
    isLatest: true,
    tags: ['logs', 'access-control', 'critical'],
    custodyChain: [
      {
        id: 'LOG-001',
        timestamp: '2024-05-19T09:00:00Z',
        actor: 'Ofc. K. Joi',
        action: 'INTAKE',
        reason: 'Initial seizure from /var/log',
        previousHash: '00000000000000000000000000000000',
        newHash: 'a1b2c3d4...',
        signature: 'SIG-RSA-4096-JOI'
      }
    ]
  },
  {
    id: 'EVD-9921-B',
    caseId: 'CASE-2024-089',
    name: 'cctv_server_room_cam4.mp4',
    type: EvidenceType.DIGITAL,
    fileType: 'video/mp4',
    size: 204857600, 
    uploadTimestamp: '2024-05-19T09:30:00Z',
    uploader: 'Ofc. K. Joi',
    hashSha256: 'fffeeeeddddccccbbbbaaaa0000111122223333444455556666777788889999',
    hashSha3: 'aaaabbbbccccddddeeeeffff0000111122223333444455556666777788889999',
    integrityStatus: IntegrityStatus.TAMPERED,
    encryptionKeyId: 'KEY-X12-99',
    version: 1,
    isLatest: false,
    tags: ['video', 'surveillance', 'original'],
    custodyChain: [
      {
        id: 'LOG-003',
        timestamp: '2024-05-19T09:30:00Z',
        actor: 'Ofc. K. Joi',
        action: 'INTAKE',
        reason: 'Initial seizure',
        previousHash: '00000000...',
        newHash: 'fffeeeed...',
        signature: 'SIG-RSA-4096-JOI'
      }
    ]
  },
  {
    id: 'EVD-9921-B-V2',
    caseId: 'CASE-2024-089',
    name: 'cctv_server_room_cam4_ENHANCED.mp4',
    type: EvidenceType.DIGITAL,
    fileType: 'video/mp4',
    size: 404857600, 
    uploadTimestamp: '2024-05-20T10:30:00Z',
    uploader: 'Tech. K. Joi',
    hashSha256: '1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff',
    hashSha3: '222233334444555566667777888899990000aaaabbbbccccddddeeeeffff1111',
    integrityStatus: IntegrityStatus.VERIFIED,
    encryptionKeyId: 'KEY-X12-99-V2',
    version: 2,
    parentId: 'EVD-9921-B',
    isLatest: true,
    tags: ['video', 'enhanced', 'ai-processed'],
    custodyChain: [
      {
        id: 'LOG-005',
        timestamp: '2024-05-20T10:30:00Z',
        actor: 'Tech. K. Joi',
        action: 'VERSION_CREATE',
        reason: 'Applied AI upscaling filter',
        previousHash: 'fffeeeed...',
        newHash: '11112222...',
        signature: 'SIG-RSA-4096-JOI'
      }
    ]
  }
];

// --- AUDIT LOGS ---

export const MOCK_AUDIT_LOGS: AuditLogEntry[] = [
  {
    id: 'AUD-5501',
    timestamp: '2024-05-21T10:45:12Z',
    userId: 'USR-7734-X',
    userRole: UserRole.INVESTIGATOR,
    action: 'LOGIN_SUCCESS',
    resourceId: 'SYSTEM',
    ipAddress: '192.168.1.42',
    status: 'SUCCESS',
    hash: '0x99aabbcc...'
  },
  {
    id: 'AUD-5502',
    timestamp: '2024-05-21T10:48:00Z',
    userId: 'USR-7734-X',
    userRole: UserRole.INVESTIGATOR,
    action: 'VIEW_EVIDENCE',
    resourceId: 'EVD-9921-A',
    ipAddress: '192.168.1.42',
    status: 'SUCCESS',
    hash: '0x11223344...'
  },
  {
    id: 'AUD-5503',
    timestamp: '2024-05-21T11:00:05Z',
    userId: 'EXT-UNKNOWN',
    userRole: UserRole.VIEWER,
    action: 'DELETE_ATTEMPT',
    resourceId: 'EVD-9921-B',
    ipAddress: '10.0.0.99',
    status: 'DENIED',
    hash: '0xffffffff...'
  },
  {
    id: 'AUD-5504',
    timestamp: '2024-05-21T11:15:00Z',
    userId: 'ANA-9921-Q',
    userRole: UserRole.FORENSIC_ANALYST,
    action: 'RUN_AI_MODEL',
    resourceId: 'EVD-9921-B',
    ipAddress: '192.168.1.105',
    status: 'SUCCESS',
    hash: '0xaa00aa00...'
  }
];
