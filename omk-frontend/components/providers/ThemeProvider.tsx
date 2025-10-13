'use client';

import { useEffect } from 'react';
import { useAppStore } from '@/lib/store';

export default function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { theme, setTheme } = useAppStore();

  useEffect(() => {
    // Apply theme from localStorage on mount
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark');
      document.body.style.backgroundColor = '#000000';
    } else {
      document.documentElement.classList.remove('dark');
      document.body.style.backgroundColor = '#ffffff';
    }

    // If theme in store doesn't match, update it
    if (savedTheme !== theme) {
      setTheme(savedTheme);
    }
  }, []); // Run once on mount

  // Re-apply theme when it changes
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      document.body.style.backgroundColor = '#000000';
    } else {
      document.documentElement.classList.remove('dark');
      document.body.style.backgroundColor = '#ffffff';
    }
  }, [theme]);

  return <>{children}</>;
}
