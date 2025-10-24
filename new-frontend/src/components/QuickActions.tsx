'use client'
import React from 'react'

export default function QuickActions({ onOpenWidget }: { onOpenWidget: (key: string, label: string) => void }) {
  const actions = [
    { key: 'private_sale', label: 'Buy OMK', icon: '💎', desc: 'Acquire OMK via guided OTC flow' },
    { key: 'stake', label: 'Stake OMK', icon: '📦', desc: 'Stake to earn and secure the Hive' },
    { key: 'blocks', label: 'Buy Blocks', icon: '🏠', desc: 'Invest in fractionalized properties' },
  ] as const
  return (
    <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
      {actions.map((a) => (
        <button
          key={a.key}
          onClick={() => onOpenWidget(a.key, a.label)}
          className="pop-in tilt-on-hover group rounded-2xl border border-[#FFD700]/25 bg-[var(--panel)] p-4 text-left transition hover:border-[#FFD700]/60 hover:bg-[var(--panel-2)] sm:p-5"
        >
          <div className="mb-2 flex items-center gap-2">
            <span className="icon-badge ring-glow">{a.icon}</span>
            <div className="text-lg font-semibold">{a.label}</div>
          </div>
          <div className="text-sm opacity-75">{a.desc}</div>
        </button>
      ))}
    </div>
  )
}
