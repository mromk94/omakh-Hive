'use client'
import Renderer from '@/components/widgets/WidgetRenderer'

type Props = {
  open: boolean
  widgetKey: string
  label: string
  onClose: () => void
  onPost?: (text: string) => void
  onOpenWidget?: (key: string, label: string) => void
}

export default function WidgetHost({ open, widgetKey, label, onClose, onPost, onOpenWidget }: Props) {
  if (!open) return null

  const handleBackdropClick: React.MouseEventHandler<HTMLDivElement> = (e) => {
    if (e.target === e.currentTarget) onClose()
  }

  const handleKeyDown: React.KeyboardEventHandler<HTMLDivElement> = (e) => {
    if (e.key === 'Escape') onClose()
  }

  return (
    <div role="dialog" aria-modal="true" className="fixed inset-0 z-50 grid place-items-center bg-black/60 p-3" onClick={handleBackdropClick} onKeyDown={handleKeyDown}>
      <div className="w-full max-w-[92vw] md:max-w-3xl rounded-2xl border border-[#FFD700]/30 bg-[var(--panel)] p-4 max-h-[85vh] overflow-y-auto" role="document">
        <div className="flex items-center justify-between">
          <div className="text-lg font-semibold">{label}</div>
          <div className="flex items-center gap-2">
            <button onClick={onClose} className="rounded-full border border-[#FFD700]/25 px-3 py-1 text-xs hover:border-[#FFD700]/60">Close</button>
          </div>
        </div>
        <div className="mt-3">
          <Renderer widgetKey={widgetKey} label={label} onPost={onPost} onOpenWidget={onOpenWidget} />
        </div>
      </div>
    </div>
  )
}
