import { useState, useEffect } from 'react';

/**
 * ThinkingPanel — live "reasoning" display, Copilot-agent style.
 *
 * While `isThinking` is true the panel shows an animated pulse and each step
 * appears as it arrives.  Once thinking is done it auto-collapses to a summary
 * line after a short pause.  The user can expand/collapse or dismiss entirely.
 *
 * Props:
 *   steps      {string[]}  — ordered list of steps received so far
 *   isThinking {boolean}   — true while SSE stream is still open
 *   onDismiss  {() => void} — called when user clicks ✕
 */
function ThinkingPanel({ steps = [], isThinking = false, onDismiss }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [isDismissed, setIsDismissed] = useState(false);

  // Auto-collapse shortly after thinking completes
  useEffect(() => {
    if (!isThinking && steps.length > 0) {
      const t = setTimeout(() => setIsExpanded(false), 1800);
      return () => clearTimeout(t);
    }
  }, [isThinking, steps.length]);

  // Re-open & un-dismiss when a new thinking session begins
  useEffect(() => {
    if (isThinking && steps.length === 1) {
      setIsExpanded(true);
      setIsDismissed(false);
    }
  }, [isThinking, steps.length]);

  if (isDismissed || steps.length === 0) return null;

  const handleDismiss = (e) => {
    e.stopPropagation();
    setIsDismissed(true);
    onDismiss?.();
  };

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg overflow-hidden shadow-sm">
      {/* ── Header — always visible, click to expand/collapse ── */}
      <div
        className="flex items-center justify-between px-4 py-2.5 cursor-pointer select-none hover:bg-gray-100 transition-colors"
        onClick={() => setIsExpanded((v) => !v)}
      >
        <div className="flex items-center gap-2.5">
          {isThinking ? (
            /* Three bouncing dots */
            <span className="flex gap-1 items-center h-4">
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" />
            </span>
          ) : (
            /* Green check when done */
            <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          )}
          <span className="text-sm font-medium text-gray-700">
            {isThinking
              ? `Thinking… (${steps.length} step${steps.length !== 1 ? 's' : ''})`
              : `Reasoned in ${steps.length} step${steps.length !== 1 ? 's' : ''}`}
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          {/* Chevron */}
          <svg
            className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
          {/* Dismiss ✕ */}
          <button
            onClick={handleDismiss}
            className="p-0.5 rounded text-gray-400 hover:text-gray-600 hover:bg-gray-200 transition-colors"
            title="Dismiss"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* ── Step list — shown when expanded ── */}
      {isExpanded && (
        <div className="px-4 pb-3 pt-1 space-y-1.5 border-t border-gray-100">
          {steps.map((step, i) => (
            <div key={i} className="flex items-center gap-2 text-sm text-gray-600">
              <svg className="w-3.5 h-3.5 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              {step}
            </div>
          ))}
          {isThinking && (
            <div className="flex items-center gap-2 text-sm text-gray-400 animate-pulse">
              <span className="w-3.5 flex-shrink-0 text-center">·</span>
              <span>Working…</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ThinkingPanel;
