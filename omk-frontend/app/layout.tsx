import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Web3Provider from '@/components/providers/Web3Provider'
import ThemeProvider from '@/components/providers/ThemeProvider'
import AppShell from '@/components/layout/AppShell'
import DevEnvBanner from '@/components/layout/DevEnvBanner'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'OMK Hive - Real Estate Investment Platform',
  description: 'Invest in fractional real estate and earn passive income powered by blockchain',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const requiredKeys = [
    'NEXT_PUBLIC_OMK_TOKEN_ADDRESS',
    'NEXT_PUBLIC_PRIVATE_SALE_ADDRESS',
    'NEXT_PUBLIC_OMK_DISPENSER_ADDRESS',
    'NEXT_PUBLIC_USDT_ADDRESS',
    'NEXT_PUBLIC_USDC_ADDRESS',
  ] as const

  const optionalKeys = [
    'NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID',
  ] as const

  const requiredMissing = requiredKeys.filter((k) => !process.env[k])
  const optionalMissing = optionalKeys.filter((k) => !process.env[k])

  return (
    <html lang="en">
      <body className={inter.className}>
        <ThemeProvider>
          <Web3Provider>
            {children}
            <AppShell />
            <DevEnvBanner requiredMissing={requiredMissing} optionalMissing={optionalMissing} />
          </Web3Provider>
        </ThemeProvider>
      </body>
    </html>
  )
}
