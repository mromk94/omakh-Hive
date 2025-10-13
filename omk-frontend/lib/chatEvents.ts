/**
 * 🌟 GOLDEN RULE: Chat Event System
 * 
 * This allows components anywhere in the app to trigger chat messages
 * Following the conversational-first design principle.
 */

export interface ChatMessage {
  user: string;
  ai: string;
  cardType?: string;
  cardData?: any;
}

export const triggerChatMessage = (message: ChatMessage) => {
  // Dispatch custom event that chat page will listen to
  window.dispatchEvent(new CustomEvent('addChatMessage', {
    detail: message
  }));
};

// Helper functions for common actions
export const chatActions = {
  showDashboard: () => {
    triggerChatMessage({
      user: 'Show me my portfolio',
      ai: 'Here\'s your portfolio overview! 📊',
      cardType: 'dashboard'
    });
  },

  buyOMK: () => {
    triggerChatMessage({
      user: 'I want to buy OMK tokens',
      ai: 'Great! Let\'s get you some OMK tokens! 🪙\n\nHow much would you like to invest?',
      cardType: 'omk_purchase'
    });
  },

  investInProperty: () => {
    triggerChatMessage({
      user: 'I want to invest in real estate',
      ai: 'Excellent choice! Here are our available properties 🏢',
      cardType: 'property_list'
    });
  },

  swap: () => {
    triggerChatMessage({
      user: 'I want to swap tokens',
      ai: 'Let\'s swap some tokens! What would you like to swap?',
      cardType: 'token_swap'
    });
  },

  showProfile: () => {
    triggerChatMessage({
      user: 'Show my profile',
      ai: 'Here are your account details! 👤',
      cardType: 'profile'
    });
  },

  showSettings: () => {
    triggerChatMessage({
      user: 'Open settings',
      ai: 'Here are your settings! ⚙️',
      cardType: 'settings'
    });
  }
};
