import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatAddress(address: string, chars = 4): string {
  return `${address.slice(0, chars + 2)}...${address.slice(-chars)}`
}

export function formatNumber(num: number, decimals = 2): string {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num)
}

export function formatCurrency(value: number, decimals: number = 2): string {
  // For large numbers, use abbreviations
  const absValue = Math.abs(value);
  
  if (absValue >= 1e12) {
    // Trillions
    return `$${(value / 1e12).toFixed(2)}T`;
  } else if (absValue >= 1e9) {
    // Billions
    return `$${(value / 1e9).toFixed(2)}B`;
  } else if (absValue >= 1e6) {
    // Millions
    return `$${(value / 1e6).toFixed(2)}M`;
  } else if (absValue >= 1e3) {
    // Thousands
    return `$${(value / 1e3).toFixed(2)}K`;
  }
  
  // Regular formatting for smaller numbers
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}
