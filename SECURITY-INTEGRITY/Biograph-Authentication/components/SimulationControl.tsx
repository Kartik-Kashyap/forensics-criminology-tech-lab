// components/SimulationControl.tsx
// Attack Mode Selection Interface

import React from 'react';
import { SimulationMode } from '../types';
import { getSimulationModeInfo } from '../services/simulationEngine';

interface SimulationControlProps {
  currentMode: SimulationMode;
  onModeChange: (mode: SimulationMode) => void;
  disabled?: boolean;
}

const SimulationControl: React.FC<SimulationControlProps> = ({ 
  currentMode, 
  onModeChange,
  disabled = false 
}) => {
  
  const modes = [
    SimulationMode.LEGITIMATE,
    SimulationMode.SHOULDER_SURFING,
    SimulationMode.BOT_ATTACK,
    SimulationMode.STRESS_MODE,
    SimulationMode.RANDOM_GUESS,
  ];
  
  const getIcon = (mode: SimulationMode) => {
    switch (mode) {
      case SimulationMode.LEGITIMATE:
        return '👤';
      case SimulationMode.SHOULDER_SURFING:
        return '👀';
      case SimulationMode.BOT_ATTACK:
        return '🤖';
      case SimulationMode.STRESS_MODE:
        return '😰';
      case SimulationMode.RANDOM_GUESS:
        return '🎲';
    }
  };
  
  const getColor = (mode: SimulationMode) => {
    switch (mode) {
      case SimulationMode.LEGITIMATE:
        return 'emerald';
      case SimulationMode.SHOULDER_SURFING:
        return 'amber';
      case SimulationMode.BOT_ATTACK:
        return 'red';
      case SimulationMode.STRESS_MODE:
        return 'orange';
      case SimulationMode.RANDOM_GUESS:
        return 'purple';
    }
  };
  
  return (
    <div className="w-full max-w-4xl mx-auto bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">
      <div className="mb-4">
        <h3 className="text-xl font-bold text-white mb-1">Attack Simulation Mode</h3>
        <p className="text-sm text-slate-400">
          Test the system's ability to detect different attack patterns
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {modes.map((mode) => {
          const info = getSimulationModeInfo(mode);
          const color = getColor(mode);
          const isActive = currentMode === mode;
          
          return (
            <button
              key={mode}
              onClick={() => onModeChange(mode)}
              disabled={disabled}
              className={`
                relative p-4 rounded-lg border-2 text-left transition-all
                ${isActive 
                  ? `border-${color}-500 bg-${color}-500/10` 
                  : 'border-slate-700 bg-slate-900 hover:border-slate-600'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:scale-[1.02] cursor-pointer'}
              `}
            >
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl">{getIcon(mode)}</span>
                <div className="flex-1">
                  <h4 className="font-bold text-white text-sm">{info.name}</h4>
                </div>
                {isActive && (
                  <span className={`text-${color}-400 text-xl`}>●</span>
                )}
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                {info.description}
              </p>
            </button>
          );
        })}
      </div>
      
      {/* Selected Mode Details */}
      <div className="mt-6 p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
        <h4 className="text-sm font-mono text-slate-400 uppercase tracking-wider mb-2">
          Expected Behavioral Patterns
        </h4>
        <ul className="space-y-1">
          {getSimulationModeInfo(currentMode).expectedBehavior.map((behavior, idx) => (
            <li key={idx} className="text-sm text-slate-300 flex items-start gap-2">
              <span className="text-emerald-400 mt-0.5">▸</span>
              <span>{behavior}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default SimulationControl;
