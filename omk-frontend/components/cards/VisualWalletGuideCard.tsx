'use client';

import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Download, Shield, Key, CheckCircle, AlertTriangle, Upload, ArrowRight, ExternalLink, Play, Camera } from 'lucide-react';

interface VisualWalletGuideCardProps {
  onComplete?: () => void;
  onAskTeacher?: (question: string, screenshot?: File) => void;
}

type Step = 1 | 2 | 3 | 4 | 5;

export default function VisualWalletGuideCard({ onComplete, onAskTeacher }: VisualWalletGuideCardProps) {
  const [currentStep, setCurrentStep] = useState<Step>(1);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onAskTeacher) {
      onAskTeacher(`I'm stuck on Step ${currentStep}. Can you help me with this screenshot?`, file);
    }
  };

  const steps = [
    {
      title: "Install MetaMask",
      icon: <Download className="w-8 h-8 text-orange-400" />,
      color: "orange",
      video: "https://www.youtube.com/watch?v=Af_lQ1zUnoM",
      content: (
        <div className="space-y-4">
          <a href="https://metamask.io/download/" target="_blank" rel="noopener noreferrer"
            className="block px-6 py-4 bg-orange-600 hover:bg-orange-500 text-white font-bold rounded-lg transition-all text-center">
            <ExternalLink className="w-5 h-5 inline mr-2" />
            Open metamask.io/download
          </a>
          <div className="bg-purple-900/30 border border-purple-500/30 rounded-lg p-4">
            <p className="text-white font-semibold mb-2">1. Choose your browser (Chrome, Firefox, Brave)</p>
            <p className="text-white font-semibold mb-2">2. Click "Add to Browser"</p>
            <p className="text-white font-semibold">3. Look for the 🦊 fox icon in your toolbar!</p>
          </div>
        </div>
      )
    },
    {
      title: "Create Your Wallet",
      icon: <Key className="w-8 h-8 text-green-400" />,
      color: "green",
      content: (
        <div className="space-y-4">
          <div className="bg-green-900/30 border border-green-500/30 rounded-lg p-4">
            <p className="text-white font-semibold mb-2">1. Click the 🦊 MetaMask icon</p>
            <p className="text-white font-semibold mb-2">2. Click "Create a new wallet"</p>
            <p className="text-white font-semibold mb-2">3. Agree to terms</p>
            <p className="text-white font-semibold mb-2">4. Create a strong password</p>
            <p className="text-white font-semibold">5. Click "Create"</p>
          </div>
          <div className="bg-yellow-900/30 border border-yellow-500/30 rounded-lg p-3">
            <p className="text-sm text-yellow-300">⚠️ Write down your password! You'll need it to unlock MetaMask.</p>
          </div>
        </div>
      )
    },
    {
      title: "Save Recovery Phrase",
      icon: <Shield className="w-8 h-8 text-red-400" />,
      color: "red",
      video: "https://www.youtube.com/watch?v=JBmq-tJh5qQ",
      content: (
        <div className="space-y-4">
          <div className="bg-red-900/40 border-2 border-red-500/50 rounded-lg p-4">
            <div className="flex items-start gap-2 mb-3">
              <AlertTriangle className="w-6 h-6 text-red-400 flex-shrink-0" />
              <div>
                <p className="font-bold text-red-300 mb-2">⚠️ MOST IMPORTANT STEP!</p>
                <p className="text-gray-200 text-sm">Your 12-word recovery phrase is like a master password. Lose it = lose your wallet FOREVER!</p>
              </div>
            </div>
          </div>
          <div className="bg-purple-900/30 border border-purple-500/30 rounded-lg p-4">
            <p className="text-white font-semibold mb-2">1. Click "Reveal Secret Recovery Phrase"</p>
            <p className="text-white font-semibold mb-2">2. Write down ALL 12 words IN ORDER on paper</p>
            <p className="text-white font-semibold mb-2">3. Store paper in safe place</p>
          </div>
          <div className="bg-red-900/30 border border-red-500/30 rounded-lg p-3">
            <p className="text-sm text-red-300 font-semibold mb-2">🚨 NEVER:</p>
            <p className="text-xs text-red-200">❌ Take screenshot | ❌ Save in email | ❌ Share with anyone</p>
            <p className="text-xs text-green-300 mt-2">✅ Write on paper with pen ONLY</p>
          </div>
        </div>
      )
    },
    {
      title: "Confirm Your Phrase",
      icon: <CheckCircle className="w-8 h-8 text-blue-400" />,
      color: "blue",
      content: (
        <div className="space-y-4">
          <div className="bg-blue-900/30 border border-blue-500/30 rounded-lg p-4">
            <p className="text-white font-semibold mb-2">1. MetaMask will show your 12 words jumbled</p>
            <p className="text-white font-semibold mb-2">2. Click them in the correct order (1,2,3...12)</p>
            <p className="text-white font-semibold">3. Click "Confirm"</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <p className="text-gray-400 text-xs mb-2">You'll see something like:</p>
            <div className="grid grid-cols-4 gap-2">
              {['zebra', 'apple', 'cherry', 'dog'].map((word) => (
                <div key={word} className="bg-gray-700 rounded px-2 py-1 text-center text-xs text-gray-300">{word}</div>
              ))}
            </div>
            <p className="text-xs text-blue-300 mt-2">Click them in YOUR order!</p>
          </div>
        </div>
      )
    },
    {
      title: "You're Done!",
      icon: <CheckCircle className="w-12 h-12 text-white" />,
      color: "green",
      content: (
        <div className="text-center space-y-4">
          <div className="text-6xl mb-4">🎉</div>
          <h3 className="text-2xl font-bold text-white">Wallet Created Successfully!</h3>
          <div className="bg-green-900/30 border border-green-500/30 rounded-lg p-4">
            <p className="text-green-300 mb-2">Your wallet address starts with "0x..."</p>
            <p className="text-gray-300 text-sm">You can now receive and send OMK tokens!</p>
          </div>
          <button onClick={onComplete}
            className="w-full py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-bold rounded-xl transition-all">
            Next: Fund My Wallet 💰
          </button>
        </div>
      )
    }
  ];

  const step = steps[currentStep - 1];

  return (
    <div className="w-full max-w-4xl">
      {/* Progress */}
      <div className="bg-gray-900/50 rounded-t-2xl p-4 border-2 border-b-0 border-purple-500/30">
        <div className="flex items-center justify-between mb-2">
          <span className="text-white font-semibold">Step {currentStep} of 5</span>
          <button onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-lg transition-all">
            <Camera className="w-4 h-4" />
            Stuck? Upload Screenshot
          </button>
          <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all" style={{ width: `${(currentStep / 5) * 100}%` }} />
        </div>
      </div>

      <motion.div key={currentStep} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
        className="bg-gradient-to-br from-purple-900/50 to-blue-900/50 rounded-b-2xl border-2 border-t-0 border-purple-500/30 p-8 backdrop-blur-sm">
        
        <div className="flex items-center gap-4 mb-6">
          <div className={`w-16 h-16 bg-${step.color}-500/20 rounded-full flex items-center justify-center`}>
            {step.icon}
          </div>
          <h3 className="text-3xl font-bold text-white">{step.title}</h3>
        </div>

        {step.content}

        {step.video && (
          <div className="mt-6 bg-black/30 border border-gray-700 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <Play className="w-5 h-5 text-blue-400" />
              <span className="font-semibold text-white">Video Tutorial</span>
            </div>
            <a href={step.video} target="_blank" rel="noopener noreferrer"
              className="flex items-center justify-center gap-3 py-3 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-all">
              <Play className="w-5 h-5" />
              Watch Tutorial
            </a>
          </div>
        )}

        {currentStep < 5 && (
          <div className="flex gap-4 mt-6">
            {currentStep > 1 && (
              <button onClick={() => setCurrentStep((currentStep - 1) as Step)}
                className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-xl transition-all">
                ← Back
              </button>
            )}
            <button onClick={() => setCurrentStep((currentStep + 1) as Step)}
              className="flex-1 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-bold rounded-xl transition-all flex items-center justify-center gap-2">
              Next Step
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        )}
      </motion.div>
    </div>
  );
}
