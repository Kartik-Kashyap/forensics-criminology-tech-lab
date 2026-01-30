
import React from 'react';
import { Evidence, ConfidenceLevel } from '../types';
import { formatTimestamp, getEvidenceIcon } from '../utils/forensics';

interface EvidenceCardProps {
  evidence: Evidence;
}

const EvidenceCard: React.FC<EvidenceCardProps> = ({ evidence }) => {
  const getConfidenceColor = (level: ConfidenceLevel) => {
    switch (level) {
      case ConfidenceLevel.VERIFIED: return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/50 shadow-[0_0_10px_rgba(16,185,129,0.2)]';
      case ConfidenceLevel.HIGH: return 'bg-blue-500/10 text-blue-400 border-blue-500/50';
      case ConfidenceLevel.MEDIUM: return 'bg-amber-500/10 text-amber-400 border-amber-500/50';
      case ConfidenceLevel.LOW: return 'bg-rose-500/10 text-rose-400 border-rose-500/50';
      default: return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  return (
    <div className="bg-[#0f1523] border border-slate-800/60 rounded-xl p-5 flex flex-col gap-4 group hover:border-emerald-500/30 transition-all hover:bg-[#131b2c] relative overflow-hidden">
      {/* Corner accents */}
      <div className="absolute top-0 right-0 w-8 h-8 bg-gradient-to-bl from-slate-800/20 to-transparent"></div>

      <div className="flex justify-between items-start z-10">
        <div className="flex items-center gap-3">
          <div className="text-2xl bg-slate-900 w-12 h-12 flex items-center justify-center rounded border border-slate-800 text-slate-400 group-hover:text-emerald-500 transition-colors">
            {getEvidenceIcon(evidence.type)}
          </div>
          <div>
            <h3 className="font-semibold text-slate-200 group-hover:text-emerald-400 transition-colors">{evidence.name}</h3>
            <span className="text-xs text-slate-500 font-mono tracking-wider">{evidence.id}</span>
          </div>
        </div>
        <span className={`text-[10px] uppercase font-bold px-2 py-1 rounded border font-mono tracking-wider ${getConfidenceColor(evidence.confidence)}`}>
          {evidence.confidence}
        </span>
      </div>

      <p className="text-sm text-slate-400 line-clamp-2 leading-relaxed border-l-2 border-slate-800 pl-3">
        {evidence.description}
      </p>

      <div className="space-y-2 mt-2 font-mono">
        <div className="flex justify-between text-[10px] text-slate-500 uppercase tracking-widest">
          <span>Captured</span>
          <span className="text-slate-400">{formatTimestamp(evidence.timestamp)}</span>
        </div>
        <div className="p-2 bg-slate-950/50 rounded border border-slate-800/50 text-[10px] text-slate-500 break-all group-hover:border-slate-700 transition-colors">
          <div className="mb-1 text-slate-600 uppercase tracking-tighter flex items-center gap-2">
            <span className="w-1 h-1 bg-emerald-500 rounded-full"></span> Hash Notary
          </div>
          <span className="opacity-70">{evidence.hash}</span>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 pt-3 border-t border-slate-800/50 mt-auto">
        {evidence.tags.map(tag => (
          <span key={tag} className="px-2 py-1 bg-slate-900 text-slate-500 text-[10px] rounded border border-slate-800 hover:text-blue-400 hover:border-blue-500/30 transition-colors">
            #{tag}
          </span>
        ))}
      </div>
    </div>
  );
};

export default EvidenceCard;
