"use client";

import { useEffect, useMemo, useState } from "react";
import { useAccount, usePublicClient, useWalletClient } from "wagmi";
import { parseUnits, formatUnits } from "viem";
import { PRIVATE_SALE_ABI, PRIVATE_SALE_ADDRESS } from "@/lib/contracts/privateSale";
import { SUPPORTED_TOKENS, ERC20_ABI } from "@/lib/contracts/dispenser";
import { Toaster, toast } from 'react-hot-toast';

type PaymentSymbol = "USDT" | "USDC";

export default function PrivateSaleCard() {
  const { address, isConnected } = useAccount();
  const publicClient = usePublicClient();
  const { data: walletClient } = useWalletClient();

  const [minPurchase, setMinPurchase] = useState<string>("0");
  const [saleActive, setSaleActive] = useState<boolean>(false);
  const [isWhitelisted, setIsWhitelisted] = useState<boolean>(false);
  const [omkAmount, setOmkAmount] = useState<string>("");
  const [paymentUSD6, setPaymentUSD6] = useState<bigint>(0n);
  const [paymentToken, setPaymentToken] = useState<PaymentSymbol>("USDT");
  const [accepted, setAccepted] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  const saleAddr = PRIVATE_SALE_ADDRESS as `0x${string}` | undefined;
  const payMeta = useMemo(() => (SUPPORTED_TOKENS as any)[paymentToken], [paymentToken]);
  const payAddr = payMeta?.address as `0x${string}` | undefined;

  useEffect(() => {
    const load = async () => {
      try {
        if (!publicClient || !saleAddr) return;
        const [minP, active] = await Promise.all([
          publicClient.readContract({ address: saleAddr, abi: PRIVATE_SALE_ABI as any, functionName: "MIN_PURCHASE" }) as Promise<bigint>,
          publicClient.readContract({ address: saleAddr, abi: PRIVATE_SALE_ABI as any, functionName: "saleActive" }) as Promise<boolean>,
        ]);
        setMinPurchase(formatUnits(minP, 18));
        setSaleActive(active);
      } catch {}
    };
    load();
  }, [publicClient, saleAddr]);

  useEffect(() => {
    const loadInvestor = async () => {
      try {
        if (!publicClient || !saleAddr || !address) return;
        const res = (await publicClient.readContract({
          address: saleAddr,
          abi: PRIVATE_SALE_ABI as any,
          functionName: "getInvestorInfo",
          args: [address as `0x${string}`],
        })) as any[];
        const whitelist = Array.isArray(res) ? (res[3] as boolean) : false;
        setIsWhitelisted(whitelist);
      } catch {}
    };
    loadInvestor();
  }, [publicClient, saleAddr, address]);

  useEffect(() => {
    const checkAccepted = async () => {
      try {
        if (!publicClient || !saleAddr || !payAddr) return;
        const acc = (await publicClient.readContract({
          address: saleAddr,
          abi: PRIVATE_SALE_ABI as any,
          functionName: "acceptedPaymentTokens",
          args: [payAddr],
        })) as boolean;
        setAccepted(acc);
      } catch {}
    };
    checkAccepted();
  }, [publicClient, saleAddr, payAddr]);

  useEffect(() => {
    const calc = async () => {
      try {
        setError("");
        if (!publicClient || !saleAddr || !omkAmount) {
          setPaymentUSD6(0n);
          return;
        }
        const amount18 = parseUnits(omkAmount, 18);
        const pay = (await publicClient.readContract({
          address: saleAddr,
          abi: PRIVATE_SALE_ABI as any,
          functionName: "calculatePayment",
          args: [amount18],
        })) as bigint;
        setPaymentUSD6(pay);
      } catch {
        setPaymentUSD6(0n);
      }
    };
    calc();
  }, [publicClient, saleAddr, omkAmount]);

  const handlePurchase = async () => {
    try {
      setError("");
      if (!isConnected || !walletClient || !publicClient || !saleAddr || !payAddr) return;
      if (!saleActive) {
        setError("Sale is not active");
        return;
      }
      if (!isWhitelisted) {
        setError("You are not whitelisted");
        return;
      }
      if (!omkAmount || paymentUSD6 <= 0n) return;

      setLoading(true);
      const amount18 = parseUnits(omkAmount, 18);
      const maxPayment = (paymentUSD6 * 101n) / 100n; // +1%

      const allowance = (await publicClient.readContract({
        address: payAddr,
        abi: ERC20_ABI as any,
        functionName: "allowance",
        args: [address as `0x${string}`, saleAddr],
      })) as bigint;

      if (allowance < paymentUSD6) {
        const approveHash = await walletClient.writeContract({
          address: payAddr,
          abi: ERC20_ABI as any,
          functionName: "approve",
          args: [saleAddr, paymentUSD6],
          account: address as `0x${string}`,
        });
        await publicClient.waitForTransactionReceipt({ hash: approveHash });
      }

      const hash = await walletClient.writeContract({
        address: saleAddr,
        abi: PRIVATE_SALE_ABI as any,
        functionName: "purchaseTokens",
        args: [amount18, payAddr, maxPayment],
        account: address as `0x${string}`,
      });
      await publicClient.waitForTransactionReceipt({ hash });
      setLoading(false);
      toast.success(`Purchase submitted\nTx: ${hash}`);
      try { window.dispatchEvent(new Event('balances:refresh')); } catch {}
    } catch (e: any) {
      setLoading(false);
      setError(e?.shortMessage || e?.message || "Transaction failed");
    }
  };

  return (
    <div className="w-full max-w-xl bg-gradient-to-br from-purple-900/40 to-blue-900/40 rounded-2xl border border-purple-500/30 p-6">
      <Toaster position="top-right" />
      <h3 className="text-2xl font-bold text-white mb-4">Private Sale</h3>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-black/30 p-4 rounded-xl">
          <div className="text-sm text-gray-400">Status</div>
          <div className={`text-lg font-bold ${saleActive ? "text-green-400" : "text-red-400"}`}>{saleActive ? "Active" : "Inactive"}</div>
        </div>
        <div className="bg-black/30 p-4 rounded-xl">
          <div className="text-sm text-gray-400">Whitelist</div>
          <div className={`text-lg font-bold ${isWhitelisted ? "text-green-400" : "text-red-400"}`}>{isWhitelisted ? "Approved" : "Required"}</div>
        </div>
      </div>

      <div className="mb-4">
        <label className="block text-sm text-gray-300 mb-2">OMK Amount (min {minPurchase})</label>
        <input
          type="number"
          value={omkAmount}
          onChange={(e) => setOmkAmount(e.target.value)}
          placeholder={minPurchase}
          className="w-full px-4 py-3 bg-black/30 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 outline-none"
        />
      </div>

      <div className="mb-4">
        <label className="block text-sm text-gray-300 mb-2">Payment Token</label>
        <div className="grid grid-cols-2 gap-2">
          {(["USDT", "USDC"] as const).map((sym) => (
            <button
              key={sym}
              onClick={() => setPaymentToken(sym)}
              className={`py-2 rounded-lg font-semibold ${paymentToken === sym ? "bg-green-600 text-white" : "bg-gray-800 text-gray-300"}`}
            >
              {sym}
            </button>
          ))}
        </div>
        {!accepted && <div className="text-xs text-red-400 mt-2">Selected token not accepted by sale</div>}
      </div>

      <div className="bg-black/30 p-4 rounded-xl mb-4">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <span>Payment (USD, 6 decimals)</span>
          <span className="text-white font-bold">{paymentUSD6 > 0n ? `${Number(formatUnits(paymentUSD6, 6)).toLocaleString()} USD` : "-"}</span>
        </div>
      </div>

      {error && <div className="mb-3 text-sm text-red-400">{error}</div>}

      <button
        onClick={handlePurchase}
        disabled={loading || !isConnected || !saleActive || !isWhitelisted || !omkAmount || !accepted}
        className="w-full py-3 bg-gradient-to-r from-yellow-500 to-yellow-600 disabled:from-gray-700 disabled:to-gray-700 text-black disabled:text-gray-400 font-bold rounded-lg"
      >
        {loading ? "Processing..." : "Purchase"}
      </button>
    </div>
  );
}
