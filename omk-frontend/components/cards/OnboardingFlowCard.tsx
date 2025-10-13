'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, Home, DollarSign, Shield, Zap, Users, CheckCircle, ArrowRight, Sparkles, Target } from 'lucide-react';

interface OnboardingFlowCardProps {
  userName?: string;
  onComplete?: () => void;
}

type Step = 'welcome' | 'tokenization' | 'real_estate' | 'earnings' | 'omk_value' | 'cta';

export default function OnboardingFlowCard({ userName = "there", onComplete }: OnboardingFlowCardProps) {
  const [step, setStep] = useState<Step>('welcome');

  const nextStep = () => {
    const steps: Step[] = ['welcome', 'tokenization', 'real_estate', 'earnings', 'omk_value', 'cta'];
    const currentIndex = steps.indexOf(step);
    if (currentIndex < steps.length - 1) {
      setStep(steps[currentIndex + 1]);
    }
  };

  // Welcome Screen
  if (step === 'welcome') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-3xl bg-gradient-to-br from-blue-900/50 to-purple-900/50 rounded-2xl border-2 border-blue-500/30 p-8 backdrop-blur-sm"
      >
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full mb-6 animate-pulse">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-4xl font-bold text-white mb-4">
            Welcome to Omakh, {userName}! 🎉
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            You're about to discover how to build wealth through real estate investing - made simple with blockchain technology.
          </p>
          
          <div className="bg-blue-900/30 border border-blue-500/30 rounded-xl p-6 mb-8">
            <p className="text-gray-300 mb-4">In the next 60 seconds, you'll learn:</p>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-left">
                <CheckCircle className="w-5 h-5 text-green-400 inline mr-2" />
                <span className="text-white">What property tokenization is</span>
              </div>
              <div className="text-left">
                <CheckCircle className="w-5 h-5 text-green-400 inline mr-2" />
                <span className="text-white">How you earn passive income</span>
              </div>
              <div className="text-left">
                <CheckCircle className="w-5 h-5 text-green-400 inline mr-2" />
                <span className="text-white">Why OMK tokens are valuable</span>
              </div>
              <div className="text-left">
                <CheckCircle className="w-5 h-5 text-green-400 inline mr-2" />
                <span className="text-white">How to get started today</span>
              </div>
            </div>
          </div>

          <button
            onClick={nextStep}
            className="w-full py-4 bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-400 hover:to-orange-400 text-black font-bold text-lg rounded-xl transition-all flex items-center justify-center gap-3"
          >
            Let's Go!
            <ArrowRight className="w-6 h-6" />
          </button>
        </div>
      </motion.div>
    );
  }

  // Property Tokenization
  if (step === 'tokenization') {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-full max-w-3xl bg-gradient-to-br from-purple-900/50 to-pink-900/50 rounded-2xl border-2 border-purple-500/30 p-8 backdrop-blur-sm"
      >
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center">
            <Home className="w-8 h-8 text-purple-400" />
          </div>
          <div>
            <h3 className="text-3xl font-bold text-white">Property Tokenization</h3>
            <p className="text-purple-300">The Future of Real Estate</p>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-purple-900/30 border border-purple-500/30 rounded-xl p-6">
            <h4 className="text-xl font-bold text-white mb-3">How It Works:</h4>
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-purple-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-purple-300 font-bold">1</span>
                </div>
                <div>
                  <p className="font-semibold text-white mb-1">We Buy Premium Properties</p>
                  <p className="text-gray-300 text-sm">Luxury Airbnb properties in high-demand locations</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-purple-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-purple-300 font-bold">2</span>
                </div>
                <div>
                  <p className="font-semibold text-white mb-1">Each Property = 1 Block with 50 Slots</p>
                  <p className="text-gray-300 text-sm">Every property has exactly 50 ownership slots you can buy</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-purple-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-purple-300 font-bold">3</span>
                </div>
                <div>
                  <p className="font-semibold text-white mb-1">Buy Slots with OMK Tokens</p>
                  <p className="text-gray-300 text-sm">Purchase ownership slots - 90% converted to USDT (stable), 10% staked in OMK</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-purple-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-purple-300 font-bold">4</span>
                </div>
                <div>
                  <p className="font-semibold text-white mb-1">Earn EXP Points!</p>
                  <p className="text-gray-300 text-sm">Each slot you own earns platform EXP - used for airdrops & community rewards</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-green-900/20 border border-green-500/30 rounded-xl p-5">
            <p className="text-green-300 font-semibold flex items-center gap-2">
              <Target className="w-5 h-5" />
              Result: You own a piece of real estate without buying a whole property!
            </p>
          </div>
        </div>

        <button
          onClick={nextStep}
          className="w-full mt-6 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-bold text-lg rounded-xl transition-all"
        >
          Next: How You Earn Money →
        </button>
      </motion.div>
    );
  }

  // Real Estate Returns
  if (step === 'real_estate') {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-full max-w-3xl bg-gradient-to-br from-green-900/50 to-emerald-900/50 rounded-2xl border-2 border-green-500/30 p-8 backdrop-blur-sm"
      >
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center">
            <TrendingUp className="w-8 h-8 text-green-400" />
          </div>
          <div>
            <h3 className="text-3xl font-bold text-white">Multiple Income Streams</h3>
            <p className="text-green-300">Earn While You Sleep</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-green-900/30 border border-green-500/30 rounded-xl p-6">
            <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mb-4">
              <Home className="w-6 h-6 text-blue-400" />
            </div>
            <h4 className="font-bold text-white mb-3 text-lg">1. Airbnb Rental Income</h4>
            <p className="text-gray-300 text-sm mb-4">
              Properties are rented on Airbnb. You get your share of the rental income every month - automatically sent to your wallet!
            </p>
            <div className="bg-blue-900/30 border border-blue-500/30 rounded-lg p-3">
              <p className="text-xs text-gray-400">Example:</p>
              <p className="text-lg font-bold text-white">10% - 30% Annual Return</p>
            </div>
          </div>

          <div className="bg-green-900/30 border border-green-500/30 rounded-xl p-6">
            <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-purple-400" />
            </div>
            <h4 className="font-bold text-white mb-3 text-lg">2. Property Value Growth</h4>
            <p className="text-gray-300 text-sm mb-4">
              As property values increase, so does the value of your blocks. Sell anytime on our marketplace!
            </p>
            <div className="bg-purple-900/30 border border-purple-500/30 rounded-lg p-3">
              <p className="text-xs text-gray-400">Example:</p>
              <p className="text-lg font-bold text-white">5% - 15% Annual Growth</p>
            </div>
          </div>
        </div>

        <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-xl p-5 mb-6">
          <p className="text-yellow-300 font-semibold text-center">
            💰 Potential Combined Returns: 15% - 45% per year!
          </p>
        </div>

        <button
          onClick={nextStep}
          className="w-full py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-bold text-lg rounded-xl transition-all"
        >
          Next: More Ways to Earn →
        </button>
      </motion.div>
    );
  }

  // Additional Earnings
  if (step === 'earnings') {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-full max-w-3xl bg-gradient-to-br from-orange-900/50 to-red-900/50 rounded-2xl border-2 border-orange-500/30 p-8 backdrop-blur-sm"
      >
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 bg-orange-500/20 rounded-full flex items-center justify-center">
            <DollarSign className="w-8 h-8 text-orange-400" />
          </div>
          <div>
            <h3 className="text-3xl font-bold text-white">Even More Earnings!</h3>
            <p className="text-orange-300">Maximize Your Returns</p>
          </div>
        </div>

        <div className="space-y-4 mb-6">
          <div className="bg-orange-900/30 border border-orange-500/30 rounded-xl p-6">
            <div className="flex items-start gap-4">
              <Shield className="w-8 h-8 text-blue-400 flex-shrink-0" />
              <div>
                <h4 className="font-bold text-white mb-2 text-lg">3. Staking Rewards</h4>
                <p className="text-gray-300 mb-3">
                  Stake your OMK tokens in our platform and earn additional passive income. No risk, withdraw anytime!
                </p>
                <div className="bg-blue-900/30 border border-blue-500/30 rounded-lg p-3 inline-block">
                  <p className="text-sm font-bold text-white">Up to 12% APY</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-orange-900/30 border border-orange-500/30 rounded-xl p-6">
            <div className="flex items-start gap-4">
              <Users className="w-8 h-8 text-green-400 flex-shrink-0" />
              <div>
                <h4 className="font-bold text-white mb-2 text-lg">4. Governance Rewards</h4>
                <p className="text-gray-300 mb-3">
                  Participate in platform decisions and earn rewards for active participation. Your voice matters!
                </p>
                <div className="bg-green-900/30 border border-green-500/30 rounded-lg p-3 inline-block">
                  <p className="text-sm font-bold text-white">Bonus Rewards</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-yellow-900/30 to-orange-900/30 border border-yellow-500/30 rounded-xl p-6">
          <h4 className="font-bold text-white text-center mb-4 text-xl">Total Earning Potential:</h4>
          <div className="text-center">
            <p className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-400 mb-2">
              20% - 60%+
            </p>
            <p className="text-gray-300">Combined Annual Returns</p>
          </div>
        </div>

        <button
          onClick={nextStep}
          className="w-full mt-6 py-4 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 text-white font-bold text-lg rounded-xl transition-all"
        >
          Next: Why OMK Tokens? →
        </button>
      </motion.div>
    );
  }

  // OMK Token Value
  if (step === 'omk_value') {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-full max-w-3xl bg-gradient-to-br from-yellow-900/50 to-amber-900/50 rounded-2xl border-2 border-yellow-500/30 p-8 backdrop-blur-sm"
      >
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 bg-yellow-500/20 rounded-full flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-yellow-400" />
          </div>
          <div>
            <h3 className="text-3xl font-bold text-white">Why OMK Tokens Are Valuable</h3>
            <p className="text-yellow-300">Your Key to Real Estate Wealth</p>
          </div>
        </div>

        <div className="space-y-4 mb-6">
          <div className="bg-yellow-900/30 border border-yellow-500/30 rounded-xl p-5">
            <h4 className="font-bold text-white mb-3 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-400" />
              Only Way to Invest
            </h4>
            <p className="text-gray-300">
              OMK tokens are the ONLY currency accepted for property blocks. More properties = higher OMK demand = higher OMK value!
            </p>
          </div>

          <div className="bg-yellow-900/30 border border-yellow-500/30 rounded-xl p-5">
            <h4 className="font-bold text-white mb-3 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-400" />
              Limited Supply
            </h4>
            <p className="text-gray-300">
              Only 1 billion OMK tokens will ever exist. As demand grows with more users and properties, scarcity drives value up.
            </p>
          </div>

          <div className="bg-yellow-900/30 border border-yellow-500/30 rounded-xl p-5">
            <h4 className="font-bold text-white mb-3 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-400" />
              Real Utility
            </h4>
            <p className="text-gray-300">
              Unlike meme coins, OMK has real-world use. It represents actual real estate value and rental income streams.
            </p>
          </div>

          <div className="bg-yellow-900/30 border border-yellow-500/30 rounded-xl p-5">
            <h4 className="font-bold text-white mb-3 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-400" />
              Early Adopter Advantage
            </h4>
            <p className="text-gray-300">
              You're getting in early! As the platform grows, early token holders benefit most from appreciation.
            </p>
          </div>
        </div>

        <div className="bg-gradient-to-r from-green-900/30 to-emerald-900/30 border border-green-500/30 rounded-xl p-6 text-center">
          <p className="text-2xl font-bold text-white mb-2">
            OMK = Your Gateway to Real Estate Wealth 🚀
          </p>
          <p className="text-gray-300">
            Own the currency that powers the future of property investing
          </p>
        </div>

        <button
          onClick={nextStep}
          className="w-full mt-6 py-4 bg-gradient-to-r from-yellow-600 to-amber-600 hover:from-yellow-500 hover:to-amber-500 text-black font-bold text-lg rounded-xl transition-all"
        >
          I'm Ready! Let's Get OMK →
        </button>
      </motion.div>
    );
  }

  // CTA - Get OMK
  if (step === 'cta') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-3xl bg-gradient-to-br from-green-900/50 to-blue-900/50 rounded-2xl border-2 border-green-500/30 p-8 backdrop-blur-sm"
      >
        <div className="text-center">
          <div className="text-6xl mb-4">🎉</div>
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Start Earning?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            You now know how Omakh works. Time to take action!
          </p>

          <div className="bg-blue-900/30 border border-blue-500/30 rounded-xl p-6 mb-8">
            <h3 className="font-bold text-white mb-4 text-xl">Quick Recap:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-left">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <span className="text-gray-300">Buy OMK tokens</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <span className="text-gray-300">Invest in properties</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <span className="text-gray-300">Earn rental income</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <span className="text-gray-300">Stake for rewards</span>
              </div>
            </div>
          </div>

          <button
            onClick={onComplete}
            className="w-full py-5 bg-gradient-to-r from-green-600 via-emerald-600 to-blue-600 hover:from-green-500 hover:via-emerald-500 hover:to-blue-500 text-white font-bold text-xl rounded-xl transition-all shadow-2xl flex items-center justify-center gap-3"
          >
            <Sparkles className="w-6 h-6" />
            Get OMK Tokens Now!
            <ArrowRight className="w-6 h-6" />
          </button>

          <p className="text-sm text-gray-400 mt-4">
            Start building wealth through real estate today 🏠
          </p>
        </div>
      </motion.div>
    );
  }

  return null;
}
