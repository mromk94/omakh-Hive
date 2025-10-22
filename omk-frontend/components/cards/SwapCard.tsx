'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowDownUp, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useAccount, useBalance } from 'wagmi';
import { parseEther, formatEther } from 'viem';
import InteractiveCard from './InteractiveCard';
import { formatNumber, formatCurrency } from '@/lib/utils';
import { SUPPORTED_TOKENS } from '@/lib/contracts/dispenser';
import { API_ENDPOINTS } from '@/lib/constants';

interface SwapCardProps {
  theme?: 'light' | 'dark';
  onSwap?: (fromAmount: number, toAmount: number) => void;
  demoMode?: boolean;
}

export default function SwapCard({ theme = 'dark', onSwap, demoMode = true }: SwapCardProps) {
  const { address, isConnected } = useAccount();
  const [fromAmount, setFromAmount] = useState('');
  const [toAmount, setToAmount] = useState('');
  const [selectedToken, setSelectedToken] = useState<keyof typeof SUPPORTED_TOKENS>('ETH');
  const [destinationAddress, setDestinationAddress] = useState('');
  const [showDestination, setShowDestination] = useState(false);
  const [isSwapping, setIsSwapping] = useState(false);
  const [swapSuccess, setSwapSuccess] = useState(false);
  const [omkPrice, setOmkPrice] = useState(0.10);

  const currentToken = SUPPORTED_TOKENS[selectedToken];

  // Get ETH balance
  const { data: ethBalance } = useBalance({
    address: address as `0x${string}`,
    query: {
      enabled: isConnected
    }
  });

  const balance = selectedToken === 'ETH' && ethBalance 
    ? parseFloat(formatEther(ethBalance.value))
    : 0;

  // Mock prices (in production, get from dispenser contract)
  const tokenPrices: Record<string, number> = {
    ETH: 2500,
    USDT: 1,
    USDC: 1
  };

  useEffect(() => {
    const loadConfig = async () => {
      try {
        const res = await fetch(`${API_ENDPOINTS.FRONTEND}/config`);
        const data = await res.json();
        const price = data?.config?.omk_price_usd;
        if (typeof price === 'number' && price > 0) {
          setOmkPrice(price);
        }
      } catch {}
    };
    loadConfig();
  }, []);

  // Calculate output amount
  useEffect(() => {
    if (fromAmount && parseFloat(fromAmount) > 0) {
      const input = parseFloat(fromAmount);
      const tokenPrice = tokenPrices[selectedToken] || 0;
      const valueUSD = input * tokenPrice;
      const omkAmount = (valueUSD / omkPrice) * 0.99; // 1% fee
      setToAmount(omkAmount.toFixed(4));
    } else {
      setToAmount('');
    }
  }, [fromAmount, selectedToken]);

  // Set default destination to connected wallet
  useEffect(() => {
    if (isConnected && address && !destinationAddress) {
      setDestinationAddress(address);
    }
  }, [isConnected, address, destinationAddress]);

  const handleExecuteSwap = async () => {
    if (!fromAmount || parseFloat(fromAmount) <= 0) return;
    
    setIsSwapping(true);
    
    try {
      // In production, call dispenser contract here
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate transaction
      
      setSwapSuccess(true);
      if (onSwap) {
        onSwap(parseFloat(fromAmount), parseFloat(toAmount));
      }

      // Reset after success
      setTimeout(() => {
        setSwapSuccess(false);
        setFromAmount('');
        setToAmount('');
      }, 3000);
    } catch (error) {
      console.error('Swap failed:', error);
    } finally {
      setIsSwapping(false);
    }
  };

  const valueUSD = fromAmount ? parseFloat(fromAmount) * tokenPrices[selectedToken] : 0;
  const canSwap = isConnected && parseFloat(fromAmount) > 0 && parseFloat(fromAmount) <= balance;

  return (
    <InteractiveCard title="🔄 Token Swap" theme={theme}>
      <div className="space-y-4 w-full max-w-full overflow-hidden">
        {!isConnected && (
          <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-xl flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-gray-300">
              Connect your wallet to swap tokens for OMK
            </p>
          </div>
        )}

        {/* Token Selector */}
        <div className="flex gap-2">
          {(Object.keys(SUPPORTED_TOKENS) as Array<keyof typeof SUPPORTED_TOKENS>).map((token) => (
            <button
              key={token}
              onClick={() => setSelectedToken(token)}
              className={`flex-1 py-2 px-3 rounded-lg font-semibold text-sm transition-all ${
                selectedToken === token
                  ? 'bg-yellow-500 text-black'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {SUPPORTED_TOKENS[token].icon} {token}
            </button>
          ))}
        </div>

        {/* From Token */}
        <div className="w-full">
          <div className="flex items-center justify-between mb-2 text-xs sm:text-sm">
            <span className="text-gray-400">You Pay</span>
            <span className="text-gray-400">
              Balance: {formatNumber(balance, 4)} {currentToken.symbol}
            </span>
          </div>
          <div className="bg-gray-800 rounded-xl p-3 sm:p-4 w-full">
            <div className="flex items-center justify-between gap-2">
              <input
                type="number"
                value={fromAmount}
                onChange={(e) => setFromAmount(e.target.value)}
                placeholder="0.0"
                className="flex-1 bg-transparent text-xl sm:text-2xl font-bold outline-none min-w-0"
                disabled={!isConnected}
              />
              <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
                <button
                  onClick={() => setFromAmount(balance.toString())}
                  className="px-2 py-1 bg-yellow-500/20 text-yellow-500 text-xs font-semibold rounded-lg hover:bg-yellow-500/30 disabled:opacity-50"
                  disabled={!isConnected || balance === 0}
                >
                  MAX
                </button>
                <div className="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-2 bg-gray-700 rounded-xl">
                  <span className="text-xl sm:text-2xl">{currentToken.icon}</span>
                  <span className="font-semibold text-sm sm:text-base">{currentToken.symbol}</span>
                </div>
              </div>
            </div>
            {fromAmount && (
              <div className="mt-2 text-sm text-gray-400">
                ≈ {formatCurrency(valueUSD)}
              </div>
            )}
          </div>
        </div>

        {/* Swap Indicator */}
        <div className="flex justify-center -my-3 relative z-10">
          <div className="p-3 bg-gray-800 border-4 border-black rounded-xl">
            <ArrowDownUp className="w-5 h-5 text-yellow-500" />
          </div>
        </div>

        {/* To Token (OMK) */}
        <div className="w-full">
          <div className="flex items-center justify-between mb-2 text-xs sm:text-sm">
            <span className="text-gray-400">You Receive</span>
            <span className="text-gray-400">OMK Tokens</span>
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
                <span className="text-xl sm:text-2xl">🟡</span>
                <span className="font-semibold text-sm sm:text-base">OMK</span>
              </div>
            </div>
            {toAmount && (
              <div className="mt-2 text-sm text-gray-400">
                ≈ {formatCurrency(parseFloat(toAmount) * omkPrice)}
              </div>
            )}
          </div>
        </div>

        {/* Destination Address (Optional) */}
        <div className="w-full">
          <button
            onClick={() => setShowDestination(!showDestination)}
            className="text-sm text-yellow-500 hover:text-yellow-400 mb-2"
          >
            {showDestination ? '− Hide' : '+ Send to different address (optional)'}
          </button>
          
          <AnimatePresence>
            {showDestination && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-xl mb-2">
                  <p className="text-xs text-gray-400 mb-2">
                    ⚠️ OMK tokens will be sent to this address. Make sure it's correct!
                  </p>
                  <input
                    type="text"
                    value={destinationAddress}
                    onChange={(e) => setDestinationAddress(e.target.value)}
                    placeholder="0x..."
                    className="w-full bg-gray-800 text-sm p-2 rounded-lg outline-none border border-gray-600 focus:border-yellow-500"
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Transaction Details */}
        {fromAmount && toAmount && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="p-3 sm:p-4 bg-gray-800/50 rounded-xl space-y-2 text-sm"
          >
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Rate</span>
              <span className="font-semibold">
                1 {currentToken.symbol} = {formatNumber((1 * tokenPrices[selectedToken]) / omkPrice, 2)} OMK
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Fee (1%)</span>
              <span className="font-semibold">{formatNumber(parseFloat(toAmount) * 0.01, 4)} OMK</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Minimum Received</span>
              <span className="font-semibold">{formatNumber(parseFloat(toAmount) * 0.99, 4)} OMK</span>
            </div>
          </motion.div>
        )}

        {/* Execute Swap Button */}
        <button
          onClick={handleExecuteSwap}
          disabled={!canSwap || isSwapping}
          className="w-full py-3 sm:py-4 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 disabled:from-gray-700 disabled:to-gray-700 text-black disabled:text-gray-500 font-bold rounded-xl transition-all text-sm sm:text-base flex items-center justify-center gap-2"
        >
          {isSwapping ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Swapping...</span>
            </>
          ) : swapSuccess ? (
            <>
              <CheckCircle2 className="w-5 h-5" />
              <span>Success!</span>
            </>
          ) : !isConnected ? (
            'Connect Wallet First'
          ) : !fromAmount || parseFloat(fromAmount) <= 0 ? (
            'Enter Amount'
          ) : parseFloat(fromAmount) > balance ? (
            'Insufficient Balance'
          ) : (
            <>
              <span className="hidden sm:inline">Swap {currentToken.symbol} for OMK</span>
              <span className="sm:hidden">Swap Now</span>
            </>
          )}
        </button>

        {/* Info */}
        <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-xl flex items-start gap-2">
          <span className="text-yellow-500 text-xl flex-shrink-0">⚡</span>
          <div className="text-xs text-gray-300 space-y-1">
            <p className="font-semibold">OTC Dispenser - Queen Controlled</p>
            <p>Instant swaps at fixed price ($0.10/OMK). No DEX fees, no slippage.</p>
            <p>Tokens sent immediately to your wallet.</p>
          </div>
        </div>
      </div>
    </InteractiveCard>
  );
}
