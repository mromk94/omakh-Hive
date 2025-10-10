'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Wallet, Info, ChevronRight } from 'lucide-react';
import { useConnect, useAccount } from 'wagmi';
import { useAuthStore } from '@/stores/authStore';

interface WalletConnectModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function WalletConnectModal({ isOpen, onClose }: WalletConnectModalProps) {
  const [step, setStep] = useState<'question' | 'chain-select' | 'connect'>('question');
  const [selectedChain, setSelectedChain] = useState<'ethereum' | 'solana' | null>(null);
  const [showEthInfo, setShowEthInfo] = useState(false);
  const [showSolInfo, setShowSolInfo] = useState(false);
  
  const { connect, connectors } = useConnect();
  const { address } = useAccount();
  const connectWallet = useAuthStore(state => state.connectWallet);

  const handleHasWallet = () => {
    setStep('chain-select');
  };

  const handleNoWallet = () => {
    // Redirect to FPRIME-9 education flow
    window.location.href = '/learn/wallets';
  };

  const handleChainSelect = (chain: 'ethereum' | 'solana') => {
    setSelectedChain(chain);
    setStep('connect');
  };

  const handleConnect = (connector: any) => {
    connect({ connector }, {
      onSuccess: (data) => {
        connectWallet({
          id: crypto.randomUUID(),
          address: data.accounts[0],
          chain: 'ethereum',
          type: connector.name,
          isPrimary: true,
          connectedAt: new Date(),
        });
        onClose();
      },
    });
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-lg bg-black border border-yellow-500/30 rounded-2xl p-6 z-50"
          >
            {/* Close Button */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 text-stone-400 hover:text-stone-200 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Step 1: Question */}
            {step === 'question' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6"
              >
                <div className="text-center">
                  <Wallet className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
                  <h2 className="text-2xl font-bold text-stone-100 mb-2">
                    Connect to Omakh
                  </h2>
                  <p className="text-stone-400">
                    Do you have a crypto wallet?
                  </p>
                </div>

                <div className="space-y-3">
                  <button
                    onClick={handleHasWallet}
                    className="w-full bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-black font-bold py-4 rounded-xl transition-all"
                  >
                    ✅ Yes, I have a wallet
                  </button>

                  <button
                    onClick={handleNoWallet}
                    className="w-full bg-stone-900 hover:bg-stone-800 text-stone-100 font-bold py-4 rounded-xl border border-yellow-500/30 transition-all"
                  >
                    📚 No, help me get started
                  </button>
                </div>
              </motion.div>
            )}

            {/* Step 2: Chain Selection */}
            {step === 'chain-select' && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-stone-100 mb-2">
                    Choose Your Network
                  </h2>
                  <p className="text-stone-400">
                    Select which blockchain network you'd like to use
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Ethereum */}
                  <div className="relative">
                    <button
                      onClick={() => handleChainSelect('ethereum')}
                      className="w-full bg-gradient-to-br from-stone-900 to-stone-800 hover:from-stone-800 hover:to-stone-700 p-6 rounded-xl border border-yellow-500/30 text-left transition-all group"
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
                      
                      <h3 className="text-xl font-bold text-stone-100 mb-2">
                        Ethereum
                      </h3>
                      
                      <ul className="text-sm text-stone-400 space-y-1 mb-4">
                        <li>• Most established</li>
                        <li>• Wide wallet support</li>
                        <li>• Higher security</li>
                      </ul>

                      <div className="flex items-center text-yellow-500 font-semibold group-hover:translate-x-1 transition-transform">
                        Choose ETH <ChevronRight className="w-4 h-4 ml-1" />
                      </div>
                    </button>

                    {/* Info Bubble */}
                    <AnimatePresence>
                      {showEthInfo && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                          className="absolute top-full mt-2 w-full bg-stone-900 border border-yellow-500/30 rounded-xl p-4 text-sm text-stone-300 z-10"
                        >
                          <p className="font-semibold text-yellow-500 mb-2">Ethereum Network:</p>
                          <p>Best for large investments. More liquidity but higher gas fees ($5-$50 per transaction).</p>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>

                  {/* Solana */}
                  <div className="relative">
                    <button
                      onClick={() => handleChainSelect('solana')}
                      className="w-full bg-gradient-to-br from-stone-900 to-stone-800 hover:from-stone-800 hover:to-stone-700 p-6 rounded-xl border border-yellow-500/30 text-left transition-all group"
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
                      
                      <h3 className="text-xl font-bold text-stone-100 mb-2">
                        Solana
                      </h3>
                      
                      <ul className="text-sm text-stone-400 space-y-1 mb-4">
                        <li>• Lightning fast</li>
                        <li>• Very low fees</li>
                        <li>• Growing ecosystem</li>
                      </ul>

                      <div className="flex items-center text-yellow-500 font-semibold group-hover:translate-x-1 transition-transform">
                        Choose SOL <ChevronRight className="w-4 h-4 ml-1" />
                      </div>
                    </button>

                    {/* Info Bubble */}
                    <AnimatePresence>
                      {showSolInfo && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                          className="absolute top-full mt-2 w-full bg-stone-900 border border-yellow-500/30 rounded-xl p-4 text-sm text-stone-300 z-10"
                        >
                          <p className="font-semibold text-yellow-500 mb-2">Solana Network:</p>
                          <p>Perfect for frequent trading. Ultra-fast transactions with fees less than $0.01.</p>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </div>

                <button
                  onClick={() => setStep('question')}
                  className="w-full text-stone-400 hover:text-stone-200 py-2 transition-colors"
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
                className="space-y-6"
              >
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-stone-100 mb-2">
                    Connect Ethereum Wallet
                  </h2>
                  <p className="text-stone-400">
                    Choose your wallet to connect
                  </p>
                </div>

                <div className="space-y-3">
                  {connectors.map((connector) => (
                    <button
                      key={connector.id}
                      onClick={() => handleConnect(connector)}
                      className="w-full bg-stone-900 hover:bg-stone-800 border border-yellow-500/30 rounded-xl p-4 flex items-center justify-between transition-all group"
                    >
                      <span className="text-stone-100 font-semibold">
                        {connector.name}
                      </span>
                      <ChevronRight className="w-5 h-5 text-yellow-500 group-hover:translate-x-1 transition-transform" />
                    </button>
                  ))}
                </div>

                <button
                  onClick={() => setStep('chain-select')}
                  className="w-full text-stone-400 hover:text-stone-200 py-2 transition-colors"
                >
                  ← Back
                </button>
              </motion.div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
