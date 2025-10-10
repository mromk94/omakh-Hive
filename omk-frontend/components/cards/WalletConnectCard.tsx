'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Wallet, Info, ChevronRight } from 'lucide-react';
import { useConnect, useAccount } from 'wagmi';
import InteractiveCard from './InteractiveCard';

interface WalletConnectCardProps {
  theme?: 'light' | 'dark';
  onConnected?: (address: string) => void;
}

export default function WalletConnectCard({ theme = 'dark', onConnected }: WalletConnectCardProps) {
  const [step, setStep] = useState<'question' | 'chain' | 'connect'>('question');
  const [selectedChain, setSelectedChain] = useState<'ethereum' | 'solana' | null>(null);
  const [showEthInfo, setShowEthInfo] = useState(false);
  const [showSolInfo, setShowSolInfo] = useState(false);
  
  const { connect, connectors } = useConnect();
  const { address, isConnected } = useAccount();

  const handleConnect = (connector: any) => {
    connect({ connector }, {
      onSuccess: (data) => {
        if (onConnected && data.accounts[0]) {
          onConnected(data.accounts[0]);
        }
      },
    });
  };

  if (isConnected && address) {
    return (
      <InteractiveCard title="✅ Wallet Connected" theme={theme}>
        <div className="text-center py-6">
          <div className="text-6xl mb-4">🎉</div>
          <h3 className="text-2xl font-bold mb-2">Successfully Connected!</h3>
          <p className="text-sm text-gray-400 mb-4">
            {address.slice(0, 6)}...{address.slice(-4)}
          </p>
          <div className="inline-block px-4 py-2 bg-green-500/20 border border-green-500/30 rounded-lg">
            <span className="text-green-400 font-semibold">Ready to invest! 🚀</span>
          </div>
        </div>
      </InteractiveCard>
    );
  }

  return (
    <InteractiveCard title="🔗 Connect Your Wallet" theme={theme}>
      <div className="space-y-4">
        {/* Step 1: Question */}
        {step === 'question' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            <p className="text-center text-lg mb-6">Do you have a crypto wallet?</p>
            
            <button
              onClick={() => setStep('chain')}
              className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-4 rounded-xl transition-all"
            >
              ✅ Yes, I have a wallet
            </button>

            <button
              onClick={() => {/* Trigger Teacher Bee help */}}
              className="w-full bg-gray-800 hover:bg-gray-700 text-white font-bold py-4 rounded-xl border border-gray-600 transition-all"
            >
              📚 No, help me set one up
            </button>
          </motion.div>
        )}

        {/* Step 2: Chain Selection */}
        {step === 'chain' && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-4"
          >
            <p className="text-center mb-4">Choose your network:</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Ethereum */}
              <div className="relative">
                <button
                  onClick={() => {
                    setSelectedChain('ethereum');
                    setStep('connect');
                  }}
                  className="w-full bg-gradient-to-br from-gray-800 to-gray-700 hover:from-gray-700 hover:to-gray-600 p-6 rounded-xl border border-yellow-500/30 text-left transition-all group"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-4xl">💎</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowEthInfo(!showEthInfo);
                      }}
                      className="text-yellow-500 hover:text-yellow-400"
                    >
                      <Info className="w-5 h-5" />
                    </button>
                  </div>
                  
                  <h3 className="text-xl font-bold mb-2">Ethereum</h3>
                  <ul className="text-sm text-gray-400 space-y-1">
                    <li>• Most established</li>
                    <li>• Wide wallet support</li>
                    <li>• Higher security</li>
                  </ul>

                  <div className="flex items-center text-yellow-500 font-semibold mt-4 group-hover:translate-x-1 transition-transform">
                    Choose ETH <ChevronRight className="w-4 h-4 ml-1" />
                  </div>
                </button>

                {showEthInfo && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute top-full mt-2 w-full bg-gray-800 border border-yellow-500/30 rounded-xl p-4 text-sm z-10"
                  >
                    <p className="font-semibold text-yellow-500 mb-2">Ethereum Network:</p>
                    <p className="text-gray-300">Best for large investments. More liquidity but higher gas fees ($5-$50 per transaction).</p>
                  </motion.div>
                )}
              </div>

              {/* Solana */}
              <div className="relative">
                <button
                  onClick={() => {
                    setSelectedChain('solana');
                    setStep('connect');
                  }}
                  className="w-full bg-gradient-to-br from-gray-800 to-gray-700 hover:from-gray-700 hover:to-gray-600 p-6 rounded-xl border border-yellow-500/30 text-left transition-all group"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-4xl">⚡</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowSolInfo(!showSolInfo);
                      }}
                      className="text-yellow-500 hover:text-yellow-400"
                    >
                      <Info className="w-5 h-5" />
                    </button>
                  </div>
                  
                  <h3 className="text-xl font-bold mb-2">Solana</h3>
                  <ul className="text-sm text-gray-400 space-y-1">
                    <li>• Lightning fast</li>
                    <li>• Very low fees</li>
                    <li>• Growing ecosystem</li>
                  </ul>

                  <div className="flex items-center text-yellow-500 font-semibold mt-4 group-hover:translate-x-1 transition-transform">
                    Choose SOL <ChevronRight className="w-4 h-4 ml-1" />
                  </div>
                </button>

                {showSolInfo && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute top-full mt-2 w-full bg-gray-800 border border-yellow-500/30 rounded-xl p-4 text-sm z-10"
                  >
                    <p className="font-semibold text-yellow-500 mb-2">Solana Network:</p>
                    <p className="text-gray-300">Perfect for frequent trading. Ultra-fast transactions with fees less than $0.01.</p>
                  </motion.div>
                )}
              </div>
            </div>

            <button
              onClick={() => setStep('question')}
              className="w-full text-gray-400 hover:text-gray-200 py-2 transition-colors"
            >
              ← Back
            </button>
          </motion.div>
        )}

        {/* Step 3: Connect Wallet */}
        {step === 'connect' && selectedChain === 'ethereum' && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-3"
          >
            <p className="text-center mb-4">Connect Ethereum Wallet:</p>

            {connectors.map((connector) => (
              <button
                key={connector.id}
                onClick={() => handleConnect(connector)}
                className="w-full bg-gray-800 hover:bg-gray-700 border border-yellow-500/30 rounded-xl p-4 flex items-center justify-between transition-all group"
              >
                <span className="font-semibold">{connector.name}</span>
                <ChevronRight className="w-5 h-5 text-yellow-500 group-hover:translate-x-1 transition-transform" />
              </button>
            ))}

            <button
              onClick={() => setStep('chain')}
              className="w-full text-gray-400 hover:text-gray-200 py-2 transition-colors"
            >
              ← Back
            </button>
          </motion.div>
        )}

        {step === 'connect' && selectedChain === 'solana' && (
          <div className="text-center py-8">
            <p className="text-yellow-500 mb-4">⚠️ Solana integration coming soon!</p>
            <button
              onClick={() => setStep('chain')}
              className="text-gray-400 hover:text-gray-200"
            >
              ← Choose Ethereum instead
            </button>
          </div>
        )}
      </div>
    </InteractiveCard>
  );
}
