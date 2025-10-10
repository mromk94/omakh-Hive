import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_QUEEN_API_URL 
  ? `${process.env.NEXT_PUBLIC_QUEEN_API_URL}/api/v1/frontend`
  : 'http://localhost:8001/api/v1/frontend';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('session_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// API methods
export const frontendAPI = {
  // Greetings
  getGreetings: () => api.get('/greetings'),
  getWelcome: (language: string) => api.post('/welcome', { language }),
  
  // Theme
  getThemeSelection: (language: string) => api.post('/theme-selection', { language }),
  askHasAccount: (theme: string, language: string) => api.post('/ask-account', { theme, language }),
  
  // Auth
  checkEmail: (email: string) => api.post('/check-email', { email }),
  register: (data: any) => api.post('/register', data),
  login: (email: string, password: string) => api.post('/login', { email, password }),
  logout: (token: string) => api.post('/logout', { session_token: token }),
  verifySession: (token: string) => api.post('/verify-session', { session_token: token }),
  
  // Onboarding
  getUserTypeOptions: () => api.post('/user-type-options', {}),
  getInfoSnippet: (snippetId: string, showMore: boolean = false) => 
    api.get(`/info-snippet/${snippetId}?show_more=${showMore}`),
  
  // Chat
  chat: (userInput: string, sessionToken?: string, context?: any) => 
    api.post('/chat', { user_input: userInput, session_token: sessionToken, context }),
  menuClick: (menuItem: string, sessionToken?: string) => 
    api.post('/menu-interaction', { menu_item: menuItem, session_token: sessionToken }),
  explainFeature: (feature: string) => api.post(`/explain/${feature}`, {}),
  getQuickHelp: () => api.get('/quick-help'),
  
  // Dashboard
  getWelcomeBack: (sessionToken: string) => 
    api.post('/welcome-back', { session_token: sessionToken }),
  getDashboardIntro: (sessionToken: string) => 
    api.post('/dashboard-intro', { session_token: sessionToken }),
  getWalletBalance: (sessionToken: string) => 
    api.post('/wallet-balance', { session_token: sessionToken }),
};
