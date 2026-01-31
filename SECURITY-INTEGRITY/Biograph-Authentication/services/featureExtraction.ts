// services/featureExtraction.ts
// Biometric Feature Extraction Module

import { AuthSessionData, BiometricFeatures, ClickData, Point } from '../types';

/**
 * Extract comprehensive behavioral biometric features from session data
 */
export function extractBiometricFeatures(session: AuthSessionData): BiometricFeatures {
  const { clicks, trajectory } = session;
  
  // ===== TIMING FEATURES =====
  const interClickLatencies = calculateInterClickLatencies(clicks);
  const meanInterClickLatency = mean(interClickLatencies);
  const stdDevInterClickLatency = stdDev(interClickLatencies);
  const latencyEntropy = calculateEntropy(interClickLatencies);
  
  // ===== TRAJECTORY FEATURES =====
  const velocities = calculateVelocities(trajectory);
  const meanVelocity = mean(velocities);
  const stdDevVelocity = stdDev(velocities);
  const velocityEntropy = calculateEntropy(velocities);
  
  // ===== PATH ANALYSIS =====
  const pathLength = calculatePathLength(trajectory);
  const directPath = calculateDirectPath(clicks);
  const directnessRatio = directPath > 0 ? pathLength / directPath : 1;
  const pathDeviation = calculatePathDeviation(trajectory, clicks);
  const curvatureIndex = calculateCurvature(trajectory);
  
  // ===== PRECISION FEATURES =====
  const clickPrecision = calculateClickPrecision(clicks, session.gridSize, session.imageDimensions);
  const { count: hesitationCount, totalTime: hesitationTotalTime } = detectHesitations(trajectory, clicks);
  
  // ===== ADVANCED METRICS =====
  const accelerations = calculateAccelerations(trajectory);
  const accelerationVariance = variance(accelerations);
  const angularVelocities = calculateAngularVelocities(trajectory);
  const angularVelocityMean = mean(angularVelocities);
  const jitterScore = calculateJitter(trajectory);
  
  return {
    meanInterClickLatency,
    stdDevInterClickLatency,
    latencyEntropy,
    pathDeviation,
    meanVelocity,
    stdDevVelocity,
    velocityEntropy,
    clickPrecision,
    hesitationCount,
    hesitationTotalTime,
    pathLength,
    directnessRatio,
    curvatureIndex,
    accelerationVariance,
    angularVelocityMean,
    jitterScore,
  };
}

// ===== HELPER FUNCTIONS =====

function calculateInterClickLatencies(clicks: ClickData[]): number[] {
  const latencies: number[] = [];
  for (let i = 1; i < clicks.length; i++) {
    latencies.push(clicks[i].t - clicks[i - 1].t);
  }
  return latencies;
}

function calculateVelocities(trajectory: Point[]): number[] {
  const velocities: number[] = [];
  for (let i = 1; i < trajectory.length; i++) {
    const p1 = trajectory[i - 1];
    const p2 = trajectory[i];
    const dist = Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
    const timeDiff = p2.t - p1.t;
    const velocity = timeDiff > 0 ? dist / timeDiff : 0;
    velocities.push(velocity);
  }
  return velocities;
}

function calculateAccelerations(trajectory: Point[]): number[] {
  const velocities = calculateVelocities(trajectory);
  const accelerations: number[] = [];
  for (let i = 1; i < velocities.length; i++) {
    const timeDiff = trajectory[i + 1].t - trajectory[i].t;
    const accel = timeDiff > 0 ? (velocities[i] - velocities[i - 1]) / timeDiff : 0;
    accelerations.push(Math.abs(accel));
  }
  return accelerations;
}

function calculateAngularVelocities(trajectory: Point[]): number[] {
  const angles: number[] = [];
  for (let i = 1; i < trajectory.length - 1; i++) {
    const p1 = trajectory[i - 1];
    const p2 = trajectory[i];
    const p3 = trajectory[i + 1];
    
    const angle1 = Math.atan2(p2.y - p1.y, p2.x - p1.x);
    const angle2 = Math.atan2(p3.y - p2.y, p3.x - p2.x);
    let angleDiff = angle2 - angle1;
    
    // Normalize to [-π, π]
    while (angleDiff > Math.PI) angleDiff -= 2 * Math.PI;
    while (angleDiff < -Math.PI) angleDiff += 2 * Math.PI;
    
    const timeDiff = p3.t - p1.t;
    const angularVel = timeDiff > 0 ? Math.abs(angleDiff) / timeDiff : 0;
    angles.push(angularVel);
  }
  return angles;
}

function calculatePathLength(trajectory: Point[]): number {
  let length = 0;
  for (let i = 1; i < trajectory.length; i++) {
    const p1 = trajectory[i - 1];
    const p2 = trajectory[i];
    length += Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
  }
  return length;
}

function calculateDirectPath(clicks: ClickData[]): number {
  let length = 0;
  for (let i = 1; i < clicks.length; i++) {
    const c1 = clicks[i - 1];
    const c2 = clicks[i];
    length += Math.sqrt(Math.pow(c2.x - c1.x, 2) + Math.pow(c2.y - c1.y, 2));
  }
  return length;
}

function calculatePathDeviation(trajectory: Point[], clicks: ClickData[]): number {
  // Measure how much the path deviates from straight lines between clicks
  let totalDeviation = 0;
  let clickIndex = 0;
  
  for (let i = 0; i < trajectory.length; i++) {
    if (clickIndex < clicks.length - 1) {
      const nextClick = clicks[clickIndex + 1];
      if (trajectory[i].t >= nextClick.t) {
        clickIndex++;
        continue;
      }
      
      const currentClick = clicks[clickIndex];
      const deviation = pointToLineDistance(
        trajectory[i],
        currentClick,
        nextClick
      );
      totalDeviation += deviation;
    }
  }
  
  return trajectory.length > 0 ? totalDeviation / trajectory.length : 0;
}

function pointToLineDistance(point: Point, lineStart: ClickData, lineEnd: ClickData): number {
  const A = point.x - lineStart.x;
  const B = point.y - lineStart.y;
  const C = lineEnd.x - lineStart.x;
  const D = lineEnd.y - lineStart.y;
  
  const dot = A * C + B * D;
  const lenSq = C * C + D * D;
  
  if (lenSq === 0) return Math.sqrt(A * A + B * B);
  
  const param = dot / lenSq;
  
  let xx, yy;
  if (param < 0) {
    xx = lineStart.x;
    yy = lineStart.y;
  } else if (param > 1) {
    xx = lineEnd.x;
    yy = lineEnd.y;
  } else {
    xx = lineStart.x + param * C;
    yy = lineStart.y + param * D;
  }
  
  const dx = point.x - xx;
  const dy = point.y - yy;
  return Math.sqrt(dx * dx + dy * dy);
}

function calculateCurvature(trajectory: Point[]): number {
  // Average curvature based on angle changes
  let totalCurvature = 0;
  for (let i = 1; i < trajectory.length - 1; i++) {
    const p1 = trajectory[i - 1];
    const p2 = trajectory[i];
    const p3 = trajectory[i + 1];
    
    const angle1 = Math.atan2(p2.y - p1.y, p2.x - p1.x);
    const angle2 = Math.atan2(p3.y - p2.y, p3.x - p2.x);
    let angleDiff = Math.abs(angle2 - angle1);
    
    if (angleDiff > Math.PI) angleDiff = 2 * Math.PI - angleDiff;
    totalCurvature += angleDiff;
  }
  
  return trajectory.length > 2 ? totalCurvature / (trajectory.length - 2) : 0;
}

function calculateClickPrecision(clicks: ClickData[], gridSize: number, dimensions: { width: number; height: number }): number {
  // Calculate average distance from grid cell centers
  const cellWidth = dimensions.width / gridSize;
  const cellHeight = dimensions.height / gridSize;
  
  let totalDistance = 0;
  for (const click of clicks) {
    const row = Math.floor(click.gridIndex / gridSize);
    const col = click.gridIndex % gridSize;
    
    const centerX = col * cellWidth + cellWidth / 2;
    const centerY = row * cellHeight + cellHeight / 2;
    
    const distance = Math.sqrt(
      Math.pow(click.x - centerX, 2) + Math.pow(click.y - centerY, 2)
    );
    totalDistance += distance;
  }
  
  return clicks.length > 0 ? totalDistance / clicks.length : 0;
}

function detectHesitations(trajectory: Point[], clicks: ClickData[]): { count: number; totalTime: number } {
  // Detect pauses (low velocity zones) near click events
  const VELOCITY_THRESHOLD = 0.1; // Very low velocity = hesitation
  const PROXIMITY_THRESHOLD = 50; // Pixels near click
  
  let hesitationCount = 0;
  let totalTime = 0;
  let inHesitation = false;
  let hesitationStart = 0;
  
  for (let i = 1; i < trajectory.length; i++) {
    const p1 = trajectory[i - 1];
    const p2 = trajectory[i];
    
    const dist = Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
    const timeDiff = p2.t - p1.t;
    const velocity = timeDiff > 0 ? dist / timeDiff : 0;
    
    // Check if near any click
    const nearClick = clicks.some(click => {
      const clickDist = Math.sqrt(Math.pow(p2.x - click.x, 2) + Math.pow(p2.y - click.y, 2));
      return clickDist < PROXIMITY_THRESHOLD;
    });
    
    if (velocity < VELOCITY_THRESHOLD && nearClick) {
      if (!inHesitation) {
        inHesitation = true;
        hesitationStart = p2.t;
        hesitationCount++;
      }
    } else if (inHesitation) {
      totalTime += p2.t - hesitationStart;
      inHesitation = false;
    }
  }
  
  return { count: hesitationCount, totalTime };
}

function calculateJitter(trajectory: Point[]): number {
  // High-frequency noise in trajectory (small rapid changes)
  if (trajectory.length < 3) return 0;
  
  let jitter = 0;
  for (let i = 1; i < trajectory.length - 1; i++) {
    const p1 = trajectory[i - 1];
    const p2 = trajectory[i];
    const p3 = trajectory[i + 1];
    
    // Second derivative approximation
    const dx = (p3.x - p2.x) - (p2.x - p1.x);
    const dy = (p3.y - p2.y) - (p2.y - p1.y);
    jitter += Math.sqrt(dx * dx + dy * dy);
  }
  
  return trajectory.length > 2 ? jitter / (trajectory.length - 2) : 0;
}

// ===== STATISTICAL UTILITIES =====

function mean(arr: number[]): number {
  if (arr.length === 0) return 0;
  return arr.reduce((a, b) => a + b, 0) / arr.length;
}

function variance(arr: number[]): number {
  if (arr.length === 0) return 0;
  const m = mean(arr);
  return arr.reduce((sum, val) => sum + Math.pow(val - m, 2), 0) / arr.length;
}

function stdDev(arr: number[]): number {
  return Math.sqrt(variance(arr));
}

function calculateEntropy(arr: number[]): number {
  if (arr.length === 0) return 0;
  
  // Discretize values into bins
  const bins = 10;
  const min = Math.min(...arr);
  const max = Math.max(...arr);
  const binSize = (max - min) / bins;
  
  if (binSize === 0) return 0;
  
  const counts = new Array(bins).fill(0);
  for (const val of arr) {
    const binIndex = Math.min(Math.floor((val - min) / binSize), bins - 1);
    counts[binIndex]++;
  }
  
  let entropy = 0;
  for (const count of counts) {
    if (count > 0) {
      const p = count / arr.length;
      entropy -= p * Math.log2(p);
    }
  }
  
  return entropy;
}

/**
 * Compare two feature sets and calculate deltas
 */
export function compareFeatures(reference: BiometricFeatures, attempt: BiometricFeatures) {
  const calcDelta = (ref: number, att: number) => {
    if (ref === 0) return att === 0 ? 0 : 100;
    return Math.abs((att - ref) / ref) * 100;
  };
  
  return {
    latencyDelta: calcDelta(reference.meanInterClickLatency, attempt.meanInterClickLatency),
    velocityDelta: calcDelta(reference.meanVelocity, attempt.meanVelocity),
    pathDeviationDelta: calcDelta(reference.pathDeviation, attempt.pathDeviation),
    precisionDelta: calcDelta(reference.clickPrecision, attempt.clickPrecision),
  };
}
