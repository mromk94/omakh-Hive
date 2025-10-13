'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { API_ENDPOINTS } from '@/lib/constants';
import { TrendingUp, Check, X, AlertCircle, Wallet, DollarSign, Clock, CheckCircle, XCircle } from 'lucide-react';
import { useAccount, useConnect, useDisconnect } from 'wagmi';
import { injected } from 'wagmi/connectors';

interface OTCPurchaseCardProps {
  onClose?: () => void;
  onSubmit?: (data: any) => void;
}

type Step = 'welcome' | 'wallet' | 'amount' | 'contact' | 'review' | 'payment' | 'verifying' | 'submitted' | 'status';

interface OTCData {
  wallet: string;
  allocation: string;
  amountUSD: string;
  email: string;
  name: string;
  pricePerToken: number;
  status: 'pending' | 'approved' | 'rejected' | 'distributed';
  paymentToken?: 'USDT' | 'USDC' | 'DAI';
  txHash?: string;
  paymentScreenshot?: string;
  treasuryWallet?: string;
}

export default function OTCPurchaseCard({ onClose, onSubmit }: OTCPurchaseCardProps) {
  const [step, setStep] = useState<Step>('welcome');
  const [formData, setFormData] = useState<Partial<OTCData>>({
    pricePerToken: 0.10, // $0.10 per OMK for OTC
    status: 'pending',
    paymentToken: 'USDT'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [treasuryWallets, setTreasuryWallets] = useState<{[key: string]: string}>({
    USDT: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0',
    USDC: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0',
    DAI: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0'
  });
  const [paymentMethodsEnabled, setPaymentMethodsEnabled] = useState<{[key: string]: boolean}>({
    usdt: true,
    usdc: true,
    dai: true
  });
  const [tgeDate, setTgeDate] = useState<string>('2025-12-31T00:00:00Z');
  const [showTGEInfo, setShowTGEInfo] = useState(false);

  // Wagmi hooks for wallet connection
  const { address, isConnected } = useAccount();
  const { connect } = useConnect();
  const { disconnect } = useDisconnect();

  // Fetch config from backend (treasury wallets, payment methods, TGE date)
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await fetch(`${API_ENDPOINTS.ADMIN}/config`);
        const data = await response.json();
        if (data.success && data.config) {
          const config = data.config;
          
          // Treasury wallets
          if (config.treasury_wallets) {
            setTreasuryWallets({
              USDT: config.treasury_wallets.usdt || treasuryWallets.USDT,
              USDC: config.treasury_wallets.usdc || treasuryWallets.USDC,
              DAI: config.treasury_wallets.dai || treasuryWallets.DAI
            });
          }
          
          // Payment methods enabled
          if (config.payment_methods_enabled) {
            setPaymentMethodsEnabled(config.payment_methods_enabled);
          }
          
          // TGE date
          if (config.tge_date) {
            setTgeDate(config.tge_date);
          }
        }
      } catch (error) {
        console.error('Failed to fetch config:', error);
        // Keep using defaults as fallback
      }
    };
    fetchConfig();
  }, []);

  // Auto-populate wallet when connected
  useEffect(() => {
    if (isConnected && address && step === 'wallet') {
      setFormData(prev => ({ ...prev, wallet: address }));
      setStep('amount');
    }
  }, [isConnected, address, step]);

  const handleConnectWallet = () => {
    try {
      connect({ connector: injected() });
    } catch (err) {
      setError('Failed to connect wallet. Please try again.');
    }
  };

  const handleManualWallet = () => {
    setStep('amount');
  };

  const calculatePrice = (allocation: string) => {
    const tokens = parseFloat(allocation) || 0;
    const price = formData.pricePerToken || 0.10;
    return (tokens * price).toLocaleString('en-US', { 
      style: 'currency', 
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  };

  const handleSubmit = async () => {
    setLoading(true);
    
    try {
      // Call backend API to submit OTC request with payment info
      const response = await fetch(`${API_ENDPOINTS.FRONTEND}/otc-request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          wallet: formData.wallet,
          allocation: formData.allocation,
          price_per_token: formData.pricePerToken || 0.10,
          payment_token: formData.paymentToken || 'USDT',
          tx_hash: formData.txHash,
          amount_usd: parseFloat(formData.allocation || '0') * (formData.pricePerToken || 0.10)
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Store request ID for tracking
        setFormData(prev => ({ ...prev, requestId: data.request_id }));
        
        // Call parent callback if provided
        if (onSubmit) {
          onSubmit({...formData, requestId: data.request_id});
        }
        
        setLoading(false);
        setStep('submitted');
      } else {
        throw new Error(data.error || 'Failed to submit request');
      }
    } catch (error) {
      console.error('OTC submission error:', error);
      setError('Failed to submit OTC request. Please check your transaction hash and try again.');
      setLoading(false);
    }
  };

  // Welcome Step
  if (step === 'welcome') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-2xl bg-gradient-to-br from-blue-900/40 to-purple-900/40 rounded-2xl border-2 border-blue-500/30 p-6 backdrop-blur-sm"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-6 h-6 text-blue-400" />
            <h3 className="text-2xl font-bold text-white">OTC Token Purchase</h3>
          </div>
          {onClose && (
            <button onClick={onClose} className="text-gray-400 hover:text-white">
              <X className="w-6 h-6" />
            </button>
          )}
        </div>

        <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-5 mb-6">
          <h4 className="font-bold text-blue-300 mb-3">🎯 Private Pre-TGE Sale</h4>
          <p className="text-sm text-gray-300 mb-4">
            Purchase OMK tokens directly before the Token Generation Event (TGE) at an exclusive price.
          </p>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-xs text-gray-500">Price per OMK</p>
              <p className="text-2xl font-bold text-green-400">$0.10</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Minimum Purchase</p>
              <p className="text-2xl font-bold text-white">100,000 OMK</p>
              <p className="text-xs text-gray-500">($10,000 USD)</p>
            </div>
          </div>
        </div>

        <div className="bg-purple-900/20 border border-purple-500/30 rounded-xl p-5 mb-6">
          <h4 className="font-bold text-purple-300 mb-3">✨ Exclusive Benefits</h4>
          <ul className="space-y-2 text-sm text-gray-300">
            <li className="flex items-start gap-2">
              <Check className="w-4 h-4 text-green-400 mt-1 flex-shrink-0" />
              <span><strong>Early Access:</strong> Get tokens before public sale</span>
            </li>
            <li className="flex items-start gap-2">
              <Check className="w-4 h-4 text-green-400 mt-1 flex-shrink-0" />
              <span><strong>Better Price:</strong> 30% cheaper than public sale price ($0.145)</span>
            </li>
            <li className="flex items-start gap-2">
              <Check className="w-4 h-4 text-green-400 mt-1 flex-shrink-0" />
              <span><strong>Guaranteed Allocation:</strong> No gas wars or failed transactions</span>
            </li>
            <li className="flex items-start gap-2">
              <Check className="w-4 h-4 text-green-400 mt-1 flex-shrink-0" />
              <span><strong>Direct Distribution:</strong> Tokens sent to your wallet at TGE</span>
            </li>
          </ul>
        </div>

        <div className="bg-orange-900/20 border border-orange-500/30 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-orange-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-orange-300 mb-1">Pre-TGE Purchase Process</p>
              <p className="text-xs text-gray-400">
                1. Submit your request and make crypto payment<br />
                2. Payment verified on blockchain automatically<br />
                3. Admin reviews (24hrs for large purchases)<br />
                4. Tokens distributed to your wallet at TGE
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={() => setStep('wallet')}
          className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold rounded-lg transition-all"
        >
          Start OTC Purchase Request
        </button>
      </motion.div>
    );
  }

  // Wallet Connection Step
  if (step === 'wallet') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-2xl bg-gradient-to-br from-blue-900/40 to-purple-900/40 rounded-2xl border-2 border-blue-500/30 p-6 backdrop-blur-sm"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Wallet className="w-6 h-6 text-blue-400" />
            <h3 className="text-2xl font-bold text-white">Connect Your Wallet</h3>
          </div>
          <button onClick={() => setStep('welcome')} className="text-gray-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        </div>

        <p className="text-gray-300 mb-6">
          Connect your Ethereum wallet to receive your OMK tokens at TGE. Don't have a wallet? 
          You can enter your address manually and set one up later.
        </p>

        {!isConnected ? (
          <div className="space-y-4">
            <button
              onClick={handleConnectWallet}
              className="w-full py-4 bg-gradient-to-r from-orange-600 to-pink-600 hover:from-orange-500 hover:to-pink-500 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-3"
            >
              <Wallet className="w-5 h-5" />
              Connect Wallet (MetaMask)
            </button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-600"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-gray-900 text-gray-400">or</span>
              </div>
            </div>

            <button
              onClick={handleManualWallet}
              className="w-full py-3 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg transition-all"
            >
              Enter Wallet Address Manually
            </button>
          </div>
        ) : (
          <div className="bg-green-900/20 border border-green-500/30 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-3">
              <CheckCircle className="w-6 h-6 text-green-400" />
              <span className="font-bold text-green-300">Wallet Connected!</span>
            </div>
            <p className="text-sm text-gray-400 mb-1">Connected Address:</p>
            <p className="text-white font-mono bg-black/30 p-3 rounded-lg break-all">
              {address}
            </p>
            <div className="flex gap-3 mt-4">
              <button
                onClick={() => setStep('amount')}
                className="flex-1 py-2 bg-green-600 hover:bg-green-500 text-white font-bold rounded-lg transition-all"
              >
                Continue →
              </button>
              <button
                onClick={() => disconnect()}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-all"
              >
                Disconnect
              </button>
            </div>
          </div>
        )}

        {error && (
          <div className="mt-4 bg-red-900/20 border border-red-500/30 rounded-lg p-3">
            <p className="text-sm text-red-300">{error}</p>
          </div>
        )}
      </motion.div>
    );
  }

  // Amount Selection Step
  if (step === 'amount') {
    const allocation = parseFloat(formData.allocation || '0');
    const minAllocation = 100000; // 100K OMK minimum

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-2xl bg-gradient-to-br from-blue-900/40 to-purple-900/40 rounded-2xl border-2 border-blue-500/30 p-6 backdrop-blur-sm"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <DollarSign className="w-6 h-6 text-blue-400" />
            <h3 className="text-2xl font-bold text-white">How Much OMK?</h3>
          </div>
          <button onClick={() => setStep('wallet')} className="text-gray-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        </div>

        {formData.wallet && (
          <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-3 mb-4">
            <p className="text-xs text-gray-400 mb-1">Tokens will be sent to:</p>
            <p className="text-xs sm:text-sm text-white font-mono break-all">{formData.wallet}</p>
          </div>
        )}

        <div className="mb-6">
          <label className="block text-sm font-medium text-purple-300 mb-2">
            OMK Token Amount *
          </label>
          <input
            type="number"
            value={formData.allocation || ''}
            onChange={(e) => setFormData({...formData, allocation: e.target.value})}
            placeholder="100,000 minimum"
            className="w-full px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg text-white text-lg font-bold placeholder-gray-500 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none"
          />
          <div className="flex gap-2 mt-3">
            {[100000, 250000, 500000, 1000000, 2000000].map(amount => (
              <button
                key={amount}
                onClick={() => setFormData({...formData, allocation: amount.toString()})}
                className="px-3 py-2 text-sm bg-purple-900/30 border border-purple-500/30 rounded-lg text-purple-300 hover:bg-purple-900/50 transition-all"
              >
                {(amount / 1000).toLocaleString()}K
              </button>
            ))}
          </div>
        </div>

        {allocation > 0 && (
          <div className="bg-green-900/20 border border-green-500/30 rounded-xl p-5 mb-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-400 mb-1">Total OMK Tokens</p>
                <p className="text-2xl font-bold text-white">{allocation.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Total Cost (USD)</p>
                <p className="text-2xl font-bold text-green-400">{calculatePrice(formData.allocation || '0')}</p>
                <p className="text-xs text-gray-500">@ $0.10 per OMK</p>
              </div>
            </div>

            {allocation < minAllocation && (
              <div className="mt-4 bg-red-900/20 border border-red-500/30 rounded-lg p-3">
                <p className="text-sm text-red-300">
                  ⚠️ Minimum purchase is {minAllocation.toLocaleString()} OMK (${(minAllocation * 0.10).toLocaleString()})
                </p>
              </div>
            )}
          </div>
        )}

        <button
          onClick={() => allocation >= minAllocation ? setStep('contact') : null}
          disabled={allocation < minAllocation}
          className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continue →
        </button>
      </motion.div>
    );
  }

  // Contact Information Step
  if (step === 'contact') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-2xl bg-gradient-to-br from-blue-900/40 to-purple-900/40 rounded-2xl border-2 border-blue-500/30 p-6 backdrop-blur-sm"
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-white">Contact Information</h3>
          <button onClick={() => setStep('amount')} className="text-gray-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        </div>

        <p className="text-gray-300 mb-6">
          We'll use this to contact you about payment details and confirm your purchase.
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-purple-300 mb-2">
              Full Name *
            </label>
            <input
              type="text"
              value={formData.name || ''}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder="John Doe"
              className="w-full px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-purple-300 mb-2">
              Email Address *
            </label>
            <input
              type="email"
              value={formData.email || ''}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              placeholder="john@example.com"
              className="w-full px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none"
            />
          </div>
        </div>

        <button
          onClick={() => formData.name && formData.email ? setStep('review') : null}
          disabled={!formData.name || !formData.email}
          className="w-full mt-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Review Purchase →
        </button>
      </motion.div>
    );
  }

  // Review & Submit Step
  if (step === 'review') {
    const allocation = parseFloat(formData.allocation || '0');
    const totalCost = allocation * (formData.pricePerToken || 0.10);

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-2xl bg-gradient-to-br from-blue-900/40 to-purple-900/40 rounded-2xl border-2 border-blue-500/30 p-6 backdrop-blur-sm"
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-white">Review Your Request</h3>
          <button onClick={() => setStep('contact')} className="text-gray-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="bg-purple-900/20 border border-purple-500/30 rounded-xl p-5 mb-6">
          <h4 className="font-bold text-purple-300 mb-4">Purchase Summary</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">OMK Tokens</span>
              <span className="text-white font-bold">{allocation.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Price per Token</span>
              <span className="text-green-400 font-bold">${formData.pricePerToken?.toFixed(2)}</span>
            </div>
            <div className="border-t border-gray-700 pt-3 flex justify-between">
              <span className="text-white font-medium">Total Cost</span>
              <span className="text-2xl font-bold text-green-400">${totalCost.toLocaleString()}</span>
            </div>
          </div>
        </div>

        <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-5 mb-6">
          <h4 className="font-bold text-blue-300 mb-4">Your Information</h4>
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-400">Name:</span>
              <span className="text-white ml-2">{formData.name}</span>
            </div>
            <div>
              <span className="text-gray-400">Email:</span>
              <span className="text-white ml-2">{formData.email}</span>
            </div>
            <div className="flex flex-col sm:flex-row sm:items-center gap-1">
              <span className="text-gray-400">Wallet:</span>
              <span className="text-white sm:ml-2 font-mono text-xs break-all">{formData.wallet}</span>
            </div>
          </div>
        </div>

        <div className="bg-orange-900/20 border border-orange-500/30 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-orange-400 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-gray-300">
              <p className="font-medium text-orange-300 mb-2">Next Step: Crypto Payment</p>
              <p className="text-xs">You'll send {formData.paymentToken || 'USDT'} directly to our treasury wallet. Payment is verified automatically on-chain!</p>
            </div>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => setStep('contact')}
            className="flex-1 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition-all"
          >
            ← Back
          </button>
          <button
            onClick={() => setStep('payment')}
            className="flex-1 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-bold rounded-lg transition-all"
          >
            Continue to Payment →
          </button>
        </div>
      </motion.div>
    );
  }

  // Payment Step
  if (step === 'payment') {
    const allocation = parseFloat(formData.allocation || '0');
    const totalCost = allocation * (formData.pricePerToken || 0.10);
    
    const treasuryWallet = treasuryWallets[formData.paymentToken || 'USDT'];
    
    const copyToClipboard = (text: string) => {
      navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    };

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-2xl bg-gradient-to-br from-green-900/40 to-blue-900/40 rounded-2xl border-2 border-green-500/30 p-4 sm:p-6 backdrop-blur-sm"
      >
        <div className="flex items-center justify-between mb-4 sm:mb-6">
          <h3 className="text-xl sm:text-2xl font-bold text-white">💰 Payment</h3>
          <button onClick={() => setStep('review')} className="text-gray-400 hover:text-white">
            <X className="w-5 h-5 sm:w-6 sm:h-6" />
          </button>
        </div>

        {/* Payment Token Selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-3">Select Payment Token</label>
          <div className="grid grid-cols-3 gap-3">
            {(['USDT', 'USDC', 'DAI'] as const)
              .filter(token => paymentMethodsEnabled[token.toLowerCase()])
              .map((token) => (
              <button
                key={token}
                onClick={() => setFormData({ ...formData, paymentToken: token })}
                className={`py-3 px-4 rounded-lg font-bold transition-all ${
                  formData.paymentToken === token
                    ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white border-2 border-green-400'
                    : 'bg-gray-800 text-gray-400 border-2 border-gray-700 hover:border-gray-600'
                }`}
              >
                {token}
              </button>
            ))}
          </div>
          {(['USDT', 'USDC', 'DAI'] as const).filter(token => paymentMethodsEnabled[token.toLowerCase()]).length === 0 && (
            <p className="text-red-400 text-sm mt-2">⚠️ No payment methods available. Please contact admin.</p>
          )}
        </div>

        {/* Amount to Send */}
        <div className="bg-green-900/20 border border-green-500/30 rounded-xl p-4 sm:p-5 mb-4 sm:mb-6">
          <h4 className="font-bold text-green-300 mb-3 text-sm sm:text-base">Amount to Send</h4>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <span className="text-gray-400 text-sm">Total Payment:</span>
            <span className="text-2xl sm:text-3xl font-bold text-green-400 break-all">
              ${totalCost.toLocaleString()} {formData.paymentToken || 'USDT'}
            </span>
          </div>
        </div>

        {/* Treasury Wallet Address */}
        <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-5 mb-6">
          <h4 className="font-bold text-blue-300 mb-3">Send Payment To:</h4>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 bg-black/30 rounded-lg p-3">
            <span className="text-white font-mono text-xs sm:text-sm flex-1 break-all overflow-hidden">{treasuryWallet}</span>
            <button
              onClick={() => copyToClipboard(treasuryWallet)}
              className="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-bold transition-all whitespace-nowrap"
            >
              {copied ? '✓ Copied!' : 'Copy'}
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-2">
            ⚠️ Send only {formData.paymentToken || 'USDT'} on Ethereum network to this address
          </p>
        </div>

        {/* Instructions */}
        <div className="bg-purple-900/20 border border-purple-500/30 rounded-xl p-5 mb-6">
          <h4 className="font-bold text-purple-300 mb-3">Payment Instructions</h4>
          <ol className="list-decimal ml-5 space-y-2 text-sm text-gray-300">
            <li>Copy the treasury wallet address above</li>
            <li>Open your wallet (MetaMask, Trust Wallet, etc.)</li>
            <li>Send exactly <strong className="text-white">${totalCost.toLocaleString()} {formData.paymentToken || 'USDT'}</strong></li>
            <li>Wait for transaction confirmation</li>
            <li>Paste the transaction hash below</li>
          </ol>
        </div>

        {/* Payment Proof Options */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-3">
            Payment Proof (Choose One) *
          </label>
          
          <div className="space-y-4">
            {/* Transaction Hash */}
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <label className="flex items-center gap-2 mb-2 cursor-pointer">
                <input
                  type="radio"
                  name="proofType"
                  checked={!formData.paymentScreenshot}
                  onChange={() => setFormData({ ...formData, paymentScreenshot: undefined })}
                  className="w-4 h-4 text-purple-600"
                />
                <span className="text-white font-medium">Transaction Hash</span>
              </label>
              <input
                type="text"
                value={formData.txHash || ''}
                onChange={(e) => setFormData({ ...formData, txHash: e.target.value, paymentScreenshot: undefined })}
                placeholder="0x..."
                disabled={!!formData.paymentScreenshot}
                className="w-full px-3 sm:px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg text-white font-mono text-xs sm:text-sm placeholder-gray-500 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none break-all disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <p className="text-xs text-gray-400 mt-1">
                Find this in your wallet under transaction history
              </p>
            </div>
            
            {/* Screenshot Upload */}
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <label className="flex items-center gap-2 mb-2 cursor-pointer">
                <input
                  type="radio"
                  name="proofType"
                  checked={!!formData.paymentScreenshot}
                  onChange={() => setFormData({ ...formData, paymentScreenshot: 'screenshot', txHash: undefined })}
                  className="w-4 h-4 text-purple-600"
                />
                <span className="text-white font-medium">Upload Payment Screenshot</span>
              </label>
              <input
                type="file"
                accept="image/*"
                disabled={!formData.paymentScreenshot}
                onChange={(e) => {
                  if (e.target.files?.[0]) {
                    setFormData({ ...formData, paymentScreenshot: e.target.files[0].name, txHash: undefined });
                  }
                }}
                className="w-full px-3 py-2 bg-black/30 border border-purple-500/30 rounded-lg text-white text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-purple-600 file:text-white hover:file:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <p className="text-xs text-gray-400 mt-1">
                Upload a screenshot of your payment confirmation from wallet
              </p>
            </div>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => setStep('review')}
            className="flex-1 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition-all"
          >
            ← Back
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading || (!formData.txHash && !formData.paymentScreenshot) || (!!formData.txHash && formData.txHash.length < 10)}
            className="flex-1 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 disabled:from-gray-700 disabled:to-gray-700 text-white font-bold rounded-lg transition-all"
          >
            {loading ? 'Submitting...' : 'Verify & Complete'}
          </button>
        </div>
      </motion.div>
    );
  }

  // Submitted Step - Add TGE countdown and education
  if (step === 'submitted') {
    const tgeDateObj = new Date(tgeDate);
    const now = new Date();
    const daysUntilTGE = Math.ceil((tgeDateObj.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-2xl bg-gradient-to-br from-green-900/40 to-blue-900/40 rounded-2xl border-2 border-green-500/30 p-6 backdrop-blur-sm"
      >
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-500/20 rounded-full mb-4">
            <CheckCircle className="w-10 h-10 text-green-400" />
          </div>
          <h3 className="text-3xl font-bold text-white mb-3">Request Submitted! 🎉</h3>
          <p className="text-gray-300 mb-6">
            We've received your OTC purchase request for {formData.allocation && parseFloat(formData.allocation).toLocaleString()} OMK tokens.
          </p>

          <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-5 mb-6">
            <h4 className="font-bold text-blue-300 mb-3">What Happens Next?</h4>
            <ol className="text-left space-y-3 text-sm text-gray-300">
              <li className="flex items-start gap-3">
                <span className="inline-flex items-center justify-center w-6 h-6 bg-blue-500/20 rounded-full text-blue-300 font-bold text-xs flex-shrink-0">1</span>
                <span><strong className="text-white">Payment Verified:</strong> Your crypto payment has been recorded and is being verified on-chain</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="inline-flex items-center justify-center w-6 h-6 bg-blue-500/20 rounded-full text-blue-300 font-bold text-xs flex-shrink-0">2</span>
                <span><strong className="text-white">Admin Review:</strong> {formData.allocation && parseFloat(formData.allocation) >= 20000000 ? 'Large purchase - admin will review within 24 hours' : 'Auto-approved - no review needed'}</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="inline-flex items-center justify-center w-6 h-6 bg-blue-500/20 rounded-full text-blue-300 font-bold text-xs flex-shrink-0">3</span>
                <span><strong className="text-white">Confirmation Email:</strong> You'll receive a confirmation email with your request details</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="inline-flex items-center justify-center w-6 h-6 bg-blue-500/20 rounded-full text-blue-300 font-bold text-xs flex-shrink-0">4</span>
                <span><strong className="text-white">TGE Distribution:</strong> Tokens automatically sent to your wallet at TGE</span>
              </li>
            </ol>
          </div>

          <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4 mb-6">
            <p className="text-sm text-gray-300">
              <strong className="text-green-300">Confirmation sent to:</strong><br />
              {formData.email}
            </p>
          </div>

          {onClose && (
            <button
              onClick={onClose}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold rounded-lg transition-all"
            >
              Close
            </button>
          )}
        </div>
      </motion.div>
    );
  }

  return null;
}
