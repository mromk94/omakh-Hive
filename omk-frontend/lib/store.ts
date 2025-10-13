import { create } from 'zustand';

interface User {
  user_id: string;
  email: string;
  full_name: string;
  user_type: string;
  language: string;
  theme: string;
  wallet_address?: string;
  wallet_balance_omk?: number;
  wallet_balance_usd?: number;
  roi_percentage?: number;
}

interface AppState {
  // User & Auth
  user: User | null;
  session_token: string | null;
  isAuthenticated: boolean;
  
  // UI State
  language: string;
  theme: string;
  currentStage: string;
  
  // Actions
  setUser: (user: User | null) => void;
  setSessionToken: (token: string | null) => void;
  setLanguage: (language: string) => void;
  setTheme: (theme: string) => void;
  setStage: (stage: string) => void;
  logout: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Initial state
  user: null,
  session_token: typeof window !== 'undefined' ? localStorage.getItem('session_token') : null,
  isAuthenticated: false,
  language: typeof window !== 'undefined' ? localStorage.getItem('language') || 'en' : 'en',
  theme: typeof window !== 'undefined' ? localStorage.getItem('theme') || 'light' : 'light',
  currentStage: 'greeting',
  
  // Actions
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  
  setSessionToken: (token) => {
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('session_token', token);
      } else {
        localStorage.removeItem('session_token');
      }
    }
    set({ session_token: token, isAuthenticated: !!token });
  },
  
  setLanguage: (language) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('language', language);
    }
    set({ language });
  },
  
  setTheme: (theme) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('theme', theme);
      // Properly add/remove dark class
      if (theme === 'dark') {
        document.documentElement.classList.add('dark');
        document.body.style.backgroundColor = '#000000';
      } else {
        document.documentElement.classList.remove('dark');
        document.body.style.backgroundColor = '#ffffff';
      }
    }
    set({ theme });
  },
  
  setStage: (stage) => set({ currentStage: stage }),
  
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('session_token');
      localStorage.removeItem('user');
    }
    set({ user: null, session_token: null, isAuthenticated: false });
  },
}));
