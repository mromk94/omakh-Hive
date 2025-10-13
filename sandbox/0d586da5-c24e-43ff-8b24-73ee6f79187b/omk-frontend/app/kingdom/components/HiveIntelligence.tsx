'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Activity, MessageSquare, Zap, TrendingUp, AlertCircle,
  CheckCircle, Clock, Users, BarChart3, Search, RefreshCw, Wifi, WifiOff
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useHiveWebSocket } from '@/app/hooks/useWebSocket';

const BACKEND_URL = 'http://localhost:8001';

export default function HiveIntelligence() {
  const [overview, setOverview] = useState<any>(null);
  const [messageStats, setMessageStats] = useState<any>(null);
  const [boardStats, setBoardStats] = useState<any>(null);
  const [beePerformance, setBeePerformance] = useState<any>(null);
  const [liveActivity, setLiveActivity] = useState<any>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // WebSocket connection for real-time updates
  const { isConnected } = useHiveWebSocket((data) => {
    // Update all state from WebSocket data
    if (data.overview) setOverview(data.overview);
    if (data.message_stats) setMessageStats(data.message_stats);
    if (data.board_stats) setBoardStats(data.board_stats);
    if (data.bee_performance) setBeePerformance(data.bee_performance);
    if (data.live_activity) setLiveActivity(data.live_activity);
    
    setLastUpdate(new Date());
    if (loading) {
      console.log('✅ Hive Intelligence data loaded via WebSocket');
      setLoading(false);
    }
  });

  // Fallback: Initial fetch if WebSocket fails
  useEffect(() => {
    if (!isConnected) {
      fetchAllData();
    }
  }, [isConnected]);

  const fetchAllData = async () => {
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const headers = { 'Authorization': `Bearer ${token}` };

      const [overviewRes, messageRes, boardRes, perfRes, activityRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/v1/admin/hive/overview`, { headers }),
        fetch(`${BACKEND_URL}/api/v1/admin/hive/message-bus/stats`, { headers }),
        fetch(`${BACKEND_URL}/api/v1/admin/hive/board/stats`, { headers }),
        fetch(`${BACKEND_URL}/api/v1/admin/hive/bees/performance`, { headers }),
        fetch(`${BACKEND_URL}/api/v1/admin/hive/activity/live`, { headers }),
      ]);

      const [overviewData, messageData, boardData, perfData, activityData] = await Promise.all([
        overviewRes.json(),
        messageRes.json(),
        boardRes.json(),
        perfRes.json(),
        activityRes.json(),
      ]);

      if (overviewData.success) setOverview(overviewData.overview);
      if (messageData.success) setMessageStats(messageData.stats);
      if (boardData.success) setBoardStats(boardData.stats);
      if (perfData.success) setBeePerformance(perfData.performance);
      if (activityData.success) setLiveActivity(activityData.active_tasks || []);

      setLastUpdate(new Date());
      if (loading) {
        console.log('✅ Hive Intelligence data loaded (HTTP fallback)');
      }
      setLoading(false);
    } catch (error: any) {
      console.error('Failed to fetch hive data:', error);
      if (loading) {
        toast.error(`Error loading hive data: ${error?.message || 'Unknown error'}`);
      }
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-yellow-500">Loading Hive Intelligence...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Last Update */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            Hive Intelligence
            {isConnected ? (
              <span className="flex items-center gap-1 text-xs text-green-500">
                <Wifi className="w-3 h-3" />
                Live
              </span>
            ) : (
              <span className="flex items-center gap-1 text-xs text-gray-500">
                <WifiOff className="w-3 h-3" />
                Polling
              </span>
            )}
          </h3>
          <p className="text-sm text-gray-400">Real-time visibility into bee operations</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-400">
            Updated: {lastUpdate.toLocaleTimeString()}
          </div>
          <button
            onClick={fetchAllData}
            className="px-3 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg flex items-center gap-2 text-black text-sm"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      {overview && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            icon={Users}
            label="Active Bees"
            value={`${overview.bees.currently_active}/${overview.bees.total}`}
            subtitle={`${overview.bees.healthy} healthy`}
            color="blue"
          />
          <StatCard
            icon={MessageSquare}
            label="Messages"
            value={overview.message_bus.total_messages}
            subtitle={`${overview.message_bus.delivery_rate.toFixed(1)}% delivered`}
            color="green"
          />
          <StatCard
            icon={Activity}
            label="Board Posts"
            value={overview.hive_board.total_posts}
            subtitle={`${overview.hive_board.active_categories} categories`}
            color="purple"
          />
          <StatCard
            icon={Zap}
            label="Queen Decisions"
            value={overview.queen.decision_count}
            subtitle={overview.queen.running ? 'Running' : 'Stopped'}
            color="yellow"
          />
        </div>
      )}

      {/* Live Activity Feed */}
      <LiveActivityFeed activities={liveActivity} />

      {/* Message Bus Stats */}
      {messageStats && <MessageBusStats stats={messageStats} />}

      {/* Bee Performance Grid */}
      {beePerformance && <BeePerformanceGrid performance={beePerformance} />}

      {/* Hive Board Stats */}
      {boardStats && <HiveBoardStats stats={boardStats} />}
    </div>
  );
}

// ==================== SUB-COMPONENTS ====================

function StatCard({ icon: Icon, label, value, subtitle, color }: any) {
  const colors: any = {
    blue: 'from-blue-600/20 to-blue-700/20 border-blue-500/30',
    green: 'from-green-600/20 to-green-700/20 border-green-500/30',
    purple: 'from-purple-600/20 to-purple-700/20 border-purple-500/30',
    yellow: 'from-yellow-600/20 to-yellow-700/20 border-yellow-500/30',
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`bg-gradient-to-br ${colors[color]} border rounded-xl p-6`}
    >
      <div className="flex items-center justify-between mb-4">
        <Icon className="w-8 h-8 text-gray-400" />
      </div>
      <div className="text-3xl font-bold text-white mb-1">{value}</div>
      <div className="text-sm text-gray-400">{label}</div>
      <div className="text-xs text-gray-500 mt-1">{subtitle}</div>
    </motion.div>
  );
}

function LiveActivityFeed({ activities }: any) {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5 text-yellow-500" />
        <h4 className="text-lg font-semibold text-white">Live Activity</h4>
        <span className="ml-auto text-sm text-gray-400">Last 10 seconds</span>
      </div>

      {activities.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No active tasks at the moment
        </div>
      ) : (
        <div className="space-y-2">
          {activities.map((activity: any, index: number) => (
            <motion.div
              key={activity.bee_name + index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg"
            >
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-white font-medium">{activity.bee_name}</span>
                <span className="text-sm text-gray-400">{activity.status}</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <Clock className="w-3 h-3" />
                {activity.seconds_ago}s ago
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

function MessageBusStats({ stats }: any) {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <MessageSquare className="w-5 h-5 text-yellow-500" />
        <h4 className="text-lg font-semibold text-white">Message Bus Statistics</h4>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-2xl font-bold text-white mb-1">
            {stats.total_messages}
          </div>
          <div className="text-sm text-gray-400">Total Messages</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-400 mb-1">
            {stats.delivery_rate.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-400">Delivery Rate</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-400 mb-1">
            {stats.active_bees}
          </div>
          <div className="text-sm text-gray-400">Active Bees</div>
        </div>
      </div>

      {/* Messages by Type */}
      <div className="mb-4">
        <div className="text-sm font-medium text-gray-400 mb-2">Messages by Type</div>
        <div className="space-y-2">
          {Object.entries(stats.by_type).map(([type, count]: any) => (
            <div key={type} className="flex items-center justify-between text-sm">
              <span className="text-gray-300 capitalize">{type}</span>
              <span className="text-white font-medium">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Top Senders */}
      <div>
        <div className="text-sm font-medium text-gray-400 mb-2">Top Communicators</div>
        <div className="space-y-2">
          {Object.entries(stats.by_sender)
            .sort(([, a]: any, [, b]: any) => b - a)
            .slice(0, 5)
            .map(([sender, count]: any) => (
              <div key={sender} className="flex items-center justify-between text-sm">
                <span className="text-gray-300">{sender}</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-yellow-500 h-2 rounded-full"
                      style={{ width: `${(count / stats.total_messages) * 100}%` }}
                    />
                  </div>
                  <span className="text-white font-medium w-8 text-right">{count}</span>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

function BeePerformanceGrid({ performance }: any) {
  const bees = Object.entries(performance);

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <BarChart3 className="w-5 h-5 text-yellow-500" />
        <h4 className="text-lg font-semibold text-white">Bee Performance</h4>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {bees.map(([name, stats]: any) => (
          <motion.div
            key={name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gray-800/50 rounded-lg p-4"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-white font-medium">{name}</span>
              {stats.llm_enabled && (
                <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded">
                  LLM
                </span>
              )}
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Tasks</span>
                <span className="text-white">{stats.task_count}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Success Rate</span>
                <span className={`font-medium ${
                  stats.success_rate >= 95 ? 'text-green-400' :
                  stats.success_rate >= 80 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {stats.success_rate.toFixed(1)}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Status</span>
                <span className={`text-xs px-2 py-1 rounded ${
                  stats.status === 'active' ? 'bg-green-500/20 text-green-400' :
                  stats.status === 'error' ? 'bg-red-500/20 text-red-400' :
                  'bg-gray-600/20 text-gray-400'
                }`}>
                  {stats.status}
                </span>
              </div>
              {stats.last_task_time && (
                <div className="text-xs text-gray-500 mt-2">
                  Last active: {new Date(stats.last_task_time).toLocaleString()}
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function HiveBoardStats({ stats }: any) {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <Search className="w-5 h-5 text-yellow-500" />
        <h4 className="text-lg font-semibold text-white">Hive Board Activity</h4>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Posts by Category */}
        <div>
          <div className="text-sm font-medium text-gray-400 mb-3">Posts by Category</div>
          <div className="space-y-2">
            {Object.entries(stats.posts_by_category).map(([category, count]: any) => (
              <div key={category} className="flex items-center justify-between text-sm">
                <span className="text-gray-300 capitalize">{category.replace('_', ' ')}</span>
                <span className="text-white font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Most Viewed Posts */}
        <div>
          <div className="text-sm font-medium text-gray-400 mb-3">Most Viewed Posts</div>
          <div className="space-y-3">
            {stats.most_viewed.map((post: any, index: number) => (
              <div key={index} className="bg-gray-800/50 rounded-lg p-3">
                <div className="text-sm text-white font-medium mb-1">{post.title}</div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-400">by {post.author}</span>
                  <span className="text-yellow-500">{post.views} views</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
