'use client'
import { useEffect, useMemo, useRef, useState } from 'react'
import { useAccount, useConnect, useDisconnect } from 'wagmi'
import { sepolia } from 'viem/chains'

export default function ConnectButton() {
  const { isConnected, address, chainId } = useAccount()
  const { connect, connectors } = useConnect()
  const { disconnect } = useDisconnect()
  const [open, setOpen] = useState(false)
  const [mounted, setMounted] = useState(false)
  const btnRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    setMounted(true)
    const onDoc = (e: MouseEvent) => {
      if (!open) return
      const el = btnRef.current
      if (el && !el.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [open])

  const short = useMemo(() => address ? `${address.slice(0,6)}…${address.slice(-4)}` : 'Connect', [address])

  // Deduplicate connectors by normalized name
  const connectorList = useMemo(() => {
    const seen = new Set<string>()
    const norm = (name: string) => name === 'Injected' ? 'MetaMask' : name
    const allowed = new Set(['MetaMask', 'WalletConnect', 'Coinbase Wallet', 'Phantom'])
    return connectors.filter(c => {
      const n = norm(c.name)
      if (!allowed.has(n)) return false
      if (seen.has(n)) return false
      seen.add(n)
      return true
    })
  }, [connectors])

  const label = (name: string) => {
    const n = name === 'Injected' ? 'MetaMask' : name
    if (n === 'WalletConnect') return 'WalletConnect / Trust Wallet'
    return n
  }

  return (
    <div className="relative">
      <button
        ref={btnRef}
        onClick={() => setOpen((v) => !v)}
        className="grid h-9 max-w-[52vw] place-items-center overflow-hidden text-ellipsis whitespace-nowrap rounded-full border border-[#FFD700]/30 bg-[var(--panel)] px-3 text-xs hover:border-[#FFD700]/60 sm:max-w-none"
        aria-expanded={open}
      >
        {mounted && isConnected ? `${short} • ${chainId === sepolia.id ? 'Sepolia' : chainId}` : 'Connect Wallet'}
      </button>
      {mounted && open && (
        <div className="absolute right-0 mt-2 w-[78vw] max-w-xs rounded-xl border border-[#FFD700]/20 bg-[var(--panel)] p-2 text-xs shadow-[0_10px_25px_rgba(0,0,0,0.3)] sm:w-64">
          {!isConnected ? (
            <div className="grid gap-1">
              {connectorList.map((c) => (
                <button key={c.uid} onClick={() => connect({ connector: c })} className="rounded-lg px-3 py-2 text-left hover:bg-[var(--panel-2)]">Connect {label(c.name)}</button>
              ))}
            </div>
          ) : (
            <div className="grid gap-1">
              <div className="rounded-lg border border-[#FFD700]/15 bg-black/20 px-3 py-2 font-mono text-[11px] break-all">{address}</div>
              <button onClick={() => disconnect()} className="rounded-lg px-3 py-2 text-left text-rose-300 hover:bg-rose-500/10">Disconnect</button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
