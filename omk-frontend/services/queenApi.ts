/**
 * Queen AI API Service
 * Connects frontend to the Queen's Hive backend
 */

const QUEEN_API_BASE = process.env.NEXT_PUBLIC_QUEEN_API_URL || 'http://localhost:8001';

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

interface ChatRequest {
  user_input: string;
  session_token?: string;
  context?: Record<string, any>;
}

interface ChatResponse {
  response: string;
  suggestions?: string[];
  context?: Record<string, any>;
}

interface MenuInteractionRequest {
  menu_item: string;
  session_token?: string;
}

class QueenApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${QUEEN_API_BASE}/api/v1/frontend`;
  }

  /**
   * Send a message to Queen AI and get conversational response
   */
  async chat(userInput: string, context?: Record<string, any>): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: userInput,
          context: context || {},
        } as ChatRequest),
      });

      if (!response.ok) {
        throw new Error(`Queen API error: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Queen API chat error:', error);
      throw error;
    }
  }

  /**
   * Handle menu interactions conversationally
   */
  async handleMenuClick(menuItem: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/menu-interaction`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          menu_item: menuItem,
        } as MenuInteractionRequest),
      });

      if (!response.ok) {
        throw new Error(`Queen API error: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Queen API menu interaction error:', error);
      throw error;
    }
  }

  /**
   * Get multilingual greetings
   */
  async getGreetings(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/greetings`);
      
      if (!response.ok) {
        throw new Error(`Queen API error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Queen API greetings error:', error);
      throw error;
    }
  }

  /**
   * Get welcome message after language selection
   */
  async getWelcomeMessage(language: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/welcome`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language }),
      });

      if (!response.ok) {
        throw new Error(`Queen API error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Queen API welcome error:', error);
      throw error;
    }
  }

  /**
   * Get theme selection prompt
   */
  async getThemeSelection(language: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/theme-selection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language }),
      });

      if (!response.ok) {
        throw new Error(`Queen API error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Queen API theme selection error:', error);
      throw error;
    }
  }

  /**
   * Ask if user has account
   */
  async askHasAccount(theme: string, language: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/ask-account`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ theme, language }),
      });

      if (!response.ok) {
        throw new Error(`Queen API error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Queen API ask account error:', error);
      throw error;
    }
  }

  /**
   * Check Queen backend health
   */
  async healthCheck(): Promise<any> {
    try {
      const response = await fetch(`${QUEEN_API_BASE}/health`);
      
      if (!response.ok) {
        throw new Error(`Queen health check failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Queen health check error:', error);
      return { status: 'offline', error: String(error) };
    }
  }

  /**
   * Explain a feature using AI
   */
  async explainFeature(feature: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/explain/${feature}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Queen API error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Queen API explain feature error:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const queenApi = new QueenApiService();
export default queenApi;
