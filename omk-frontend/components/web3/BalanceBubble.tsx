'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Settings, RefreshCw, User, LogOut, Copy, Check } from 'lucide-react';
import { useAccount, useBalance, useDisconnect, usePublicClient } from 'wagmi';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { formatAddress, formatNumber, formatCurrency } from '@/lib/utils';
import { chatActions } from '@/lib/chatEvents';
import { ERC20_ABI } from '@/lib/contracts/dispenser';
import { formatUnits } from 'viem';

export default function BalanceBubble() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copiedAddress, setCopiedAddress] = useState(false);
  const [omkBalance, setOmkBalance] = useState<string | null>(null);
  
  const router = useRouter();
  const { address, isConnected, chain } = useAccount();
  const { disconnect } = useDisconnect();
  const { primaryWallet, balances, logout, isConnected: authConnected } = useAuthStore();
  const publicClient = usePublicClient();
  
  // Get ETH balance
  const { data: ethBalance } = useBalance({
    address: address as `0x${string}`,
  });

  // Load OMK ERC20 balance (if configured)
  useEffect(() => {
    const loadOMK = async () => {
      try {
        setOmkBalance(null);
        const omkAddr = (
          chain?.id === 1
            ? (process.env.NEXT_PUBLIC_OMK_TOKEN_MAINNET as `0x${string}` | undefined)
            : chain?.id === 11155111
            ? (process.env.NEXT_PUBLIC_OMK_TOKEN_SEPOLIA as `0x${string}` | undefined)
            : (process.env.NEXT_PUBLIC_OMK_TOKEN_ADDRESS as `0x${string}` | undefined)
        );
        if (!publicClient || !address || !omkAddr) return;
        const bal = await publicClient.readContract({
          address: omkAddr,
          abi: ERC20_ABI as any,
          functionName: 'balanceOf',
          args: [address as `0x${string}`],
        }) as bigint;
        setOmkBalance(formatUnits(bal, 18));
      } catch (e) {
        setOmkBalance('0');
      }
    };
    loadOMK();
  }, [publicClient, address, chain?.id]);

  // Listen for global refresh events (e.g., after swaps/purchases)
  useEffect(() => {
    const handler = async () => {
      try {
        const omkAddr = (
          chain?.id === 1
            ? (process.env.NEXT_PUBLIC_OMK_TOKEN_MAINNET as `0x${string}` | undefined)
            : chain?.id === 11155111
            ? (process.env.NEXT_PUBLIC_OMK_TOKEN_SEPOLIA as `0x${string}` | undefined)
            : (process.env.NEXT_PUBLIC_OMK_TOKEN_ADDRESS as `0x${string}` | undefined)
        );
        if (!publicClient || !address || !omkAddr) return;
        const bal = await publicClient.readContract({
          address: omkAddr,
          abi: ERC20_ABI as any,
          functionName: 'balanceOf',
          args: [address as `0x${string}`],
        }) as bigint;
        setOmkBalance(formatUnits(bal, 18));
      } catch {}
    };
    window.addEventListener('balances:refresh', handler);
    return () => window.removeEventListener('balances:refresh', handler);
  }, [publicClient, address, chain?.id]);

  const handleCopyAddress = () => {
    if (address) {
      navigator.clipboard.writeText(address);
      setCopiedAddress(true);
      setTimeout(() => setCopiedAddress(false), 2000);
    }
  };

  const handleDisconnect = () => {
    disconnect();
    logout();
  };

  // 🌟 GOLDEN RULE: Button handlers that trigger chat
  const handleBuyOMK = () => {
    router.push('/chat');
    setTimeout(() => chatActions.buyOMK(), 300);
  };

  const handleSwap = () => {
    router.push('/chat');
    setTimeout(() => chatActions.swap(), 300);
  };

  const handleProfile = () => {
    router.push('/chat');
    setTimeout(() => chatActions.showProfile(), 300);
  };

  const handleSettings = () => {
    router.push('/chat');
    setTimeout(() => chatActions.showSettings(), 300);
  };

  // Show if wallet is connected; auth store enhances but shouldn't block wallet balances in dev
  if (!isConnected || !address) return null;

  // Calculate total portfolio value
  const totalValue = balances.reduce((sum, b) => sum + b.usdValue, 0) + 
    (ethBalance ? parseFloat(ethBalance.formatted) * 2500 : 0); // Mock ETH price

  return (
    <motion.div
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="fixed top-4 right-20 z-[90]"
    >
      {/* Collapsed View */}
      <motion.div
        layout
        className="bg-gradient-to-r from-stone-900 to-black border border-yellow-500/30 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-sm"
      >
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full px-6 py-3 flex items-center justify-between gap-4 hover:bg-yellow-500/5 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-yellow-500 to-amber-600 flex items-center justify-center text-black font-bold">
              {address[2]}
            </div>
            
            <div className="text-left">
              <div className="text-xs text-stone-400">Connected</div>
              <div className="text-sm font-semibold text-stone-100">
                {formatAddress(address)}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="text-right">
              <div className="text-xs text-stone-400">Portfolio</div>
              <div className="text-sm font-bold text-yellow-500">
                {formatCurrency(totalValue)}
              </div>
            </div>
            
            {isExpanded ? (
              <ChevronUp className="w-4 h-4 text-yellow-500" />
            ) : (
              <ChevronDown className="w-4 h-4 text-yellow-500" />
            )}
          </div>
        </button>

        {/* Expanded View */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="border-t border-yellow-500/20"
            >
              <div className="p-6 space-y-4">
                {/* Address Section */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-stone-400">Wallet Address</span>
                    <button
                      onClick={handleCopyAddress}
                      className="text-xs text-yellow-500 hover:text-yellow-400 transition-colors flex items-center gap-1"
                    >
                      {copiedAddress ? (
                        <>
                          <Check className="w-3 h-3" />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          Copy
                        </>
                      )}
                    </button>
                  </div>
                  <div className="text-sm font-mono text-stone-300 break-all">
                    {address}
                  </div>
                </div>

                {/* Network */}
                <div className="flex items-center justify-between py-2 border-y border-yellow-500/10">
                  <span className="text-xs text-stone-400">Network</span>
                  <span className="text-sm font-semibold text-stone-100 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                    {chain?.name || (chain?.id === 1 ? 'Ethereum Mainnet' : chain?.id === 11155111 ? 'Sepolia' : 'Unknown')}
                  </span>
                </div>

                {/* Balances */}
                <div className="space-y-3">
                  <div className="text-xs text-stone-400 font-semibold">Balances</div>
                  
                  {/* ETH Balance */}
                  {ethBalance && (
                    <div className="flex items-center justify-between p-3 bg-yellow-500/5 rounded-lg">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">💎</span>
                        <div>
                          <div className="text-sm font-semibold text-stone-100">ETH</div>
                          <div className="text-xs text-stone-400">Ethereum</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold text-stone-100">
                          {formatNumber(parseFloat(ethBalance.formatted), 4)}
                        </div>
                        <div className="text-xs text-stone-400">
                          {formatCurrency(parseFloat(ethBalance.formatted) * 2500)}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* OMK Balance */}
                  <div className="flex items-center justify-between p-3 bg-yellow-500/5 rounded-lg">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">🟡</span>
                      <div>
                        <div className="text-sm font-semibold text-stone-100">OMK</div>
                        <div className="text-xs text-stone-400">Omakh Token</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-stone-100">
                        {omkBalance !== null ? formatNumber(parseFloat(omkBalance || '0'), 4) : '—'}
                      </div>
                      <div className="text-xs text-stone-400">
                        —
                      </div>
                    </div>
                  </div>
                </div>

                {/* Total Portfolio */}
                <div className="pt-3 border-t border-yellow-500/10">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-stone-100">Total Portfolio</span>
                    <span className="text-lg font-bold text-yellow-500">
                      {formatCurrency(totalValue)}
                    </span>
                  </div>
                </div>

                {/* Actions - 🌟 GOLDEN RULE: Trigger chat conversations */}
                <div className="grid grid-cols-2 gap-2 pt-2">
                  <button 
                    onClick={handleBuyOMK}
                    className="px-4 py-2 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-black font-semibold rounded-lg transition-all text-sm"
                  >
                    Buy OMK
                  </button>
                  <button 
                    onClick={handleSwap}
                    className="px-4 py-2 bg-stone-800 hover:bg-stone-700 text-stone-100 font-semibold rounded-lg transition-all text-sm"
                  >
                    Swap
                  </button>
                </div>

                {/* Footer Actions - 🌟 GOLDEN RULE: Trigger chat conversations */}
                <div className="flex items-center gap-2 pt-2">
                  <button 
                    onClick={handleProfile}
                    className="flex-1 px-3 py-2 bg-stone-800/50 hover:bg-stone-800 text-stone-300 rounded-lg transition-all text-xs flex items-center justify-center gap-2"
                  >
                    <User className="w-3 h-3" />
                    Profile
                  </button>
                  <button 
                    onClick={handleSettings}
                    className="flex-1 px-3 py-2 bg-stone-800/50 hover:bg-stone-800 text-stone-300 rounded-lg transition-all text-xs flex items-center justify-center gap-2"
                  >
                    <Settings className="w-3 h-3" />
                    Settings
                  </button>
                  <button 
                    onClick={handleDisconnect}
                    className="flex-1 px-3 py-2 bg-red-900/20 hover:bg-red-900/30 text-red-400 rounded-lg transition-all text-xs flex items-center justify-center gap-2"
                  >
                    <LogOut className="w-3 h-3" />
                    Disconnect
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
}
