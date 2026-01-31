// components/FeatureExtractor.tsx
// Detailed Biometric Feature Display

import React from 'react';
import { BiometricFeatures, FeatureComparison } from '../types';

interface FeatureExtractorProps {
  referenceFeatures: BiometricFeatures;
  attemptFeatures: BiometricFeatures;
  comparison: FeatureComparison;
}

const FeatureExtractor: React.FC<FeatureExtractorProps> = ({ 
  referenceFeatures, 
  attemptFeatures, 
  comparison 
}) => {
  
  const renderFeatureRow = (
    label: string,
    refValue: number,
    attValue: number,
    delta: number,
    unit: string = ''
  ) => {
    const getDeltaColor = (delta: number) => {
      if (delta < 15) return 'text-emerald-400';
      if (delta < 35) return 'text-amber-400';
      return 'text-red-400';
    };
    
    return (
      <div className="grid grid-cols-4 gap-4 py-3 border-b border-slate-700/50 hover:bg-slate-800/30 transition-colors">
        <div className="text-sm text-slate-300 font-medium">{label}</div>
        <div className="text-sm text-slate-400 font-mono text-right">
          {refValue.toFixed(2)}{unit}
        </div>
        <div className="text-sm text-slate-400 font-mono text-right">
          {attValue.toFixed(2)}{unit}
        </div>
        <div className={`text-sm font-mono text-right font-bold ${getDeltaColor(delta)}`}>
          {delta.toFixed(1)}%
        </div>
      </div>
    );
  };
  
  return (
    <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-md">
      <div className="mb-4">
        <h3 className="text-xl font-bold text-white mb-1">Extracted Biometric Features</h3>
        <p className="text-sm text-slate-400">
          Quantitative comparison of behavioral patterns
        </p>
      </div>
      
      {/* Header */}
      <div className="grid grid-cols-4 gap-4 pb-3 border-b-2 border-slate-600 mb-2">
        <div className="text-xs text-slate-500 uppercase tracking-wider font-bold">Feature</div>
        <div className="text-xs text-slate-500 uppercase tracking-wider font-bold text-right">Reference</div>
        <div className="text-xs text-slate-500 uppercase tracking-wider font-bold text-right">Attempt</div>
        <div className="text-xs text-slate-500 uppercase tracking-wider font-bold text-right">Δ%</div>
      </div>
      
      {/* Timing Features */}
      <div className="mb-4">
        <h4 className="text-xs text-indigo-400 uppercase tracking-widest font-bold mb-2 mt-4">
          ⏱️ Timing Features
        </h4>
        {renderFeatureRow(
          'Mean Inter-Click Latency',
          referenceFeatures.meanInterClickLatency,
          attemptFeatures.meanInterClickLatency,
          comparison.latencyDelta,
          'ms'
        )}
        {renderFeatureRow(
          'Std Dev Latency',
          referenceFeatures.stdDevInterClickLatency,
          attemptFeatures.stdDevInterClickLatency,
          Math.abs((attemptFeatures.stdDevInterClickLatency - referenceFeatures.stdDevInterClickLatency) / Math.max(referenceFeatures.stdDevInterClickLatency, 1) * 100),
          'ms'
        )}
        {renderFeatureRow(
          'Latency Entropy',
          referenceFeatures.latencyEntropy,
          attemptFeatures.latencyEntropy,
          Math.abs((attemptFeatures.latencyEntropy - referenceFeatures.latencyEntropy) / Math.max(referenceFeatures.latencyEntropy, 1) * 100),
          ''
        )}
      </div>
      
      {/* Trajectory Features */}
      <div className="mb-4">
        <h4 className="text-xs text-emerald-400 uppercase tracking-widest font-bold mb-2 mt-4">
          🎯 Trajectory Features
        </h4>
        {renderFeatureRow(
          'Mean Velocity',
          referenceFeatures.meanVelocity,
          attemptFeatures.meanVelocity,
          comparison.velocityDelta,
          'px/ms'
        )}
        {renderFeatureRow(
          'Velocity Entropy',
          referenceFeatures.velocityEntropy,
          attemptFeatures.velocityEntropy,
          Math.abs((attemptFeatures.velocityEntropy - referenceFeatures.velocityEntropy) / Math.max(referenceFeatures.velocityEntropy, 1) * 100),
          ''
        )}
        {renderFeatureRow(
          'Path Deviation',
          referenceFeatures.pathDeviation,
          attemptFeatures.pathDeviation,
          comparison.pathDeviationDelta,
          'px'
        )}
        {renderFeatureRow(
          'Directness Ratio',
          referenceFeatures.directnessRatio,
          attemptFeatures.directnessRatio,
          Math.abs((attemptFeatures.directnessRatio - referenceFeatures.directnessRatio) / Math.max(referenceFeatures.directnessRatio, 1) * 100),
          'x'
        )}
      </div>
      
      {/* Precision Features */}
      <div className="mb-4">
        <h4 className="text-xs text-cyan-400 uppercase tracking-widest font-bold mb-2 mt-4">
          🎲 Precision & Hesitation
        </h4>
        {renderFeatureRow(
          'Click Precision',
          referenceFeatures.clickPrecision,
          attemptFeatures.clickPrecision,
          comparison.precisionDelta,
          'px'
        )}
        {renderFeatureRow(
          'Hesitation Count',
          referenceFeatures.hesitationCount,
          attemptFeatures.hesitationCount,
          Math.abs((attemptFeatures.hesitationCount - referenceFeatures.hesitationCount) / Math.max(referenceFeatures.hesitationCount, 1) * 100),
          ''
        )}
        {renderFeatureRow(
          'Jitter Score',
          referenceFeatures.jitterScore,
          attemptFeatures.jitterScore,
          Math.abs((attemptFeatures.jitterScore - referenceFeatures.jitterScore) / Math.max(referenceFeatures.jitterScore, 1) * 100),
          ''
        )}
      </div>
      
      {/* Summary Statistics */}
      <div className="mt-6 p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
        <div className="flex justify-between items-center">
          <span className="text-sm text-slate-400">Average Feature Deviation</span>
          <span className="text-lg font-bold text-white font-mono">
            {((comparison.latencyDelta + comparison.velocityDelta + comparison.pathDeviationDelta + comparison.precisionDelta) / 4).toFixed(1)}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default FeatureExtractor;
