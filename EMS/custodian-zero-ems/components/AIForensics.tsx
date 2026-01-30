import React, { useState, useEffect, useRef } from 'react';
import { Cpu, Terminal, Mic, StopCircle } from 'lucide-react';

export const AIForensics: React.FC = () => {
  const [analyzing, setAnalyzing] = useState(false);
  const [output, setOutput] = useState<string[]>([]);
  const outputEndRef = useRef<HTMLDivElement>(null);

  const startAnalysis = () => {
    if (analyzing) return;
    setAnalyzing(true);
    setOutput(['> INITIALIZING LLaMA 3.2 LOCAL CONTEXT...', '> LOADING EVIDENCE VECTOR STORE...', '> MOUNTING READ-ONLY FILE SYSTEM...', '']);
    
    const analysisSteps = [
      "> ANALYZING: server_access_logs_raw.log",
      "> DETECTED: 4,021 lines of text.",
      "> PATTERN MATCHING: Searching for 'sudo' anomalies...",
      "> ...",
      "> [INSIGHT] Spike in failed login attempts detected at 03:14:22 UTC from IP 192.168.1.55.",
      "> [INSIGHT] Successful root login at 03:15:00 UTC via SSH key (KeyID: unknown).",
      "> [HYPOTHESIS] The attacker may have brute-forced the 'admin' account and pivoted.",
      "> ",
      "> ANALYZING: cctv_server_room_cam4.mp4",
      "> EXTRACTING KEYFRAMES (Interval: 1s)...",
      "> [ANOMALY] Motion detected at 03:15:10 UTC in restricted zone.",
      "> [OCR] Text extracted from badge: 'VISITOR 404'.",
      "> ",
      "> REPORT GENERATION COMPLETE.",
      "> DISCLAIMER: AI insights are advisory only and non-evidentiary."
    ];

    let step = 0;
    const interval = setInterval(() => {
      if (step >= analysisSteps.length) {
        clearInterval(interval);
        setAnalyzing(false);
      } else {
        setOutput(prev => [...prev, analysisSteps[step]]);
        step++;
      }
    }, 800);
  };

  useEffect(() => {
    outputEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [output]);

  return (
    <div className="h-full flex flex-col max-h-[80vh]">
      <div className="mb-4 border-b border-[#1a1a1a] pb-4 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Cpu className="text-[#ff003c]" /> 
            AI FORENSIC ASSISTANT
          </h2>
          <p className="text-xs text-gray-500 font-mono mt-1">MODEL: LLaMA 3.2 (QUANTIZED) // HOST: LOCALHOST:11434</p>
        </div>
        <div className="flex gap-4">
           <div className="text-right">
              <div className="text-[10px] text-gray-500">PRIVACY MODE</div>
              <div className="text-xs text-[#00ff41] font-bold">AIR-GAPPED / NO CLOUD</div>
           </div>
        </div>
      </div>

      <div className="flex-1 bg-black border border-[#333] p-4 font-mono text-sm relative overflow-hidden flex flex-col shadow-[0_0_30px_rgba(0,0,0,0.5)]">
        {/* Terminal Header */}
        <div className="absolute top-0 left-0 w-full bg-[#111] p-1 flex items-center justify-between border-b border-[#333] px-2 z-10">
           <div className="flex gap-1">
             <div className="w-2 h-2 rounded-full bg-[#ff5f56]"></div>
             <div className="w-2 h-2 rounded-full bg-[#ffbd2e]"></div>
             <div className="w-2 h-2 rounded-full bg-[#27c93f]"></div>
           </div>
           <div className="text-[10px] text-gray-500">bash — forensic-agent — 80x24</div>
        </div>

        {/* Output Area */}
        <div className="mt-6 flex-1 overflow-y-auto space-y-1 pb-4">
           {output.map((line, i) => (
             <div key={i} className={`${line.includes('[INSIGHT]') ? 'text-[#00f3ff]' : line.includes('[ANOMALY]') ? 'text-[#ff003c]' : 'text-gray-300'}`}>
               {line}
             </div>
           ))}
           {analyzing && <div className="animate-pulse text-[#00ff41]">_</div>}
           <div ref={outputEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-[#333] pt-4 mt-2 flex gap-2">
          <div className="flex-1 bg-[#0a0a0a] border border-[#333] flex items-center px-3">
             <Terminal size={14} className="text-gray-500 mr-2" />
             <input 
               type="text" 
               placeholder="Ask LLaMA about the evidence timeline..." 
               className="bg-transparent border-none outline-none text-gray-300 text-xs w-full h-10 placeholder-gray-700"
               disabled={analyzing}
             />
          </div>
          <button 
            onClick={startAnalysis}
            disabled={analyzing}
            className={`px-6 text-xs font-bold flex items-center gap-2 uppercase tracking-wider transition-colors
              ${analyzing ? 'bg-[#333] text-gray-500 cursor-not-allowed' : 'bg-[#ff003c] hover:bg-[#d60032] text-white'}
            `}
          >
             {analyzing ? <StopCircle size={14} /> : <Cpu size={14} />}
             {analyzing ? 'PROCESSING' : 'RUN ANALYSIS'}
          </button>
        </div>
      </div>

      <div className="mt-4 p-4 bg-[#1a1a00] border border-yellow-900/50 text-yellow-600 text-xs font-mono">
        WARNING: AI outputs are generated probabilistically and must be verified by a human forensic analyst before inclusion in legal reports.
      </div>
    </div>
  );
};
