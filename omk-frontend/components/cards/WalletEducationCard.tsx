'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Wallet, Lock, Key, Shield, Book, ExternalLink, CheckCircle, ArrowRight, Lightbulb } from 'lucide-react';

interface WalletEducationCardProps {
  onGetWallet?: () => void;
  onHaveWallet?: () => void;
  onContactTeacher?: () => void;
  theme?: 'light' | 'dark';
}

type Step = 'intro' | 'what' | 'why' | 'how' | 'security' | 'ready';

export default function WalletEducationCard({ 
  onGetWallet, 
  onHaveWallet, 
  onContactTeacher,
  theme = 'dark' 
}: WalletEducationCardProps) {
  const [step, setStep] = useState<Step>('intro');

  // Intro Step
  if (step === 'intro') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl bg-gradient-to-br from-purple-900/40 to-blue-900/40 rounded-2xl border-2 border-purple-500/30 p-6 backdrop-blur-sm"
      >
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-500/20 rounded-full mb-4">
            <Wallet className="w-8 h-8 text-purple-400" />
          </div>
          <h3 className="text-3xl font-bold text-white mb-3">Understanding Crypto Wallets</h3>
          <p className="text-gray-300 text-lg">
            A crypto wallet is your gateway to owning OMK tokens and investing in real estate!
          </p>
        </div>

        <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-5 mb-6">
          <h4 className="font-bold text-blue-300 mb-3 flex items-center gap-2">
            <Lightbulb className="w-5 h-5" />
            Quick Overview
          </h4>
          <ul className="space-y-3 text-sm text-gray-300">
            <li className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span><strong className="text-white">It's like a digital bank account</strong> - but you're the only one in control</span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span><strong className="text-white">Store & manage your tokens</strong> - OMK tokens for real estate investment</span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span><strong className="text-white">Free & easy to set up</strong> - takes less than 5 minutes</span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span><strong className="text-white">You own your assets</strong> - not controlled by any bank or company</span>
            </li>
          </ul>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => setStep('what')}
            className="py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-bold rounded-lg transition-all"
          >
            Learn More →
          </button>
          <button
            onClick={onContactTeacher}
            className="py-3 bg-gradient-to-r from-orange-600 to-yellow-600 hover:from-orange-500 hover:to-yellow-500 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2"
          >
            <Book className="w-5 h-5" />
            Get Help
          </button>
        </div>
      </motion.div>
    );
  }

  // What is a Wallet
  if (step === 'what') {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-full max-w-2xl bg-gradient-to-br from-purple-900/40 to-blue-900/40 rounded-2xl border-2 border-purple-500/30 p-6 backdrop-blur-sm"
      >
        <div className="mb-6">
          <h3 className="text-2xl font-bold text-white mb-3 flex items-center gap-3">
            <Wallet className="w-7 h-7 text-purple-400" />
            What is a Crypto Wallet?
          </h3>
        </div>

        <div className="space-y-4 mb-6">
          <div className="bg-purple-900/20 border border-purple-500/30 rounded-xl p-5">
            <h4 className="font-bold text-purple-300 mb-3">Think of it like...</h4>
            <div className="space-y-3 text-gray-300">
              <p><strong className="text-white">📧 An Email Address</strong> - Just like you need an email to send/receive messages, you need a wallet to send/receive crypto</p>
              <p><strong className="text-white">🏦 A Bank Account</strong> - Stores your digital money (but YOU control it, not a bank)</p>
              <p><strong className="text-white">🔑 A Safe with Keys</strong> - Only you have the keys to access your funds</p>
            </div>
          </div>

          <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-5">
            <h4 className="font-bold text-blue-300 mb-3">A wallet gives you:</h4>
            <ul className="space-y-2 text-gray-300">
              <li className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <span>A <strong className="text-white">unique address</strong> (like: 0xABC...123)</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <span>The ability to <strong className="text-white">send & receive</strong> OMK tokens</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <span><strong className="text-white">Full control</strong> over your investments</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <span><strong className="text-white">Security</strong> - protected by cryptography</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => setStep('intro')}
            className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition-all"
          >
            ← Back
          </button>
          <button
            onClick={() => setStep('why')}
            className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-bold rounded-lg transition-all"
          >
            Why Do I Need One? →
          </button>
        </div>
      </motion.div>
    );
  }

  // Why You Need a Wallet
  if (step === 'why') {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-full max-w-2xl bg-gradient-to-br from-purple-900/40 to-blue-900/40 rounded-2xl border-2 border-purple-500/30 p-6 backdrop-blur-sm"
      >
        <div className="mb-6">
          <h3 className="text-2xl font-bold text-white mb-3 flex items-center gap-3">
            <Key className="w-7 h-7 text-blue-400" />
            Why You Need a Wallet for OMK
          </h3>
        </div>

        <div className="space-y-4 mb-6">
          <div className="bg-green-900/20 border border-green-500/30 rounded-xl p-5">
            <h4 className="font-bold text-green-300 mb-3">🎯 To Own OMK Tokens</h4>
            <p className="text-gray-300">
              OMK tokens represent your share in real estate investments. A wallet is where your tokens live - 
              it's proof that YOU own them, not stored on someone else's server.
            </p>
          </div>

          <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-5">
            <h4 className="font-bold text-blue-300 mb-3">💰 To Receive Rental Income</h4>
            <p className="text-gray-300">
              When properties generate rental income, your earnings (in USDT) are sent directly to your wallet. 
              No middleman, no delays, no bank fees.
            </p>
          </div>

          <div className="bg-purple-900/20 border border-purple-500/30 rounded-xl p-5">
            <h4 className="font-bold text-purple-300 mb-3">🔒 Full Control & Security</h4>
            <p className="text-gray-300 mb-3">
              Unlike traditional platforms where the company holds your assets, with a crypto wallet:
            </p>
            <ul className="space-y-2 text-sm text-gray-300">
              <li>✅ <strong className="text-white">You</strong> control your tokens 24/7</li>
              <li>✅ <strong className="text-white">Nobody</strong> can freeze your account</li>
              <li>✅ <strong className="text-white">No</strong> withdrawal limits or restrictions</li>
              <li>✅ <strong className="text-white">Your assets</strong>, your rules</li>
            </ul>
          </div>

          <div className="bg-orange-900/20 border border-orange-500/30 rounded-xl p-4">
            <p className="text-sm text-gray-300">
              💡 <strong className="text-orange-300">Think of it this way:</strong> Having OMK tokens without a wallet 
              is like having a house deed but nowhere to store it safely!
            </p>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => setStep('what')}
            className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition-all"
          >
            ← Back
          </button>
          <button
            onClick={() => setStep('how')}
            className="flex-1 py-3 bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-500 hover:to-green-500 text-white font-bold rounded-lg transition-all"
          >
            How to Get One →
          </button>
        </div>
      </motion.div>
    );
  }

  // How to Get a Wallet
  if (step === 'how') {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-full max-w-2xl bg-gradient-to-br from-purple-900/40 to-blue-900/40 rounded-2xl border-2 border-purple-500/30 p-6 backdrop-blur-sm"
      >
        <div className="mb-6">
          <h3 className="text-2xl font-bold text-white mb-3 flex items-center gap-3">
            <Shield className="w-7 h-7 text-green-400" />
            How to Get a Wallet (Easy!)
          </h3>
          <p className="text-gray-300">
            We recommend <strong className="text-white">MetaMask</strong> - the most popular and trusted wallet. It's free and takes 5 minutes.
          </p>
        </div>

        <div className="bg-gradient-to-r from-orange-900/30 to-yellow-900/30 border border-orange-500/30 rounded-xl p-5 mb-6">
          <h4 className="font-bold text-orange-300 mb-4 text-lg">📱 Quick Setup Guide:</h4>
          <ol className="space-y-4">
            <li className="flex gap-3">
              <span className="inline-flex items-center justify-center w-7 h-7 bg-orange-500/20 rounded-full text-orange-300 font-bold flex-shrink-0">1</span>
              <div>
                <p className="font-semibold text-white mb-1">Install MetaMask</p>
                <p className="text-sm text-gray-300">Download as a browser extension (Chrome, Firefox, Brave) or mobile app</p>
              </div>
            </li>
            <li className="flex gap-3">
              <span className="inline-flex items-center justify-center w-7 h-7 bg-orange-500/20 rounded-full text-orange-300 font-bold flex-shrink-0">2</span>
              <div>
                <p className="font-semibold text-white mb-1">Create New Wallet</p>
                <p className="text-sm text-gray-300">Click "Create a new wallet" and set a strong password</p>
              </div>
            </li>
            <li className="flex gap-3">
              <span className="inline-flex items-center justify-center w-7 h-7 bg-orange-500/20 rounded-full text-orange-300 font-bold flex-shrink-0">3</span>
              <div>
                <p className="font-semibold text-white mb-1">Save Your Recovery Phrase</p>
                <p className="text-sm text-gray-300">Write down the 12 words and store them safely (NEVER share this!)</p>
              </div>
            </li>
            <li className="flex gap-3">
              <span className="inline-flex items-center justify-center w-7 h-7 bg-orange-500/20 rounded-full text-orange-300 font-bold flex-shrink-0">4</span>
              <div>
                <p className="font-semibold text-white mb-1">Done! 🎉</p>
                <p className="text-sm text-gray-300">You now have a wallet address starting with "0x..."</p>
              </div>
            </li>
          </ol>
        </div>

        <div className="bg-red-900/20 border border-red-500/30 rounded-xl p-4 mb-6">
          <h4 className="font-bold text-red-300 mb-2 flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Important Security Tip
          </h4>
          <p className="text-sm text-gray-300">
            Your <strong className="text-white">recovery phrase (seed phrase)</strong> is like a master password. 
            Anyone with these 12 words can access your wallet. <strong className="text-red-300">NEVER share it with anyone!</strong>
          </p>
        </div>

        <div className="space-y-3">
          <button
            onClick={() => window.open('https://metamask.io/download/', '_blank')}
            className="w-full py-4 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-3"
          >
            <img src="https://upload.wikimedia.org/wikipedia/commons/3/36/MetaMask_Fox.svg" alt="MetaMask" className="w-6 h-6" />
            Get MetaMask Now
            <ExternalLink className="w-5 h-5" />
          </button>

          <button
            onClick={onContactTeacher}
            className="w-full py-3 bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-500 hover:to-orange-500 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2"
          >
            <Book className="w-5 h-5" />
            Need Step-by-Step Help? Talk to Teacher Bee
          </button>

          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => setStep('why')}
              className="py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition-all"
            >
              ← Back
            </button>
            <button
              onClick={() => setStep('security')}
              className="py-3 bg-purple-600 hover:bg-purple-500 text-white font-bold rounded-lg transition-all"
            >
              Security Tips →
            </button>
          </div>
        </div>
      </motion.div>
    );
  }

  // Security Best Practices
  if (step === 'security') {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-full max-w-2xl bg-gradient-to-br from-purple-900/40 to-blue-900/40 rounded-2xl border-2 border-purple-500/30 p-6 backdrop-blur-sm"
      >
        <div className="mb-6">
          <h3 className="text-2xl font-bold text-white mb-3 flex items-center gap-3">
            <Lock className="w-7 h-7 text-red-400" />
            Security Best Practices
          </h3>
          <p className="text-gray-300">
            Keep your wallet safe with these simple rules:
          </p>
        </div>

        <div className="space-y-3 mb-6">
          <div className="bg-green-900/20 border border-green-500/30 rounded-xl p-4">
            <h4 className="font-semibold text-green-300 mb-2 flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              ✅ DO These Things
            </h4>
            <ul className="space-y-2 text-sm text-gray-300">
              <li>• Write down your recovery phrase on paper</li>
              <li>• Store it in a safe place (not on your computer)</li>
              <li>• Use a strong, unique password</li>
              <li>• Double-check addresses before sending tokens</li>
              <li>• Keep your browser and MetaMask updated</li>
            </ul>
          </div>

          <div className="bg-red-900/20 border border-red-500/30 rounded-xl p-4">
            <h4 className="font-semibold text-red-300 mb-2 flex items-center gap-2">
              <Shield className="w-5 h-5" />
              ❌ NEVER Do These Things
            </h4>
            <ul className="space-y-2 text-sm text-gray-300">
              <li>• <strong className="text-white">NEVER</strong> share your recovery phrase with anyone</li>
              <li>• <strong className="text-white">NEVER</strong> enter your phrase on websites</li>
              <li>• <strong className="text-white">NEVER</strong> take screenshots of your phrase</li>
              <li>• <strong className="text-white">NEVER</strong> store it in email or cloud storage</li>
              <li>• <strong className="text-white">NEVER</strong> give it to "support" (scammers!)</li>
            </ul>
          </div>

          <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-xl p-4">
            <p className="text-sm text-gray-300">
              ⚠️ <strong className="text-yellow-300">Remember:</strong> Omakh team will NEVER ask for your recovery phrase or private keys. 
              If someone does, it's a scam!
            </p>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => setStep('how')}
            className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition-all"
          >
            ← Back
          </button>
          <button
            onClick={() => setStep('ready')}
            className="flex-1 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-bold rounded-lg transition-all"
          >
            I'm Ready! →
          </button>
        </div>
      </motion.div>
    );
  }

  // Ready to Start
  if (step === 'ready') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-2xl bg-gradient-to-br from-green-900/40 to-emerald-900/40 rounded-2xl border-2 border-green-500/30 p-6 backdrop-blur-sm"
      >
        <div className="text-center mb-6">
          <div className="text-6xl mb-4">🎉</div>
          <h3 className="text-3xl font-bold text-white mb-3">You're All Set!</h3>
          <p className="text-gray-300 text-lg">
            Choose your next step:
          </p>
        </div>

        <div className="space-y-4">
          <button
            onClick={() => window.open('https://metamask.io/download/', '_blank')}
            className="w-full py-4 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-3 text-lg"
          >
            <Wallet className="w-6 h-6" />
            Get MetaMask & Create Wallet
            <ExternalLink className="w-5 h-5" />
          </button>

          <button
            onClick={onHaveWallet}
            className="w-full py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-3 text-lg"
          >
            <CheckCircle className="w-6 h-6" />
            I Already Have a Wallet
            <ArrowRight className="w-5 h-5" />
          </button>

          <button
            onClick={onContactTeacher}
            className="w-full py-3 bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-500 hover:to-orange-500 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2"
          >
            <Book className="w-5 h-5" />
            I Need More Help from Teacher Bee
          </button>
        </div>

        <div className="mt-6 bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
          <p className="text-sm text-gray-300 text-center">
            💡 <strong className="text-white">New to crypto?</strong> Teacher Bee can guide you step-by-step through 
            creating your first wallet and making your first investment!
          </p>
        </div>
      </motion.div>
    );
  }

  return null;
}
