'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
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
        // Fallback with ALL 8 languages
        const fallback = {
          en: { text: 'Hello', flag: '🇬🇧', name: 'English' },
          es: { text: 'Hola', flag: '🇪🇸', name: 'Spanish' },
          zh: { text: '你好', flag: '🇨🇳', name: 'Chinese' },
          ja: { text: 'こんにちは', flag: '🇯🇵', name: 'Japanese' },
          pcm: { text: 'How far', flag: '🇳🇬', name: 'Nigerian Pidgin' },
          fr: { text: 'Bonjour', flag: '🇫🇷', name: 'French' },
          ru: { text: 'Привет', flag: '🇷🇺', name: 'Russian' },
          ar: { text: 'مرحبا', flag: '🇸🇦', name: 'Arabic' },
        };
        setGreetings(fallback);
        setGreetingKeys(Object.keys(fallback));
        setLoading(false);
      });
  }, []);

  // Rotate greetings every 2.5 seconds
  useEffect(() => {
    if (greetingKeys.length === 0) return;
    
    const timer = setInterval(() => {
      setCurrentIndex(prev => (prev + 1) % greetingKeys.length);
    }, 2500);
    
    return () => clearInterval(timer);
  }, [greetingKeys]);

  // Show language selector after 4 seconds
  useEffect(() => {
    const timer = setTimeout(() => setShowLanguageSelector(true), 4000);
    return () => clearTimeout(timer);
  }, []);

  const handleLanguageSelect = (lang: string) => {
    setLanguage(lang);
    router.push('/chat');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360, scale: [1, 1.2, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="text-6xl"
        >
          👑
        </motion.div>
      </div>
    );
  }

  const currentGreeting = greetingKeys[currentIndex] ? greetings[greetingKeys[currentIndex]] : null;

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center p-4 overflow-hidden relative">
      {/* MASSIVE Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-20">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
            x: [0, 100, 0],
            y: [0, -100, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear",
          }}
          className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-yellow-600 to-amber-700 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            rotate: [360, 180, 0],
            x: [0, -100, 0],
            y: [0, 100, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "linear",
          }}
          className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-gradient-to-br from-yellow-500 to-yellow-700 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1, 1.4, 1],
            x: [0, 150, -150, 0],
            y: [0, -150, 150, 0],
          }}
          transition={{
            duration: 30,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-1/2 left-1/2 w-[600px] h-[600px] bg-gradient-to-br from-amber-600 to-yellow-800 rounded-full blur-3xl"
        />
      </div>

      {/* HUGE Animated Greeting */}
      <div className="z-10 text-center space-y-8">
        <AnimatePresence mode="wait">
          {currentGreeting && (
            <motion.div
              key={currentIndex}
              initial={{ opacity: 0, scale: 0.5, rotateX: -90 }}
              animate={{ opacity: 1, scale: 1, rotateX: 0 }}
              exit={{ opacity: 0, scale: 0.5, rotateX: 90 }}
              transition={{ duration: 0.7, ease: "easeOut" }}
              className="perspective-1000"
            >
              <motion.h1 
                className="text-8xl md:text-[12rem] lg:text-[15rem] font-black mb-4 leading-none"
                style={{
                  background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FFD700 100%)',
                  backgroundSize: '200% 200%',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  textShadow: '0 0 80px rgba(234,179,8,0.5), 0 0 120px rgba(245,158,11,0.8)',
                }}
                animate={{
                  backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
                  textShadow: [
                    '0 0 80px rgba(234,179,8,0.5), 0 0 120px rgba(245,158,11,0.8)',
                    '0 0 100px rgba(234,179,8,0.8), 0 0 150px rgba(245,158,11,1)',
                    '0 0 80px rgba(234,179,8,0.5), 0 0 120px rgba(245,158,11,0.8)',
                  ],
                }}
                transition={{
                  backgroundPosition: { duration: 3, repeat: Infinity, ease: "linear" },
                  textShadow: { duration: 2, repeat: Infinity, ease: "easeInOut" },
                }}
              >
                {currentGreeting.text}
              </motion.h1>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-stone-400 text-2xl md:text-3xl font-light mt-8"
        >
          Welcome to the Future of Finance
        </motion.p>
      </div>

      {/* BOLD Language Selector */}
      <AnimatePresence>
        {showLanguageSelector && (
          <motion.div
            initial={{ opacity: 0, y: 100, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.8, type: "spring" }}
            className="mt-16 z-20 w-full max-w-6xl px-4"
          >            
            {/* Small Pulsating Flags - Simple */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="flex flex-wrap justify-center gap-4"
            >
              {greetingKeys.map((key, idx) => (
                <motion.button
                  key={key}
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ 
                    opacity: 1, 
                    scale: [1, 1.1, 1],
                  }}
                  transition={{ 
                    delay: 0.1 * idx,
                    scale: {
                      duration: 2,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }
                  }}
                  whileHover={{ scale: 1.3 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => handleLanguageSelect(key)}
                  className="text-5xl transition-all"
                  style={{
                    filter: 'drop-shadow(0 0 20px rgba(234, 179, 8, 0.6))'
                  }}
                  title={greetings[key].name}
                >
                  {greetings[key].flag}
                </motion.button>
              ))}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Pulsing dots indicator */}
      {!showLanguageSelector && (
        <motion.div
          className="absolute bottom-12 left-1/2 -translate-x-1/2 flex gap-3"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-3 h-3 rounded-full bg-yellow-500/60"
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.6, 1, 0.6],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: i * 0.2,
              }}
            />
          ))}
        </motion.div>
      )}
    </div>
  );
}
