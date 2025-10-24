'use client'
import { useMemo } from 'react'

type Props = { theme: 'dark' | 'light'; onToggle: () => void }

export default function ThemeToggle({ theme, onToggle }: Props) {
  const label = useMemo(() => (theme === 'dark' ? 'Dark' : 'Light'), [theme])
  return (
    <button
      onClick={onToggle}
      aria-label="Toggle theme"
      className="rounded-full border border-[#FFD700]/30 bg-black/50 px-3 py-2 text-sm text-[var(--foreground)] hover:bg-[#141414] data-[light=true]:bg-white/70 data-[light=true]:hover:bg-white"
      data-light={theme === 'light'}
    >
      {label}
    </button>
  )
}
