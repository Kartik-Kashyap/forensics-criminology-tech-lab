
import React, { useState, useEffect } from 'react';
import { Case, BiasAlert, AIReasoningLog } from '../types';
import { analyzeCaseForBias } from '../services/geminiService';

interface AnalysisViewProps {
  currentCase: Case;
}

const AnalysisView: React.FC<AnalysisViewProps> = ({ currentCase }) => {
  const [loading, setLoading] = useState(false);
  const [alerts, setAlerts] = useState<BiasAlert[]>([]);
  const [reasoning, setReasoning] = useState<AIReasoningLog[]>([]);

  const runAnalysis = async () => {
    setLoading(true);
    const result = await analyzeCaseForBias(currentCase);
    setAlerts(result.alerts);
    setReasoning(result.reasoning);
    setLoading(false);
  };

  useEffect(() => {
    runAnalysis();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Left Column: Bias Alerts */}
      <div className="lg:col-span-1 space-y-6">
        <div className="glass-panel p-6 rounded-2xl relative overflow-hidden">
          <div className="flex justify-between items-center mb-6 z-10 relative">
            <h3 className="font-bold text-slate-200 font-mono tracking-wider flex items-center gap-2">
              <span className="text-emerald-500">⚠</span> SIGNAL_DETECTION
            </h3>
            <button
              onClick={runAnalysis}
              disabled={loading}
              className="text-[10px] px-3 py-1 bg-emerald-500/10 text-emerald-400 font-mono border border-emerald-500/30 rounded hover:bg-emerald-500/20 disabled:opacity-50 transition-colors uppercase tracking-widest"
            >
              {loading ? 'SCANNING...' : 'RERUN_DIAGNOSTICS'}
            </button>
          </div>

          <div className="space-y-4">
            {alerts.length === 0 && !loading && (
              <p className="text-sm text-slate-500 italic font-mono p-4 border border-dashed border-slate-800 rounded">No critical thought-pattern anomalies detected in current dataset.</p>
            )}

            {alerts.map((alert, i) => (
              <div key={i} className={`p-4 rounded border-l-2 ${alert.severity === 'CRITICAL' ? 'bg-rose-950/30 border-rose-500' : 'bg-amber-950/30 border-amber-500'}`}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg animate-pulse">{alert.severity === 'CRITICAL' ? '🛑' : '⚠️'}</span>
                  <h4 className={`font-bold text-sm uppercase tracking-tight font-mono ${alert.severity === 'CRITICAL' ? 'text-rose-400' : 'text-amber-400'}`}>{alert.title}</h4>
                </div>
                <p className="text-xs text-slate-400 mb-3 font-mono leading-relaxed">{alert.description}</p>
                <div className="bg-slate-900/80 p-2 rounded text-[10px] text-slate-500 border border-slate-700/50 font-mono">
                  <strong className="text-emerald-500/80">SUGGESTED_PROTOCOL:</strong> {alert.suggestedAction}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[#05080f] border border-slate-800 p-6 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 p-2 opacity-20">
            <div className="text-[10px] font-mono text-blue-500">REF_DB_992</div>
          </div>
          <h4 className="font-bold mb-3 text-blue-400 font-mono text-xs uppercase tracking-widest">Psych-Db Entry #442</h4>
          <p className="text-xs text-slate-400 leading-relaxed font-mono opacity-80">
            "Confirmation bias is the tendency to search for, interpret, favor, and recall information in a way that confirms one's prior beliefs. Protocol requires active falsification attempts."
          </p>
          <div className="mt-4 flex items-center gap-2">
            <div className="h-px bg-slate-800 flex-1"></div>
            <p className="text-[9px] text-slate-600 uppercase tracking-widest font-bold">Forensic Research Inst.</p>
          </div>
        </div>
      </div>

      {/* Right Column: Reasoning Log */}
      <div className="lg:col-span-2">
        <div className="glass-panel p-8 rounded-2xl min-h-[500px] flex flex-col">
          <div className="flex items-center gap-3 mb-6 border-b border-slate-700/50 pb-4">
            <div className="p-2 bg-emerald-500/10 rounded border border-emerald-500/30 text-emerald-400 text-lg">🧠</div>
            <div>
              <h3 className="font-bold text-slate-200 text-lg font-mono">NEURAL_REASONING_TRACE</h3>
              <p className="text-xs text-slate-500 font-mono">Logic chain verification & confidence scoring</p>
            </div>
          </div>

          <div className="space-y-8 relative flex-1">
            {/* Visual connector line */}
            <div className="absolute left-4 top-2 bottom-2 w-px bg-slate-800"></div>

            {reasoning.map((step) => (
              <div key={step.step} className="relative pl-12 group">
                <div className="absolute left-0 top-0 w-8 h-8 rounded bg-slate-900 border border-slate-700 flex items-center justify-center font-mono text-xs font-bold text-emerald-500 z-10 shadow-[0_0_10px_rgba(0,0,0,0.5)] group-hover:border-emerald-500/50 transition-colors">
                  {step.step.toString().padStart(2, '0')}
                </div>
                <div className="space-y-3">
                  <div className="text-sm font-medium text-slate-300 leading-relaxed font-mono">
                    <span className="text-emerald-500/50 mr-2 opacity-50 select-none">{'>'}</span>
                    {step.thought}
                  </div>

                  {step.supportingEvidence.length > 0 && (
                    <div className="flex items-center gap-2 ml-4">
                      <span className="text-[10px] font-bold text-slate-600 uppercase tracking-wider">Ref:</span>
                      {step.supportingEvidence.map(id => (
                        <span key={id} className="px-2 py-0.5 bg-slate-800 text-slate-400 text-[10px] font-mono rounded border border-slate-700 hover:text-emerald-400 hover:border-emerald-500/30 transition-colors cursor-crosshair">
                          {id}
                        </span>
                      ))}
                    </div>
                  )}

                  {step.alternatives.length > 0 && (
                    <div className="bg-slate-900/50 p-3 rounded border border-slate-800/50 ml-4">
                      <div className="text-[10px] font-bold text-amber-500/70 uppercase mb-2 tracking-widest">Alternative Path Simulation:</div>
                      <ul className="space-y-1">
                        {step.alternatives.map((alt, idx) => (
                          <li key={idx} className="text-xs text-slate-500 italic font-mono flex gap-2">
                            <span>-</span> {alt}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex flex-col items-center justify-center py-20 gap-4 h-full">
                <div className="relative">
                  <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
                  <div className="absolute inset-0 rounded-full border-r-2 border-l-2 border-blue-500 animate-spin opacity-50" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
                </div>
                <div className="text-center space-y-1">
                  <p className="text-sm text-emerald-400 animate-pulse font-mono uppercase tracking-widest">Initializing Neural Link...</p>
                  <p className="textxs text-slate-600 font-mono">Accessing Local Llama 3.2 Core at ported 11434...</p>
                </div>
                <div className="w-64 bg-slate-900 h-1 rounded-full overflow-hidden mt-4">
                  <div className="h-full bg-emerald-500 animate-scan w-full origin-left"></div>
                </div>
              </div>
            )}

            {!loading && reasoning.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-slate-600 opacity-50">
                <div className="text-4xl mb-4">⌨</div>
                <p className="font-mono text-sm">System Ready. Await Input.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisView;
