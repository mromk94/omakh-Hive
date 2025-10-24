'use client'
import PriceTicker from '@/components/PriceTicker'
import ConnectButton from '@/components/ConnectButton'
import BalanceBubble from '@/components/BalanceBubble'

type Props = {
  onMenuSelect?: (key: string, label: string) => void
}

export default function AppHeader({ onMenuSelect }: Props) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#FFD700]/10 bg-[var(--background)]/70 backdrop-blur" style={{ paddingTop: 'env(safe-area-inset-top)' }}>
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-3 py-3 sm:px-4">
        <div className="flex items-center gap-3">
          <div className="rounded-lg border border-[#FFD700]/30 bg-[var(--panel)] px-2 py-1 text-xs font-semibold">OMK Hive</div>
          <div className="hidden sm:block">
            <PriceTicker onMenuSelect={onMenuSelect} />
          </div>
        </div>
        <div className="flex items-center gap-2">
          <BalanceBubble variant="inline" />
          <ConnectButton />
        </div>
      </div>
      <div className="px-3 pb-2 sm:hidden">
        <PriceTicker onMenuSelect={onMenuSelect} />
      </div>
    </header>
  )
}
