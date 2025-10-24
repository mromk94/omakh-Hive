'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageSquare, Send, Sparkles, Code, CheckCircle, XCircle,
  Clock, AlertTriangle, Loader, RefreshCw, Eye, Play, X,
  GitBranch, TestTube, Zap, Shield, TrendingUp
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { API_ENDPOINTS } from '../../../lib/constants';

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

export default function QueenDevelopment() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [selectedProposal, setSelectedProposal] = useState<Proposal | null>(null);
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
      const response = await fetch(`${API_ENDPOINTS.QUEEN_DEV}/conversation-history`, {
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
      const response = await fetch(`${API_ENDPOINTS.QUEEN_DEV}/proposals`, {
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
      const response = await fetch(`${API_ENDPOINTS.QUEEN_DEV}/chat`, {
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
      const response = await fetch(`${API_ENDPOINTS.QUEEN_DEV}/analyze-system`, {
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

      {/* Tabs */}
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

      {/* Content */}
      {activeTab === 'chat' ? (
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
      )}
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

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      onClick={onClick}
      className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 hover:border-gray-700 cursor-pointer transition-colors"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h4 className="text-lg font-semibold text-white mb-1">{proposal.title}</h4>
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
