'use client';

import { usePathname } from 'next/navigation';
import BalanceBubble from '@/components/web3/BalanceBubble';
import FloatingMenu from '@/components/menu/FloatingMenu';

export default function AppShell() {
  const pathname = usePathname();
  
  // Don't show on landing/connect pages
  const showComponents = pathname !== '/' && pathname !== '/connect';

  const handleMenuClick = (action: string, url?: string) => {
    if (url) {
      window.open(url, '_blank');
    } else {
      // Handle menu actions
      console.log('Menu action:', action);
      
      // Navigate based on action
      const routes: Record<string, string> = {
        'dashboard': '/dashboard',
        'buy_omk': '/swap',
        'profit_calculator': '/invest',
        'login': '/connect',
        'register': '/connect',
      };
      
      if (routes[action]) {
        window.location.href = routes[action];
      }
    }
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
