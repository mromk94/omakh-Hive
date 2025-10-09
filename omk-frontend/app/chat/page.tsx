'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { Send, Sparkles } from 'lucide-react';
import { frontendAPI } from '@/lib/api';
import { useAppStore } from '@/lib/store';

export default function ChatInterface() {
  const router = useRouter();
  const { language, theme, setTheme } = useAppStore();
  
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Get initial welcome message
    frontendAPI.getWelcome(language)
      .then(res => {
        addMessage('ai', res.data.message, [{
          type: 'theme_selector',
          options: [
            { id: 'light', label: '🌞 White Theme' },
            { id: 'dark', label: '🌚 Dark Theme' }
          ]
        }]);
      })
      .catch(() => {
        addMessage('ai', 'Welcome! Choose your theme:', [{
          type: 'theme_selector',
          options: [
            { id: 'light', label: '🌞 White Theme' },
            { id: 'dark', label: '🌚 Dark Theme' }
          ]
        }]);
      });
  }, [language]);

  const addMessage = (sender: 'user' | 'ai', content: string, options?: any[]) => {
    setMessages(prev => [...prev, { sender, content, options, timestamp: new Date() }]);
  };

  const handleThemeSelect = (selectedTheme: string) => {
    setTheme(selectedTheme);
    addMessage('user', `I choose ${selectedTheme} theme ✨`);
    addMessage('ai', 'Perfect! Loading your experience...');
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    addMessage('user', input);
    setInput('');
  };

  return (
    <div className={`min-h-screen transition-all duration-500 ${
      theme === 'dark' ? 'bg-gray-900' : 'bg-gradient-to-br from-blue-50 via-white to-purple-50'
    }`}>
      {/* Header */}
      <div className={`fixed top-0 left-0 right-0 z-50 backdrop-blur-lg border-b p-4 ${
        theme === 'dark' ? 'bg-gray-900/80 border-gray-700' : 'bg-white/80 border-gray-200'
      }`}>
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="text-purple-600" />
            <span className="font-bold text-lg">OMK Hive</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="max-w-4xl mx-auto pt-24 pb-32 px-4 space-y-6">
        {messages.map((msg, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${msg.sender === 'ai' ? 'justify-start' : 'justify-end'}`}
          >
            {msg.sender === 'ai' ? (
              <div className={`max-w-[85%] shadow-xl rounded-3xl rounded-tl-sm px-6 py-4 ${
                theme === 'dark' ? 'bg-gray-800 text-white' : 'bg-white'
              }`}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">🤖</span>
                  <span className="text-sm font-semibold opacity-60">Queen AI</span>
                </div>
                <div>{msg.content}</div>
                {msg.options && msg.options[0]?.type === 'theme_selector' && (
                  <div className="mt-4 space-y-3">
                    {msg.options[0].options.map((opt: any) => (
                      <button
                        key={opt.id}
                        onClick={() => handleThemeSelect(opt.id)}
                        className={`w-full text-left px-6 py-4 rounded-2xl transition-all ${
                          theme === 'dark'
                            ? 'bg-gray-700 hover:bg-gray-600'
                            : 'bg-gradient-to-r from-blue-50 to-purple-50 hover:from-blue-100 hover:to-purple-100'
                        }`}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="max-w-[85%] bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg rounded-3xl rounded-tr-sm px-6 py-4">
                {msg.content}
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Input */}
      <div className={`fixed bottom-0 left-0 right-0 backdrop-blur-lg border-t p-4 ${
        theme === 'dark' ? 'bg-gray-900/90 border-gray-700' : 'bg-white/90 border-gray-200'
      }`}>
        <div className="max-w-4xl mx-auto flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            className={`flex-1 px-6 py-4 rounded-full border-2 focus:outline-none ${
              theme === 'dark'
                ? 'bg-gray-800 border-gray-700 text-white'
                : 'bg-white border-gray-300'
            }`}
          />
          <button
            onClick={handleSend}
            className="px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full flex items-center gap-2"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
