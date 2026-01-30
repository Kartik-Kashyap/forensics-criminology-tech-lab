import React, { useState } from 'react';
import { MOCK_CASES } from '../constants';
import { Briefcase, Plus, FolderOpen, Clock, AlertCircle } from 'lucide-react';
import { User } from '../types';

interface CaseManagementProps {
  currentUser: User;
}

export const CaseManagement: React.FC<CaseManagementProps> = ({ currentUser }) => {
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);

  const handleCreateCase = () => {
    alert("ACCESS_CONTROL: Case Creation Wizard Initiated...");
  };

  return (
    <div className="h-full flex flex-col space-y-6">
      <div className="flex justify-between items-end border-b border-[#1a1a1a] pb-4">
         <div>
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
               <Briefcase className="text-[#00ff41]" />
               CASE MANAGEMENT
            </h2>
            <p className="text-xs text-gray-500 font-mono mt-1">ACTIVE INVESTIGATIONS & ARCHIVES</p>
         </div>
         {currentUser.permissions.includes('create_case') && (
           <button 
             onClick={handleCreateCase}
             className="bg-[#00ff41] hover:bg-[#00cc33] text-black px-4 py-2 text-xs font-bold uppercase tracking-wider flex items-center gap-2"
           >
              <Plus size={16} />
              New Case
           </button>
         )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
         {MOCK_CASES.map(c => (
           <div 
             key={c.id} 
             className={`bg-[#0a0b10] border p-6 relative cursor-pointer group transition-all duration-300
               ${selectedCaseId === c.id ? 'border-[#00ff41] shadow-[0_0_20px_rgba(0,255,65,0.1)]' : 'border-[#1a1a1a] hover:border-[#333]'}
             `}
             onClick={() => setSelectedCaseId(c.id)}
           >
              <div className="absolute top-0 right-0 p-2">
                 {c.priority === 'HIGH' && <AlertCircle className="text-[#ff003c]" size={16} />}
              </div>

              <div className="mb-4">
                 <span className={`text-[10px] px-2 py-1 border ${c.status === 'OPEN' ? 'border-[#00ff41] text-[#00ff41]' : 'border-gray-600 text-gray-600'}`}>
                    {c.status}
                 </span>
              </div>

              <h3 className="text-white font-bold text-lg mb-1 group-hover:text-[#00f3ff] transition-colors">{c.title}</h3>
              <p className="text-xs text-gray-500 font-mono mb-4">{c.id}</p>
              
              <p className="text-sm text-gray-400 mb-6 line-clamp-2">{c.description}</p>

              <div className="grid grid-cols-2 gap-4 text-xs font-mono text-gray-500 border-t border-[#1a1a1a] pt-4">
                 <div>
                    <span className="block text-gray-700 uppercase mb-1">Investigator</span>
                    <span className="text-gray-300">{c.investigator}</span>
                 </div>
                 <div className="text-right">
                    <span className="block text-gray-700 uppercase mb-1">Evidence</span>
                    <span className="text-[#00f3ff]">{c.evidenceCount} Items</span>
                 </div>
                 <div className="col-span-2 flex items-center gap-2 mt-2">
                    <Clock size={12} />
                    Last Update: {new Date(c.lastUpdate).toLocaleDateString()}
                 </div>
              </div>
           </div>
         ))}
      </div>
      
      {/* Mock details view could go here if we had more screen real estate */}
      {selectedCaseId && (
        <div className="mt-8 p-4 border border-[#00f3ff]/30 bg-[#00f3ff]/5 text-[#00f3ff] text-xs font-mono">
           {'>'} CASE {selectedCaseId} SELECTED. NAVIGATE TO EVIDENCE LOCKER TO VIEW ARTIFACTS.
        </div>
      )}
    </div>
  );
};
