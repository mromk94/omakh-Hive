"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { useAccount, useConnect, useReadContracts, useWriteContract } from 'wagmi'
import { parseUnits } from 'viem'
import { queenAPI, frontendAPI } from '@/lib/api/queen'
import { API_ENDPOINTS } from '@/lib/constants'

type Props = {
  widgetKey: string;
  label: string;
  onPost?: (text: string) => void;
  onOpenWidget?: (key: string, label: string) => void;
};

const SectionTitle: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <h3 className="mb-2 text-lg font-semibold">{children}</h3>
);

const UtilitiesWidget: React.FC = () => {
  const { isConnected } = useAccount()
  const { writeContractAsync } = useWriteContract()
  const [claiming, setClaiming] = useState(false)
  const [claimMsg, setClaimMsg] = useState<string>('')
  const envPairs = [
    ['OMK Token', process.env.NEXT_PUBLIC_OMK_TOKEN_SEPOLIA],
    ['Private Sale', process.env.NEXT_PUBLIC_PRIVATE_SALE_ADDRESS],
    ['OMK Dispenser', process.env.NEXT_PUBLIC_OMK_DISPENSER_ADDRESS],
    ['Staking', process.env.NEXT_PUBLIC_STAKING_CONTRACT],
    ['Treasury', process.env.NEXT_PUBLIC_TREASURY_ADDRESS],
    ['Stablecoin', process.env.NEXT_PUBLIC_STABLECOIN_ADDRESS],
    ['Admin Treasury', process.env.NEXT_PUBLIC_ADMIN_TREASURY_ADDRESS],
  ] as Array<[string, any]>
  const copy = async (v?: string) => { try { if (v) await navigator.clipboard.writeText(v) } catch {} }
  return (
    <div>
      <div className="mb-2 flex items-center gap-2"><span className="icon-badge ring-glow">🛠️</span><SectionTitle>Utilities</SectionTitle></div>
      {/* Hive health banner */}
      <div className="rounded-2xl border border-[#FFD700]/30 bg-gradient-to-br from-yellow-500/10 to-amber-500/10 p-4">
        <div className="flex items-center gap-3">
          <div className="relative h-8 w-8 rounded-full bg-yellow-400/20">
            <div className="absolute inset-0 animate-ping rounded-full bg-yellow-400/20"></div>
            <div className="absolute inset-1 rounded-full bg-yellow-400/30"></div>
          </div>
          <div>
            <div className="font-semibold">Hive health</div>
            <div className="text-sm opacity-80">All bees alive and buzzing — all is well in the hive today!</div>
          </div>
        </div>
      </div>
      {/* Testnet Dispenser */}
      <div className="mt-3 rounded-xl border border-[#FFD700]/20 bg-black/20 p-3 text-sm">
        <div className="mb-1 flex items-center justify-between"><div className="font-medium">Testnet Dispenser</div><span className="text-xs opacity-70">Sepolia</span></div>
        <div className="opacity-80">Quickly claim testnet OMK for demos.</div>
        <div className="mt-2 flex items-center gap-2">
          <button
            onClick={async () => {
              const disp = process.env.NEXT_PUBLIC_OMK_DISPENSER_ADDRESS as `0x${string}` | undefined
              setClaimMsg('')
              if (!disp) { setClaimMsg('Dispenser address not configured.'); return }
              if (!isConnected) { setClaimMsg('Connect wallet first.'); return }
              try {
                setClaiming(true)
                await writeContractAsync({ address: disp, abi: [ { type:'function', stateMutability:'nonpayable', name:'claim', inputs:[], outputs:[] } ] as const, functionName: 'claim', args: [], gas: BigInt(300000) })
                setClaimMsg('Claim submitted. Check wallet activity.')
              } catch (e: any) {
                setClaimMsg(e?.shortMessage || e?.message || 'Claim failed')
              } finally { setClaiming(false) }
            }}
            className="rounded-full bg-gradient-to-br from-[#FFD700] to-[#F5A623] px-3 py-2 text-xs font-semibold text-black hover:brightness-95 disabled:opacity-50"
            disabled={claiming}
          >{claiming ? 'Claiming…' : 'Claim OMK'}</button>
          {claimMsg && <span className="text-xs opacity-80">{claimMsg}</span>}
        </div>
      </div>
      <div className="mt-3 grid gap-2">
        {envPairs.map(([label, val]) => (
          <div key={label} className="rounded-xl border border-[#FFD700]/15 bg-black/15 p-3 text-sm">
            <div className="flex items-center justify-between gap-2">
              <div className="opacity-80">{label}</div>
              <button onClick={() => copy(val)} className="rounded-full border border-[#FFD700]/25 px-2 py-0.5 text-[10px] hover:border-[#FFD700]/60">Copy</button>
            </div>
            <div className="mt-1 font-mono text-xs break-all opacity-70">{val || '—'}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

const Badge: React.FC<{ children: React.ReactNode; tone?: "emerald" | "amber" | "zinc" }>
  = ({ children, tone = "zinc" }) => (
  <span
    className={[
      "rounded-full border px-2 py-1 text-xs",
      tone === "emerald" && "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
      tone === "amber" && "border-amber-500/30 bg-amber-500/10 text-amber-300",
      tone === "zinc" && "border-zinc-500/30 bg-zinc-500/10 text-zinc-300",
    ].filter(Boolean).join(" ")}
  >
    {children}
  </span>
);

const Row: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => (
  <div className={["mt-3 flex flex-wrap items-center gap-2", className].filter(Boolean).join(" ")}>{children}</div>
);

const useOmkPrice = () => {
  const [price, setPrice] = useState<number | null>(null);
  useEffect(() => {
    const API = `${API_ENDPOINTS.MARKET}/omk`;
    let alive = true;
    const fetchOnce = async () => {
      try {
        const res = await fetch(API, { cache: "no-store" });
        if (!res.ok) return;
        const data = await res.json();
        const p = Number(data?.data?.price ?? data?.price);
        if (isFinite(p) && p > 0 && alive) setPrice(p);
      } catch {}
    };
    fetchOnce();
    return () => { alive = false; };
  }, []);
  return price;
};

const AboutOMKWidget: React.FC<{ onPost?: (text: string) => void }> = ({ onPost }) => (
  <div>
    <div className="mb-2 flex items-center gap-2"><span className="icon-badge ring-glow">🪙</span><SectionTitle>About OMK</SectionTitle></div>
    <p className="opacity-80">
      OMK is the native token of the OMK Hive ecosystem, powering access, rewards, and governance.
      It anchors private investment flows and aligns incentives across participants.
    </p>
    <Row>
      <button
        className="rounded-full border border-[#FFD700]/30 px-3 py-1.5 text-xs hover:border-[#FFD700]/60"
        onClick={() => onPost?.("Tell me how OMK is used.")}
        aria-label="Ask about OMK utility"
      >
        OMK Utility
      </button>
      <button
        className="rounded-full border border-[#FFD700]/30 px-3 py-1.5 text-xs hover:border-[#FFD700]/60"
        onClick={() => onPost?.("Who can get OMK and how?")}
        aria-label="Ask how to get OMK"
      >
        How to get OMK
      </button>
    </Row>
  </div>
  );

const AboutHiveWidget: React.FC<{ onPost?: (text: string) => void }> = ({ onPost }) => (
  <div>
    <div className="mb-2 flex items-center gap-2"><span className="icon-badge ring-glow">🐝</span><SectionTitle>About the HIVE</SectionTitle></div>
    <p className="opacity-80">
      The OMK Hive is a coordinated environment where investors, projects, and services connect.
      It blends on-chain verification with curated off-chain flows to make private deals seamless.
    </p>
    <Row>
      <Badge tone="amber">Curated Deals</Badge>
      <Badge tone="emerald">On-chain settlement</Badge>
      <Badge>AI Guidance</Badge>
    </Row>
  </div>
);

const TokenomicsWidget: React.FC = () => {
  const dist = [
    { label: 'Public Acquisition', pct: 40, color: '#FDE047' },
    { label: 'Founders', pct: 25, color: '#F59E0B' },
    { label: 'Treasury', pct: 12, color: '#A78BFA' },
    { label: 'Ecosystem', pct: 10, color: '#34D399' },
    { label: 'Private Investors', pct: 10, color: '#60A5FA' },
    { label: 'Advisors', pct: 2, color: '#F472B6' },
    { label: 'Breakswitch', pct: 1, color: '#F87171' },
  ]
  let acc = 0
  const grad = dist.map(d => {
    const start = acc; const end = acc + d.pct; acc = end; return `${d.color} ${start}% ${end}%`
  }).join(', ')
  return (
    <div>
      <div className="mb-2 flex items-center gap-2"><span className="icon-badge ring-glow">💎</span><SectionTitle>Tokenomics</SectionTitle></div>
      <div className="grid gap-3 sm:grid-cols-[220px,1fr] items-center">
        <div className="mx-auto h-40 w-40 rounded-full" style={{ background: `conic-gradient(${grad})` }}>
          <div className="relative h-full w-full">
            <div className="absolute inset-4 rounded-full bg-black/80 grid place-items-center text-sm opacity-80">1B OMK</div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          {dist.map(d => (
            <div key={d.label} className="rounded-xl border border-[#FFD700]/20 p-3 flex items-center gap-2">
              <span className="h-3 w-3 rounded-sm" style={{ background: d.color }}></span>
              <div className="flex-1">
                <div className="opacity-80">{d.label}</div>
                <div className="font-semibold">{d.pct}%</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

const ProfitCalculatorWidget: React.FC = () => {
  const price = useOmkPrice();
  const [usd, setUsd] = useState<string>("");
  const parsed = useMemo(() => Number(usd), [usd]);
  const omk = useMemo(() => {
    if (!price || !isFinite(parsed) || parsed <= 0) return 0;
    return parsed / price;
  }, [parsed, price]);
  return (
    <div>
      <div className="mb-2 flex items-center gap-2"><span className="icon-badge ring-glow">📈</span><SectionTitle>Profit Calculator</SectionTitle></div>
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="flex flex-col text-sm opacity-80">
          <span className="mb-1">Amount (USD)</span>
          <input
            value={usd}
            onChange={(e) => setUsd(e.target.value)}
            inputMode="decimal"
            placeholder="1000"
            aria-label="Amount in USD"
            className="rounded-xl border border-[#FFD700]/30 bg-transparent px-3 py-2 outline-none placeholder:opacity-40 focus:border-[#FFD700]/60"
          />
        </label>
        <div className="flex flex-col text-sm opacity-80">
          <span className="mb-1">Est. OMK</span>
          <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 px-3 py-2">
            {price ? `${omk.toFixed(2)} OMK @ $${price.toFixed(4)}` : "Fetching price…"}
          </div>
        </div>
      </div>
      <div className="mt-2 text-xs opacity-60">This is an estimate based on the latest price feed.</div>
    </div>
  );
};

const HowItWorksWidget: React.FC = () => {
  const [open, setOpen] = useState<{[k: string]: boolean}>({ s1: true, s2: false, s3: false });
  const Item: React.FC<{ id: string; title: string; body: string }> = ({ id, title, body }) => (
    <div className="rounded-xl border border-[#FFD700]/20">
      <button
        onClick={() => setOpen((o) => ({ ...o, [id]: !o[id] }))}
        aria-expanded={!!open[id]}
        className="flex w-full items-center justify-between px-3 py-2 text-left hover:bg-[var(--panel-2)]"
      >
        <span className="text-sm font-medium">{title}</span>
        <span className="text-xs opacity-60">{open[id] ? "Hide" : "Show"}</span>
      </button>
      {open[id] && <div className="px-3 pb-3 text-sm opacity-80">{body}</div>}
    </div>
  );
  return (
    <div>
      <div className="mb-2 flex items-center gap-2"><span className="icon-badge ring-glow">🧩</span><SectionTitle>How it works</SectionTitle></div>
      <div className="grid gap-2">
        <Item id="s1" title="Discover" body="Explore opportunities and guidance curated by the Hive and Queen." />
        <Item id="s2" title="Decide" body="Use data, diligence and simulations to make your informed choice." />
        <Item id="s3" title="Settle" body="Execute with transparent on-chain settlement where applicable." />
      </div>
    </div>
  );
};

const SimpleCard: React.FC<{ title: string; lines: string[] }> = ({ title, lines }) => (
  <div>
    <SectionTitle>{title}</SectionTitle>
    <ul className="list-disc space-y-1 pl-5 text-sm opacity-80">
      {lines.map((l) => (<li key={l}>{l}</li>))}
    </ul>
  </div>
);

// Minimal widgets to avoid runtime errors and keep UI consistent
const CommunityWidget: React.FC = () => (
  <div>
    <div className="mb-2 flex items-center gap-2"><span className="icon-badge ring-glow">🌐</span><SectionTitle>Community</SectionTitle></div>
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 text-sm">
      <a className="rounded-xl border border-[#1DA1F2]/30 bg-black/20 p-3 text-center hover:border-[#1DA1F2]/60" href="#" target="_blank">X</a>
      <a className="rounded-xl border border-indigo-400/30 bg-black/20 p-3 text-center hover:border-indigo-400/60" href="#" target="_blank">Discord</a>
      <a className="rounded-xl border border-pink-400/30 bg-black/20 p-3 text-center hover:border-pink-400/60" href="#" target="_blank">Instagram</a>
      <a className="rounded-xl border border-emerald-400/30 bg-black/20 p-3 text-center hover:border-emerald-400/60" href="#" target="_blank">TikTok</a>
      <a className="rounded-xl border border-red-400/30 bg-black/20 p-3 text-center hover:border-red-400/60" href="#" target="_blank">YouTube</a>
    </div>
  </div>
)

const BeesWidget: React.FC<{ onOpenWidget?: (key: string, label: string) => void }> = () => (
  <SimpleCard title="Queen & Bees" lines={["Autonomous services orchestrated by Queen.", "Security, governance, analytics and more."]} />
)

const FractionalizedAssetsWidget: React.FC = () => (
  <SimpleCard title="Fractionalized Assets" lines={["Tokenized real estate and curated assets."]} />
)

const TokenizationWidget: React.FC = () => (
  <SimpleCard title="Tokenization" lines={["On-chain representation with compliance-aware flows."]} />
)

const TreasuryWidget: React.FC = () => (
  <SimpleCard title="Treasury" lines={["Protocol-owned funds with safeguards."]} />
)

const PatternWidget: React.FC = () => (
  <SimpleCard title="Market Patterns" lines={["Signals and risk overlays informed by data."]} />
)

const PurchaseBeeWidget: React.FC = () => (
  <SimpleCard title="Purchase Bee" lines={["Executes curated buy flows with guardrails."]} />
)

const VisualizationWidget: React.FC = () => (
  <SimpleCard title="Visualization" lines={["Charts and dashboards coming soon."]} />
)

const RoadmapWidget: React.FC = () => (
  <SimpleCard title="Roadmap" lines={["Milestones, releases, and timelines."]} />
)

const DripScheduleWidget: React.FC = () => (
  <SimpleCard title="Drip Schedule" lines={["Adaptive LP top-ups governed by proposals."]} />
)

const InvestmentBlocksWidget: React.FC<{ onOpenWidget?: (key: string, label: string) => void }> = ({ onOpenWidget }) => {
  const sample = [
    { id: 0, name: 'Dubai Marina Apt', city: 'Dubai', price: 250000 },
    { id: 1, name: 'Mayfair Flat', city: 'London', price: 600000 },
    { id: 2, name: 'Upper East Apt', city: 'NYC', price: 900000 },
  ]
  const [propsList, setPropsList] = useState<Array<{ id: number | string; name: string; city?: string; price?: number; images?: string[] }>>(sample)
  const [loadingProps, setLoadingProps] = useState(true)
  const [errProps, setErrProps] = useState('')
  const [selected, setSelected] = useState<number>(0)
  const [slots, setSlots] = useState<number>(1)
  const [priceUsd, setPriceUsd] = useState<number>(sample[0].price!)
  const [show, setShow] = useState(false)
  useEffect(() => {
    let alive = true
    frontendAPI.getProperties().then((res) => {
      if (!alive) return
      const list = Array.isArray(res) ? res : (Array.isArray(res?.data) ? res.data : [])
      if (list.length) {
        const mapped = list.map((p: any, i: number) => ({
          id: p.id ?? i,
          name: p.name || p.title || `Property #${i+1}`,
          city: p.city || p.location || '',
          price: Number(p.price_usd ?? p.price ?? 0) || 0,
          images: Array.isArray(p.images) ? p.images : [],
        }))
        setPropsList(mapped)
        setSelected(0)
        setPriceUsd(mapped[0]?.price || 0)
      }
    }).catch((e) => {
      if (!alive) return
      setErrProps('Could not load properties. Showing samples.')
    }).finally(() => { if (alive) setLoadingProps(false) })
    return () => { alive = false }
  }, [])
  useEffect(() => { const p = propsList[selected]?.price || 0; setPriceUsd(p) }, [selected, propsList])
  const perSlot = useMemo(() => (priceUsd || 0) / 50, [priceUsd])
  const fee = useMemo(() => perSlot * 0.05, [perSlot])
  const total = useMemo(() => (perSlot + fee) * slots, [perSlot, fee, slots])
  return (
    <div>
      <div className="mb-2 flex items-center gap-2"><span className="icon-badge ring-glow">🏠</span><SectionTitle>Investment Blocks</SectionTitle></div>
      <p className="opacity-80 text-sm">
        Tokenized apartments sold fractionally in 50 slots per property. You can buy one or more slots.
        Each slot equals 1/50 of the property price. A 5% platform fee applies per slot.
      </p>
      {errProps && <div className="mt-2 rounded-xl border border-amber-400/30 bg-amber-500/10 p-3 text-xs text-amber-200">{errProps}</div>}
      <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {loadingProps ? (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="animate-pulse rounded-xl border border-[#FFD700]/15 bg-black/10 p-3">
              <div className="h-24 rounded-lg bg-[#111]"></div>
              <div className="mt-2 h-3 w-2/3 rounded bg-[#111]"></div>
              <div className="mt-1 h-3 w-1/3 rounded bg-[#111]"></div>
            </div>
          ))
        ) : (
          propsList.map((p, i) => (
            <button
              key={p.id}
              onClick={() => setSelected(i)}
              className={["rounded-xl border p-3 text-left text-xs transition", selected === i ? "border-[#FFD700]/60 bg-[#FFD700]/10" : "border-[#FFD700]/20 bg-black/20 hover:border-[#FFD700]/40"].join(' ')}
            >
              <div className="flex items-center gap-2"><span className="icon-badge">🏠</span><div className="font-medium">{p.name}</div></div>
              <div className="opacity-70">{p.city || '—'}</div>
              <div className="mt-1 font-mono">${(p.price || 0).toLocaleString()}</div>
            </button>
          ))
        )}
      </div>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <label className="flex flex-col text-sm opacity-80">
          <span className="mb-1">Property Price (USD)</span>
          <input
            value={priceUsd}
            onChange={(e) => setPriceUsd(Math.max(1, Number(e.target.value) || 0))}
            inputMode="decimal"
            className="rounded-xl border border-[#FFD700]/30 bg-transparent px-3 py-2 outline-none placeholder:opacity-40 focus:border-[#FFD700]/60"
          />
        </label>
        <label className="flex flex-col text-sm opacity-80">
          <span className="mb-1">Slots to buy (1–50)</span>
          <input
            value={slots}
            onChange={(e) => setSlots(Math.min(50, Math.max(1, Number(e.target.value) || 1)))}
            inputMode="numeric"
            className="rounded-xl border border-[#FFD700]/30 bg-transparent px-3 py-2 outline-none placeholder:opacity-40 focus:border-[#FFD700]/60"
          />
        </label>
      </div>
      <div className="mt-3 grid gap-2 text-sm">
        <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 p-3">
          <div className="flex items-center justify-between"><span>Per-slot base</span><span className="font-semibold">${perSlot.toFixed(2)}</span></div>
          <div className="mt-1 flex items-center justify-between opacity-80"><span>Per-slot fee (5%)</span><span>${fee.toFixed(2)}</span></div>
        </div>
        <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 p-3">
          <div className="flex items-center justify-between"><span>Total for {slots} slot(s)</span><span className="font-semibold">${total.toFixed(2)}</span></div>
        </div>
      </div>
      <Row className="justify-end">
        <button onClick={() => setShow(true)} className="rounded-full border border-[#FFD700]/40 px-3 py-2 text-xs hover:border-[#FFD700]/70">
          View details
        </button>
        <button className="rounded-full bg-gradient-to-br from-[#FFD700] to-[#F5A623] px-3 py-2 text-xs font-semibold text-black hover:brightness-95">
          Proceed to Invest
        </button>
      </Row>

      {show && (
        <div role="dialog" aria-modal="true" className="fixed inset-0 z-30 grid place-items-center bg-black/60 p-3">
          <div className="w-full max-w-2xl rounded-2xl border border-[#FFD700]/30 bg-[var(--panel)] p-4">
            <div className="flex items-center justify-between">
              <div className="text-lg font-semibold">{propsList[selected]?.name || 'Property'}</div>
              <button onClick={() => setShow(false)} className="rounded-full border border-[#FFD700]/25 px-3 py-1 text-xs hover:border-[#FFD700]/60">Close</button>
            </div>
            <div className="mt-2 text-sm opacity-70">{propsList[selected]?.city || '—'} • ${((propsList[selected]?.price || 0) as number).toLocaleString()}</div>
            <div className="mt-3 grid gap-2 sm:grid-cols-2">
              {propsList[selected]?.images && propsList[selected]!.images!.length > 0 ? (
                propsList[selected]!.images!.slice(0,2).map((src, k) => (
                  <img key={k} src={src} alt="Property" className="h-40 w-full rounded-xl border border-[#FFD700]/20 object-cover"/>
                ))
              ) : (
                <>
                  <div className="h-40 rounded-xl border border-[#FFD700]/20 bg-gradient-to-br from-[#1a1a1a] to-[#0e0e0e]"/>
                  <div className="h-40 rounded-xl border border-[#FFD700]/20 bg-gradient-to-br from-[#1a1a1a] to-[#0e0e0e]"/>
                </>
              )}
            </div>
            <div className="mt-3 grid grid-cols-3 gap-2 text-sm">
              <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 p-3"><div className="opacity-70">Slots total</div><div className="mt-1 text-lg font-semibold">50</div></div>
              <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 p-3"><div className="opacity-70">Slots left</div><div className="mt-1 text-lg font-semibold">{Math.max(0, 50 - Math.floor(priceUsd / 10000) - 3)}</div></div>
              <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 p-3"><div className="opacity-70">Est. ROI</div><div className="mt-1 text-lg font-semibold">8–12%</div></div>
            </div>
            <div className="mt-3 flex flex-wrap justify-end gap-2">
              <button onClick={() => onOpenWidget?.('profit_calc','Profit Calculator')} className="rounded-full border border-[#FFD700]/30 px-3 py-2 text-xs hover:border-[#FFD700]/60">Open Profit Calculator</button>
              <button onClick={() => { /* demo reserve: no backend call */ alert('Slot reserved (demo)'); }} className="rounded-full border border-emerald-400/40 px-3 py-2 text-xs text-emerald-300 hover:border-emerald-300">Reserve Slot</button>
              <button onClick={() => { setShow(false); onOpenWidget?.('private_sale','Private Sale') }} className="rounded-full bg-gradient-to-br from-[#FFD700] to-[#F5A623] px-3 py-2 text-xs font-semibold text-black hover:brightness-95">Proceed to Invest</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const PrivateSaleWidget: React.FC = () => {
  const [info, setInfo] = useState<{ active: boolean; price: number; stablecoin?: string; minPurchase?: number } | null>(null)
  const [step, setStep] = useState<'welcome'|'wallet'|'amount'|'contact'|'review'|'payment'|'submitted'>('welcome')
  const [omk, setOmk] = useState<string>("")
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [txHash, setTxHash] = useState('')
  const [err, setErr] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [realMode, setRealMode] = useState(false) // testnet demo by default
  const [stableSel, setStableSel] = useState<'USDT'|'USDC'>('USDT')
  const price = info?.price
  const sepoliaStable = (process.env.NEXT_PUBLIC_STABLECOIN_ADDRESS || '0x') as string
  const sepoliaTreasury = (process.env.NEXT_PUBLIC_TREASURY_ADDRESS || '0x') as string
  const adminTreasury = (process.env.NEXT_PUBLIC_ADMIN_TREASURY_ADDRESS || sepoliaTreasury) as string
  const mainnetUSDT = (process.env.NEXT_PUBLIC_MAINNET_USDT || '0x') as string
  const mainnetUSDC = (process.env.NEXT_PUBLIC_MAINNET_USDC || '0x') as string
  const stablecoin = realMode ? (stableSel === 'USDT' ? mainnetUSDT : mainnetUSDC) : (info?.stablecoin || sepoliaStable)
  const treasury = realMode ? adminTreasury : sepoliaTreasury
  const omkNum = Number(omk)
  const usd = price && isFinite(omkNum) && omkNum > 0 ? (omkNum * price) : 0

  useEffect(() => {
    let alive = true
    const API = `${API_ENDPOINTS.MARKET}/omk`
    fetch(API, { cache: 'no-store' })
      .then((r) => r.ok ? r.json() : null)
      .then((j) => {
        if (!alive) return
        const price = Number(j?.data?.price ?? j?.price)
        if (isFinite(price) && price > 0) setInfo({ active: true, price, stablecoin: j?.data?.stablecoin, minPurchase: j?.data?.minPurchase })
        else setInfo({ active: true, price: 0.10 })
      })
      .catch(() => { if (alive) setInfo({ active: true, price: 0.10 }) })
    return () => { alive = false }
  }, [])

  const { isConnected, address } = useAccount()
  const { connect, connectors } = useConnect()

  const canContinueAmount = () => isFinite(omkNum) && omkNum > 0 && usd > 0
  const canContinueContact = () => name.trim().length > 1 && /.+@.+/.test(email)
  const canContinuePayment = () => /^0x[0-9a-fA-F]{10,}$/.test(txHash.trim())

  return (
    <div>
      <div className="mb-2 flex items-center gap-2"><span className="icon-badge ring-glow">💎</span><SectionTitle>Private Sale</SectionTitle></div>
      <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 p-3 text-sm">
        <div className="mb-2 flex items-center justify-between">
          <div className="text-xs opacity-70">Mode</div>
          <button onClick={() => setRealMode(v => !v)} className="relative inline-flex h-7 w-40 items-center rounded-full border border-[#FFD700]/25 bg-black/30 p-0.5 text-[11px]">
            <span className={`flex-1 rounded-full py-1 text-center transition ${!realMode ? 'bg-[#FFD700] text-black' : 'text-[#FFD700]/80'}`}>Testnet demo</span>
            <span className={`flex-1 rounded-full py-1 text-center transition ${realMode ? 'bg-[#FFD700] text-black' : 'text-[#FFD700]/80'}`}>Real investment</span>
          </button>
        </div>
        <div className="grid grid-cols-[auto,1fr] items-center gap-2">
          <span>Status</span>
          <span className={`font-medium justify-self-end ${info?.active ? 'text-emerald-300' : 'text-rose-300'}`}>{info?.active ? 'Active' : 'Offline'}</span>
        </div>
        <div className="mt-1 grid grid-cols-[auto,1fr] items-center gap-2 opacity-80">
          <span>Current Price (per OMK)</span>
          <span className="justify-self-end">${(price ?? 0.10).toFixed(3)}</span>
        </div>
        <div className="mt-1 grid grid-cols-[auto,1fr] items-center gap-2 opacity-80">
          <span>Stablecoin</span>
          <span className="font-mono text-xs break-all text-right">{stablecoin}</span>
        </div>
        {realMode && (
          <div className="mt-2 flex justify-end gap-2">
            <button onClick={() => setStableSel('USDT')} className={`rounded-full border px-3 py-1 text-xs ${stableSel==='USDT' ? 'border-[#FFD700] bg-[#FFD700] text-black' : 'border-[#FFD700]/25 hover:border-[#FFD700]/60'}`}>USDT</button>
            <button onClick={() => setStableSel('USDC')} className={`rounded-full border px-3 py-1 text-xs ${stableSel==='USDC' ? 'border-[#FFD700] bg-[#FFD700] text-black' : 'border-[#FFD700]/25 hover:border-[#FFD700]/60'}`}>USDC</button>
          </div>
        )}
      </div>

      {step === 'welcome' && (
        <div className="mt-3 space-y-3 text-sm opacity-80">
          <p>Welcome to the private sale. You can acquire OMK using stablecoin, then submit your transaction hash for verification.</p>
          <div className="flex justify-end">
            <button onClick={() => setStep('wallet')} className="rounded-full bg-gradient-to-br from-[#FFD700] to-[#F5A623] px-4 py-2 text-xs font-semibold text-black hover:brightness-95">Get Started</button>
          </div>
        </div>
      )}

      {step === 'wallet' && (
        <div className="mt-3 space-y-3">
          {!isConnected ? (
            <div>
              <div className="mb-2 text-sm opacity-80">Connect your wallet</div>
              <div className="grid gap-2">
                {connectors.map((c: any) => (
                  <button key={c.uid} onClick={() => connect({ connector: c })} className="w-full rounded-xl border border-emerald-400/40 px-3 py-2 text-xs text-emerald-300 hover:border-emerald-300">Connect {c.name}</button>
                ))}
              </div>
            </div>
          ) : (
            <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 p-3 text-xs">Connected: <span className="font-mono">{address?.slice(0,6)}…{address?.slice(-4)}</span></div>
          )}
          <div className="flex justify-between">
            <button onClick={() => setStep('welcome')} className="rounded-full border border-[#FFD700]/25 px-4 py-2 text-xs hover:border-[#FFD700]/60">Back</button>
            <button onClick={() => setStep('amount')} className="rounded-full bg-gradient-to-br from-[#FFD700] to-[#F5A623] px-4 py-2 text-xs font-semibold text-black hover:brightness-95" disabled={!isConnected}>Continue</button>
          </div>
        </div>
      )}

      {step === 'amount' && (
        <div className="mt-3 space-y-3">
          <label className="flex flex-col text-sm opacity-80">
            <span className="mb-1">OMK to purchase</span>
            <input value={omk} onChange={(e) => setOmk(e.target.value)} inputMode="decimal" placeholder="100000" className="rounded-xl border border-[#FFD700]/30 bg-transparent px-3 py-2 outline-none placeholder:opacity-40 focus:border-[#FFD700]/60" />
          </label>
          <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 p-3 text-sm"><div className="flex items-center justify-between"><span>Estimated USD</span><span className="font-semibold">{usd ? `$${usd.toLocaleString(undefined, { maximumFractionDigits: 2 })}` : '—'}</span></div></div>
          {!realMode ? (
            <div className="rounded-xl border border-amber-400/30 bg-amber-500/10 p-3 text-xs text-amber-200">
              Testnet demo: ONLY SEND SEPOLIA TESTNET COINS. Do NOT send mainnet funds here.
            </div>
          ) : (
            <div className="rounded-xl border border-emerald-400/30 bg-emerald-500/10 p-3 text-xs text-emerald-200">
              Real investment on Ethereum Mainnet. Stablecoin will be sent to the Admin Treasury address.
            </div>
          )}
          <div className="text-xs opacity-60">Tiered pricing applies (0–100M @ $0.100 → $0.145). Actual cost depends on tier fill. This is an estimate.</div>
          <div className="flex justify-between">
            <button onClick={() => setStep('wallet')} className="rounded-full border border-[#FFD700]/25 px-4 py-2 text-xs hover:border-[#FFD700]/60">Back</button>
            <button onClick={() => canContinueAmount() && setStep('contact')} className="rounded-full bg-gradient-to-br from-[#FFD700] to-[#F5A623] px-4 py-2 text-xs font-semibold text-black hover:brightness-95" disabled={!canContinueAmount()}>Continue</button>
          </div>
        </div>
      )}

      {step === 'contact' && (
        <div className="mt-3 space-y-3">
          <label className="flex flex-col text-sm opacity-80">
            <span className="mb-1">Full name</span>
            <input value={name} onChange={(e) => setName(e.target.value)} className="rounded-xl border border-[#FFD700]/30 bg-transparent px-3 py-2 outline-none placeholder:opacity-40 focus:border-[#FFD700]/60" />
          </label>
          <label className="flex flex-col text-sm opacity-80">
            <span className="mb-1">Email</span>
            <input value={email} onChange={(e) => setEmail(e.target.value)} inputMode="email" className="rounded-xl border border-[#FFD700]/30 bg-transparent px-3 py-2 outline-none placeholder:opacity-40 focus:border-[#FFD700]/60" />
          </label>
          <div className="flex justify-between">
            <button onClick={() => setStep('amount')} className="rounded-full border border-[#FFD700]/25 px-4 py-2 text-xs hover:border-[#FFD700]/60">Back</button>
            <button onClick={() => canContinueContact() && setStep('review')} className="rounded-full bg-gradient-to-br from-[#FFD700] to-[#F5A623] px-4 py-2 text-xs font-semibold text-black hover:brightness-95" disabled={!canContinueContact()}>Continue</button>
          </div>
        </div>
      )}

      {step === 'review' && (
        <div className="mt-3 space-y-3 text-sm">
          <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 p-3">
            <div className="grid grid-cols-[auto,1fr] items-center gap-2"><span>OMK</span><span className="font-semibold justify-self-end">{omkNum.toLocaleString()}</span></div>
            <div className="mt-1 grid grid-cols-[auto,1fr] items-center gap-2"><span>Est. USD</span><span className="font-semibold justify-self-end">{usd ? `$${usd.toLocaleString(undefined, { maximumFractionDigits: 2 })}` : '—'}</span></div>
            <div className="mt-1 grid grid-cols-[auto,1fr] items-center gap-2 opacity-80"><span>Stablecoin</span><span className="font-mono text-xs break-all text-right">{stablecoin}</span></div>
            <div className="mt-1 grid grid-cols-[auto,1fr] items-center gap-2 opacity-80"><span>Treasury</span><span className="font-mono text-xs break-all text-right">{treasury}</span></div>
          </div>
          {!realMode ? (
            <div className="rounded-xl border border-amber-400/30 bg-amber-500/10 p-3 text-xs text-amber-200">
              You are in Testnet demo mode. Do NOT send mainnet funds.
            </div>
          ) : (
            <div className="rounded-xl border border-emerald-400/30 bg-emerald-500/10 p-3 text-xs text-emerald-200">
              You are in Real investment mode on Ethereum Mainnet.
            </div>
          )}
          <div className="flex justify-between">
            <button onClick={() => setStep('contact')} className="rounded-full border border-[#FFD700]/25 px-4 py-2 text-xs hover:border-[#FFD700]/60">Back</button>
            <button onClick={() => setStep('payment')} className="rounded-full bg-gradient-to-br from-[#FFD700] to-[#F5A623] px-4 py-2 text-xs font-semibold text-black hover:brightness-95">Proceed to Payment</button>
          </div>
        </div>
      )}

      {step === 'payment' && (
        <div className="mt-3 space-y-3 text-sm">
          <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 p-3">
            <div className="mb-1 text-xs opacity-80">Send payment to treasury wallet ({realMode ? 'Ethereum Mainnet' : 'Sepolia testnet'})</div>
            <div className="grid grid-cols-[auto,1fr] items-center gap-2"><span>Treasury</span><span className="font-mono text-[11px] break-all text-right">{treasury}</span></div>
            <div className="mt-1 grid grid-cols-[auto,1fr] items-center gap-2"><span>Stablecoin</span><span className="font-mono text-[11px] break-all text-right">{stablecoin}</span></div>
            <div className="mt-1 grid grid-cols-[auto,1fr] items-center gap-2"><span>Amount</span><span className="font-semibold justify-self-end">{usd ? `$${usd.toLocaleString(undefined, { maximumFractionDigits: 2 })}` : '—'}</span></div>
          </div>
          {!realMode && (
            <div className="text-xs text-rose-300">Testnet demo: ONLY SEND SEPOLIA TESTNET COINS. Mainnet funds sent here will be unrecoverable.</div>
          )}
          <label className="flex flex-col text-sm opacity-80">
            <span className="mb-1">Transaction Hash</span>
            <input value={txHash} onChange={(e) => setTxHash(e.target.value)} inputMode="text" placeholder="0x..." className="rounded-xl border border-[#FFD700]/30 bg-transparent px-3 py-2 outline-none placeholder:opacity-40 focus:border-[#FFD700]/60" />
          </label>
          {err && <div className="text-xs text-rose-300">{err}</div>}
          <div className="flex justify-between">
            <button onClick={() => setStep('review')} className="rounded-full border border-[#FFD700]/25 px-4 py-2 text-xs hover:border-[#FFD700]/60">Back</button>
            <button
              onClick={async () => {
                if (!canContinuePayment()) { setErr('Please enter a valid transaction hash.'); return }
                setErr('');
                setSubmitting(true)
                try {
                  await queenAPI.submitOtc({
                    address,
                    network: realMode ? 'mainnet' : 'sepolia',
                    omk: omkNum,
                    usd: usd || 0,
                    stablecoin,
                    treasury,
                    txHash: txHash.trim(),
                    name,
                    email,
                    mode: realMode ? 'real' : 'testnet',
                    stable: stableSel,
                  })
                  setStep('submitted')
                } catch (e: any) {
                  setErr(e?.message || 'Submission failed. Please try again.')
                } finally { setSubmitting(false) }
              }}
              className="rounded-full bg-gradient-to-br from-[#FFD700] to-[#F5A623] px-4 py-2 text-xs font-semibold text-black hover:brightness-95 disabled:opacity-50"
              disabled={submitting}
            >{submitting ? 'Submitting…' : 'Verify & Complete'}</button>
          </div>
          <div className="text-[11px] opacity-60">After submission, Queen will verify the transaction on-chain and process your request. Tokens are delivered per TGE/vesting schedule.</div>
        </div>
      )}

      {step === 'submitted' && (
        <div className="mt-3 space-y-2">
          <div className="rounded-xl border border-emerald-400/30 bg-emerald-500/10 p-3 text-sm text-emerald-300">Your request has been submitted for verification.</div>
          <div className="text-xs opacity-60">Ref: local. You will receive an email update after verification.</div>
        </div>
      )}
    </div>
  )
}

const GovernanceWidget: React.FC = () => {
  const gov = (process.env.NEXT_PUBLIC_GOVERNANCE_MANAGER_ADDRESS || process.env.GOVERNANCE_MANAGER_ADDRESS) as `0x${string}` | undefined
  const { data: govReads } = useReadContracts({
    allowFailure: true,
    contracts: gov ? [
      { address: gov, abi: [ { type:'function', stateMutability:'view', name:'proposalCount', inputs:[], outputs:[{type:'uint256'}] } ] as const, functionName: 'proposalCount' }
    ] : [],
    query: { enabled: !!gov }
  })
  const proposalCount = Number((govReads?.[0]?.result as bigint | undefined) ?? 0)
  const open = proposalCount || 0
  const passed = 12
  const treasuryUsd = 1250000
  const sample = { id: 'GIP-12', title: 'Enable Treasury Streaming for Operations', status: 'Open', endsIn: '2d 5h' }
  return (
    <div>
      <div className="mb-2 flex items-center gap-2"><span className="icon-badge ring-glow">🏛️</span><SectionTitle>Governance</SectionTitle></div>
      <div className="grid grid-cols-3 gap-2 text-sm">
        <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 p-3"><div className="opacity-70">Open Proposals</div><div className="mt-1 text-lg font-semibold">{open}</div></div>
        <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 p-3"><div className="opacity-70">Passed</div><div className="mt-1 text-lg font-semibold">{passed}</div></div>
        <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 p-3"><div className="opacity-70">Treasury</div><div className="mt-1 text-lg font-semibold">${treasuryUsd.toLocaleString()}</div></div>
      </div>
      <div className="mt-3 rounded-xl border border-[#FFD700]/20 bg-black/20 p-3 text-sm">
        <div className="flex items-center justify-between"><div className="font-medium">{sample.id}</div><span className="rounded-full border border-emerald-400/40 px-2 py-0.5 text-xs text-emerald-300">{sample.status}</span></div>
        <div className="mt-1 opacity-80">{sample.title}</div>
        <div className="mt-2 flex items-center justify-between text-xs opacity-70"><span>Ends in {sample.endsIn}</span><button className="rounded-full border border-[#FFD700]/30 px-3 py-1 text-xs hover:border-[#FFD700]/60">View details</button></div>
        {gov && <div className="mt-2 text-xs opacity-60">Manager: <span className="font-mono">{gov}</span></div>}
      </div>
    </div>
  )
}

const StakeWidget: React.FC = () => {
  const { address, isConnected } = useAccount()
  const token = process.env.NEXT_PUBLIC_OMK_TOKEN_SEPOLIA as `0x${string}` | undefined
  const staking = process.env.NEXT_PUBLIC_STAKING_CONTRACT as `0x${string}` | undefined
  const [amount, setAmount] = useState<string>('')
  const [stakingInfo, setStakingInfo] = useState<{ apr?: number, lock?: number, terms?: string } | null>(null)
  useEffect(() => {
    let alive = true
    frontendAPI.getPublicConfig().then((c: any) => {
      if (!alive) return
      const st = c?.config?.staking
      setStakingInfo({ apr: st?.apr, lock: st?.lock_days, terms: st?.terms })
    }).catch(() => {})
    return () => { alive = false }
  }, [])
  const { data: reads } = useReadContracts({
    allowFailure: true,
    contracts: [
      { abi: [ { type: 'function', stateMutability: 'view', name: 'balanceOf', inputs: [{ name: 'a', type: 'address' }], outputs: [{ type: 'uint256' }] } ] as const, address: token, functionName: 'balanceOf', args: [address as `0x${string}`] },
      { abi: [ { type: 'function', stateMutability: 'view', name: 'decimals', inputs: [], outputs: [{ type: 'uint8' }] } ] as const, address: token, functionName: 'decimals' },
      { abi: [ { type: 'function', stateMutability: 'view', name: 'allowance', inputs: [{name:'o',type:'address'},{name:'s',type:'address'}], outputs: [{ type: 'uint256' }] } ] as const, address: token, functionName: 'allowance', args: [address as `0x${string}`, staking as `0x${string}`] },
    ],
    query: { enabled: !!address && !!token && !!staking }
  })
  const bal = reads?.[0]?.result as bigint | undefined
  const dec = Number(reads?.[1]?.result ?? 18)
  const allowance = reads?.[2]?.result as bigint | undefined
  const amountOk = useMemo(() => {
    const n = Number(amount)
    return isFinite(n) && n > 0
  }, [amount])
  const stakeBig = useMemo(() => {
    try { return parseUnits(amount || '0', dec || 18) } catch { return BigInt(0) }
  }, [amount, dec])
  const hasAllowance = useMemo(() => allowance !== undefined && stakeBig > BigInt(0) && allowance! >= stakeBig, [allowance, stakeBig])
  const { writeContractAsync } = useWriteContract()
  const [errMsg, setErrMsg] = useState('')
  const badStaking = !staking || staking.toLowerCase() === '0xd4a3209ff4adf36d6e43eedc41a8c705e25708c1'.toLowerCase()
  return (
    <div>
      <div className="mb-2 flex items-center gap-2"><span className="icon-badge ring-glow">📦</span><SectionTitle>Stake</SectionTitle></div>
      {badStaking ? (
        <div className="rounded-xl border border-amber-400/30 bg-amber-500/10 p-3 text-sm text-amber-200">Staking is not configured. Set a valid `NEXT_PUBLIC_STAKING_CONTRACT` (Sepolia).</div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-xl border border-[#FFD700]/20 bg-black/20 p-3 text-sm">
            <div className="flex items-center justify-between"><span>Wallet balance</span><span className="font-semibold">{bal ? (Number(bal) / Math.pow(10, dec || 18)).toFixed(4) : '—'} OMK</span></div>
          </div>
          <label className="flex flex-col text-sm opacity-80">
            <span className="mb-1">Amount to stake</span>
            <input value={amount} onChange={(e) => setAmount(e.target.value)} inputMode="decimal" placeholder="1000" className="rounded-xl border border-[#FFD700]/30 bg-transparent px-3 py-2 outline-none placeholder:opacity-40 focus:border-[#FFD700]/60" />
          </label>
          {!hasAllowance ? (
            <button onClick={
              async () => {
                if (!amountOk) return;
                setErrMsg('')
                try { await writeContractAsync({ address: token!, abi: [ { type: 'function', stateMutability: 'nonpayable', name: 'approve', inputs: [{name:'s',type:'address'},{name:'a',type:'uint256'}], outputs: [{type:'bool'}] } ] as const, functionName: 'approve', args: [staking!, stakeBig] }) }
                catch (e: any) { setErrMsg(e?.shortMessage || e?.message || 'Approve failed') }
              }
            } className="rounded-full border border-[#FFD700]/40 px-3 py-2 text-xs hover:border-[#FFD700]/70">Approve</button>
          ) : (
            <button onClick={
              async () => {
                if (!amountOk) return;
                setErrMsg('')
                try { await writeContractAsync({ address: staking!, abi: [ { type: 'function', stateMutability: 'nonpayable', name: 'stake', inputs: [{name:'a',type:'uint256'}], outputs: [] } ] as const, functionName: 'stake', args: [stakeBig] }) }
                catch (e: any) { setErrMsg(e?.shortMessage || e?.message || 'Stake failed') }
              }
            } className="rounded-full bg-gradient-to-br from-[#FFD700] to-[#F5A623] px-3 py-2 text-xs font-semibold text-black hover:brightness-95">Stake</button>
          )}
          {errMsg && <div className="text-xs text-rose-300">{errMsg}</div>}
        </div>
      )}
    </div>
  );
};

const SecurityWidget: React.FC = () => (
  <div>
    <div className="mb-2 flex items-center gap-2"><span className="icon-badge ring-glow">🔐</span><SectionTitle>Security</SectionTitle></div>
    <ul className="list-disc space-y-1 pl-5 text-sm opacity-80">
      <li>Multisig approvals and timelocks for treasury-critical actions.</li>
      <li>On-chain logging of AI proposals and decisions.</li>
      <li>Audited contracts; sandboxed bees with usage caps.</li>
      <li>KYC and anti-whale measures at launch; rate-limited bridges.</li>
    </ul>
  </div>
);

const CrossChainWidget: React.FC = () => (
  <div>
    <div className="mb-2 flex items-center gap-2"><span className="icon-badge ring-glow">🔗</span><SectionTitle>Cross-chain</SectionTitle></div>
    <ul className="list-disc space-y-1 pl-5 text-sm opacity-80">
      <li>ETH is the master chain; SOL uses wrapped sOMK via lock/mint relayer.</li>
      <li>Single off-chain price engine for parity across chains initially.</li>
      <li>Deeper ETH pool to stabilize price; auto-rebalancer to manage deltas.</li>
      <li>Relayer starts multisig-based; decentralize validators as maturity grows.</li>
    </ul>
  </div>
);

const Renderer: React.FC<Props> = ({ widgetKey, label, onPost, onOpenWidget }) => {
  const content = useMemo(() => {
    switch (widgetKey) {
      case "about_omk":
        return <AboutOMKWidget onPost={onPost} />;
      case "about_hive":
        return <AboutHiveWidget onPost={onPost} />;
      case "tokenomics":
        return <TokenomicsWidget />;
      case "profit_calc":
        return <ProfitCalculatorWidget />;
      case "how":
        return <HowItWorksWidget />;
      case "blocks":
        return <InvestmentBlocksWidget onOpenWidget={onOpenWidget} />;
      case "private_sale":
        return <PrivateSaleWidget />;
      case "governance":
        return <GovernanceWidget />;
      case "stake":
        return <StakeWidget />;
      case "community":
        return <CommunityWidget />;
      case "bees":
        return <BeesWidget onOpenWidget={onOpenWidget} />;
      case "fractional_assets":
        return <FractionalizedAssetsWidget />;
      case "tokenization":
        return <TokenizationWidget />;
      case "treasury_bee":
        return <TreasuryWidget />;
      case "pattern_bee":
        return <PatternWidget />;
      case "purchase_bee":
        return <PurchaseBeeWidget />;
      case "visualization":
        return <VisualizationWidget />;
      case "roadmap":
        return <RoadmapWidget />;
      case "drip_schedule":
        return <DripScheduleWidget />;
      case "security":
        return <SecurityWidget />;
      case "cross_chain":
        return <CrossChainWidget />;
      case "utilities":
        return <UtilitiesWidget />;
      default:
        return (
          <div>
            <SectionTitle>{label}</SectionTitle>
            <p className="opacity-80">No content available.</p>
          </div>
        );
    }
  }, [widgetKey, label, onPost, onOpenWidget]);

  return (
    <div className="space-y-3">
      <div className="text-sm opacity-70">{label}</div>
      {content}
    </div>
  );
};

export default Renderer;
