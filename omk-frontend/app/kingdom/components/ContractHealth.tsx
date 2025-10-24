'use client';

import { useEffect, useState } from 'react';
import { usePublicClient } from 'wagmi';
import { formatUnits } from 'viem';
import { Shield, CheckCircle2, XCircle, Activity } from 'lucide-react';
import { DISPENSER_ADDRESS, DISPENSER_ABI, SUPPORTED_TOKENS } from '@/lib/contracts/dispenser';
import { PRIVATE_SALE_ABI, PRIVATE_SALE_ADDRESS } from '@/lib/contracts/privateSale';

export default function ContractHealth() {
  const publicClient = usePublicClient();
  const [loading, setLoading] = useState(true);
  const [disp, setDisp] = useState<any>(null);
  const [sale, setSale] = useState<any>(null);
  const isDev = process.env.NODE_ENV === 'development';
  const requiredEnv = [
    'NEXT_PUBLIC_OMK_TOKEN_ADDRESS',
    'NEXT_PUBLIC_PRIVATE_SALE_ADDRESS',
    'NEXT_PUBLIC_OMK_DISPENSER_ADDRESS',
    'NEXT_PUBLIC_USDT_ADDRESS',
    'NEXT_PUBLIC_USDC_ADDRESS',
  ];
  const optionalEnv = [
    'NEXT_PUBLIC_OMK_TOKEN_MAINNET',
    'NEXT_PUBLIC_OMK_TOKEN_SEPOLIA',
    'NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID',
  ];
  const missingRequired = requiredEnv.filter((k) => !process.env[k as keyof NodeJS.ProcessEnv]);
  const missingOptional = optionalEnv.filter((k) => !process.env[k as keyof NodeJS.ProcessEnv]);

  useEffect(() => {
    const load = async () => {
      if (!publicClient) return;
      try {
        const res: any = {};
        // Dispenser
        if (DISPENSER_ADDRESS && DISPENSER_ADDRESS !== '0x0000000000000000000000000000000000000000') {
          const ethAddr = SUPPORTED_TOKENS.ETH.address as `0x${string}`;
          const [ethSupported, ethPrice, omkPrice, available] = await Promise.all([
            publicClient.readContract({ address: DISPENSER_ADDRESS as `0x${string}`, abi: DISPENSER_ABI as any, functionName: 'supportedTokens', args: [ethAddr] }) as Promise<boolean>,
            publicClient.readContract({ address: DISPENSER_ADDRESS as `0x${string}`, abi: DISPENSER_ABI as any, functionName: 'tokenPricesUSD', args: [ethAddr] }) as Promise<bigint>,
            publicClient.readContract({ address: DISPENSER_ADDRESS as `0x${string}`, abi: DISPENSER_ABI as any, functionName: 'omkPriceUSD' }) as Promise<bigint>,
            publicClient.readContract({ address: DISPENSER_ADDRESS as `0x${string}`, abi: DISPENSER_ABI as any, functionName: 'getAvailableOMK' }) as Promise<bigint>,
          ]);
          res.dispenser = {
            address: DISPENSER_ADDRESS,
            ethSupported,
            ethPriceUSD8: ethPrice,
            omkPriceUSD8: omkPrice,
            availableOMK18: available,
          };
        }

        // Private Sale
        if (PRIVATE_SALE_ADDRESS) {
          const [status, minPurchase, usdtAccepted, usdcAccepted] = await Promise.all([
            publicClient.readContract({ address: PRIVATE_SALE_ADDRESS as `0x${string}`, abi: PRIVATE_SALE_ABI as any, functionName: 'getSaleStatus' }) as Promise<any>,
            publicClient.readContract({ address: PRIVATE_SALE_ADDRESS as `0x${string}`, abi: PRIVATE_SALE_ABI as any, functionName: 'MIN_PURCHASE' }) as Promise<bigint>,
            publicClient.readContract({ address: PRIVATE_SALE_ADDRESS as `0x${string}`, abi: PRIVATE_SALE_ABI as any, functionName: 'acceptedPaymentTokens', args: [SUPPORTED_TOKENS.USDT.address as `0x${string}`] }) as Promise<boolean>,
            publicClient.readContract({ address: PRIVATE_SALE_ADDRESS as `0x${string}`, abi: PRIVATE_SALE_ABI as any, functionName: 'acceptedPaymentTokens', args: [SUPPORTED_TOKENS.USDC.address as `0x${string}`] }) as Promise<boolean>,
          ]);
          const [_totalSold, _currentTier, _soldInCurrentTier, _currentPrice, _remainingInTier, _isActive] = status as any[];
          res.privateSale = {
            address: PRIVATE_SALE_ADDRESS,
            isActive: _isActive as boolean,
            currentTier: Number(_currentTier || 0),
            remainingInTier: BigInt(_remainingInTier || 0n) as bigint,
            currentPriceMills: BigInt(_currentPrice || 0n) as bigint,
            minPurchase18: minPurchase,
            usdtAccepted,
            usdcAccepted,
          };
        }

        setDisp(res.dispenser || null);
        setSale(res.privateSale || null);
      } catch (e) {
        console.error('ContractHealth load error:', e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [publicClient]);

  const Box = ({ children }: { children: any }) => (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5">{children}</div>
  );

  const Badge = ({ ok, label }: { ok: boolean; label: string }) => (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${ok ? 'bg-green-600/20 text-green-300' : 'bg-red-600/20 text-red-300'}`}>
      {ok ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
      {label}
    </span>
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-white">
        <Shield className="w-5 h-5 text-yellow-500" />
        <h3 className="text-lg font-semibold">Contract Health (Read-only)</h3>
      </div>
      {isDev && (missingRequired.length > 0 || missingOptional.length > 0) && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
          <div className="text-sm font-semibold text-yellow-300 mb-2">Dev Env Check</div>
          {missingRequired.length > 0 && (
            <div className="text-xs mb-2">
              <span className="font-semibold text-yellow-300">Missing required:</span>
              <ul className="list-disc list-inside mt-1">
                {missingRequired.map((k) => (
                  <li key={k} className="text-yellow-200">{k}</li>
                ))}
              </ul>
            </div>
          )}
          {missingOptional.length > 0 && (
            <div className="text-xs">
              <span className="font-semibold text-yellow-300">Missing optional:</span>
              <ul className="list-disc list-inside mt-1">
                {missingOptional.map((k) => (
                  <li key={k} className="text-yellow-200">{k}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {loading && (
        <div className="text-gray-400 text-sm flex items-center gap-2"><Activity className="w-4 h-4 animate-pulse" /> Loading...</div>
      )}

      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Box>
            <div className="text-sm text-gray-400 mb-2">OMK Dispenser</div>
            <div className="text-xs text-gray-500 mb-3">{DISPENSER_ADDRESS || 'not configured'}</div>
            {disp ? (
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">ETH Supported</span>
                  <Badge ok={!!disp.ethSupported} label={disp.ethSupported ? 'Yes' : 'No'} />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">ETH Price (USD)</span>
                  <span className="text-white font-medium">{Number(formatUnits(disp.ethPriceUSD8 || 0n, 8)).toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">OMK Price (USD)</span>
                  <span className="text-white font-medium">{Number(formatUnits(disp.omkPriceUSD8 || 0n, 8)).toFixed(4)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Available OMK</span>
                  <span className="text-white font-medium">{Number(formatUnits(disp.availableOMK18 || 0n, 18)).toLocaleString()}</span>
                </div>
              </div>
            ) : (
              <div className="text-sm text-gray-500">Dispenser not configured or unreachable</div>
            )}
          </Box>

          <Box>
            <div className="text-sm text-gray-400 mb-2">Private Sale</div>
            <div className="text-xs text-gray-500 mb-3">{PRIVATE_SALE_ADDRESS || 'not configured'}</div>
            {sale ? (
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Sale Active</span>
                  <Badge ok={!!sale.isActive} label={sale.isActive ? 'Active' : 'Inactive'} />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Current Tier</span>
                  <span className="text-white font-medium">{sale.currentTier}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Remaining in Tier</span>
                  <span className="text-white font-medium">{Number(formatUnits(sale.remainingInTier || 0n, 18)).toLocaleString()} OMK</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Min Purchase</span>
                  <span className="text-white font-medium">{Number(formatUnits(sale.minPurchase18 || 0n, 18)).toLocaleString()} OMK</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">USDT Accepted</span>
                  <Badge ok={!!sale.usdtAccepted} label={sale.usdtAccepted ? 'Yes' : 'No'} />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">USDC Accepted</span>
                  <Badge ok={!!sale.usdcAccepted} label={sale.usdcAccepted ? 'Yes' : 'No'} />
                </div>
              </div>
            ) : (
              <div className="text-sm text-gray-500">PrivateSale not configured or unreachable</div>
            )}
          </Box>
        </div>
      )}
    </div>
  );
}
