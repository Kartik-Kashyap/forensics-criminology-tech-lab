// services/simulationEngine.ts
// Attack Pattern Simulation Engine

import { SimulationMode, ClickData, Point, AuthSessionData, UserProfile } from '../types';

/**
 * Generate simulated authentication attempts based on attack patterns
 */
export function simulateAuthAttempt(
  userProfile: UserProfile,
  mode: SimulationMode,
  imageDimensions: { width: number; height: number }
): { clicks: ClickData[]; trajectory: Point[]; totalTime: number } {
  
  switch (mode) {
    case SimulationMode.LEGITIMATE:
      return simulateLegitimateUser(userProfile, imageDimensions);
    
    case SimulationMode.SHOULDER_SURFING:
      return simulateShoulderSurfing(userProfile, imageDimensions);
    
    case SimulationMode.BOT_ATTACK:
      return simulateBotAttack(userProfile, imageDimensions);
    
    case SimulationMode.STRESS_MODE:
      return simulateStressMode(userProfile, imageDimensions);
    
    case SimulationMode.RANDOM_GUESS:
      return simulateRandomGuess(userProfile, imageDimensions);
    
    default:
      return simulateLegitimateUser(userProfile, imageDimensions);
  }
}

// ===== SIMULATION MODES =====

/**
 * LEGITIMATE USER
 * Mimics the reference profile with natural variation
 */
function simulateLegitimateUser(
  profile: UserProfile,
  dimensions: { width: number; height: number }
): { clicks: ClickData[]; trajectory: Point[]; totalTime: number } {
  
  const ref = profile.referenceBiometrics;
  const clicks: ClickData[] = [];
  const trajectory: Point[] = [];
  const startTime = Date.now();
  
  // Add natural variation (±10-20%)
  const VARIATION_FACTOR = 0.15;
  
  for (let i = 0; i < ref.clicks.length; i++) {
    const refClick = ref.clicks[i];
    
    // Slightly vary click position (±5 pixels)
    const x = refClick.x + (Math.random() - 0.5) * 10;
    const y = refClick.y + (Math.random() - 0.5) * 10;
    
    // Vary timing (±15%)
    const timingVariation = i === 0 ? 0 : (Math.random() - 0.5) * VARIATION_FACTOR;
    const baseLatency = i === 0 ? 0 : (refClick.t - ref.clicks[i - 1].t);
    const t = startTime + (i === 0 ? 0 : clicks[i - 1].t - startTime + baseLatency * (1 + timingVariation));
    
    clicks.push({
      seqIndex: i,
      gridIndex: refClick.gridIndex,
      x,
      y,
      t,
    });
    
    // Generate trajectory between clicks
    if (i > 0) {
      const prevClick = clicks[i - 1];
      const trajSegment = generateNaturalTrajectory(
        { x: prevClick.x, y: prevClick.y, t: prevClick.t },
        { x, y, t },
        'natural'
      );
      trajectory.push(...trajSegment);
    }
  }
  
  const totalTime = clicks[clicks.length - 1].t - startTime;
  return { clicks, trajectory, totalTime };
}

/**
 * SHOULDER-SURFING ATTACKER
 * Correct sequence, but slower and more deliberate (different behavior)
 */
function simulateShoulderSurfing(
  profile: UserProfile,
  dimensions: { width: number; height: number }
): { clicks: ClickData[]; trajectory: Point[]; totalTime: number } {
  
  const ref = profile.referenceBiometrics;
  const clicks: ClickData[] = [];
  const trajectory: Point[] = [];
  const startTime = Date.now();
  
  // Attacker is 2-3x slower and more hesitant
  const SLOWDOWN_FACTOR = 2.5;
  
  for (let i = 0; i < ref.clicks.length; i++) {
    const refClick = ref.clicks[i];
    
    // More centered clicks (attacker is being careful)
    const gridSize = ref.gridSize;
    const cellWidth = dimensions.width / gridSize;
    const cellHeight = dimensions.height / gridSize;
    const row = Math.floor(refClick.gridIndex / gridSize);
    const col = refClick.gridIndex % gridSize;
    
    const x = col * cellWidth + cellWidth / 2 + (Math.random() - 0.5) * 5;
    const y = row * cellHeight + cellHeight / 2 + (Math.random() - 0.5) * 5;
    
    // Much slower timing
    const baseLatency = i === 0 ? 500 : (refClick.t - ref.clicks[i - 1].t);
    const t = startTime + (i === 0 ? 500 : clicks[i - 1].t - startTime + baseLatency * SLOWDOWN_FACTOR);
    
    clicks.push({
      seqIndex: i,
      gridIndex: refClick.gridIndex,
      x,
      y,
      t,
    });
    
    // Trajectory with hesitations
    if (i > 0) {
      const prevClick = clicks[i - 1];
      const trajSegment = generateNaturalTrajectory(
        { x: prevClick.x, y: prevClick.y, t: prevClick.t },
        { x, y, t },
        'hesitant'
      );
      trajectory.push(...trajSegment);
    }
  }
  
  const totalTime = clicks[clicks.length - 1].t - startTime;
  return { clicks, trajectory, totalTime };
}

/**
 * BOT ATTACK
 * Perfectly straight lines, constant velocity, inhuman precision
 */
function simulateBotAttack(
  profile: UserProfile,
  dimensions: { width: number; height: number }
): { clicks: ClickData[]; trajectory: Point[]; totalTime: number } {
  
  const ref = profile.referenceBiometrics;
  const clicks: ClickData[] = [];
  const trajectory: Point[] = [];
  const startTime = Date.now();
  
  // Bot uses constant timing (300ms between clicks)
  const CONSTANT_LATENCY = 300;
  
  for (let i = 0; i < ref.clicks.length; i++) {
    const refClick = ref.clicks[i];
    
    // Perfect grid center clicks
    const gridSize = ref.gridSize;
    const cellWidth = dimensions.width / gridSize;
    const cellHeight = dimensions.height / gridSize;
    const row = Math.floor(refClick.gridIndex / gridSize);
    const col = refClick.gridIndex % gridSize;
    
    const x = col * cellWidth + cellWidth / 2;
    const y = row * cellHeight + cellHeight / 2;
    const t = startTime + i * CONSTANT_LATENCY;
    
    clicks.push({
      seqIndex: i,
      gridIndex: refClick.gridIndex,
      x,
      y,
      t,
    });
    
    // Perfectly straight trajectory
    if (i > 0) {
      const prevClick = clicks[i - 1];
      const trajSegment = generateNaturalTrajectory(
        { x: prevClick.x, y: prevClick.y, t: prevClick.t },
        { x, y, t },
        'robotic'
      );
      trajectory.push(...trajSegment);
    }
  }
  
  const totalTime = clicks[clicks.length - 1].t - startTime;
  return { clicks, trajectory, totalTime };
}

/**
 * STRESS MODE
 * Correct sequence but with high jitter, delays, and imprecision
 */
function simulateStressMode(
  profile: UserProfile,
  dimensions: { width: number; height: number }
): { clicks: ClickData[]; trajectory: Point[]; totalTime: number } {
  
  const ref = profile.referenceBiometrics;
  const clicks: ClickData[] = [];
  const trajectory: Point[] = [];
  const startTime = Date.now();
  
  // High variance in timing and position
  for (let i = 0; i < ref.clicks.length; i++) {
    const refClick = ref.clicks[i];
    
    // Large position errors (±15 pixels)
    const x = refClick.x + (Math.random() - 0.5) * 30;
    const y = refClick.y + (Math.random() - 0.5) * 30;
    
    // Highly variable timing (0.5x to 3x reference)
    const baseLatency = i === 0 ? 0 : (refClick.t - ref.clicks[i - 1].t);
    const timingFactor = 0.5 + Math.random() * 2.5;
    const t = startTime + (i === 0 ? 0 : clicks[i - 1].t - startTime + baseLatency * timingFactor);
    
    clicks.push({
      seqIndex: i,
      gridIndex: refClick.gridIndex,
      x,
      y,
      t,
    });
    
    // Jittery trajectory
    if (i > 0) {
      const prevClick = clicks[i - 1];
      const trajSegment = generateNaturalTrajectory(
        { x: prevClick.x, y: prevClick.y, t: prevClick.t },
        { x, y, t },
        'jittery'
      );
      trajectory.push(...trajSegment);
    }
  }
  
  const totalTime = clicks[clicks.length - 1].t - startTime;
  return { clicks, trajectory, totalTime };
}

/**
 * RANDOM GUESS
 * Wrong sequence entirely
 */
function simulateRandomGuess(
  profile: UserProfile,
  dimensions: { width: number; height: number }
): { clicks: ClickData[]; trajectory: Point[]; totalTime: number } {
  
  const gridSize = profile.referenceBiometrics.gridSize;
  const clicks: ClickData[] = [];
  const trajectory: Point[] = [];
  const startTime = Date.now();
  
  // Generate 4 random grid indices
  const usedIndices = new Set<number>();
  const cellWidth = dimensions.width / gridSize;
  const cellHeight = dimensions.height / gridSize;
  
  for (let i = 0; i < 4; i++) {
    let gridIndex;
    do {
      gridIndex = Math.floor(Math.random() * (gridSize * gridSize));
    } while (usedIndices.has(gridIndex));
    usedIndices.add(gridIndex);
    
    const row = Math.floor(gridIndex / gridSize);
    const col = gridIndex % gridSize;
    const x = col * cellWidth + cellWidth / 2 + (Math.random() - 0.5) * 20;
    const y = row * cellHeight + cellHeight / 2 + (Math.random() - 0.5) * 20;
    const t = startTime + i * (400 + Math.random() * 200);
    
    clicks.push({
      seqIndex: i,
      gridIndex,
      x,
      y,
      t,
    });
    
    if (i > 0) {
      const prevClick = clicks[i - 1];
      const trajSegment = generateNaturalTrajectory(
        { x: prevClick.x, y: prevClick.y, t: prevClick.t },
        { x, y, t },
        'natural'
      );
      trajectory.push(...trajSegment);
    }
  }
  
  const totalTime = clicks[clicks.length - 1].t - startTime;
  return { clicks, trajectory, totalTime };
}

// ===== TRAJECTORY GENERATION =====

type TrajectoryStyle = 'natural' | 'hesitant' | 'robotic' | 'jittery';

function generateNaturalTrajectory(
  start: Point,
  end: Point,
  style: TrajectoryStyle
): Point[] {
  const trajectory: Point[] = [];
  const duration = end.t - start.t;
  const steps = Math.max(10, Math.floor(duration / 10)); // ~10ms per step
  
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    let x = start.x + (end.x - start.x) * t;
    let y = start.y + (end.y - start.y) * t;
    
    switch (style) {
      case 'natural':
        // Slight curve with noise
        x += Math.sin(t * Math.PI) * (Math.random() - 0.5) * 3;
        y += Math.sin(t * Math.PI) * (Math.random() - 0.5) * 3;
        break;
      
      case 'hesitant':
        // Pauses and slowdowns
        if (Math.random() < 0.1) {
          x += (Math.random() - 0.5) * 2; // Small jitter during pause
          y += (Math.random() - 0.5) * 2;
        }
        break;
      
      case 'robotic':
        // Perfectly straight, no deviation
        break;
      
      case 'jittery':
        // High frequency noise
        x += (Math.random() - 0.5) * 8;
        y += (Math.random() - 0.5) * 8;
        break;
    }
    
    trajectory.push({
      x,
      y,
      t: start.t + (duration * t),
    });
  }
  
  return trajectory;
}

/**
 * Get descriptive information about a simulation mode
 */
export function getSimulationModeInfo(mode: SimulationMode): {
  name: string;
  description: string;
  expectedBehavior: string[];
} {
  const info = {
    [SimulationMode.LEGITIMATE]: {
      name: 'Legitimate User',
      description: 'Natural behavioral variation matching the registered profile',
      expectedBehavior: [
        'Similar timing patterns (±15%)',
        'Natural path curvature',
        'Slight position variance',
        'Consistent velocity profile',
      ],
    },
    [SimulationMode.SHOULDER_SURFING]: {
      name: 'Shoulder-Surfing Attacker',
      description: 'Correct sequence but different behavioral signature',
      expectedBehavior: [
        '2-3x slower execution',
        'More centered, careful clicks',
        'Increased hesitation',
        'Different velocity patterns',
      ],
    },
    [SimulationMode.BOT_ATTACK]: {
      name: 'Bot / Scripted Attack',
      description: 'Automated attack with perfect precision',
      expectedBehavior: [
        'Constant inter-click timing',
        'Perfectly straight trajectories',
        'Zero hesitation',
        'Inhuman precision',
      ],
    },
    [SimulationMode.STRESS_MODE]: {
      name: 'Cognitive Load / Stress',
      description: 'Legitimate user under stress or distraction',
      expectedBehavior: [
        'High timing variance',
        'Imprecise clicking',
        'Jittery trajectories',
        'Irregular velocity',
      ],
    },
    [SimulationMode.RANDOM_GUESS]: {
      name: 'Random Guess Attack',
      description: 'Incorrect password sequence',
      expectedBehavior: [
        'Wrong grid indices',
        'No behavioral correlation',
        'Random timing',
        'Unpredictable path',
      ],
    },
  };
  
  return info[mode];
}
