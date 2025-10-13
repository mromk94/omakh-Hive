'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Crown, Wallet, GraduationCap, TrendingUp } from 'lucide-react';
import WalletConnectModal from '@/components/web3/WalletConnectModal';

export default function ConnectPage() {
  const [showConnectModal, setShowConnectModal] = useState(false);

  return (
    <div className="min-h-screen bg-black text-stone-100">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 opacity-20">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              rotate: [0, 180, 360],
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              ease: "linear",
            }}
            className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-yellow-600 to-amber-700 rounded-full blur-3xl"
          />
          <motion.div
            animate={{
              scale: [1, 1.3, 1],
              rotate: [360, 180, 0],
            }}
            transition={{
              duration: 25,
              repeat: Infinity,
              ease: "linear",
            }}
            className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-gradient-to-br from-yellow-500 to-yellow-700 rounded-full blur-3xl"
          />
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-6xl mx-auto px-6 py-20">
          {/* Logo & Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <motion.div
              animate={{
                rotate: [0, -10, 10, -10, 0],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatDelay: 3,
              }}
              className="inline-block mb-6"
            >
              <Crown className="w-20 h-20 text-yellow-500 mx-auto" style={{
                filter: 'drop-shadow(0 0 20px rgba(234, 179, 8, 0.8))'
              }} />
            </motion.div>

            <h1 className="text-6xl md:text-7xl font-black mb-6">
              <span className="bg-gradient-to-r from-yellow-500 via-yellow-600 to-yellow-700 bg-clip-text text-transparent">
                OMK HIVE
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-stone-400 max-w-2xl mx-auto">
              Invest in real estate, earn passive income, powered by blockchain
            </p>
          </motion.div>

          {/* Main CTA */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-center mb-16"
          >
            <button
              onClick={() => setShowConnectModal(true)}
              className="group relative px-12 py-6 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-black font-bold text-xl rounded-2xl transition-all shadow-2xl"
              style={{
                boxShadow: '0 20px 60px rgba(234, 179, 8, 0.5)'
              }}
            >
              <span className="relative z-10 flex items-center gap-3">
                <Wallet className="w-6 h-6" />
                Get Started
              </span>
            </button>

            <p className="text-sm text-stone-500 mt-4">
              Connect your wallet or learn how to get one
            </p>
          </motion.div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-gradient-to-br from-stone-900 to-black p-8 rounded-2xl border border-yellow-500/20"
            >
              <div className="w-12 h-12 bg-yellow-500/10 rounded-xl flex items-center justify-center mb-4">
                <TrendingUp className="w-6 h-6 text-yellow-500" />
              </div>
              <h3 className="text-xl font-bold text-stone-100 mb-2">
                Earn Passive Income
              </h3>
              <p className="text-stone-400">
                Invest in fractional real estate and earn monthly returns starting from $100
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-gradient-to-br from-stone-900 to-black p-8 rounded-2xl border border-yellow-500/20"
            >
              <div className="w-12 h-12 bg-yellow-500/10 rounded-xl flex items-center justify-center mb-4">
                <GraduationCap className="w-6 h-6 text-yellow-500" />
              </div>
              <h3 className="text-xl font-bold text-stone-100 mb-2">
                Learn & Grow
              </h3>
              <p className="text-stone-400">
                New to crypto? Our AI teacher will guide you every step of the way
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-gradient-to-br from-stone-900 to-black p-8 rounded-2xl border border-yellow-500/20"
            >
              <div className="w-12 h-12 bg-yellow-500/10 rounded-xl flex items-center justify-center mb-4">
                <Crown className="w-6 h-6 text-yellow-500" />
              </div>
              <h3 className="text-xl font-bold text-stone-100 mb-2">
                Web3 Powered
              </h3>
              <p className="text-stone-400">
                Transparent, secure, and fully decentralized real estate investment
              </p>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Wallet Connect Modal */}
      <WalletConnectModal 
        isOpen={showConnectModal}
        onClose={() => setShowConnectModal(false)}
      />
    </div>
  );
}
