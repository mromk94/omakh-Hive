import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Web3Provider from '@/components/providers/Web3Provider'
import ThemeProvider from '@/components/providers/ThemeProvider'
import AppShell from '@/components/layout/AppShell'

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
  return (
    <html lang="en">
      <body className={inter.className}>
        <ThemeProvider>
          <Web3Provider>
            {children}
            <AppShell />
          </Web3Provider>
        </ThemeProvider>
      </body>
    </html>
  )
}
