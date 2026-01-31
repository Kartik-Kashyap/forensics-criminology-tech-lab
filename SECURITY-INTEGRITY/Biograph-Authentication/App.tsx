// App.tsx - Main Application with Enhanced Features

import React, { useState, useEffect } from 'react';
import AuthCanvas from './components/AuthCanvas';
import BiometricAnalysis from './components/BiometricAnalysis';
import SimulationControl from './components/SimulationControl';
import FeatureExtractor from './components/FeatureExtractor';
import CaptchaMode from './components/CaptchaMode';
import GamingMode from './components/GamingMode';
import ResearchDashboard from './components/ResearchDashboard';
import { 
  AppState, 
  UserProfile, 
  AuthSessionData, 
  AnalysisResult, 
  ClickData, 
  Point, 
  SimulationMode,
  SessionLog,
  BiometricFeatures,
} from './types';
import { extractBiometricFeatures, compareFeatures } from './services/featureExtraction';
import { generateLLMExplanation, checkLLMAvailability } from './services/llmService';
import { simulateAuthAttempt } from './services/simulationEngine';

const AUTH_IMAGE_URL = "/img.jpg";
const GRID_SIZE = 4;

const App: React.FC = () => {
  const [appState, setAppState] = useState<AppState>(AppState.LANDING);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [currentAttempt, setCurrentAttempt] = useState<AuthSessionData | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [simulationMode, setSimulationMode] = useState<SimulationMode>(SimulationMode.LEGITIMATE);
  const [useSimulation, setUseSimulation] = useState(false);
  const [llmAvailable, setLlmAvailable] = useState(false);
  const [sessionLogs, setSessionLogs] = useState<SessionLog[]>([]);
  
  // Check LLM availability on mount
  useEffect(() => {
    checkLLMAvailability().then(setLlmAvailable);
  }, []);
  
  // Load session logs from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('biograph_sessions');
    if (stored) {
      try {
        setSessionLogs(JSON.parse(stored));
      } catch (e) {
        console.error('Failed to load sessions:', e);
      }
    }
  }, []);
  
  // Save session logs to localStorage
  useEffect(() => {
    if (sessionLogs.length > 0) {
      localStorage.setItem('biograph_sessions', JSON.stringify(sessionLogs));
    }
  }, [sessionLogs]);
  
  // ===== REGISTRATION =====
  const handleRegistrationComplete = (clicks: ClickData[], trajectory: Point[], totalTime: number) => {
    const sequence = clicks.map(c => c.gridIndex);
    
    const sessionData: AuthSessionData = {
      sessionId: `reg-${Date.now()}`,
      gridSize: GRID_SIZE,
      clicks,
      trajectory,
      totalTime,
      imageDimensions: { width: 500, height: 500 },
    };
    
    const features = extractBiometricFeatures(sessionData);
    
    const profile: UserProfile = {
      username: "DemoUser",
      passwordSequence: sequence,
      referenceBiometrics: sessionData,
      referenceFeatures: features,
    };

    setUserProfile(profile);
    
    // Log registration
    setSessionLogs(prev => [...prev, {
      timestamp: Date.now(),
      sessionId: sessionData.sessionId,
      mode: 'registration',
      success: true,
    }]);
    
    setAppState(AppState.LOGIN);
  };

  // ===== LOGIN (REAL OR SIMULATED) =====
  const handleLoginComplete = async (clicks: ClickData[], trajectory: Point[], totalTime: number) => {
    if (!userProfile) return;
    setAppState(AppState.ANALYZING);

    let attemptSession: AuthSessionData;
    
    if (useSimulation) {
      // Use simulation engine
      const simulated = simulateAuthAttempt(userProfile, simulationMode, { width: 500, height: 500 });
      attemptSession = {
        sessionId: `auth-${Date.now()}`,
        gridSize: GRID_SIZE,
        clicks: simulated.clicks,
        trajectory: simulated.trajectory,
        totalTime: simulated.totalTime,
        imageDimensions: { width: 500, height: 500 },
        simulationMode,
      };
    } else {
      // Real user input
      attemptSession = {
        sessionId: `auth-${Date.now()}`,
        gridSize: GRID_SIZE,
        clicks,
        trajectory,
        totalTime,
        imageDimensions: { width: 500, height: 500 },
      };
    }

    setCurrentAttempt(attemptSession);

    // Extract features
    const attemptFeatures = extractBiometricFeatures(attemptSession);
    const featureComparison = compareFeatures(userProfile.referenceFeatures, attemptFeatures);
    
    // Check password sequence
    const attemptSequence = attemptSession.clicks.map(c => c.gridIndex);
    const isSequenceCorrect = 
      attemptSequence.length === userProfile.passwordSequence.length &&
      attemptSequence.every((val, index) => val === userProfile.passwordSequence[index]);

    // AI Analysis with deterministic + biometric scoring
    const result = await analyzeBehavioralBiometrics(
      userProfile.referenceFeatures,
      attemptFeatures,
      featureComparison,
      isSequenceCorrect,
      attemptSession.simulationMode
    );

    setAnalysisResult(result);
    
    // Log session
    setSessionLogs(prev => [...prev, {
      timestamp: Date.now(),
      sessionId: attemptSession.sessionId,
      mode: 'authentication',
      simulationMode: attemptSession.simulationMode,
      result,
      success: result.aiVerdict === 'LEGITIMATE' && isSequenceCorrect,
    }]);
    
    setAppState(AppState.RESULT);
  };

  // ===== ANALYSIS LOGIC =====
  const analyzeBehavioralBiometrics = async (
    refFeatures: BiometricFeatures,
    attFeatures: BiometricFeatures,
    comparison: any,
    isSequenceCorrect: boolean,
    simMode?: SimulationMode
  ): Promise<AnalysisResult> => {
    
    // If password is wrong, immediately reject
    if (!isSequenceCorrect) {
      return {
        isSequenceCorrect: false,
        biometricScore: 0,
        aiVerdict: 'ANOMALOUS',
        reasoning: 'Password sequence is incorrect.',
        threatLevel: 'HIGH',
        extractedFeatures: attFeatures,
        featureComparison: comparison,
        confidenceFactors: {
          timingMatch: 0,
          pathMatch: 0,
          precisionMatch: 0,
          overall: 0,
        },
      };
    }
    
    // Calculate biometric similarity score
    const timingMatch = 100 - Math.min(comparison.latencyDelta, 100);
    const velocityMatch = 100 - Math.min(comparison.velocityDelta, 100);
    const pathMatch = 100 - Math.min(comparison.pathDeviationDelta, 100);
    const precisionMatch = 100 - Math.min(comparison.precisionDelta, 100);
    
    const biometricScore = (timingMatch + velocityMatch + pathMatch + precisionMatch) / 4;
    
    // Determine verdict
    let aiVerdict: 'LEGITIMATE' | 'ANOMALOUS' | 'INCONCLUSIVE';
    let threatLevel: 'LOW' | 'MEDIUM' | 'HIGH';
    
    if (biometricScore >= 70) {
      aiVerdict = 'LEGITIMATE';
      threatLevel = 'LOW';
    } else if (biometricScore >= 40) {
      aiVerdict = 'INCONCLUSIVE';
      threatLevel = 'MEDIUM';
    } else {
      aiVerdict = 'ANOMALOUS';
      threatLevel = 'HIGH';
    }
    
    // Get LLM explanation (if available)
    let llmExplanation: string | undefined;
    if (llmAvailable) {
      try {
        llmExplanation = await generateLLMExplanation(
          refFeatures,
          attFeatures,
          comparison,
          isSequenceCorrect,
          simMode
        );
      } catch (e) {
        console.error('LLM explanation failed:', e);
      }
    }
    
    const reasoning = llmExplanation || generateFallbackReasoning(biometricScore, comparison);
    
    return {
      isSequenceCorrect,
      biometricScore,
      aiVerdict,
      reasoning,
      threatLevel,
      extractedFeatures: attFeatures,
      featureComparison: comparison,
      llmExplanation,
      confidenceFactors: {
        timingMatch,
        pathMatch: velocityMatch,
        precisionMatch,
        overall: biometricScore,
      },
    };
  };

  const generateFallbackReasoning = (score: number, comparison: any): string => {
    if (score >= 70) {
      return `Behavioral patterns closely match the reference profile (${score.toFixed(1)}% similarity). Timing, velocity, and path characteristics are within expected bounds.`;
    } else if (score >= 40) {
      return `Moderate behavioral differences detected (${score.toFixed(1)}% similarity). Could indicate stress, distraction, or a different user with similar patterns.`;
    } else {
      return `Significant behavioral deviations detected (${score.toFixed(1)}% similarity). Timing variance: ${comparison.latencyDelta.toFixed(1)}%, Path deviation: ${comparison.pathDeviationDelta.toFixed(1)}%. Likely attacker or bot.`;
    }
  };

  const resetApp = () => {
    setAppState(AppState.LANDING);
    setUserProfile(null);
    setCurrentAttempt(null);
    setAnalysisResult(null);
    setUseSimulation(false);
  };

  const retryLogin = () => {
    setAppState(AppState.LOGIN);
    setCurrentAttempt(null);
    setAnalysisResult(null);
  };

  const clearSessionData = () => {
    setSessionLogs([]);
    localStorage.removeItem('biograph_sessions');
  };

  // ===== RENDER =====

  const renderLanding = () => (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 text-center max-w-4xl mx-auto">
      <div className="mb-6 p-4 bg-indigo-500/10 rounded-full">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-indigo-400">
          <rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>
          <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
        </svg>
      </div>
      <h1 className="text-5xl font-extrabold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400">
        BioGraph Auth
      </h1>
      <p className="text-slate-400 text-lg mb-2 leading-relaxed max-w-2xl">
        AI-Enhanced Graphical Authentication with Behavioral Biometrics
      </p>
      <p className="text-sm text-slate-500 mb-8 max-w-xl">
        Research-grade system combining graphical passwords with mouse dynamics analysis. 
        Powered by feature extraction + {llmAvailable ? 'LLaMA 3.2 LLM' : 'ML reasoning'}.
      </p>
      
      {!llmAvailable && (
        <div className="mb-6 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg max-w-md">
          <p className="text-xs text-amber-300">
            ⚠️ LLaMA not detected. Using fallback reasoning. Run <code className="bg-slate-900 px-1 rounded">ollama pull llama3.2</code> for full AI explanations.
          </p>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full mb-6">
        <button 
          onClick={() => setAppState(AppState.REGISTER)}
          className="group relative p-6 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl transition-all hover:scale-[1.02]"
        >
          <h3 className="text-xl font-bold text-white mb-2">🔐 Register Profile</h3>
          <p className="text-sm text-slate-400">Create graphical password and establish baseline biometric profile</p>
        </button>
        
        <button 
          disabled={!userProfile}
          onClick={() => setAppState(AppState.LOGIN)}
          className={`group relative p-6 border rounded-xl transition-all ${userProfile ? 'bg-slate-800 hover:bg-slate-700 border-slate-700 hover:scale-[1.02] cursor-pointer' : 'bg-slate-900 border-slate-800 opacity-50 cursor-not-allowed'}`}
        >
          <h3 className="text-xl font-bold text-white mb-2">🔓 Authenticate</h3>
          <p className="text-sm text-slate-400">Test authentication with behavioral analysis</p>
          {!userProfile && <span className="text-xs text-red-400 mt-2 block">(Register first)</span>}
        </button>
        
        <button 
          onClick={() => setAppState(AppState.CAPTCHA)}
          className="group relative p-6 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl transition-all hover:scale-[1.02]"
        >
          <h3 className="text-xl font-bold text-white mb-2">🤖 CAPTCHA Mode</h3>
          <p className="text-sm text-slate-400">Human vs Bot detection challenge</p>
        </button>
        
        <button 
          onClick={() => setAppState(AppState.GAMING)}
          className="group relative p-6 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl transition-all hover:scale-[1.02]"
        >
          <h3 className="text-xl font-bold text-white mb-2">🎮 Gaming Mode</h3>
          <p className="text-sm text-slate-400">Anti-bot verification for games</p>
        </button>
      </div>
      
      <button 
        onClick={() => setAppState(AppState.RESEARCH_DASHBOARD)}
        className="px-6 py-3 bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 rounded-lg font-bold transition-all"
      >
        📊 Research Dashboard ({sessionLogs.length} sessions)
      </button>
    </div>
  );

  const renderRegister = () => (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <h2 className="text-2xl font-bold text-emerald-400 mb-2">Registration Phase</h2>
      <p className="text-slate-400 mb-6 text-center max-w-md">
        Select 4 points on the image to create your graphical password
        <br/><span className="text-xs opacity-75">Mouse dynamics are being recorded</span>
      </p>
      <AuthCanvas 
        mode="register" 
        gridSize={GRID_SIZE} 
        onComplete={handleRegistrationComplete}
        imageUrl={AUTH_IMAGE_URL} 
      />
      <button onClick={() => setAppState(AppState.LANDING)} className="mt-8 text-slate-500 hover:text-white transition-colors">
        Cancel
      </button>
    </div>
  );

  const renderLogin = () => (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <h2 className="text-2xl font-bold text-indigo-400 mb-2">Authentication Phase</h2>
      <p className="text-slate-400 mb-4 text-center max-w-md">
        Re-enter your graphical password
        <br/><span className="text-xs opacity-75">Behavioral biometrics will be analyzed</span>
      </p>
      
      {/* Simulation Toggle */}
      <div className="mb-6">
        <label className="flex items-center gap-2 cursor-pointer">
          <input 
            type="checkbox" 
            checked={useSimulation} 
            onChange={(e) => setUseSimulation(e.target.checked)}
            className="w-4 h-4 rounded bg-slate-700 border-slate-600"
          />
          <span className="text-sm text-slate-400">Use Simulated Attack (skip manual input)</span>
        </label>
      </div>
      
      {useSimulation ? (
        <div className="mb-6">
          <SimulationControl 
            currentMode={simulationMode}
            onModeChange={setSimulationMode}
          />
          <div className="mt-6 flex justify-center">
            <button 
              onClick={() => handleLoginComplete([], [], 0)}
              className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-bold shadow-lg transition-all transform hover:scale-105"
            >
              Run Simulation
            </button>
          </div>
        </div>
      ) : (
        <AuthCanvas 
          mode="login" 
          gridSize={GRID_SIZE} 
          onComplete={handleLoginComplete}
          imageUrl={AUTH_IMAGE_URL} 
        />
      )}
      
      <button onClick={() => setAppState(AppState.LANDING)} className="mt-8 text-slate-500 hover:text-white transition-colors">
        Cancel
      </button>
    </div>
  );

  const renderAnalyzing = () => (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-900">
      <div className="relative w-24 h-24 mb-8">
        <div className="absolute inset-0 border-t-4 border-indigo-500 rounded-full animate-spin"></div>
        <div className="absolute inset-2 border-t-4 border-emerald-500 rounded-full animate-spin reverse-spin opacity-70" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
      </div>
      <h2 className="text-2xl font-bold text-white mb-2">Analyzing Biometrics</h2>
      <p className="text-slate-400">Extracting features and comparing patterns...</p>
    </div>
  );

  return (
    <div className="bg-slate-950 min-h-screen text-slate-200 selection:bg-indigo-500 selection:text-white">
      {appState === AppState.LANDING && renderLanding()}
      {appState === AppState.REGISTER && renderRegister()}
      {appState === AppState.LOGIN && renderLogin()}
      {appState === AppState.ANALYZING && renderAnalyzing()}
      
      {appState === AppState.RESULT && userProfile && currentAttempt && analysisResult && (
        <div className="p-6">
          <BiometricAnalysis 
            reference={userProfile.referenceBiometrics} 
            attempt={currentAttempt} 
            result={analysisResult}
            onReset={retryLogin}
          />
          
          {/* Feature Extraction Details */}
          <div className="max-w-6xl mx-auto mt-6">
            <FeatureExtractor 
              referenceFeatures={userProfile.referenceFeatures}
              attemptFeatures={analysisResult.extractedFeatures}
              comparison={analysisResult.featureComparison}
            />
          </div>
          
          <div className="flex justify-center mt-6 gap-4">
            <button 
              onClick={retryLogin}
              className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-bold shadow-lg transition-all"
            >
              Try Again
            </button>
            <button 
              onClick={resetApp}
              className="px-8 py-3 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg font-bold transition-all"
            >
              Back to Menu
            </button>
          </div>
        </div>
      )}
      
      {appState === AppState.CAPTCHA && (
        <CaptchaMode onBack={() => setAppState(AppState.LANDING)} />
      )}
      
      {appState === AppState.GAMING && (
        <GamingMode onBack={() => setAppState(AppState.LANDING)} />
      )}
      
      {appState === AppState.RESEARCH_DASHBOARD && (
        <ResearchDashboard 
          sessions={sessionLogs}
          onBack={() => setAppState(AppState.LANDING)}
          onClearData={clearSessionData}
        />
      )}
    </div>
  );
};

export default App;
