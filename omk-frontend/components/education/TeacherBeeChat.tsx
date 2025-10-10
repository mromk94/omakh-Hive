'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, X, Volume2, VolumeX, Lightbulb } from 'lucide-react';
import { teacherBee } from '@/lib/ai/teacherBee';

interface Message {
  id: string;
  role: 'user' | 'teacher';
  content: string;
  timestamp: Date;
}

interface TeacherBeeChatProps {
  context?: string;
  initialMessage?: string;
  onClose?: () => void;
}

export default function TeacherBeeChat({ context, initialMessage, onClose }: TeacherBeeChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initial greeting
    setMessages([{
      id: '1',
      role: 'teacher',
      content: initialMessage || `👑🐝 Hi! I'm Teacher Bee, your friendly Web3 educator!

I'm here to help you learn about:
• Setting up crypto wallets
• Understanding blockchain & DeFi
• Buying and swapping tokens
• Investing in real estate on Omakh
• Security best practices

What would you like to learn about?`,
      timestamp: new Date(),
    }]);
  }, [initialMessage]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await teacherBee.ask(userMessage.content, context);
      
      const teacherMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'teacher',
        content: response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, teacherMessage]);

      // Text-to-speech if enabled
      if (voiceEnabled && 'speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(response);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        window.speechSynthesis.speak(utterance);
      }
    } catch (error) {
      console.error('Teacher Bee error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'teacher',
        content: "Oops! I'm having trouble right now. Please try again!",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const quickActions = [
    { label: 'Download wallet', action: 'wallet-setup' },
    { label: 'Security tips', action: 'security' },
    { label: 'Buy crypto', action: 'buy-crypto' },
    { label: 'Invest in property', action: 'invest' },
  ];

  const handleQuickAction = async (action: string) => {
    const prompts: Record<string, string> = {
      'wallet-setup': 'How do I set up a crypto wallet?',
      'security': 'What security practices should I follow?',
      'buy-crypto': 'How do I buy my first cryptocurrency?',
      'invest': 'How do I invest in real estate on Omakh?',
    };

    setInput(prompts[action] || '');
    setTimeout(() => handleSend(), 100);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="w-full max-w-3xl h-[600px] bg-gradient-to-br from-stone-900 to-black border border-yellow-500/30 rounded-2xl shadow-2xl flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-yellow-500/20">
          <div className="flex items-center gap-3">
            <motion.div
              animate={{
                rotate: [0, -10, 10, -10, 0],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatDelay: 3,
              }}
              className="text-4xl"
            >
              👑🐝
            </motion.div>
            <div>
              <h2 className="text-xl font-bold text-stone-100">Teacher Bee</h2>
              <p className="text-sm text-stone-400">Your Web3 Learning Assistant</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setVoiceEnabled(!voiceEnabled)}
              className="p-2 hover:bg-yellow-500/10 rounded-lg transition-colors"
            >
              {voiceEnabled ? (
                <Volume2 className="w-5 h-5 text-yellow-500" />
              ) : (
                <VolumeX className="w-5 h-5 text-stone-400" />
              )}
            </button>

            {onClose && (
              <button
                onClick={onClose}
                className="p-2 hover:bg-yellow-500/10 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-stone-400" />
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-yellow-500 to-yellow-600 text-black'
                      : 'bg-stone-800 text-stone-100 border border-yellow-500/20'
                  }`}
                >
                  {message.role === 'teacher' && (
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-lg">👑🐝</span>
                      <span className="text-xs font-semibold text-yellow-500">Teacher Bee</span>
                    </div>
                  )}
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">
                    {message.content}
                  </p>
                  <p className={`text-xs mt-2 ${message.role === 'user' ? 'text-black/60' : 'text-stone-500'}`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="bg-stone-800 border border-yellow-500/20 rounded-2xl px-4 py-3">
                <div className="flex items-center gap-2">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="text-xl"
                  >
                    👑🐝
                  </motion.div>
                  <span className="text-sm text-stone-400">Teacher Bee is thinking...</span>
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Actions */}
        {messages.length <= 1 && (
          <div className="px-6 pb-4">
            <div className="flex items-center gap-2 mb-2">
              <Lightbulb className="w-4 h-4 text-yellow-500" />
              <span className="text-xs text-stone-400">Quick topics:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {quickActions.map((action) => (
                <button
                  key={action.action}
                  onClick={() => handleQuickAction(action.action)}
                  className="px-3 py-1.5 bg-yellow-500/10 hover:bg-yellow-500/20 border border-yellow-500/30 text-yellow-500 text-sm rounded-lg transition-colors"
                >
                  {action.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="p-6 border-t border-yellow-500/20">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask me anything about Web3..."
              className="flex-1 px-4 py-3 bg-stone-800 border border-yellow-500/30 rounded-xl text-stone-100 placeholder-stone-500 focus:outline-none focus:border-yellow-500/50 transition-colors"
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="px-6 py-3 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 disabled:from-stone-700 disabled:to-stone-700 text-black disabled:text-stone-500 rounded-xl transition-all flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
