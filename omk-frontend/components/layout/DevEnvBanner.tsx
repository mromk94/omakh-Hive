'use client';

import { useEffect, useState } from 'react';

export default function DevEnvBanner({ requiredMissing, optionalMissing }: { requiredMissing: string[]; optionalMissing: string[] }) {
  const [mounted, setMounted] = useState(false);
  const [minimized, setMinimized] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    try {
      const saved = localStorage.getItem('omk_dev_env_banner_minimized');
      setMinimized(saved === '1');
    } catch {}
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem('omk_dev_env_banner_minimized', minimized ? '1' : '0');
    } catch {}
  }, [minimized]);

  if (!mounted) return null;
  if (process.env.NODE_ENV !== 'development') return null;

  const hasIssues = requiredMissing.length > 0 || optionalMissing.length > 0;
  

  if (!hasIssues) return null;

  if (minimized) {
    return (
      <button
        onClick={() => setMinimized(false)}
        className="fixed bottom-4 right-4 z-50 px-3 py-2 rounded-full border border-yellow-500/40 bg-yellow-500/10 text-yellow-200 text-xs shadow-xl hover:bg-yellow-500/20"
        title="Show Dev Env Check"
      >
        DEV • Env Check
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-md p-3 sm:p-4 rounded-xl border border-yellow-500/40 bg-yellow-500/10 backdrop-blur text-yellow-200 shadow-xl">
      <div className="flex items-center justify-between mb-1">
        <div className="text-sm font-semibold">Dev Env Check</div>
        <button
          onClick={() => setMinimized(true)}
          className="text-xs text-yellow-300 hover:text-yellow-200"
          title="Minimize"
        >
          Minimize
        </button>
      </div>
      {requiredMissing.length > 0 && (
        <div className="text-xs mb-1">
          <span className="font-semibold text-yellow-300">Missing required:</span>
          <ul className="list-disc list-inside mt-1">
            {requiredMissing.map((k) => (
              <li key={k} className="text-yellow-200">{k}</li>
            ))}
          </ul>
        </div>
      )}
      {optionalMissing.length > 0 && (
        <div className="text-xs">
          <span className="font-semibold text-yellow-300">Missing optional:</span>
          <ul className="list-disc list-inside mt-1">
            {optionalMissing.map((k) => (
              <li key={k} className="text-yellow-200">{k}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
