'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Wallet, Info, ChevronRight, Smartphone, Monitor, QrCode } from 'lucide-react';
import { useConnect, useAccount } from 'wagmi';
import { useAuthStore } from '@/stores/authStore';
import InteractiveCard from './InteractiveCard';

// Device detection
function useDeviceType() {
  const [deviceType, setDeviceType] = useState<'mobile' | 'tablet' | 'desktop'>('desktop');

  useEffect(() => {
    const checkDevice = () => {
      const width = window.innerWidth;
      if (width < 768) {
        setDeviceType('mobile');
      } else if (width < 1024) {
        setDeviceType('tablet');
      } else {
        setDeviceType('desktop');
      }
    };

    checkDevice();
    window.addEventListener('resize', checkDevice);
    return () => window.removeEventListener('resize', checkDevice);
  }, []);

  return deviceType;
}

interface WalletConnectCardProps {
  theme?: 'light' | 'dark';
  onConnected?: (address: string) => void;
}

export default function WalletConnectCard({ theme = 'dark', onConnected }: WalletConnectCardProps) {
  const [step, setStep] = useState<'question' | 'chain' | 'connect'>('question');
  const [selectedChain, setSelectedChain] = useState<'ethereum' | 'solana' | null>(null);
  const [showEthInfo, setShowEthInfo] = useState(false);
  const [showSolInfo, setShowSolInfo] = useState(false);
  const deviceType = useDeviceType();
  const isMobile = deviceType === 'mobile' || deviceType === 'tablet';
  
  const { connect, connectors, error } = useConnect({
    mutation: {
      onSuccess: () => {
        // Connection successful - address will be available from useAccount hook
      },
      onError: (error) => {
        console.error('Failed to connect wallet:', error);
      },
    },
  });
  const { address, isConnected } = useAccount();
  const { connectWallet, connectedWallets } = useAuthStore();
  const [hasCalledCallback, setHasCalledCallback] = useState(false);

  // When address changes, sync with authStore and call callback ONCE
  useEffect(() => {
    if (address && isConnected && !hasCalledCallback) {
      // Check if wallet is already connected (prevent infinite loop)
      const alreadyConnected = connectedWallets.some(w => w.address === address);
      
      if (!alreadyConnected) {
        // Update authStore
        connectWallet({
          id: address,
          address,
          chain: 'ethereum',
          type: 'injected',
          isPrimary: true,
          connectedAt: new Date(),
        });
        
        // Call callback if provided - ONLY ONCE
        if (onConnected) {
          onConnected(address);
          setHasCalledCallback(true);
        }
      }
    }
  }, [address, isConnected, hasCalledCallback]); // Track if callback was called

  const handleConnect = (connector: any) => {
    connect({ connector });
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

            {error && (
              <div className="bg-red-900/30 border border-red-500/30 rounded-xl p-4 text-sm text-red-300">
                <p className="font-semibold mb-1">Connection Failed</p>
                <p>{error.message}</p>
                {error.message.includes('MetaMask') && (
                  <p className="mt-2 text-xs">
                    Make sure MetaMask is installed and unlocked. Try refreshing the page.
                  </p>
                )}
              </div>
            )}

            {/* Device-specific UI */}
            {isMobile ? (
              <div className="space-y-3">
                <div className="bg-blue-900/30 border border-blue-500/30 rounded-xl p-4 mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Smartphone className="w-5 h-5 text-blue-400" />
                    <p className="font-semibold text-blue-300">Mobile Device Detected</p>
                  </div>
                  <p className="text-sm text-gray-300">Choose your wallet app:</p>
                </div>

                {connectors.map((connector) => {
                  const isWalletConnect = connector.id === 'walletConnect';
                  const isCoinbase = connector.id === 'coinbaseWallet';
                  const isInjected = connector.id === 'injected';

                  return (
                    <button
                      key={connector.id}
                      onClick={() => handleConnect(connector)}
                      className="w-full bg-gradient-to-r from-gray-800 to-gray-700 hover:from-gray-700 hover:to-gray-600 border border-yellow-500/30 rounded-xl p-4 transition-all group"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {isWalletConnect && <QrCode className="w-6 h-6 text-blue-400" />}
                          {isCoinbase && <div className="w-6 h-6 text-2xl">🔵</div>}
                          {isInjected && <div className="w-6 h-6 text-2xl">🦊</div>}
                          <div className="text-left">
                            <p className="font-semibold">{connector.name}</p>
                            <p className="text-xs text-gray-400">
                              {isWalletConnect && 'MetaMask, Trust Wallet, Rainbow...'}
                              {isCoinbase && 'Coinbase Wallet app'}
                              {isInjected && 'Browser wallet (if installed)'}
                            </p>
                          </div>
                        </div>
                        <ChevronRight className="w-5 h-5 text-yellow-500 group-hover:translate-x-1 transition-transform" />
                      </div>
                    </button>
                  );
                })}

                <div className="bg-yellow-900/30 border border-yellow-500/30 rounded-lg p-3 text-sm">
                  <p className="text-yellow-300 font-semibold mb-1">💡 Don't have a wallet?</p>
                  <a
                    href="https://metamask.io/download/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 underline"
                  >
                    Install MetaMask Mobile →
                  </a>
                </div>
              </div>
            ) : (
              // Desktop UI
              <div className="space-y-3">
                <div className="bg-purple-900/30 border border-purple-500/30 rounded-xl p-4 mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Monitor className="w-5 h-5 text-purple-400" />
                    <p className="font-semibold text-purple-300">Desktop Browser</p>
                  </div>
                  <p className="text-sm text-gray-300">Connect your browser wallet:</p>
                </div>

                {connectors.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-gray-400 mb-4">No wallet detected</p>
                    <a
                      href="https://metamask.io/download/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-block px-6 py-3 bg-orange-600 hover:bg-orange-500 text-white font-semibold rounded-lg transition-all"
                    >
                      Install MetaMask
                    </a>
                  </div>
                ) : (
                  connectors.map((connector) => {
                    const isInjected = connector.id === 'injected';
                    const isWalletConnect = connector.id === 'walletConnect';

                    return (
                      <button
                        key={connector.id}
                        onClick={() => handleConnect(connector)}
                        className="w-full bg-gray-800 hover:bg-gray-700 border border-yellow-500/30 rounded-xl p-4 flex items-center justify-between transition-all group"
                      >
                        <div className="flex items-center gap-3">
                          {isInjected && <span className="text-2xl">🦊</span>}
                          {isWalletConnect && <QrCode className="w-6 h-6 text-blue-400" />}
                          <div className="text-left">
                            <span className="font-semibold">{connector.name}</span>
                            {isWalletConnect && (
                              <p className="text-xs text-gray-400">Scan QR with mobile wallet</p>
                            )}
                          </div>
                        </div>
                        <ChevronRight className="w-5 h-5 text-yellow-500 group-hover:translate-x-1 transition-transform" />
                      </button>
                    );
                  })
                )}

                <div className="text-center text-sm text-gray-400">
                  <p>Using mobile? <span className="text-yellow-500">Refresh on your phone</span> for better options</p>
                </div>
              </div>
            )}

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
