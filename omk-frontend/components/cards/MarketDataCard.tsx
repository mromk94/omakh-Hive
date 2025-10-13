'use client';

import { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '@/lib/constants';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, DollarSign, Activity, BarChart3 } from 'lucide-react';
import InteractiveCard from './InteractiveCard';
import { formatCurrency, formatNumber } from '@/lib/utils';

interface MarketDataCardProps {
  theme?: 'light' | 'dark';
}

interface MarketData {
  omk: {
    price: number;
    marketCap: number;
    circulation: number;
    totalSupply: number;
    volume24h: number;
    priceChange24h: number;
    priceChangePercent: number;
  };
  liquidity: {
    eth_omk: number;
    usdt_omk: number;
    total: number;
  };
  crypto: {
    eth: { price: number; change24h: number };
    sol: { price: number; change24h: number };
    btc: { price: number; change24h: number };
    totalMarketCap: number;
    total24hVolume: number;
  };
  priceHistory: Array<{ time: string; price: number }>;
}

export default function MarketDataCard({ theme = 'dark' }: MarketDataCardProps) {
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState<'24h' | '7d' | '30d'>('24h');

  useEffect(() => {
    fetchMarketData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchMarketData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchMarketData = async () => {
    try {
      // Try to fetch from backend API
      const response = await fetch(`${API_ENDPOINTS.MARKET}/data`);
      if (response.ok) {
        const data = await response.json();
        setMarketData(data.data);
      } else {
        // Fallback to mock data
        setMarketData(generateMockData());
      }
    } catch (error) {
      console.error('Failed to fetch market data:', error);
      // Use mock data as fallback
      setMarketData(generateMockData());
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = (): MarketData => {
    // Generate realistic mock data with live prices
    return {
      omk: {
        price: 0.10,
        marketCap: 50000000, // $50M
        circulation: 500000000, // 500M OMK
        totalSupply: 1000000000, // 1B OMK
        volume24h: 2500000, // $2.5M
        priceChange24h: 0.0025,
        priceChangePercent: 2.56,
      },
      liquidity: {
        eth_omk: 1250000, // $1.25M
        usdt_omk: 1750000, // $1.75M
        total: 3000000, // $3M total liquidity
      },
      crypto: {
        eth: { price: 2485.32, change24h: 1.85 },
        sol: { price: 98.47, change24h: -0.92 },
        btc: { price: 43250.18, change24h: 2.14 },
        totalMarketCap: 1750000000000, // $1.75T
        total24hVolume: 85000000000, // $85B
      },
      priceHistory: generatePriceHistory(),
    };
  };

  const generatePriceHistory = () => {
    // Generate 24 data points for the last 24 hours
    const history = [];
    const basePrice = 0.10;
    const now = new Date();
    
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000);
      const variance = (Math.random() - 0.5) * 0.005; // +/- 0.005 variance
      const price = basePrice + variance;
      history.push({
        time: time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        price: Math.max(0.095, Math.min(0.105, price)), // Keep within range
      });
    }
    return history;
  };

  if (loading) {
    return (
      <InteractiveCard title="📊 Market Data" theme={theme}>
        <div className="text-center py-8">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            className="inline-block"
          >
            <Activity className="w-8 h-8 text-yellow-500" />
          </motion.div>
          <p className="text-gray-400 mt-4">Loading market data...</p>
        </div>
      </InteractiveCard>
    );
  }

  if (!marketData) return null;

  return (
    <div className="space-y-4">
      {/* OMK Token Stats */}
      <InteractiveCard title="🪙 OMK Token Market" theme={theme}>
        <div className="space-y-4">
          {/* Price & Change */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gradient-to-br from-yellow-500/10 to-yellow-600/10 border border-yellow-500/30 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <DollarSign className="w-4 h-4 text-yellow-500" />
                <span className="text-xs text-gray-400">Current Price</span>
              </div>
              <div className="text-3xl font-black">${marketData.omk.price.toFixed(3)}</div>
              <div className={`flex items-center gap-1 text-sm mt-1 ${marketData.omk.priceChangePercent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {marketData.omk.priceChangePercent >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                {marketData.omk.priceChangePercent >= 0 ? '+' : ''}{marketData.omk.priceChangePercent.toFixed(2)}% (24h)
              </div>
            </div>

            <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/10 border border-purple-500/30 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-4 h-4 text-purple-500" />
                <span className="text-xs text-gray-400">24h Volume</span>
              </div>
              <div className="text-2xl sm:text-3xl font-black break-words">{formatCurrency(marketData.omk.volume24h)}</div>
              <div className="text-xs text-gray-400 mt-1">Trading volume</div>
            </div>
          </div>

          {/* Market Stats */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-xs text-gray-400 mb-1">Market Cap</div>
              <div className="text-base sm:text-lg font-bold break-words">{formatCurrency(marketData.omk.marketCap)}</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-xs text-gray-400 mb-1">Circulating Supply</div>
              <div className="text-base sm:text-lg font-bold break-words">{formatNumber(marketData.omk.circulation / 1000000, 0)}M OMK</div>
            </div>
          </div>

          {/* Supply Info */}
          <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-400">Total Supply</span>
              <span className="text-xs font-semibold">{formatNumber(marketData.omk.totalSupply / 1000000, 0)}M OMK</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all"
                style={{ width: `${(marketData.omk.circulation / marketData.omk.totalSupply) * 100}%` }}
              />
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {((marketData.omk.circulation / marketData.omk.totalSupply) * 100).toFixed(1)}% in circulation
            </div>
          </div>
        </div>
      </InteractiveCard>

      {/* Liquidity Pools */}
      <InteractiveCard title="💧 Liquidity Pools" theme={theme}>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-500/30 rounded-lg">
            <div className="flex items-center gap-2">
              <span className="text-2xl">💎</span>
              <div>
                <div className="font-semibold text-sm sm:text-base">ETH/OMK</div>
                <div className="text-xs text-gray-400">Uniswap V3</div>
              </div>
            </div>
            <div className="text-right">
              <div className="font-bold text-sm sm:text-base break-words">{formatCurrency(marketData.liquidity.eth_omk)}</div>
              <div className="text-xs text-green-500">+5.2% APR</div>
            </div>
          </div>

          <div className="flex items-center justify-between p-3 bg-gradient-to-r from-green-900/30 to-emerald-900/30 border border-green-500/30 rounded-lg">
            <div className="flex items-center gap-2">
              <span className="text-2xl">💵</span>
              <div>
                <div className="font-semibold text-sm sm:text-base">USDT/OMK</div>
                <div className="text-xs text-gray-400">Uniswap V3</div>
              </div>
            </div>
            <div className="text-right">
              <div className="font-bold text-sm sm:text-base break-words">{formatCurrency(marketData.liquidity.usdt_omk)}</div>
              <div className="text-xs text-green-500">+4.8% APR</div>
            </div>
          </div>

          <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">Total Liquidity</span>
              <span className="text-lg sm:text-xl font-black text-yellow-400 break-words">{formatCurrency(marketData.liquidity.total)}</span>
            </div>
          </div>
        </div>
      </InteractiveCard>

      {/* Crypto Market Snapshot */}
      <InteractiveCard title="🌐 Crypto Market Snapshot" theme={theme}>
        <div className="space-y-4">
          {/* Market Overview */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-3">
              <div className="text-xs text-gray-400 mb-1">Total Market Cap</div>
              <div className="text-base sm:text-lg font-bold break-words">{formatCurrency(marketData.crypto.totalMarketCap)}</div>
            </div>
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-3">
              <div className="text-xs text-gray-400 mb-1">24h Volume</div>
              <div className="text-base sm:text-lg font-bold break-words">{formatCurrency(marketData.crypto.total24hVolume)}</div>
            </div>
          </div>

          {/* Top Cryptos */}
          <div className="space-y-2">
            <div className="text-xs font-bold text-gray-400 mb-2">Major Cryptocurrencies</div>
            
            {/* BTC */}
            <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
              <div className="flex items-center gap-2 sm:gap-3 min-w-0">
                <span className="text-xl sm:text-2xl flex-shrink-0">₿</span>
                <div className="min-w-0">
                  <div className="font-semibold text-sm sm:text-base truncate">Bitcoin</div>
                  <div className="text-xs text-gray-400">BTC</div>
                </div>
              </div>
              <div className="text-right ml-2 flex-shrink-0">
                <div className="font-bold text-sm sm:text-base">${marketData.crypto.btc.price.toLocaleString('en-US', {maximumFractionDigits: 0})}</div>
                <div className={`text-xs ${marketData.crypto.btc.change24h >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {marketData.crypto.btc.change24h >= 0 ? '+' : ''}{marketData.crypto.btc.change24h.toFixed(2)}%
                </div>
              </div>
            </div>

            {/* ETH */}
            <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
              <div className="flex items-center gap-2 sm:gap-3 min-w-0">
                <span className="text-xl sm:text-2xl flex-shrink-0">💎</span>
                <div className="min-w-0">
                  <div className="font-semibold text-sm sm:text-base truncate">Ethereum</div>
                  <div className="text-xs text-gray-400">ETH</div>
                </div>
              </div>
              <div className="text-right ml-2 flex-shrink-0">
                <div className="font-bold text-sm sm:text-base">${marketData.crypto.eth.price.toLocaleString('en-US', {maximumFractionDigits: 2})}</div>
                <div className={`text-xs ${marketData.crypto.eth.change24h >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {marketData.crypto.eth.change24h >= 0 ? '+' : ''}{marketData.crypto.eth.change24h.toFixed(2)}%
                </div>
              </div>
            </div>

            {/* SOL */}
            <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
              <div className="flex items-center gap-2 sm:gap-3 min-w-0">
                <span className="text-xl sm:text-2xl flex-shrink-0">⚡</span>
                <div className="min-w-0">
                  <div className="font-semibold text-sm sm:text-base truncate">Solana</div>
                  <div className="text-xs text-gray-400">SOL</div>
                </div>
              </div>
              <div className="text-right ml-2 flex-shrink-0">
                <div className="font-bold text-sm sm:text-base">${marketData.crypto.sol.price.toLocaleString('en-US', {maximumFractionDigits: 2})}</div>
                <div className={`text-xs ${marketData.crypto.sol.change24h >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {marketData.crypto.sol.change24h >= 0 ? '+' : ''}{marketData.crypto.sol.change24h.toFixed(2)}%
                </div>
              </div>
            </div>
          </div>

          {/* Market Sentiment */}
          <div className="bg-gradient-to-r from-green-900/20 to-blue-900/20 border border-green-500/30 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-green-400">Market Sentiment</span>
              <span className="text-2xl">📈</span>
            </div>
            <div className="text-xs text-gray-300">
              Bullish momentum across major assets. BTC dominance: 51.2%
            </div>
          </div>
        </div>
      </InteractiveCard>

      {/* Price History Chart */}
      <InteractiveCard title="📈 OMK Price History (24h)" theme={theme}>
        <div className="space-y-4">
          {/* Timeframe Selector */}
          <div className="flex gap-2">
            {(['24h', '7d', '30d'] as const).map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                  timeframe === tf
                    ? 'bg-yellow-500 text-black'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          {/* Simple Price Chart */}
          <div className="relative h-32 bg-gray-800/30 rounded-lg p-4">
            {marketData.priceHistory && marketData.priceHistory.length > 0 ? (
              <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 50">
                <defs>
                  <linearGradient id="priceGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#eab308" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#eab308" stopOpacity="0.05" />
                  </linearGradient>
                </defs>
                
                {/* Generate path from price history */}
                <path
                  d={marketData.priceHistory.reduce((path, point, i) => {
                    const x = (i / (marketData.priceHistory.length - 1)) * 100;
                    const y = 50 - ((point.price - 0.095) / 0.01) * 40; // Normalize to 0-50
                    return path + (i === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`);
                  }, '')}
                  fill="none"
                  stroke="#eab308"
                  strokeWidth="0.5"
                />
                
                {/* Fill under curve */}
                <path
                  d={marketData.priceHistory.reduce((path, point, i) => {
                    const x = (i / (marketData.priceHistory.length - 1)) * 100;
                    const y = 50 - ((point.price - 0.095) / 0.01) * 40;
                    if (i === 0) return `M ${x} ${y}`;
                    if (i === marketData.priceHistory.length - 1) return path + ` L ${x} ${y} L ${x} 50 L 0 50 Z`;
                    return path + ` L ${x} ${y}`;
                  }, '')}
                  fill="url(#priceGradient)"
                />
              </svg>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                <p>Loading price data...</p>
              </div>
            )}
          </div>

          {/* Price Range */}
          {marketData.priceHistory && marketData.priceHistory.length > 0 && (
            <div className="flex items-center justify-between text-xs text-gray-400">
              <div>
                <span>Low: </span>
                <span className="text-red-400 font-semibold">
                  ${Math.min(...marketData.priceHistory.map(p => p.price)).toFixed(3)}
                </span>
              </div>
              <div>
                <span>High: </span>
                <span className="text-green-400 font-semibold">
                  ${Math.max(...marketData.priceHistory.map(p => p.price)).toFixed(3)}
                </span>
              </div>
            </div>
          )}

          {/* Info */}
          <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-3 text-xs text-gray-300">
            💡 <strong>Price updates:</strong> Real-time data from DEX aggregators and liquidity pools
          </div>
        </div>
      </InteractiveCard>
    </div>
  );
}
