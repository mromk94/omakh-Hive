'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, DollarSign, Users, Activity, Calendar,
  ArrowUp, ArrowDown, Download, Filter, AlertCircle
} from 'lucide-react';
import { toast } from 'react-hot-toast';

const BACKEND_URL = 'http://localhost:8001';

export default function EnhancedAnalytics() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [userStats, setUserStats] = useState<any>(null);
  const [transactionStats, setTransactionStats] = useState<any>(null);
  const [timeRange, setTimeRange] = useState('7d');
  const [loading, setLoading] = useState(true);
  const [isVisible, setIsVisible] = useState(true);

  // Detect tab visibility to pause polling when hidden
  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsVisible(!document.hidden);
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  useEffect(() => {
    fetchAnalytics();
    // 60s is reasonable for analytics - they don't need real-time updates
    // TODO: Consider WebSocket for live metric updates if needed
    const interval = setInterval(() => {
      if (isVisible) {
        fetchAnalytics();
      }
    }, 60000); // Refresh every 60s when visible
    return () => clearInterval(interval);
  }, [timeRange, isVisible]);

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const headers = { 'Authorization': `Bearer ${token}` };

      const [overviewRes, usersRes, txRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/v1/admin/analytics/overview`, { headers }),
        fetch(`${BACKEND_URL}/api/v1/admin/analytics/users`, { headers }),
        fetch(`${BACKEND_URL}/api/v1/admin/analytics/transactions`, { headers }),
      ]);

      const [overview, users, transactions] = await Promise.all([
        overviewRes.json(),
        usersRes.json(),
        txRes.json(),
      ]);

      if (overview.success) setAnalytics(overview.analytics);
      if (users.success) setUserStats(users.stats);
      if (transactions.success) setTransactionStats(transactions.stats);
      
      if (loading) {
        console.log('✅ Analytics loaded successfully');
      }
      setLoading(false);
    } catch (error: any) {
      console.error('Failed to fetch analytics:', error);
      toast.error(`Error loading analytics: ${error?.message || 'Unknown error'}`);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center text-gray-400 py-12">
        <div className="w-8 h-8 border-4 border-yellow-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        Loading analytics...
      </div>
    );
  }

  if (!analytics && !userStats && !transactionStats) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-12 text-center">
        <AlertCircle className="w-16 h-16 text-gray-600 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-white mb-2">No Analytics Data</h3>
        <p className="text-gray-400 mb-6">
          Analytics data will appear here once the system collects enough data.
        </p>
        <button
          onClick={fetchAnalytics}
          className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-black rounded-lg font-medium transition-colors"
        >
          Refresh Analytics
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Time Range */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-white">Advanced Analytics</h3>
          <p className="text-sm text-gray-400">Comprehensive platform metrics and insights</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-700"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="all">All Time</option>
          </select>
          <button className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg flex items-center gap-2 text-black">
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={Users}
          label="Total Users"
          value={analytics?.total_users || 0}
          change={userStats?.growth_rate || 0}
          trend="up"
        />
        <MetricCard
          icon={DollarSign}
          label="Total Revenue"
          value={`$${(analytics?.total_revenue_usd || 0).toLocaleString()}`}
          change={transactionStats?.revenue_growth || 0}
          trend="up"
        />
        <MetricCard
          icon={TrendingUp}
          label="OMK Distributed"
          value={(analytics?.total_omk_distributed || 0).toLocaleString()}
          change={12.5}
          trend="up"
        />
        <MetricCard
          icon={Activity}
          label="Active Users"
          value={analytics?.active_users_24h || 0}
          change={-5.2}
          trend="down"
        />
      </div>

      {/* Revenue Chart */}
      <RevenueOverview analytics={analytics} />

      {/* User Growth */}
      {userStats && <UserGrowth stats={userStats} />}

      {/* Transaction Activity */}
      {transactionStats && <TransactionActivity stats={transactionStats} />}

      {/* OTC Pipeline */}
      <OTCPipeline analytics={analytics} />
    </div>
  );
}

// ==================== SUB-COMPONENTS ====================

function MetricCard({ icon: Icon, label, value, change, trend }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gray-900/50 border border-gray-800 rounded-xl p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <Icon className="w-8 h-8 text-gray-400" />
        {change !== undefined && (
          <div className={`flex items-center gap-1 text-sm ${
            trend === 'up' ? 'text-green-400' : 'text-red-400'
          }`}>
            {trend === 'up' ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
            {Math.abs(change).toFixed(1)}%
          </div>
        )}
      </div>
      <div className="text-3xl font-bold text-white mb-1">{value}</div>
      <div className="text-sm text-gray-400">{label}</div>
    </motion.div>
  );
}

function RevenueOverview({ analytics }: any) {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <h4 className="text-lg font-semibold text-white mb-4">Revenue Overview</h4>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <div className="text-sm text-gray-400 mb-2">Total Revenue</div>
          <div className="text-2xl font-bold text-white">
            ${(analytics?.total_revenue_usd || 0).toLocaleString()}
          </div>
          <div className="text-xs text-green-400 mt-1">
            From {analytics?.approved_otc_requests || 0} approved OTC requests
          </div>
        </div>
        
        <div>
          <div className="text-sm text-gray-400 mb-2">Average Deal Size</div>
          <div className="text-2xl font-bold text-white">
            ${analytics?.approved_otc_requests > 0 
              ? Math.round(analytics.total_revenue_usd / analytics.approved_otc_requests).toLocaleString()
              : 0}
          </div>
          <div className="text-xs text-gray-500 mt-1">Per transaction</div>
        </div>
        
        <div>
          <div className="text-sm text-gray-400 mb-2">Pending Value</div>
          <div className="text-2xl font-bold text-yellow-400">
            ${(analytics?.pending_value_usd || 0).toLocaleString()}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {analytics?.pending_otc_requests || 0} requests awaiting approval
          </div>
        </div>
      </div>

      {/* Simple revenue bar chart */}
      <div className="mt-6">
        <div className="text-sm text-gray-400 mb-3">Revenue by Status</div>
        <div className="space-y-3">
          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-gray-300">Approved</span>
              <span className="text-green-400">${(analytics?.total_revenue_usd || 0).toLocaleString()}</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full"
                style={{ width: '65%' }}
              />
            </div>
          </div>
          
          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-gray-300">Pending</span>
              <span className="text-yellow-400">${(analytics?.pending_value_usd || 0).toLocaleString()}</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2">
              <div 
                className="bg-yellow-500 h-2 rounded-full"
                style={{ width: '25%' }}
              />
            </div>
          </div>
          
          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-gray-300">Rejected</span>
              <span className="text-red-400">$0</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2">
              <div 
                className="bg-red-500 h-2 rounded-full"
                style={{ width: '10%' }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function UserGrowth({ stats }: any) {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <h4 className="text-lg font-semibold text-white mb-4">User Growth</h4>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">New Today</div>
          <div className="text-2xl font-bold text-white">{stats.new_users_today || 0}</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">New This Week</div>
          <div className="text-2xl font-bold text-white">{stats.new_users_week || 0}</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">New This Month</div>
          <div className="text-2xl font-bold text-white">{stats.new_users_month || 0}</div>
        </div>
      </div>

      <div className="mt-4">
        <div className="text-sm text-gray-400 mb-2">Growth Rate</div>
        <div className="flex items-center gap-2">
          <div className="text-xl font-bold text-green-400">
            +{stats.growth_rate || 0}%
          </div>
          <span className="text-xs text-gray-500">vs last period</span>
        </div>
      </div>
    </div>
  );
}

function TransactionActivity({ stats }: any) {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <h4 className="text-lg font-semibold text-white mb-4">Transaction Activity</h4>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
          <div>
            <div className="text-white font-medium">Total Transactions</div>
            <div className="text-xs text-gray-400">All time</div>
          </div>
          <div className="text-2xl font-bold text-white">{stats.total_transactions || 0}</div>
        </div>

        <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
          <div>
            <div className="text-white font-medium">Today's Volume</div>
            <div className="text-xs text-gray-400">Last 24 hours</div>
          </div>
          <div className="text-2xl font-bold text-blue-400">
            ${(stats.volume_today || 0).toLocaleString()}
          </div>
        </div>

        <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
          <div>
            <div className="text-white font-medium">Average Transaction</div>
            <div className="text-xs text-gray-400">Mean value</div>
          </div>
          <div className="text-2xl font-bold text-purple-400">
            ${(stats.avg_transaction || 0).toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
}

function OTCPipeline({ analytics }: any) {
  const pending = analytics?.pending_otc_requests || 0;
  const approved = analytics?.approved_otc_requests || 0;
  const rejected = analytics?.rejected_otc_requests || 0;
  const total = pending + approved + rejected || 1;

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <h4 className="text-lg font-semibold text-white mb-4">OTC Pipeline</h4>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4">
          <div className="text-sm text-yellow-400 mb-1">Pending Review</div>
          <div className="text-3xl font-bold text-white">{pending}</div>
          <div className="text-xs text-gray-400 mt-2">
            {((pending / total) * 100).toFixed(0)}% of total
          </div>
        </div>

        <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
          <div className="text-sm text-green-400 mb-1">Approved</div>
          <div className="text-3xl font-bold text-white">{approved}</div>
          <div className="text-xs text-gray-400 mt-2">
            {((approved / total) * 100).toFixed(0)}% conversion rate
          </div>
        </div>

        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
          <div className="text-sm text-red-400 mb-1">Rejected</div>
          <div className="text-3xl font-bold text-white">{rejected}</div>
          <div className="text-xs text-gray-400 mt-2">
            {((rejected / total) * 100).toFixed(0)}% rejection rate
          </div>
        </div>
      </div>

      {/* Pipeline visualization */}
      <div className="space-y-2">
        <div className="text-sm text-gray-400 mb-2">Pipeline Status</div>
        <div className="flex gap-1 h-8 rounded-lg overflow-hidden">
          <div 
            className="bg-yellow-500 flex items-center justify-center text-xs text-black font-medium"
            style={{ width: `${(pending / total) * 100}%` }}
          >
            {pending > 0 && pending}
          </div>
          <div 
            className="bg-green-500 flex items-center justify-center text-xs text-black font-medium"
            style={{ width: `${(approved / total) * 100}%` }}
          >
            {approved > 0 && approved}
          </div>
          <div 
            className="bg-red-500 flex items-center justify-center text-xs text-white font-medium"
            style={{ width: `${(rejected / total) * 100}%` }}
          >
            {rejected > 0 && rejected}
          </div>
        </div>
      </div>
    </div>
  );
}
