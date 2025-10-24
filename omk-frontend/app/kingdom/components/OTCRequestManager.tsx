'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Clock, CheckCircle2, XCircle, DollarSign, User, Mail, Wallet, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { API_ENDPOINTS } from '../../../lib/constants';

interface OTCRequest {
  id: string;
  name: string;
  email: string;
  wallet: string;
  allocation: string;
  amount_usd: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  price_per_token: number;
}

export default function OTCRequestManager() {
  const [requests, setRequests] = useState<OTCRequest[]>([]);
  const [filter, setFilter] = useState<string>('all');
  const [selectedRequest, setSelectedRequest] = useState<OTCRequest | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRequests();
  }, [filter]);

  const loadRequests = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const queryParam = filter !== 'all' ? `?status=${filter}` : '';
      const response = await fetch(`${API_ENDPOINTS.ADMIN}/otc/requests${queryParam}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.success) {
        setRequests(data.requests || []);
        console.log(`✅ Loaded ${data.requests?.length || 0} OTC requests`);
      } else {
        console.error('Failed to load requests:', data);
        setRequests([]);
        toast.error('Failed to load OTC requests');
      }
    } catch (error: any) {
      console.error('Failed to load OTC requests:', error);
      setRequests([]);
      toast.error(`Error loading requests: ${error?.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (requestId: string) => {
    try {
      const response = await fetch(`${API_ENDPOINTS.ADMIN}/otc/requests/${requestId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      
      if (response.ok) {
        toast.success('✅ Request approved! Email sent to investor.');
        loadRequests();
        setSelectedRequest(null);
      } else {
        toast.error('Failed to approve request');
      }
    } catch (error: any) {
      toast.error(`Error: ${error?.message || 'Failed to approve request'}`);
    }
  };

  const handleReject = async (requestId: string) => {
    const reason = prompt('Reason for rejection:');
    if (!reason) return;

    try {
      const response = await fetch(`${API_ENDPOINTS.ADMIN}/otc/requests/${requestId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({ reason })
      });
      
      if (response.ok) {
        toast.success('Request rejected successfully');
        loadRequests();
        setSelectedRequest(null);
      } else {
        toast.error('Failed to reject request');
      }
    } catch (error: any) {
      toast.error(`Error: ${error?.message || 'Failed to reject request'}`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30';
      case 'approved': return 'text-green-500 bg-green-500/10 border-green-500/30';
      case 'rejected': return 'text-red-500 bg-red-500/10 border-red-500/30';
      default: return 'text-gray-500 bg-gray-500/10 border-gray-500/30';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return Clock;
      case 'approved': return CheckCircle2;
      case 'rejected': return XCircle;
      default: return Clock;
    }
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex gap-2">
        {['all', 'pending', 'approved', 'rejected'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg capitalize transition-colors ${
              filter === f
                ? 'bg-yellow-600 text-black font-semibold'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Requests List */}
      {loading ? (
        <div className="text-center text-gray-400 py-12">
          <div className="w-8 h-8 border-4 border-yellow-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          Loading requests...
        </div>
      ) : requests.length === 0 ? (
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-12 text-center">
          <AlertCircle className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No {filter !== 'all' ? filter : ''} requests found</h3>
          <p className="text-gray-400 mb-6">
            {filter === 'all' 
              ? 'No OTC requests have been submitted yet. They will appear here once users submit requests.'
              : `No ${filter} requests at the moment. Try changing the filter.`
            }
          </p>
          {filter !== 'all' && (
            <button
              onClick={() => setFilter('all')}
              className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-black rounded-lg font-medium transition-colors"
            >
              View All Requests
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {requests.map((request) => {
            const StatusIcon = getStatusIcon(request.status);
            return (
              <motion.div
                key={request.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gray-900/50 border border-gray-800 rounded-xl p-5 hover:border-yellow-600 transition-colors cursor-pointer"
                onClick={() => setSelectedRequest(request)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-white font-semibold text-lg">{request.name}</h3>
                      <span className="text-gray-500 text-sm">({request.id})</span>
                    </div>
                    <p className="text-gray-400 text-sm">{request.email}</p>
                  </div>
                  <div className={`px-3 py-1 rounded-full border flex items-center gap-2 ${getStatusColor(request.status)}`}>
                    <StatusIcon className="w-4 h-4" />
                    <span className="text-sm capitalize">{request.status}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Allocation</div>
                    <div className="text-white font-semibold">
                      {parseFloat(request.allocation).toLocaleString()} OMK
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Total Amount</div>
                    <div className="text-green-500 font-semibold">
                      ${parseFloat(request.amount_usd).toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Price per Token</div>
                    <div className="text-white font-semibold">
                      ${request.price_per_token.toFixed(2)}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Submitted</div>
                    <div className="text-gray-400 text-sm">
                      {new Date(request.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Request Detail Modal */}
      {selectedRequest && (
        <div 
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedRequest(null)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-gray-900 border border-gray-800 rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">OTC Request Details</h2>
              <div className={`px-3 py-1 rounded-full border flex items-center gap-2 ${getStatusColor(selectedRequest.status)}`}>
                {React.createElement(getStatusIcon(selectedRequest.status), { className: 'w-4 h-4' })}
                <span className="text-sm capitalize">{selectedRequest.status}</span>
              </div>
            </div>

            <div className="space-y-6">
              {/* Investor Info */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Investor Information</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <User className="w-5 h-5 text-gray-400" />
                    <div>
                      <div className="text-xs text-gray-500">Name</div>
                      <div className="text-white">{selectedRequest.name}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Mail className="w-5 h-5 text-gray-400" />
                    <div>
                      <div className="text-xs text-gray-500">Email</div>
                      <div className="text-white">{selectedRequest.email}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Wallet className="w-5 h-5 text-gray-400" />
                    <div>
                      <div className="text-xs text-gray-500">Wallet Address</div>
                      <div className="text-white font-mono text-sm break-all">{selectedRequest.wallet}</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Purchase Details */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Purchase Details</h3>
                <div className="bg-gray-800/50 rounded-xl p-4 space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">OMK Tokens</span>
                    <span className="text-white font-semibold">
                      {parseFloat(selectedRequest.allocation).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Price per Token</span>
                    <span className="text-white font-semibold">
                      ${selectedRequest.price_per_token.toFixed(2)}
                    </span>
                  </div>
                  <div className="border-t border-gray-700 pt-3 flex justify-between">
                    <span className="text-gray-400">Total Amount</span>
                    <span className="text-green-500 font-bold text-xl">
                      ${parseFloat(selectedRequest.amount_usd).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Request Info */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Request Information</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Request ID</span>
                    <span className="text-white">{selectedRequest.id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Submitted</span>
                    <span className="text-white">
                      {new Date(selectedRequest.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              {selectedRequest.status === 'pending' && (
                <div className="flex gap-3 pt-4 border-t border-gray-800">
                  <button
                    onClick={() => handleApprove(selectedRequest.id)}
                    className="flex-1 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors"
                  >
                    ✅ Approve Request
                  </button>
                  <button
                    onClick={() => handleReject(selectedRequest.id)}
                    className="flex-1 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors"
                  >
                    ❌ Reject Request
                  </button>
                </div>
              )}

              <button
                onClick={() => setSelectedRequest(null)}
                className="w-full py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
