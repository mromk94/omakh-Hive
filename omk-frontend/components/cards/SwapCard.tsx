'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowDownUp } from 'lucide-react';
import InteractiveCard from './InteractiveCard';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface SwapCardProps {
  theme?: 'light' | 'dark';
  onSwap?: (fromAmount: number, toAmount: number) => void;
  demoMode?: boolean;
}

export default function SwapCard({ theme = 'dark', onSwap }: SwapCardProps) {
  const [fromAmount, setFromAmount] = useState('');
  const [toAmount, setToAmount] = useState('');
  const [fromToken, setFromToken] = useState({ symbol: 'ETH', icon: '💎', balance: 0.5, price: 2500 });
  const [toToken, setToToken] = useState({ symbol: 'OMK', icon: '🟡', balance: 10000, price: 0.10 });

  useEffect(() => {
    if (fromAmount) {
      const from = parseFloat(fromAmount);
      const rate = fromToken.price / toToken.price;
      const to = from * rate * 0.99; // 1% slippage
      setToAmount(to.toFixed(4));
    } else {
      setToAmount('');
    }
  }, [fromAmount, fromToken, toToken]);

  const handleSwapTokens = () => {
    const temp = fromToken;
    setFromToken(toToken);
    setToToken(temp);
    setFromAmount(toAmount);
  };

  const handleExecuteSwap = () => {
    if (onSwap) {
      onSwap(parseFloat(fromAmount), parseFloat(toAmount));
    }
    // Show success message
    alert('Swap executed! (This is a demo)');
  };

  return (
    <InteractiveCard title="🔄 Token Swap" theme={theme}>
      <div className="space-y-4">
        {/* From Token */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">You Pay</span>
            <span className="text-sm text-gray-400">Balance: {formatNumber(fromToken.balance, 4)}</span>
          </div>
          <div className="bg-gray-800 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <input
                type="number"
                value={fromAmount}
                onChange={(e) => setFromAmount(e.target.value)}
                placeholder="0.0"
                className="flex-1 bg-transparent text-2xl font-bold outline-none"
              />
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setFromAmount(fromToken.balance.toString())}
                  className="px-2 py-1 bg-yellow-500/20 text-yellow-500 text-xs font-semibold rounded-lg hover:bg-yellow-500/30"
                >
                  MAX
                </button>
                <div className="flex items-center gap-2 px-3 py-2 bg-gray-700 rounded-xl">
                  <span className="text-2xl">{fromToken.icon}</span>
                  <span className="font-semibold">{fromToken.symbol}</span>
                </div>
              </div>
            </div>
            {fromAmount && (
              <div className="mt-2 text-sm text-gray-400">
                ≈ {formatCurrency(parseFloat(fromAmount) * fromToken.price)}
              </div>
            )}
          </div>
        </div>

        {/* Swap Button */}
        <div className="flex justify-center -my-3 relative z-10">
          <button
            onClick={handleSwapTokens}
            className="p-3 bg-gray-800 hover:bg-gray-700 border-4 border-black rounded-xl transition-colors"
          >
            <ArrowDownUp className="w-5 h-5 text-yellow-500" />
          </button>
        </div>

        {/* To Token */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">You Receive</span>
            <span className="text-sm text-gray-400">Balance: {formatNumber(toToken.balance, 2)}</span>
          </div>
          <div className="bg-gray-800 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <input
                type="number"
                value={toAmount}
                readOnly
                placeholder="0.0"
                className="flex-1 bg-transparent text-2xl font-bold outline-none"
              />
              <div className="flex items-center gap-2 px-3 py-2 bg-gray-700 rounded-xl">
                <span className="text-2xl">{toToken.icon}</span>
                <span className="font-semibold">{toToken.symbol}</span>
              </div>
            </div>
            {toAmount && (
              <div className="mt-2 text-sm text-gray-400">
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
            className="p-4 bg-gray-800/50 rounded-xl space-y-2 text-sm"
          >
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Price Impact</span>
              <span className="text-green-500 font-semibold">0.12%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Network Fee</span>
              <span className="font-semibold">≈ {formatCurrency(5.50)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Minimum Received</span>
              <span className="font-semibold">{(parseFloat(toAmount) * 0.99).toFixed(4)} {toToken.symbol}</span>
            </div>
          </motion.div>
        )}

        {/* Execute Swap Button */}
        <button
          onClick={handleExecuteSwap}
          disabled={!fromAmount || parseFloat(fromAmount) <= 0 || parseFloat(fromAmount) > fromToken.balance}
          className="w-full py-4 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 disabled:from-gray-700 disabled:to-gray-700 text-black disabled:text-gray-500 font-bold rounded-xl transition-all"
        >
          {!fromAmount ? 'Enter Amount' : parseFloat(fromAmount) > fromToken.balance ? 'Insufficient Balance' : `Swap ${fromToken.symbol} for ${toToken.symbol}`}
        </button>

        {/* Info */}
        <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-xl flex items-start gap-2">
          <span className="text-yellow-500 text-xl">⚡</span>
          <p className="text-xs text-gray-300">
            Best rate found across multiple DEXs. Your transaction is protected by MEV protection.
          </p>
        </div>
      </div>
    </InteractiveCard>
  );
}
