import { useState } from 'react';
import { ChevronDownIcon, ChevronUpIcon, InformationCircleIcon } from '@heroicons/react/24/solid';

interface Source {
  filename: string;
  chunk_index: number;
  content: string;
}

interface SourcesAccordionProps {
  sources: Source[];
  defaultExpanded?: boolean;
}

/**
 * Collapsible sources accordion component
 * 
 * Displays source documents in a collapsible panel.
 * Hidden by default to reduce UI clutter.
 */
export default function SourcesAccordion({ 
  sources, 
  defaultExpanded = false 
}: SourcesAccordionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  if (!sources || sources.length === 0) {
    return null;
  }

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      toggleExpanded();
    }
  };

  return (
    <div className="mt-4 pt-4 border-t border-slate-600">
      {/* Toggle Button */}
      <button
        onClick={toggleExpanded}
        onKeyDown={handleKeyPress}
        className="flex items-center justify-between w-full text-left hover:bg-slate-800/30 rounded-lg px-3 py-2 transition-colors group"
        aria-expanded={isExpanded}
        aria-controls="sources-content"
      >
        <div className="flex items-center gap-2">
          {isExpanded ? (
            <ChevronUpIcon className="w-4 h-4 text-purple-400" />
          ) : (
            <ChevronDownIcon className="w-4 h-4 text-purple-400" />
          )}
          <span className="text-sm font-semibold text-slate-300">
            {isExpanded ? 'Hide Sources' : 'Show Sources'}
          </span>
          <span className="text-xs text-slate-400 bg-slate-700/50 px-2 py-0.5 rounded-full">
            {sources.length}
          </span>
        </div>
        
        {/* Info Icon with Tooltip */}
        <div className="relative group/tooltip">
          <InformationCircleIcon className="w-4 h-4 text-slate-400 hover:text-slate-300 transition-colors" />
          <div className="absolute right-0 bottom-full mb-2 hidden group-hover/tooltip:block z-10">
            <div className="bg-slate-700 text-xs text-slate-200 px-3 py-2 rounded-lg shadow-lg whitespace-nowrap">
              View source documents used for this answer
              <div className="absolute top-full right-4 -mt-1">
                <div className="border-4 border-transparent border-t-slate-700"></div>
              </div>
            </div>
          </div>
        </div>
      </button>

      {/* Sources Content */}
      <div
        id="sources-content"
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isExpanded ? 'max-h-[1000px] opacity-100 mt-2' : 'max-h-0 opacity-0'
        }`}
        aria-hidden={!isExpanded}
      >
        <div className="space-y-2">
          {sources.map((source, idx) => (
            <div 
              key={idx} 
              className="bg-slate-800/50 rounded-lg p-3 text-sm border border-slate-700/50 hover:border-purple-500/30 transition-colors"
            >
              <div className="flex items-start justify-between gap-2 mb-1">
                <p className="font-medium text-purple-400 flex-1">
                  📄 {source.filename}
                </p>
                {source.chunk_index !== undefined && (
                  <span className="text-xs text-slate-400 bg-slate-700/70 px-2 py-0.5 rounded">
                    Chunk {source.chunk_index}
                  </span>
                )}
              </div>
              <p className="text-slate-300 text-xs line-clamp-3">
                {source.content}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* First-time hint (optional - can be shown on first query only) */}
      {!isExpanded && sources.length > 0 && (
        <p className="text-xs text-slate-500 mt-2 italic">
          💡 Click to see source references
        </p>
      )}
    </div>
  );
}

