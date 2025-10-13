'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, TrendingUp, DollarSign, Activity, Database,
  Play, Download, Code, Zap, AlertCircle
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const BACKEND_URL = 'http://localhost:8001';

interface QueryResult {
  columns: string[];
  rows: any[][];
  row_count: number;
}

interface PrebuiltQuery {
  id: string;
  name: string;
  description: string;
  query: string;
  icon: any;
  color: string;
}

const PREBUILT_QUERIES: PrebuiltQuery[] = [
  {
    id: 'gas_trends',
    name: 'Gas Price Trends (7 days)',
    description: 'Average gas prices on Ethereum',
    icon: TrendingUp,
    color: 'blue',
    query: `
SELECT 
  DATE(block_timestamp) as date,
  AVG(gas_price_gwei) as avg_gas,
  MAX(gas_price_gwei) as max_gas,
  MIN(gas_price_gwei) as min_gas,
  COUNT(*) as tx_count
FROM \`omk-hive-prod.fivetran_blockchain_data.ethereum_transactions\`
WHERE block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY date
ORDER BY date DESC
LIMIT 7
    `.trim()
  },
  {
    id: 'dex_volume',
    name: 'DEX Trading Volume',
    description: 'Top 10 pools by 24h volume',
    icon: BarChart3,
    color: 'green',
    query: `
SELECT 
  pool_address,
  token0_symbol,
  token1_symbol,
  SUM(total_liquidity_usd) as total_liquidity,
  dex
FROM \`omk-hive-prod.fivetran_blockchain_data.dex_pools\`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
GROUP BY pool_address, token0_symbol, token1_symbol, dex
ORDER BY total_liquidity DESC
LIMIT 10
    `.trim()
  },
  {
    id: 'transaction_status',
    name: 'Transaction Success Rate',
    description: 'Success vs failed transactions',
    icon: Activity,
    color: 'purple',
    query: `
SELECT 
  status,
  COUNT(*) as count,
  AVG(gas_used) as avg_gas_used
FROM \`omk-hive-prod.fivetran_blockchain_data.ethereum_transactions\`
WHERE block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY status
    `.trim()
  },
  {
    id: 'price_feeds',
    name: 'Oracle Price Feeds',
    description: 'Latest prices from Chainlink',
    icon: DollarSign,
    color: 'yellow',
    query: `
SELECT 
  pair,
  price,
  updated_at,
  round_id
FROM \`omk-hive-prod.fivetran_blockchain_data.chainlink_prices\`
WHERE round_id IN (
  SELECT MAX(round_id)
  FROM \`omk-hive-prod.fivetran_blockchain_data.chainlink_prices\`
  GROUP BY pair
)
ORDER BY pair
    `.trim()
  }
];

export default function BigQueryAnalytics() {
  const [selectedQuery, setSelectedQuery] = useState<PrebuiltQuery | null>(null);
  const [customQuery, setCustomQuery] = useState('');
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [showCustomEditor, setShowCustomEditor] = useState(false);

  const executeQuery = async (query: string) => {
    setLoading(true);

    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/admin/bigquery/query`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
      });

      if (!response.ok) throw new Error('Query failed');

      const data = await response.json();
      
      if (data.success) {
        setQueryResult(data.result);
        toast.success(`Query executed: ${data.result.row_count} rows`);
      } else {
        toast.error(data.error || 'Query failed');
      }
    } catch (error: any) {
      console.error('Query error:', error);
      toast.error('Failed to execute query');
    } finally {
      setLoading(false);
    }
  };

  const handlePrebuiltQuery = (query: PrebuiltQuery) => {
    setSelectedQuery(query);
    setShowCustomEditor(false);
    executeQuery(query.query);
  };

  const handleCustomQuery = () => {
    if (!customQuery.trim()) {
      toast.error('Please enter a query');
      return;
    }
    executeQuery(customQuery);
  };

  const exportToCSV = () => {
    if (!queryResult) return;

    const csv = [
      queryResult.columns.join(','),
      ...queryResult.rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bigquery_export_${Date.now()}.csv`;
    a.click();
    
    toast.success('Exported to CSV');
  };

  // Convert query results to chart data
  const getChartData = () => {
    if (!queryResult || queryResult.rows.length === 0) return [];

    return queryResult.rows.map((row) => {
      const obj: any = {};
      queryResult.columns.forEach((col, index) => {
        obj[col] = row[index];
      });
      return obj;
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Database className="w-6 h-6 text-blue-400" />
          BigQuery Analytics
        </h2>
        <p className="text-gray-400 mt-1">Query blockchain data from BigQuery</p>
      </div>

      {/* Pre-built Queries */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {PREBUILT_QUERIES.map((query) => {
          const Icon = query.icon;
          return (
            <motion.button
              key={query.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handlePrebuiltQuery(query)}
              className={`
                p-6 rounded-xl text-left
                bg-gray-800/50 backdrop-blur border border-gray-700
                hover:border-${query.color}-500/50 transition-all
              `}
            >
              <div className="flex items-start gap-3">
                <div className={`p-3 rounded-lg bg-${query.color}-600/20`}>
                  <Icon className={`w-6 h-6 text-${query.color}-400`} />
                </div>
                <div className="flex-1">
                  <h3 className="text-white font-bold">{query.name}</h3>
                  <p className="text-gray-400 text-sm mt-1">{query.description}</p>
                </div>
              </div>
            </motion.button>
          );
        })}
      </div>

      {/* Custom Query Editor */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-800/50 backdrop-blur border border-gray-700 rounded-xl p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white font-bold flex items-center gap-2">
            <Code className="w-5 h-5 text-purple-400" />
            Custom SQL Query
          </h3>
          <button
            onClick={() => setShowCustomEditor(!showCustomEditor)}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm"
          >
            {showCustomEditor ? 'Hide' : 'Show'} Editor
          </button>
        </div>

        {showCustomEditor && (
          <div className="space-y-3">
            <textarea
              value={customQuery}
              onChange={(e) => setCustomQuery(e.target.value)}
              placeholder="SELECT * FROM ethereum_transactions LIMIT 10"
              className="w-full h-32 px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white font-mono text-sm"
            />
            <button
              onClick={handleCustomQuery}
              disabled={loading}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium disabled:opacity-50 flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              Execute Query
            </button>
          </div>
        )}
      </motion.div>

      {/* Query Results */}
      {queryResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gray-800/50 backdrop-blur border border-gray-700 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-white font-bold">Query Results</h3>
              <p className="text-gray-400 text-sm mt-1">
                {queryResult.row_count} rows × {queryResult.columns.length} columns
              </p>
            </div>
            <button
              onClick={exportToCSV}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
          </div>

          {/* Chart Visualization */}
          {selectedQuery?.id === 'gas_trends' && queryResult.rows.length > 0 && (
            <div className="mb-6">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={getChartData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="avg_gas" stroke="#3B82F6" name="Avg Gas" />
                  <Line type="monotone" dataKey="max_gas" stroke="#EF4444" name="Max Gas" />
                  <Line type="monotone" dataKey="min_gas" stroke="#10B981" name="Min Gas" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {selectedQuery?.id === 'dex_volume' && queryResult.rows.length > 0 && (
            <div className="mb-6">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={getChartData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="pool_address" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                  />
                  <Legend />
                  <Bar dataKey="total_liquidity" fill="#10B981" name="Liquidity (USD)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700">
                  {queryResult.columns.map((col, index) => (
                    <th
                      key={index}
                      className="px-4 py-3 text-left text-gray-400 font-medium text-sm"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {queryResult.rows.slice(0, 10).map((row, rowIndex) => (
                  <tr
                    key={rowIndex}
                    className="border-b border-gray-800 hover:bg-gray-900/50"
                  >
                    {row.map((cell, cellIndex) => (
                      <td
                        key={cellIndex}
                        className="px-4 py-3 text-gray-300 text-sm font-mono"
                      >
                        {typeof cell === 'object' ? JSON.stringify(cell) : String(cell)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {queryResult.rows.length > 10 && (
              <p className="text-gray-500 text-sm mt-3 text-center">
                Showing first 10 rows. Export to CSV for full data.
              </p>
            )}
          </div>
        </motion.div>
      )}

      {/* Info Box */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-gradient-to-r from-blue-900/20 to-cyan-900/20 border border-blue-500/50 rounded-xl p-6"
      >
        <div className="flex items-start gap-3">
          <AlertCircle className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
          <div>
            <h4 className="text-white font-bold mb-2">BigQuery Tables</h4>
            <ul className="text-gray-300 text-sm space-y-1">
              <li>• <code className="text-blue-400">ethereum_transactions</code> - All Ethereum transactions</li>
              <li>• <code className="text-blue-400">solana_transactions</code> - All Solana transactions</li>
              <li>• <code className="text-blue-400">dex_pools</code> - DEX pool snapshots (Uniswap)</li>
              <li>• <code className="text-blue-400">chainlink_prices</code> - Chainlink price feeds</li>
              <li>• <code className="text-blue-400">pyth_prices</code> - Pyth network prices</li>
              <li className="mt-2 text-gray-400">
                <strong>Note:</strong> Data populated by Fivetran connectors via GCS
              </li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
