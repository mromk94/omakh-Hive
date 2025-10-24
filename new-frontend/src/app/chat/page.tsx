'use client';
import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { frontendAPI } from '@/lib/api/queen';
import { useTheme } from '@/lib/useTheme';
import ThemeToggle from '@/components/ThemeToggle';
import PriceTicker from '@/components/PriceTicker';
import BalanceBubble from '@/components/BalanceBubble';
import { useI18n } from '@/lib/i18n';
import { queenAPI } from '@/lib/api/queen';
import WidgetRenderer from '@/components/widgets/WidgetRenderer';
import ConnectButton from '@/components/ConnectButton';
import { handleIntent } from '@/lib/intent/relay';

type Msg = {
  sender: 'user' | 'ai';
  content?: string;
  ts: number;
  id: string;
  type?: 'text' | 'widget';
  widget?: { key: string; label: string };
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiTyping, setAiTyping] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const [parallax, setParallax] = useState({ x1: 0, y1: 0, x2: 0, y2: 0, x3: 0, y3: 0 });
  const { theme, toggle } = useTheme();
  const { t, lang } = useI18n();
  const [flag, setFlag] = useState<string>('🏳️');
  const greetedRef = useRef(false);
  const reduceMotionRef = useRef(false);
  const [queenLive, setQueenLive] = useState<boolean | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      try { reduceMotionRef.current = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch {}
    }
  }, []);

  useEffect(() => {
    const key = 'queen_welcome_msg';
    const metaKey = 'queen_welcome_meta';
    const lockKey = 'queen_welcome_lock';
    const addedKey = 'queen_welcome_added';
    const ttlMs = 15 * 60 * 1000;
    const l = typeof window !== 'undefined' ? localStorage.getItem('language') || 'en' : 'en';
    const stored = typeof window !== 'undefined' ? sessionStorage.getItem(key) : null;
    const meta = typeof window !== 'undefined' ? sessionStorage.getItem(metaKey) : null;
    const flags: Record<string, string> = { en: '🇬🇧', es: '🇪🇸', fr: '🇫🇷' };
    setFlag(flags[l] || '🏳️');
    const now = Date.now();
    let metaObj: { ts: number; added?: boolean } | null = null;
    const fresh = (() => {
      if (!meta) return false;
      try {
        metaObj = JSON.parse(meta) as { ts: number; added?: boolean };
        return now - metaObj.ts < ttlMs;
      } catch {
        return false;
      }
    })();
    const addOnce = (msg: string) => {
      if (typeof window === 'undefined') return;
      if (greetedRef.current) return;
      try {
        const w: any = window as any;
        if (w.__queenGreetAdded) return; // global guard
        w.__queenGreetAdded = true;
      } catch {}
      try {
        const m = sessionStorage.getItem(metaKey);
        let o: { ts: number; added?: boolean } | null = null;
        if (m) o = JSON.parse(m) as any;
        if (o?.added) { greetedRef.current = true; return; }
        const tsVal = o?.ts ?? now;
        sessionStorage.setItem(metaKey, JSON.stringify({ ts: tsVal, added: true }));
      } catch {
        sessionStorage.setItem(metaKey, JSON.stringify({ ts: now, added: true }));
      }
      greetedRef.current = true;
      sessionStorage.setItem(addedKey, '1');
      add('ai', msg);
    };

    const checkHealth = () => {
      queenAPI.health().then((ok) => setQueenLive(!!ok)).catch(() => setQueenLive(false));
    };
    if (stored && fresh) {
      addOnce(stored);
      checkHealth();
      return;
    }
    setAiTyping(true);

    if (typeof window !== 'undefined' && sessionStorage.getItem(lockKey) === '1') {
      let tries = 0;
      const iv = setInterval(() => {
        tries += 1;
        const s = sessionStorage.getItem(key);
        const m = sessionStorage.getItem(metaKey);
        if (s && m) {
          try {
            const { ts, added } = JSON.parse(m) as { ts: number; added?: boolean };
            if (!added && now - ts < ttlMs) addOnce(s);
          } catch {}
          setAiTyping(false);
          clearInterval(iv);
        }
        if (tries > 20) clearInterval(iv);
      }, 100);
      return () => clearInterval(iv);
    }

    if (typeof window !== 'undefined') sessionStorage.setItem(lockKey, '1');

    const greetPrompt = `Greet the user briefly in ${l}. One short sentence. Introduce yourself as Queen AI of OMK Hive and offer help.`
    frontendAPI
      .chat(greetPrompt)
      .then((res) => {
        const msg = res?.message || ''
        if (msg) {
          if (typeof window !== 'undefined') {
            sessionStorage.setItem(key, msg)
            sessionStorage.setItem(metaKey, JSON.stringify({ ts: now, added: false }))
          }
          addOnce(msg)
          checkHealth()
        }
      })
      .catch(() => {
        const fallback = 'Hello, I am Queen. How can I help you today?'
        if (typeof window !== 'undefined') {
          sessionStorage.setItem(key, fallback)
          sessionStorage.setItem(metaKey, JSON.stringify({ ts: now, added: false }))
        }
        addOnce(fallback)
        checkHealth()
      })
      .finally(() => {
        if (typeof window !== 'undefined') sessionStorage.removeItem(lockKey);
        setAiTyping(false);
      });
  }, []);

  const add = (sender: 'user' | 'ai', content: string) => {
    const ts = Date.now();
    const id = `${ts}-${Math.random().toString(36).slice(2, 7)}`;
    setMessages((prev) => {
      if (sender === 'ai' && prev.length) {
        const last = prev[prev.length - 1];
        if (last.sender === 'ai' && last.content && content && last.content.trim() === content.trim()) return prev; // dedupe greeting
      }
      return [...prev, { sender, content, ts, id, type: 'text' }];
    });
    setTimeout(() => endRef.current?.scrollIntoView({ behavior: 'smooth' }), 0);
  };

  const addWidget = (key: string, label: string) => {
    const ts = Date.now();
    const id = `${ts}-${Math.random().toString(36).slice(2, 7)}`;
    setMessages((prev) => [...prev, { sender: 'ai', ts, id, type: 'widget', widget: { key, label } }]);
    setTimeout(() => endRef.current?.scrollIntoView({ behavior: 'smooth' }), 0);
  };

  const askFromWidget = async (prompt: string) => {
    // First try local intent relay before LLM
    const intent = handleIntent(prompt)
    if (intent.handled) {
      if (intent.reply) add('ai', intent.reply)
      if (intent.widget) addWidget(intent.widget.key, intent.widget.label)
      return
    }
    setAiTyping(true);
    try {
      const res = await frontendAPI.chat(prompt);
      add('ai', res?.message || '');
    } catch {
      add('ai', 'Sorry, I could not reach the Queen service.');
    } finally { setAiTyping(false); }
  };

  const send = async () => {
    const text = input.trim();
    if (!text) return;
    setInput('');
    add('user', text);
    // Relay first to avoid LLM cost when a widget can answer
    const intent = handleIntent(text)
    if (intent.handled) {
      if (intent.reply) add('ai', intent.reply)
      if (intent.widget) addWidget(intent.widget.key, intent.widget.label)
      return
    }
    setLoading(true);
    setAiTyping(true);
    try {
      const res = await frontendAPI.chat(text);
      add('ai', res?.message || '');
    } catch {
      add('ai', 'Sorry, I could not reach the Queen service.');
    } finally {
      setLoading(false);
      setAiTyping(false);
    }
  };

  const suggestions = [
    t('suggest_what_can'),
    t('suggest_explain_simple'),
    t('suggest_how_start'),
  ];

  const sendSuggestion = (text: string) => {
    setInput(text);
    setTimeout(() => send(), 0);
  };

  const onMouseMove: React.MouseEventHandler<HTMLDivElement> = (e) => {
    if (reduceMotionRef.current) return;
    const r = (e.currentTarget as HTMLDivElement).getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - 0.5;
    const py = (e.clientY - r.top) / r.height - 0.5;
    setParallax({
      x1: px * 8,
      y1: py * 8,
      x2: px * -14,
      y2: py * -14,
      x3: px * 10,
      y3: py * 10,
    });
  };

  const formatTime = (ts: number) => {
    const d = new Date(ts);
    const h = d.getHours().toString().padStart(2, '0');
    const m = d.getMinutes().toString().padStart(2, '0');
    return `${h}:${m}`;
  };

  return (
    <div className="relative min-h-screen bg-[var(--background)] text-[var(--foreground)]" onMouseMove={onMouseMove}>
      <div className="blob left-[-60px] top-10 h-52 w-52 bg-[radial-gradient(circle_at_center,rgba(255,215,0,0.25),transparent_60%)]" style={{ transform: `translate3d(${parallax.x1}px, ${parallax.y1}px, 0)` }} />
      <div className="blob right-[-40px] top-1/3 h-64 w-64 bg-[radial-gradient(circle_at_center,rgba(245,166,35,0.18),transparent_60%)]" style={{ transform: `translate3d(${parallax.x2}px, ${parallax.y2}px, 0)` }} />
      <div className="blob bottom-[-60px] left-1/3 h-56 w-56 bg-[radial-gradient(circle_at_center,rgba(255,215,0,0.18),transparent_60%)]" style={{ transform: `translate3d(${parallax.x3}px, ${parallax.y3}px, 0)` }} />

      <div className="relative mx-auto flex min-h-screen max-w-3xl flex-col px-3 py-4 sm:px-4 sm:py-6">
        <header className="sticky top-0 z-30 flex items-center justify-between gap-2 border-b border-[#FFD700]/10 bg-[var(--background)]/80 py-3 backdrop-blur sm:py-4">
          <h1 className="text-glow text-lg font-semibold tracking-tight sm:text-xl">👑 {t('queen_chat_title')}</h1>
          <div className="flex items-center gap-2">
            <ThemeToggle theme={theme} onToggle={toggle} />
            <ConnectButton />
            <button
              onClick={() => router.push('/')}
              aria-label={t('language')}
              className="grid h-9 w-9 place-items-center rounded-full border border-[#FFD700]/30 bg-[var(--panel)] text-lg hover:border-[#FFD700]/60"
            >
              <span>{flag}</span>
            </button>
          </div>
        </header>

        <div className="sticky top-[56px] z-20 mb-2 flex items-center justify-between gap-3 border-b border-[#FFD700]/10 bg-[var(--background)]/80 py-2 backdrop-blur sm:top-[64px] sm:mb-3">
          <PriceTicker onMenuSelect={(key, label) => {
            add('ai', `Let's explore: ${label}`);
            addWidget(key, label);
          }} />
          <BalanceBubble variant="inline" onOpenWidget={(k,l) => addWidget(k,l)} />
        </div>

        <div className="bg-glass float-bubble mt-2 flex-1 overflow-y-auto overscroll-contain rounded-2xl border border-[#FFD700]/15 p-3 sm:mt-4 sm:p-4" style={{ perspective: '1000px' }}>
          {queenLive !== null && (
            <div className="sticky top-0 z-10 mb-2 flex justify-center">
              <div className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-[11px] sm:text-xs ${queenLive ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' : 'border-rose-500/40 bg-rose-500/10 text-rose-300'}`}>
                <span className={`h-2 w-2 rounded-full ${queenLive ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                <span>{queenLive ? t('queen_live') : t('queen_offline')}</span>
              </div>
            </div>
          )}
          {messages.map((m) => (
            <div key={m.id} className={`mb-3 sm:mb-4 ${m.sender === 'ai' ? 'text-[#E7E5E4]' : 'text-white'}`}>
              <div className={`flex items-end ${m.sender === 'user' ? 'justify-end' : ''}`}>
                {m.sender === 'ai' && (
                  <div className="mr-2 grid h-8 w-8 place-items-center rounded-full border border-[#FFD700]/30 bg-[#141414] text-base">👑</div>
                )}
                <div
                  className={`pop-in tilt-on-hover inline-block max-w-[80%] rounded-3xl px-4 py-3 sm:max-w-[75%] sm:px-5 sm:py-4 ${
                    m.sender === 'ai'
                      ? theme === 'dark'
                        ? 'bg-[#141414] border border-[#FFD700]/20 shadow-[0_10px_30px_rgba(0,0,0,0.35)]'
                        : 'bg-white border border-[#FFD700]/30 text-[#171717] shadow-[0_10px_30px_rgba(0,0,0,0.15)]'
                      : theme === 'dark'
                        ? 'bg-[#1f1f1f] shadow-[0_10px_30px_rgba(0,0,0,0.35)]'
                        : 'bg-[#f4f4f5] text-[#171717] shadow-[0_10px_30px_rgba(0,0,0,0.1)]'
                  }`}
                  style={{ transform: 'translateZ(0)' }}
                >
                  <span className="text-xs opacity-80 sm:text-sm">{m.sender === 'ai' ? 'Queen' : 'You'}</span>
                  {m.type === 'widget' && m.widget ? (
                    <div className="mt-2">
                      <WidgetRenderer widgetKey={m.widget.key} label={m.widget.label} onPost={(text) => askFromWidget(text)} onOpenWidget={(k, l) => addWidget(k, l)} />
                    </div>
                  ) : (
                    <div className="mt-1 whitespace-pre-wrap break-words text-sm sm:text-base">{m.content}</div>
                  )}
                  <div className={`mt-2 text-[10px] opacity-60 ${m.sender === 'user' ? 'text-right' : ''}`}>{formatTime(m.ts)}</div>
                </div>
                {m.sender === 'user' && (
                  <div className="ml-2 grid h-8 w-8 place-items-center rounded-full border border-[#FFD700]/30 bg-[#1f1f1f] text-base">🙂</div>
                )}
              </div>
            </div>
          ))}
          {aiTyping && (
            <div className="mb-3 sm:mb-4 text-[#E7E5E4]">
              <div className="tilt-on-hover inline-block max-w-[80%] rounded-3xl border border-[#FFD700]/20 bg-[#141414] px-4 py-3 shadow-[0_10px_30px_rgba(0,0,0,0.35)] sm:max-w-[75%] sm:px-5 sm:py-4">
                <span className="text-xs opacity-80 sm:text-sm">Queen</span>
                <div className="mt-2 typing-dots"><span></span><span></span><span></span></div>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <div className="mt-3 flex gap-2 overflow-x-auto sm:mt-4">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => sendSuggestion(s)}
              className="tilt-on-hover whitespace-nowrap rounded-full border border-[#FFD700]/25 bg-[#0A0A0A] px-3 py-2 text-xs text-[#E7E5E4] hover:border-[#FFD700]/60 hover:bg-[#141414] sm:px-4 sm:text-sm"
            >
              {s}
            </button>
          ))}
        </div>

        <div className="sticky bottom-2 mt-3 flex gap-2 sm:bottom-4 sm:mt-4" style={{ paddingBottom: 'max(env(safe-area-inset-bottom), 0.5rem)' }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
            placeholder={t('input_placeholder')}
            aria-label="Message input"
            inputMode="text"
            autoComplete="off"
            className="flex-1 rounded-2xl border border-[#FFD700]/30 bg-black/80 px-4 py-3 text-base outline-none placeholder:text-zinc-500 focus:border-[#FFD700]/60 sm:px-5 sm:py-4"
          />
          <button
            onClick={send}
            aria-label="Send message"
            className="rounded-2xl bg-gradient-to-br from-[#FFD700] to-[#F5A623] px-4 py-3 text-sm font-semibold text-black shadow-[0_10px_20px_rgba(255,215,0,0.25)] hover:brightness-95 disabled:opacity-50 sm:px-5 sm:py-4 sm:text-base"
            disabled={loading}
          >
            {t('send')}
          </button>
        </div>
      </div>
    </div>
  );
}
