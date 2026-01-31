// types.ts - Enhanced Type Definitions

// ===== CORE DATA STRUCTURES =====

export interface Point {
  x: number;
  y: number;
  t: number; // Timestamp
}

export interface ClickData {
  seqIndex: number;
  gridIndex: number;
  x: number;
  y: number;
  t: number;
  pressure?: number;
}

export interface AuthSessionData {
  sessionId: string;
  gridSize: number;
  clicks: ClickData[];
  trajectory: Point[];
  totalTime: number;
  imageDimensions: { width: number; height: number };
  simulationMode?: SimulationMode; // NEW
}

// ===== BIOMETRIC FEATURES =====

export interface BiometricFeatures {
  // Timing Features
  meanInterClickLatency: number;
  stdDevInterClickLatency: number;
  latencyEntropy: number;
  
  // Trajectory Features
  pathDeviation: number; // Straightness vs curvature
  meanVelocity: number;
  stdDevVelocity: number;
  velocityEntropy: number;
  
  // Precision Features
  clickPrecision: number; // Distance from grid center
  hesitationCount: number; // Pauses near clicks
  hesitationTotalTime: number;
  
  // Path Complexity
  pathLength: number;
  directnessRatio: number; // Actual path / theoretical straight path
  curvatureIndex: number;
  
  // Advanced Metrics
  accelerationVariance: number;
  angularVelocityMean: number;
  jitterScore: number; // High-frequency noise in path
}

// ===== SIMULATION MODES =====

export enum SimulationMode {
  LEGITIMATE = 'LEGITIMATE',
  SHOULDER_SURFING = 'SHOULDER_SURFING', // Correct seq, wrong behavior
  BOT_ATTACK = 'BOT_ATTACK', // Perfect timing, straight lines
  STRESS_MODE = 'STRESS_MODE', // Delayed, jittery
  RANDOM_GUESS = 'RANDOM_GUESS', // Wrong sequence
}

export interface SimulationConfig {
  mode: SimulationMode;
  velocityFactor: number; // 0.5 = half speed, 2.0 = double speed
  jitterAmount: number; // Pixel deviation
  hesitationProbability: number; // 0-1
  straightnessBoost: number; // For bot mode
}

// ===== ANALYSIS RESULTS =====

export interface AnalysisResult {
  isSequenceCorrect: boolean;
  biometricScore: number; // 0-100
  aiVerdict: 'LEGITIMATE' | 'ANOMALOUS' | 'INCONCLUSIVE';
  reasoning: string;
  threatLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  
  // NEW: Detailed breakdown
  extractedFeatures: BiometricFeatures;
  featureComparison: FeatureComparison;
  llmExplanation?: string; // From LLaMA
  confidenceFactors: {
    timingMatch: number;
    pathMatch: number;
    precisionMatch: number;
    overall: number;
  };
}

export interface FeatureComparison {
  latencyDelta: number; // % difference
  velocityDelta: number;
  pathDeviationDelta: number;
  precisionDelta: number;
}

// ===== APP STATE =====

export enum AppState {
  LANDING = 'LANDING',
  REGISTER = 'REGISTER',
  LOGIN = 'LOGIN',
  ANALYZING = 'ANALYZING',
  RESULT = 'RESULT',
  CAPTCHA = 'CAPTCHA', // NEW
  GAMING = 'GAMING', // NEW
  RESEARCH_DASHBOARD = 'RESEARCH_DASHBOARD', // NEW
}

export interface UserProfile {
  username: string;
  passwordSequence: number[];
  referenceBiometrics: AuthSessionData;
  referenceFeatures: BiometricFeatures; // NEW
}

// ===== SESSION LOGGING =====

export interface SessionLog {
  timestamp: number;
  sessionId: string;
  mode: 'registration' | 'authentication' | 'captcha' | 'gaming';
  simulationMode?: SimulationMode;
  result?: AnalysisResult;
  success: boolean;
}

// ===== CAPTCHA MODE =====

export interface CaptchaChallenge {
  challengeId: string;
  instructions: string;
  requiredClicks: number;
  imageUrl: string;
}

export interface CaptchaResult {
  isHuman: boolean;
  confidence: number;
  reasoning: string;
  detectedPatterns: string[];
}

// ===== GAMING MODE =====

export interface GamingChallenge {
  challengeType: 'pattern_trace' | 'rapid_click' | 'precision_test';
  difficulty: 'easy' | 'medium' | 'hard';
  targetPattern?: number[];
  timeLimit?: number;
}
