'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Wallet, Network, Zap, ExternalLink, CheckCircle, 
  AlertCircle, Loader2, DollarSign, Copy, ChevronRight,
  RefreshCw, Info
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useAccount, useConnect, useDisconnect, useSwitchChain } from 'wagmi';
import { sepolia } from 'viem/chains';

export default function TestnetUtilities() {
  const { address, isConnected, chain } = useAccount();
  const { connect, connectors } = useConnect();
  const { disconnect } = useDisconnect();
  const { switchChain } = useSwitchChain();
  const [requesting, setRequesting] = useState(false);

  const isOnSepolia = chain?.id === sepolia.id;

  const handleConnectWallet = () => {
    const injected = connectors.find(c => c.id === 'injected' || c.name.includes('MetaMask'));
    if (injected) {
      connect({ connector: injected });
    } else {
      toast.error('Please install MetaMask to continue');
      window.open('https://metamask.io/download/', '_blank');
    }
  };

  const handleSwitchToSepolia = async () => {
    if (!isConnected) {
      toast.error('Please connect your wallet first');
      return;
    }

    try {
      await switchChain({ chainId: sepolia.id });
      toast.success('✅ Switched to Sepolia Testnet!');
    } catch (error: any) {
      console.error('Network switch failed:', error);
      toast.error('Failed to switch network. Please switch manually in MetaMask.');
    }
  };

  const handleRequestFunds = async (faucet: string) => {
    if (!isConnected) {
      toast.error('Please connect your wallet first');
      return;
    }

    if (!isOnSepolia) {
      toast.error('Please switch to Sepolia Testnet first');
      return;
    }

    setRequesting(true);

    try {
      // Open faucet in new tab with pre-filled address
      const faucetUrls: Record<string, string> = {
        alchemy: `https://sepoliafaucet.com/?address=${address}`,
        chainlink: `https://faucets.chain.link/sepolia`,
        infura: `https://www.infura.io/faucet/sepolia`,
        quicknode: `https://faucet.quicknode.com/ethereum/sepolia`
      };

      window.open(faucetUrls[faucet], '_blank');
      toast.success('Faucet opened! Complete the request in the new tab.');
    } catch (error) {
      console.error('Error opening faucet:', error);
      toast.error('Failed to open faucet');
    } finally {
      setTimeout(() => setRequesting(false), 2000);
    }
  };

  const copyAddress = () => {
    if (address) {
      navigator.clipboard.writeText(address);
      toast.success('Address copied to clipboard!');
    }
  };

  const faucets = [
    {
      id: 'alchemy',
      name: 'Alchemy Faucet',
      description: 'Get 0.5 Sepolia ETH per day',
      amount: '0.5 ETH',
      speed: 'Fast',
      color: 'blue'
    },
    {
      id: 'chainlink',
      name: 'Chainlink Faucet',
      description: 'Get 0.1 Sepolia ETH',
      amount: '0.1 ETH',
      speed: 'Fast',
      color: 'purple'
    },
    {
      id: 'infura',
      name: 'Infura Faucet',
      description: 'Get 0.5 Sepolia ETH per day',
      amount: '0.5 ETH',
      speed: 'Medium',
      color: 'orange'
    },
    {
      id: 'quicknode',
      name: 'QuickNode Faucet',
      description: 'Get 0.05 Sepolia ETH',
      amount: '0.05 ETH',
      speed: 'Fast',
      color: 'green'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Zap className="w-7 h-7 text-yellow-500" />
            Testnet Utilities
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Connect wallet, switch to Sepolia, and get test ETH for deployment
          </p>
        </div>
      </div>

      {/* Quick Start Guide */}
      <div className="bg-gradient-to-br from-yellow-900/20 to-gray-900/50 border border-yellow-500/30 rounded-xl p-6">
        <div className="flex items-start gap-3">
          <Info className="w-6 h-6 text-yellow-500 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">Quick Start Guide</h3>
            <div className="space-y-2 text-sm text-gray-300">
              <div className="flex items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 bg-yellow-500 text-black rounded-full font-bold text-xs">1</span>
                <span>Connect your MetaMask wallet</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 bg-yellow-500 text-black rounded-full font-bold text-xs">2</span>
                <span>Switch to Sepolia Testnet</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 bg-yellow-500 text-black rounded-full font-bold text-xs">3</span>
                <span>Get test ETH from any faucet below</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 bg-yellow-500 text-black rounded-full font-bold text-xs">4</span>
                <span>Start deploying contracts!</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Wallet Connection */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Wallet className="w-5 h-5 text-yellow-500" />
          Step 1: Connect Wallet
        </h3>

        {!isConnected ? (
          <button
            onClick={handleConnectWallet}
            className="w-full px-6 py-4 bg-gradient-to-r from-yellow-600 to-yellow-500 hover:from-yellow-700 hover:to-yellow-600 text-black rounded-lg font-semibold transition-all flex items-center justify-center gap-3 text-lg"
          >
            <Wallet className="w-6 h-6" />
            Connect MetaMask Wallet
          </button>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-green-600/10 border border-green-500/30 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-white" />
                </div>
                <div>
                  <div className="text-sm text-gray-400">Connected Wallet</div>
                  <div className="font-mono text-white font-medium">{address?.slice(0, 10)}...{address?.slice(-8)}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={copyAddress}
                  className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
                  title="Copy Address"
                >
                  <Copy className="w-4 h-4 text-gray-400" />
                </button>
                <button
                  onClick={() => disconnect()}
                  className="px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition-colors text-sm font-medium"
                >
                  Disconnect
                </button>
              </div>
            </div>

            <div className="flex items-center gap-2 text-sm text-gray-400">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-600'}`} />
              <span>Network: {chain?.name || 'Unknown'}</span>
            </div>
          </div>
        )}
      </div>

      {/* Network Switch */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Network className="w-5 h-5 text-yellow-500" />
          Step 2: Switch to Sepolia Testnet
        </h3>

        {!isConnected ? (
          <div className="text-center py-8 text-gray-500">
            <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Connect your wallet first to switch networks</p>
          </div>
        ) : isOnSepolia ? (
          <div className="p-4 bg-green-600/10 border border-green-500/30 rounded-lg">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-6 h-6 text-green-500" />
              <div>
                <div className="text-white font-semibold">Already on Sepolia Testnet! ✅</div>
                <div className="text-sm text-gray-400">You're ready to get test ETH</div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-4 bg-yellow-600/10 border border-yellow-500/30 rounded-lg">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-6 h-6 text-yellow-500" />
                <div>
                  <div className="text-white font-semibold">Wrong Network</div>
                  <div className="text-sm text-gray-400">Currently on {chain?.name}. Switch to Sepolia to continue.</div>
                </div>
              </div>
            </div>
            
            <button
              onClick={handleSwitchToSepolia}
              disabled={!isConnected}
              className="w-full px-6 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-all flex items-center justify-center gap-3"
            >
              <RefreshCw className="w-5 h-5" />
              Switch to Sepolia Testnet
            </button>
          </div>
        )}
      </div>

      {/* Faucets */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-yellow-500" />
          Step 3: Get Test ETH (Faucets)
        </h3>

        {!isConnected || !isOnSepolia ? (
          <div className="text-center py-8 text-gray-500">
            <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Complete steps 1 & 2 first to request test ETH</p>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="p-3 bg-blue-600/10 border border-blue-500/30 rounded-lg text-sm text-blue-400">
              💡 <strong>Tip:</strong> Try multiple faucets to get more test ETH. Each faucet has different daily limits.
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {faucets.map((faucet) => (
                <motion.div
                  key={faucet.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`p-5 bg-gradient-to-br from-${faucet.color}-900/20 to-gray-900/50 border border-${faucet.color}-500/30 rounded-xl cursor-pointer hover:border-${faucet.color}-500/50 transition-all`}
                  onClick={() => handleRequestFunds(faucet.id)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-semibold text-white mb-1">{faucet.name}</h4>
                      <p className="text-xs text-gray-400">{faucet.description}</p>
                    </div>
                    <ExternalLink className={`w-4 h-4 text-${faucet.color}-400`} />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`px-3 py-1 bg-${faucet.color}-600/20 text-${faucet.color}-400 rounded-full text-xs font-semibold`}>
                        {faucet.amount}
                      </div>
                      <div className={`px-3 py-1 bg-gray-800 text-gray-400 rounded-full text-xs`}>
                        {faucet.speed}
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-500" />
                  </div>
                </motion.div>
              ))}
            </div>

            <div className="mt-4 p-4 bg-gray-800/50 border border-gray-700 rounded-lg">
              <h4 className="text-sm font-semibold text-white mb-2">After Requesting:</h4>
              <ul className="text-xs text-gray-400 space-y-1">
                <li>• Complete any verification (CAPTCHA, login, etc.) on the faucet site</li>
                <li>• Test ETH should arrive in 30 seconds to 5 minutes</li>
                <li>• Check your MetaMask balance to confirm receipt</li>
                <li>• You can request from multiple faucets to get more ETH</li>
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Success State */}
      {isConnected && isOnSepolia && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-green-900/30 to-gray-900/50 border border-green-500/30 rounded-xl p-6"
        >
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
              <CheckCircle className="w-7 h-7 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-white mb-2">You're All Set! 🎉</h3>
              <p className="text-gray-300 text-sm mb-4">
                Your wallet is connected to Sepolia Testnet. Once you have test ETH, you can:
              </p>
              <div className="grid md:grid-cols-2 gap-3">
                <a
                  href="/kingdom?tab=contracts"
                  className="px-4 py-3 bg-yellow-600 hover:bg-yellow-700 text-black rounded-lg font-medium transition-all flex items-center gap-2 justify-center"
                >
                  <Zap className="w-4 h-4" />
                  Deploy Contracts
                </a>
                <a
                  href={`https://sepolia.etherscan.io/address/${address}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all flex items-center gap-2 justify-center"
                >
                  <ExternalLink className="w-4 h-4" />
                  View on Etherscan
                </a>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
