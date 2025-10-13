'use client';

import { usePathname, useRouter } from 'next/navigation';
import BalanceBubble from '@/components/web3/BalanceBubble';
import FloatingMenu from '@/components/menu/FloatingMenu';
import { chatActions } from '@/lib/chatEvents';

export default function AppShell() {
  const pathname = usePathname();
  const router = useRouter();
  
  // Don't show on landing/connect pages
  const showComponents = pathname !== '/' && pathname !== '/connect';

  // 🌟 GOLDEN RULE: All menu actions trigger chat conversations
  const handleMenuClick = (action: string, url?: string) => {
    if (url) {
      window.open(url, '_blank');
      return;
    }

    // Navigate to chat first if not already there
    if (pathname !== '/chat') {
      router.push('/chat');
    }

    // Trigger chat conversation based on action
    setTimeout(() => {
      switch (action) {
        case 'dashboard':
          chatActions.showDashboard();
          break;
        case 'buy_omk':
          chatActions.buyOMK();
          break;
        case 'profit_calculator':
        case 'profit_calc':
          chatActions.investInProperty();
          break;
        default:
          // For other actions, trigger generic chat
          console.log('Menu action:', action);
      }
    }, 300);
  };

  if (!showComponents) return null;

  return (
    <>
      <BalanceBubble />
      <FloatingMenu 
        onItemClick={handleMenuClick} 
        theme="dark" 
      />
    </>
  );
}
