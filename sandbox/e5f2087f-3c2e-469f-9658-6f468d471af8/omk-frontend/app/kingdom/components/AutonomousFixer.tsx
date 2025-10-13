'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bug, Send, Loader2, CheckCircle2, XCircle, Clock,
  AlertTriangle, Code, TestTube, Zap, Shield, Eye,
  Play, RefreshCw, TrendingUp, GitBranch, FileCode
} from 'lucide-react';
import { toast } from 'react-hot-toast';

const BACKEND_URL = 'http://localhost:8001';

interface FixAttempt {
  fix_id: string;
  status: string;
  analysis: any;
  approaches_tested: number;
  best_approach: any;
  proposal_id: string;
  test_results: any[];
  auto_applied: boolean;
  requires_admin_approval: boolean;
  timestamp: string;
}

export default function AutonomousFixer() {
  const [bugDescription, setBugDescription] = useState('');
  const [processing, setProcessing] = useState(false);
  const [activeFixes, setActiveFixes] = useState<FixAttempt[]>([]);
  const [selectedFix, setSelectedFix] = useState<FixAttempt | null>(null);
  const [indexingStatus, setIndexingStatus] = useState<any>(null);

  useEffect(() => {
    loadActiveFixes();
    checkIndexingStatus();
  }, []);

  const loadActiveFixes = async () => {
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/autonomous/fixes`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const data = await response.json();
      if (data.success) {
        setActiveFixes(data.fixes || []);
      }
    } catch (error) {
      console.error('Failed to load fixes:', error);
    }
  };

  const checkIndexingStatus = async () => {
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/autonomous/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const data = await response.json();
      if (data.success) {
        setIndexingStatus(data.status);
      }
    } catch (error) {
      console.error('Failed to check status:', error);
    }
  };

  const indexCodebase = async () => {
    try {
      toast.loading('Indexing codebase...');
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/autonomous/index-codebase`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ force: true })
      });

      const data = await response.json();
      toast.dismiss();
      
      if (data.success) {
        toast.success(`✅ Indexed ${data.stats.python_files + data.stats.typescript_files} files`);
        checkIndexingStatus();
      } else {
        toast.error('Indexing failed');
      }
    } catch (error) {
      toast.dismiss();
      toast.error('Indexing failed');
    }
  };

  const submitBugReport = async () => {
    if (!bugDescription.trim() || processing) return;

    setProcessing(true);
    const bugText = bugDescription.trim();
    setBugDescription('');

    try {
      toast.loading('Queen is analyzing the bug...', { duration: 5000 });

      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/autonomous/fix-bug`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          bug_description: bugText,
          num_approaches: 3,
          auto_apply_if_safe: false
        })
      });

      const data = await response.json();
      toast.dismiss();

      if (data.success) {
        toast.success('✅ Bug analysis complete!');
        loadActiveFixes();
        
        // Auto-select the new fix
        if (data.fix_id) {
          const newFix = activeFixes.find(f => f.fix_id === data.fix_id) || data;
          setSelectedFix(newFix);
        }
      } else {
        toast.error(`Failed: ${data.error || 'Unknown error'}`);
      }
    } catch (error: any) {
      toast.dismiss();
      toast.error(`Error: ${error.message}`);
    } finally {
      setProcessing(false);
    }
  };

  const approveFix = async (fixId: string) => {
    try {
      toast.loading('Applying fix...');
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/autonomous/fixes/${fixId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ notes: 'Approved from admin dashboard' })
      });

      const data = await response.json();
      toast.dismiss();

      if (data.success) {
        toast.success('✅ Fix applied successfully!');
        loadActiveFixes();
      } else {
        toast.error(`Failed to apply: ${data.error}`);
      }
    } catch (error) {
      toast.dismiss();
      toast.error('Failed to apply fix');
    }
  };

  const rejectFix = async (fixId: string) => {
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/autonomous/fixes/${fixId}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason: 'Rejected from admin dashboard' })
      });

      const data = await response.json();
      if (data.success) {
        toast.success('Fix rejected');
        loadActiveFixes();
        setSelectedFix(null);
      }
    } catch (error) {
      toast.error('Failed to reject fix');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500 bg-red-500/10';
      case 'high': return 'text-orange-500 bg-orange-500/10';
      case 'medium': return 'text-yellow-500 bg-yellow-500/10';
      default: return 'text-blue-500 bg-blue-500/10';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'applied': return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'rejected': return <XCircle className="w-5 h-5 text-red-500" />;
      case 'awaiting_approval': return <Clock className="w-5 h-5 text-yellow-500" />;
      default: return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
    }
  };

  return (
    <div className="grid grid-cols-12 gap-6">
      {/* Left Panel - Bug Report & Status */}
      <div className="col-span-12 lg:col-span-5 space-y-6">
        {/* System Status */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Shield className="w-5 h-5 text-purple-500" />
              Autonomous System Status
            </h3>
            <button
              onClick={checkIndexingStatus}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4 text-gray-400" />
            </button>
          </div>

          {indexingStatus && (
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                <span className="text-sm text-gray-400">Codebase Indexed</span>
                <span className="text-sm font-semibold text-white">
                  {indexingStatus.codebase_indexed ? (
                    <span className="text-green-500">✅ {indexingStatus.indexed_files} files</span>
                  ) : (
                    <span className="text-yellow-500">⚠️ Not indexed</span>
                  )}
                </span>
              </div>

              {!indexingStatus.codebase_indexed && (
                <button
                  onClick={indexCodebase}
                  className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <GitBranch className="w-4 h-4" />
                  Index Codebase Now
                </button>
              )}

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-gray-800/50 rounded-lg text-center">
                  <div className="text-2xl font-bold text-yellow-500">
                    {indexingStatus.active_fixes || 0}
                  </div>
                  <div className="text-xs text-gray-400">Active Fixes</div>
                </div>
                <div className="p-3 bg-gray-800/50 rounded-lg text-center">
                  <div className="text-2xl font-bold text-green-500">
                    {indexingStatus.fixes_by_status?.applied || 0}
                  </div>
                  <div className="text-xs text-gray-400">Applied</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Bug Report Input */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Bug className="w-5 h-5 text-red-500" />
            Report a Bug
          </h3>

          <div className="space-y-4">
            <textarea
              value={bugDescription}
              onChange={(e) => setBugDescription(e.target.value)}
              placeholder="Describe the bug in detail...&#10;&#10;Example: 'Users getting wrong password error even when entering correct password. Happening in login form on /login page.'"
              className="w-full h-32 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 resize-none"
              disabled={processing}
            />

            <button
              onClick={submitBugReport}
              disabled={!bugDescription.trim() || processing}
              className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600 disabled:from-gray-700 disabled:to-gray-700 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2"
            >
              {processing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Queen is analyzing...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Analyze & Fix Autonomously
                </>
              )}
            </button>
          </div>
        </div>

        {/* Active Fixes List */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-4">Recent Fixes</h3>

          <div className="space-y-3">
            {activeFixes.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Bug className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No fixes yet</p>
              </div>
            ) : (
              activeFixes.map((fix) => (
                <motion.button
                  key={fix.fix_id}
                  onClick={() => setSelectedFix(fix)}
                  className={`w-full p-4 rounded-lg border transition-all text-left ${
                    selectedFix?.fix_id === fix.fix_id
                      ? 'bg-purple-500/10 border-purple-500'
                      : 'bg-gray-800/50 border-gray-700 hover:border-gray-600'
                  }`}
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="flex items-start gap-3">
                    {getStatusIcon(fix.status)}
                    <div className="flex-1">
                      <div className="font-semibold text-white text-sm mb-1">
                        Fix #{fix.fix_id.slice(0, 8)}
                      </div>
                      <div className="text-xs text-gray-400">
                        {fix.approaches_tested} approaches tested
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded text-xs font-bold ${
                      getSeverityColor(fix.analysis?.severity || 'medium')
                    }`}>
                      {fix.analysis?.severity || 'medium'}
                    </div>
                  </div>
                </motion.button>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Right Panel - Fix Details */}
      <div className="col-span-12 lg:col-span-7">
        {selectedFix ? (
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-xl font-bold text-white mb-2">
                  Fix #{selectedFix.fix_id.slice(0, 8)}
                </h3>
                <div className="flex items-center gap-2">
                  {getStatusIcon(selectedFix.status)}
                  <span className="text-sm text-gray-400">
                    {selectedFix.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
              <div className={`px-3 py-1 rounded-lg text-sm font-bold ${
                getSeverityColor(selectedFix.analysis?.severity || 'medium')
              }`}>
                {selectedFix.analysis?.severity || 'medium'} severity
              </div>
            </div>

            {/* Analysis */}
            <div className="p-4 bg-gray-800/50 rounded-lg">
              <h4 className="text-sm font-semibold text-white mb-2">Root Cause Analysis</h4>
              <p className="text-sm text-gray-300">
                {selectedFix.analysis?.root_cause || 'Analyzing...'}
              </p>
            </div>

            {/* Test Results */}
            <div>
              <h4 className="text-sm font-semibold text-white mb-3">
                Test Results ({selectedFix.approaches_tested} approaches tested)
              </h4>
              <div className="space-y-2">
                {selectedFix.test_results?.map((result, idx) => (
                  <div key={idx} className="p-3 bg-gray-800/50 rounded-lg flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <TestTube className="w-4 h-4 text-blue-400" />
                      <span className="text-sm text-gray-300">{result.approach}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-400">
                        {result.tests_passed} tests
                      </span>
                      {result.success ? (
                        <CheckCircle2 className="w-4 h-4 text-green-500" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-500" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Best Approach */}
            {selectedFix.best_approach && (
              <div className="p-4 bg-gradient-to-r from-green-500/10 to-transparent border border-green-500/20 rounded-lg">
                <h4 className="text-sm font-semibold text-green-400 mb-2 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Recommended Fix
                </h4>
                <p className="text-sm text-gray-300 mb-3">
                  {selectedFix.best_approach.description}
                </p>
                <div className="flex items-center gap-4 text-xs">
                  <span className="text-gray-400">
                    Risk: <span className="font-semibold text-white">{selectedFix.best_approach.risk_level}</span>
                  </span>
                  <span className="text-gray-400">
                    Success: <span className="font-semibold text-white">{(selectedFix.best_approach.success_rate * 100).toFixed(0)}%</span>
                  </span>
                </div>
              </div>
            )}

            {/* Actions */}
            {selectedFix.requires_admin_approval && selectedFix.status === 'awaiting_approval' && (
              <div className="flex gap-3">
                <button
                  onClick={() => approveFix(selectedFix.fix_id)}
                  className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <CheckCircle2 className="w-5 h-5" />
                  Approve & Deploy
                </button>
                <button
                  onClick={() => rejectFix(selectedFix.fix_id)}
                  className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <XCircle className="w-5 h-5" />
                  Reject
                </button>
              </div>
            )}

            {selectedFix.auto_applied && (
              <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                <p className="text-sm text-green-400 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  This fix was automatically applied because it passed all tests and had low risk.
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-12 text-center">
            <FileCode className="w-16 h-16 mx-auto mb-4 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-400 mb-2">
              No Fix Selected
            </h3>
            <p className="text-sm text-gray-500">
              Submit a bug report or select an existing fix to view details
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
