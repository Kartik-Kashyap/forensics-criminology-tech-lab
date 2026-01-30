
import React from 'react';

interface LayoutProps {
  children: React.ReactNode;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const Layout: React.FC<LayoutProps> = ({ children, activeTab, setActiveTab }) => {
  const navItems = [
    { id: 'dashboard', label: 'COMMAND CENTER', icon: '📊' },
    { id: 'evidence', label: 'EVIDENCE VAULT', icon: '📦' },
    { id: 'reconstruction', label: 'TIMELINE RECON', icon: '⏳' },
    { id: 'analysis', label: 'AI NEURO-LINK', icon: '🧠' },
    { id: 'report', label: 'FINAL DOSSIER', icon: '📜' }
  ];

  return (
    <div className="flex h-screen bg-[#0a0f18] text-slate-300 overflow-hidden font-mono selection:bg-emerald-500/30 selection:text-emerald-300">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800/50 bg-[#05080f] flex flex-col relative z-20">
        <div className="p-6 border-b border-slate-800/50">
          <h1 className="text-2xl font-bold tracking-tighter flex items-center gap-2">
            <span className="text-emerald-500 neon-text">ASTRA</span>
            <span className="text-xs font-normal text-slate-500 uppercase tracking-[0.2em]">Forensics</span>
          </h1>
          <div className="mt-2 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_#10b981]"></div>
            <span className="text-[10px] uppercase text-emerald-500/80 tracking-widest">System Online</span>
          </div>
        </div>

        <nav className="flex-1 px-3 py-6 space-y-2">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded border transition-all duration-300 ${activeTab === item.id
                  ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.1)]'
                  : 'border-transparent text-slate-500 hover:text-slate-300 hover:bg-slate-900 hover:border-slate-800'
                }`}
            >
              <span className="opacity-70">{item.icon}</span>
              <span className="text-xs font-bold tracking-widest">{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Decorative Grid Background for sidebar */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-5 pointer-events-none"></div>

        <div className="p-4 border-t border-slate-800/50 text-[10px] text-slate-600 font-mono">
          <div className="flex justify-between mb-1">
            <span>OPERATOR:</span>
            <span className="text-emerald-500/70">ADMIN_01</span>
          </div>
          <div className="flex justify-between">
            <span>SESSION:</span>
            <span className="text-slate-500">XF-992-K</span>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-800/30">
            <div className="flex items-center gap-2 text-slate-700">
              <div className="w-full bg-slate-800 h-1 rounded overflow-hidden">
                <div className="bg-emerald-600 h-full w-[85%] animate-pulse"></div>
              </div>
              <span>85%</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Header */}
        <header className="h-16 border-b border-slate-800/50 bg-[#0a0f18]/80 backdrop-blur flex items-center justify-between px-8 z-10">
          <div className="flex items-center gap-4">
            <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 rounded text-xs font-mono font-bold tracking-wider">
              CASE #2024-0812-B
            </span>
            <h2 className="text-lg font-semibold text-slate-200 tracking-wide">Incident at Riverbend Warehouse</h2>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex flex-col items-end">
              <span className="text-[10px] text-slate-500 uppercase tracking-widest">Security Level 4</span>
              <span className="text-xs text-emerald-500/50 font-mono">ENCRYPTED CONNECTION</span>
            </div>
            <div className="h-10 w-10 rounded bg-slate-900 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-400">
              JD
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-8 relative">
          {/* Background Grid Pattern */}
          <div className="absolute inset-0 z-0 opacity-[0.03]"
            style={{
              backgroundImage: `linear-gradient(#334155 1px, transparent 1px), linear-gradient(90deg, #334155 1px, transparent 1px)`,
              backgroundSize: '40px 40px'
            }}
          ></div>
          <div className="relative z-10">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Layout;
