'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, TrendingUp, AlertCircle, CheckCircle, Shield, Zap,
  Code, RefreshCw, Play, Clock, BarChart3, Target, Loader
} from 'lucide-react';
import { toast } from 'react-hot-toast';

const BACKEND_URL = 'http://localhost:8001';

interface Recommendation {
  title: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  impact: string;
  status: 'pending' | 'in_progress' | 'completed';
  estimatedImprovement: string;
  files: string[];
}

interface AnalysisData {
  timestamp: string;
  overallScore: number;
  dataFlow: {
    score: number;
    bottlenecks: string[];
    strengths: string[];
  };
  security: {
    coverage: number;
    integrationPoints: number;
    recommendations: string[];
  };
  performance: {
    avgLatency: number;
    securityGateLatency: number;
    llmLatency: number;
  };
  recommendations: Recommendation[];
}

export default function ClaudeSystemAnalysis() {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [implementing, setImplementing] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalysisData();
  }, []);

  const fetchAnalysisData = async () => {
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/admin/claude/analysis`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      console.log('✅ Analysis data loaded:', data);
      setAnalysisData(data);
    } catch (error: any) {
      console.error('Failed to fetch analysis:', error);
      toast.error(`Error loading analysis: ${error?.message || 'Unknown error'}`);
      setAnalysisData(null);
    } finally {
      setLoading(false);
    }
  };

  const requestImplementation = async (recommendationTitle: string) => {
    setImplementing(recommendationTitle);
    try {
      toast.loading('Claude is generating implementation...', { id: 'implementing' });
      
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/admin/claude/implement`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ recommendation: recommendationTitle })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      
      toast.dismiss('implementing');
      
      if (result.success && result.proposal_created) {
        toast.success('✅ Code proposal created! Redirecting to Queen Development...', {
          duration: 2000
        });
        
        await fetchAnalysisData(); // Refresh data
        
        // Navigate to Queen Development with proposal
        setTimeout(() => {
          window.location.href = result.navigate_to;
        }, 1500);
      } else if (result.success) {
        toast.success(`✅ Implementation generated!`);
        await fetchAnalysisData();
      } else {
        toast.error(result.error || 'Failed to generate implementation');
      }
    } catch (error: any) {
      toast.dismiss('implementing');
      console.error('Failed to request implementation:', error);
      toast.error(`❌ ${error?.message || 'Failed to generate implementation'}`);
    } finally {
      setImplementing(null);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'red';
      case 'high': return 'yellow';
      case 'medium': return 'blue';
      case 'low': return 'gray';
      default: return 'gray';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'in_progress': return <Clock className="h-4 w-4 text-yellow-500 animate-pulse" />;
      default: return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader className="w-8 h-8 text-yellow-500 animate-spin" />
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="bg-gray-900/50 border border-gray-700 rounded-xl p-8 text-center">
        <AlertCircle className="w-12 h-12 text-gray-500 mx-auto mb-4" />
        <h3 className="text-lg font-bold text-white mb-2">No Analysis Data</h3>
        <p className="text-gray-400 mb-4">Run a system analysis to see results here.</p>
        <button
          onClick={fetchAnalysisData}
          className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-black rounded-lg font-semibold transition-all"
        >
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-yellow-500 to-yellow-300 bg-clip-text text-transparent">
            Claude System Analysis
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Last updated: {new Date(analysisData.timestamp).toLocaleString()}
          </p>
        </div>
        <button
          onClick={fetchAnalysisData}
          className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg font-medium transition-all flex items-center gap-2 border border-gray-700"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-yellow-900/20 to-yellow-800/10 border border-yellow-500/30 rounded-xl p-5"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-yellow-500/20 rounded-lg">
              <Target className="w-5 h-5 text-yellow-500" />
            </div>
            <span className="text-sm font-medium text-gray-400">Overall Score</span>
          </div>
          <div className="text-3xl font-bold text-white">{analysisData?.overallScore || 0}/10</div>
          <p className="text-xs text-gray-500 mt-1">System efficiency</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-br from-green-900/20 to-green-800/10 border border-green-500/30 rounded-xl p-5"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Shield className="w-5 h-5 text-green-500" />
            </div>
            <span className="text-sm font-medium text-gray-400">Security</span>
          </div>
          <div className="text-3xl font-bold text-white">{analysisData?.security?.coverage || 0}%</div>
          <p className="text-xs text-gray-500 mt-1">{analysisData?.security?.integrationPoints || 0} integration points</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-blue-900/20 to-blue-800/10 border border-blue-500/30 rounded-xl p-5"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Zap className="w-5 h-5 text-blue-500" />
            </div>
            <span className="text-sm font-medium text-gray-400">Avg Latency</span>
          </div>
          <div className="text-3xl font-bold text-white">{analysisData?.performance?.avgLatency || 0}ms</div>
          <p className="text-xs text-gray-500 mt-1">Security: {analysisData?.performance?.securityGateLatency || 0}ms</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-br from-purple-900/20 to-purple-800/10 border border-purple-500/30 rounded-xl p-5"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <TrendingUp className="w-5 h-5 text-purple-500" />
            </div>
            <span className="text-sm font-medium text-gray-400">Recommendations</span>
          </div>
          <div className="text-3xl font-bold text-white">{analysisData?.recommendations?.length || 0}</div>
          <p className="text-xs text-gray-500 mt-1">
            {analysisData?.recommendations?.filter(r => r.priority === 'critical' || r.priority === 'high').length || 0} high priority
          </p>
        </motion.div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-700">
        {['overview', 'recommendations', 'performance', 'security'].map((tab) => (
          <button
            key={tab}
            onClick={() => setSelectedTab(tab)}
            className={`px-4 py-3 font-medium transition-all capitalize ${
              selectedTab === tab
                ? 'text-yellow-500 border-b-2 border-yellow-500'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={selectedTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          {selectedTab === 'overview' && (
            <div className="space-y-4">
              {/* Data Flow */}
              <div className="bg-gray-900/50 border border-gray-700 rounded-xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-yellow-500" />
                  Data Flow Analysis
                  <span className="ml-auto text-sm font-normal text-gray-400">
                    Score: {analysisData?.dataFlow?.score || 0}/10
                  </span>
                </h3>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold text-white mb-2 flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      Strengths
                    </h4>
                    <ul className="space-y-1">
                      {analysisData?.dataFlow?.strengths?.map((strength, idx) => (
                        <li key={idx} className="text-sm text-gray-400 pl-4 border-l-2 border-green-500/30">
                          {strength}
                        </li>
                      )) || <li className="text-sm text-gray-500">No data available</li>}
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-white mb-2 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-yellow-500" />
                      Bottlenecks
                    </h4>
                    <ul className="space-y-1">
                      {analysisData?.dataFlow?.bottlenecks?.map((bottleneck, idx) => (
                        <li key={idx} className="text-sm text-yellow-400 pl-4 border-l-2 border-yellow-500/30">
                          {bottleneck}
                        </li>
                      )) || <li className="text-sm text-gray-500">No data available</li>}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {selectedTab === 'recommendations' && (
            <div className="space-y-4">
              {(analysisData?.recommendations || []).map((rec, idx) => {
                const color = getPriorityColor(rec.priority);
                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className={`bg-gradient-to-r from-${color}-900/10 to-transparent border border-${color}-500/30 rounded-xl p-6`}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          {getStatusIcon(rec.status)}
                          <h3 className="text-lg font-bold text-white">{rec.title}</h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-bold bg-${color}-500/20 text-${color}-400 uppercase`}>
                            {rec.priority}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400">{rec.impact}</p>
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <span className="text-xs font-semibold text-gray-500 uppercase">Expected Improvement</span>
                        <p className="text-sm text-green-400 font-medium mt-1">{rec.estimatedImprovement}</p>
                      </div>
                      <div>
                        <span className="text-xs font-semibold text-gray-500 uppercase">Status</span>
                        <p className="text-sm text-white font-medium mt-1 capitalize">{rec.status.replace('_', ' ')}</p>
                      </div>
                    </div>

                    <div className="mb-4">
                      <span className="text-xs font-semibold text-gray-500 uppercase">Files to Modify</span>
                      <div className="mt-2 space-y-1">
                        {rec.files.map((file, i) => (
                          <div key={i} className="text-xs bg-black/30 p-2 rounded font-mono text-gray-300 flex items-center gap-2">
                            <Code className="w-3 h-3" />
                            {file}
                          </div>
                        ))}
                      </div>
                    </div>

                    {rec.status === 'pending' && (
                      <button
                        onClick={() => requestImplementation(rec.title)}
                        disabled={implementing === rec.title}
                        className="w-full px-4 py-3 bg-yellow-500 hover:bg-yellow-600 disabled:bg-gray-700 disabled:text-gray-500 text-black font-semibold rounded-lg transition-all flex items-center justify-center gap-2"
                      >
                        {implementing === rec.title ? (
                          <>
                            <Loader className="w-4 h-4 animate-spin" />
                            Creating Code Proposal...
                          </>
                        ) : (
                          <>
                            <Code className="w-4 h-4" />
                            Create Code Proposal
                          </>
                        )}
                      </button>
                    )}
                    {rec.status === 'completed' && (
                      <div className="w-full px-4 py-3 bg-green-500/20 border border-green-500/30 text-green-400 font-semibold rounded-lg flex items-center justify-center gap-2">
                        <CheckCircle className="w-4 h-4" />
                        Implementation Completed
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          )}

          {selectedTab === 'performance' && (
            <div className="bg-gray-900/50 border border-gray-700 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-6">Performance Metrics</h3>
              
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-gray-400">Security Gate Latency</span>
                    <span className="text-sm font-semibold text-white">{analysisData?.performance?.securityGateLatency || 0}ms</span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-3">
                    <div 
                      className="bg-gradient-to-r from-blue-600 to-blue-400 h-3 rounded-full transition-all" 
                      style={{ width: `${((analysisData?.performance?.securityGateLatency || 0) / (analysisData?.performance?.avgLatency || 1)) * 100}%` }}
                    ></div>
                    <span className="font-bold text-xl text-yellow-500">{analysisData?.performance?.avgLatency || 0}ms</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {selectedTab === 'security' && (
            <div className="bg-gray-900/50 border border-gray-700 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-6">Security Assessment</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-green-900/20 border border-green-500/30 rounded-lg">
                  <div>
                    <h4 className="font-semibold text-white">Coverage</h4>
                    <p className="text-sm text-gray-400">All critical endpoints secured</p>
                  </div>
                  <div className="text-3xl font-bold text-green-500">{analysisData?.security?.coverage || 0}%</div>
                </div>

                <div className="flex items-center justify-between p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
                  <div>
                    <h4 className="font-semibold text-white">Integration Points</h4>
                    <p className="text-sm text-gray-400">Security gate integrations</p>
                  </div>
                  <div className="text-3xl font-bold text-blue-500">{analysisData?.security?.integrationPoints || 0}</div>
                </div>

                {(analysisData?.security?.recommendations?.length || 0) > 0 && (
                  <div className="pt-4 border-t border-gray-700">
                    <h4 className="font-semibold text-white mb-3">Security Recommendations</h4>
                    <ul className="space-y-2">
                      {(analysisData?.security?.recommendations || []).map((rec, idx) => (
                        <li key={idx} className="text-sm text-gray-300 pl-4 border-l-2 border-yellow-500/30 flex items-center gap-2">
                          <Shield className="w-4 h-4 text-yellow-500" />
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
