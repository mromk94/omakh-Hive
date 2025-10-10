import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Wallet {
  id: string;
  address: string;
  chain: 'ethereum' | 'solana';
  type: string;
  nickname?: string;
  isPrimary: boolean;
  connectedAt: Date;
}

export interface Balance {
  token: string;
  symbol: string;
  amount: number;
  decimals: number;
  usdValue: number;
  chain: string;
}

export interface UserProfile {
  id?: string;
  email?: string;
  kycStatus?: 'pending' | 'verified' | 'rejected';
  tier?: 'basic' | 'premium' | 'institutional';
}

interface AuthState {
  isConnected: boolean;
  primaryWallet: Wallet | null;
  connectedWallets: Wallet[];
  balances: Balance[];
  user: UserProfile | null;
  sessionToken: string | null;
  
  // Actions
  connectWallet: (wallet: Wallet) => void;
  disconnectWallet: (walletId: string) => void;
  setPrimaryWallet: (walletId: string) => void;
  setBalances: (balances: Balance[]) => void;
  setUser: (user: UserProfile) => void;
  setSessionToken: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      isConnected: false,
      primaryWallet: null,
      connectedWallets: [],
      balances: [],
      user: null,
      sessionToken: null,

      connectWallet: (wallet) => set((state) => {
        const wallets = [...state.connectedWallets, wallet];
        return {
          connectedWallets: wallets,
          primaryWallet: state.primaryWallet || wallet,
          isConnected: true,
        };
      }),

      disconnectWallet: (walletId) => set((state) => {
        const wallets = state.connectedWallets.filter(w => w.id !== walletId);
        const primary = state.primaryWallet?.id === walletId 
          ? wallets[0] || null 
          : state.primaryWallet;
        
        return {
          connectedWallets: wallets,
          primaryWallet: primary,
          isConnected: wallets.length > 0,
        };
      }),

      setPrimaryWallet: (walletId) => set((state) => {
        const wallet = state.connectedWallets.find(w => w.id === walletId);
        if (!wallet) return state;
        
        return {
          primaryWallet: wallet,
          connectedWallets: state.connectedWallets.map(w => ({
            ...w,
            isPrimary: w.id === walletId,
          })),
        };
      }),

      setBalances: (balances) => set({ balances }),
      setUser: (user) => set({ user }),
      setSessionToken: (token) => set({ sessionToken: token }),
      
      logout: () => set({
        isConnected: false,
        primaryWallet: null,
        connectedWallets: [],
        balances: [],
        user: null,
        sessionToken: null,
      }),
    }),
    {
      name: 'omk-auth-storage',
    }
  )
);
