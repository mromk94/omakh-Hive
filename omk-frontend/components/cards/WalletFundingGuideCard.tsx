'use client';

import { motion } from 'framer-motion';
import { Wallet, CreditCard, Building2, ArrowRight, Info, CheckCircle, ExternalLink } from 'lucide-react';

interface WalletFundingGuideCardProps {
  onComplete?: () => void;
}

export default function WalletFundingGuideCard({ onComplete }: WalletFundingGuideCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-4xl bg-gradient-to-br from-blue-900/50 to-purple-900/50 rounded-2xl border-2 border-blue-500/30 p-8 backdrop-blur-sm"
    >
      <div className="flex items-center gap-4 mb-6">
        <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center">
          <Wallet className="w-8 h-8 text-blue-400" />
        </div>
        <div>
          <h2 className="text-3xl font-bold text-white">Fund Your Wallet</h2>
          <p className="text-blue-300">Add money before buying OMK</p>
        </div>
      </div>

      {/* Why Fund First */}
      <div className="bg-blue-900/30 border border-blue-500/30 rounded-xl p-6 mb-6">
        <div className="flex items-start gap-3 mb-4">
          <Info className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-bold text-white text-lg mb-2">Why Do I Need to Fund My Wallet?</h3>
            <p className="text-gray-300 mb-3">
              Think of your MetaMask wallet like a bank account. Right now it's empty! You need to add crypto (like ETH or USDT) to buy OMK tokens.
            </p>
            <div className="bg-blue-900/40 border border-blue-500/30 rounded-lg p-3">
              <p className="text-sm text-blue-300">
                💡 You can't buy OMK with regular money directly - you need cryptocurrency first!
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Funding Methods */}
      <div className="space-y-4 mb-6">
        <h3 className="font-bold text-white text-xl">How to Fund Your Wallet:</h3>

        {/* Method 1: Crypto Exchange */}
        <div className="bg-purple-900/30 border border-purple-500/30 rounded-xl p-5">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center flex-shrink-0">
              <Building2 className="w-6 h-6 text-purple-400" />
            </div>
            <div className="flex-1">
              <h4 className="font-bold text-white mb-2 text-lg">Option 1: Buy from Exchange (Recommended)</h4>
              <p className="text-gray-300 text-sm mb-3">
                The easiest way! Buy ETH or USDT on Coinbase, Binance, or Kraken, then send to your wallet.
              </p>
              
              <div className="bg-purple-900/40 rounded-lg p-4 mb-3">
                <p className="text-xs text-purple-300 font-semibold mb-2">Step-by-Step:</p>
                <ol className="space-y-2 text-sm text-gray-300">
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400 font-bold">1.</span>
                    <span>Sign up on Coinbase or Binance</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400 font-bold">2.</span>
                    <span>Buy ETH or USDT with your credit card</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400 font-bold">3.</span>
                    <span>Click "Send" or "Withdraw"</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400 font-bold">4.</span>
                    <span>Paste your MetaMask address (starts with 0x...)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400 font-bold">5.</span>
                    <span>Wait 5-10 minutes for it to arrive!</span>
                  </li>
                </ol>
              </div>

              <div className="flex gap-3">
                <a href="https://www.coinbase.com/join" target="_blank" rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-sm transition-all">
                  <ExternalLink className="w-4 h-4" />
                  Open Coinbase
                </a>
                <a href="https://www.binance.com/en/register" target="_blank" rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-sm transition-all">
                  <ExternalLink className="w-4 h-4" />
                  Open Binance
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Method 2: Credit Card */}
        <div className="bg-green-900/30 border border-green-500/30 rounded-xl p-5">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center flex-shrink-0">
              <CreditCard className="w-6 h-6 text-green-400" />
            </div>
            <div className="flex-1">
              <h4 className="font-bold text-white mb-2 text-lg">Option 2: Buy Directly in MetaMask</h4>
              <p className="text-gray-300 text-sm mb-3">
                MetaMask lets you buy crypto with a credit card directly! (Higher fees but faster)
              </p>
              
              <div className="bg-green-900/40 rounded-lg p-4 mb-3">
                <p className="text-xs text-green-300 font-semibold mb-2">Quick Steps:</p>
                <ol className="space-y-2 text-sm text-gray-300">
                  <li className="flex items-start gap-2">
                    <span className="text-green-400 font-bold">1.</span>
                    <span>Open MetaMask extension</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-400 font-bold">2.</span>
                    <span>Click "Buy"</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-400 font-bold">3.</span>
                    <span>Choose ETH or USDT</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-400 font-bold">4.</span>
                    <span>Enter your credit card info</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-400 font-bold">5.</span>
                    <span>Funds appear instantly!</span>
                  </li>
                </ol>
              </div>

              <div className="bg-yellow-900/30 border border-yellow-500/30 rounded-lg p-3">
                <p className="text-xs text-yellow-300">
                  ⚠️ Note: Fees are usually 3-5% with this method vs 1-2% on exchanges
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recommended Amount */}
      <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-500/30 rounded-xl p-5 mb-6">
        <h4 className="font-bold text-white mb-3 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-blue-400" />
          How Much Should I Add?
        </h4>
        <div className="space-y-2 text-gray-300 text-sm">
          <p><span className="font-semibold text-white">For OMK Purchase:</span> Minimum $50-100 USDT or ETH</p>
          <p><span className="font-semibold text-white">Recommended:</span> $200-500 for property investments</p>
          <p><span className="font-semibold text-white">Gas Fees:</span> Keep extra $10-20 ETH for transaction fees</p>
        </div>
      </div>

      {/* Important Note */}
      <div className="bg-orange-900/30 border border-orange-500/30 rounded-xl p-4 mb-6">
        <h4 className="font-bold text-orange-300 mb-2 flex items-center gap-2">
          <Info className="w-5 h-5" />
          Important!
        </h4>
        <ul className="space-y-1 text-sm text-gray-300">
          <li>✅ Double-check your wallet address before sending</li>
          <li>✅ Start with a small test amount first ($10-20)</li>
          <li>✅ ONLY send ETH or USDT on Ethereum network</li>
          <li>⚠️ Sending on wrong network = lost funds forever!</li>
        </ul>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <button
          onClick={onComplete}
          className="flex-1 py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-bold rounded-xl transition-all flex items-center justify-center gap-2"
        >
          I've Funded My Wallet!
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>

      <p className="text-center text-gray-400 text-sm mt-4">
        Need help? Contact Teacher Bee 🐝 for step-by-step guidance!
      </p>
    </motion.div>
  );
}
