// components/ResearchDashboard.tsx
// Research Dashboard: Session Logs & Analytics

import React from 'react';
import { SessionLog } from '../types';

interface ResearchDashboardProps {
  sessions: SessionLog[];
  onBack: () => void;
  onClearData: () => void;
}

const ResearchDashboard: React.FC<ResearchDashboardProps> = ({ sessions, onBack, onClearData }) => {
  
  const stats = {
    total: sessions.length,
    successful: sessions.filter(s => s.success).length,
    failed: sessions.filter(s => !s.success).length,
    captcha: sessions.filter(s => s.mode === 'captcha').length,
    gaming: sessions.filter(s => s.mode === 'gaming').length,
    auth: sessions.filter(s => s.mode === 'authentication').length,
  };
  
  const successRate = stats.total > 0 ? (stats.successful / stats.total * 100).toFixed(1) : '0.0';
  
  // Group by simulation mode
  const bySimulation: Record<string, { total: number; success: number }> = {};
  sessions.forEach(session => {
    if (session.simulationMode) {
      if (!bySimulation[session.simulationMode]) {
        bySimulation[session.simulationMode] = { total: 0, success: 0 };
      }
      bySimulation[session.simulationMode].total++;
      if (session.success) bySimulation[session.simulationMode].success++;
    }
  });
  
  return (
    <div className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white mb-2">Research Dashboard</h1>
          <p className="text-slate-400">Session analytics and experimental data</p>
        </div>
        
        {/* Stats Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatCard label="Total Sessions" value={stats.total} color="indigo" />
          <StatCard label="Successful" value={stats.successful} color="emerald" />
          <StatCard label="Failed" value={stats.failed} color="red" />
          <StatCard label="Success Rate" value={`${successRate}%`} color="cyan" />
        </div>
        
        {/* Mode Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <h3 className="text-sm text-slate-400 uppercase tracking-wider mb-2">Authentication</h3>
            <p className="text-3xl font-bold text-white">{stats.auth}</p>
          </div>
          <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <h3 className="text-sm text-slate-400 uppercase tracking-wider mb-2">CAPTCHA</h3>
            <p className="text-3xl font-bold text-white">{stats.captcha}</p>
          </div>
          <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <h3 className="text-sm text-slate-400 uppercase tracking-wider mb-2">Gaming</h3>
            <p className="text-3xl font-bold text-white">{stats.gaming}</p>
          </div>
        </div>
        
        {/* Attack Mode Analysis */}
        {Object.keys(bySimulation).length > 0 && (
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 mb-6">
            <h2 className="text-xl font-bold text-white mb-4">Attack Simulation Results</h2>
            <div className="space-y-3">
              {Object.entries(bySimulation).map(([mode, data]) => {
                const rate = (data.success / data.total * 100).toFixed(1);
                return (
                  <div key={mode} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-slate-300 font-medium">{mode.replace(/_/g, ' ')}</span>
                      <span className="text-slate-400 text-sm">
                        {data.success}/{data.total} successful
                      </span>
                    </div>
                    <div className="w-full bg-slate-700 h-2 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${parseFloat(rate) > 50 ? 'bg-emerald-500' : 'bg-red-500'}`}
                        style={{ width: `${rate}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">{rate}% detection rate</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}
        
        {/* Session Log Table */}
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-white">Session Log</h2>
            {sessions.length > 0 && (
              <button 
                onClick={onClearData}
                className="px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg text-sm font-medium border border-red-600/30 transition-colors"
              >
                Clear All Data
              </button>
            )}
          </div>
          
          {sessions.length === 0 ? (
            <div className="text-center py-12">
              <svg className="w-16 h-16 text-slate-700 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-slate-500">No sessions recorded yet</p>
              <p className="text-sm text-slate-600 mt-2">Start using the system to see analytics here</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Timestamp</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Mode</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Simulation</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Verdict</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {sessions.slice().reverse().map((session, idx) => (
                    <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                      <td className="py-3 px-4 text-slate-300 font-mono text-xs">
                        {new Date(session.timestamp).toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-slate-400 capitalize">
                        {session.mode}
                      </td>
                      <td className="py-3 px-4 text-slate-400 text-xs">
                        {session.simulationMode ? session.simulationMode.replace(/_/g, ' ') : '—'}
                      </td>
                      <td className="py-3 px-4">
                        {session.result && (
                          <span className={`
                            px-2 py-1 rounded text-xs font-medium
                            ${session.result.aiVerdict === 'LEGITIMATE' ? 'bg-emerald-500/20 text-emerald-400' : ''}
                            ${session.result.aiVerdict === 'ANOMALOUS' ? 'bg-red-500/20 text-red-400' : ''}
                            ${session.result.aiVerdict === 'INCONCLUSIVE' ? 'bg-amber-500/20 text-amber-400' : ''}
                          `}>
                            {session.result.aiVerdict}
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`
                          px-2 py-1 rounded text-xs font-medium
                          ${session.success ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}
                        `}>
                          {session.success ? 'Success' : 'Failed'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
        
        {/* Actions */}
        <div className="flex justify-center">
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

// Stat Card Component
const StatCard: React.FC<{ label: string; value: number | string; color: string }> = ({ label, value, color }) => {
  const colorClasses = {
    indigo: 'from-indigo-500/20 to-indigo-600/20 border-indigo-500/30',
    emerald: 'from-emerald-500/20 to-emerald-600/20 border-emerald-500/30',
    red: 'from-red-500/20 to-red-600/20 border-red-500/30',
    cyan: 'from-cyan-500/20 to-cyan-600/20 border-cyan-500/30',
  };
  
  return (
    <div className={`bg-gradient-to-br ${colorClasses[color as keyof typeof colorClasses]} rounded-xl p-6 border`}>
      <p className="text-sm text-slate-400 uppercase tracking-wider mb-2">{label}</p>
      <p className="text-4xl font-bold text-white">{value}</p>
    </div>
  );
};

export default ResearchDashboard;
