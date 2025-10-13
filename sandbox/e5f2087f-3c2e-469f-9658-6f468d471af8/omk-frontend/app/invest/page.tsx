'use client';

/**
 * 🌟 GOLDEN RULE REDIRECT 🌟
 * 
 * This page redirects to /chat with property investment view.
 * Following the conversational-first design principle.
 * 
 * Property browsing and investment is now a card flow in chat.
 * No standalone pages - everything flows through conversation.
 * 
 * See: GOLDEN_RULE.md for details
 */

import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useAccount } from 'wagmi';

export default function InvestPage() {
  const { isConnected } = useAccount();
  const router = useRouter();

  useEffect(() => {
    // 🌟 GOLDEN RULE: Redirect to chat with property investment view
    // Following conversational-first design principle
    
    if (!isConnected) {
      router.push('/connect');
      return;
    }

    // Redirect to chat - properties will show as cards
    router.push('/chat?view=properties');
  }, [isConnected, router]);

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center">
      <motion.div
        animate={{ rotate: 360, scale: [1, 1.2, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="text-6xl mb-4"
      >
        🏢
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
