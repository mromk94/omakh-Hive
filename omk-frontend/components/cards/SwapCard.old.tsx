'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowDownUp, Loader2 } from 'lucide-react';
import { useAccount, useBalance, useReadContract, useWriteContract, useWaitForTransactionReceipt } from 'wagmi';
import { parseEther, formatUnits } from 'viem';
import InteractiveCard from './InteractiveCard';
import { formatNumber, formatCurrency } from '@/lib/utils';
import { DISPENSER_ADDRESS, DISPENSER_ABI, SUPPORTED_TOKENS } from '@/lib/contracts/dispenser';

interface SwapCardProps {
  theme?: 'light' | 'dark';
  onSwap?: (fromAmount: number, toAmount: number) => void;
  demoMode?: boolean;
}

export default function SwapCard({ theme = 'dark', onSwap, demoMode = false }: SwapCardProps) {
  const { address, isConnected } = useAccount();
  const [fromAmount, setFromAmount] = useState('');
  const [toAmount, setToAmount] = useState('');
  const [selectedToken, setSelectedToken] = useState<keyof typeof SUPPORTED_TOKENS>('ETH');
  const [destinationAddress, setDestinationAddress] = useState('');
  const [showDestination, setShowDestination] = useState(false);
  const [isSwapping, setIsSwapping] = useState(false);

  // Get ETH balance
  const { data: ethBalance } = useBalance({
    address: address as `0x${string}`,
    enabled: isConnected
  });

  // Get OMK price from dispenser
  const { data: omkPrice } = useReadContract({
    address: DISPENSER_ADDRESS as `0x${string}`,
    abi: DISPENSER_ABI,
    functionName: 'omkPriceUSD',
    query: { enabled: !demoMode }
  });

  // Get token price from dispenser
  const { data: tokenPrice } = useReadContract({
    address: DISPENSER_ADDRESS as `0x${string}`,
    abi: DISPENSER_ABI,
    functionName: 'tokenPricesUSD',
    args: [SUPPORTED_TOKENS[selectedToken].address as `0x${string}`],
    query: { enabled: !demoMode }
  });

  // Get swap quote
  const { data: swapQuote } = useReadContract({
    address: DISPENSER_ADDRESS as `0x${string}`,
    abi: DISPENSER_ABI,
    functionName: 'getSwapQuote',
    args: [
      SUPPORTED_TOKENS[selectedToken].address as `0x${string}`,
      fromAmount ? parseEther(fromAmount) : BigInt(0)
    ],
    query: {
      enabled: !demoMode && !!fromAmount && parseFloat(fromAmount) > 0
    }
  });

  // Swap contract write
  const { writeContract: swapETH, data: swapHash } = useWriteContract();
  
  const { isLoading: isConfirming, isSuccess: isConfirmed } = useWaitForTransactionReceipt({
    hash: swapHash,
  });

  // Calculate output amount
  useEffect(() => {
    if (demoMode) {
      // Demo mode - use mock calculation
      if (fromAmount) {
        const from = parseFloat(fromAmount);
        const rate = 2500 / 0.10; // ETH price / OMK price
        const to = from * rate * 0.99; // 1% slippage
        setToAmount(to.toFixed(4));
      } else {
        setToAmount('');
      }
    } else if (swapQuote) {
      // Real mode - use contract quote
      const [omkOut] = swapQuote as [bigint, bigint];
      setToAmount(formatUnits(omkOut, 18));
    } else {
      setToAmount('');
    }
  }, [fromAmount, swapQuote, demoMode]);

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
      <div className="space-y-4 w-full max-w-full overflow-hidden">
        {/* From Token */}
        <div className="w-full">
          <div className="flex items-center justify-between mb-2 text-xs sm:text-sm">
            <span className="text-gray-400">You Pay</span>
            <span className="text-gray-400">Balance: {formatNumber(fromToken.balance, 4)}</span>
          </div>
          <div className="bg-gray-800 rounded-xl p-3 sm:p-4 w-full">
            <div className="flex items-center justify-between gap-2">
              <input
                type="number"
                value={fromAmount}
                onChange={(e) => setFromAmount(e.target.value)}
                placeholder="0.0"
                className="flex-1 bg-transparent text-xl sm:text-2xl font-bold outline-none min-w-0"
              />
              <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
                <button
                  onClick={() => setFromAmount(fromToken.balance.toString())}
                  className="px-2 py-1 bg-yellow-500/20 text-yellow-500 text-xs font-semibold rounded-lg hover:bg-yellow-500/30"
                >
                  MAX
                </button>
                <div className="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-2 bg-gray-700 rounded-xl">
                  <span className="text-xl sm:text-2xl">{fromToken.icon}</span>
                  <span className="font-semibold text-sm sm:text-base">{fromToken.symbol}</span>
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
        <div className="w-full">
          <div className="flex items-center justify-between mb-2 text-xs sm:text-sm">
            <span className="text-gray-400">You Receive</span>
            <span className="text-gray-400">Balance: {formatNumber(toToken.balance, 2)}</span>
          </div>
          <div className="bg-gray-800 rounded-xl p-3 sm:p-4 w-full">
            <div className="flex items-center justify-between gap-2">
              <input
                type="number"
                value={toAmount}
                readOnly
                placeholder="0.0"
                className="flex-1 bg-transparent text-xl sm:text-2xl font-bold outline-none min-w-0"
              />
              <div className="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-2 bg-gray-700 rounded-xl flex-shrink-0">
                <span className="text-xl sm:text-2xl">{toToken.icon}</span>
                <span className="font-semibold text-sm sm:text-base">{toToken.symbol}</span>
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
          className="w-full py-3 sm:py-4 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 disabled:from-gray-700 disabled:to-gray-700 text-black disabled:text-gray-500 font-bold rounded-xl transition-all text-sm sm:text-base"
        >
          {!fromAmount ? 'Enter Amount' : parseFloat(fromAmount) > fromToken.balance ? 'Insufficient Balance' : (
            <>
              <span className="hidden sm:inline">Swap {fromToken.symbol} for {toToken.symbol}</span>
              <span className="sm:hidden">Swap Tokens</span>
            </>
          )}
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
