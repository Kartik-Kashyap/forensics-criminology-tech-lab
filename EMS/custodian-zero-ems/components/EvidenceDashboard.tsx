import React from 'react';
import { MOCK_EVIDENCE } from '../constants';
import { IntegrityStatus, Evidence } from '../types';
import { AlertTriangle, Check, FileCode, Video, Lock, GitBranch } from 'lucide-react';

export const EvidenceDashboard: React.FC = () => {
  // Group evidence by parentId (or id if no parent) for logic, but display flat for now with visual cues
  const evidenceList = MOCK_EVIDENCE;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end border-b border-[#1a1a1a] pb-4">
         <div>
            <h2 className="text-2xl font-bold text-white">EVIDENCE LOCKER</h2>
            <p className="text-xs text-gray-500 font-mono mt-1">CASE-2024-089 :: ALL ARTIFACTS</p>
         </div>
         <div className="flex gap-2">
            <span className="text-[10px] bg-[#1a1a1a] px-2 py-1 text-gray-400 border border-[#333]">TOTAL_ITEMS: {evidenceList.length}</span>
            <span className="text-[10px] bg-[#1a1a1a] px-2 py-1 text-[#ff003c] border border-[#ff003c]/30">INTEGRITY_ALERTS: {evidenceList.filter(e => e.integrityStatus === IntegrityStatus.TAMPERED).length}</span>
         </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {evidenceList.map((item) => (
          <div key={item.id} className="bg-[#0a0b10] border border-[#1a1a1a] hover:border-[#333] transition-colors group relative flex flex-col">
            
            {/* Integrity Strip */}
            <div className={`absolute top-0 left-0 w-1 h-full ${
              item.integrityStatus === IntegrityStatus.VERIFIED ? 'bg-[#00ff41]' : 'bg-[#ff003c]'
            }`} />

            <div className="p-5 pl-7 flex-1">
               <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-2">
                    <div className="p-2 bg-[#111] border border-[#222]">
                      {item.fileType.includes('video') ? <Video size={20} className="text-[#00f3ff]" /> : <FileCode size={20} className="text-gray-400" />}
                    </div>
                    {/* Version Badge */}
                    <div className="flex items-center gap-1 bg-[#1a1a1a] border border-[#333] px-2 py-1 text-[10px] text-gray-400 font-mono">
                       <GitBranch size={10} />
                       v{item.version}
                    </div>
                  </div>

                  {item.integrityStatus === IntegrityStatus.TAMPERED && (
                    <div className="flex items-center gap-1 text-[#ff003c] text-[10px] border border-[#ff003c] px-2 py-0.5 bg-[#ff003c]/10 animate-pulse">
                      <AlertTriangle size={10} /> TAMPERED
                    </div>
                  )}
                  {item.integrityStatus === IntegrityStatus.VERIFIED && (
                    <div className="flex items-center gap-1 text-[#00ff41] text-[10px] border border-[#00ff41] px-2 py-0.5 bg-[#00ff41]/10">
                      <Check size={10} /> VERIFIED
                    </div>
                  )}
               </div>

               <h3 className="text-white font-mono text-sm truncate" title={item.name}>{item.name}</h3>
               <p className="text-[10px] text-gray-500 mb-2">{item.id}</p>
               
               {item.parentId && (
                 <div className="text-[9px] text-gray-600 mb-4 flex items-center gap-1">
                   ↳ Derived from: <span className="text-gray-400">{item.parentId}</span>
                 </div>
               )}

               <div className="space-y-2 mb-4">
                  <div className="text-[10px] font-mono text-gray-400 bg-[#050505] p-2 border border-[#222] break-all">
                     <span className="text-gray-600 block mb-1">SHA-3 HASH PREVIEW</span>
                     {item.hashSha3.substring(0, 32)}...
                  </div>
               </div>

               <div className="flex flex-wrap gap-2 mb-4">
                  {item.tags.map(tag => (
                    <span key={tag} className="text-[9px] px-1.5 py-0.5 bg-[#111] text-gray-400 border border-[#333]">#{tag}</span>
                  ))}
               </div>
            </div>

            <div className="p-3 border-t border-[#1a1a1a] flex justify-between items-center bg-[#080808]">
                <span className="text-[10px] text-gray-600 flex items-center gap-1">
                    <Lock size={10} /> {item.encryptionKeyId}
                </span>
                <button className="text-[10px] text-[#00f3ff] hover:text-white uppercase tracking-wider">
                  History
                </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
