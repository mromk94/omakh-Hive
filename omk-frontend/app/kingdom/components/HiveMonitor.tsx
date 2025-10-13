'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { API_ENDPOINTS } from '@/lib/constants';
import { Activity, CheckCircle2, AlertCircle, Clock, Zap } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface Bee {
  bee_id: number;
  name: string;
  role: string;
  status: string;
  tasks_completed: number;
  tasks_pending: number;
  last_active: string;
}

export default function HiveMonitor() {
  const [bees, setBees] = useState<Bee[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedBee, setSelectedBee] = useState<Bee | null>(null);
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
    loadBees();
    // Reduced from 5s to 15s - more reasonable for bee monitoring
    // TODO: Replace with WebSocket for true real-time updates
    const interval = setInterval(() => {
      if (isVisible) {
        loadBees();
      }
    }, 15000); // Refresh every 15s when visible
    return () => clearInterval(interval);
  }, [isVisible]);

  const loadBees = async () => {
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${API_ENDPOINTS.ADMIN}/queen/bees`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      if (data.success && data.bees) {
        // Transform bee data into display format
        const formattedBees: Bee[] = data.bees.map((bee: any, index: number) => ({
          bee_id: bee.bee_id || index + 1,
          name: bee.name || 'Unknown Bee',
          role: bee.role || 'General Purpose',
          status: bee.status || 'idle',
          tasks_completed: bee.tasks_completed || 0,
          tasks_pending: bee.tasks_pending || 0,
          last_active: bee.last_active || 'Unknown'
        }));
        setBees(formattedBees);
      } else {
        // If no real bees yet, show empty state
        setBees([]);
      }
    } catch (error) {
      console.error('Failed to load bees:', error);
      setBees([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-500 bg-green-500/10';
      case 'idle': return 'text-yellow-500 bg-yellow-500/10';
      case 'error': return 'text-red-500 bg-red-500/10';
      default: return 'text-gray-500 bg-gray-500/10';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return CheckCircle2;
      case 'idle': return Clock;
      case 'error': return AlertCircle;
      default: return Activity;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading hive data...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
          <div className="text-gray-400 text-sm mb-1">Total Bees</div>
          <div className="text-3xl font-bold text-white">{bees.length}</div>
        </div>
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
          <div className="text-gray-400 text-sm mb-1">Active</div>
          <div className="text-3xl font-bold text-green-500">
            {bees.filter(b => b.status === 'active').length}
          </div>
        </div>
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
          <div className="text-gray-400 text-sm mb-1">Tasks Pending</div>
          <div className="text-3xl font-bold text-yellow-500">
            {bees.reduce((sum, b) => sum + b.tasks_pending, 0)}
          </div>
        </div>
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
          <div className="text-gray-400 text-sm mb-1">Tasks Completed</div>
          <div className="text-3xl font-bold text-blue-500">
            {bees.reduce((sum, b) => sum + b.tasks_completed, 0)}
          </div>
        </div>
      </div>

      {/* Bee Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {bees.map((bee) => {
          const StatusIcon = getStatusIcon(bee.status);
          return (
            <motion.div
              key={bee.bee_id}
              whileHover={{ scale: 1.02 }}
              onClick={() => setSelectedBee(bee)}
              className="bg-gray-900/50 border border-gray-800 hover:border-yellow-600 rounded-xl p-5 cursor-pointer transition-all"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-yellow-500" />
                  <h3 className="text-white font-semibold">{bee.name}</h3>
                </div>
                <div className={`px-2 py-1 rounded-full flex items-center gap-1 ${getStatusColor(bee.status)}`}>
                  <StatusIcon className="w-3 h-3" />
                  <span className="text-xs capitalize">{bee.status}</span>
                </div>
              </div>

              <p className="text-sm text-gray-400 mb-4">{bee.role}</p>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Completed</span>
                  <span className="text-white font-semibold">{bee.tasks_completed}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Pending</span>
                  <span className="text-yellow-500 font-semibold">{bee.tasks_pending}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Last Active</span>
                  <span className="text-gray-400">{bee.last_active}</span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Bee Detail Modal */}
      {selectedBee && (
        <div 
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedBee(null)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-gray-900 border border-gray-800 rounded-xl p-6 max-w-2xl w-full"
          >
            <h2 className="text-2xl font-bold text-white mb-4">
              {selectedBee.name} Bee
            </h2>
            <div className="space-y-4">
              <div>
                <div className="text-sm text-gray-400 mb-1">Role</div>
                <div className="text-white">{selectedBee.role}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400 mb-1">Status</div>
                <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${getStatusColor(selectedBee.status)}`}>
                  {React.createElement(getStatusIcon(selectedBee.status), { className: 'w-4 h-4' })}
                  <span className="capitalize">{selectedBee.status}</span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-400 mb-1">Tasks Completed</div>
                  <div className="text-2xl font-bold text-white">{selectedBee.tasks_completed}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Tasks Pending</div>
                  <div className="text-2xl font-bold text-yellow-500">{selectedBee.tasks_pending}</div>
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-400 mb-1">Last Active</div>
                <div className="text-white">{selectedBee.last_active}</div>
              </div>
            </div>
            <button
              onClick={() => setSelectedBee(null)}
              className="mt-6 w-full py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
            >
              Close
            </button>
          </motion.div>
        </div>
      )}
    </div>
  );
}
