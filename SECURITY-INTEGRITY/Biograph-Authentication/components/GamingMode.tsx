// components/GamingMode.tsx
// Gaming Anti-Bot: Prove You're Human Before Playing

import React, { useState } from 'react';
import AuthCanvas from './AuthCanvas';
import { ClickData, Point } from '../types';
import { extractBiometricFeatures } from '../services/featureExtraction';
import { generateCaptchaExplanation } from '../services/llmService';

interface GamingModeProps {
  onBack: () => void;
}

const GamingMode: React.FC<GamingModeProps> = ({ onBack }) => {
  const [state, setState] = useState<'intro' | 'challenge' | 'analyzing' | 'result'>('intro');
  const [isHuman, setIsHuman] = useState(false);
  const [confidence, setConfidence] = useState(0);
  const [reasoning, setReasoning] = useState('');
  
  const handleComplete = async (clicks: ClickData[], trajectory: Point[], totalTime: number) => {
    setState('analyzing');
    
    const sessionData = {
      sessionId: `gaming-${Date.now()}`,
      gridSize: 4,
      clicks,
      trajectory,
      totalTime,
      imageDimensions: { width: 500, height: 500 },
    };
    
    const features = extractBiometricFeatures(sessionData);
    const result = await generateCaptchaExplanation(features);
    
    setIsHuman(result.isHuman);
    setConfidence(result.confidence);
    setReasoning(result.reasoning);
    setState('result');
  };
  
  const reset = () => {
    setState('intro');
    setIsHuman(false);
    setConfidence(0);
    setReasoning('');
  };
  
  if (state === 'intro') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950">
        <div className="max-w-2xl w-full text-center">
          <div className="mb-8">
            <div className="inline-block p-6 bg-indigo-500/20 rounded-2xl mb-4 border-2 border-indigo-500/30">
              <svg className="w-24 h-24 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h1 className="text-5xl font-extrabold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
              NEXUS ARENA
            </h1>
            <p className="text-slate-400 text-xl mb-2">
              Multiplayer Battle Royale
            </p>
            <div className="flex items-center justify-center gap-2 text-sm text-slate-500">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
              <span>1,247 players online</span>
            </div>
          </div>
          
          <div className="bg-slate-800 rounded-xl p-8 border-2 border-amber-500/30 mb-6">
            <div className="flex items-center justify-center gap-3 mb-4">
              <svg className="w-8 h-8 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <h3 className="text-2xl font-bold text-amber-400">Anti-Bot Verification Required</h3>
            </div>
            <p className="text-slate-300 leading-relaxed mb-6">
              To maintain fair gameplay and prevent cheating, all players must pass our 
              AI-powered behavioral verification. This ensures you're a human player, 
              not a bot or automated script.
            </p>
            
            <div className="grid grid-cols-2 gap-4 mb-6 text-left">
              <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-emerald-400">✓</span>
                  <span className="text-sm font-bold text-white">Protected</span>
                </div>
                <p className="text-xs text-slate-400">Fair matchmaking</p>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-emerald-400">✓</span>
                  <span className="text-sm font-bold text-white">Quick</span>
                </div>
                <p className="text-xs text-slate-400">Takes ~5 seconds</p>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-emerald-400">✓</span>
                  <span className="text-sm font-bold text-white">Private</span>
                </div>
                <p className="text-xs text-slate-400">No data stored</p>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-emerald-400">✓</span>
                  <span className="text-sm font-bold text-white">AI-Powered</span>
                </div>
                <p className="text-xs text-slate-400">99.7% accuracy</p>
              </div>
            </div>
            
            <button 
              onClick={() => setState('challenge')}
              className="px-12 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl font-bold text-lg shadow-2xl shadow-indigo-500/50 transition-all transform hover:scale-105"
            >
              Start Verification
            </button>
          </div>
          
          <button 
            onClick={onBack}
            className="text-slate-500 hover:text-white transition-colors"
          >
            ← Back to Menu
          </button>
        </div>
      </div>
    );
  }
  
  if (state === 'challenge') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950">
        <div className="max-w-2xl w-full text-center mb-8">
          <h2 className="text-3xl font-bold text-white mb-3">Human Verification</h2>
          <p className="text-slate-400 mb-6">
            Click 4 points on the image naturally. Our AI will verify you're human.
          </p>
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-full border border-slate-700">
            <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-slate-400">Analyzing mouse dynamics...</span>
          </div>
        </div>
        
        <AuthCanvas 
          mode="register"
          gridSize={4}
          onComplete={handleComplete}
          imageUrl="/img.jpg"
        />
      </div>
    );
  }
  
  if (state === 'analyzing') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950">
        <div className="relative w-32 h-32 mb-8">
          <div className="absolute inset-0 border-t-4 border-indigo-500 rounded-full animate-spin"></div>
          <div className="absolute inset-4 border-t-4 border-purple-500 rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Analyzing Behavioral Signature</h2>
        <p className="text-slate-400">Verifying human patterns...</p>
      </div>
    );
  }
  
  // Result state
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950">
      <div className="max-w-2xl w-full">
        {isHuman ? (
          // ACCESS GRANTED
          <div className="bg-gradient-to-br from-emerald-900/30 to-slate-800 rounded-2xl p-8 border-2 border-emerald-500/50 shadow-2xl shadow-emerald-500/20">
            <div className="text-center mb-6">
              <div className="inline-block p-6 bg-emerald-500/20 rounded-full mb-4 border-2 border-emerald-500/40">
                <svg className="w-24 h-24 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-4xl font-bold text-emerald-400 mb-2">ACCESS GRANTED</h2>
              <p className="text-xl text-slate-300 mb-4">Verification Successful</p>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/20 rounded-full border border-emerald-500/30">
                <span className="text-emerald-400 font-mono font-bold">{confidence.toFixed(1)}% Confidence</span>
              </div>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-4 mb-6 border border-slate-700/50">
              <p className="text-xs text-slate-400 uppercase tracking-widest mb-2">AI Analysis</p>
              <p className="text-slate-300 italic leading-relaxed">"{reasoning}"</p>
            </div>
            
            <div className="space-y-3 mb-6">
              <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg border border-emerald-500/20">
                <span className="text-slate-400">Natural mouse dynamics</span>
                <span className="text-emerald-400 font-bold">✓ Detected</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg border border-emerald-500/20">
                <span className="text-slate-400">Human timing patterns</span>
                <span className="text-emerald-400 font-bold">✓ Verified</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg border border-emerald-500/20">
                <span className="text-slate-400">Bot indicators</span>
                <span className="text-emerald-400 font-bold">✓ None found</span>
              </div>
            </div>
            
            <div className="flex gap-4">
              <button 
                className="flex-1 px-8 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl font-bold text-lg shadow-2xl shadow-emerald-500/30 transition-all transform hover:scale-105"
              >
                🎮 Enter Game
              </button>
              <button 
                onClick={reset}
                className="px-6 py-4 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-xl font-bold transition-all"
              >
                Reset
              </button>
            </div>
          </div>
        ) : (
          // ACCESS DENIED
          <div className="bg-gradient-to-br from-red-900/30 to-slate-800 rounded-2xl p-8 border-2 border-red-500/50 shadow-2xl shadow-red-500/20">
            <div className="text-center mb-6">
              <div className="inline-block p-6 bg-red-500/20 rounded-full mb-4 border-2 border-red-500/40">
                <svg className="w-24 h-24 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h2 className="text-4xl font-bold text-red-400 mb-2">ACCESS DENIED</h2>
              <p className="text-xl text-slate-300 mb-4">Bot-like Behavior Detected</p>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-red-500/20 rounded-full border border-red-500/30">
                <span className="text-red-400 font-mono font-bold">{confidence.toFixed(1)}% Confidence</span>
              </div>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-4 mb-6 border border-slate-700/50">
              <p className="text-xs text-slate-400 uppercase tracking-widest mb-2">Detection Reason</p>
              <p className="text-slate-300 italic leading-relaxed">"{reasoning}"</p>
            </div>
            
            <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-4 mb-6">
              <p className="text-sm text-amber-300 leading-relaxed">
                <strong>Not a bot?</strong> Try moving your mouse more naturally. Bots typically have 
                perfectly straight paths, constant timing, and inhuman precision.
              </p>
            </div>
            
            <div className="flex gap-4">
              <button 
                onClick={reset}
                className="flex-1 px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-lg shadow-lg transition-all transform hover:scale-105"
              >
                Try Again
              </button>
              <button 
                onClick={onBack}
                className="px-6 py-4 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-xl font-bold transition-all"
              >
                Back
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GamingMode;
