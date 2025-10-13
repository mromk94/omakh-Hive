'use client';

/**
 * 🌟 GOLDEN RULE REDIRECT 🌟
 * 
 * This page redirects to /chat with dashboard view.
 * Following the conversational-first design principle.
 * 
 * Dashboard functionality is now a card in the chat interface.
 * No standalone pages - everything flows through conversation.
 * 
 * See: GOLDEN_RULE.md for details
 */

import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useAccount } from 'wagmi';

export default function DashboardPage() {
  const { isConnected } = useAccount();
  const router = useRouter();

  useEffect(() => {
    // 🌟 GOLDEN RULE: Redirect to chat with dashboard view
    // Following conversational-first design principle
    
    if (!isConnected) {
      router.push('/connect');
      return;
    }

    // Redirect to chat - dashboard will show as a card
    router.push('/chat?view=dashboard');
  }, [isConnected, router]);

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center">
      <motion.div
        animate={{ rotate: 360, scale: [1, 1.2, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="text-6xl mb-4"
      >
        👑
      </motion.div>
      <p className="text-yellow-500 text-center text-lg font-semibold">
        Redirecting to chat...
      </p>
      <p className="text-gray-400 text-center text-sm mt-2">
        Following conversational design
      </p>
    </div>
  );
}
