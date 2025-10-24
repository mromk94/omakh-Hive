'use client'
import { useEffect, useMemo, useRef, useState } from 'react'
import { useI18n } from '@/lib/i18n'
import { useAccount, useConnect, useDisconnect, useReadContract, useReadContracts } from 'wagmi'
import { sepolia } from 'viem/chains'
import { formatUnits } from 'viem'
import { API_ENDPOINTS } from '@/lib/constants'

type Props = {
  variant?: 'floating' | 'inline'
  onOpenWidget?: (key: string, label: string) => void
}

export default function BalanceBubble({ variant = 'floating', onOpenWidget }: Props) {
  const [expanded, setExpanded] = useState(false)
  const [mounted, setMounted] = useState(false)
  const panelRef = useRef<HTMLDivElement>(null)
  const { address, isConnected, chainId } = useAccount()
  const { connect, connectors, status: connectStatus } = useConnect()
  const { disconnect } = useDisconnect()
  const [hideWc, setHideWc] = useState(false)
  const token = process.env.NEXT_PUBLIC_OMK_TOKEN_SEPOLIA as `0x${string}` | undefined
  const { data: reads } = useReadContracts({
    allowFailure: true,
    contracts: [
      {
        abi: [ { type: 'function', stateMutability: 'view', name: 'balanceOf', inputs: [{ name: 'a', type: 'address' }], outputs: [{ type: 'uint256' }] } ] as const,
        address: token,
        functionName: 'balanceOf',
        args: [address as `0x${string}`],
        chainId: sepolia.id,
      },
      {
        abi: [ { type: 'function', stateMutability: 'view', name: 'decimals', inputs: [], outputs: [{ type: 'uint8' }] } ] as const,
        address: token,
        functionName: 'decimals',
        chainId: sepolia.id,
      }
    ],
    query: { enabled: mounted && !!address && !!token }
  })
  const { t } = useI18n()

  useEffect(() => {
    setMounted(true)
    try { setHideWc(localStorage.getItem('hide_wc') === '1') } catch {}
  }, [])

  const setHide = (v: boolean) => {
    setHideWc(v)
    try {
      if (v) localStorage.setItem('hide_wc', '1')
      else localStorage.removeItem('hide_wc')
    } catch {}
  }

  useEffect(() => {
    const id = setInterval(() => {}, 5000)
    return () => clearInterval(id)
  }, [])

  const [usd, setUsd] = useState(0)
  useEffect(() => {
    const API = `${API_ENDPOINTS.MARKET}/omk`
    let alive = true
    fetch(API, { cache: 'no-store' }).then(r => r.ok ? r.json() : null).then(j => {
      if (!alive) return
      const p = Number(j?.data?.price ?? j?.price)
      if (isFinite(p) && p > 0) setUsd(p)
    }).catch(() => {})
    return () => { alive = false }
  }, [])

  const omk = useMemo(() => {
    const bal = reads?.[0]?.result as bigint | undefined
    const dec = Number(reads?.[1]?.result ?? 18)
    if (bal === undefined || !isFinite(dec)) return '0.0000'
    try {
      const s = parseFloat(formatUnits(bal, dec))
      return (isFinite(s) ? s : 0).toFixed(4)
    } catch { return '0.0000' }
  }, [reads])

  const shortAddr = useMemo(() => address ? `${address.slice(0,6)}…${address.slice(-4)}` : '' , [address])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setExpanded(false) }
    const onDoc = (e: MouseEvent) => {
      if (!expanded) return
      const el = panelRef.current
      if (el && !el.contains(e.target as Node)) setExpanded(false)
    }
    document.addEventListener('keydown', onKey)
    document.addEventListener('mousedown', onDoc)
    return () => { document.removeEventListener('keydown', onKey); document.removeEventListener('mousedown', onDoc) }
  }, [expanded])

  const panel = (
    <div ref={panelRef} id="balance-panel" className="pop-in absolute right-0 z-20 mt-2 w-72 max-w-[85vw] rounded-2xl border border-[#FFD700]/30 bg-[var(--panel)] p-4 text-sm shadow-[0_10px_25px_rgba(0,0,0,0.3)]">
      <div className="flex items-center justify-between"><span>OMK</span><span className="font-semibold">{omk}</span></div>
      <div className="mt-1 flex items-center justify-between text-xs opacity-70"><span>USD</span><span>${(Number(omk) * usd || 0).toFixed(2)}</span></div>
      <div className="mt-3 grid grid-cols-2 gap-2">
        <button onClick={() => onOpenWidget?.('private_sale','Private Sale')} className="rounded-xl bg-gradient-to-br from-[#FFD700] to-[#F5A623] px-3 py-2 text-xs font-semibold text-black hover:brightness-95">{t('buy_omk')}</button>
        <button onClick={() => onOpenWidget?.('private_sale','Private Sale')} className="rounded-xl border border-[#FFD700]/30 px-3 py-2 text-xs hover:border-[#FFD700]/60">{t('swap')}</button>
      </div>
      <div className="mt-3">
        {!isConnected ? (
          <div className="grid gap-2">
            {(() => {
              const seen = new Set<string>()
              const norm = (name: string) => name === 'Injected' ? 'MetaMask' : name
              const allowed = new Set(['MetaMask', 'WalletConnect', 'Coinbase Wallet', 'Phantom'])
              const list = connectors.filter(c => {
                const n = norm(c.name)
                if (!allowed.has(n)) return false
                if (hideWc && n === 'WalletConnect') return false
                if (seen.has(n)) return false
                seen.add(n)
                return true
              })
              const label = (name: string) => {
                const n = name === 'Injected' ? 'MetaMask' : name
                return n === 'WalletConnect' ? 'WalletConnect / Trust Wallet' : n
              }
              return (
                <>
                  {list.map((c) => (
                    <button
                      key={c.uid}
                      onClick={() => connect({ connector: c })}
                      className="w-full rounded-xl border border-emerald-400/40 px-3 py-2 text-xs text-emerald-300 hover:border-emerald-300"
                    >
                      {t('connect_wallet')} {label(c.name)}
                    </button>
                  ))}
                  <div className="mt-1 text-[11px] opacity-60">
                    {hideWc ? (
                      <button onClick={() => setHide(false)} className="underline hover:opacity-100">Show WalletConnect</button>
                    ) : (
                      <button onClick={() => setHide(true)} className="underline hover:opacity-100">Having issues with QR? Hide WalletConnect</button>
                    )}
                  </div>
                </>
              )
            })()}
          </div>
        ) : (
          <div className="grid gap-2">
            <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 px-3 py-2 text-xs">{shortAddr} • {chainId === sepolia.id ? 'Sepolia' : `Chain ${chainId}`}</div>
            <button onClick={() => disconnect()} className="w-full rounded-xl border border-rose-400/40 px-3 py-2 text-xs text-rose-300 hover:border-rose-300">{t('disconnect')}</button>
          </div>
        )}
      </div>
      <div className="mt-2 text-[11px] opacity-60">More actions coming soon.</div>
    </div>
  )

  if (variant === 'inline') {
    return (
      <div className="relative inline-block">
        <button
          onClick={() => setExpanded((e) => !e)}
          className="float-bubble rounded-full border border-[#FFD700]/30 bg-[var(--panel)] px-4 py-2 text-sm shadow-[0_10px_20px_rgba(0,0,0,0.25)] hover:border-[#FFD700]/60 hover:bg-[var(--panel-2)]"
          aria-expanded={expanded}
          aria-controls="balance-panel"
        >
          💰 {t('balance')}{mounted && isConnected && ` • ${omk}`}
        </button>
        {expanded && panel}
      </div>
    )
  }

  return (
    <div className="pointer-events-auto fixed bottom-4 right-4 z-10 sm:bottom-6 sm:right-6">
      <button
        onClick={() => setExpanded((e) => !e)}
        className="float-bubble rounded-full border border-[#FFD700]/30 bg-[var(--panel)] px-4 py-2 text-sm shadow-[0_10px_20px_rgba(0,0,0,0.25)] hover:border-[#FFD700]/60 hover:bg-[var(--panel-2)]"
        aria-expanded={expanded}
        aria-controls="balance-panel"
      >
        💰 {t('balance')}
      </button>
      {expanded && (
        <div className="relative">{panel}</div>
      )}
    </div>
  )
}
