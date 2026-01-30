import React, { useState } from 'react';
import { USERS } from '../constants';
import { User } from '../types';
import { ShieldCheck, HardDrive, FileText, Activity, Lock, Server, Cpu, Briefcase, FileCode, ChevronDown, User as UserIcon, LogOut } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  activeTab: string;
  onTabChange: (tab: string) => void;
  currentUser: User;
  onUserSwitch: (user: User) => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, activeTab, onTabChange, currentUser, onUserSwitch }) => {
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  // RBAC: Filter menu items based on role permissions
  const allMenuItems = [
    { id: 'dashboard', label: 'DASHBOARD', icon: <Activity size={18} />, allowed: ['all'] },
    { id: 'cases', label: 'CASE_FILES', icon: <Briefcase size={18} />, allowed: ['create_case', 'view_case', 'all'] },
    { id: 'evidence', label: 'EVIDENCE_LOCKER', icon: <HardDrive size={18} />, allowed: ['view_evidence', 'all'] },
    { id: 'intake', label: 'SECURE_INTAKE', icon: <FileText size={18} />, allowed: ['upload_evidence', 'all'] },
    { id: 'ai', label: 'AI_FORENSICS', icon: <Cpu size={18} />, allowed: ['run_ai', 'all'] },
    { id: 'logs', label: 'AUDIT_LEDGER', icon: <FileCode size={18} />, allowed: ['all'] }, // Simplified: visible to all for demo, usually admin only
    { id: 'specs', label: 'SYSTEM_ARCH', icon: <Server size={18} />, allowed: ['all'] },
  ];

  const menuItems = allMenuItems.filter(item => 
    item.allowed.includes('all') || item.allowed.some(p => currentUser.permissions.includes(p))
  );

  return (
    <div className="flex h-screen w-full bg-[#050505] text-gray-300 font-mono overflow-hidden selection:bg-[#00ff41] selection:text-black">
      {/* Sidebar */}
      <aside className="w-64 border-r border-[#1a1a1a] flex flex-col justify-between bg-[#080808]">
        <div>
          <div className="p-6 border-b border-[#1a1a1a] border-l-4 border-l-[#00ff41]">
            <h1 className="text-2xl font-bold text-white tracking-wider flex items-center gap-2">
              <ShieldCheck className="text-[#00ff41]" />
              CUSTODIAN
              <span className="text-[#00ff41] text-xs align-top">ZERO</span>
            </h1>
            <p className="text-[10px] text-gray-500 mt-1 uppercase tracking-widest">Forensic Evidence System</p>
          </div>

          <nav className="mt-8 flex flex-col gap-1 px-2">
            {menuItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={`flex items-center gap-3 px-4 py-3 text-sm font-medium transition-all duration-200 border-l-2
                  ${activeTab === item.id 
                    ? 'border-[#00ff41] bg-[#00ff41]/10 text-[#00ff41] shadow-[0_0_15px_rgba(0,255,65,0.2)]' 
                    : 'border-transparent text-gray-500 hover:text-gray-300 hover:bg-[#111]'
                  }`}
              >
                {item.icon}
                {item.label}
              </button>
            ))}
          </nav>
        </div>

        {/* User Profile / Switcher */}
        <div className="p-4 border-t border-[#1a1a1a] relative">
          <div 
            className="flex items-center gap-3 cursor-pointer hover:bg-[#111] p-2 rounded transition-colors"
            onClick={() => setUserMenuOpen(!userMenuOpen)}
          >
            <div className={`w-8 h-8 border border-[#333] flex items-center justify-center font-bold text-xs
               ${currentUser.role === 'ADMIN' ? 'bg-[#ff003c] text-white' : 'bg-[#111] text-[#00ff41]'}
            `}>
              {currentUser.name.charAt(0)}
            </div>
            <div className="flex-1">
              <div className="text-xs text-white font-bold truncate w-32">{currentUser.name}</div>
              <div className="text-[10px] text-gray-500">{currentUser.role}</div>
            </div>
            <ChevronDown size={14} className={`transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
          </div>
          
          <div className="mt-3 flex items-center gap-2 text-[10px] text-[#00ff41]">
            <span className="w-2 h-2 rounded-full bg-[#00ff41] animate-pulse"></span>
            CONN: SECURE (TLS 1.3)
          </div>

          {/* Role Switcher Menu */}
          {userMenuOpen && (
            <div className="absolute bottom-full left-0 w-full bg-[#0a0b10] border border-[#333] mb-2 shadow-2xl z-50">
               <div className="p-2 border-b border-[#222] text-[10px] text-gray-500 font-bold uppercase">Switch Session (Debug)</div>
               {Object.values(USERS).map((u) => (
                 <button
                   key={u.id}
                   onClick={() => {
                     onUserSwitch(u);
                     setUserMenuOpen(false);
                   }}
                   className={`w-full text-left p-2 text-xs flex items-center gap-2 hover:bg-[#1a1a1a]
                     ${u.id === currentUser.id ? 'text-[#00ff41]' : 'text-gray-400'}
                   `}
                 >
                   <UserIcon size={12} />
                   {u.name} ({u.role})
                 </button>
               ))}
               <div className="border-t border-[#222] p-2 text-xs text-[#ff003c] flex items-center gap-2 cursor-not-allowed opacity-50">
                 <LogOut size={12} /> Logout
               </div>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]">
        
        {/* Header */}
        <header className="h-16 border-b border-[#1a1a1a] bg-[#080808]/90 backdrop-blur flex items-center justify-between px-8 z-10">
          <div className="flex items-center gap-4 text-xs tracking-widest">
             <span className="text-gray-500">SYSTEM_TIME_UTC:</span>
             <span className="text-[#00f3ff] font-bold">{new Date().toISOString().slice(0, 19).replace('T', ' ')}</span>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-xs border border-[#333] px-3 py-1 bg-[#050505]">
               <Lock size={12} className="text-[#00ff41]" />
               <span className="text-gray-400">ENCRYPTION:</span>
               <span className="text-[#00ff41]">AES-256-GCM</span>
            </div>
            <div className="flex items-center gap-2 text-xs border border-[#333] px-3 py-1 bg-[#050505]">
               <Cpu size={12} className="text-[#ff003c]" />
               <span className="text-gray-400">AI_ENGINE:</span>
               <span className="text-[#ff003c]">OFFLINE (LOCAL)</span>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-auto p-8 relative z-0">
          {children}
        </div>

      </main>
    </div>
  );
};
