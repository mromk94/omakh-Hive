'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import { 
  Crown, Settings, Users, TrendingUp, DollarSign, 
  Activity, MessageSquare, Shield, Database, Zap,
  BarChart3, PieChart, Calendar, Bell, Search,
  ChevronRight, AlertCircle, CheckCircle2, Sparkles
} from 'lucide-react';
import { API_ENDPOINTS } from '@/lib/constants';
import ContractDeployer from './components/ContractDeployer';
import TestnetUtilities from './components/TestnetUtilities';

export default function KingdomAdminPortal() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [systemConfig, setSystemConfig] = useState<any>(null);
  const [adminUser, setAdminUser] = useState<any>(null);
  const [notificationCount, setNotificationCount] = useState(0);
  const [hiveStats, setHiveStats] = useState<any>(null);
  const [otcPendingCount, setOtcPendingCount] = useState(0);

  // Check auth
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('auth_token');
      
      // DEV MODE: Allow access without auth if no token exists
      const isDev = process.env.NODE_ENV === 'development';
      if (!token && !isDev) {
        router.push('/kingdom/login');
        return;
      }
      
      // If no token but in dev mode, set mock auth
      if (!token && isDev) {
        console.log('🔓 DEV MODE: Bypassing auth');
        setAdminUser({ email: 'dev@omk.com', role: 'admin', full_name: 'Dev Admin' });
        setIsAuthenticated(true);
        setLoading(false);
        await Promise.all([
          loadSystemConfig(),
          loadDashboardStats()
        ]);
        return;
      }
      
      // Verify token with backend (with timeout)
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
        
        const response = await fetch(`${API_ENDPOINTS.AUTH}/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
          const data = await response.json();
          // Check if user is admin
          if (data.role === 'admin') {
            setAdminUser(data);
            setIsAuthenticated(true);
            setLoading(false);
            // Load system config and stats
            await Promise.all([
              loadSystemConfig(),
              loadDashboardStats()
            ]);
          } else {
            // Not an admin
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user');
            router.push('/kingdom/login');
          }
        } else {
          // Invalid token
          console.error('Auth check failed:', response.status, response.statusText);
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
          router.push('/kingdom/login');
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        // Check if it's a timeout or network error
        if (error instanceof Error && error.name === 'AbortError') {
          console.error('⚠️ Backend timeout - is the server running?');
        }
        // In dev mode, allow access even if backend is down
        const isDev = process.env.NODE_ENV === 'development';
        if (isDev) {
          console.log('🔓 DEV MODE: Auth failed but allowing access');
          setAdminUser({ email: 'dev@omk.com', role: 'admin', full_name: 'Dev Admin' });
          setIsAuthenticated(true);
          setLoading(false);
          return;
        }
        // Production: Clear token and redirect
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        router.push('/kingdom/login');
      }
    };
    
    checkAuth();
  }, [router]);

  const loadSystemConfig = async () => {
    try {
      const response = await fetch(`${API_ENDPOINTS.ADMIN}/config`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setSystemConfig(data.config);
      }
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  };

  const loadDashboardStats = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const headers = { 'Authorization': `Bearer ${token}` };
      
      // Load hive overview for real bee count
      const hiveRes = await fetch(`${API_ENDPOINTS.ADMIN}/hive/overview`, { headers });
      if (hiveRes.ok) {
        const hiveData = await hiveRes.json();
        if (hiveData.success) {
          setHiveStats(hiveData.overview);
        }
      }
      
      // Load OTC pending count
      const otcRes = await fetch(`${API_ENDPOINTS.ADMIN}/otc/requests?status=pending`, { headers });
      if (otcRes.ok) {
        const otcData = await otcRes.json();
        if (otcData.success) {
          setOtcPendingCount(otcData.requests.length);
        }
      }
      
      // TODO: Load notifications when endpoint ready
      setNotificationCount(0);
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    router.push('/kingdom/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-yellow-500 text-xl">Loading Kingdom...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity, badge: null, category: 'main' },
    { id: 'hive', label: 'Hive Intelligence', icon: Zap, badge: hiveStats?.bees?.total?.toString() || null, category: 'queen' },
    { id: 'queen-dev', label: 'Queen Development', icon: Sparkles, badge: 'AI', category: 'queen' },
    { id: 'system-analysis', label: 'System Analysis', icon: TrendingUp, badge: null, category: 'queen' },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, badge: null, category: 'main' },
    { id: 'data-pipeline', label: 'Data Pipeline', icon: Database, badge: 'FIVETRAN', category: 'hackathon' },
    { id: 'elastic-search', label: 'Elastic Search', icon: Search, badge: 'ELASTIC', category: 'hackathon' },
    { id: 'bigquery', label: 'BigQuery', icon: PieChart, badge: 'BIGQUERY', category: 'hackathon' },
    { id: 'users', label: 'Users', icon: Users, badge: null, category: 'manage' },
    { id: 'otc', label: 'OTC', icon: DollarSign, badge: otcPendingCount > 0 ? otcPendingCount.toString() : null, category: 'manage' },
    { id: 'config', label: 'Config', icon: Settings, badge: null, category: 'system' },
    { id: 'contracts', label: 'Contracts', icon: Shield, badge: null, category: 'system' },
    { id: 'testnet', label: 'Testnet Utils', icon: Zap, badge: 'NEW', category: 'system' },
  ];

  const categories = [
    { id: 'main', label: 'Main', color: 'yellow' },
    { id: 'queen', label: 'Queen AI', color: 'purple' },
    { id: 'hackathon', label: 'Data & Analytics', color: 'green' },
    { id: 'manage', label: 'Management', color: 'blue' },
    { id: 'system', label: 'System', color: 'gray' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black">
      {/* Toast Notifications */}
      <Toaster 
        position="top-right"
        toastOptions={{
          className: '',
          style: {
            background: '#1f2937',
            color: '#fff',
            border: '1px solid #374151'
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      
      {/* Header */}
      <header className="bg-black/80 backdrop-blur-2xl border-b border-yellow-500/20 sticky top-0 z-50 shadow-2xl shadow-yellow-500/5">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Crown className="w-10 h-10 text-yellow-500 drop-shadow-lg" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-black animate-pulse" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-yellow-500 to-yellow-300 bg-clip-text text-transparent">Kingdom</h1>
                <p className="text-xs text-gray-400 flex items-center gap-2">
                  <span>Admin Portal</span>
                  <span className="text-green-400">• Online</span>
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button className="relative px-3 py-2 bg-gray-800/80 hover:bg-gray-700 rounded-lg transition-all hover:scale-105 group">
                <Bell className="w-5 h-5 text-gray-400 group-hover:text-yellow-500 transition-colors" />
                {notificationCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-yellow-500 text-black text-xs rounded-full flex items-center justify-center font-bold">
                    {notificationCount}
                  </span>
                )}
              </button>
              <div className="h-8 w-px bg-gray-700" />
              <button className="px-4 py-2 bg-gray-800/80 hover:bg-gray-700 rounded-lg text-gray-300 hover:text-white text-sm font-medium transition-all flex items-center gap-2">
                <div className="w-7 h-7 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-full flex items-center justify-center text-black font-bold text-xs">
                  {adminUser?.full_name?.charAt(0) || adminUser?.email?.charAt(0) || 'A'}
                </div>
                <span>{adminUser?.full_name || adminUser?.email?.split('@')[0] || 'Admin'}</span>
              </button>
              <button 
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600/10 hover:bg-red-600/20 text-red-400 rounded-lg text-sm font-medium transition-all border border-red-500/20 hover:border-red-500/40">
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Enhanced Navigation */}
        <div className="mb-8 space-y-4">
          {/* Category Tabs */}
          <div className="flex flex-wrap gap-3">
            {categories.map((category) => {
              const categoryTabs = tabs.filter(t => t.category === category.id);
              const isAnyCategoryActive = categoryTabs.some(t => t.id === activeTab);
              
              return (
                <div key={category.id} className="relative group">
                  <div className={`px-4 py-2 rounded-lg border transition-all cursor-pointer ${
                    isAnyCategoryActive
                      ? 'bg-yellow-500/10 border-yellow-500/50 text-yellow-500'
                      : 'bg-gray-800/30 border-gray-700 text-gray-400 hover:border-gray-600'
                  }`}>
                    <span className="text-sm font-medium">{category.label}</span>
                  </div>
                  
                  {/* Dropdown on hover */}
                  <div className="absolute top-full left-0 mt-2 min-w-[200px] bg-gray-900 border border-gray-700 rounded-xl shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                    <div className="p-2 space-y-1">
                      {categoryTabs.map((tab) => (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id)}
                          className={`w-full px-3 py-2 rounded-lg flex items-center gap-3 transition-all text-left ${
                            activeTab === tab.id
                              ? 'bg-yellow-500 text-black font-semibold'
                              : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                          }`}
                        >
                          <tab.icon className="w-4 h-4 flex-shrink-0" />
                          <span className="text-sm flex-1">{tab.label}</span>
                          {tab.badge && (
                            <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                              activeTab === tab.id
                                ? 'bg-black/20 text-black'
                                : tab.badge === 'NEW'
                                ? 'bg-green-500/20 text-green-400'
                                : 'bg-yellow-500/20 text-yellow-400'
                            }`}>
                              {tab.badge}
                            </span>
                          )}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          
          {/* Active Tab Indicator */}
          <div className="flex items-center gap-3 p-4 bg-gradient-to-r from-gray-800/50 to-transparent border border-gray-700/50 rounded-xl">
            {tabs.find(t => t.id === activeTab) && (
              <>
                <div className="p-2 bg-yellow-500/10 rounded-lg">
                  {(() => {
                    const Icon = tabs.find(t => t.id === activeTab)?.icon;
                    return Icon ? <Icon className="w-5 h-5 text-yellow-500" /> : null;
                  })()}
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-bold text-white">
                    {tabs.find(t => t.id === activeTab)?.label}
                  </h2>
                  <p className="text-xs text-gray-400">
                    {activeTab === 'overview' && 'System overview and quick stats'}
                    {activeTab === 'hive' && 'Real-time bee intelligence and monitoring'}
                    {activeTab === 'queen-dev' && 'Chat, code proposals, bug fixing, and database queries'}
                    {activeTab === 'system-analysis' && 'AI-powered system architecture analysis'}
                    {activeTab === 'analytics' && 'Advanced metrics and reports'}
                    {activeTab === 'users' && 'Manage user accounts and permissions'}
                    {activeTab === 'otc' && 'OTC requests and approvals'}
                    {activeTab === 'config' && 'System configuration and settings'}
                    {activeTab === 'contracts' && 'Smart contract management'}
                    {activeTab === 'testnet' && 'Testnet utilities and faucets'}
                  </p>
                </div>
                {tabs.find(t => t.id === activeTab)?.badge && (
                  <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-xs font-bold">
                    {tabs.find(t => t.id === activeTab)?.badge}
                  </span>
                )}
              </>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="space-y-6">
          {activeTab === 'overview' && <OverviewTab onNavigate={setActiveTab} />}
          {activeTab === 'config' && <SystemConfigTab config={systemConfig} onUpdate={loadSystemConfig} />}
          {activeTab === 'users' && <UsersTab />}
          {activeTab === 'otc' && <OTCManagementTab />}
          {activeTab === 'queen-dev' && <QueenDevelopmentTab />}
          {activeTab === 'system-analysis' && <ClaudeAnalysisTab />}
          {activeTab === 'hive' && <HiveDashboardTab />}
          {activeTab === 'analytics' && <AnalyticsTab />}
          {activeTab === 'data-pipeline' && <DataPipelineTab />}
          {activeTab === 'elastic-search' && <ElasticSearchTab />}
          {activeTab === 'bigquery' && <BigQueryTab />}
          {activeTab === 'contracts' && <ContractDeployer />}
          {activeTab === 'testnet' && <TestnetUtilities />}
        </div>
      </div>
    </div>
  );
}

// ==================== TAB COMPONENTS ====================

function OverviewTab({ onNavigate }: { onNavigate?: (tab: string) => void }) {
  const [analytics, setAnalytics] = useState<any>(null);
  const [hiveOverview, setHiveOverview] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('auth_token') || 'dev_token';
        const headers = { 'Authorization': `Bearer ${token}` };

        // Add timeout to prevent hanging
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout

        const [analyticsRes, hiveRes] = await Promise.all([
          fetch(`${API_ENDPOINTS.ADMIN}/analytics/overview`, { 
            headers,
            signal: controller.signal 
          }),
          fetch(`${API_ENDPOINTS.ADMIN}/hive/overview`, { 
            headers,
            signal: controller.signal 
          }),
        ]);

        clearTimeout(timeoutId);

        const [analyticsData, hiveData] = await Promise.all([
          analyticsRes.json(),
          hiveRes.json(),
        ]);

        if (analyticsData.success) setAnalytics(analyticsData.analytics);
        if (hiveData.success) setHiveOverview(hiveData.overview);
        setLoading(false);
      } catch (error: any) {
        console.error('Failed to fetch overview data:', error);
        // If backend is down, show mock data
        if (error.name === 'AbortError') {
          console.warn('⚠️ Backend timeout - is the server running?');
          toast.error('Backend is slow or not responding');
        }
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s (reduced from 10s)
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <div className="w-8 h-8 border-4 border-yellow-500 border-t-transparent rounded-full animate-spin mb-4"></div>
        <div className="text-gray-400">Loading overview...</div>
        <div className="text-xs text-gray-600 mt-2">If this takes too long, check if backend is running</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">System Overview</h2>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Users}
          label="Total Users"
          value={analytics?.total_users || 0}
          change={`+${analytics?.new_users_today || 0} today`}
          color="blue"
        />
        <StatCard
          icon={DollarSign}
          label="Total Revenue"
          value={`$${(analytics?.total_revenue_usd || 0).toLocaleString()}`}
          change={`${analytics?.pending_otc_requests || 0} pending`}
          color="green"
        />
        <StatCard
          icon={TrendingUp}
          label="OMK Distributed"
          value={(analytics?.total_omk_distributed || 0).toLocaleString()}
          change="OTC Sales"
          color="yellow"
        />
        <StatCard
          icon={Activity}
          label="Hive Active"
          value={`${hiveOverview?.bees.currently_active || 0}/${hiveOverview?.bees.total || 19}`}
          change={`${hiveOverview?.bees.healthy || 0} healthy`}
          color="purple"
        />
      </div>

      {/* Hive Status */}
      {hiveOverview && (
        <div className="bg-gradient-to-br from-yellow-900/20 to-yellow-800/20 border border-yellow-500/30 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-500" />
            Hive Status
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="text-sm text-gray-400 mb-1">Message Bus</div>
              <div className="text-xl font-bold text-white">
                {hiveOverview.message_bus.total_messages} messages
              </div>
              <div className="text-xs text-green-400">
                {hiveOverview.message_bus.delivery_rate.toFixed(1)}% delivery rate
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">Hive Board</div>
              <div className="text-xl font-bold text-white">
                {hiveOverview.hive_board.total_posts} posts
              </div>
              <div className="text-xs text-blue-400">
                {hiveOverview.hive_board.active_categories} active categories
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">Queen AI</div>
              <div className="text-xl font-bold text-white">
                {hiveOverview.queen.decision_count} decisions
              </div>
              <div className="text-xs text-purple-400">
                {hiveOverview.queen.running ? 'Running' : 'Stopped'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">⚡ Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button onClick={() => onNavigate?.('config')} className="p-4 bg-gradient-to-br from-yellow-900/40 to-gray-800 hover:from-yellow-900/60 hover:to-gray-700 border border-yellow-500/30 rounded-lg flex flex-col items-center gap-2 transition-all">
            <Settings className="w-6 h-6 text-yellow-400" />
            <span className="text-xs font-medium text-white">System Config</span>
            <span className="text-xs text-gray-400">OTC Phase & Treasury</span>
          </button>
          <button onClick={() => onNavigate?.('otc')} className="p-4 bg-gradient-to-br from-green-900/40 to-gray-800 hover:from-green-900/60 hover:to-gray-700 border border-green-500/30 rounded-lg flex flex-col items-center gap-2 transition-all">
            <DollarSign className="w-6 h-6 text-green-400" />
            <span className="text-xs font-medium text-white">OTC Requests</span>
            <span className="text-xs text-gray-400">Review & Approve</span>
          </button>
          <button onClick={() => onNavigate?.('users')} className="p-4 bg-gradient-to-br from-blue-900/40 to-gray-800 hover:from-blue-900/60 hover:to-gray-700 border border-blue-500/30 rounded-lg flex flex-col items-center gap-2 transition-all">
            <Users className="w-6 h-6 text-blue-400" />
            <span className="text-xs font-medium text-white">User Management</span>
            <span className="text-xs text-gray-400">Accounts & Permissions</span>
          </button>
          <button onClick={() => onNavigate?.('queen')} className="p-4 bg-gradient-to-br from-purple-900/40 to-gray-800 hover:from-purple-900/60 hover:to-gray-700 border border-purple-500/30 rounded-lg flex flex-col items-center gap-2 transition-all">
            <MessageSquare className="w-6 h-6 text-purple-400" />
            <span className="text-xs font-medium text-white">Queen AI Chat</span>
            <span className="text-xs text-gray-400">Direct AI Access</span>
          </button>
        </div>
      </div>

      {/* System Health */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">System Health</h3>
        <div className="space-y-3">
          <HealthItem 
            label="Queen AI" 
            status={hiveOverview?.queen.running ? "operational" : "error"} 
          />
          <HealthItem 
            label="Hive Communication" 
            status={hiveOverview?.message_bus.delivery_rate > 95 ? "operational" : "warning"} 
          />
          <HealthItem 
            label="Bee Swarm" 
            status={hiveOverview?.bees.healthy === hiveOverview?.bees.total ? "operational" : "warning"} 
          />
          <HealthItem label="Database" status="operational" />
        </div>
      </div>
    </div>
  );
}

function SystemConfigTab({ config, onUpdate }: any) {
  const [otcPhase, setOtcPhase] = useState(config?.otc_phase || 'private_sale');
  const [treasuryWallets, setTreasuryWallets] = useState({
    usdt: config?.treasury_wallets?.usdt || '',
    usdc: config?.treasury_wallets?.usdc || '',
    dai: config?.treasury_wallets?.dai || '',
    eth: config?.treasury_wallets?.eth || ''
  });
  const [paymentMethods, setPaymentMethods] = useState({
    usdt: config?.payment_methods_enabled?.usdt ?? true,
    usdc: config?.payment_methods_enabled?.usdc ?? true,
    dai: config?.payment_methods_enabled?.dai ?? true,
    eth: config?.payment_methods_enabled?.eth ?? false
  });
  const [tgeDate, setTgeDate] = useState(config?.tge_date || '2025-12-31T00:00:00Z');
  const [saving, setSaving] = useState(false);
  const [savingWallets, setSavingWallets] = useState(false);
  const [savingPaymentMethods, setSavingPaymentMethods] = useState(false);
  const [savingTGEDate, setSavingTGEDate] = useState(false);

  const handleSaveOTCPhase = async () => {
    setSaving(true);
    try {
      const response = await fetch(`${API_ENDPOINTS.ADMIN}/config/otc-phase`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({ phase: otcPhase })
      });
      
      if (response.ok) {
        toast.success('✅ OTC Phase updated successfully!');
        onUpdate();
      } else {
        toast.error('Failed to update OTC phase');
      }
    } catch (error: any) {
      toast.error(`Error: ${error?.message || 'Network error. Please try again.'}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">System Configuration</h2>

      {/* OTC Phase Control */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">OTC Phase Management</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Active OTC Phase</label>
            <select
              value={otcPhase}
              onChange={(e) => setOtcPhase(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white"
            >
              <option value="private_sale">Private Sale (Pre-TGE) - Manual Approval</option>
              <option value="standard">Standard OTC - Instant Swaps</option>
              <option value="disabled">Disabled - No Purchases</option>
            </select>
          </div>
          
          <button
            onClick={handleSaveOTCPhase}
            disabled={saving}
            className="px-6 py-3 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-700 text-black font-semibold rounded-lg"
          >
            {saving ? 'Saving...' : 'Save OTC Phase'}
          </button>

          <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <p className="text-sm text-blue-300">
              <strong>Current Phase:</strong> {config?.otc_phase || 'Loading...'}
            </p>
            <p className="text-xs text-gray-400 mt-2">
              This controls which OTC flow users see when they want to buy OMK tokens.
            </p>
          </div>
        </div>
      </div>

      {/* Treasury Wallet Configuration */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Treasury Wallets (OTC Payments)</h3>
        <p className="text-sm text-gray-400 mb-4">
          Configure wallet addresses where users will send their crypto payments for OTC purchases. These addresses are displayed during the payment step.
        </p>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">USDT Treasury Wallet</label>
            <input
              type="text"
              value={treasuryWallets.usdt}
              onChange={(e) => setTreasuryWallets({ ...treasuryWallets, usdt: e.target.value })}
              placeholder="0x..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white font-mono text-sm"
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-400 mb-2">USDC Treasury Wallet</label>
            <input
              type="text"
              value={treasuryWallets.usdc}
              onChange={(e) => setTreasuryWallets({ ...treasuryWallets, usdc: e.target.value })}
              placeholder="0x..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white font-mono text-sm"
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-400 mb-2">DAI Treasury Wallet</label>
            <input
              type="text"
              value={treasuryWallets.dai}
              onChange={(e) => setTreasuryWallets({ ...treasuryWallets, dai: e.target.value })}
              placeholder="0x..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white font-mono text-sm"
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-400 mb-2">ETH Treasury Wallet (Backup)</label>
            <input
              type="text"
              value={treasuryWallets.eth}
              onChange={(e) => setTreasuryWallets({ ...treasuryWallets, eth: e.target.value })}
              placeholder="0x..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white font-mono text-sm"
            />
          </div>
          
          <button
            onClick={async () => {
              setSavingWallets(true);
              try {
                const response = await fetch(`${API_ENDPOINTS.ADMIN}/config/treasury-wallets`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                  },
                  body: JSON.stringify({ wallets: treasuryWallets })
                });
                
                if (response.ok) {
                  toast.success('Treasury wallets updated successfully!');
                  onUpdate();
                } else {
                  toast.error('Failed to update treasury wallets');
                }
              } catch (error) {
                toast.error('Network error. Please try again.');
              } finally {
                setSavingWallets(false);
              }
            }}
            disabled={savingWallets}
            className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 text-white font-semibold rounded-lg"
          >
            {savingWallets ? 'Saving...' : 'Save Treasury Wallets'}
          </button>

          <div className="p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg">
            <p className="text-sm text-orange-300">
              <strong>⚠️ Important:</strong> Double-check these addresses before saving. Incorrect addresses may result in lost funds!
            </p>
          </div>
        </div>
      </div>

      {/* Payment Methods Toggle */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Payment Methods</h3>
        <p className="text-sm text-gray-400 mb-4">
          Enable or disable specific payment tokens for OTC purchases. Disabled tokens won't appear in the payment selector.
        </p>
        
        <div className="space-y-3 mb-4">
          {Object.keys(paymentMethods).map((token) => (
            <label key={token} className="flex items-center justify-between p-3 bg-gray-800 rounded-lg hover:bg-gray-750 cursor-pointer">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  paymentMethods[token as keyof typeof paymentMethods] 
                    ? 'bg-green-500/20 text-green-400' 
                    : 'bg-gray-700 text-gray-500'
                }`}>
                  {token.toUpperCase()}
                </div>
                <div>
                  <div className="text-white font-medium">{token.toUpperCase()}</div>
                  <div className="text-xs text-gray-400">
                    {token === 'usdt' && 'Tether USD'}
                    {token === 'usdc' && 'USD Coin'}
                    {token === 'dai' && 'Dai Stablecoin'}
                    {token === 'eth' && 'Ethereum (backup)'}
                  </div>
                </div>
              </div>
              <input
                type="checkbox"
                checked={paymentMethods[token as keyof typeof paymentMethods]}
                onChange={(e) => setPaymentMethods({ ...paymentMethods, [token]: e.target.checked })}
                className="w-5 h-5 rounded border-gray-600 text-green-600 focus:ring-green-500"
              />
            </label>
          ))}
        </div>

        <button
          onClick={async () => {
            setSavingPaymentMethods(true);
            try {
              const response = await fetch(`${API_ENDPOINTS.ADMIN}/config/payment-methods`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: JSON.stringify({ payment_methods: paymentMethods })
              });
              
              if (response.ok) {
                toast.success('Payment methods updated successfully!');
                onUpdate();
              } else {
                toast.error('Failed to update payment methods');
              }
            } catch (error) {
              toast.error('Network error. Please try again.');
            } finally {
              setSavingPaymentMethods(false);
            }
          }}
          disabled={savingPaymentMethods}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white font-semibold rounded-lg"
        >
          {savingPaymentMethods ? 'Saving...' : 'Save Payment Methods'}
        </button>
      </div>

      {/* TGE Date Configuration */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">TGE (Token Generation Event) Date</h3>
        <p className="text-sm text-gray-400 mb-4">
          Set the date when OMK tokens will be distributed to presale wallets. This date is shown to users during the purchase process.
        </p>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">TGE Date & Time (UTC)</label>
            <input
              type="datetime-local"
              value={tgeDate.slice(0, 16)}
              onChange={(e) => setTgeDate(e.target.value + ':00Z')}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white"
            />
            <p className="text-xs text-gray-500 mt-1">Current: {new Date(tgeDate).toLocaleString()}</p>
          </div>
          
          <button
            onClick={async () => {
              setSavingTGEDate(true);
              try {
                const response = await fetch(`${API_ENDPOINTS.ADMIN}/config/tge-date`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                  },
                  body: JSON.stringify({ tge_date: tgeDate })
                });
                
                if (response.ok) {
                  toast.success('TGE date updated successfully!');
                  onUpdate();
                } else {
                  toast.error('Failed to update TGE date');
                }
              } catch (error) {
                toast.error('Network error. Please try again.');
              } finally {
                setSavingTGEDate(false);
              }
            }}
            disabled={savingTGEDate}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 text-white font-semibold rounded-lg"
          >
            {savingTGEDate ? 'Saving...' : 'Save TGE Date'}
          </button>

          <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <p className="text-sm text-blue-300">
              <strong>📅 TGE Countdown:</strong> Users will see a countdown to this date during OTC purchase. Tokens will be automatically distributed to presale wallets at TGE.
            </p>
          </div>
        </div>
      </div>

      {/* Feature Flags */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Feature Flags</h3>
        <p className="text-sm text-gray-400 mb-4">
          Enable or disable platform features. Changes take effect immediately.
        </p>
        <div className="space-y-3">
          <ToggleOption 
            label="Property Investment" 
            enabled={config?.allow_property_investment}
            description="Allow users to invest in tokenized properties"
            onChange={async (value: boolean) => {
              try {
                const response = await fetch('http://localhost:8001/api/v1/admin/config', {
                  method: 'PUT',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                  },
                  body: JSON.stringify({ allow_property_investment: value })
                });
                if (response.ok) {
                  toast.success(`Property investment ${value ? 'enabled' : 'disabled'}`);
                  onUpdate();
                } else {
                  toast.error('Failed to update setting');
                }
              } catch (error) {
                toast.error('Network error');
              }
            }}
          />
          <ToggleOption 
            label="Staking" 
            enabled={config?.allow_staking}
            description="Enable OMK token staking"
            onChange={async (value: boolean) => {
              try {
                const response = await fetch('http://localhost:8001/api/v1/admin/config', {
                  method: 'PUT',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                  },
                  body: JSON.stringify({ allow_staking: value })
                });
                if (response.ok) {
                  toast.success(`Staking ${value ? 'enabled' : 'disabled'}`);
                  onUpdate();
                } else {
                  toast.error('Failed to update setting');
                }
              } catch (error) {
                toast.error('Network error');
              }
            }}
          />
          <ToggleOption 
            label="Governance" 
            enabled={config?.allow_governance}
            description="Enable DAO governance voting"
            onChange={async (value: boolean) => {
              try {
                const response = await fetch('http://localhost:8001/api/v1/admin/config', {
                  method: 'PUT',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                  },
                  body: JSON.stringify({ allow_governance: value })
                });
                if (response.ok) {
                  toast.success(`Governance ${value ? 'enabled' : 'disabled'}`);
                  onUpdate();
                } else {
                  toast.error('Failed to update setting');
                }
              } catch (error) {
                toast.error('Network error');
              }
            }}
          />
        </div>
      </div>
    </div>
  );
}

function UsersTab() {
  const UserManagement = require('./components/UserManagement').default;
  return (
    <div className="space-y-6">
      <UserManagement />
    </div>
  );
}

function OTCManagementTab() {
  const OTCRequestManager = require('./components/OTCRequestManager').default;
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">OTC Request Management</h2>
      <OTCRequestManager />
    </div>
  );
}

function QueenDevelopmentTab() {
  const QueenDevelopmentHub = require('./components/QueenDevelopmentHub').default;
  return (
    <div className="space-y-6">
      <QueenDevelopmentHub />
    </div>
  );
}

function ClaudeAnalysisTab() {
  const ClaudeSystemAnalysis = require('./components/ClaudeSystemAnalysis').default;
  const DataPipelineManager = require('./components/DataPipelineManager').default;
  const ElasticSearchDashboard = require('./components/ElasticSearchDashboard').default;
  const BigQueryAnalytics = require('./components/BigQueryAnalytics').default;
  return (
    <div className="space-y-6">
      <ClaudeSystemAnalysis />
    </div>
  );
}

function HiveDashboardTab() {
  const HiveIntelligence = require('./components/HiveIntelligence').default;
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white flex items-center gap-2">
        <Zap className="w-6 h-6 text-yellow-500" />
        Hive Intelligence
      </h2>
      <p className="text-gray-400 mb-6">
        Real-time visibility into all bee operations, communication, and performance
      </p>
      <HiveIntelligence />
    </div>
  );
}

function AnalyticsTab() {
  const EnhancedAnalytics = require('./components/EnhancedAnalytics').default;
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white flex items-center gap-2">
        <BarChart3 className="w-6 h-6 text-yellow-500" />
        Advanced Analytics
      </h2>
      <p className="text-gray-400 mb-6">
        Comprehensive metrics, revenue tracking, and business intelligence
      </p>
      <EnhancedAnalytics />
    </div>
  );
}

function DataPipelineTab() {
  const DataPipelineManager = require('./components/DataPipelineManager').default;
  return (
    <div className="space-y-6">
      <DataPipelineManager />
    </div>
  );
}

function ElasticSearchTab() {
  const ElasticSearchDashboard = require('./components/ElasticSearchDashboard').default;
  return (
    <div className="space-y-6">
      <ElasticSearchDashboard />
    </div>
  );
}

function BigQueryTab() {
  const BigQueryAnalytics = require('./components/BigQueryAnalytics').default;
  return (
    <div className="space-y-6">
      <BigQueryAnalytics />
    </div>
  );
}

function ContractsTab() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Smart Contracts</h2>
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <p className="text-gray-400">Contract management interface coming soon...</p>
        <p className="text-sm text-gray-500 mt-2">
          Deploy, upgrade, and interact with smart contracts directly from here.
        </p>
      </div>
    </div>
  );
}

// ==================== HELPER COMPONENTS ====================

function StatCard({ icon: Icon, label, value, change, color }: any) {
  const colors = {
    blue: 'from-blue-600 to-blue-700',
    green: 'from-green-600 to-green-700',
    yellow: 'from-yellow-600 to-yellow-700',
    purple: 'from-purple-600 to-purple-700'
  };

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <Icon className="w-8 h-8 text-gray-400" />
        <span className="text-sm text-green-400">{change}</span>
      </div>
      <div className="text-3xl font-bold text-white mb-1">{value}</div>
      <div className="text-sm text-gray-400">{label}</div>
    </div>
  );
}

function QuickAction({ icon: Icon, label }: any) {
  return (
    <button className="p-4 bg-gray-800 hover:bg-gray-700 rounded-lg flex flex-col items-center gap-2 transition-colors">
      <Icon className="w-6 h-6 text-yellow-500" />
      <span className="text-xs text-gray-300">{label}</span>
    </button>
  );
}

function HealthItem({ label, status }: any) {
  const statusConfig = {
    operational: { icon: CheckCircle2, color: 'text-green-500', bg: 'bg-green-500/10' },
    warning: { icon: AlertCircle, color: 'text-yellow-500', bg: 'bg-yellow-500/10' },
    error: { icon: AlertCircle, color: 'text-red-500', bg: 'bg-red-500/10' }
  };

  const config = statusConfig[status as keyof typeof statusConfig];
  const Icon = config.icon;

  return (
    <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
      <span className="text-white">{label}</span>
      <div className={`flex items-center gap-2 px-3 py-1 ${config.bg} rounded-full`}>
        <Icon className={`w-4 h-4 ${config.color}`} />
        <span className={`text-sm ${config.color} capitalize`}>{status}</span>
      </div>
    </div>
  );
}

function ToggleOption({ label, enabled, description, onChange }: any) {
  const [isEnabled, setIsEnabled] = useState(enabled);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setIsEnabled(enabled);
  }, [enabled]);

  const handleToggle = async () => {
    if (loading) return;
    setLoading(true);
    const newValue = !isEnabled;
    setIsEnabled(newValue); // Optimistic update
    
    try {
      await onChange(newValue);
    } catch (error) {
      // Revert on error
      setIsEnabled(!newValue);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
      <div>
        <div className="text-white font-medium">{label}</div>
        <div className="text-xs text-gray-400 mt-1">{description}</div>
      </div>
      <button
        onClick={handleToggle}
        disabled={loading}
        className={`w-12 h-6 rounded-full transition-all relative ${
          isEnabled ? 'bg-green-500' : 'bg-gray-600'
        } ${loading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}`}
      >
        <div className={`w-5 h-5 bg-white rounded-full transition-all absolute top-0.5 ${
          isEnabled ? 'translate-x-6' : 'translate-x-1'
        }`} />
      </button>
    </div>
  );
}
