'use client';

import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Home, Wallet } from 'lucide-react';
import { useAccount, useBalance } from 'wagmi';
import InteractiveCard from './InteractiveCard';
import { formatCurrency, formatNumber } from '@/lib/utils';

interface DashboardCardProps {
  theme?: 'light' | 'dark';
  demoMode?: boolean;
}

export default function DashboardCard({ theme = 'dark', demoMode = false }: DashboardCardProps) {
  const { address, isConnected } = useAccount();
  const { data: ethBalance } = useBalance({ address: address as `0x${string}` });

  // Mock data - replace with real API calls
  const portfolio = {
    totalValue: 5250.00,
    cryptoValue: 2500.00,
    realEstateValue: 2750.00,
    change24h: 125.50,
    changePercent: 2.45,
  };

  const holdings = [
    { name: 'Ethereum', symbol: 'ETH', amount: ethBalance ? parseFloat(ethBalance.formatted) : 0.5, value: 1250, icon: '💎' },
    { name: 'OMK Token', symbol: 'OMK', amount: 10000, value: 1000, icon: '🟡' },
    { name: 'Dubai Apartment', symbol: 'Blocks', amount: 10, value: 1500, icon: '🏢' },
  ];

  // Show demo data if demoMode or not connected
  if (!isConnected && !demoMode) {
    return (
      <InteractiveCard title="📊 Portfolio Dashboard" theme={theme}>
        <div className="text-center py-8">
          <div className="text-6xl mb-4">🔐</div>
          <p className="text-gray-400 mb-4">Connect your wallet to view your portfolio</p>
          <button className="px-6 py-3 bg-gradient-to-r from-yellow-500 to-yellow-600 text-black font-bold rounded-xl">
            Connect Wallet
          </button>
        </div>
      </InteractiveCard>
    );
  }

  return (
    <InteractiveCard title="📊 Your Portfolio" theme={theme}>
      <div className="space-y-4">
        {/* Total Value */}
        <div className="bg-gradient-to-br from-yellow-500/10 to-yellow-600/10 border border-yellow-500/30 rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Total Portfolio</span>
            <Wallet className="w-5 h-5 text-yellow-500" />
          </div>
          <div className="text-4xl font-black mb-2">{formatCurrency(portfolio.totalValue)}</div>
          <div className={`flex items-center gap-1 text-sm ${portfolio.change24h >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {portfolio.change24h >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            {formatCurrency(Math.abs(portfolio.change24h))} ({portfolio.changePercent.toFixed(2)}%) 24h
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-800/50 rounded-xl p-4">
            <div className="text-2xl mb-1">💎</div>
            <div className="text-xs text-gray-400 mb-1">Crypto Assets</div>
            <div className="text-xl font-bold">{formatCurrency(portfolio.cryptoValue)}</div>
          </div>
          <div className="bg-gray-800/50 rounded-xl p-4">
            <div className="text-2xl mb-1">🏠</div>
            <div className="text-xs text-gray-400 mb-1">Real Estate</div>
            <div className="text-xl font-bold">{formatCurrency(portfolio.realEstateValue)}</div>
          </div>
        </div>

        {/* Holdings */}
        <div>
          <h3 className="text-sm font-bold mb-3 text-gray-400">Your Holdings</h3>
          <div className="space-y-2">
            {holdings.map((holding, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-center justify-between p-3 bg-gray-800/50 hover:bg-gray-800 rounded-xl transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{holding.icon}</span>
                  <div>
                    <div className="font-semibold">{holding.name}</div>
                    <div className="text-sm text-gray-400">
                      {formatNumber(holding.amount, holding.symbol === 'ETH' ? 4 : 0)} {holding.symbol}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-semibold">{formatCurrency(holding.value)}</div>
                  <div className="text-xs text-green-500">+2.3%</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="grid grid-cols-2 gap-3 pt-4">
          <button className="px-4 py-3 bg-gradient-to-r from-yellow-500 to-yellow-600 text-black font-semibold rounded-xl">
            Buy OMK
          </button>
          <button className="px-4 py-3 bg-gray-800 hover:bg-gray-700 text-white font-semibold rounded-xl border border-gray-600">
            Invest More
          </button>
        </div>
      </div>
    </InteractiveCard>
  );
}
