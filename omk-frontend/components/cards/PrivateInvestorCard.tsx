'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { API_ENDPOINTS } from '@/lib/constants';
import { Users, Plus, Check, X, AlertTriangle, TrendingUp, Calendar, DollarSign, Rocket } from 'lucide-react';

interface PrivateInvestorCardProps {
  onClose?: () => void;
}

interface Investor {
  wallet: string;
  allocation: string;
  amountPaid: string;
  pricePerToken: string;
  investorId: string;
  distributed: boolean;
}

export default function PrivateInvestorCard({ onClose }: PrivateInvestorCardProps) {
  const [step, setStep] = useState<'list' | 'register' | 'tge' | 'distribute'>('list');
  const [formData, setFormData] = useState({
    wallet: '',
    allocation: '',
    amountPaid: '',
    investorId: ''
  });
  const [loading, setLoading] = useState(false);
  const [tgeExecuted, setTgeExecuted] = useState(false);
  const [investors, setInvestors] = useState<Investor[]>([]);
  const [error, setError] = useState('');

  // Load investors from backend
  useEffect(() => {
    fetchInvestors();
  }, []);

  const fetchInvestors = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${API_ENDPOINTS.ADMIN}/private-investors`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setInvestors(data.investors.map((inv: any) => ({
            wallet: inv.wallet,
            allocation: inv.allocation.toLocaleString(),
            amountPaid: `$${inv.amount_paid.toLocaleString()}`,
            pricePerToken: `$${inv.price_per_token.toFixed(4)}`,
            investorId: inv.investor_id,
            distributed: inv.distributed || false
          })));
        }
      }
    } catch (error) {
      console.error('Failed to fetch investors:', error);
    }
  };

  const totalAllocated = investors.reduce((sum, inv) => sum + parseFloat(inv.allocation.replace(/,/g, '')), 0);
  const totalDistributed = investors.filter(i => i.distributed).reduce((sum, inv) => sum + parseFloat(inv.allocation.replace(/,/g, '')), 0);
  const pendingInvestors = investors.filter(i => !i.distributed);

  const handleRegisterInvestor = async () => {
    setLoading(true);
    setError('');
    
    // Validation
    if (!formData.wallet || !formData.allocation || !formData.amountPaid || !formData.investorId) {
      setError('Please fill all fields');
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${API_ENDPOINTS.ADMIN}/private-investors`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          wallet: formData.wallet,
          allocation: parseInt(formData.allocation),
          amount_paid: parseFloat(formData.amountPaid),
          investor_id: formData.investorId
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          await fetchInvestors(); // Reload list
          setFormData({ wallet: '', allocation: '', amountPaid: '', investorId: '' });
          setStep('list');
        } else {
          setError(data.message || 'Failed to register investor');
        }
      } else {
        setError('Failed to register investor');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteTGE = async () => {
    setLoading(true);
    // Mock TGE execution - replace with actual contract call
    await new Promise(resolve => setTimeout(resolve, 3000));
    setTgeExecuted(true);
    setLoading(false);
    setStep('distribute');
  };

  const handleDistributeToInvestor = async (wallet: string) => {
    setLoading(true);
    // Mock distribution - replace with actual contract call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setInvestors(investors.map(inv => 
      inv.wallet === wallet ? { ...inv, distributed: true } : inv
    ));
    setLoading(false);
  };

  const handleDistributeAll = async () => {
    setLoading(true);
    // Mock batch distribution - replace with actual contract call
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    setInvestors(investors.map(inv => ({ ...inv, distributed: true })));
    setLoading(false);
  };

  if (step === 'register') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-2xl bg-gradient-to-br from-purple-900/40 to-pink-900/40 rounded-2xl border-2 border-purple-500/30 p-6 backdrop-blur-sm"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Plus className="w-6 h-6 text-purple-400" />
            <h3 className="text-2xl font-bold text-white">Register Private Investor</h3>
          </div>
          <button onClick={() => setStep('list')} className="text-gray-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="space-y-5">
          {/* Wallet Address */}
          <div>
            <label className="block text-sm font-medium text-purple-300 mb-2">
              Wallet Address *
            </label>
            <input
              type="text"
              value={formData.wallet}
              onChange={(e) => setFormData({...formData, wallet: e.target.value})}
              placeholder="0x..."
              className="w-full px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none"
            />
            <p className="text-xs text-gray-500 mt-1">Ethereum address where tokens will be sent at TGE</p>
          </div>

          {/* OMK Allocation */}
          <div>
            <label className="block text-sm font-medium text-purple-300 mb-2">
              OMK Allocation *
            </label>
            <input
              type="number"
              value={formData.allocation}
              onChange={(e) => setFormData({...formData, allocation: e.target.value})}
              placeholder="1000000"
              className="w-full px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none"
            />
            <div className="flex gap-2 mt-2">
              {[100000, 500000, 1000000, 2000000, 5000000].map(amount => (
                <button
                  key={amount}
                  onClick={() => setFormData({...formData, allocation: amount.toString()})}
                  className="px-3 py-1 text-xs bg-purple-900/30 border border-purple-500/30 rounded-lg text-purple-300 hover:bg-purple-900/50"
                >
                  {(amount / 1000).toLocaleString()}K
                </button>
              ))}
            </div>
          </div>

          {/* Amount Paid */}
          <div>
            <label className="block text-sm font-medium text-purple-300 mb-2">
              Amount Paid (USD) *
            </label>
            <input
              type="number"
              value={formData.amountPaid}
              onChange={(e) => setFormData({...formData, amountPaid: e.target.value})}
              placeholder="100000"
              className="w-full px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none"
            />
            {formData.allocation && formData.amountPaid && (
              <p className="text-sm text-green-400 mt-1">
                Price per token: ${(parseFloat(formData.amountPaid) / parseFloat(formData.allocation)).toFixed(4)}
              </p>
            )}
          </div>

          {/* Investor ID */}
          <div>
            <label className="block text-sm font-medium text-purple-300 mb-2">
              Investor ID *
            </label>
            <input
              type="text"
              value={formData.investorId}
              onChange={(e) => setFormData({...formData, investorId: e.target.value})}
              placeholder="INV-004 or ACME-CORP"
              className="w-full px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none"
            />
            <p className="text-xs text-gray-500 mt-1">Internal reference for your records</p>
          </div>

          {/* Submit Button */}
          <button
            onClick={handleRegisterInvestor}
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-bold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Registering...' : 'Register Investor'}
          </button>
        </div>
      </motion.div>
    );
  }

  if (step === 'tge') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-2xl bg-gradient-to-br from-orange-900/40 to-red-900/40 rounded-2xl border-2 border-orange-500/50 p-6 backdrop-blur-sm"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Rocket className="w-6 h-6 text-orange-400" />
            <h3 className="text-2xl font-bold text-white">Execute Token Generation Event</h3>
          </div>
          <button onClick={() => setStep('list')} className="text-gray-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="bg-orange-900/20 border border-orange-500/30 rounded-xl p-5 mb-6">
          <div className="flex items-start gap-3 mb-4">
            <AlertTriangle className="w-6 h-6 text-orange-400 mt-1" />
            <div>
              <h4 className="font-bold text-orange-300 mb-2">⚠️ CRITICAL ACTION - READ CAREFULLY</h4>
              <p className="text-sm text-gray-300 mb-3">
                Executing TGE is <strong>IRREVERSIBLE</strong>. Once executed, you cannot:
              </p>
              <ul className="text-sm text-gray-400 space-y-1 ml-4">
                <li>• Add new investors to this registry</li>
                <li>• Modify investor allocations</li>
                <li>• Remove registered investors</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="bg-purple-900/20 border border-purple-500/30 rounded-xl p-5 mb-6">
          <h4 className="font-bold text-purple-300 mb-3">📊 TGE Summary</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-500">Total Investors</p>
              <p className="text-2xl font-bold text-white">{investors.length}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Total Allocated</p>
              <p className="text-2xl font-bold text-purple-300">{totalAllocated.toLocaleString()} OMK</p>
            </div>
            <div className="col-span-2">
              <p className="text-xs text-gray-500 mb-2">Contract Balance Required</p>
              <div className="flex items-center justify-between">
                <span className="text-lg font-bold text-green-400">{totalAllocated.toLocaleString()} OMK</span>
                <Check className="w-5 h-5 text-green-400" />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-green-900/20 border border-green-500/30 rounded-xl p-5 mb-6">
          <h4 className="font-bold text-green-300 mb-3">✅ What Happens After TGE</h4>
          <ul className="text-sm text-gray-300 space-y-2">
            <li className="flex items-start gap-2">
              <span className="text-green-400">→</span>
              <span>Distribution unlocked for all {investors.length} investors</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400">→</span>
              <span>You can distribute tokens individually or in batches</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400">→</span>
              <span>TGE timestamp recorded on-chain permanently</span>
            </li>
          </ul>
        </div>

        <div className="flex gap-4">
          <button
            onClick={() => setStep('list')}
            className="flex-1 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition-all"
          >
            Cancel
          </button>
          <button
            onClick={handleExecuteTGE}
            disabled={loading}
            className="flex-1 py-3 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 text-white font-bold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Executing TGE...' : '🚀 Execute TGE'}
          </button>
        </div>
      </motion.div>
    );
  }

  if (step === 'distribute') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-3xl bg-gradient-to-br from-blue-900/40 to-cyan-900/40 rounded-2xl border-2 border-blue-500/30 p-6 backdrop-blur-sm"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-6 h-6 text-blue-400" />
            <h3 className="text-2xl font-bold text-white">Token Distribution</h3>
          </div>
          <button onClick={() => setStep('list')} className="text-gray-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="bg-black/30 border border-blue-500/30 rounded-xl p-5 mb-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-blue-300">Distribution Progress</span>
            <span className="text-sm font-bold text-white">
              {Math.round((totalDistributed / totalAllocated) * 100)}%
            </span>
          </div>
          <div className="w-full h-3 bg-gray-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-500"
              style={{ width: `${(totalDistributed / totalAllocated) * 100}%` }}
            />
          </div>
          <div className="flex justify-between mt-2 text-xs text-gray-400">
            <span>Distributed: {totalDistributed.toLocaleString()} OMK</span>
            <span>Pending: {(totalAllocated - totalDistributed).toLocaleString()} OMK</span>
          </div>
        </div>

        {/* Distribute All Button */}
        {pendingInvestors.length > 0 && (
          <button
            onClick={handleDistributeAll}
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-bold rounded-lg transition-all mb-6 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Distributing...' : `📦 Distribute to All ${pendingInvestors.length} Pending Investors`}
          </button>
        )}

        {/* Investor List */}
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {investors.map((investor) => (
            <div
              key={investor.investorId}
              className={`p-4 rounded-xl border ${
                investor.distributed
                  ? 'bg-green-900/20 border-green-500/30'
                  : 'bg-purple-900/20 border-purple-500/30'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-bold text-white">{investor.investorId}</span>
                    {investor.distributed && (
                      <span className="px-2 py-1 bg-green-500/20 border border-green-500/30 rounded text-xs text-green-300 font-medium">
                        ✓ Distributed
                      </span>
                    )}
                    {!investor.distributed && (
                      <span className="px-2 py-1 bg-orange-500/20 border border-orange-500/30 rounded text-xs text-orange-300 font-medium">
                        ⏳ Pending
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-400 mb-1">{investor.wallet}</p>
                  <div className="flex gap-4 text-xs text-gray-500">
                    <span>{investor.allocation} OMK</span>
                    <span>•</span>
                    <span>{investor.amountPaid} paid</span>
                    <span>•</span>
                    <span>{investor.pricePerToken}/token</span>
                  </div>
                </div>
                {!investor.distributed && (
                  <button
                    onClick={() => handleDistributeToInvestor(investor.investorId)}
                    disabled={loading}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Distribute
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    );
  }

  // Default: Investor List
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="w-full max-w-3xl bg-gradient-to-br from-purple-900/40 to-blue-900/40 rounded-2xl border-2 border-purple-500/30 p-6 backdrop-blur-sm"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Users className="w-6 h-6 text-purple-400" />
          <h3 className="text-2xl font-bold text-white">Private Investors (Pre-TGE)</h3>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-900/30 border border-blue-500/30 rounded-xl p-4">
          <p className="text-xs text-gray-400 mb-1">Total Investors</p>
          <p className="text-2xl font-bold text-white">{investors.length}</p>
        </div>
        <div className="bg-purple-900/30 border border-purple-500/30 rounded-xl p-4">
          <p className="text-xs text-gray-400 mb-1">Total Allocated</p>
          <p className="text-2xl font-bold text-purple-300">{totalAllocated.toLocaleString()}</p>
          <p className="text-xs text-gray-500">OMK tokens</p>
        </div>
        <div className="bg-green-900/30 border border-green-500/30 rounded-xl p-4">
          <p className="text-xs text-gray-400 mb-1">Remaining</p>
          <p className="text-2xl font-bold text-green-300">{(100000000 - totalAllocated).toLocaleString()}</p>
          <p className="text-xs text-gray-500">Available</p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={() => setStep('register')}
          className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Register Investor
        </button>
        <button
          onClick={() => setStep(tgeExecuted ? 'distribute' : 'tge')}
          disabled={investors.length === 0}
          className="flex-1 py-3 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Rocket className="w-5 h-5" />
          {tgeExecuted ? 'Distribute Tokens' : 'Execute TGE'}
        </button>
      </div>

      {/* Investor List */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {investors.map((investor) => (
          <div
            key={investor.investorId}
            className="p-4 bg-black/30 border border-purple-500/30 rounded-xl hover:border-purple-500/50 transition-all"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold text-purple-300">{investor.investorId}</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                investor.distributed
                  ? 'bg-green-500/20 border border-green-500/30 text-green-300'
                  : 'bg-gray-700/50 border border-gray-600/30 text-gray-400'
              }`}>
                {investor.distributed ? '✓ Distributed' : 'Pre-TGE'}
              </span>
            </div>
            <p className="text-sm text-gray-400 mb-2">{investor.wallet}</p>
            <div className="flex justify-between text-sm">
              <div>
                <span className="text-white font-bold">{investor.allocation} OMK</span>
                <span className="text-gray-500 ml-2">• {investor.amountPaid}</span>
              </div>
              <span className="text-gray-500">{investor.pricePerToken}/token</span>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
