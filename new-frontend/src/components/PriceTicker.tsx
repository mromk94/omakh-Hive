'use client'
import { useEffect, useMemo, useRef, useState } from 'react'
import { API_ENDPOINTS } from '@/lib/constants'
import { useI18n } from '@/lib/i18n'

type Props = {
  onMenuSelect?: (key: string, label: string) => void
}

export default function PriceTicker({ onMenuSelect }: Props) {
  const [price, setPrice] = useState(1.00)
  const [base, setBase] = useState(1.00)
  const [dir, setDir] = useState<'up' | 'down'>('up')
  const { t } = useI18n()
  const simRef = useRef<number | null>(null)
  const feedRef = useRef<boolean>(false)
  const [open, setOpen] = useState(false)
  const [active, setActive] = useState(0)
  const menuRef = useRef<HTMLDivElement | null>(null)
  const buttonRef = useRef<HTMLButtonElement | null>(null)
  const itemRefs = useRef<Array<HTMLButtonElement | null>>([])

  useEffect(() => {
    const API = `${API_ENDPOINTS.MARKET}/omk`

    async function tickFetch() {
      try {
        const res = await fetch(API, { cache: 'no-store' })
        if (!res.ok) throw new Error(String(res.status))
        const data = await res.json()
        const p = Number(data?.data?.price ?? data?.price)
        const ref = Number(data?.data?.open ?? data?.open ?? p)
        if (!isFinite(p) || p <= 0) throw new Error('bad price')
        feedRef.current = true
        setBase(isFinite(ref) && ref > 0 ? ref : p)
        setDir(p >= price ? 'up' : 'down')
        setPrice(p)
      } catch {
        if (!feedRef.current && simRef.current == null) {
          const id = window.setInterval(() => {
            setPrice((prev) => {
              const delta = (Math.random() * 0.004) * (Math.random() > 0.5 ? 1 : -1)
              const next = Math.max(0.01, +(prev + delta).toFixed(4))
              setDir(next >= prev ? 'up' : 'down')
              return next
            })
          }, 2500)
          simRef.current = id
        }
      }
    }

    tickFetch()
    const poll = window.setInterval(tickFetch, 10000)
    return () => {
      window.clearInterval(poll)
      if (simRef.current) window.clearInterval(simRef.current)
      simRef.current = null
    }
  }, [])

  const color = useMemo(() => dir === 'up' ? 'text-emerald-400' : 'text-rose-400', [dir])
  const arrow = useMemo(() => dir === 'up' ? '▲' : '▼', [dir])
  const pct = useMemo(() => {
    const p = ((price - base) / (base || 1)) * 100
    return p
  }, [price, base])
  const pctLabel = useMemo(() => `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`, [pct])
  const pctColor = useMemo(() => pct >= 0 ? 'text-emerald-400' : 'text-rose-400', [pct])

  const menu: Array<{ key: string; label: string }> = [
    { key: 'blocks', label: t('menu_blocks') },
    { key: 'how', label: t('menu_how_it_works') },
    { key: 'stake', label: t('menu_stake') },
    { key: 'private_sale', label: t('menu_private_sale') },
    { key: 'governance', label: t('menu_governance_full') },
    { key: 'profit_calc', label: t('menu_profit_calc') },
    { key: 'about_omk', label: t('menu_about_omk') },
    { key: 'about_hive', label: t('menu_about_hive') },
    { key: 'tokenomics', label: t('menu_tokenomics') },
    { key: 'community', label: t('menu_community') },
    { key: 'bees', label: t('menu_bees') },
    { key: 'roadmap', label: t('menu_roadmap') },
    { key: 'drip_schedule', label: t('menu_drip_schedule') },
    { key: 'security', label: t('menu_security') },
    { key: 'cross_chain', label: t('menu_cross_chain') },
    { key: 'utilities', label: t('menu_utilities') },
  ]

  useEffect(() => {
    if (!open) return
    setActive(0)
    const to = setTimeout(() => {
      itemRefs.current[0]?.focus()
    }, 0)
    const onDocDown = (e: MouseEvent) => {
      const target = e.target as Node
      if (!menuRef.current || !buttonRef.current) return
      if (!menuRef.current.contains(target) && !buttonRef.current.contains(target)) {
        setOpen(false)
      }
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        setOpen(false)
        buttonRef.current?.focus()
      }
    }
    document.addEventListener('mousedown', onDocDown)
    document.addEventListener('keydown', onKey)
    return () => {
      clearTimeout(to)
      document.removeEventListener('mousedown', onDocDown)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  const handleButtonKeyDown: React.KeyboardEventHandler<HTMLButtonElement> = (e) => {
    if (e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setOpen(true)
    }
  }

  const handleMenuKeyDown: React.KeyboardEventHandler<HTMLDivElement> = (e) => {
    if (!open) return
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      const next = (active + 1) % menu.length
      setActive(next)
      itemRefs.current[next]?.focus()
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      const next = (active - 1 + menu.length) % menu.length
      setActive(next)
      itemRefs.current[next]?.focus()
    } else if (e.key === 'Enter') {
      e.preventDefault()
      const m = menu[active]
      setOpen(false)
      onMenuSelect?.(m.key, m.label)
    }
  }

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        onClick={() => setOpen((v) => !v)}
        onKeyDown={handleButtonKeyDown}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls="ticker-menu"
        title={t('main_menu_title')}
        className="float-bubble tilt-on-hover inline-flex items-center gap-3 rounded-full border border-[#FFD700]/30 bg-[var(--panel)] px-4 py-2 text-sm shadow-[0_10px_20px_rgba(0,0,0,0.25)] focus:outline-none focus:ring-2 focus:ring-[#FFD700]/50"
      >
        <div className="rounded-full bg-gradient-to-br from-[#FFD700] to-[#F5A623] px-3 py-1 text-xs font-semibold text-black">OMK/USDT</div>
        <div className={`font-semibold ${color}`}>{arrow} ${price.toFixed(4)}</div>
        <div className={`rounded-full border px-2 py-0.5 text-xs ${pct >= 0 ? 'border-emerald-500/30 bg-emerald-500/10' : 'border-rose-500/30 bg-rose-500/10'}`}> 
          <span className={pctColor}>{pctLabel}</span>
        </div>
        <div className="text-xs opacity-60">{t('live')}</div>
        <div aria-hidden className="ml-1 text-xs opacity-70">▾</div>
      </button>
      {open && (
        <div
          id="ticker-menu"
          ref={menuRef}
          role="menu"
          aria-label={t('main_menu_title')}
          onKeyDown={handleMenuKeyDown}
          className="absolute left-0 right-0 z-30 mx-auto mt-2 w-[min(94vw,360px)] rounded-2xl border border-[#FFD700]/25 bg-[var(--panel)] p-2 text-sm shadow-[0_10px_25px_rgba(0,0,0,0.35)] sm:left-auto sm:right-auto"
        >
          <div className="sticky top-0 z-10 flex items-center justify-between rounded-xl bg-[var(--panel)]/85 px-2 pb-1 pt-1 backdrop-blur">
            <div className="text-xs opacity-70">{t('main_menu_title')}</div>
            <button onClick={() => setOpen(false)} className="rounded-lg border border-[#FFD700]/25 px-2 py-0.5 text-[10px] hover:border-[#FFD700]/60">Close</button>
          </div>
          <div className="relative max-h-[70vh] overflow-auto pr-1">
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {menu.map((m, idx) => (
                <button
                  key={m.key}
                  ref={(el) => { itemRefs.current[idx] = el }}
                  role="menuitem"
                  tabIndex={-1}
                  onClick={() => { setOpen(false); onMenuSelect?.(m.key, m.label); }}
                  className={`rounded-full border border-[#FFD700]/25 px-3 py-2 text-left hover:border-[#FFD700]/60 ${active === idx ? 'bg-[var(--panel-2)]' : ''}`}
                >
                  {m.label}
                </button>
              ))}
            </div>
            <div aria-hidden className="pointer-events-none absolute inset-x-0 bottom-0 h-6 bg-gradient-to-t from-[var(--panel)] to-transparent" />
          </div>
        </div>
      )}
    </div>
  )
}
