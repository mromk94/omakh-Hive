'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageSquare, Send, Sparkles, Code, CheckCircle, XCircle,
  Clock, AlertTriangle, Loader, RefreshCw, Eye, Play, X,
  GitBranch, TestTube, Zap, Shield, TrendingUp, Database, Search
} from 'lucide-react';
import { toast } from 'react-hot-toast';

const BACKEND_URL = 'http://localhost:8001';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  code_proposal_created?: boolean;
  proposal_id?: string;
}

interface Proposal {
  id: string;
  title: string;
  description: string;
  priority: string;
  risk_level: string;
  status: string;
  created_at: string;
  files_to_modify: any[];
  test_results?: any;
  sandbox_path?: string;
}

export default function QueenDevelopmentHub() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [selectedProposal, setSelectedProposal] = useState<Proposal | null>(null);
  const [activeMode, setActiveMode] = useState<'chat' | 'bugs' | 'queries'>('chat');
  const [activeTab, setActiveTab] = useState<'chat' | 'proposals'>('chat');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConversationHistory();
    loadProposals();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadConversationHistory = async () => {
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/queen-dev/conversation-history`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      if (data.success) {
        setMessages(data.history || []);
        console.log(`✅ Loaded ${data.history?.length || 0} messages`);
      }
    } catch (error: any) {
      console.error('Failed to load history:', error);
      // Silent fail for history - not critical
    }
  };

  const loadProposals = async () => {
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${BACKEND_URL}/api/v1/queen-dev/proposals`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      if (data.success) {
        setProposals(data.proposals || []);
        console.log(`✅ Loaded ${data.proposals?.length || 0} proposals`);
      }
    } catch (error: any) {
      console.error('Failed to load proposals:', error);
      toast.error(`Error loading proposals: ${error?.message || 'Unknown error'}`);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);

    // Add user message
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }]);

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${BACKEND_URL}/api/v1/queen-dev/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: userMessage,
          include_system_info: true
        })
      });

      const data = await response.json();

      if (data.success) {
        // Add Queen's response
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response,
          timestamp: data.timestamp,
          code_proposal_created: data.code_proposal_created,
          proposal_id: data.proposal_id
        }]);

        // Reload proposals if one was created
        if (data.code_proposal_created) {
          await loadProposals();
        }
      }
    } catch (error) {
      console.error('Chat failed:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const analyzeSystem = async () => {
    setLoading(true);
    setMessages(prev => [...prev, {
      role: 'user',
      content: '[System Analysis Requested]',
      timestamp: new Date().toISOString()
    }]);

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${BACKEND_URL}/api/v1/queen-dev/analyze-system`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const data = await response.json();

      if (data.success) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.analysis,
          timestamp: new Date().toISOString(),
          code_proposal_created: data.code_proposal_created,
          proposal_id: data.proposal_id
        }]);

        if (data.code_proposal_created) {
          await loadProposals();
        }
      }
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-yellow-500" />
            Queen Development System
          </h3>
          <p className="text-sm text-gray-400">
            Autonomous AI-powered system development with Claude
          </p>
        </div>
        <button
          onClick={analyzeSystem}
          disabled={loading}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 rounded-lg flex items-center gap-2 text-white"
        >
          <Zap className="w-4 h-4" />
          Analyze System
        </button>
      </div>

      {/* Mode Selector */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <button
          onClick={() => setActiveMode('chat')}
          className={`p-4 rounded-lg border-2 transition-all ${
            activeMode === 'chat'
              ? 'bg-purple-500/20 border-purple-500'
              : 'bg-gray-800/50 border-gray-700 hover:border-gray-600'
          }`}
        >
          <MessageSquare className="w-5 h-5 mx-auto mb-2 text-purple-400" />
          <div className="text-sm font-semibold text-white">Chat & Proposals</div>
        </button>
        <button
          onClick={() => setActiveMode('bugs')}
          className={`p-4 rounded-lg border-2 transition-all ${
            activeMode === 'bugs'
              ? 'bg-purple-500/20 border-purple-500'
              : 'bg-gray-800/50 border-gray-700 hover:border-gray-600'
          }`}
        >
          <Shield className="w-5 h-5 mx-auto mb-2 text-purple-400" />
          <div className="text-sm font-semibold text-white">Bug Fixing</div>
        </button>
        <button
          onClick={() => setActiveMode('queries')}
          className={`p-4 rounded-lg border-2 transition-all ${
            activeMode === 'queries'
              ? 'bg-purple-500/20 border-purple-500'
              : 'bg-gray-800/50 border-gray-700 hover:border-gray-600'
          }`}
        >
          <TrendingUp className="w-5 h-5 mx-auto mb-2 text-purple-400" />
          <div className="text-sm font-semibold text-white">Database Queries</div>
        </button>
      </div>

      {/* Sub-tabs for Chat mode */}
      {activeMode === 'chat' && (
        <div className="flex gap-2 border-b border-gray-800">
          <button
            onClick={() => setActiveTab('chat')}
            className={`px-4 py-3 flex items-center gap-2 transition-colors ${
              activeTab === 'chat'
                ? 'text-yellow-500 border-b-2 border-yellow-500'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            Chat with Queen
          </button>
          <button
            onClick={() => setActiveTab('proposals')}
            className={`px-4 py-3 flex items-center gap-2 transition-colors ${
              activeTab === 'proposals'
                ? 'text-yellow-500 border-b-2 border-yellow-500'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            <Code className="w-4 h-4" />
            Code Proposals ({proposals.length})
          </button>
        </div>
      )}

      {/* Content */}
      {activeMode === 'chat' && (
        activeTab === 'chat' ? (
          <ChatInterface
            messages={messages}
            input={input}
            setInput={setInput}
            loading={loading}
            onSend={sendMessage}
            messagesEndRef={messagesEndRef}
          />
        ) : (
          <ProposalsInterface
            proposals={proposals}
            selectedProposal={selectedProposal}
            setSelectedProposal={setSelectedProposal}
            onUpdate={loadProposals}
          />
        )
      )}
      {activeMode === 'bugs' && <BugFixingMode />}
      {activeMode === 'queries' && <DatabaseQueriesMode />}
    </div>
  );
}

// ==================== CHAT INTERFACE ====================

function ChatInterface({ messages, input, setInput, loading, onSend, messagesEndRef }: any) {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden flex flex-col" style={{ height: '600px' }}>
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <Sparkles className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
            <p className="text-gray-400 mb-2">Start a conversation with Queen AI</p>
            <p className="text-sm text-gray-500">
              Ask her to analyze the system, fix bugs, or propose improvements
            </p>
          </div>
        ) : (
          <>
            {messages.map((msg: Message, index: number) => (
              <MessageBubble key={index} message={msg} />
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-gray-400">
                <Loader className="w-4 h-4 animate-spin" />
                <span className="text-sm">Queen is thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && onSend()}
            placeholder="Ask Queen anything..."
            disabled={loading}
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 disabled:opacity-50"
          />
          <button
            onClick={onSend}
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-700 rounded-lg flex items-center gap-2 text-black font-medium disabled:text-gray-500"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div className={`rounded-lg p-4 ${
          isUser 
            ? 'bg-yellow-600 text-black'
            : 'bg-gray-800 text-white'
        }`}>
          <p className="whitespace-pre-wrap">{message.content}</p>
          
          {message.code_proposal_created && (
            <div className="mt-3 pt-3 border-t border-gray-700">
              <div className="flex items-center gap-2 text-sm text-green-400">
                <CheckCircle className="w-4 h-4" />
                Code proposal created! Check the Proposals tab.
              </div>
            </div>
          )}
        </div>
        <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </motion.div>
  );
}

// ==================== PROPOSALS INTERFACE ====================

function ProposalsInterface({ proposals, selectedProposal, setSelectedProposal, onUpdate }: any) {
  if (selectedProposal) {
    return (
      <ProposalDetail
        proposal={selectedProposal}
        onClose={() => setSelectedProposal(null)}
        onUpdate={onUpdate}
      />
    );
  }

  return (
    <div className="space-y-4">
      {proposals.length === 0 ? (
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-12 text-center">
          <Code className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No code proposals yet</p>
          <p className="text-sm text-gray-500 mt-2">
            Chat with Queen and ask her to analyze the system
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {proposals.map((proposal: Proposal) => (
            <ProposalCard
              key={proposal.id}
              proposal={proposal}
              onClick={() => setSelectedProposal(proposal)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ProposalCard({ proposal, onClick }: any) {
  const statusConfig: any = {
    proposed: { color: 'yellow', icon: Clock, label: 'Proposed' },
    sandbox_deployed: { color: 'blue', icon: GitBranch, label: 'In Sandbox' },
    testing: { color: 'purple', icon: TestTube, label: 'Testing' },
    tests_passed: { color: 'green', icon: CheckCircle, label: 'Tests Passed' },
    tests_failed: { color: 'red', icon: XCircle, label: 'Tests Failed' },
    approved: { color: 'green', icon: CheckCircle, label: 'Approved' },
    rejected: { color: 'red', icon: XCircle, label: 'Rejected' },
    applied: { color: 'green', icon: Zap, label: 'Applied' },
  };

  const config = statusConfig[proposal.status] || statusConfig.proposed;
  const Icon = config.icon;

  // Determine proposal source
  const source = proposal.created_by === 'system_analysis' || proposal.title?.includes('[System Analysis]') 
    ? 'system_analysis' 
    : proposal.title?.includes('[Bug Fix]') || proposal.metadata?.source === 'bug_fix'
    ? 'bug_fix'
    : 'chat';

  const sourceLabels: any = {
    system_analysis: { icon: TrendingUp, label: 'From System Analysis', color: 'blue' },
    bug_fix: { icon: Shield, label: 'Bug Fix', color: 'red' },
    chat: { icon: Sparkles, label: 'Queen Suggestion', color: 'purple' }
  };

  const sourceInfo = sourceLabels[source];
  const SourceIcon = sourceInfo.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      onClick={onClick}
      className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 hover:border-gray-700 cursor-pointer transition-colors"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="text-lg font-semibold text-white">{proposal.title}</h4>
            <span className={`px-2 py-0.5 bg-${sourceInfo.color}-500/10 border border-${sourceInfo.color}-500/30 text-${sourceInfo.color}-400 rounded-full text-xs font-medium flex items-center gap-1`}>
              <SourceIcon className="w-3 h-3" />
              {sourceInfo.label}
            </span>
          </div>
          <p className="text-sm text-gray-400 line-clamp-2">{proposal.description}</p>
        </div>
        <div className={`px-3 py-1 bg-${config.color}-500/20 text-${config.color}-400 rounded-full text-xs font-medium flex items-center gap-1`}>
          <Icon className="w-3 h-3" />
          {config.label}
        </div>
      </div>

      <div className="flex items-center gap-4 text-sm text-gray-500">
        <span className="capitalize">Priority: {proposal.priority}</span>
        <span>•</span>
        <span className="capitalize">Risk: {proposal.risk_level}</span>
        <span>•</span>
        <span>{proposal.files_to_modify.length} files</span>
        <span>•</span>
        <span>{new Date(proposal.created_at).toLocaleDateString()}</span>
      </div>
    </motion.div>
  );
}

function ProposalDetail({ proposal, onClose, onUpdate }: any) {
  const [loading, setLoading] = useState(false);
  const [activeAction, setActiveAction] = useState('');
  const [autoFixing, setAutoFixing] = useState(false);
  const [autoFixProgress, setAutoFixProgress] = useState('');

  const handleAction = async (action: string) => {
    setLoading(true);
    setActiveAction(action);

    try {
      const token = localStorage.getItem('auth_token');
      const url = `${BACKEND_URL}/api/v1/queen-dev/proposals/${proposal.id}/${action}`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const data = await response.json();

      if (data.success) {
        await onUpdate();
        if (action !== 'deploy-sandbox' && action !== 'run-tests') {
          onClose();
        }
      } else {
        alert(`Action failed: ${data.error}`);
      }
    } catch (error) {
      console.error('Action failed:', error);
      alert('Action failed. Check console for details.');
    } finally {
      setLoading(false);
      setActiveAction('');
    }
  };

  const triggerAutoFix = async () => {
    setAutoFixing(true);
    setAutoFixProgress('🔍 Analyzing test failures...');
    
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `${BACKEND_URL}/api/v1/admin/proposals/auto-fix/${proposal.id}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      const result = await response.json();
      
      if (result.success && result.fix_applied) {
        setAutoFixProgress(`✅ Fix applied! (Attempt ${result.attempts}/3)`);
        setTimeout(() => {
          setAutoFixProgress(`💡 ${result.explanation || 'Ready to re-test!'}`);
        }, 2000);
        
        // Refresh proposal to show updated code
        await onUpdate();
        
        // Show success message
        alert(`✅ Auto-fix applied!\n\n${result.explanation}\n\nClick "Deploy to Sandbox" to test the fix.`);
      } else {
        setAutoFixProgress('');
        alert(result.error || 'Auto-fix failed. Manual intervention needed.');
      }
    } catch (error: any) {
      setAutoFixProgress('');
      console.error('Auto-fix error:', error);
      alert(`❌ Auto-fix failed: ${error.message}`);
    } finally {
      setAutoFixing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-2xl font-bold text-white mb-2">{proposal.title}</h3>
          <p className="text-gray-400">{proposal.description}</p>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-gray-400" />
        </button>
      </div>

      {/* Metadata */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetadataCard label="Priority" value={proposal.priority} />
        <MetadataCard label="Risk Level" value={proposal.risk_level} />
        <MetadataCard label="Status" value={proposal.status} />
        <MetadataCard label="Files" value={`${proposal.files_to_modify.length} files`} />
      </div>

      {/* Files to Modify */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h4 className="text-lg font-semibold text-white mb-4">Files to Modify</h4>
        <div className="space-y-2">
          {proposal.files_to_modify.map((file: any, index: number) => (
            <div key={index} className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-white font-mono text-sm mb-1">{file.path}</div>
              <div className="text-xs text-gray-400">{file.changes}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Test Results */}
      {proposal.test_results && (
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <h4 className="text-lg font-semibold text-white mb-4">Test Results</h4>
          <div className="space-y-2">
            {proposal.test_results.tests.map((test: any, index: number) => (
              <div key={index} className="flex items-center justify-between bg-gray-800/50 rounded-lg p-3">
                <span className="text-white">{test.name}</span>
                <span className={`text-sm px-2 py-1 rounded ${
                  test.status === 'passed' ? 'bg-green-500/20 text-green-400' :
                  test.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                  'bg-gray-600/20 text-gray-400'
                }`}>
                  {test.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Auto-Fix Section - Show when tests failed */}
      {proposal.status === 'tests_failed' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-purple-500/10 border border-purple-500/30 rounded-xl p-6"
        >
          <div className="flex items-start gap-4">
            <AlertTriangle className="w-6 h-6 text-purple-400 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <h4 className="text-lg font-semibold text-purple-400 mb-2">
                🤖 Autonomous Fix Available
              </h4>
              <p className="text-sm text-gray-400 mb-4">
                Claude can analyze the test failures and automatically generate a fix. 
                This typically takes 30-60 seconds.
              </p>
              
              {autoFixing ? (
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Loader className="w-5 h-5 animate-spin text-purple-400" />
                    <span className="text-purple-300">{autoFixProgress || 'Working...'}</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    Claude is analyzing error logs and generating fixes...
                  </div>
                </div>
              ) : (
                <button
                  onClick={triggerAutoFix}
                  disabled={loading}
                  className="px-6 py-3 bg-purple-500 hover:bg-purple-600 disabled:bg-gray-700 disabled:text-gray-500 text-white font-semibold rounded-lg transition-all flex items-center gap-2"
                >
                  <Sparkles className="w-5 h-5" />
                  🤖 Auto-Fix & Retry
                </button>
              )}
            </div>
          </div>
          
          {/* Show fix history if exists */}
          {proposal.auto_fix_history && proposal.auto_fix_history.length > 0 && (
            <div className="mt-6 pt-6 border-t border-purple-500/20">
              <h5 className="text-sm font-semibold text-purple-400 mb-3">
                🔧 Fix History ({proposal.auto_fix_history.length} attempts)
              </h5>
              <div className="space-y-3">
                {proposal.auto_fix_history.map((fix: any, index: number) => (
                  <div key={index} className="bg-gray-900/50 border border-gray-700 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-gray-400">Attempt {fix.attempt}</span>
                      <span className="text-xs text-gray-500">
                        {new Date(fix.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="text-sm text-yellow-400 mb-1">
                      Root Cause: {fix.analysis?.root_cause || 'Unknown'}
                    </div>
                    {fix.fix?.explanation && (
                      <div className="text-xs text-green-400 mt-2">
                        ✅ {fix.fix.explanation}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* Actions */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h4 className="text-lg font-semibold text-white mb-4">Actions</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {proposal.status === 'proposed' && (
            <ActionButton
              icon={GitBranch}
              label="Deploy to Sandbox"
              onClick={() => handleAction('deploy-sandbox')}
              loading={loading && activeAction === 'deploy-sandbox'}
              color="blue"
            />
          )}
          {proposal.status === 'sandbox_deployed' && (
            <ActionButton
              icon={TestTube}
              label="Run Tests"
              onClick={() => handleAction('run-tests')}
              loading={loading && activeAction === 'run-tests'}
              color="purple"
            />
          )}
          {proposal.status === 'tests_passed' && (
            <>
              <ActionButton
                icon={CheckCircle}
                label="Approve"
                onClick={() => handleAction('approve')}
                loading={loading && activeAction === 'approve'}
                color="green"
              />
              <ActionButton
                icon={XCircle}
                label="Reject"
                onClick={() => handleAction('reject')}
                loading={loading && activeAction === 'reject'}
                color="red"
              />
            </>
          )}
          {proposal.status === 'approved' && (
            <ActionButton
              icon={Play}
              label="Apply to Production"
              onClick={() => handleAction('apply')}
              loading={loading && activeAction === 'apply'}
              color="green"
            />
          )}
          {proposal.status === 'applied' && (
            <ActionButton
              icon={RefreshCw}
              label="Rollback"
              onClick={() => handleAction('rollback')}
              loading={loading && activeAction === 'rollback'}
              color="red"
            />
          )}
        </div>
      </div>
    </div>
  );
}

function MetadataCard({ label, value }: any) {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
      <div className="text-sm text-gray-400 mb-1">{label}</div>
      <div className="text-white font-medium capitalize">{value}</div>
    </div>
  );
}

function ActionButton({ icon: Icon, label, onClick, loading, color }: any) {
  const colors: any = {
    blue: 'bg-blue-600 hover:bg-blue-700',
    purple: 'bg-purple-600 hover:bg-purple-700',
    green: 'bg-green-600 hover:bg-green-700',
    red: 'bg-red-600 hover:bg-red-700',
  };

  return (
    <button
      onClick={onClick}
      disabled={loading}
      className={`${colors[color]} disabled:bg-gray-700 text-white px-4 py-3 rounded-lg flex items-center justify-center gap-2 transition-colors`}
    >
      {loading ? (
        <Loader className="w-4 h-4 animate-spin" />
      ) : (
        <Icon className="w-4 h-4" />
      )}
      <span className="text-sm font-medium">{label}</span>
    </button>
  );
}

// ==================== BUG FIXING MODE ====================

function BugFixingMode() {
  const AutonomousFixer = require('./AutonomousFixer').default;
  return <AutonomousFixer />;
}

// ==================== DATABASE QUERIES MODE ====================

function DatabaseQueriesMode() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  const EXAMPLE_QUERIES = [
    "How many users are currently active?",
    "Show me female users in Tokyo with wallet balance > $500",
    "What's the average wallet balance by region?",
    "How many users have completed KYC verification?",
    "List top 10 users by wallet balance",
    "Show users created in the last 7 days"
  ];

  const executeQuery = async (query: string) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch('http://localhost:8001/api/v1/queen-dev/chat', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: query,
          include_system_info: true
        })
      });

      const data = await response.json();
      if (data.success) {
        setResults({ query, response: data.response });
      }
    } catch (error) {
      console.error('Query failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Example Queries */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">Quick Database Queries</h3>
        <div className="grid grid-cols-2 gap-3">
          {EXAMPLE_QUERIES.map((query, idx) => (
            <button
              key={idx}
              onClick={() => { setInput(query); executeQuery(query); }}
              className="p-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-left text-sm text-gray-300 transition-colors"
            >
              {query}
            </button>
          ))}
        </div>
      </div>

      {/* Query Input */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">Ask Queen About Your System</h3>
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && input.trim() && executeQuery(input)}
            placeholder="Ask a question about users, system data, etc..."
            className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
            disabled={loading}
          />
          <button
            onClick={() => executeQuery(input)}
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 disabled:text-gray-500 text-white font-semibold rounded-lg transition-colors flex items-center gap-2"
          >
            {loading ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Querying...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Query
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results */}
      {results && (
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <div className="flex items-start justify-between mb-4">
            <h3 className="text-lg font-bold text-white">Query Results</h3>
            <button
              onClick={() => setResults(null)}
              className="text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="mb-3 p-3 bg-gray-800/50 rounded-lg">
            <div className="text-xs text-gray-400 mb-1">Your Question:</div>
            <div className="text-sm text-white">{results.query}</div>
          </div>
          
          <div className="p-4 bg-gray-800 rounded-lg">
            <div className="text-sm text-gray-300 whitespace-pre-wrap">{results.response}</div>
          </div>
        </div>
      )}
    </div>
  );
}
