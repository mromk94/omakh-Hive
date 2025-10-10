'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { Send, Crown, Wifi, WifiOff } from 'lucide-react';
import { frontendAPI } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import FloatingMenu from '@/components/menu/FloatingMenu';
import ROICalculator from '@/components/interactive/ROICalculator';
import InfoCard from '@/components/cards/InfoCard';
import WalletConnectCard from '@/components/cards/WalletConnectCard';
import DashboardCard from '@/components/cards/DashboardCard';
import SwapCard from '@/components/cards/SwapCard';
import PropertyCard from '@/components/cards/PropertyCard';

export default function ChatInterface() {
  const router = useRouter();
  const { language, theme, setTheme } = useAppStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [queenConnected, setQueenConnected] = useState<boolean | null>(null);
  const [teacherBeeMode, setTeacherBeeMode] = useState(false);
  const [flowState, setFlowState] = useState<any>({ type: null, data: {} });
  const hasInitialized = useRef(false);

  // Check Queen connection status
  useEffect(() => {
    const checkQueenConnection = async () => {
      try {
        const response = await fetch('http://localhost:8001/health');
        const data = await response.json();
        setQueenConnected(data.status === 'healthy');
      } catch (error) {
        console.error('❌ Queen connection check failed:', error);
        setQueenConnected(false);
      }
    };
    
    checkQueenConnection();
    // Check every 30 seconds
    const interval = setInterval(checkQueenConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Get initial welcome message ONCE - using ref to prevent double calls
    if (!hasInitialized.current) {
      hasInitialized.current = true;
      
      frontendAPI.getWelcome(language)
        .then(res => {
          addMessage('ai', res.data.message);
          // Show theme selector after 1 second
          setTimeout(() => {
            addMessage('ai', '', [{
              type: 'theme_selector',
              options: [
                { id: 'light', label: '🌞 White Theme', description: 'Clean, bright, easy on the eyes' },
                { id: 'dark', label: '🌚 Dark Theme', description: 'Sleek, modern, perfect for night' }
              ]
            }]);
          }, 1000);
        })
        .catch(() => {
          addMessage('ai', 'Hi there 👋, welcome! Before we begin, how do you prefer your world to look?');
          setTimeout(() => {
            addMessage('ai', '', [{
              type: 'theme_selector',
              options: [
                { id: 'light', label: '🌞 White Theme', description: 'Clean, bright, easy on the eyes' },
                { id: 'dark', label: '🌚 Dark Theme', description: 'Sleek, modern, perfect for night' }
              ]
            }]);
          }, 1000);
        });
    }
  }, []); // Empty dependency array - only run once

  const addMessage = (sender: 'user' | 'ai', content: string, options?: any[]) => {
    setMessages(prev => [...prev, { sender, content, options, timestamp: new Date(), id: Date.now() }]);
    scrollToBottom();
  };

  const scrollToBottom = () => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleThemeSelect = async (selectedTheme: string) => {
    setTheme(selectedTheme);
    addMessage('user', `I choose ${selectedTheme} theme ✨`);
    
    setLoading(true);
    try {
      const res = await frontendAPI.askHasAccount(selectedTheme, language);
      setTimeout(() => {
        addMessage('ai', res.data.message, res.data.options);
        setLoading(false);
      }, 800);
    } catch (err) {
      addMessage('ai', "Great choice! Let's continue... Do you have an account with us?", [
        { id: 'yes', label: '🟢 Yes, I have an account', action: 'login' },
        { id: 'no', label: '🔵 No, I\'m new here', action: 'onboard' }
      ]);
      setLoading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    
    addMessage('user', input);
    const userInput = input;
    setInput('');
    setLoading(true);

    try {
      // Handle active flows
      if (flowState.type === 'email_login') {
        return handleEmailLoginFlow(userInput);
      } else if (flowState.type === 'email_signup') {
        return handleEmailSignupFlow(userInput);
      }

      // If Teacher Bee mode is active, use Gemini AI
      if (teacherBeeMode) {
        const { teacherBee } = await import('@/lib/ai/teacherBee');
        const response = await teacherBee.ask(userInput, 'wallet-education');
        
        setTimeout(() => {
          addMessage('ai', '👑🐝 ' + response);
          setLoading(false);
        }, 800);
        return;
      }

      // Normal Queen AI flow
      const res = await frontendAPI.chat(userInput);
      setTimeout(() => {
        addMessage('ai', res.data.message, res.data.options);
        setLoading(false);
      }, 600);
    } catch (err) {
      addMessage('ai', "Oops! Something went wrong. Can you try that again? 🤔");
      setLoading(false);
    }
  };

  const handleEmailLoginFlow = async (userInput: string) => {
    const { step, email } = flowState.data;
    
    if (step === 'email') {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(userInput)) {
        setTimeout(() => {
          addMessage('ai', '❌ That doesn\'t look like a valid email. Try again? 📧');
          setLoading(false);
        }, 500);
        return;
      }
      
      setFlowState({ type: 'email_login', data: { step: 'password', email: userInput } });
      setTimeout(() => {
        addMessage('ai', '✅ Got it! Now enter your password 🔒\n\n(Demo: Use "Demo1234!" for demo@omakh.com)');
        setLoading(false);
      }, 500);
    } else if (step === 'password') {
      // Validate login
      try {
        const res = await frontendAPI.login(email, userInput);
        setFlowState({ type: null, data: {} });
        setTimeout(() => {
          addMessage('ai', `🎉 Welcome back! You\'re logged in!\n\nWhat would you like to do?`, [
            { label: '📊 View my dashboard', action: 'show_dashboard' },
            { label: '🏠 Browse properties', action: 'show_properties' },
            { label: '💰 Buy OMK tokens', action: 'show_swap' }
          ]);
          setLoading(false);
        }, 800);
      } catch (err) {
        setTimeout(() => {
          addMessage('ai', '❌ Login failed. Incorrect password or email not found.\n\nTry again?', [
            { label: '🔄 Try again', action: 'email_login' },
            { label: '📝 Sign up instead', action: 'email_signup' }
          ]);
          setFlowState({ type: null, data: {} });
          setLoading(false);
        }, 500);
      }
    }
  };

  const handleEmailSignupFlow = async (userInput: string) => {
    const { step, email, name } = flowState.data;
    
    if (step === 'email') {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(userInput)) {
        setTimeout(() => {
          addMessage('ai', '❌ Invalid email format. Try again? 📧');
          setLoading(false);
        }, 500);
        return;
      }
      
      setFlowState({ type: 'email_signup', data: { step: 'name', email: userInput } });
      setTimeout(() => {
        addMessage('ai', '✅ Perfect! What should I call you? (Your name)');
        setLoading(false);
      }, 500);
    } else if (step === 'name') {
      setFlowState({ type: 'email_signup', data: { step: 'password', email, name: userInput } });
      setTimeout(() => {
        addMessage('ai', `Nice to meet you, ${userInput}! 👋\n\nNow create a strong password 🔒\n\n(Min 8 characters, include numbers & symbols)`);
        setLoading(false);
      }, 500);
    } else if (step === 'password') {
      if (userInput.length < 8) {
        setTimeout(() => {
          addMessage('ai', '❌ Password too short. Needs at least 8 characters.');
          setLoading(false);
        }, 500);
        return;
      }
      
      // Register user
      try {
        await frontendAPI.register({ email, name, password: userInput });
        setFlowState({ type: null, data: {} });
        setTimeout(() => {
          addMessage('ai', `🎉 Account created successfully, ${name}!\n\nLet\'s get you started!`, [
            { label: '🔗 Connect my wallet', action: 'connect_wallet' },
            { label: '🏠 Browse properties', action: 'show_properties' },
            { label: '📚 Learn the basics', action: 'ask_teacher_bee' }
          ]);
          setLoading(false);
        }, 800);
      } catch (err) {
        setTimeout(() => {
          addMessage('ai', '❌ Registration failed. Email might already exist.\n\nTry logging in?', [
            { label: '🔑 Login instead', action: 'email_login' },
            { label: '🔄 Try different email', action: 'email_signup' }
          ]);
          setFlowState({ type: null, data: {} });
          setLoading(false);
        }, 500);
      }
    }
  };

  const handleOptionClick = (option: any) => {
    if (option.action === 'select_theme') {
      handleThemeSelect(option.id);
    } else if (option.action === 'login') {
      addMessage('user', 'Yes, I have an account');
      addMessage('ai', 'Great! Do you want to login with your wallet or email?', [
        { label: '🔗 Connect Wallet', action: 'connect_wallet' },
        { label: '📧 Login with Email', action: 'email_login' }
      ]);
    } else if (option.action === 'email_login') {
      addMessage('user', 'Login with Email');
      setFlowState({ type: 'email_login', data: { step: 'email' } });
      addMessage('ai', 'Please enter your email address 📧\n\n(Demo: demo@omakh.com)');
    } else if (option.action === 'onboard') {
      addMessage('user', 'No, I\'m new here');
      addMessage('ai', 'Perfect! Do you have a crypto wallet?', [
        { label: '✅ Yes, I have a wallet', action: 'connect_wallet' },
        { label: '❓ No, what\'s a wallet?', action: 'ask_teacher_bee' },
        { label: '📧 I prefer email signup', action: 'email_signup' }
      ]);
    } else if (option.action === 'show_roi_calculator') {
      addMessage('user', option.label);
      addMessage('ai', '', [{ type: 'roi_calculator' }]);
    } else if (option.action === 'show_about') {
      addMessage('user', option.label);
      addMessage('ai', '', [{ type: 'info_card', data: option.data }]);
    } else if (option.action === 'connect_wallet') {
      addMessage('user', option.label);
      addMessage('ai', 'Perfect! Let\'s connect your wallet so you can start investing! 🔗', [{ type: 'wallet_connect' }]);
    } else if (option.action === 'show_dashboard') {
      addMessage('user', option.label);
      addMessage('ai', 'Here\'s your portfolio overview! 📊', [{ type: 'dashboard' }]);
    } else if (option.action === 'show_swap') {
      addMessage('user', option.label);
      addMessage('ai', 'Great! Let\'s get you some OMK tokens! 💰', [{ type: 'token_swap' }]);
    } else if (option.action === 'show_properties') {
      addMessage('user', option.label);
      addMessage('ai', 'Here are our premium investment properties! 🏠', [{ type: 'property_browser' }]);
    } else if (option.action === 'ask_teacher_bee') {
      addMessage('user', option.label);
      setTeacherBeeMode(true);
      addMessage('ai', '👑🐝 Hi! I\'m Teacher Bee, your Web3 learning assistant!\n\nI can help you with:\n• Setting up your first wallet\n• Understanding crypto & blockchain\n• Security best practices\n• How to invest in real estate\n\nWhat would you like to learn about?');
    } else if (option.action === 'email_signup') {
      addMessage('user', option.label);
      setFlowState({ type: 'email_signup', data: { step: 'email' } });
      addMessage('ai', 'Great! Let\'s create your account. What\'s your email address? 📧');
    } else if (option.id === 'explorer' || option.id === 'investor' || option.id === 'institutional') {
      addMessage('user', option.label);
      addMessage('ai', `Awesome! Welcome ${option.id}! 🎉\n\nLet me show you around. What would you like to do first?`, [
        { label: '💰 Calculate potential returns', action: 'show_roi_calculator' },
        { label: '🏠 Browse properties', action: 'show_properties' },
        { label: '🔗 Connect my wallet', action: 'connect_wallet' },
        { label: '📚 Learn about Omakh', action: 'about' }
      ]);
    } else if (option.action === 'show_private_sale') {
      addMessage('user', option.label);
      addMessage('ai', 'Welcome to the OMK Private Sale! 🎯\n\nGet in early with exclusive benefits!', [{ type: 'private_sale' }]);
    } else if (option.action === 'start_kyc') {
      addMessage('user', option.label);
      addMessage('ai', '🔐 KYC Verification Process\n\nTo comply with regulations, we need to verify your identity.\n\nYou\'ll need:\n• Government ID (Passport/Driver\'s License)\n• Proof of address (Utility bill)\n• Selfie for verification\n\nThis usually takes 24-48 hours.\n\nReady to start?', [
        { label: '✅ Yes, start KYC', action: 'kyc_upload' },
        { label: '📖 Why is KYC needed?', action: 'show_about', data: { title: 'KYC Information', icon: '🔐' } },
        { label: '❌ Maybe later', action: 'show_dashboard' }
      ]);
    } else if (option.action === 'kyc_upload') {
      addMessage('user', option.label);
      addMessage('ai', '📤 KYC Document Upload\n\n(In production, this would open a secure upload form)\n\nFor demo purposes:\n✅ Documents uploaded\n✅ Verification in progress\n⏳ Expected completion: 24-48 hours\n\nYou\'ll receive an email notification once approved!', [
        { label: '📊 View my dashboard', action: 'show_dashboard' },
        { label: '🏠 Browse properties', action: 'show_properties' }
      ]);
    } else if (option.action === 'show_tiers') {
      addMessage('user', option.label);
      addMessage('ai', '🎯 OMK Token Sale Tiers\n\n**Tier 1** (Current)\n• Price: $0.100 per OMK\n• Bonus: 15%\n• Min: $500\n\n**Tier 2**\n• Price: $0.115 per OMK\n• Bonus: 10%\n• Min: $500\n\n**Tier 3**\n• Price: $0.130 per OMK\n• Bonus: 5%\n• Min: $300\n\n**Public Sale**\n• Price: $0.145 per OMK\n• No bonus\n• Min: $100\n\nLower tiers = Better price! 🚀', [
        { label: '💰 Join Tier 1 now', action: 'show_private_sale' },
        { label: '🔢 Calculate my allocation', action: 'show_roi_calculator' },
        { label: '📚 Learn more', action: 'show_about', data: { title: 'Tokenomics', icon: '💎' } }
      ]);
    } else {
      addMessage('user', option.label);
    }
  };

  const handleMenuClick = (action: string, url?: string) => {
    if (url) {
      window.open(url, '_blank');
      return;
    }

    switch (action) {
      case 'about':
        addMessage('ai', 'Let me tell you about Omakh - the future of real estate investing! 🏰', [{
          type: 'info_card',
          data: {
            title: 'About Omakh',
            icon: '🏰',
            content: `Omakh is democratizing access to global real estate investments through blockchain technology and tokenization.

🌍 **Our Mission**
Make premium real estate investing accessible to everyone, regardless of capital or location. No more $500K barriers - start with just $100.

💡 **What Makes Us Different**
We're not just another crypto platform. We tokenize REAL Airbnb properties across Africa and beyond, giving you fractional ownership and passive income.`,
            expandedContent: (
              <div className="space-y-6">
                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">🎯 The Vision</h4>
                  <p className="mb-4">
                    Traditional real estate investing is broken. It requires massive capital, complex paperwork, geographic limitations, and zero liquidity. 
                    We're fixing all of that with blockchain technology.
                  </p>
                  <p className="mb-4">
                    Imagine owning a piece of a luxury apartment in Lagos, a beachfront condo in Cape Town, AND a premium villa in Dubai - 
                    all from your phone, with just a few hundred dollars. That's Omakh.
                  </p>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">🚀 Why Real Estate + Blockchain?</h4>
                  <div className="space-y-3">
                    <div className="p-4 bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-xl border border-blue-500/30">
                      <strong className="text-blue-400">Stable Asset Class</strong>
                      <p className="text-sm text-gray-400 mt-1">Real estate has consistently outperformed most investments over the long term. It's tangible, real, and always in demand.</p>
                    </div>
                    <div className="p-4 bg-gradient-to-r from-yellow-900/30 to-amber-900/30 rounded-xl border border-yellow-500/30">
                      <strong className="text-yellow-400">Passive Income</strong>
                      <p className="text-sm text-gray-400 mt-1">Airbnb and short-term rentals generate consistent monthly income. You earn while you sleep.</p>
                    </div>
                    <div className="p-4 bg-gradient-to-r from-pink-900/30 to-red-900/30 rounded-xl border border-pink-500/30">
                      <strong className="text-pink-400">Blockchain Transparency</strong>
                      <p className="text-sm text-gray-400 mt-1">Every property, transaction, and earning is recorded on-chain. No hidden fees, no surprises.</p>
                    </div>
                    <div className="p-4 bg-gradient-to-r from-green-900/30 to-emerald-900/30 rounded-xl border border-green-500/30">
                      <strong className="text-green-400">Global Diversification</strong>
                      <p className="text-sm text-gray-400 mt-1">Spread risk across multiple cities and properties. One market down? Others keep earning.</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">📊 Market Opportunity</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-5 bg-gradient-to-br from-yellow-900/20 to-orange-900/20 rounded-xl border border-yellow-500/30">
                      <div className="text-3xl font-black text-yellow-400 mb-2">$200B+</div>
                      <div className="text-sm text-gray-300">Global Short-Term Rental Market</div>
                      <div className="text-xs text-gray-500 mt-1">Growing 10.4% annually</div>
                    </div>
                    <div className="p-5 bg-gradient-to-br from-purple-900/20 to-pink-900/20 rounded-xl border border-purple-500/30">
                      <div className="text-3xl font-black text-purple-400 mb-2">$16T</div>
                      <div className="text-sm text-gray-300">Tokenized Assets by 2030</div>
                      <div className="text-xs text-gray-500 mt-1">BlackRock prediction</div>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">🏆 Our Competitive Edge</h4>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-2">
                      <span className="text-green-500">✅</span>
                      <span><strong>AI-Powered Platform:</strong> Queen AI guides you through every step - no Web3 knowledge needed</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-500">✅</span>
                      <span><strong>Verified Properties:</strong> Every listing is inspected, certified, and operational before tokenization</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-500">✅</span>
                      <span><strong>Local Partnerships:</strong> We work with top property managers in each city for maximum occupancy</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-500">✅</span>
                      <span><strong>Insurance Backed:</strong> Properties are insured against damages and downtime</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-500">✅</span>
                      <span><strong>Instant Liquidity:</strong> Trade your tokens on exchanges anytime - no 30-day escrows</span>
                    </li>
                  </ul>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">👥 Who Is Omakh For?</h4>
                  <div className="space-y-3">
                    <div className="flex items-start gap-3">
                      <span className="text-3xl">🌱</span>
                      <div>
                        <strong className="text-green-400">First-Time Investors</strong>
                        <p className="text-sm text-gray-400 mt-1">Start with $100. Learn about real estate without risking your life savings.</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-3xl">💼</span>
                      <div>
                        <strong className="text-blue-400">Experienced Investors</strong>
                        <p className="text-sm text-gray-400 mt-1">Diversify globally, earn passive income, and leverage blockchain for transparency.</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-3xl">🌍</span>
                      <div>
                        <strong className="text-purple-400">Diaspora Community</strong>
                        <p className="text-sm text-gray-400 mt-1">Invest back home in Africa while living abroad. Support local economies remotely.</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-3xl">🏢</span>
                      <div>
                        <strong className="text-orange-400">Institutions</strong>
                        <p className="text-sm text-gray-400 mt-1">Access African real estate markets with compliance, liquidity, and transparency.</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-6 p-6 bg-gradient-to-br from-purple-900/30 to-pink-900/30 rounded-2xl border-2 border-purple-500/50">
                  <p className="text-lg font-semibold text-purple-300 mb-3">🎯 Our Goal for 2025</p>
                  <p className="text-gray-300 mb-3">
                    Tokenize $100M worth of premium properties across 12 African cities. Create 10,000+ fractional real estate investors. 
                    Distribute $5M+ in passive income to our community.
                  </p>
                  <p className="text-sm text-gray-400 italic">
                    "Real estate investment, reimagined for the blockchain generation." 🚀
                  </p>
                </div>
              </div>
            ),
          }
        }]);
        break;
      case 'how_it_works':
        addMessage('ai', "Let me show you how Omakh works - it's revolutionary! 🏠✨", [{
          type: 'info_card',
          data: {
            title: 'How Omakh Works',
            icon: '🏠',
            content: `Welcome to the future of real estate investment! Omakh combines two powerful markets:

🏢 **Global Short-Term Rental Market** ($200B+)
The Airbnb and vacation rental market is booming worldwide, with travelers seeking authentic, home-like accommodations.

💎 **Tokenized Real-World Assets** ($16T by 2030)
Blockchain technology now allows you to own fractional pieces of premium real estate across the globe.`,
            expandedContent: (
              <div className="space-y-6">
                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">🌍 Own Pieces of the World</h4>
                  <p className="mb-4">
                    Instead of saving $500,000 to buy one apartment, invest just $100-$5,000 to own fractional shares of multiple premium properties across global cities. Your investment is tokenized, giving you real ownership on the blockchain.
                  </p>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">🏙️ Premium Locations, Real Returns</h4>
                  <p className="mb-3">We focus on high-demand tourist and business destinations:</p>
                  <ul className="space-y-2 ml-4">
                    <li className="flex items-start gap-2">
                      <span className="text-yellow-500 font-bold">•</span>
                      <span><strong>Lagos, Nigeria</strong> - 12.5% APY - Financial hub with growing tourism</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-yellow-500 font-bold">•</span>
                      <span><strong>Abuja, Nigeria</strong> - 10.8% APY - Political capital with stable diplomatic demand</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-yellow-500 font-bold">•</span>
                      <span><strong>Cape Town, South Africa</strong> - 9.7% APY - Premier tourist destination</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-yellow-500 font-bold">•</span>
                      <span><strong>Nairobi, Kenya</strong> - 11.2% APY - East Africa's tech hub</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-yellow-500 font-bold">•</span>
                      <span><strong>Accra, Ghana</strong> - 11.3% APY - Growing international business travel</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-yellow-500 font-bold">•</span>
                      <span><strong>Dubai, UAE</strong> - Coming Soon - Luxury tourism hotspot</span>
                    </li>
                  </ul>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">💰 How You Earn Money</h4>
                  <ol className="space-y-3 ml-4">
                    <li>
                      <strong className="text-green-400">1. Property Rental Income</strong>
                      <p className="text-gray-400 mt-1">Properties are listed on Airbnb, Booking.com, and other platforms. When guests book and stay, you earn your share of the rental income.</p>
                    </li>
                    <li>
                      <strong className="text-green-400">2. Token Staking Rewards</strong>
                      <p className="text-gray-400 mt-1">Your OMK tokens earn 5-10% APY just for holding them in the platform.</p>
                    </li>
                    <li>
                      <strong className="text-green-400">3. Property Appreciation</strong>
                      <p className="text-gray-400 mt-1">As property values increase over time, your fractional ownership becomes more valuable.</p>
                    </li>
                  </ol>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">🔄 Simple 4-Step Process</h4>
                  <div className="space-y-3">
                    <div className="p-4 bg-gradient-to-r from-yellow-900/30 to-amber-900/30 rounded-xl border border-yellow-500/30">
                      <strong>Step 1: Create Account</strong>
                      <p className="text-sm text-gray-400 mt-1">Sign up with email or connect your Web3 wallet</p>
                    </div>
                    <div className="p-4 bg-gradient-to-r from-yellow-900/30 to-amber-900/30 rounded-xl border border-yellow-500/30">
                      <strong>Step 2: Buy OMK Tokens</strong>
                      <p className="text-sm text-gray-400 mt-1">1 OMK = 1 USDT - Purchase through our platform or supported exchanges</p>
                    </div>
                    <div className="p-4 bg-gradient-to-r from-yellow-900/30 to-amber-900/30 rounded-xl border border-yellow-500/30">
                      <strong>Step 3: Select Investment Blocks</strong>
                      <p className="text-sm text-gray-400 mt-1">Browse properties, compare APYs, choose your investment blocks (starting from $100)</p>
                    </div>
                    <div className="p-4 bg-gradient-to-r from-yellow-900/30 to-amber-900/30 rounded-xl border border-yellow-500/30">
                      <strong>Step 4: Earn Passive Income</strong>
                      <p className="text-sm text-gray-400 mt-1">Receive monthly distributions directly to your wallet. Track everything in your dashboard.</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">🛡️ Why It's Safe</h4>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-2">
                      <span className="text-green-500">✅</span>
                      <span><strong>Real Assets:</strong> Every token is backed by real, verified properties</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-500">✅</span>
                      <span><strong>Blockchain Security:</strong> Ownership recorded immutably on the blockchain</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-500">✅</span>
                      <span><strong>Professional Management:</strong> Properties managed by experienced local teams</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-500">✅</span>
                      <span><strong>Liquidity:</strong> Trade your tokens anytime on supported exchanges</span>
                    </li>
                  </ul>
                </div>

                <div className="mt-6 p-6 bg-gradient-to-br from-yellow-900/20 to-orange-900/20 rounded-2xl border border-yellow-500/30">
                  <p className="text-lg font-semibold text-yellow-400 mb-2">💡 The Big Picture</p>
                  <p className="text-gray-300">
                    Traditional real estate investing requires huge capital, complex paperwork, and is illiquid. 
                    Omakh democratizes this by letting anyone invest small amounts in premium global properties, 
                    earn passive income from Airbnb rentals, and exit anytime by selling their tokens. 
                    It's real estate investing for the 21st century! 🚀
                  </p>
                </div>
              </div>
            ),
          }
        }]);
        break;
      case 'tokenomics':
        addMessage('ai', 'Let me break down the OMK token economics! 💎', [{
          type: 'info_card',
          data: {
            title: 'OMK Tokenomics',
            icon: '💎',
            content: `The OMK token is the heart of our ecosystem - it's your key to fractional real estate ownership and passive income.

💰 **Token Value**
1 OMK = 1 USDT (Initial listing price: $0.10 USDT)

🎯 **Utility**
Purchase investment blocks, stake for rewards, vote on governance, and trade on exchanges.`,
            expandedContent: (
              <div className="space-y-6">
                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">📊 Token Distribution</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 bg-blue-900/20 rounded-lg border border-blue-500/30">
                      <div>
                        <strong className="text-blue-400">Public Sale</strong>
                        <p className="text-xs text-gray-500">Available to everyone</p>
                      </div>
                      <span className="text-2xl font-black text-blue-300">40%</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-green-900/20 rounded-lg border border-green-500/30">
                      <div>
                        <strong className="text-green-400">Liquidity Pool</strong>
                        <p className="text-xs text-gray-500">DEX trading pairs</p>
                      </div>
                      <span className="text-2xl font-black text-green-300">20%</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-purple-900/20 rounded-lg border border-purple-500/30">
                      <div>
                        <strong className="text-purple-400">Team & Advisors</strong>
                        <p className="text-xs text-gray-500">4-year vesting</p>
                      </div>
                      <span className="text-2xl font-black text-purple-300">15%</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-orange-900/20 rounded-lg border border-orange-500/30">
                      <div>
                        <strong className="text-orange-400">Development Fund</strong>
                        <p className="text-xs text-gray-500">Platform improvements</p>
                      </div>
                      <span className="text-2xl font-black text-orange-300">10%</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-pink-900/20 rounded-lg border border-pink-500/30">
                      <div>
                        <strong className="text-pink-400">Marketing & Growth</strong>
                        <p className="text-xs text-gray-500">User acquisition</p>
                      </div>
                      <span className="text-2xl font-black text-pink-300">10%</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-yellow-900/20 rounded-lg border border-yellow-500/30">
                      <div>
                        <strong className="text-yellow-400">Community Rewards</strong>
                        <p className="text-xs text-gray-500">Staking, referrals, airdrops</p>
                      </div>
                      <span className="text-2xl font-black text-yellow-300">5%</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">💰 How to Earn with OMK</h4>
                  <div className="space-y-4">
                    <div className="p-4 bg-gradient-to-r from-green-900/30 to-emerald-900/30 rounded-xl border border-green-500/30">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-3xl">1️⃣</span>
                        <strong className="text-green-400 text-lg">Property Rental Income (8-12% APY)</strong>
                      </div>
                      <p className="text-sm text-gray-400 ml-12">
                        When you invest in property blocks, you receive monthly distributions from Airbnb bookings. 
                        The more slots you own, the more you earn.
                      </p>
                    </div>

                    <div className="p-4 bg-gradient-to-r from-purple-900/30 to-pink-900/30 rounded-xl border border-purple-500/30">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-3xl">2️⃣</span>
                        <strong className="text-purple-400 text-lg">Token Staking (5-10% APY)</strong>
                      </div>
                      <p className="text-sm text-gray-400 ml-12">
                        Lock your OMK tokens in our staking pool to earn additional rewards. The longer you stake, 
                        the higher your APY (30 days: 5% | 90 days: 7% | 180 days: 10%).
                      </p>
                    </div>

                    <div className="p-4 bg-gradient-to-r from-blue-900/30 to-cyan-900/30 rounded-xl border border-blue-500/30">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-3xl">3️⃣</span>
                        <strong className="text-blue-400 text-lg">Property Appreciation</strong>
                      </div>
                      <p className="text-sm text-gray-400 ml-12">
                        As property values increase over time (typical 3-5% annually), your fractional ownership 
                        becomes more valuable. Sell anytime on exchanges.
                      </p>
                    </div>

                    <div className="p-4 bg-gradient-to-r from-yellow-900/30 to-orange-900/30 rounded-xl border border-yellow-500/30">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-3xl">4️⃣</span>
                        <strong className="text-yellow-400 text-lg">Referral Bonuses (2% Commission)</strong>
                      </div>
                      <p className="text-sm text-gray-400 ml-12">
                        Invite friends and earn 2% of their investments forever. Build passive income through 
                        your network.
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">🔥 Token Burn Mechanism</h4>
                  <p className="mb-3 text-gray-300">
                    To ensure long-term value, we burn OMK tokens quarterly based on platform revenue:
                  </p>
                  <ul className="space-y-2 ml-4">
                    <li className="flex items-start gap-2">
                      <span className="text-orange-500">🔥</span>
                      <span><strong>5% of platform fees</strong> burned every quarter</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-orange-500">🔥</span>
                      <span><strong>1% of all property sales</strong> burned automatically</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-orange-500">🔥</span>
                      <span><strong>Target:</strong> Reduce supply by 50% over 10 years</span>
                    </li>
                  </ul>
                  <div className="mt-3 p-3 bg-orange-900/20 rounded-lg border border-orange-500/30">
                    <p className="text-sm text-gray-400">
                      💡 <strong>Why burns matter:</strong> As supply decreases and demand grows, token value increases. 
                      This benefits all long-term holders.
                    </p>
                  </div>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">🛡️ Security & Compliance</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="p-4 bg-green-900/20 rounded-xl border border-green-500/30">
                      <div className="text-green-400 font-bold mb-1">✅ Audited Smart Contracts</div>
                      <p className="text-xs text-gray-400">CertiK security audit passed</p>
                    </div>
                    <div className="p-4 bg-blue-900/20 rounded-xl border border-blue-500/30">
                      <div className="text-blue-400 font-bold mb-1">✅ Multi-Sig Wallet</div>
                      <p className="text-xs text-gray-400">Team funds require 3/5 signatures</p>
                    </div>
                    <div className="p-4 bg-purple-900/20 rounded-xl border border-purple-500/30">
                      <div className="text-purple-400 font-bold mb-1">✅ KYC/AML Compliant</div>
                      <p className="text-xs text-gray-400">Full regulatory compliance</p>
                    </div>
                    <div className="p-4 bg-pink-900/20 rounded-xl border border-pink-500/30">
                      <div className="text-pink-400 font-bold mb-1">✅ Insurance Fund</div>
                      <p className="text-xs text-gray-400">5% reserve for emergencies</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 p-6 bg-gradient-to-br from-purple-900/30 to-pink-900/30 rounded-2xl border-2 border-purple-500/50">
                  <p className="text-lg font-semibold text-purple-300 mb-3">🎯 Why OMK Will Appreciate</p>
                  <ul className="space-y-2 text-sm text-gray-300">
                    <li>📈 <strong>Limited Supply:</strong> Quarterly burns reduce circulation</li>
                    <li>🏠 <strong>Real Asset Backing:</strong> Every token backed by tangible real estate</li>
                    <li>💰 <strong>Growing Demand:</strong> More properties = more investors = higher demand</li>
                    <li>🌍 <strong>Network Effects:</strong> As platform grows, token utility increases</li>
                    <li>🔒 <strong>Staking Locks Supply:</strong> Less circulating supply = price appreciation</li>
                  </ul>
                </div>
              </div>
            ),
          }
        }]);
        break;
      case 'profit_calculator':
        addMessage('ai', 'Calculate your potential returns! 💰', [{
          type: 'roi_calculator'
        }]);
        break;
      case 'register':
        addMessage('ai', "Let's create your account! ✨ First, what's your email?");
        break;
      case 'login':
        addMessage('ai', 'Welcome back! 🔐 What\'s your email?');
        break;
      case 'dashboard':
        addMessage('ai', 'Here\'s your portfolio dashboard! 📊', [{ type: 'dashboard' }]);
        break;
      case 'buy_omk':
        addMessage('ai', 'Let\'s get you some OMK tokens! 💰', [{ type: 'token_swap' }]);
        break;
      case 'private_sale':
        addMessage('ai', 'Welcome to the OMK Private Sale! 🎯\n\nGet in early with exclusive benefits!', [{ type: 'private_sale' }]);
        break;
      case 'roadmap':
        addMessage('ai', 'Here\'s our journey to becoming the #1 tokenized real estate platform! 🗺️', [{
          type: 'info_card',
          data: {
            title: 'Omakh Roadmap',
            icon: '🗺️',
            content: `We're moving fast and shipping features that matter. Here's what we've achieved and what's coming next.

✅ **Q4 2024 - Foundation** (COMPLETED)
Platform architecture, smart contracts, and first property partnerships established.

🚀 **Q1 2025 - Launch** (IN PROGRESS)
Public launch, first investment blocks live, community building.`,
            expandedContent: (
              <div className="space-y-6">
                <div>
                  <h4 className="text-xl font-bold mb-4 text-green-400">✅ Q4 2024 - Foundation (COMPLETED)</h4>
                  <div className="space-y-3 ml-4">
                    <div className="flex items-start gap-3">
                      <span className="text-green-500 text-xl">✓</span>
                      <div>
                        <strong className="text-green-300">Smart Contract Development</strong>
                        <p className="text-sm text-gray-400">ERC-20 token, property NFTs, staking contracts</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-green-500 text-xl">✓</span>
                      <div>
                        <strong className="text-green-300">Security Audit</strong>
                        <p className="text-sm text-gray-400">CertiK audit passed with zero critical issues</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-green-500 text-xl">✓</span>
                      <div>
                        <strong className="text-green-300">Property Partnerships</strong>
                        <p className="text-sm text-gray-400">Secured 15 premium properties across 5 African cities</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-green-500 text-xl">✓</span>
                      <div>
                        <strong className="text-green-300">Platform Beta</strong>
                        <p className="text-sm text-gray-400">Closed beta with 500 early adopters</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-xl border-2 border-blue-500/50">
                  <h4 className="text-xl font-bold mb-4 text-blue-400">🚀 Q1 2025 - Public Launch (IN PROGRESS)</h4>
                  <div className="space-y-3 ml-4">
                    <div className="flex items-start gap-3">
                      <span className="text-blue-500 text-xl">⚡</span>
                      <div>
                        <strong className="text-blue-300">Token Generation Event (TGE)</strong>
                        <p className="text-sm text-gray-400">OMK token listed on major DEXs (Uniswap, PancakeSwap)</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-blue-500 text-xl">⚡</span>
                      <div>
                        <strong className="text-blue-300">First Investment Blocks Live</strong>
                        <p className="text-sm text-gray-400">Lagos, Abuja, Cape Town properties available</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-blue-500 text-xl">⚡</span>
                      <div>
                        <strong className="text-blue-300">Mobile App Launch</strong>
                        <p className="text-sm text-gray-400">iOS & Android apps with wallet integration</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-blue-500 text-xl">⚡</span>
                      <div>
                        <strong className="text-blue-300">AI Chat Integration</strong>
                        <p className="text-sm text-gray-400">Queen AI guides users through every step</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-4 text-purple-400">🎯 Q2 2025 - Expansion</h4>
                  <div className="space-y-3 ml-4">
                    <div className="flex items-start gap-3">
                      <span className="text-purple-500 text-xl">📅</span>
                      <div>
                        <strong className="text-purple-300">10 New Cities</strong>
                        <p className="text-sm text-gray-400">Nairobi, Accra, Johannesburg, Kigali, Addis Ababa, + 5 more</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-purple-500 text-xl">📅</span>
                      <div>
                        <strong className="text-purple-300">50+ Properties</strong>
                        <p className="text-sm text-gray-400">Diversified portfolio worth $50M+</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-purple-500 text-xl">📅</span>
                      <div>
                        <strong className="text-purple-300">CEX Listings</strong>
                        <p className="text-sm text-gray-400">Major exchanges (Binance, Coinbase, KuCoin)</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-purple-500 text-xl">📅</span>
                      <div>
                        <strong className="text-purple-300">Governance Launch</strong>
                        <p className="text-sm text-gray-400">Token holders vote on new properties</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-4 text-pink-400">🌟 Q3-Q4 2025 - Global Domination</h4>
                  <div className="space-y-3 ml-4">
                    <div className="flex items-start gap-3">
                      <span className="text-pink-500 text-xl">🔮</span>
                      <div>
                        <strong className="text-pink-300">Dubai Properties</strong>
                        <p className="text-sm text-gray-400">Luxury market expansion into UAE</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-pink-500 text-xl">🔮</span>
                      <div>
                        <strong className="text-pink-300">100+ Properties</strong>
                        <p className="text-sm text-gray-400">$100M+ in tokenized real estate</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-pink-500 text-xl">🔮</span>
                      <div>
                        <strong className="text-pink-300">Secondary Market</strong>
                        <p className="text-sm text-gray-400">P2P trading of property NFTs</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-pink-500 text-xl">🔮</span>
                      <div>
                        <strong className="text-pink-300">Institutional Partnerships</strong>
                        <p className="text-sm text-gray-400">Banks, hedge funds, family offices</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-pink-500 text-xl">🔮</span>
                      <div>
                        <strong className="text-pink-300">10,000+ Investors</strong>
                        <p className="text-sm text-gray-400">Community milestone with $5M+ distributed</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-4 text-orange-400">🚀 2026 & Beyond - The Future</h4>
                  <div className="space-y-3 ml-4">
                    <div className="flex items-start gap-3">
                      <span className="text-orange-500 text-xl">🌍</span>
                      <div>
                        <strong className="text-orange-300">Global Expansion</strong>
                        <p className="text-sm text-gray-400">Asia, Europe, Latin America markets</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-orange-500 text-xl">🏢</span>
                      <div>
                        <strong className="text-orange-300">Commercial Real Estate</strong>
                        <p className="text-sm text-gray-400">Office buildings, retail spaces, warehouses</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-orange-500 text-xl">🤖</span>
                      <div>
                        <strong className="text-orange-300">AI Property Management</strong>
                        <p className="text-sm text-gray-400">Automated pricing, maintenance, guest communication</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-orange-500 text-xl">💳</span>
                      <div>
                        <strong className="text-orange-300">Omakh Card</strong>
                        <p className="text-sm text-gray-400">Crypto debit card to spend rental income</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-6 p-6 bg-gradient-to-br from-yellow-900/20 to-orange-900/20 rounded-2xl border-2 border-yellow-500/50">
                  <p className="text-lg font-semibold text-yellow-400 mb-3">💡 Join Us on This Journey</p>
                  <p className="text-gray-300">
                    We're not just building a platform - we're creating a movement to democratize real estate investing globally. 
                    Early investors will benefit from the best properties, highest APYs, and exclusive perks. The future of 
                    real estate is tokenized, and it starts with Omakh. 🚀
                  </p>
                </div>
              </div>
            ),
          }
        }]);
        break;
      case 'team':
        addMessage('ai', 'Meet the minds behind Omakh! 👥', [{
          type: 'info_card',
          data: {
            title: 'Our Team',
            icon: '👥',
            content: `We're a diverse team of blockchain engineers, real estate experts, and AI specialists united by one vision: making premium real estate accessible to everyone.

🌍 **Global Presence**
Team members across Africa, Europe, and North America working 24/7.

💪 **Combined Experience**
50+ years in real estate, 30+ years in blockchain, 20+ years in AI/ML.`,
            expandedContent: (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-5 bg-gradient-to-br from-blue-900/30 to-purple-900/30 rounded-xl border border-blue-500/30">
                    <div className="text-4xl mb-3">👨‍💼</div>
                    <h4 className="text-lg font-bold text-blue-300 mb-1">Founder & CEO</h4>
                    <p className="text-sm text-gray-400 mb-3">15 years in real estate investment, ex-Goldman Sachs</p>
                    <p className="text-xs text-gray-500">Led $500M+ in property transactions across Africa</p>
                  </div>

                  <div className="p-5 bg-gradient-to-br from-purple-900/30 to-pink-900/30 rounded-xl border border-purple-500/30">
                    <div className="text-4xl mb-3">👨‍💻</div>
                    <h4 className="text-lg font-bold text-purple-300 mb-1">CTO & Co-Founder</h4>
                    <p className="text-sm text-gray-400 mb-3">Blockchain architect, ex-Ethereum Foundation</p>
                    <p className="text-xs text-gray-500">Built smart contracts securing $2B+ in assets</p>
                  </div>

                  <div className="p-5 bg-gradient-to-br from-green-900/30 to-emerald-900/30 rounded-xl border border-green-500/30">
                    <div className="text-4xl mb-3">👩‍💼</div>
                    <h4 className="text-lg font-bold text-green-300 mb-1">Head of Operations</h4>
                    <p className="text-sm text-gray-400 mb-3">Property management expert, 10+ years Airbnb</p>
                    <p className="text-xs text-gray-500">Managed 200+ short-term rental properties</p>
                  </div>

                  <div className="p-5 bg-gradient-to-br from-orange-900/30 to-yellow-900/30 rounded-xl border border-orange-500/30">
                    <div className="text-4xl mb-3">🤖</div>
                    <h4 className="text-lg font-bold text-orange-300 mb-1">Head of AI</h4>
                    <p className="text-sm text-gray-400 mb-3">ML engineer, ex-OpenAI research team</p>
                    <p className="text-xs text-gray-500">Built Queen AI conversational platform</p>
                  </div>
                </div>

                <div>
                  <h4 className="text-xl font-bold mb-3 text-purple-400">🏆 Advisory Board</h4>
                  <div className="space-y-3">
                    <div className="p-4 bg-gray-900/50 rounded-xl border border-gray-700">
                      <strong className="text-purple-300">Real Estate Advisor</strong>
                      <p className="text-sm text-gray-400 mt-1">Former VP of Africa Operations at Marriott International</p>
                    </div>
                    <div className="p-4 bg-gray-900/50 rounded-xl border border-gray-700">
                      <strong className="text-blue-300">Blockchain Advisor</strong>
                      <p className="text-sm text-gray-400 mt-1">Core contributor to Polygon and Chainlink ecosystems</p>
                    </div>
                    <div className="p-4 bg-gray-900/50 rounded-xl border border-gray-700">
                      <strong className="text-green-300">Legal Advisor</strong>
                      <p className="text-sm text-gray-400 mt-1">Securities lawyer specializing in tokenized assets</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 p-6 bg-gradient-to-br from-purple-900/30 to-pink-900/30 rounded-2xl border-2 border-purple-500/50">
                  <p className="text-lg font-semibold text-purple-300 mb-3">🚀 Join Our Team</p>
                  <p className="text-gray-300 mb-3">
                    We're always looking for talented individuals who share our vision. If you're passionate about 
                    real estate, blockchain, or AI, we'd love to hear from you!
                  </p>
                  <p className="text-sm text-gray-400">
                    📧 careers@omakh.io
                  </p>
                </div>
              </div>
            ),
          }
        }]);
        break;
      case 'faq':
        addMessage('ai', 'Here are answers to common questions! ❓', [{
          type: 'info_card',
          data: {
            title: 'Frequently Asked Questions',
            icon: '❓',
            content: `Got questions? We've got answers! Here are the most common questions from our community.

🤔 **Quick Answers**
Everything you need to know about investing, earning, and withdrawing.`,
            expandedContent: (
              <div className="space-y-5">
                <div className="p-4 bg-blue-900/20 rounded-xl border border-blue-500/30">
                  <h4 className="text-lg font-bold text-blue-400 mb-2">What is Omakh?</h4>
                  <p className="text-sm text-gray-300">
                    Omakh is a platform that tokenizes premium Airbnb properties across Africa and beyond, allowing 
                    anyone to invest in fractional real estate with as little as $100. You earn passive income from 
                    rental bookings.
                  </p>
                </div>

                <div className="p-4 bg-purple-900/20 rounded-xl border border-purple-500/30">
                  <h4 className="text-lg font-bold text-purple-400 mb-2">How do I start investing?</h4>
                  <p className="text-sm text-gray-300 mb-2">
                    1. Create an account (2 minutes)<br/>
                    2. Buy OMK tokens (1 OMK = $0.10 USDT)<br/>
                    3. Browse investment blocks<br/>
                    4. Select properties you like<br/>
                    5. Start earning monthly income!
                  </p>
                </div>

                <div className="p-4 bg-green-900/20 rounded-xl border border-green-500/30">
                  <h4 className="text-lg font-bold text-green-400 mb-2">What's the minimum investment?</h4>
                  <p className="text-sm text-gray-300">
                    Just $100! Each property block costs between $100-$5,000 depending on the location and property type.
                  </p>
                </div>

                <div className="p-4 bg-orange-900/20 rounded-xl border border-orange-500/30">
                  <h4 className="text-lg font-bold text-orange-400 mb-2">How much can I earn?</h4>
                  <p className="text-sm text-gray-300">
                    Returns vary by city and property. Typical range is 8-12% APY from rental income, plus 5-10% APY 
                    from token staking, plus property appreciation. Total potential: 15-25% annual returns.
                  </p>
                </div>

                <div className="p-4 bg-pink-900/20 rounded-xl border border-pink-500/30">
                  <h4 className="text-lg font-bold text-pink-400 mb-2">When do I get paid?</h4>
                  <p className="text-sm text-gray-300">
                    Rental income is distributed monthly directly to your wallet (around the 5th of each month). 
                    Staking rewards accrue daily and can be claimed anytime.
                  </p>
                </div>

                <div className="p-4 bg-yellow-900/20 rounded-xl border border-yellow-500/30">
                  <h4 className="text-lg font-bold text-yellow-400 mb-2">Can I withdraw anytime?</h4>
                  <p className="text-sm text-gray-300">
                    Yes! Your OMK tokens are liquid and tradable on major exchanges 24/7. Unstaking has a small 
                    cooldown period (7-14 days depending on your plan).
                  </p>
                </div>

                <div className="p-4 bg-red-900/20 rounded-xl border border-red-500/30">
                  <h4 className="text-lg font-bold text-red-400 mb-2">What are the risks?</h4>
                  <p className="text-sm text-gray-300">
                    Like any investment, there are risks: property vacancy, market downturns, regulatory changes. 
                    However, we mitigate these through diversification, insurance, professional management, and 
                    carefully selected properties.
                  </p>
                </div>

                <div className="p-4 bg-cyan-900/20 rounded-xl border border-cyan-500/30">
                  <h4 className="text-lg font-bold text-cyan-400 mb-2">Is it legal?</h4>
                  <p className="text-sm text-gray-300">
                    Yes! We're fully compliant with securities regulations in all jurisdictions we operate. All users 
                    must complete KYC verification. Our legal team ensures we meet all regulatory requirements.
                  </p>
                </div>

                <div className="p-4 bg-indigo-900/20 rounded-xl border border-indigo-500/30">
                  <h4 className="text-lg font-bold text-indigo-400 mb-2">Do I need crypto knowledge?</h4>
                  <p className="text-sm text-gray-300">
                    Nope! Queen AI guides you through everything. We handle the complex blockchain stuff. You just 
                    pick properties and watch your money grow. Simple as that! 🚀
                  </p>
                </div>

                <div className="mt-6 p-6 bg-gradient-to-br from-purple-900/30 to-pink-900/30 rounded-2xl border-2 border-purple-500/50">
                  <p className="text-lg font-semibold text-purple-300 mb-3">💬 Still Have Questions?</p>
                  <p className="text-gray-300">
                    Just ask me anything! I'm Queen AI, and I'm here 24/7 to help you understand Omakh and start your 
                    real estate investment journey. Type your question below! 👇
                  </p>
                </div>
              </div>
            ),
          }
        }]);
        break;
      default:
        addMessage('ai', `You selected: ${action}. This feature is coming soon! 🚀`);
    }
  };

  return (
    <div className={`min-h-screen transition-all duration-500 relative ${
      theme === 'dark' 
        ? 'bg-black' 
        : 'bg-gradient-to-br from-stone-100 via-stone-50 to-amber-50'
    }`}>
      {/* Animated Background */}
      <div className={`absolute inset-0 overflow-hidden pointer-events-none ${theme === 'dark' ? 'opacity-10' : 'opacity-30'}`}>
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            x: [0, 50, 0],
            y: [0, -50, 0],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className={`absolute top-0 right-0 w-96 h-96 rounded-full blur-3xl ${
            theme === 'dark' ? 'bg-yellow-900/20' : 'bg-yellow-200/40'
          }`}
        />
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            x: [0, -50, 0],
            y: [0, 50, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className={`absolute bottom-0 left-0 w-96 h-96 rounded-full blur-3xl ${
            theme === 'dark' ? 'bg-yellow-800/20' : 'bg-amber-200/40'
          }`}
        />
      </div>

      {/* Header */}
      <motion.div 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className={`fixed top-0 left-0 right-0 z-50 backdrop-blur-xl border-b ${
          theme === 'dark' ? 'bg-black/95 border-yellow-900/30' : 'bg-stone-50/80 border-yellow-600/30'
        }`}
      >
        <div className="max-w-5xl mx-auto px-6 py-4">
          {/* Logo and Price */}
          <div className="flex flex-col items-center gap-2 relative">
            {/* Connection Status Indicator */}
            <div className="absolute -left-2 top-0 flex items-center gap-1">
              {queenConnected === null ? (
                <div className={`w-2 h-2 rounded-full animate-pulse ${theme === 'dark' ? 'bg-gray-600' : 'bg-gray-400'}`} />
              ) : queenConnected ? (
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="w-2 h-2 rounded-full bg-green-500"
                  title="Queen AI Connected"
                />
              ) : (
                <div className="w-2 h-2 rounded-full bg-red-500" title="Queen AI Offline" />
              )}
            </div>
            
            <div className="flex items-center gap-3">
              {teacherBeeMode ? (
                <motion.div
                  animate={{
                    rotate: [0, -10, 10, -10, 0],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    repeatDelay: 3,
                  }}
                  className="text-3xl"
                  style={{
                    filter: 'drop-shadow(0 0 8px rgba(234, 179, 8, 0.6))'
                  }}
                >
                  👑🐝
                </motion.div>
              ) : (
                <motion.div
                  animate={{
                    rotate: [0, -10, 10, -10, 0],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    repeatDelay: 3,
                  }}
                >
                  <Crown className="w-7 h-7 text-yellow-500" style={{
                    filter: 'drop-shadow(0 0 8px rgba(234, 179, 8, 0.6))'
                  }} />
                </motion.div>
              )}
              <span className="font-black text-xl bg-gradient-to-r from-yellow-500 via-yellow-600 to-yellow-700 bg-clip-text text-transparent">
                {teacherBeeMode ? 'Teacher Bee' : 'OMK Queen'}
              </span>
              {queenConnected && (
                <span className={`text-[10px] px-2 py-0.5 rounded-full ${
                  theme === 'dark' ? 'bg-green-900/30 text-green-400' : 'bg-green-100 text-green-700'
                }`}>
                  LIVE
                </span>
              )}
            </div>
            {/* Price Display - Smaller and Under */}
            <div className="flex items-center gap-2 text-xs">
              <span className={theme === 'dark' ? 'text-stone-500' : 'text-stone-600'}>1</span>
              <motion.span 
                className="font-bold text-sm"
                style={{
                  background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FFD700 100%)',
                  backgroundSize: '200% 200%',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }}
                animate={{
                  backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "linear",
                }}
              >
                OMK
              </motion.span>
              <span className={theme === 'dark' ? 'text-stone-500' : 'text-stone-600'}>=</span>
              <span className={theme === 'dark' ? 'text-yellow-600' : 'text-yellow-700'}>0.1 USDT</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Messages Container */}
      <div className="relative z-10 max-w-5xl mx-auto pt-28 pb-48 px-6">
        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 30, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.4, type: "spring" }}
              className={`flex mb-6 ${msg.sender === 'ai' ? 'justify-start' : 'justify-end'}`}
            >
              {msg.sender === 'ai' ? (
                <div className={`max-w-[90%] shadow-2xl rounded-3xl rounded-tl-sm p-6 ${
                  theme === 'dark' 
                    ? 'bg-black/95 backdrop-blur-xl text-stone-100 border border-yellow-900/30' 
                    : 'bg-stone-50/90 backdrop-blur-xl border border-yellow-600/30'
                }`}>
                  <div className="flex items-center gap-3 mb-3">
                    <Crown className={`w-6 h-6 ${theme === 'dark' ? 'text-yellow-400' : 'text-yellow-600'}`} />
                    <span className={`text-sm font-bold ${
                      theme === 'dark' ? 'text-white' : 'text-gray-900'
                    }`}>OMK Queen</span>
                  </div>
                  
                  {msg.content && (
                    <div className="text-lg leading-relaxed whitespace-pre-wrap mb-2">
                      {msg.content}
                    </div>
                  )}
                  
                  {msg.options && msg.options[0]?.type === 'theme_selector' && (
                    <div className="mt-4 space-y-3">
                      {msg.options[0].options.map((opt: any) => (
                        <motion.button
                          key={opt.id}
                          whileHover={{ scale: 1.03, x: 5 }}
                          whileTap={{ scale: 0.97 }}
                          onClick={() => handleOptionClick({ ...opt, action: 'select_theme' })}
                          className={`w-full text-left px-6 py-5 rounded-2xl transition-all shadow-lg ${
                            theme === 'dark'
                              ? 'bg-gray-800 hover:bg-gray-700 text-white border border-gray-700'
                              : 'bg-gradient-to-r from-blue-100 to-purple-100 hover:from-blue-200 hover:to-purple-200'
                          }`}
                        >
                          <div className="font-bold text-xl mb-1">{opt.label}</div>
                          <div className={`text-sm ${
                            theme === 'dark' ? 'text-gray-400' : 'text-gray-600'
                          }`}>{opt.description}</div>
                        </motion.button>
                      ))}
                    </div>
                  )}
                  
                  {msg.options && msg.options[0]?.type === 'roi_calculator' && (
                    <div className="mt-4">
                      <ROICalculator theme={theme as 'light' | 'dark'} />
                    </div>
                  )}

                  {msg.options && msg.options[0]?.type === 'info_card' && (
                    <div className="mt-4">
                      <InfoCard
                        title={msg.options[0].data.title}
                        content={msg.options[0].data.content}
                        icon={msg.options[0].data.icon}
                        expandedContent={msg.options[0].data.expandedContent}
                        theme={theme as 'light' | 'dark'}
                        maxHeight={500}
                      />
                    </div>
                  )}

                  {msg.options && msg.options[0]?.type === 'wallet_connect' && (
                    <div className="mt-4">
                      <WalletConnectCard
                        theme={theme as 'light' | 'dark'}
                        onConnected={(address) => {
                          addMessage('ai', `Great! Your wallet ${address.slice(0,6)}...${address.slice(-4)} is connected! 🎉 What would you like to do next?`, [
                            { label: '📊 View Dashboard', action: 'show_dashboard' },
                            { label: '💰 Buy OMK Tokens', action: 'show_swap' },
                            { label: '🏠 Browse Properties', action: 'show_properties' },
                          ]);
                        }}
                      />
                    </div>
                  )}

                  {msg.options && msg.options[0]?.type === 'dashboard' && (
                    <div className="mt-4">
                      <DashboardCard theme={theme as 'light' | 'dark'} demoMode={true} />
                    </div>
                  )}

                  {msg.options && msg.options[0]?.type === 'token_swap' && (
                    <div className="mt-4">
                      <SwapCard
                        theme={theme as 'light' | 'dark'}
                        demoMode={true}
                        onSwap={(from, to) => {
                          addMessage('ai', `Awesome! You swapped ${from} for ${to} OMK tokens! 🎉 Ready to invest in properties now?`, [
                            { label: '🏠 Yes, show me properties', action: 'show_properties' },
                            { label: '📊 View my portfolio', action: 'show_dashboard' },
                          ]);
                        }}
                      />
                    </div>
                  )}

                  {msg.options && msg.options[0]?.type === 'property_browser' && (
                    <div className="mt-4">
                      <PropertyCard
                        theme={theme as 'light' | 'dark'}
                        onInvest={(propId, blocks) => {
                          addMessage('ai', `Congratulations! 🎉 You've invested in ${blocks} blocks! You'll start earning passive income monthly. Check your dashboard to track returns!`, [
                            { label: '📊 View Dashboard', action: 'show_dashboard' },
                            { label: '🏠 Invest in more properties', action: 'show_properties' },
                          ]);
                        }}
                      />
                    </div>
                  )}

                  {msg.options && msg.options[0]?.type === 'private_sale' && (
                    <div className="mt-4">
                      <div className="bg-gradient-to-br from-purple-900/50 to-blue-900/50 rounded-2xl p-6 border border-purple-500/30">
                        <h3 className="text-2xl font-bold mb-4 text-center">🎯 Private Sale</h3>
                        <div className="space-y-4">
                          <div className="bg-black/30 rounded-xl p-4">
                            <p className="text-sm text-gray-400 mb-2">Current Tier</p>
                            <p className="text-3xl font-bold text-yellow-400">Tier 1</p>
                            <p className="text-lg text-gray-300">$0.100 per OMK</p>
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div className="bg-black/30 rounded-xl p-4">
                              <p className="text-sm text-gray-400">Min Investment</p>
                              <p className="text-xl font-bold">$500</p>
                            </div>
                            <div className="bg-black/30 rounded-xl p-4">
                              <p className="text-sm text-gray-400">Bonus</p>
                              <p className="text-xl font-bold text-green-400">+15%</p>
                            </div>
                          </div>
                          <div className="bg-black/30 rounded-xl p-4">
                            <p className="text-sm text-gray-400 mb-3">Why Join?</p>
                            <ul className="space-y-2 text-sm">
                              <li>✅ Lowest price per token</li>
                              <li>✅ 15% bonus tokens</li>
                              <li>✅ Early access to platform</li>
                              <li>✅ Priority support</li>
                            </ul>
                          </div>
                          <button 
                            onClick={() => {
                              addMessage('user', 'I want to join the private sale');
                              addMessage('ai', 'Excellent choice! 🎉\n\nTo participate:\n1️⃣ Minimum $500 investment\n2️⃣ KYC verification required\n3️⃣ 15% bonus tokens\n4️⃣ Vesting: 20% TGE, rest over 6 months\n\nReady to proceed?', [
                                { label: '✅ Start KYC process', action: 'start_kyc' },
                                { label: '📖 View token tiers', action: 'show_tiers' },
                                { label: '💰 Calculate my allocation', action: 'show_roi_calculator' },
                                { label: '❌ Maybe later', action: 'show_dashboard' }
                              ]);
                            }}
                            className="w-full bg-gradient-to-r from-yellow-500 to-yellow-600 text-black font-bold py-3 rounded-xl hover:scale-105 transition-transform"
                          >
                            Join Private Sale 🚀
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {msg.options && msg.options[0]?.type !== 'theme_selector' && msg.options[0]?.type !== 'roi_calculator' && msg.options[0]?.type !== 'info_card' && msg.options[0]?.type !== 'wallet_connect' && msg.options[0]?.type !== 'dashboard' && msg.options[0]?.type !== 'token_swap' && msg.options[0]?.type !== 'property_browser' && msg.options[0]?.type !== 'private_sale' && (
                    <div className="mt-4 space-y-2">
                      {msg.options.map((opt: any, optIdx: number) => (
                        <motion.button
                          key={optIdx}
                          whileHover={{ scale: 1.02, x: 5 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => handleOptionClick(opt)}
                          className={`w-full text-left px-5 py-4 rounded-xl transition-all text-lg font-medium ${
                            theme === 'dark'
                              ? 'bg-gray-800 hover:bg-gray-700 text-white border border-gray-700'
                              : 'bg-purple-100 hover:bg-purple-200'
                          }`}
                        >
                          {opt.label}
                        </motion.button>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="max-w-[90%] bg-gradient-to-r from-yellow-500 via-yellow-600 to-yellow-700 text-black shadow-2xl rounded-3xl rounded-tr-sm px-6 py-4">
                  <div className="text-lg leading-relaxed font-semibold">{msg.content}</div>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
          
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start mb-6"
          >
            <div className={`shadow-lg rounded-3xl rounded-tl-sm px-6 py-4 ${
              theme === 'dark' ? 'bg-gray-900/95 border border-gray-800' : 'bg-white/90 backdrop-blur-xl'
            }`}>
              <div className="flex gap-2">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.2 }}
                    className={`w-3 h-3 rounded-full ${
                      theme === 'dark' ? 'bg-gray-600' : 'bg-purple-400'
                    }`}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <motion.div 
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        className={`fixed bottom-0 left-0 right-0 z-30 backdrop-blur-xl border-t p-6 shadow-2xl ${
          theme === 'dark' ? 'bg-black/95 border-yellow-900/30' : 'bg-stone-50/90 border-yellow-600/30'
        }`}
      >
        <div className="max-w-5xl mx-auto flex gap-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            disabled={loading}
            className={`flex-1 px-8 py-5 rounded-full border-2 focus:outline-none transition-all text-lg font-medium ${
              theme === 'dark'
                ? 'bg-stone-900 border-yellow-900/30 focus:border-yellow-600 text-stone-100 placeholder-stone-500'
                : 'bg-white border-yellow-600/30 focus:border-yellow-500 placeholder-stone-400'
            }`}
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-8 py-5 bg-gradient-to-r from-yellow-500 via-yellow-600 to-yellow-700 text-black rounded-full shadow-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 font-bold text-lg hover:from-yellow-400 hover:via-yellow-500 hover:to-yellow-600"
          >
            <Send className="w-6 h-6" />
          </motion.button>
        </div>
      </motion.div>

      {/* Floating Menu */}
      <FloatingMenu onItemClick={handleMenuClick} theme={theme as 'light' | 'dark'} />
    </div>
  );
}
