// components/BiometricAnalysis.tsx

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter, Cell } from 'recharts';
import { AuthSessionData, AnalysisResult } from '../types';

interface BiometricAnalysisProps {
  reference: AuthSessionData;
  attempt: AuthSessionData;
  result: AnalysisResult;
  onReset: () => void;
}

const BiometricAnalysis: React.FC<BiometricAnalysisProps> = ({ reference, attempt, result, onReset }) => {
  
  // Transform trajectory data for velocity chart
  // We need to calculate velocity between points
  const calculateVelocityData = (data: AuthSessionData, name: string) => {
    const processed = [];
    const points = data.trajectory.filter((_, i) => i % 5 === 0); // Downsample for chart performance
    
    for (let i = 1; i < points.length; i++) {
        const p1 = points[i-1];
        const p2 = points[i];
        const dist = Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
        const timeDiff = p2.t - p1.t;
        const velocity = timeDiff > 0 ? dist / timeDiff : 0;
        
        // Relative time from start
        const time = p2.t - data.trajectory[0].t;
        
        processed.push({
            time,
            velocity,
            type: name
        });
    }
    return processed;
  };

  const refVelocity = calculateVelocityData(reference, 'Reference');
  const attemptVelocity = calculateVelocityData(attempt, 'Attempt');
  
  // Combine for velocity chart? Or just show Attempt and overlay avg?
  // Let's just show Attempt Velocity Profile for simplicity of the chart
  const velocityData = [
      ...refVelocity.map(d => ({ ...d, velocityRef: d.velocity, velocityAttempt: null })),
      ...attemptVelocity.map(d => ({ ...d, velocityRef: null, velocityAttempt: d.velocity }))
  ].sort((a, b) => a.time - b.time);

  // Click Timing Data
  const clickTimingData = reference.clicks.map((refClick, i) => {
    const attemptClick = attempt.clicks[i];
    return {
        step: `Click ${i + 1}`,
        referenceTime: i === 0 ? 0 : refClick.t - reference.clicks[i-1].t,
        attemptTime: i === 0 ? 0 : (attemptClick ? attemptClick.t - attempt.clicks[i-1].t : 0)
    };
  });

  const getVerdictColor = (verdict: string) => {
      switch(verdict) {
          case 'LEGITIMATE': return 'text-emerald-400';
          case 'ANOMALOUS': return 'text-red-500';
          default: return 'text-amber-400';
      }
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6 bg-slate-900 min-h-screen text-slate-100">
      
      {/* Header Result Section */}
      <div className="mb-8 p-6 bg-slate-800 rounded-xl border border-slate-700 shadow-lg">
        <h2 className="text-2xl font-bold mb-4 border-b border-slate-700 pb-2">Authentication Analysis Report</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-slate-900/50 p-4 rounded-lg">
                <p className="text-xs text-slate-400 uppercase tracking-widest font-mono">Password Sequence</p>
                <p className={`text-2xl font-bold mt-2 ${result.isSequenceCorrect ? 'text-emerald-400' : 'text-red-500'}`}>
                    {result.isSequenceCorrect ? 'MATCH' : 'MISMATCH'}
                </p>
            </div>
            <div className="bg-slate-900/50 p-4 rounded-lg">
                <p className="text-xs text-slate-400 uppercase tracking-widest font-mono">AI Verdict</p>
                <p className={`text-2xl font-bold mt-2 ${getVerdictColor(result.aiVerdict)}`}>
                    {result.aiVerdict}
                </p>
            </div>
            <div className="bg-slate-900/50 p-4 rounded-lg">
                <p className="text-xs text-slate-400 uppercase tracking-widest font-mono">Confidence Score</p>
                <div className="flex items-center mt-2">
                    <div className="w-full bg-slate-700 h-4 rounded-full mr-3 overflow-hidden">
                        <div 
                            className={`h-full ${result.biometricScore > 80 ? 'bg-emerald-500' : result.biometricScore > 50 ? 'bg-amber-500' : 'bg-red-500'}`} 
                            style={{ width: `${result.biometricScore}%` }}
                        ></div>
                    </div>
                    <span className="font-mono font-bold">{result.biometricScore}%</span>
                </div>
            </div>
        </div>

        <div className="mt-6 bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
            <p className="text-xs text-slate-400 uppercase tracking-widest font-mono mb-2">AI Reasoning</p>
            <p className="text-slate-300 italic leading-relaxed">"{result.reasoning}"</p>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          
          {/* Velocity Profile */}
          <div className="bg-slate-800 p-4 rounded-xl shadow-md border border-slate-700">
            <h3 className="text-lg font-semibold mb-4 text-slate-300">Mouse Velocity Profile</h3>
            <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={velocityData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                        <XAxis dataKey="time" type="number" hide domain={['dataMin', 'dataMax']} />
                        <YAxis stroke="#94a3b8" fontSize={12} />
                        <Tooltip 
                            contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', color: '#f1f5f9' }}
                            labelStyle={{ color: '#94a3b8' }}
                        />
                        <Line type="monotone" dataKey="velocityRef" stroke="#10b981" strokeWidth={2} dot={false} name="Reference" connectNulls />
                        <Line type="monotone" dataKey="velocityAttempt" stroke="#f43f5e" strokeWidth={2} dot={false} name="Attempt" connectNulls />
                    </LineChart>
                </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-6 mt-2 text-sm">
                <span className="text-emerald-400 flex items-center"><span className="w-3 h-3 bg-emerald-500 mr-2 rounded-full"></span> Reference</span>
                <span className="text-rose-500 flex items-center"><span className="w-3 h-3 bg-rose-500 mr-2 rounded-full"></span> Attempt</span>
            </div>
          </div>

          {/* Timing Comparison */}
          <div className="bg-slate-800 p-4 rounded-xl shadow-md border border-slate-700">
            <h3 className="text-lg font-semibold mb-4 text-slate-300">Inter-Click Latency (ms)</h3>
             <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                        <XAxis dataKey="step" type="category" stroke="#94a3b8" />
                        <YAxis type="number" dataKey="attemptTime" name="Time" unit="ms" stroke="#94a3b8" />
                        <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569' }} />
                        <Scatter name="Reference" data={clickTimingData} fill="#10b981" line shape="circle" />
                        <Scatter name="Attempt" data={clickTimingData} fill="#f43f5e" line shape="cross" />
                    </ScatterChart>
                </ResponsiveContainer>
            </div>
            <p className="text-center text-xs text-slate-500 mt-2">Comparison of time taken between clicks</p>
          </div>
      </div>

        {/* Action */}
      <div className="flex justify-center">
        <button 
            onClick={onReset}
            className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-bold shadow-lg shadow-indigo-500/20 transition-all transform hover:scale-105"
        >
            Start New Session
        </button>
      </div>

    </div>
  );
};

export default BiometricAnalysis;