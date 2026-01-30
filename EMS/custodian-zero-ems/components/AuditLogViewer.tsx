import React, { useState } from 'react';
import { MOCK_AUDIT_LOGS } from '../constants';
import { Shield, Filter, Search, Ban, Check, Terminal } from 'lucide-react';
import { UserRole } from '../types';

export const AuditLogViewer: React.FC = () => {
  const [filter, setFilter] = useState('');

  const filteredLogs = MOCK_AUDIT_LOGS.filter(log => 
    log.action.toLowerCase().includes(filter.toLowerCase()) ||
    log.userId.toLowerCase().includes(filter.toLowerCase()) ||
    log.resourceId.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full bg-[#0a0b10]">
       {/* Header */}
       <div className="border-b border-[#1a1a1a] p-6 flex justify-between items-center bg-[#050505]">
          <div>
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <Shield className="text-[#00ff41]" />
              IMMUTABLE AUDIT LEDGER
            </h2>
            <p className="text-xs text-gray-500 font-mono mt-1">
              READ-ONLY VIEW :: HASH-CHAIN VERIFIED
            </p>
          </div>
          <div className="flex gap-2 text-xs font-mono text-gray-500">
             <div className="bg-[#111] px-3 py-1 border border-[#333] flex items-center gap-2">
               <span className="w-2 h-2 bg-[#00ff41] rounded-full animate-pulse"></span>
               LOG_STREAM_ACTIVE
             </div>
          </div>
       </div>

       {/* Toolbar */}
       <div className="p-4 flex gap-4 border-b border-[#1a1a1a] bg-[#0a0a0a]">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600" size={14} />
            <input 
              type="text" 
              placeholder="Filter logs by User, Action ID, or Resource..."
              className="w-full bg-[#050505] border border-[#333] text-gray-300 text-xs pl-9 pr-3 py-2 focus:border-[#00ff41] outline-none font-mono"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-[#111] border border-[#333] text-gray-400 hover:text-white text-xs font-bold uppercase transition-colors">
             <Filter size={14} />
             Advanced Filter
          </button>
       </div>

       {/* Log Table */}
       <div className="flex-1 overflow-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-[#050505] sticky top-0 z-10 text-xs font-mono text-gray-500 uppercase tracking-wider">
               <tr>
                 <th className="p-4 border-b border-[#333]">Timestamp (UTC)</th>
                 <th className="p-4 border-b border-[#333]">Actor</th>
                 <th className="p-4 border-b border-[#333]">Role</th>
                 <th className="p-4 border-b border-[#333]">Action</th>
                 <th className="p-4 border-b border-[#333]">Target Resource</th>
                 <th className="p-4 border-b border-[#333]">Status</th>
                 <th className="p-4 border-b border-[#333]">Ledger Hash</th>
               </tr>
            </thead>
            <tbody className="font-mono text-xs text-gray-300">
               {filteredLogs.map((log) => (
                 <tr key={log.id} className="hover:bg-[#111] border-b border-[#1a1a1a] transition-colors group">
                    <td className="p-4 text-[#00f3ff]">{log.timestamp}</td>
                    <td className="p-4 font-bold">{log.userId}</td>
                    <td className="p-4 text-gray-500 text-[10px]">{log.userRole}</td>
                    <td className="p-4 text-white">{log.action}</td>
                    <td className="p-4 text-gray-400">{log.resourceId}</td>
                    <td className="p-4">
                      {log.status === 'SUCCESS' ? (
                        <span className="text-[#00ff41] flex items-center gap-1"><Check size={12}/> OK</span>
                      ) : (
                        <span className="text-[#ff003c] flex items-center gap-1"><Ban size={12}/> DENIED</span>
                      )}
                    </td>
                    <td className="p-4 text-gray-600 font-mono text-[10px] max-w-[150px] truncate group-hover:text-[#00ff41] transition-colors cursor-help" title={log.hash}>
                       {log.hash}
                    </td>
                 </tr>
               ))}
            </tbody>
          </table>
          {filteredLogs.length === 0 && (
            <div className="p-12 text-center text-gray-600 font-mono">
               <Terminal size={48} className="mx-auto mb-4 opacity-20" />
               NO_LOGS_FOUND_MATCHING_CRITERIA
            </div>
          )}
       </div>
    </div>
  );
};
