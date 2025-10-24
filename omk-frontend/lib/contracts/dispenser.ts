/**
 * OMK Dispenser Contract Integration
 * Automated token swaps controlled by Queen AI
 */

export const DISPENSER_ADDRESS = process.env.NEXT_PUBLIC_OMK_DISPENSER_ADDRESS || '0x0000000000000000000000000000000000000000';

export const DISPENSER_ABI = [
  // Read Functions
  {
    inputs: [
      { name: 'tokenIn', type: 'address' },
      { name: 'amountIn', type: 'uint256' }
    ],
    name: 'getSwapQuote',
    outputs: [
      { name: 'omkOut', type: 'uint256' },
      { name: 'valueUSD', type: 'uint256' }
    ],
    stateMutability: 'view',
    type: 'function'
  },
  {
    inputs: [{ name: '', type: 'address' }],
    name: 'supportedTokens',
    outputs: [{ name: '', type: 'bool' }],
    stateMutability: 'view',
    type: 'function'
  },
  {
    inputs: [{ name: '', type: 'address' }],
    name: 'tokenPricesUSD',
    outputs: [{ name: '', type: 'uint256' }],
    stateMutability: 'view',
    type: 'function'
  },
  {
    inputs: [],
    name: 'omkPriceUSD',
    outputs: [{ name: '', type: 'uint256' }],
    stateMutability: 'view',
    type: 'function'
  },
  {
    inputs: [],
    name: 'getAvailableOMK',
    outputs: [{ name: '', type: 'uint256' }],
    stateMutability: 'view',
    type: 'function'
  },
  {
    inputs: [{ name: 'user', type: 'address' }],
    name: 'getRemainingDailyLimit',
    outputs: [{ name: '', type: 'uint256' }],
    stateMutability: 'view',
    type: 'function'
  },
  
  // Write Functions
  {
    inputs: [
      { name: 'minOMKOut', type: 'uint256' },
      { name: 'recipient', type: 'address' }
    ],
    name: 'swapETHForOMK',
    outputs: [{ name: 'omkOut', type: 'uint256' }],
    stateMutability: 'payable',
    type: 'function'
  },
  {
    inputs: [
      { name: 'tokenIn', type: 'address' },
      { name: 'amountIn', type: 'uint256' },
      { name: 'minOMKOut', type: 'uint256' },
      { name: 'recipient', type: 'address' }
    ],
    name: 'swapTokenForOMK',
    outputs: [{ name: 'omkOut', type: 'uint256' }],
    stateMutability: 'nonpayable',
    type: 'function'
  },
  
  // Events
  {
    anonymous: false,
    inputs: [
      { indexed: true, name: 'user', type: 'address' },
      { indexed: true, name: 'tokenIn', type: 'address' },
      { name: 'amountIn', type: 'uint256' },
      { name: 'omkOut', type: 'uint256' },
      { name: 'recipient', type: 'address' }
    ],
    name: 'TokenSwapped',
    type: 'event'
  }
] as const;

// Supported tokens with their addresses
export const SUPPORTED_TOKENS = {
  ETH: {
    address: '0x0000000000000000000000000000000000000000', // Native ETH
    symbol: 'ETH',
    name: 'Ethereum',
    decimals: 18,
    icon: '💎',
    coingeckoId: 'ethereum'
  },
  USDT: {
    address: process.env.NEXT_PUBLIC_USDT_ADDRESS || '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    symbol: 'USDT',
    name: 'Tether USD',
    decimals: 6,
    icon: '💵',
    coingeckoId: 'tether'
  },
  USDC: {
    address: process.env.NEXT_PUBLIC_USDC_ADDRESS || '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    symbol: 'USDC',
    name: 'USD Coin',
    decimals: 6,
    icon: '💰',
    coingeckoId: 'usd-coin'
  }
} as const;

// ERC20 ABI (minimal for approvals and balances)
export const ERC20_ABI = [
  {
    inputs: [{ name: 'account', type: 'address' }],
    name: 'balanceOf',
    outputs: [{ name: '', type: 'uint256' }],
    stateMutability: 'view',
    type: 'function'
  },
  {
    inputs: [
      { name: 'spender', type: 'address' },
      { name: 'amount', type: 'uint256' }
    ],
    name: 'approve',
    outputs: [{ name: '', type: 'bool' }],
    stateMutability: 'nonpayable',
    type: 'function'
  },
  {
    inputs: [
      { name: 'owner', type: 'address' },
      { name: 'spender', type: 'address' }
    ],
    name: 'allowance',
    outputs: [{ name: '', type: 'uint256' }],
    stateMutability: 'view',
    type: 'function'
  }
] as const;
