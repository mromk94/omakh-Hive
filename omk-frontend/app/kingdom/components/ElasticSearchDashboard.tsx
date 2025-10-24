'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, MessageSquare, Sparkles, Activity, FileText,
  TrendingUp, Filter, Send, Loader
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { API_ENDPOINTS } from '../../../lib/constants';

const BACKEND_URL = 'http://localhost:8001';

interface SearchResult {
  bee_name: string;
  action: string;
  timestamp: string;
  success: boolean;
  tx_hash?: string;
  chain?: string;
  _score: number;
}

interface RAGResponse {
  answer: string;
  context: any[];
  sources: string[];
}

export default function ElasticSearchDashboard() {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [ragResponse, setRagResponse] = useState<RAGResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchType, setSearchType] = useState<'search' | 'rag'>('search');
  const [recentActivities, setRecentActivities] = useState<SearchResult[]>([]);
  const [filterBee, setFilterBee] = useState<string>('all');

  useEffect(() => {
    loadRecentActivities();
  }, []);

  const loadRecentActivities = async () => {
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${API_ENDPOINTS.ADMIN}/elastic/recent`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) return;

      const data = await response.json();
      if (data.success) {
        setRecentActivities(data.activities || []);
      }
    } catch (error: any) {
      console.error('Failed to load recent activities:', error);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const endpoint = searchType === 'rag' 
        ? `${API_ENDPOINTS.ADMIN}/elastic/rag`
        : `${API_ENDPOINTS.ADMIN}/elastic/search`;

      const filters = filterBee !== 'all' ? { bee_name: filterBee } : undefined;

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          query,
          filters,
          size: 10
        })
      });

      if (!response.ok) throw new Error('Search failed');

      const data = await response.json();
      
      if (searchType === 'rag') {
        setRagResponse(data);
        setSearchResults([]);
      } else {
        setSearchResults(data.results || []);
        setRagResponse(null);
      }
    } catch (error: any) {
      console.error('Search error:', error);
      toast.error('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Search className="w-6 h-6 text-green-400" />
          Elastic Search Dashboard
        </h2>
        <p className="text-gray-400 mt-1">Hybrid search & RAG-powered answers</p>
      </div>

      {/* Search Box */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-800/50 backdrop-blur border border-gray-700 rounded-xl p-6"
      >
        {/* Search Type Tabs */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setSearchType('search')}
            className={`
              px-4 py-2 rounded-lg font-medium flex items-center gap-2
              ${searchType === 'search' 
                ? 'bg-green-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}
            `}
          >
            <Search className="w-4 h-4" />
            Hybrid Search
          </button>
          <button
            onClick={() => setSearchType('rag')}
            className={`
              px-4 py-2 rounded-lg font-medium flex items-center gap-2
              ${searchType === 'rag' 
                ? 'bg-purple-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}
            `}
          >
            <Sparkles className="w-4 h-4" />
            RAG Query
          </button>
        </div>

        {/* Search Input */}
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              searchType === 'rag' 
                ? 'Ask a question... (e.g., "Why did the last bridge transaction fail?")'
                : 'Search bee activities... (e.g., "failed transactions", "uniswap swaps")'
            }
            className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 pr-24"
          />
          <button
            onClick={handleSearch}
            disabled={loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg font-medium disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            Search
          </button>
        </div>

        {/* Filters */}
        {searchType === 'search' && (
          <div className="mt-4">
            <label className="text-gray-400 text-sm block mb-2">Filter by Bee:</label>
            <select
              value={filterBee}
              onChange={(e) => setFilterBee(e.target.value)}
              className="px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white"
            >
              <option value="all">All Bees</option>
              <option value="BlockchainBee">Blockchain Bee</option>
              <option value="BridgeBee">Bridge Bee</option>
              <option value="SwapBee">Swap Bee</option>
              <option value="LiquidityBee">Liquidity Bee</option>
              <option value="LiquiditySentinelBee">Liquidity Sentinel Bee</option>
              <option value="SecurityBee">Security Bee</option>
              <option value="EnhancedSecurityBee">Enhanced Security Bee</option>
              <option value="DataBee">Data Bee</option>
              <option value="DataPipelineBee">Data Pipeline Bee</option>
              <option value="TradingBee">Trading Bee</option>
              <option value="GasPriceBee">Gas Price Bee</option>
              <option value="NotificationBee">Notification Bee</option>
              <option value="AnalyticsBee">Analytics Bee</option>
              <option value="GovernanceBee">Governance Bee</option>
              <option value="PropertyManagementBee">Property Management Bee</option>
              <option value="StakingBee">Staking Bee</option>
            </select>
          </div>
        )}
      </motion.div>

      {/* RAG Response */}
      <AnimatePresence>
        {ragResponse && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-gradient-to-r from-purple-900/20 to-pink-900/20 border border-purple-500/50 rounded-xl p-6"
          >
            <div className="flex items-start gap-3">
              <Sparkles className="w-6 h-6 text-purple-400 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h3 className="text-white font-bold mb-3">AI-Powered Answer:</h3>
                <p className="text-gray-300 whitespace-pre-wrap">{ragResponse.answer}</p>
                
                {ragResponse.sources.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-purple-500/30">
                    <p className="text-gray-400 text-sm">
                      <strong>Sources:</strong> {ragResponse.sources.join(', ')}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Search Results */}
      <AnimatePresence>
        {searchResults.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-3"
          >
            <h3 className="text-white font-bold flex items-center gap-2">
              <FileText className="w-5 h-5 text-green-400" />
              Search Results ({searchResults.length})
            </h3>

            {searchResults.map((result, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-gray-800/50 backdrop-blur border border-gray-700 rounded-xl p-4 hover:border-green-500/50 transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-1 bg-green-600/20 text-green-400 text-xs font-medium rounded">
                        {result.bee_name}
                      </span>
                      {result.success ? (
                        <span className="px-2 py-1 bg-emerald-600/20 text-emerald-400 text-xs font-medium rounded">
                          Success
                        </span>
                      ) : (
                        <span className="px-2 py-1 bg-red-600/20 text-red-400 text-xs font-medium rounded">
                          Failed
                        </span>
                      )}
                      {result.chain && (
                        <span className="px-2 py-1 bg-blue-600/20 text-blue-400 text-xs font-medium rounded">
                          {result.chain}
                        </span>
                      )}
                    </div>
                    
                    <p className="text-white font-medium">{result.action}</p>
                    
                    {result.tx_hash && (
                      <p className="text-gray-400 text-sm mt-1 font-mono">
                        TX: {result.tx_hash.substring(0, 10)}...
                      </p>
                    )}
                    
                    <p className="text-gray-500 text-xs mt-2">
                      {new Date(result.timestamp).toLocaleString()}
                    </p>
                  </div>

                  <div className="text-right">
                    <p className="text-gray-400 text-xs">Relevance</p>
                    <p className="text-green-400 font-bold">
                      {(result._score * 10).toFixed(1)}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Recent Activities */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-gray-800/50 backdrop-blur border border-gray-700 rounded-xl p-6"
      >
        <h3 className="text-white font-bold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-400" />
          Recent Bee Activities
        </h3>

        {recentActivities.length === 0 ? (
          <p className="text-gray-400 text-center py-8">
            No recent activities. Run the data pipeline to populate Elastic Search.
          </p>
        ) : (
          <div className="space-y-2">
            {recentActivities.slice(0, 5).map((activity, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${activity.success ? 'bg-green-400' : 'bg-red-400'}`} />
                  <div>
                    <p className="text-white text-sm">{activity.bee_name}</p>
                    <p className="text-gray-400 text-xs">{activity.action}</p>
                  </div>
                </div>
                <p className="text-gray-500 text-xs">
                  {new Date(activity.timestamp).toLocaleTimeString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </motion.div>

      {/* Info Box */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-gradient-to-r from-green-900/20 to-emerald-900/20 border border-green-500/50 rounded-xl p-6"
      >
        <div className="flex items-start gap-3">
          <TrendingUp className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
          <div>
            <h4 className="text-white font-bold mb-2">Elastic Search Features</h4>
            <ul className="text-gray-300 text-sm space-y-1">
              <li>• <strong>Hybrid Search:</strong> Combines vector (semantic) + keyword search</li>
              <li>• <strong>RAG Query:</strong> AI-powered answers using Gemini + Elastic context</li>
              <li>• <strong>Bee Monitoring:</strong> Track all bee activities in real-time</li>
              <li>• <strong>Transaction Search:</strong> Find specific transactions by hash, address, or chain</li>
              <li>• <strong>Natural Language:</strong> Ask questions like "Why did it fail?"</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
