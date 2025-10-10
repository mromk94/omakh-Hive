'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Home, Wallet, Clock, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { useAccount } from 'wagmi';
import { useRouter } from 'next/navigation';
import { formatCurrency, formatNumber } from '@/lib/utils';

interface PortfolioStats {
  totalValue: number;
  cryptoValue: number;
  realEstateValue: number;
  change24h: number;
  changePercent: number;
}

interface Holding {
  type: 'crypto' | 'real-estate';
  name: string;
  symbol: string;
  amount: number;
  value: number;
  change24h: number;
  icon: string;
}

interface Transaction {
  id: string;
  type: 'buy' | 'sell' | 'receive' | 'send';
  asset: string;
  amount: number;
  value: number;
  timestamp: Date;
  status: 'completed' | 'pending';
}

export default function DashboardPage() {
  const { address, isConnected } = useAccount();
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  // Mock data - replace with actual API calls
  const [portfolio, setPortfolio] = useState<PortfolioStats>({
    totalValue: 5250.00,
    cryptoValue: 2500.00,
    realEstateValue: 2750.00,
    change24h: 125.50,
    changePercent: 2.45,
  });

  const [holdings, setHoldings] = useState<Holding[]>([
    {
      type: 'crypto',
      name: 'Ethereum',
      symbol: 'ETH',
      amount: 0.5,
      value: 1250.00,
      change24h: 2.3,
      icon: '💎',
    },
    {
      type: 'crypto',
      name: 'OMK Token',
      symbol: 'OMK',
      amount: 10000,
      value: 1000.00,
      change24h: 5.2,
      icon: '🟡',
    },
    {
      type: 'crypto',
      name: 'USDC',
      symbol: 'USDC',
      amount: 250,
      value: 250.00,
      change24h: 0,
      icon: '💵',
    },
    {
      type: 'real-estate',
      name: 'Dubai Marina Apartment',
      symbol: 'Blocks',
      amount: 10,
      value: 1500.00,
      change24h: 1.2,
      icon: '🏢',
    },
    {
      type: 'real-estate',
      name: 'London Commercial Property',
      symbol: 'Blocks',
      amount: 5,
      value: 1250.00,
      change24h: 0.8,
      icon: '🏛️',
    },
  ]);

  const [transactions, setTransactions] = useState<Transaction[]>([
    {
      id: '1',
      type: 'buy',
      asset: 'OMK',
      amount: 1000,
      value: 100.00,
      timestamp: new Date(Date.now() - 3600000),
      status: 'completed',
    },
    {
      id: '2',
      type: 'buy',
      asset: 'Dubai Marina - 10 Blocks',
      amount: 10,
      value: 1500.00,
      timestamp: new Date(Date.now() - 7200000),
      status: 'completed',
    },
  ]);

  useEffect(() => {
    if (!isConnected) {
      router.push('/connect');
      return;
    }

    // Simulate loading
    setTimeout(() => setLoading(false), 1000);
  }, [isConnected, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360, scale: [1, 1.2, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="text-6xl"
        >
          👑
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-stone-100">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl md:text-4xl font-black mb-2">
            <span className="bg-gradient-to-r from-yellow-500 to-yellow-600 bg-clip-text text-transparent">
              Dashboard
            </span>
          </h1>
          <p className="text-stone-400">
            Welcome back! Here's your portfolio overview.
          </p>
        </motion.div>

        {/* Portfolio Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Total Value */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-stone-900 to-black p-6 rounded-2xl border border-yellow-500/30"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-stone-400">Total Portfolio</span>
              <Wallet className="w-5 h-5 text-yellow-500" />
            </div>
            <div className="text-3xl font-bold text-stone-100 mb-2">
              {formatCurrency(portfolio.totalValue)}
            </div>
            <div className={`flex items-center gap-1 text-sm ${portfolio.change24h >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {portfolio.change24h >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              {formatCurrency(Math.abs(portfolio.change24h))} ({portfolio.changePercent.toFixed(2)}%) 24h
            </div>
          </motion.div>

          {/* Crypto Holdings */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-stone-900 to-black p-6 rounded-2xl border border-yellow-500/30"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-stone-400">Crypto Assets</span>
              <span className="text-2xl">💎</span>
            </div>
            <div className="text-3xl font-bold text-stone-100 mb-2">
              {formatCurrency(portfolio.cryptoValue)}
            </div>
            <div className="text-sm text-stone-400">
              {holdings.filter(h => h.type === 'crypto').length} tokens
            </div>
          </motion.div>

          {/* Real Estate */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-stone-900 to-black p-6 rounded-2xl border border-yellow-500/30"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-stone-400">Real Estate</span>
              <Home className="w-5 h-5 text-yellow-500" />
            </div>
            <div className="text-3xl font-bold text-stone-100 mb-2">
              {formatCurrency(portfolio.realEstateValue)}
            </div>
            <div className="text-sm text-stone-400">
              {holdings.filter(h => h.type === 'real-estate').length} properties
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Holdings List */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-gradient-to-br from-stone-900 to-black p-6 rounded-2xl border border-yellow-500/30"
            >
              <h2 className="text-xl font-bold text-stone-100 mb-6">Your Holdings</h2>
              
              <div className="space-y-3">
                {holdings.map((holding, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.05 }}
                    className="flex items-center justify-between p-4 bg-stone-800/50 hover:bg-stone-800 rounded-xl transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-3xl">{holding.icon}</span>
                      <div>
                        <div className="font-semibold text-stone-100">{holding.name}</div>
                        <div className="text-sm text-stone-400">
                          {formatNumber(holding.amount, holding.type === 'crypto' && holding.symbol !== 'USDC' ? 4 : 0)} {holding.symbol}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-stone-100">
                        {formatCurrency(holding.value)}
                      </div>
                      <div className={`text-sm flex items-center gap-1 justify-end ${holding.change24h >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {holding.change24h >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                        {holding.change24h.toFixed(2)}%
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              <div className="mt-6 grid grid-cols-2 gap-3">
                <button className="px-4 py-3 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-black font-semibold rounded-xl transition-all">
                  Buy OMK
                </button>
                <button className="px-4 py-3 bg-stone-800 hover:bg-stone-700 text-stone-100 font-semibold rounded-xl transition-all border border-yellow-500/30">
                  Invest in Property
                </button>
              </div>
            </motion.div>
          </div>

          {/* Recent Activity */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-gradient-to-br from-stone-900 to-black p-6 rounded-2xl border border-yellow-500/30"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-stone-100">Recent Activity</h2>
                <Clock className="w-5 h-5 text-yellow-500" />
              </div>

              <div className="space-y-4">
                {transactions.map((tx) => (
                  <div
                    key={tx.id}
                    className="flex items-start gap-3 pb-4 border-b border-stone-800 last:border-0"
                  >
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      tx.type === 'buy' ? 'bg-green-500/20 text-green-500' : 'bg-blue-500/20 text-blue-500'
                    }`}>
                      {tx.type === 'buy' ? '↓' : '↑'}
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold text-stone-100 text-sm">
                        {tx.type.charAt(0).toUpperCase() + tx.type.slice(1)} {tx.asset}
                      </div>
                      <div className="text-xs text-stone-400">
                        {tx.timestamp.toLocaleString()}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-stone-100 text-sm">
                        {formatCurrency(tx.value)}
                      </div>
                      <div className={`text-xs ${tx.status === 'completed' ? 'text-green-500' : 'text-yellow-500'}`}>
                        {tx.status}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <button className="w-full mt-4 px-4 py-2 bg-stone-800/50 hover:bg-stone-800 text-stone-300 text-sm font-semibold rounded-lg transition-colors">
                View All Transactions
              </button>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
