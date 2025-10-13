'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowDownUp, Settings, Info, Zap, TrendingUp } from 'lucide-react';
import { useAccount } from 'wagmi';
import { useRouter } from 'next/navigation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface Token {
  symbol: string;
  name: string;
  icon: string;
  balance: number;
  price: number;
}

export default function SwapPage() {
  const { address, isConnected } = useAccount();
  const router = useRouter();
  
  const [fromToken, setFromToken] = useState<Token>({
    symbol: 'ETH',
    name: 'Ethereum',
    icon: '💎',
    balance: 0.5,
    price: 2500,
  });

  const [toToken, setToToken] = useState<Token>({
    symbol: 'OMK',
    name: 'Omakh Token',
    icon: '🟡',
    balance: 10000,
    price: 0.10,
  });

  const [fromAmount, setFromAmount] = useState('');
  const [toAmount, setToAmount] = useState('');
  const [slippage, setSlippage] = useState(1);
  const [showSettings, setShowSettings] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isConnected) {
      router.push('/connect');
    }
  }, [isConnected, router]);

  useEffect(() => {
    if (fromAmount) {
      const from = parseFloat(fromAmount);
      const rate = fromToken.price / toToken.price;
      const to = from * rate * (1 - slippage / 100);
      setToAmount(to.toFixed(4));
    } else {
      setToAmount('');
    }
  }, [fromAmount, fromToken, toToken, slippage]);

  const handleSwap = () => {
    // Temporary tokens switch
    const temp = fromToken;
    setFromToken(toToken);
    setToToken(temp);
    setFromAmount(toAmount);
  };

  const handleMaxClick = () => {
    setFromAmount(fromToken.balance.toString());
  };

  const handleSwapTokens = async () => {
    setIsLoading(true);
    // Simulate swap transaction
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsLoading(false);
    alert('Swap successful! (This is a demo)');
  };

  const priceImpact = 0.12;
  const networkFee = 5.50;
  const minReceived = toAmount ? (parseFloat(toAmount) * (1 - slippage / 100)).toFixed(4) : '0';

  return (
    <div className="min-h-screen bg-black text-stone-100">
      <div className="max-w-2xl mx-auto px-6 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-3xl md:text-4xl font-black mb-2">
            <span className="bg-gradient-to-r from-yellow-500 to-yellow-600 bg-clip-text text-transparent">
              Token Swap
            </span>
          </h1>
          <p className="text-stone-400">
            Trade tokens with the best rates
          </p>
        </motion.div>

        {/* Swap Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-stone-900 to-black border border-yellow-500/30 rounded-2xl p-6"
        >
          {/* Settings Button */}
          <div className="flex justify-end mb-4">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 hover:bg-yellow-500/10 rounded-lg transition-colors"
            >
              <Settings className="w-5 h-5 text-stone-400" />
            </button>
          </div>

          {/* Settings Panel */}
          {showSettings && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 p-4 bg-stone-800/50 rounded-xl"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-stone-400">Slippage Tolerance</span>
                <span className="text-sm text-stone-100 font-semibold">{slippage}%</span>
              </div>
              <div className="flex gap-2">
                {[0.5, 1, 2, 3].map((val) => (
                  <button
                    key={val}
                    onClick={() => setSlippage(val)}
                    className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-colors ${
                      slippage === val
                        ? 'bg-yellow-500 text-black'
                        : 'bg-stone-700 text-stone-300 hover:bg-stone-600'
                    }`}
                  >
                    {val}%
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {/* From Token */}
          <div className="mb-2">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-stone-400">You Pay</span>
              <span className="text-sm text-stone-400">
                Balance: {formatNumber(fromToken.balance, 4)}
              </span>
            </div>
            <div className="bg-stone-800 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <input
                  type="number"
                  value={fromAmount}
                  onChange={(e) => setFromAmount(e.target.value)}
                  placeholder="0.0"
                  className="flex-1 bg-transparent text-2xl font-bold text-stone-100 outline-none"
                />
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleMaxClick}
                    className="px-2 py-1 bg-yellow-500/20 text-yellow-500 text-xs font-semibold rounded-lg hover:bg-yellow-500/30 transition-colors"
                  >
                    MAX
                  </button>
                  <button className="flex items-center gap-2 px-3 py-2 bg-stone-700 hover:bg-stone-600 rounded-xl transition-colors">
                    <span className="text-2xl">{fromToken.icon}</span>
                    <span className="font-semibold">{fromToken.symbol}</span>
                  </button>
                </div>
              </div>
              {fromAmount && (
                <div className="mt-2 text-sm text-stone-400">
                  ≈ {formatCurrency(parseFloat(fromAmount) * fromToken.price)}
                </div>
              )}
            </div>
          </div>

          {/* Swap Button */}
          <div className="flex justify-center -my-3 relative z-10">
            <button
              onClick={handleSwap}
              className="p-3 bg-stone-800 hover:bg-stone-700 border-4 border-black rounded-xl transition-colors"
            >
              <ArrowDownUp className="w-5 h-5 text-yellow-500" />
            </button>
          </div>

          {/* To Token */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-stone-400">You Receive</span>
              <span className="text-sm text-stone-400">
                Balance: {formatNumber(toToken.balance, 2)}
              </span>
            </div>
            <div className="bg-stone-800 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <input
                  type="number"
                  value={toAmount}
                  readOnly
                  placeholder="0.0"
                  className="flex-1 bg-transparent text-2xl font-bold text-stone-100 outline-none"
                />
                <button className="flex items-center gap-2 px-3 py-2 bg-stone-700 hover:bg-stone-600 rounded-xl transition-colors">
                  <span className="text-2xl">{toToken.icon}</span>
                  <span className="font-semibold">{toToken.symbol}</span>
                </button>
              </div>
              {toAmount && (
                <div className="mt-2 text-sm text-stone-400">
                  ≈ {formatCurrency(parseFloat(toAmount) * toToken.price)}
                </div>
              )}
            </div>
          </div>

          {/* Transaction Details */}
          {fromAmount && toAmount && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mb-6 p-4 bg-stone-800/50 rounded-xl space-y-2 text-sm"
            >
              <div className="flex items-center justify-between">
                <span className="text-stone-400">Price Impact</span>
                <span className={`font-semibold ${priceImpact < 1 ? 'text-green-500' : priceImpact < 3 ? 'text-yellow-500' : 'text-red-500'}`}>
                  {priceImpact.toFixed(2)}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-stone-400">Minimum Received</span>
                <span className="text-stone-100 font-semibold">
                  {minReceived} {toToken.symbol}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-stone-400">Network Fee</span>
                <span className="text-stone-100 font-semibold">
                  ≈ {formatCurrency(networkFee)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1">
                  <span className="text-stone-400">Route</span>
                  <Info className="w-3 h-3 text-stone-500" />
                </div>
                <span className="text-stone-100 font-semibold text-xs">
                  {fromToken.symbol} → {toToken.symbol}
                </span>
              </div>
            </motion.div>
          )}

          {/* Swap Button */}
          <button
            onClick={handleSwapTokens}
            disabled={!fromAmount || parseFloat(fromAmount) <= 0 || parseFloat(fromAmount) > fromToken.balance || isLoading}
            className="w-full py-4 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 disabled:from-stone-700 disabled:to-stone-700 text-black disabled:text-stone-500 font-bold rounded-xl transition-all"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  ⏳
                </motion.div>
                Processing...
              </span>
            ) : !fromAmount ? (
              'Enter Amount'
            ) : parseFloat(fromAmount) > fromToken.balance ? (
              'Insufficient Balance'
            ) : (
              `Swap ${fromToken.symbol} for ${toToken.symbol}`
            )}
          </button>

          {/* Info Banner */}
          <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-xl flex items-start gap-2">
            <Zap className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-stone-300">
              Best rate found across multiple DEXs. Your transaction is protected by MEV protection.
            </p>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mt-6 grid grid-cols-2 gap-4"
        >
          <button
            onClick={() => router.push('/invest')}
            className="p-4 bg-gradient-to-br from-stone-900 to-black border border-yellow-500/30 rounded-xl hover:border-yellow-500/50 transition-all group"
          >
            <TrendingUp className="w-6 h-6 text-yellow-500 mb-2" />
            <div className="text-sm font-semibold text-stone-100 mb-1">Invest in Property</div>
            <div className="text-xs text-stone-400">Use OMK to earn passive income</div>
          </button>

          <button className="p-4 bg-gradient-to-br from-stone-900 to-black border border-yellow-500/30 rounded-xl hover:border-yellow-500/50 transition-all group">
            <Info className="w-6 h-6 text-yellow-500 mb-2" />
            <div className="text-sm font-semibold text-stone-100 mb-1">Learn More</div>
            <div className="text-xs text-stone-400">How token swaps work</div>
          </button>
        </motion.div>
      </div>
    </div>
  );
}
