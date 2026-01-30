
import React, { useState } from 'react';
import Layout from './components/Layout';
import EvidenceCard from './components/EvidenceCard';
import TimelineView from './components/TimelineView';
import AnalysisView from './components/AnalysisView';
import { Case, EvidenceType, ConfidenceLevel } from './types';
import { generateMockHash } from './utils/forensics';

// Initial Mock Data reflecting a realistic Forensic Case
const INITIAL_CASE: Case = {
  id: 'case-001',
  caseNumber: '2024-0812-B',
  title: 'Incident at Riverbend Warehouse',
  summary: 'A reported break-in occurred on Aug 12, 2024. Security footage shows a single perpetrator entering via the north loading dock. Recovered items include a glove and a digital storage device.',
  leadInvestigator: 'Det. Sarah Miller',
  status: 'OPEN',
  createdAt: '2024-08-12T09:00:00Z',
  evidence: [
    {
      id: 'E-001',
      name: 'North Dock CCTV',
      type: EvidenceType.VIDEO,
      timestamp: '2024-08-12T02:15:00Z',
      description: 'Grains video showing a masked individual wearing a dark hoodie. Individual appears to have a limp.',
      hash: generateMockHash('video_stream_0215_cctv'),
      metadata: { resolution: '720p', duration: '120s', sensor: 'AXIS-V2' },
      source: 'Internal CCTV System',
      confidence: ConfidenceLevel.MEDIUM,
      tags: ['identification', 'video', 'loading-dock']
    },
    {
      id: 'E-002',
      name: 'Latex Glove (Blue)',
      type: EvidenceType.IMAGE,
      timestamp: '2024-08-12T08:30:00Z',
      description: 'Found near shelving unit 4B. Presumed left by perpetrator during the search.',
      hash: generateMockHash('image_glove_physical'),
      metadata: { location_x: 12.4, location_y: 55.2 },
      source: 'On-scene Recovery',
      confidence: ConfidenceLevel.VERIFIED,
      tags: ['physical', 'dna', 'latent-print']
    },
    {
      id: 'E-003',
      name: 'USB Drive (16GB)',
      type: EvidenceType.DOCUMENT,
      timestamp: '2024-08-12T08:45:00Z',
      description: 'Discovered in the office area. Encrypted partition detected.',
      hash: generateMockHash('usb_drive_binary_dump'),
      metadata: { capacity: '16GB', filesystem: 'FAT32' },
      source: 'On-scene Recovery',
      confidence: ConfidenceLevel.HIGH,
      tags: ['digital', 'encryption']
    },
    {
      id: 'E-004',
      name: 'Witness Statement - Guard J. Doe',
      type: EvidenceType.TEXT,
      timestamp: '2024-08-12T09:15:00Z',
      description: 'Reported hearing a loud bang at approx 02:10 AM. Did not see perpetrator.',
      hash: generateMockHash('text_witness_doe'),
      metadata: { interviewer: 'S. Miller' },
      source: 'Official Interview',
      confidence: ConfidenceLevel.MEDIUM,
      tags: ['witness', 'statement']
    }
  ],
  events: [
    {
      id: 'EV-001',
      title: 'Perpetrator Entry',
      description: 'Individual bypasses north dock magnetic lock.',
      startTime: '2024-08-12T02:12:00Z',
      linkedEvidenceIds: ['E-001'],
      participants: ['Perpetrator']
    },
    {
      id: 'EV-002',
      title: 'Security Alert',
      description: 'Motion sensor triggered in warehouse area.',
      startTime: '2024-08-12T02:15:00Z',
      linkedEvidenceIds: ['E-001'],
      participants: ['System']
    },
    {
      id: 'EV-003',
      title: 'Departure',
      description: 'Individual exits via the same route.',
      startTime: '2024-08-12T02:24:00Z',
      linkedEvidenceIds: ['E-001'],
      participants: ['Perpetrator']
    },
    {
      id: 'EV-004',
      title: 'Discovery',
      startTime: '2024-08-12T06:00:00Z',
      description: 'Opening shift manager discovers the office in disarray.',
      linkedEvidenceIds: [],
      participants: ['M. Smith']
    }
  ]
};

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [currentCase] = useState<Case>(INITIAL_CASE);

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <div className="space-y-8 animate-in fade-in duration-500">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {[
                { label: 'Total Evidence', val: currentCase.evidence.length, color: 'text-blue-400', border: 'border-blue-500/30' },
                { label: 'Timeline Events', val: currentCase.events.length, color: 'text-slate-300', border: 'border-slate-500/30' },
                { label: 'High Confidence', val: currentCase.evidence.filter(e => e.confidence === 'VERIFIED').length, color: 'text-emerald-400', border: 'border-emerald-500/30' },
                { label: 'Linked People', val: 3, color: 'text-amber-400', border: 'border-amber-500/30' }
              ].map((stat, i) => (
                <div key={i} className={`glass-panel p-6 rounded-2xl flex flex-col items-center justify-center relative overlow-hidden group hover:scale-[1.02] transition-transform ${stat.border}`}>
                  <div className={`absolute inset-0 bg-transparent opacity-0 group-hover:opacity-10 transition-opacity`}></div>
                  <span className={`text-4xl font-bold font-mono ${stat.color} drop-shadow-lg`}>{stat.val}</span>
                  <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mt-2">{stat.label}</span>
                </div>
              ))}
            </div>

            <div className="glass-panel p-8 rounded-2xl relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500/50"></div>
              <h3 className="text-lg font-bold mb-4 font-mono text-emerald-400 flex items-center gap-2">
                <span className="animate-pulse">_</span> CASE_NARRATIVE.LOG
              </h3>
              <p className="text-slate-300 leading-relaxed text-sm font-mono opacity-80 border-l-2 border-slate-700 pl-4">
                {currentCase.summary}
              </p>
              <div className="mt-8 pt-6 border-t border-slate-700/50 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
                <div>
                  <div className="text-slate-500 mb-1 uppercase tracking-wider">Lead Investigator</div>
                  <div className="text-emerald-500/80">{currentCase.leadInvestigator}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1 uppercase tracking-wider">Jurisdiction</div>
                  <div className="text-slate-300">Metro Central</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1 uppercase tracking-wider">Status</div>
                  <div className="inline-block text-emerald-400 font-bold tracking-widest animate-pulse">ACTIVE_INVESTIGATION</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1 uppercase tracking-wider">Last Sync</div>
                  <div className="text-slate-400">00:02:14</div>
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <button onClick={() => setActiveTab('analysis')} className="flex-1 group relative overflow-hidden bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-bold py-4 rounded-xl transition-all">
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-emerald-500/10 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
                <span className="relative z-10 flex items-center justify-center gap-2">
                  <span>⚡</span> INITIALIZE AI BIAS DETECTION
                </span>
              </button>
              <button onClick={() => setActiveTab('reconstruction')} className="flex-1 bg-slate-800/50 hover:bg-slate-800 text-slate-400 hover:text-white font-bold py-4 rounded-xl transition-all border border-slate-700">
                VIEW EVENT TIMELINE
              </button>
            </div>
          </div>
        );
      case 'evidence':
        return (
          <div className="space-y-6 animate-in slide-in-from-bottom-2 duration-300">
            <div className="flex justify-between items-center">
              <h3 className="text-2xl font-bold neon-text font-mono">EVIDENCE_VAULT</h3>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="SEARCH_HASH..."
                  className="bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2 text-sm w-64 text-emerald-400 focus:border-emerald-500 focus:outline-none placeholder-slate-600 font-mono"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {currentCase.evidence.map(item => (
                <EvidenceCard key={item.id} evidence={item} />
              ))}
              <div className="border border-dashed border-slate-700 rounded-xl flex flex-col items-center justify-center p-8 opacity-50 hover:opacity-100 transition-opacity bg-slate-900/30 cursor-pointer hover:border-emerald-500/50 hover:bg-emerald-900/10 group">
                <span className="text-2xl mb-2 group-hover:scale-110 transition-transform">➕</span>
                <span className="text-xs font-bold uppercase text-slate-500 group-hover:text-emerald-500">Ingest New Evidence</span>
                <span className="text-[10px] text-slate-600 mt-1">Immutable Chain Mode</span>
              </div>
            </div>
          </div>
        );
      case 'reconstruction':
        return <TimelineView events={currentCase.events} evidence={currentCase.evidence} />;
      case 'analysis':
        return <AnalysisView currentCase={currentCase} />;
      case 'report':
        return (
          <div className="max-w-4xl mx-auto bg-slate-950 p-12 border border-slate-800 min-h-screen font-mono text-sm space-y-8 animate-in zoom-in-95 duration-500 shadow-[0_0_50px_rgba(0,0,0,0.5)] relative">
            {/* Top Secret Stamp */}
            <div className="absolute top-12 right-12 border-4 border-slate-800 p-2 opacity-30 transform rotate-12 pointer-events-none">
              <span className="text-4xl font-black uppercase text-slate-700">CONFIDENTIAL</span>
            </div>

            <div className="text-center space-y-2 border-b border-slate-800 pb-8">
              <h2 className="text-2xl font-bold uppercase tracking-[0.3em] text-emerald-500/80">Forensic Analysis Protocol</h2>
              <p className="text-slate-500">Astra Platform Generated • <span className="text-emerald-800">Classified Level 4</span></p>
              <p className="text-slate-600 text-[10px]">{new Date().toISOString()}</p>
            </div>

            <div className="grid grid-cols-2 gap-8 border-b border-slate-800 pb-8">
              <div>
                <h4 className="font-bold text-slate-500 text-[10px] uppercase mb-4 tracking-widest">Subject Case</h4>
                <div className="space-y-1 text-slate-300">
                  <p><span className="w-24 inline-block text-slate-600">Case ID:</span> {currentCase.caseNumber}</p>
                  <p><span className="w-24 inline-block text-slate-600">Title:</span> {currentCase.title}</p>
                  <p><span className="w-24 inline-block text-slate-600">Status:</span> {currentCase.status}</p>
                </div>
              </div>
              <div>
                <h4 className="font-bold text-slate-500 text-[10px] uppercase mb-4 tracking-widest">Certification</h4>
                <p className="text-xs text-slate-500 leading-relaxed">
                  This report certifies that the evidence listed has been processed through the Astra Forensic Engine with hash verification enabled. Chain of custody is digitally logged.
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-bold text-[10px] uppercase text-emerald-500/50 tracking-widest">Inventory Summary</h4>
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-[10px] text-slate-500 uppercase">
                    <th className="py-2">Item ID</th>
                    <th className="py-2">Type</th>
                    <th className="py-2">Verification (SHA256)</th>
                  </tr>
                </thead>
                <tbody>
                  {currentCase.evidence.map(e => (
                    <tr key={e.id} className="border-b border-slate-900 text-[10px] text-slate-400 hover:bg-slate-900/50">
                      <td className="py-3 font-bold text-emerald-500/70">{e.id}</td>
                      <td className="py-3">{e.type}</td>
                      <td className="py-3 text-slate-600 font-mono">{e.hash.substring(0, 32)}...</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="space-y-4 bg-slate-900/30 p-6 rounded border border-slate-800">
              <h4 className="font-bold text-[10px] uppercase text-amber-500/50 tracking-widest">Notice</h4>
              <p className="text-[11px] text-slate-500 leading-relaxed">
                The AI Review & Bias Detection layer has flagged potential cognitive anomalies. Review attached addendum logs for details.
              </p>
            </div>

            <div className="flex justify-between items-end pt-20 text-slate-600">
              <div className="w-48 border-t border-slate-800 text-[10px] pt-2 text-center">
                Investigator Signature
              </div>
              <div className="w-48 border-t border-slate-800 text-[10px] pt-2 text-center">
                Verification Officer
              </div>
            </div>
          </div>
        );
      default:
        return <div>Select a tab</div>;
    }
  };

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderContent()}
    </Layout>
  );
};

export default App;
