'use client'
import Link from 'next/link'
import { useState } from 'react'
import AppHeader from '@/components/layout/AppHeader'
import WidgetHost from '@/components/widgets/WidgetHost'
import WidgetRenderer from '@/components/widgets/WidgetRenderer'
import QuickActions from '@/components/QuickActions'

export default function InvestPage() {
  const [open, setOpen] = useState(false)
  const [wKey, setWKey] = useState('')
  const [wLabel, setWLabel] = useState('')

  const onOpenWidget = (key: string, label: string) => {
    setWKey(key); setWLabel(label); setOpen(true)
  }

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <AppHeader onMenuSelect={onOpenWidget} />
      <WidgetHost open={open} widgetKey={wKey} label={wLabel} onClose={() => setOpen(false)} onOpenWidget={onOpenWidget} />
      <div className="relative mx-auto max-w-3xl px-4 py-8">
        <div className="mb-5 flex items-center justify-between">
          <h1 className="text-glow text-xl font-semibold">🏗️ Invest</h1>
          <Link href="/chat" className="rounded-full border border-[#FFD700]/30 px-3 py-2 text-sm hover:border-[#FFD700]/60">← Chat</Link>
        </div>
        <QuickActions onOpenWidget={onOpenWidget} />
        <div className="float-bubble rounded-2xl border border-[#FFD700]/20 bg-[var(--panel)] p-4 sm:p-6">
          <WidgetRenderer widgetKey="blocks" label="Investment Blocks" onOpenWidget={onOpenWidget} />
        </div>
      </div>
    </div>
  )
}
