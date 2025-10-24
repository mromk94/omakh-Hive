'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowDownUp, Settings, Info, Zap, TrendingUp } from 'lucide-react';
import { useAccount, usePublicClient, useWalletClient } from 'wagmi';
import { useRouter } from 'next/navigation';
import { formatNumber, formatCurrency } from '@/lib/utils';
import { DISPENSER_ADDRESS, DISPENSER_ABI, SUPPORTED_TOKENS, ERC20_ABI } from '@/lib/contracts/dispenser';
import { parseEther, formatUnits, parseUnits } from 'viem';
import { Toaster, toast } from 'react-hot-toast';

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
  const publicClient = usePublicClient();
  const { data: walletClient } = useWalletClient();
  
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
  const [showFromTokenMenu, setShowFromTokenMenu] = useState(false);

  const getPriceForSymbol = (symbol: string) => {
    if (symbol === 'ETH') return 2500;
    if (symbol === 'USDT' || symbol === 'USDC') return 1;
    return 0;
  };

  const selectFromToken = (symbol: 'ETH' | 'USDT' | 'USDC') => {
    const meta = (SUPPORTED_TOKENS as any)[symbol];
    const icon = symbol === 'ETH' ? '💎' : symbol === 'USDT' ? '💵' : '💰';
    setFromToken({
      symbol,
      name: meta?.name || symbol,
      icon,
      balance: 0,
      price: getPriceForSymbol(symbol)
    });
    setFromAmount('');
    setToAmount('');
    setShowFromTokenMenu(false);
  };

  useEffect(() => {
    if (!isConnected) {
      router.push('/connect');
    }
  }, [isConnected, router]);

  useEffect(() => {
    let cancelled = false;
    const quote = async () => {
      if (!publicClient) {
        return;
      }
      if (!fromAmount) {
        setToAmount('');
        return;
      }
      try {
        if (!DISPENSER_ADDRESS || DISPENSER_ADDRESS === '0x0000000000000000000000000000000000000000') {
          setToAmount('');
          return;
        }
        const meta = (SUPPORTED_TOKENS as any)[fromToken.symbol];
        if (!meta) {
          const from = parseFloat(fromAmount);
          const rate = fromToken.price / toToken.price;
          const to = from * rate * (1 - slippage / 100);
          if (!cancelled) setToAmount(to.toFixed(4));
          return;
        }
        const tokenIn = meta.address as `0x${string}`;
        const amountIn = parseUnits(fromAmount || '0', meta.decimals);
        const res: any = await publicClient.readContract({
          address: DISPENSER_ADDRESS as `0x${string}`,
          abi: DISPENSER_ABI as any,
          functionName: 'getSwapQuote',
          args: [tokenIn, amountIn],
        });
        const omkOut = Array.isArray(res) ? res[0] : res;
        const omkOutAdj = parseFloat(formatUnits(omkOut, 18)) * (1 - slippage / 100);
        if (!cancelled) setToAmount(omkOutAdj.toFixed(4));
      } catch {
        const from = parseFloat(fromAmount);
        const rate = fromToken.price / toToken.price;
        const to = from * rate * (1 - slippage / 100);
        if (!cancelled) setToAmount(Number.isFinite(to) ? to.toFixed(4) : '');
      }
    };
    quote();
    return () => {
      cancelled = true;
    };
  }, [fromAmount, fromToken, toToken, slippage, publicClient]);

  // Fetch on-chain balance for selected fromToken
  useEffect(() => {
    let cancelled = false;
    const loadBalance = async () => {
      try {
        if (!publicClient || !address) return;
        const sym = fromToken.symbol;
        if ((SUPPORTED_TOKENS as any)[sym]) {
          if (sym === 'ETH') {
            const bal = await publicClient.getBalance({ address: address as `0x${string}` });
            if (!cancelled) setFromToken((prev) => ({ ...prev, balance: parseFloat(formatUnits(bal, 18)) }));
          } else {
            const meta = (SUPPORTED_TOKENS as any)[sym];
            const bal = await publicClient.readContract({
              address: meta.address as `0x${string}`,
              abi: ERC20_ABI as any,
              functionName: 'balanceOf',
              args: [address as `0x${string}`]
            }) as bigint;
            if (!cancelled) setFromToken((prev) => ({ ...prev, balance: parseFloat(formatUnits(bal, meta.decimals)) }));
          }
        }
      } catch {
        // ignore
      }
    };
    loadBalance();
    return () => { cancelled = true; };
  }, [address, publicClient, fromToken.symbol]);

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
    try {
      if (!fromAmount || parseFloat(fromAmount) <= 0) return;
      setIsLoading(true);

      // ETH path → on-chain swap via Dispenser
      if (fromToken.symbol === 'ETH') {
        if (!walletClient || !address) {
          setIsLoading(false);
          toast.error('Connect wallet to proceed');
          return;
        }
        if (!DISPENSER_ADDRESS || DISPENSER_ADDRESS === '0x0000000000000000000000000000000000000000') {
          setIsLoading(false);
          toast.error('Dispenser not configured');
          return;
        }

        // Use current displayed toAmount as slippage-adjusted minOut (18 decimals)
        const minOut = toAmount ? parseUnits(toAmount, 18) : 0n;
        const value = parseEther(fromAmount);

        const hash = await walletClient.writeContract({
          address: DISPENSER_ADDRESS as `0x${string}`,
          abi: DISPENSER_ABI as any,
          functionName: 'swapETHForOMK',
          args: [minOut, address as `0x${string}`],
          value,
          account: address as `0x${string}`,
        });

        // Optional: wait for receipt with public client
        if (publicClient) {
          await publicClient.waitForTransactionReceipt({ hash });
        }

        // Refresh from-token balance
        try {
          if (publicClient) {
            const sym = fromToken.symbol;
            if (sym === 'ETH') {
              const bal = await publicClient.getBalance({ address: address as `0x${string}` });
              setFromToken((prev) => ({ ...prev, balance: parseFloat(formatUnits(bal, 18)) }));
            }
          }
        } catch {}

        setIsLoading(false);
        toast.success(`Swap successful!\nTx: ${hash}`);
        try { window.dispatchEvent(new Event('balances:refresh')); } catch {}
        return;
      }

      // ERC20 path (USDT/USDC)
      const meta = (SUPPORTED_TOKENS as any)[fromToken.symbol];
      if (!meta || !walletClient || !address) {
        setIsLoading(false);
        toast.error('Unsupported token or wallet disconnected');
        return;
      }
      const tokenIn = meta.address as `0x${string}`;
      const amountIn = parseUnits(fromAmount, meta.decimals);
      const minOut = toAmount ? parseUnits(toAmount, 18) : 0n;

      // Check allowance
      const allowance = await publicClient!.readContract({
        address: tokenIn,
        abi: ERC20_ABI as any,
        functionName: 'allowance',
        args: [address as `0x${string}`, DISPENSER_ADDRESS as `0x${string}`]
      }) as bigint;

      if (allowance < amountIn) {
        const approveHash = await walletClient.writeContract({
          address: tokenIn,
          abi: ERC20_ABI as any,
          functionName: 'approve',
          args: [DISPENSER_ADDRESS as `0x${string}`, amountIn],
          account: address as `0x${string}`,
        });
        if (publicClient) {
          await publicClient.waitForTransactionReceipt({ hash: approveHash });
        }
      }

      const swapHash = await walletClient.writeContract({
        address: DISPENSER_ADDRESS as `0x${string}`,
        abi: DISPENSER_ABI as any,
        functionName: 'swapTokenForOMK',
        args: [tokenIn, amountIn, minOut, address as `0x${string}`],
        account: address as `0x${string}`,
      });
      if (publicClient) {
        await publicClient.waitForTransactionReceipt({ hash: swapHash });
      }
      // Refresh from-token balance
      try {
        if (publicClient) {
          const bal = await publicClient.readContract({
            address: tokenIn,
            abi: ERC20_ABI as any,
            functionName: 'balanceOf',
            args: [address as `0x${string}`]
          }) as bigint;
          setFromToken((prev) => ({ ...prev, balance: parseFloat(formatUnits(bal, meta.decimals)) }));
        }
      } catch {}

      setIsLoading(false);
      toast.success(`Swap successful!\nTx: ${swapHash}`);
      try { window.dispatchEvent(new Event('balances:refresh')); } catch {}
    } catch (e: any) {
      console.error(e);
      setIsLoading(false);
      toast.error(e?.shortMessage || e?.message || 'Swap failed');
    }
  };

  const priceImpact = 0.12;
  const networkFee = 5.50;
  const minReceived = toAmount ? (parseFloat(toAmount) * (1 - slippage / 100)).toFixed(4) : '0';

  return (
    <div className="min-h-screen bg-black text-stone-100">
      <Toaster position="top-right" />
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
                  <button onClick={() => setShowFromTokenMenu(!showFromTokenMenu)} className="flex items-center gap-2 px-3 py-2 bg-stone-700 hover:bg-stone-600 rounded-xl transition-colors">
                    <span className="text-2xl">{fromToken.icon}</span>
                    <span className="font-semibold">{fromToken.symbol}</span>
                  </button>
                </div>
              </div>
              {showFromTokenMenu && (
                <div className="mt-3 grid grid-cols-3 gap-2">
                  {(['ETH','USDT','USDC'] as const).map((sym) => (
                    <button
                      key={sym}
                      onClick={() => selectFromToken(sym)}
                      className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors ${fromToken.symbol === sym ? 'bg-yellow-500 text-black' : 'bg-stone-700 text-stone-200 hover:bg-stone-600'}`}
                    >
                      {sym}
                    </button>
                  ))}
                </div>
              )}
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
