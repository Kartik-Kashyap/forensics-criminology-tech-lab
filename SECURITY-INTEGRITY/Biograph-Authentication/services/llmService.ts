// services/llmService.ts
// LLaMA 3.2 Integration via Ollama for Explainability

import { BiometricFeatures, FeatureComparison, SimulationMode } from '../types';

const OLLAMA_BASE_URL = 'http://localhost:11434';
const MODEL_NAME = 'llama3.2'; // Ensure this model is pulled in Ollama

interface OllamaRequest {
  model: string;
  prompt: string;
  stream: boolean;
  options?: {
    temperature?: number;
    max_tokens?: number;
  };
}

interface OllamaResponse {
  response: string;
  done: boolean;
}

/**
 * Generate explainable reasoning using LLaMA 3.2
 * This is NOT making the authentication decision, just explaining it
 */
export async function generateLLMExplanation(
  referenceFeatures: BiometricFeatures,
  attemptFeatures: BiometricFeatures,
  featureComparison: FeatureComparison,
  isSequenceCorrect: boolean,
  simulationMode?: SimulationMode
): Promise<string> {
  
  try {
    const prompt = constructPrompt(
      referenceFeatures,
      attemptFeatures,
      featureComparison,
      isSequenceCorrect,
      simulationMode
    );
    
    const response = await fetch(`${OLLAMA_BASE_URL}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: MODEL_NAME,
        prompt,
        stream: false,
        options: {
          temperature: 0.7,
          max_tokens: 300,
        },
      } as OllamaRequest),
    });
    
    if (!response.ok) {
      throw new Error(`Ollama API error: ${response.statusText}`);
    }
    
    const data = (await response.json()) as OllamaResponse;
    return data.response.trim();
    
  } catch (error) {
    console.error('LLM Explanation Error:', error);
    return generateFallbackExplanation(featureComparison, isSequenceCorrect);
  }
}

/**
 * Construct a detailed prompt for LLaMA
 */
function constructPrompt(
  ref: BiometricFeatures,
  att: BiometricFeatures,
  comparison: FeatureComparison,
  isSequenceCorrect: boolean,
  simulationMode?: SimulationMode
): string {
  
  const contextInfo = simulationMode 
    ? `\nContext: This is a simulated ${simulationMode} attack scenario.`
    : '';
  
  return `You are an expert in behavioral biometrics and authentication security. Analyze the following authentication attempt and explain whether it appears legitimate or anomalous.

REFERENCE PROFILE (Enrolled User):
- Mean Inter-Click Latency: ${ref.meanInterClickLatency.toFixed(2)}ms
- Mean Velocity: ${ref.meanVelocity.toFixed(2)} px/ms
- Path Deviation: ${ref.pathDeviation.toFixed(2)} px
- Click Precision: ${ref.clickPrecision.toFixed(2)} px
- Hesitation Count: ${ref.hesitationCount}
- Velocity Entropy: ${ref.velocityEntropy.toFixed(2)}
- Jitter Score: ${ref.jitterScore.toFixed(2)}

AUTHENTICATION ATTEMPT:
- Mean Inter-Click Latency: ${att.meanInterClickLatency.toFixed(2)}ms
- Mean Velocity: ${att.meanVelocity.toFixed(2)} px/ms
- Path Deviation: ${att.pathDeviation.toFixed(2)} px
- Click Precision: ${att.clickPrecision.toFixed(2)} px
- Hesitation Count: ${att.hesitationCount}
- Velocity Entropy: ${att.velocityEntropy.toFixed(2)}
- Jitter Score: ${att.jitterScore.toFixed(2)}

COMPARISON DELTAS:
- Latency Difference: ${comparison.latencyDelta.toFixed(1)}%
- Velocity Difference: ${comparison.velocityDelta.toFixed(1)}%
- Path Deviation Difference: ${comparison.pathDeviationDelta.toFixed(1)}%
- Precision Difference: ${comparison.precisionDelta.toFixed(1)}%

PASSWORD SEQUENCE: ${isSequenceCorrect ? 'CORRECT' : 'INCORRECT'}${contextInfo}

Provide a concise explanation (2-3 sentences) assessing whether this appears to be:
1. The legitimate enrolled user
2. An attacker who observed the password (shoulder-surfing)
3. An automated bot/script
4. A stressed or distracted legitimate user

Focus on the most distinctive behavioral indicators.`;
}

/**
 * Fallback explanation if LLM is unavailable
 */
function generateFallbackExplanation(
  comparison: FeatureComparison,
  isSequenceCorrect: boolean
): string {
  
  if (!isSequenceCorrect) {
    return 'Password sequence is incorrect. Behavioral analysis not performed for failed authentication attempts.';
  }
  
  const avgDelta = (
    comparison.latencyDelta +
    comparison.velocityDelta +
    comparison.pathDeviationDelta +
    comparison.precisionDelta
  ) / 4;
  
  if (avgDelta < 20) {
    return 'Behavioral patterns closely match the reference profile. Minor variations are within expected bounds for legitimate users.';
  } else if (avgDelta < 50) {
    return 'Moderate behavioral differences detected. Could indicate stress, distraction, or a different user attempting authentication.';
  } else {
    return 'Significant behavioral deviations detected. Timing, velocity, and path characteristics differ substantially from the enrolled profile.';
  }
}

/**
 * Generate human vs bot explanation for CAPTCHA mode
 */
export async function generateCaptchaExplanation(
  features: BiometricFeatures
): Promise<{ isHuman: boolean; confidence: number; reasoning: string }> {
  
  // Bot detection heuristics
  const botIndicators = {
    perfectPrecision: features.clickPrecision < 5, // Too perfect
    constantVelocity: features.stdDevVelocity < 0.1, // No variation
    lowEntropy: features.velocityEntropy < 1.0, // Too predictable
    noJitter: features.jitterScore < 1.0, // Too smooth
    straightPath: features.directnessRatio < 1.1, // Too direct
  };
  
  const botScore = Object.values(botIndicators).filter(Boolean).length;
  const isHuman = botScore < 3; // Need at least 3 bot indicators to flag as bot
  const confidence = Math.abs((botScore / 5) - (isHuman ? 0 : 1)) * 100;
  
  try {
    const prompt = `You are analyzing mouse dynamics to determine if a user is human or a bot.

OBSERVED FEATURES:
- Click Precision: ${features.clickPrecision.toFixed(2)} px (lower = more precise)
- Velocity Std Dev: ${features.stdDevVelocity.toFixed(2)} (higher = more variation)
- Velocity Entropy: ${features.velocityEntropy.toFixed(2)} (higher = more unpredictable)
- Jitter Score: ${features.jitterScore.toFixed(2)} (higher = more natural noise)
- Path Directness: ${features.directnessRatio.toFixed(2)} (>1.0 = curved path)

BOT INDICATORS DETECTED:
${Object.entries(botIndicators)
  .filter(([_, value]) => value)
  .map(([key]) => `- ${key.replace(/([A-Z])/g, ' $1').trim()}`)
  .join('\n') || '- None detected'}

Based on these metrics, is this likely a HUMAN or BOT? Explain in 2 sentences focusing on the most distinctive patterns.`;

    const response = await fetch(`${OLLAMA_BASE_URL}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: MODEL_NAME,
        prompt,
        stream: false,
        options: { temperature: 0.6, max_tokens: 200 },
      }),
    });
    
    if (response.ok) {
      const data = (await response.json()) as OllamaResponse;
      return { isHuman, confidence, reasoning: data.response.trim() };
    }
  } catch (error) {
    console.error('CAPTCHA LLM Error:', error);
  }
  
  // Fallback reasoning
  const reasoning = isHuman
    ? `Natural human patterns detected: irregular timing (entropy ${features.velocityEntropy.toFixed(2)}), curved paths (${features.directnessRatio.toFixed(2)}x direct distance), and natural jitter (${features.jitterScore.toFixed(2)}). These characteristics are inconsistent with automated scripts.`
    : `Bot-like patterns detected: ${Object.entries(botIndicators)
        .filter(([_, v]) => v)
        .map(([k]) => k)
        .join(', ')}. These indicate automated or scripted input.`;
  
  return { isHuman, confidence, reasoning };
}

/**
 * Check if Ollama is running and the model is available
 */
export async function checkLLMAvailability(): Promise<boolean> {
  try {
    const response = await fetch(`${OLLAMA_BASE_URL}/api/tags`);
    if (!response.ok) return false;
    
    const data = await response.json();
    const models = data.models || [];
    return models.some((m: any) => m.name.includes('llama3.2'));
  } catch {
    return false;
  }
}
