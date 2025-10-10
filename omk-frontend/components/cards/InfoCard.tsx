'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { ReactNode, useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface InfoCardProps {
  title: string;
  content: string | ReactNode;
  icon?: ReactNode;
  expandedContent?: string | ReactNode;
  actions?: {
    label: string;
    action: () => void;
    variant?: 'primary' | 'secondary';
  }[];
  theme?: 'light' | 'dark';
  maxHeight?: number;
}

export default function InfoCard({ title, content, icon, expandedContent, actions, theme = 'light', maxHeight = 400 }: InfoCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const hasExpandedContent = !!expandedContent;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4, type: 'spring' }}
      className={`relative overflow-hidden rounded-3xl p-8 shadow-2xl ${
        theme === 'dark'
          ? 'bg-black/95 border border-yellow-900/30'
          : 'bg-stone-50/95 backdrop-blur-xl border border-yellow-600/30'
      }`}
    >
      {/* Gradient border effect */}
      <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-yellow-500/20 via-amber-500/20 to-yellow-600/20 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
      
      {/* Content */}
      <div className="relative z-10">
        {/* Icon + Title */}
        {(icon || title) && (
          <div className="flex items-center gap-4 mb-6">
            {icon && (
              <div className="text-4xl">
                {icon}
              </div>
            )}
            <h3 className={`text-2xl font-bold ${
              theme === 'dark' ? 'text-yellow-500' : 'text-yellow-700'
            }`}>
              {title}
            </h3>
          </div>
        )}
        
        {/* Body Content */}
        <div 
          className={`text-lg leading-relaxed mb-6 ${
            theme === 'dark' ? 'text-stone-300' : 'text-stone-700'
          } ${hasExpandedContent && !isExpanded ? 'max-h-[200px] overflow-hidden' : ''}`}
          style={hasExpandedContent && !isExpanded ? {
            maskImage: 'linear-gradient(to bottom, black 60%, transparent 100%)',
            WebkitMaskImage: 'linear-gradient(to bottom, black 60%, transparent 100%)',
          } : {}}
        >
          {content}
        </div>

        {/* Expanded Content */}
        <AnimatePresence>
          {isExpanded && expandedContent && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className={`text-lg leading-relaxed mb-6 overflow-y-auto ${
                theme === 'dark' ? 'text-stone-300' : 'text-stone-700'
              }`}
              style={{ maxHeight: `${maxHeight}px` }}
            >
              {expandedContent}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Read More Button */}
        {hasExpandedContent && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setIsExpanded(!isExpanded)}
            className={`w-full mb-4 px-6 py-3 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 ${
              theme === 'dark'
                ? 'bg-yellow-900/20 hover:bg-yellow-800/30 text-yellow-500 border border-yellow-900/30'
                : 'bg-yellow-100 hover:bg-yellow-200 text-yellow-700'
            }`}
          >
            {isExpanded ? (
              <>
                Show Less <ChevronUp className="w-5 h-5" />
              </>
            ) : (
              <>
                Read More <ChevronDown className="w-5 h-5" />
              </>
            )}
          </motion.button>
        )}
        
        {/* Action Buttons */}
        {actions && actions.length > 0 && (
          <div className="flex flex-wrap gap-3">
            {actions.map((action, idx) => (
              <motion.button
                key={idx}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={action.action}
                className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                  action.variant === 'secondary'
                    ? theme === 'dark'
                      ? 'bg-stone-800 hover:bg-stone-700 text-stone-200 border border-yellow-900/30'
                      : 'bg-stone-100 hover:bg-stone-200 text-stone-900'
                    : 'bg-gradient-to-r from-yellow-500 via-yellow-600 to-yellow-700 hover:from-yellow-400 hover:via-yellow-500 hover:to-yellow-600 text-black shadow-lg'
                }`}
              >
                {action.label}
              </motion.button>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}
