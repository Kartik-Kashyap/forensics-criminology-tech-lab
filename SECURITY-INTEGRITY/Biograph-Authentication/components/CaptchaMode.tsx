// components/CaptchaMode.tsx
// Behavioral CAPTCHA: Human vs Bot Detection

import React, { useState } from 'react';
import AuthCanvas from './AuthCanvas';
import { ClickData, Point, BiometricFeatures } from '../types';
import { extractBiometricFeatures } from '../services/featureExtraction';
import { generateCaptchaExplanation } from '../services/llmService';

interface CaptchaResult {
  isHuman: boolean;
  confidence: number;
  reasoning: string;
  features: BiometricFeatures;
}

interface CaptchaModeProps {
  onBack: () => void;
}

const CaptchaMode: React.FC<CaptchaModeProps> = ({ onBack }) => {
  const [state, setState] = useState<'challenge' | 'analyzing' | 'result'>('challenge');
  const [result, setResult] = useState<CaptchaResult | null>(null);
  
  const handleComplete = async (clicks: ClickData[], trajectory: Point[], totalTime: number) => {
    setState('analyzing');
    
    // Extract features from the CAPTCHA attempt
    const sessionData = {
      sessionId: `captcha-${Date.now()}`,
      gridSize: 4,
      clicks,
      trajectory,
      totalTime,
      imageDimensions: { width: 500, height: 500 },
    };
    
    const features = extractBiometricFeatures(sessionData);
    
    // Get AI verdict
    const { isHuman, confidence, reasoning } = await generateCaptchaExplanation(features);
    
    setResult({ isHuman, confidence, reasoning, features });
    setState('result');
  };
  
  const reset = () => {
    setState('challenge');
    setResult(null);
  };
  
  if (state === 'challenge') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-slate-950">
        <div className="max-w-2xl w-full text-center mb-8">
          <div className="inline-block p-4 bg-indigo-500/10 rounded-full mb-4">
            <svg className="w-16 h-16 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-white mb-3">Behavioral CAPTCHA</h2>
          <p className="text-slate-400 text-lg mb-2">
            Prove you're human through natural mouse dynamics
          </p>
          <p className="text-sm text-slate-500 max-w-lg mx-auto">
            Click 4 points on the image below. Our AI will analyze your timing, velocity, 
            and path characteristics to determine if you're human or a bot.
          </p>
        </div>
        
        <AuthCanvas 
          mode="register"
          gridSize={4}
          onComplete={handleComplete}
          imageUrl="/img.jpg"
        />
        
        <button 
          onClick={onBack}
          className="mt-8 px-6 py-2 text-slate-400 hover:text-white transition-colors"
        >
          ← Back to Menu
        </button>
      </div>
    );
  }
  
  if (state === 'analyzing') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950">
        <div className="relative w-24 h-24 mb-8">
          <div className="absolute inset-0 border-t-4 border-indigo-500 rounded-full animate-spin"></div>
          <div className="absolute inset-2 border-t-4 border-emerald-500 rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Analyzing Behavioral Patterns</h2>
        <p className="text-slate-400">Computing biometric features...</p>
      </div>
    );
  }
  
  // Result state
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-slate-950">
      <div className="max-w-3xl w-full">
        
        {/* Main Result Card */}
        <div className="bg-slate-800 rounded-2xl p-8 border-2 border-slate-700 shadow-2xl mb-6">
          <div className="text-center mb-6">
            <div className={`inline-block p-6 rounded-full mb-4 ${result?.isHuman ? 'bg-emerald-500/20' : 'bg-red-500/20'}`}>
              {result?.isHuman ? (
                <svg className="w-20 h-20 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-20 h-20 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
            </div>
            
            <h2 className={`text-4xl font-bold mb-2 ${result?.isHuman ? 'text-emerald-400' : 'text-red-400'}`}>
              {result?.isHuman ? 'HUMAN DETECTED' : 'BOT DETECTED'}
            </h2>
            
            <div className="flex items-center justify-center gap-2 mb-4">
              <span className="text-slate-400">Confidence:</span>
              <span className="text-2xl font-bold text-white font-mono">{result?.confidence.toFixed(1)}%</span>
            </div>
            
            <div className="w-full bg-slate-700 h-3 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-1000 ${result?.isHuman ? 'bg-emerald-500' : 'bg-red-500'}`}
                style={{ width: `${result?.confidence}%` }}
              ></div>
            </div>
          </div>
          
          {/* AI Reasoning */}
          <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50">
            <p className="text-xs text-slate-400 uppercase tracking-widest font-mono mb-2">
              AI Analysis
            </p>
            <p className="text-slate-300 leading-relaxed italic">
              "{result?.reasoning}"
            </p>
          </div>
        </div>
        
        {/* Feature Breakdown */}
        {result && (
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 mb-6">
            <h3 className="text-lg font-bold text-white mb-4">Behavioral Indicators</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <FeatureCard 
                label="Velocity Entropy"
                value={result.features.velocityEntropy.toFixed(2)}
                interpretation={result.features.velocityEntropy > 2.0 ? 'Natural' : 'Suspicious'}
                isGood={result.features.velocityEntropy > 2.0}
              />
              <FeatureCard 
                label="Jitter Score"
                value={result.features.jitterScore.toFixed(2)}
                interpretation={result.features.jitterScore > 2.0 ? 'Human-like' : 'Too Smooth'}
                isGood={result.features.jitterScore > 2.0}
              />
              <FeatureCard 
                label="Path Directness"
                value={result.features.directnessRatio.toFixed(2)}
                interpretation={result.features.directnessRatio > 1.15 ? 'Curved' : 'Too Straight'}
                isGood={result.features.directnessRatio > 1.15}
              />
              <FeatureCard 
                label="Click Precision"
                value={`${result.features.clickPrecision.toFixed(1)}px`}
                interpretation={result.features.clickPrecision > 8 ? 'Natural' : 'Too Perfect'}
                isGood={result.features.clickPrecision > 8}
              />
              <FeatureCard 
                label="Velocity StdDev"
                value={result.features.stdDevVelocity.toFixed(2)}
                interpretation={result.features.stdDevVelocity > 0.15 ? 'Variable' : 'Constant'}
                isGood={result.features.stdDevVelocity > 0.15}
              />
              <FeatureCard 
                label="Hesitations"
                value={result.features.hesitationCount.toString()}
                interpretation={result.features.hesitationCount > 0 ? 'Present' : 'None'}
                isGood={result.features.hesitationCount > 0}
              />
            </div>
          </div>
        )}
        
        {/* Actions */}
        <div className="flex justify-center gap-4">
          <button 
            onClick={reset}
            className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-bold shadow-lg transition-all transform hover:scale-105"
          >
            Try Again
          </button>
          <button 
            onClick={onBack}
            className="px-8 py-3 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg font-bold transition-all"
          >
            Back to Menu
          </button>
        </div>
      </div>
    </div>
  );
};

// Feature Card Component
const FeatureCard: React.FC<{ label: string; value: string; interpretation: string; isGood: boolean }> = ({
  label, value, interpretation, isGood
}) => (
  <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50">
    <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">{label}</p>
    <p className="text-xl font-bold text-white font-mono mb-1">{value}</p>
    <p className={`text-xs font-medium ${isGood ? 'text-emerald-400' : 'text-amber-400'}`}>
      {interpretation}
    </p>
  </div>
);

export default CaptchaMode;
