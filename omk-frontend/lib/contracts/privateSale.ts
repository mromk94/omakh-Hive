export const PRIVATE_SALE_ADDRESS = process.env.NEXT_PUBLIC_PRIVATE_SALE_ADDRESS as `0x${string}` | undefined;

export const PRIVATE_SALE_ABI = [
  // View
  { inputs: [], name: 'MIN_PURCHASE', outputs: [{ type: 'uint256' }], stateMutability: 'view', type: 'function' },
  { inputs: [], name: 'saleActive', outputs: [{ type: 'bool' }], stateMutability: 'view', type: 'function' },
  { inputs: [{ name: 'amount', type: 'uint256' }], name: 'calculatePayment', outputs: [{ type: 'uint256' }], stateMutability: 'view', type: 'function' },
  { inputs: [{ name: 'investor', type: 'address' }], name: 'getInvestorInfo', outputs: [
      { name: 'totalPurchased', type: 'uint256' },
      { name: 'totalPaidUSD', type: 'uint256' },
      { name: 'remainingAllocation', type: 'uint256' },
      { name: 'isWhitelisted', type: 'bool' }
    ], stateMutability: 'view', type: 'function' },
  { inputs: [{ name: '', type: 'address' }], name: 'acceptedPaymentTokens', outputs: [{ type: 'bool' }], stateMutability: 'view', type: 'function' },
  { inputs: [], name: 'getSaleStatus', outputs: [
      { name: '_totalSold', type: 'uint256' },
      { name: '_currentTier', type: 'uint256' },
      { name: '_soldInCurrentTier', type: 'uint256' },
      { name: '_currentPrice', type: 'uint256' },
      { name: '_remainingInTier', type: 'uint256' },
      { name: '_isActive', type: 'bool' }
    ], stateMutability: 'view', type: 'function' },
  // Write
  { inputs: [
      { name: 'amount', type: 'uint256' },
      { name: 'paymentToken', type: 'address' },
      { name: 'maxPayment', type: 'uint256' }
    ], name: 'purchaseTokens', outputs: [], stateMutability: 'nonpayable', type: 'function' },
] as const;
