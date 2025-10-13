'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X } from 'lucide-react';
import LanguageSelector from '@/components/LanguageSelector';

interface MenuItem {
  icon: string;
  label: string;
  action: string;
  url?: string;
}

interface MenuSection {
  [key: string]: MenuItem[];
}

interface FloatingMenuProps {
  onItemClick: (action: string, url?: string) => void;
  theme?: 'light' | 'dark';
}

export default function FloatingMenu({ onItemClick, theme = 'light' }: FloatingMenuProps) {
  const [isOpen, setIsOpen] = useState(false);

  const menuSections: MenuSection = {
    "🎯 EXPLORE": [
      { icon: "🏰", label: "About OMK Hive", action: "about" },
      { icon: "⚡", label: "How It Works", action: "how_it_works" },
      { icon: "💎", label: "Tokenomics", action: "tokenomics" },
      { icon: "🗺️", label: "Roadmap", action: "roadmap" },
      { icon: "👥", label: "Our Team", action: "team" }
    ],
    "💰 GET STARTED": [
      { icon: "🎯", label: "Private Sale", action: "private_sale" },
      { icon: "🧮", label: "Profit Calculator", action: "profit_calculator" },
      { icon: "✨", label: "Create Account", action: "register" },
      { icon: "🔐", label: "Login", action: "login" },
      { icon: "🛒", label: "Buy OMK", action: "buy_omk" },
      { icon: "📊", label: "View Dashboard", action: "dashboard" }
    ],
    "📊 RESOURCES": [
      { icon: "📜", label: "Whitepaper", action: "whitepaper", url: "/whitepaper.pdf" },
      { icon: "🔗", label: "API Docs", action: "api_docs" },
      { icon: "📈", label: "Analytics", action: "analytics" },
      { icon: "❓", label: "FAQ", action: "faq" }
    ],
    "🤝 CONNECT": [
      { icon: "💬", label: "Community", action: "community" },
      { icon: "🐦", label: "Twitter", action: "twitter" },
      { icon: "📧", label: "Support", action: "support" },
      { icon: "🤝", label: "Partners", action: "partners" }
    ]
  };

  const handleItemClick = (item: MenuItem) => {
    onItemClick(item.action, item.url);
    setIsOpen(false);
  };

  return (
    <>
      {/* Language Selector - Top Left */}
      <div className="fixed top-6 left-6 z-50">
        <LanguageSelector theme={theme} compact />
      </div>

      {/* Header Menu Button - Top Right */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed top-6 right-6 z-50 w-12 h-12 rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 ${
          theme === 'dark'
            ? 'bg-gradient-to-br from-yellow-500 via-yellow-600 to-yellow-700'
            : 'bg-gradient-to-br from-yellow-400 via-yellow-500 to-yellow-600'
        }`}
        style={{
          boxShadow: '0 8px 32px rgba(234, 179, 8, 0.6)',
        }}
      >
        <motion.div
          animate={{ rotate: isOpen ? 90 : 0 }}
          transition={{ duration: 0.3 }}
        >
          {isOpen ? (
            <X className="w-6 h-6 text-black" />
          ) : (
            <Menu className="w-6 h-6 text-black" />
          )}
        </motion.div>

        {/* Pulse animation when closed */}
        {!isOpen && (
          <motion.div
            className="absolute inset-0 rounded-full bg-yellow-500"
            animate={{
              scale: [1, 1.4, 1],
              opacity: [0.6, 0, 0.6],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        )}
      </motion.button>

      {/* Menu Panel */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            />

            {/* Menu Content */}
            <motion.div
              initial={{ y: -400, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: -400, opacity: 0 }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className={`fixed right-6 top-24 z-50 w-80 max-h-[70vh] overflow-y-auto rounded-3xl shadow-2xl p-6 ${
                theme === 'dark'
                  ? 'bg-black/95 border border-yellow-600/30'
                  : 'bg-stone-50/95 backdrop-blur-xl border border-yellow-500/30'
              }`}
            >
              {/* Menu Title */}
              <h2 className={`text-2xl font-black mb-6 bg-gradient-to-r from-yellow-500 via-yellow-600 to-yellow-700 bg-clip-text text-transparent`}>
                Quick Menu
              </h2>

              {/* Menu Sections */}
              <div className="space-y-6">
                {Object.entries(menuSections).map(([section, items]) => (
                  <div key={section}>
                    <h3 className={`text-sm font-bold mb-3 ${
                      theme === 'dark' ? 'text-yellow-600' : 'text-yellow-700'
                    }`}>
                      {section}
                    </h3>
                    <div className="space-y-2">
                      {items.map((item, idx) => (
                        <motion.button
                          key={idx}
                          whileHover={{ x: 5, scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => handleItemClick(item)}
                          className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-left ${
                            theme === 'dark'
                              ? 'hover:bg-yellow-900/20 text-stone-300'
                              : 'hover:bg-yellow-50 text-stone-700'
                          }`}
                        >
                          <span className="text-2xl">{item.icon}</span>
                          <span className="font-medium">{item.label}</span>
                        </motion.button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Footer */}
              <div className={`mt-6 pt-4 border-t ${
                theme === 'dark' ? 'border-yellow-900/30' : 'border-yellow-500/30'
              }`}>
                <p className={`text-xs text-center ${
                  theme === 'dark' ? 'text-yellow-700' : 'text-yellow-700'
                }`}>
                  Omakh © 2025
                </p>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
