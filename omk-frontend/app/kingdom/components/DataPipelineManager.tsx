'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Database, Play, Pause, RefreshCw, Clock, CheckCircle, 
  XCircle, TrendingUp, Upload, Calendar, AlertCircle
} from 'lucide-react';
import { toast } from 'react-hot-toast';

const BACKEND_URL = 'http://localhost:8001';

interface PipelineStatus {
  run_count: number;
  error_count: number;
  last_run: string | null;
  last_success: string | null;
  schedule_interval_minutes: number;
  gcs_bucket: string;
  gcs_available: boolean;
}

interface PipelineRun {
  success: boolean;
  pipeline_run: number;
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  total_records?: number;
  csv_files_uploaded?: number;
  error?: string;
}

export default function DataPipelineManager() {
  const [status, setStatus] = useState<PipelineStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [lastRun, setLastRun] = useState<PipelineRun | null>(null);
  const [scheduleInterval, setScheduleInterval] = useState(15);

  useEffect(() => {
    loadPipelineStatus();
    // Refresh status every 30 seconds
    const interval = setInterval(loadPipelineStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadPipelineStatus = async () => {
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/admin/data-pipeline/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to load status');

      const data = await response.json();
      if (data.success) {
        setStatus(data.status);
      }
    } catch (error: any) {
      console.error('Failed to load pipeline status:', error);
    }
  };

  const runPipeline = async () => {
    setRunning(true);
    setLoading(true);

    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/admin/data-pipeline/run`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) throw new Error('Pipeline failed');

      const data = await response.json();
      
      if (data.success) {
        setLastRun(data);
        toast.success(`Pipeline completed! ${data.total_records} records collected`);
        await loadPipelineStatus();
      } else {
        toast.error(data.error || 'Pipeline failed');
      }
    } catch (error: any) {
      console.error('Pipeline error:', error);
      toast.error('Failed to run pipeline');
    } finally {
      setRunning(false);
      setLoading(false);
    }
  };

  const schedulePipeline = async () => {
    setLoading(true);

    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/admin/data-pipeline/schedule`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ interval_minutes: scheduleInterval })
      });

      if (!response.ok) throw new Error('Failed to schedule');

      const data = await response.json();
      
      if (data.success) {
        toast.success(`Pipeline scheduled every ${scheduleInterval} minutes`);
        await loadPipelineStatus();
      }
    } catch (error: any) {
      console.error('Schedule error:', error);
      toast.error('Failed to schedule pipeline');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Database className="w-6 h-6 text-blue-400" />
            Data Pipeline Manager
          </h2>
          <p className="text-gray-400 mt-1">Fivetran blockchain data collection</p>
        </div>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={runPipeline}
          disabled={running || loading}
          className={`
            px-6 py-3 rounded-lg font-medium flex items-center gap-2
            ${running ? 'bg-yellow-600' : 'bg-gradient-to-r from-blue-600 to-purple-600'}
            text-white shadow-lg
            ${(running || loading) ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-xl'}
          `}
        >
          {running ? (
            <>
              <RefreshCw className="w-5 h-5 animate-spin" />
              Running...
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              Run Pipeline Now
            </>
          )}
        </motion.button>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gray-800/50 backdrop-blur border border-gray-700 rounded-xl p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Runs</p>
              <p className="text-3xl font-bold text-white mt-1">
                {status?.run_count || 0}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-400" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gray-800/50 backdrop-blur border border-gray-700 rounded-xl p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Success Rate</p>
              <p className="text-3xl font-bold text-green-400 mt-1">
                {status ? Math.round(((status.run_count - status.error_count) / status.run_count) * 100) : 100}%
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-400" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gray-800/50 backdrop-blur border border-gray-700 rounded-xl p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Errors</p>
              <p className="text-3xl font-bold text-red-400 mt-1">
                {status?.error_count || 0}
              </p>
            </div>
            <XCircle className="w-8 h-8 text-red-400" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gray-800/50 backdrop-blur border border-gray-700 rounded-xl p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">GCS Status</p>
              <p className="text-lg font-bold text-white mt-1">
                {status?.gcs_available ? 'Connected' : 'Offline'}
              </p>
            </div>
            <Upload className={`w-8 h-8 ${status?.gcs_available ? 'text-green-400' : 'text-gray-500'}`} />
          </div>
        </motion.div>
      </div>

      {/* Last Run Details */}
      {lastRun && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gray-800/50 backdrop-blur border border-gray-700 rounded-xl p-6"
        >
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-400" />
            Last Pipeline Run
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-gray-400 text-sm">Run #</p>
              <p className="text-white font-medium">{lastRun.pipeline_run}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Records Collected</p>
              <p className="text-white font-medium">{lastRun.total_records || 0}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Files Uploaded</p>
              <p className="text-white font-medium">{lastRun.csv_files_uploaded || 0}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Duration</p>
              <p className="text-white font-medium">{lastRun.duration_seconds?.toFixed(1)}s</p>
            </div>
          </div>

          {lastRun.error && (
            <div className="mt-4 p-3 bg-red-900/20 border border-red-500/50 rounded-lg">
              <p className="text-red-400 text-sm">{lastRun.error}</p>
            </div>
          )}
        </motion.div>
      )}

      {/* Schedule Configuration */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-gray-800/50 backdrop-blur border border-gray-700 rounded-xl p-6"
      >
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-purple-400" />
          Pipeline Schedule
        </h3>

        <div className="space-y-4">
          <div>
            <label className="text-gray-400 text-sm block mb-2">
              Run Interval (minutes)
            </label>
            <div className="flex gap-2">
              {[15, 30, 60].map((interval) => (
                <button
                  key={interval}
                  onClick={() => setScheduleInterval(interval)}
                  className={`
                    px-4 py-2 rounded-lg font-medium
                    ${scheduleInterval === interval 
                      ? 'bg-purple-600 text-white' 
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}
                  `}
                >
                  {interval}m
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={schedulePipeline}
            disabled={loading}
            className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium disabled:opacity-50"
          >
            Update Schedule
          </button>

          {status && status.last_run && (
            <div className="p-3 bg-blue-900/20 border border-blue-500/50 rounded-lg">
              <p className="text-blue-400 text-sm">
                <strong>Last Run:</strong> {new Date(status.last_run).toLocaleString()}
              </p>
              <p className="text-blue-400 text-sm mt-1">
                <strong>Next Run:</strong> ~{status.schedule_interval_minutes} minutes
              </p>
            </div>
          )}
        </div>
      </motion.div>

      {/* Info Box */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/50 rounded-xl p-6"
      >
        <div className="flex items-start gap-3">
          <AlertCircle className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
          <div>
            <h4 className="text-white font-bold mb-2">Pipeline Information</h4>
            <ul className="text-gray-300 text-sm space-y-1">
              <li>• Collects blockchain transactions (Ethereum & Solana)</li>
              <li>• Monitors DEX pools (Uniswap liquidity & volume)</li>
              <li>• Tracks price oracles (Chainlink & Pyth feeds)</li>
              <li>• Converts to CSV format → Uploads to GCS → Syncs with BigQuery</li>
              <li>• GCS Bucket: <code className="text-blue-400">{status?.gcs_bucket}</code></li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
