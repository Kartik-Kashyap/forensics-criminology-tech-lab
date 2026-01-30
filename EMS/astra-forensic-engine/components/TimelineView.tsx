
import React from 'react';
import { TimelineEvent, Evidence } from '../types';
import { formatTimestamp } from '../utils/forensics';

interface TimelineViewProps {
  events: TimelineEvent[];
  evidence: Evidence[];
}

const TimelineView: React.FC<TimelineViewProps> = ({ events, evidence }) => {
  const sortedEvents = [...events].sort((a, b) =>
    new Date(a.startTime).getTime() - new Date(b.startTime).getTime()
  );

  return (
    <div className="max-w-4xl mx-auto py-10 relative">
      {/* Vertical Line */}
      <div className="absolute left-1/2 transform -translate-x-1/2 top-0 bottom-0 w-px bg-slate-800"></div>

      {sortedEvents.map((event, index) => {
        const isLeft = index % 2 === 0;
        const linkedItems = evidence.filter(e => event.linkedEvidenceIds.includes(e.id));

        return (
          <div key={event.id} className={`flex w-full mb-12 items-center ${isLeft ? 'flex-row' : 'flex-row-reverse'}`}>
            {/* Content Card */}
            <div className={`w-5/12 ${isLeft ? 'pr-8 text-right' : 'pl-8 text-left'}`}>
              <div className="glass-panel p-6 rounded-2xl shadow-lg border border-slate-700/50 hover:border-emerald-500/50 transition-colors group relative overflow-hidden">
                <div className="absolute top-0 w-full h-px bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>

                <div className={`text-[10px] font-bold text-emerald-500/80 uppercase tracking-widest mb-1 font-mono`}>
                  {formatTimestamp(event.startTime)}
                </div>
                <h4 className="font-bold text-slate-200 text-lg mb-2 font-mono">{event.title}</h4>
                <p className="text-sm text-slate-400 mb-4 leading-relaxed">{event.description}</p>

                {linkedItems.length > 0 && (
                  <div className={`flex flex-wrap gap-2 ${isLeft ? 'justify-end' : 'justify-start'}`}>
                    {linkedItems.map(item => (
                      <div key={item.id} className="text-[10px] px-2 py-1 bg-slate-900/50 rounded text-slate-500 font-mono border border-slate-700 hover:border-emerald-500/30 transition-colors">
                        {item.name}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Timeline Dot */}
            <div className="w-2/12 flex justify-center z-10">
              <div className="h-4 w-4 rounded-full bg-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.5)] ring-4 ring-slate-900 border border-emerald-400"></div>
            </div>

            {/* Empty space for alignment */}
            <div className="w-5/12"></div>
          </div>
        );
      })}
    </div>
  );
};

export default TimelineView;
