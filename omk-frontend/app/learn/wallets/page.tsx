'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Wallet, Shield, BookOpen } from 'lucide-react';
import { useRouter } from 'next/navigation';
import TeacherBeeChat from '@/components/education/TeacherBeeChat';

export default function LearnWalletsPage() {
  const router = useRouter();
  const [showTeacherBee, setShowTeacherBee] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState<string>('');

  const learningPaths = [
    {
      icon: <Wallet className="w-8 h-8" />,
      title: 'What is a Crypto Wallet?',
      description: 'Learn the basics of crypto wallets and why you need one',
      topic: 'wallet-basics',
      time: '5 min',
    },
    {
      icon: <BookOpen className="w-8 h-8" />,
      title: 'Set Up Your First Wallet',
      description: 'Step-by-step guide to installing MetaMask or Phantom',
      topic: 'wallet-setup',
      time: '10 min',
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: 'Security Best Practices',
      description: 'Critical security tips to keep your crypto safe',
      topic: 'security',
      time: '8 min',
    },
  ];

  const handleTopicClick = (topic: string) => {
    setSelectedTopic(topic);
    setShowTeacherBee(true);
  };

  const getInitialMessage = (topic: string) => {
    const messages: Record<string, string> = {
      'wallet-basics': `👑🐝 Great! Let's learn about crypto wallets!

Think of a crypto wallet like a digital bank account, but YOU are the bank!

Here's what you need to know:

🏦 Traditional Bank:
• Bank controls your money
• Can freeze your account
• Has your personal info
• You trust them

🔐 Crypto Wallet:
• YOU control your money
• No one can freeze it
• Private and secure
• You trust yourself!

Your wallet stores:
• Cryptocurrencies (ETH, SOL, OMK)
• NFTs and digital assets
• Access to DeFi apps

Ready to set one up?`,

      'wallet-setup': `👑🐝 Awesome! Let's set up your first wallet!

I'll guide you through installing MetaMask (the most popular).

Which device are you using?
1️⃣ Desktop Computer
2️⃣ Mobile Phone

Just let me know and I'll give you exact steps!`,

      'security': `👑🐝 Security is THE most important thing in crypto!

Let's cover the critical security rules:

🔐 Your Seed Phrase:
• 12-24 words that control EVERYTHING
• NEVER share with anyone
• Write on paper, store safely
• Lose it = lose everything

⚠️ Common Scams:
• Fake support asking for seed phrase
• Phishing websites
• "Too good to be true" offers
• Impersonators

✅ Stay Safe:
• Verify all websites
• Use hardware wallet for large amounts
• Start with small amounts
• Ask questions when unsure

What would you like to know more about?`,
    };

    return messages[topic] || '';
  };

  return (
    <div className="min-h-screen bg-black text-stone-100">
      {/* Header */}
      <div className="border-b border-yellow-500/20">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <button
            onClick={() => router.push('/connect')}
            className="flex items-center gap-2 text-stone-400 hover:text-stone-200 transition-colors mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Connect
          </button>

          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <motion.div
              animate={{
                rotate: [0, -10, 10, -10, 0],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatDelay: 3,
              }}
              className="inline-block mb-4"
            >
              <span className="text-6xl">👑🐝</span>
            </motion.div>

            <h1 className="text-4xl md:text-5xl font-black mb-4">
              <span className="bg-gradient-to-r from-yellow-500 to-yellow-600 bg-clip-text text-transparent">
                Learn About Wallets
              </span>
            </h1>

            <p className="text-lg text-stone-400 max-w-2xl mx-auto">
              New to crypto? No problem! Teacher Bee will guide you through everything you need to know.
            </p>
          </motion.div>
        </div>
      </div>

      {/* Learning Paths */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {learningPaths.map((path, index) => (
            <motion.button
              key={path.topic}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => handleTopicClick(path.topic)}
              className="group bg-gradient-to-br from-stone-900 to-black p-8 rounded-2xl border border-yellow-500/20 hover:border-yellow-500/40 transition-all text-left"
            >
              <div className="w-14 h-14 bg-yellow-500/10 group-hover:bg-yellow-500/20 rounded-xl flex items-center justify-center mb-4 text-yellow-500 transition-colors">
                {path.icon}
              </div>

              <h3 className="text-xl font-bold text-stone-100 mb-2">
                {path.title}
              </h3>

              <p className="text-stone-400 mb-4">
                {path.description}
              </p>

              <div className="flex items-center justify-between">
                <span className="text-sm text-yellow-500">{path.time} read</span>
                <span className="text-yellow-500 group-hover:translate-x-1 transition-transform">
                  →
                </span>
              </div>
            </motion.button>
          ))}
        </div>

        {/* Chat with Teacher Bee CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="bg-gradient-to-r from-yellow-500/10 to-yellow-600/10 border border-yellow-500/30 rounded-2xl p-8 text-center"
        >
          <h2 className="text-2xl font-bold text-stone-100 mb-2">
            Have Specific Questions?
          </h2>
          <p className="text-stone-400 mb-6">
            Chat directly with Teacher Bee for personalized help
          </p>
          <button
            onClick={() => {
              setSelectedTopic('general');
              setShowTeacherBee(true);
            }}
            className="px-8 py-4 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-black font-bold rounded-xl transition-all"
          >
            💬 Chat with Teacher Bee
          </button>
        </motion.div>
      </div>

      {/* Teacher Bee Chat Modal */}
      {showTeacherBee && (
        <TeacherBeeChat
          context={`Learning about: ${selectedTopic}`}
          initialMessage={getInitialMessage(selectedTopic)}
          onClose={() => setShowTeacherBee(false)}
        />
      )}
    </div>
  );
}
