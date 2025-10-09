'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { Globe } from 'lucide-react';
import { frontendAPI } from '@/lib/api';
import { useAppStore } from '@/lib/store';

interface Greeting {
  text: string;
  flag: string;
  name: string;
}

export default function GreetingScreen() {
  const router = useRouter();
  const { setLanguage } = useAppStore();
  
  const [greetings, setGreetings] = useState<Record<string, Greeting>>({});
  const [greetingKeys, setGreetingKeys] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showLanguageSelector, setShowLanguageSelector] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch greetings from API
    frontendAPI.getGreetings()
      .then(res => {
        setGreetings(res.data.greetings);
        setGreetingKeys(Object.keys(res.data.greetings));
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load greetings:', err);
        // Fallback greetings
        const fallback = {
          en: { text: 'Hello', flag: '🇬🇧', name: 'English' },
          es: { text: 'Hola', flag: '🇪🇸', name: 'Spanish' },
          zh: { text: '你好', flag: '🇨🇳', name: 'Chinese' },
        };
        setGreetings(fallback);
        setGreetingKeys(Object.keys(fallback));
        setLoading(false);
      });
  }, []);

  // Rotate greetings every 3 seconds
  useEffect(() => {
    if (greetingKeys.length === 0) return;
    
    const timer = setInterval(() => {
      setCurrentIndex(prev => (prev + 1) % greetingKeys.length);
    }, 3000);
    
    return () => clearInterval(timer);
  }, [greetingKeys]);

  // Show language selector after 5 seconds
  useEffect(() => {
    const timer = setTimeout(() => setShowLanguageSelector(true), 5000);
    return () => clearTimeout(timer);
  }, []);

  const handleLanguageSelect = (lang: string) => {
    setLanguage(lang);
    router.push('/chat');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-4xl">✨</div>
      </div>
    );
  }

  const currentGreeting = greetingKeys[currentIndex] ? greetings[greetingKeys[currentIndex]] : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex flex-col items-center justify-center p-4 overflow-hidden relative">
      {/* Floating background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            y: [0, -30, 0],
            x: [0, 20, 0],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-20 left-10 w-32 h-32 bg-blue-200/30 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            y: [0, 40, 0],
            x: [0, -30, 0],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute bottom-20 right-10 w-40 h-40 bg-purple-200/30 rounded-full blur-3xl"
        />
      </div>

      {/* Animated Greeting */}
      <AnimatePresence mode="wait">
        {currentGreeting && (
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: -20 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="text-center z-10"
          >
            <motion.h1 
              className="text-7xl md:text-9xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-6"
              animate={{
                backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
              }}
              transition={{
                duration: 5,
                repeat: Infinity,
                ease: "linear",
              }}
              style={{
                backgroundSize: '200% 200%',
              }}
            >
              {currentGreeting.text}
            </motion.h1>
            <motion.p 
              className="text-3xl md:text-4xl text-gray-600 flex items-center justify-center gap-3"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <span className="text-5xl">{currentGreeting.flag}</span>
              <span>{currentGreeting.name}</span>
            </motion.p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Language Selector Button */}
      <AnimatePresence>
        {showLanguageSelector && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mt-20 z-10"
          >
            <motion.button
              onClick={() => setShowLanguageSelector(prev => !prev)}
              whileHover={{ scale: 1.05, y: -5 }}
              whileTap={{ scale: 0.95 }}
              className="px-10 py-5 bg-white rounded-full shadow-2xl hover:shadow-3xl transition-all flex items-center gap-4 animate-float"
            >
              <Globe className="w-8 h-8 text-blue-600" />
              <span className="text-xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Choose Your Language
              </span>
            </motion.button>
            
            {/* Language Grid */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8"
            >
              {greetingKeys.map((key) => (
                <motion.button
                  key={key}
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleLanguageSelect(key)}
                  className="p-6 bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-2xl transition-all border-2 border-transparent hover:border-purple-300"
                >
                  <div className="text-5xl mb-3">{greetings[key].flag}</div>
                  <div className="text-base font-semibold text-gray-800">{greetings[key].name}</div>
                  <div className="text-2xl font-bold text-gray-400 mt-1">{greetings[key].text}</div>
                </motion.button>
              ))}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bottom hint */}
      {!showLanguageSelector && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="absolute bottom-10 text-gray-400 text-sm"
        >
          Language selector appearing soon...
        </motion.p>
      )}
    </div>
  );
}
