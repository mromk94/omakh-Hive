'use client';

import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface InteractiveCardProps {
  title: string;
  children: ReactNode;
  theme?: 'light' | 'dark';
}

export default function InteractiveCard({ title, children, theme = 'light' }: InteractiveCardProps) {
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
      {/* Animated gradient border */}
      <motion.div 
        className="absolute inset-0 rounded-3xl opacity-50"
        style={{
          background: 'linear-gradient(135deg, rgba(234,179,8,0.3) 0%, rgba(245,158,11,0.3) 50%, rgba(217,119,6,0.3) 100%)',
          backgroundSize: '200% 200%',
        }}
        animate={{
          backgroundPosition: ['0% 0%', '100% 100%', '0% 0%'],
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
      
      {/* Content */}
      <div className="relative z-10">
        {/* Title */}
        <h3 className={`text-2xl font-bold mb-6 ${
          theme === 'dark' ? 'text-yellow-500' : 'text-yellow-700'
        }`}>
          {title}
        </h3>
        
        {/* Interactive Content */}
        <div>
          {children}
        </div>
      </div>
    </motion.div>
  );
}
