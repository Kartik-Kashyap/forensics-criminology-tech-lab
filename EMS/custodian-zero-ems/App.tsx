import React, { useState } from 'react';
import { Layout } from './components/Layout';
import { EvidenceDashboard } from './components/EvidenceDashboard';
import { EvidenceIntake } from './components/EvidenceIntake';
import { AIForensics } from './components/AIForensics';
import { SystemSpecs } from './components/SystemSpecs';
import { CaseManagement } from './components/CaseManagement';
import { AuditLogViewer } from './components/AuditLogViewer';
import { USERS, CURRENT_USER as DEFAULT_USER } from './constants';
import { User } from './types';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [currentUser, setCurrentUser] = useState<User>(DEFAULT_USER);

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
              {/* Stats Overview */}
              <div className="grid grid-cols-3 gap-4">
                 <div className="bg-[#0a0b10] border border-[#1a1a1a] p-4">
                    <div className="text-xs text-gray-500 uppercase">Open Cases</div>
                    <div className="text-2xl font-bold text-white font-mono">2</div>
                 </div>
                 <div className="bg-[#0a0b10] border border-[#1a1a1a] p-4">
                    <div className="text-xs text-gray-500 uppercase">Evidence Items</div>
                    <div className="text-2xl font-bold text-[#00f3ff] font-mono">17</div>
                 </div>
                 <div className="bg-[#0a0b10] border border-[#1a1a1a] p-4">
                    <div className="text-xs text-gray-500 uppercase">System Alerts</div>
                    <div className="text-2xl font-bold text-[#ff003c] font-mono">1</div>
                 </div>
              </div>

              {/* Activity Feed Mockup */}
              <div className="bg-[#0a0b10] border border-[#1a1a1a] p-4 mb-8">
                 <h3 className="text-xs font-bold text-gray-500 mb-4 flex justify-between">
                    <span>RECENT_CUSTODY_EVENTS</span>
                    <span className="text-[#00ff41] animate-pulse">LIVE</span>
                 </h3>
                 <div className="space-y-3">
                    {[1,2,3].map(i => (
                      <div key={i} className="flex gap-3 text-xs border-b border-[#111] pb-2 last:border-0">
                         <span className="text-gray-600 font-mono">10:4{i}:00</span>
                         <span className="text-[#00f3ff]">DET. DECKARD</span>
                         <span className="text-gray-400">accessed EVIDENCE #EVD-9921-A</span>
                      </div>
                    ))}
                 </div>
              </div>
            </div>
            
            <div className="space-y-8">
              <div className="bg-[#0a0b10] border border-[#1a1a1a] p-4">
                 <h3 className="text-xs font-bold text-gray-500 mb-2">SYSTEM_HEALTH</h3>
                 <div className="grid grid-cols-2 gap-4 mt-4">
                    <div className="text-center p-2 border border-[#222]">
                       <div className="text-xs text-gray-500">CPU LOAD</div>
                       <div className="text-lg font-mono text-[#00ff41]">12%</div>
                    </div>
                    <div className="text-center p-2 border border-[#222]">
                       <div className="text-xs text-gray-500">STORAGE_ENCRYPTED</div>
                       <div className="text-lg font-mono text-[#00ff41]">420 TB</div>
                    </div>
                 </div>
              </div>
              <div className="bg-[#1a0505] border border-[#333] p-4">
                 <h3 className="text-xs font-bold text-[#ff003c] mb-2">PENDING_ACTIONS</h3>
                 <ul className="text-xs space-y-2 text-gray-400">
                    <li>[ ] Review Flagged Video (Case-102)</li>
                    <li>[ ] Sign Custody Transfer #991</li>
                 </ul>
              </div>
            </div>
          </div>
        );
      case 'cases':
        return <CaseManagement currentUser={currentUser} />;
      case 'evidence':
        return <EvidenceDashboard />;
      case 'intake':
        // RBAC check example
        if (currentUser.role === 'VIEWER') return <div className="text-red-500 font-mono p-10 border border-red-900 bg-red-900/20">ACCESS DENIED: INSUFFICIENT PERMISSIONS</div>;
        return <EvidenceIntake />;
      case 'ai':
        if (currentUser.role === 'VIEWER') return <div className="text-red-500 font-mono p-10 border border-red-900 bg-red-900/20">ACCESS DENIED: INSUFFICIENT PERMISSIONS</div>;
        return <AIForensics />;
      case 'logs':
        return <AuditLogViewer />;
      case 'specs':
        return <SystemSpecs />;
      default:
        return <EvidenceDashboard />;
    }
  };

  return (
    <Layout 
      activeTab={activeTab} 
      onTabChange={setActiveTab} 
      currentUser={currentUser}
      onUserSwitch={setCurrentUser}
    >
      {renderContent()}
    </Layout>
  );
};

export default App;
