'use client';
import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { frontendAPI } from '@/lib/api/queen';
import { useTheme } from '@/lib/useTheme';
import ThemeToggle from '@/components/ThemeToggle';
import AppHeader from '@/components/layout/AppHeader';
import WidgetHost from '@/components/widgets/WidgetHost';

type Greeting = { text: string; flag: string; name: string };

export default function Home() {
  const router = useRouter();
  const [greetings, setGreetings] = useState<Record<string, Greeting>>({
    en: { text: 'Hello', flag: '🇬🇧', name: 'English' },
    es: { text: 'Hola', flag: '🇪🇸', name: 'Spanish' },
    fr: { text: 'Bonjour', flag: '🇫🇷', name: 'French' },
  });
  const [idx, setIdx] = useState(0);
  const { theme, toggle } = useTheme();
  const [widgetOpen, setWidgetOpen] = useState(false);
  const [widgetKey, setWidgetKey] = useState('');
  const [widgetLabel, setWidgetLabel] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), 1000);
    frontendAPI
      .getGreetings({ signal: controller.signal })
      .then((res) => {
        if (res?.greetings && Object.keys(res.greetings).length) setGreetings(res.greetings)
      })
      .catch(() => {})
      .finally(() => clearTimeout(id));
    return () => clearTimeout(id)
  }, []);

  const list = useMemo(() => Object.entries(greetings), [greetings]);

  useEffect(() => {
    if (!list.length) return;
    const t = setInterval(() => setIdx((v) => (v + 1) % list.length), 2500);
    return () => clearInterval(t);
  }, [list.length]);

  const choose = (lang: string) => {
    localStorage.setItem('language', lang);
    if (typeof window !== 'undefined') {
      try {
        sessionStorage.removeItem('queen_welcome_done');
        sessionStorage.removeItem('queen_welcome_meta');
        sessionStorage.removeItem('queen_welcome_msg');
      } catch {}
    }
    router.push('/chat');
  };

  const handleMenuSelect = (key: string, label: string) => {
    setWidgetKey(key);
    setWidgetLabel(label);
    setWidgetOpen(true);
  };

  return (
    <div className="relative min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <AppHeader onMenuSelect={handleMenuSelect} />
      <WidgetHost
        open={widgetOpen}
        widgetKey={widgetKey}
        label={widgetLabel}
        onClose={() => setWidgetOpen(false)}
      />
      <div className="blob left-[-60px] top-10 h-52 w-52 bg-[radial-gradient(circle_at_center,rgba(255,215,0,0.25),transparent_60%)]" />
      <div className="blob right-[-40px] top-1/3 h-64 w-64 bg-[radial-gradient(circle_at_center,rgba(245,166,35,0.18),transparent_60%)]" />
      <div className="blob bottom-[-60px] left-1/3 h-56 w-56 bg-[radial-gradient(circle_at_center,rgba(255,215,0,0.18),transparent_60%)]" />

      <div className="relative mx-auto max-w-5xl px-4 py-16 sm:px-6 sm:py-20 lg:py-24" style={{ paddingBottom: 'max(env(safe-area-inset-bottom), 4rem)' }}>
        <div className="mb-4 flex justify-end">
          <ThemeToggle theme={theme} onToggle={toggle} />
        </div>
        <h1
          className="float-bubble text-glow text-center text-5xl font-black sm:text-7xl lg:text-[9rem]"
          style={{ color: '#E7E5E4' }}
        >
          {list.length ? list[idx][1].text : 'Welcome'}
        </h1>
        <p className="mt-4 text-center text-base opacity-80 sm:mt-6 sm:text-lg">Choose your language</p>

        <div className="mt-10 grid grid-cols-2 gap-3 sm:mt-12 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4">
          {list.map(([code, g]) => (
            <button
              key={code}
              onClick={() => choose(code)}
              className="pop-in tilt-on-hover rounded-2xl border border-[#FFD700]/30 bg-[#0A0A0A] p-4 text-left hover:border-[#FFD700]/60 hover:bg-[#141414] sm:p-5"
            >
              <div className="text-4xl sm:text-5xl">{g.flag}</div>
              <div className="mt-2 text-lg font-semibold sm:mt-3 sm:text-xl">{g.name}</div>
            </button>
          ))}
        </div>

        {/* Quick actions removed from landing by request */}
      </div>
    </div>
  );
}
