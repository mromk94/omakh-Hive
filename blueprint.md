# OMK Hive – Project Blueprint

This document is a living systems blueprint for the OMK Hive platform. It captures the current architecture, code layout, integrations, runtime configuration, and operational guidance. Update iteratively as the system evolves.

---

## 1) High-Level Overview

- **Purpose**: Luxury fractional real-estate platform with conversational UX (Queen AI), OTC token sales, and admin operations (Kingdom).
- **Stack**:
  - Frontends: `new-frontend/` (Next 16, Wagmi), `omk-frontend/` (Next 14 admin portal)
  - Backend: `backend/queen-ai` (FastAPI, LLM orchestration, bee agents, contracts integration)
  - Chain: Ethereum Sepolia testnet (current), mainnet-ready
  - LLM Providers: Gemini (default), OpenAI, Anthropic via abstraction
  - Data/Integrations: ElasticSearch (optional), Market Data Agent

---

## 2) Monorepo Structure

- `backend/queen-ai/` – FastAPI app, orchestration, bees, contracts, admin + frontend APIs
- `new-frontend/` – New user-facing Next.js app (Chat, Invest, Wallet)
- `omk-frontend/` – Legacy full-featured app housing the mature Kingdom admin portal
- `contracts/` – Smart contract ABIs and build artifacts
- `infrastructure/`, `scripts/`, `docs/` – Ops and guidance
- Top-level audit docs: numerous `.md` files summarizing phases and prior work

---

## 3) Environments & Processes

- Local dev servers
  - Backend: `uvicorn main:app --host 0.0.0.0 --port 8001 --reload` in `backend/queen-ai/`
  - New Frontend: `npm run dev -- --port 3000` in `new-frontend/`
  - Legacy Admin: `npm run dev` (port 3001) in `omk-frontend/`
- Ports
  - 8001: Queen AI API
  - 3000: New user app
  - 3001: Admin Kingdom
  - Dev Proxy: `new-frontend/next.config.ts` proxies `/kingdom/*` → `http://localhost:3001/kingdom/*` for a single dev URL.
- Env files
  - `backend/queen-ai/.env` – LLM keys, RPC URLs, contract addresses
  - `new-frontend/.env.local` – Queen API URL, RPC, WalletConnect project, token/treasury addresses, `NEXT_PUBLIC_ADMIN_URL`
  - `omk-frontend/.env.local` – Queen API URL pointing to backend

- Start methods
  - Scripts (recommended)
    - Start: `./start-omakh.sh`
    - Stop: `./stop-omakh.sh`
    - Reboot: `./reboot-omakh.sh`
    - Behavior:
      - Backend at `http://localhost:8001`
      - Admin at `http://localhost:3001/kingdom`
      - New Frontend at `http://localhost:3000` (Admin via `/kingdom`)
      - Logs: `logs/queen-backend.log`, `logs/frontend.log`, `logs/new-frontend.log`
  - Manual
    - Backend (in `backend/queen-ai/`): `uvicorn main:app --host 0.0.0.0 --port 8001 --reload`
    - Admin (in `omk-frontend/`): `npm run dev -- -p 3001`
    - New Frontend (in `new-frontend/`): `npm run dev`

---

## 4) Backend (Queen AI)

- Entry: `backend/queen-ai/main.py`
  - FastAPI app with CORS + Double Submit CSRF middleware
  - Lifespan initializes DB, `QueenOrchestrator`, WebSocket bridges
  - Routers included under `/api/v1`: `frontend`, `admin`, `market`, `contracts`, `queen`, `queen-dev`, `autonomous_dev`, `notifications`, `proposal_auto_fix`, `websocket`
  - Health: `/health` returns init state and environment

- Orchestrator: `app/core/orchestrator.py`
  - Components: `BlockchainConnector`, `StateManager`, `LLMAbstraction`, `BeeManager`, `MessageBus`, `HiveInformationBoard`, optional `ElasticSearchIntegration`
  - Background loops: monitoring, decision making, staking-rewards, data pipeline
  - Chain operations: proposal submission to bridge/treasury, bee registry sync

- LLM Abstraction: `app/llm/abstraction.py`
  - Providers: Gemini, OpenAI, Anthropic; memory via `ConversationMemory`
  - Config via `DEFAULT_LLM_PROVIDER`, `{PROVIDER}_API_KEY`
  - Failover + simple cost tracking; vision supported via Gemini

- Bees (Agents): `app/bees/`
  - `manager.py`: registers all bees and enables LLM for `logic`, `pattern`, `governance`, `security`, `user_experience`
  - Core: `maths`, `security`, `data`, `treasury`, `blockchain`, `logic`, `pattern`
  - Ops: `purchase`, `liquidity_sentinel`, `stake_bot`, `tokenization`, `monitoring`
  - Sales: `private_sale`
  - Governance: `governance`
  - Viz: `visualization`
  - Bridge: `bridge`
  - Onboarding + UX: `onboarding`, `user_experience`

- APIs
  - Frontend API: `app/api/v1/frontend.py` (prefix `/api/v1/frontend`)
    - Greetings, Welcome, Theme, Onboarding, Chat, Public Config, Properties, Health
    - Chat path calls `user_experience` bee after security checks via `EnhancedSecurityBee`
  - Admin API: `app/api/v1/admin.py` (prefix `/api/v1/admin`)
    - Config: `/config`, `/config/otc-phase`, `/config/payment-methods`, `/config/treasury-wallets`, `/config/tge-date`
    - Queen control: `/queen/chat`, `/queen/status`, `/queen/bees`, `/queen/bee/execute`
    - Analytics: `/analytics/*`
    - OTC: `/otc/requests`, approve/reject, get-by-id
    - Hive Intelligence: message bus stats/history/health, board posts/stats/search, bees performance
    - Users: list, details, activate/deactivate, verify email, delete
    - Private Investors + TGE: register/distribute
  - Market API: `app/api/v1/market.py` (prefix `/api/v1/market`)
    - `/data`, `/omk`, `/crypto`, `/news`, `/config`, `/health`
    - Note: There is no `/omk-usdt` endpoint; new frontend currently requests `/api/v1/market/omk-usdt` which returns 404 (observed in logs). Update UI to use `/api/v1/market/omk` for price.

- Middleware: `app/middleware/csrf_protection.py`
  - Double Submit CSRF enabled
  - Dev exemptions include `/api/v1/frontend` and `/api/v1/admin` for local development

- Blockchain Connector: `app/utils/blockchain.py`
  - Web3 to ETH RPC; loads ABIs for BeeSpawner, GovernanceManager, TreasuryVault, EcosystemManager, OMKBridge, SystemDashboard, AdvisorsManager
  - Read ops (system metrics, bee info) + proposal/bee tx helpers

---

## 5) Frontends

### 5.1 New Frontend (`new-frontend/`)

- Framework: Next 16, React Server Components with client components for Wagmi/Wallet
- Providers: `src/components/web3/Providers.tsx` wraps Wagmi + React Query
- Web3 Config: `src/lib/web3/config.ts`
  - Chains: Sepolia
  - Transports: `NEXT_PUBLIC_ETH_RPC`
  - Connectors: Injected (MetaMask), WalletConnect (projectId, dynamic metadata.url), Coinbase Wallet
  - `ssr: false`, cookie storage
- App Shell
  - `src/components/layout/AppHeader.tsx` provides a consistent header with brand, `PriceTicker`, `ConnectButton`, and inline `BalanceBubble`.
  - `src/components/widgets/WidgetHost.tsx` is a modal host for rendering `WidgetRenderer` content (escape and backdrop close enabled).
  - Integrated on `src/app/page.tsx`, `src/app/invest/page.tsx`, `src/app/governance/page.tsx`, and `src/app/portfolio/page.tsx` to open widgets from the ticker menu.
  - `src/components/QuickActions.tsx` surfaces primary flows with animated icons: Buy OMK (`private_sale`), Stake (`stake`), and Buy Blocks (`blocks`). Used on `app/page.tsx` and `app/invest/page.tsx`.
- Wallet UX
  - `src/components/ConnectButton.tsx`: deduplicates connectors, labels WC as “WalletConnect / Trust Wallet”
  - `src/components/BalanceBubble.tsx`: dedupe + WC label; adds localStorage-driven toggle to hide WalletConnect for blocked environments; reads OMK balance via ERC20 `balanceOf` + `decimals`
- Chat
  - `src/app/chat/page.tsx`: initial greeting via `frontendAPI.chat()` (LLM-backed), not canned `getWelcome()`
  - Intent relay: `src/lib/intent/relay.ts` opens relevant widgets for common intents (private sale, profit calc, blocks, governance, stake, how it works, tokenomics, community, about OMK/Hive)
  - New intent: “utilities/health/config/addresses” → opens `utilities` widget.
- API client: `src/lib/api/queen.ts`
  - Base: `NEXT_PUBLIC_QUEEN_API_URL`
  - CSRF helper: prefetches `/frontend/greetings` or `/health` to get `X-CSRF-Token`; includes token header on POSTs
  - `submitOtc(...)` transforms UI payload to `{ wallet, allocation, price_per_token, payment_token, tx_hash }` for `/api/v1/frontend/otc-request`
  - Helpers added: `getProperties()` and `getProperty(id)` for Investment Blocks; `getPublicConfig()` for Utilities.
- Shared constants: `src/lib/constants.ts` re-exports from `shared/config/constants.ts` for `API_ENDPOINTS` and `WS_ENDPOINTS`.
- i18n: `src/lib/i18n.ts`
  - Bundles present: `en`, `es`, `fr`. To add: `zh`, `ja`, `ru`, `ar`, `pcm` per roadmap
- Admin link
  - `src/app/layout.tsx` shows a fixed “Admin” link
  - `NEXT_PUBLIC_ADMIN_URL` controls target; defaults to `/kingdom`
  - Duplicate `/kingdom` page in new-frontend has been removed to defer to legacy admin
  - Dev rewrites route `/kingdom/*` to the Admin app on port 3001 (see `next.config.ts`).

### 5.2 Legacy Admin (`omk-frontend/`)

- Purpose: Robust Kingdom admin portal under `app/kingdom/`
- Tabs/Components: `components/`
  - Deploy/Health: `ContractDeployer.tsx`, `ContractHealth.tsx`
  - Hive: `HiveIntelligence.tsx`, `HiveMonitor.tsx`
  - Analytics: `EnhancedAnalytics.tsx`, `ElasticSearchDashboard.tsx`, `BigQueryAnalytics.tsx`
  - Users/OTC: `UserManagement.tsx`, `OTCRequestManager.tsx`
  - Queen Dev: `QueenDevelopment.tsx`, `QueenDevelopmentHub.tsx`
  - Utilities: `TestnetUtilities.tsx`, `DataPipelineManager.tsx`
- Config: `lib/constants.ts`
  - Re-exports shared constants from `../../shared/config/constants.ts`.
  - `NEXT_PUBLIC_QUEEN_API_URL` defines all API endpoints; WS endpoints derived from base URL
- Auth: dev mode bypasses token; otherwise expects `auth_token` in localStorage and validates via `/api/v1/auth/me` (when available)
- Contract flows:
  - Admin lists/contracts via backend admin `/api/v1/admin/contracts*`
  - Deploy via Wagmi hooks (wallet signs); result saved back via `/api/v1/admin/contracts/save-deployment`

---

## 6) Chain & Contracts

- Current Network: Sepolia (testnet)
- Known deployed addresses (Sepolia) [from prior session memory]
  - `OMKToken`: `0x9654B4F2AC47BF46884d69BcCC636ef5A9c48632`
  - `PrivateSale`: `0xc801977eA4c3dAA93ca18e00aB07625923714484`
  - `PrivateInvestorRegistry`: `0x966E8C8C8a0a267Baf978A7cECBc1baB66b47939`
  - `OMKDispenser`: `0x6165050d8F9a09498D5A36Ea58BBcc9c0039889D`
- Stablecoin (test/demo): `0x8b81ffe0ad7bca69f05b18a603f4352d22cfa8b2` (6 decimals, $1.00)
- OTC payment policy
  - For “Real investment” mode, USD stablecoins must go to Admin Treasury: `0xd4a3209ff4ADf36d6e43eeDC41A8C705e25708c1`
  - Mainnet stablecoins for reference: USDT `0xdAC17F...D831ec7`, USDC `0xA0b869...6eB48`
  - Frontend env keys: `NEXT_PUBLIC_ADMIN_TREASURY_ADDRESS`, `NEXT_PUBLIC_MAINNET_USDT`, `NEXT_PUBLIC_MAINNET_USDC`

---

## 7) Security & Compliance

- CSRF
  - Double Submit CSRF middleware enabled; MVP dev exemptions for `/api/v1/frontend` and `/api/v1/admin`
  - Action: tighten in prod by removing exemptions and enforcing tokens/cookies across admin/frontend
- CORS
  - Configured via `settings.CORS_ORIGINS`
- Admin Auth
  - Current admin middleware accepts any Bearer token in dev (UNSAFE for prod)
  - Action: implement proper JWT/role claims and secure storage; wire `/api/v1/auth/*`
- LLM Safety
  - `EnhancedSecurityBee` validates inputs and filters outputs for chat endpoints; quarantines or blocks risky content

---

## 8) Wallets & Onboarding

- Wagmi connectors (new-frontend)
  - Deduped UI to remove duplicate MetaMask (“Injected” vs MetaMask)
  - Label WalletConnect as “WalletConnect / Trust Wallet”
  - Toggle to hide WC for blocked relay environments
- WalletConnect Issues
  - Common errors (publish/subscription failures) often due to relay blocked by extensions/corporate networks
  - Mitigations: `ssr: false`, dynamic `metadata.url`; manual fallback recommended (add copyable WC URI if needed)

---

## 9) Market Data

- Market API: `app/api/v1/market.py`
  - Use `/api/v1/market/omk` for OMK price and meta
  - UI updated to consume `/market/omk` in:
    - `new-frontend/src/components/BalanceBubble.tsx`
    - `new-frontend/src/components/PriceTicker.tsx`
    - `new-frontend/src/components/widgets/WidgetRenderer.tsx` (price + sale info)
    - `new-frontend/src/components/widgets/WidgetRenderer.tsx::UtilitiesWidget` shows backend health (`/health`) and public config (`/api/v1/frontend/config`).

---

## 10) Internationalization

- Present bundles: `en`, `es`, `fr`
- Roadmap bundles: `zh`, `ja`, `ru`, `ar`, `pcm`
- Guidance: centralize keys in `src/lib/i18n.ts`, ensure components only reference keys present across bundles

---

## 11) Observability & Data

- Structured logging via `structlog`
- Optional ElasticSearch integration (auto-initialized if credentials present) – used for bee activity logging and data queries
- Message Bus + Hive Board for internal telemetry and knowledge capture; exposed via admin APIs
- Data Pipeline Agent runs every 15 minutes for automated data collection and publishing

---

## 12) Deployment & CI Notes

- Target: Google Cloud Run for backend and frontend as per roadmap; do not block local dev
- Env requirements for backend
  - LLM keys: `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
  - RPC: `ETHEREUM_RPC_URL` (Infura HTTPS/WSS)
  - Contract addresses environment settings
- Frontend deploy
  - New user app can deploy independently; ensure `NEXT_PUBLIC_QUEEN_API_URL` points to backend’s public URL
  - Admin (legacy) can be deployed separately or proxied from new frontend via rewrites
- CI: To be aligned with GitHub Actions (repair requested earlier); always keep prod configs CSRF-enabled, admin auth enforced

---

## 13) Known Issues & Recommendations

- [Market endpoint mismatch] `BalanceBubble.tsx` requests `/market/omk-usdt` which returns 404. Update to `/market/omk` for price.
- [WalletConnect instability] Persisting in some networks. Add “Copy WC URI” fallback and optional hide WC default if repeated failures detected.
- [Admin auth hardening] Replace dev-any-bearer with JWT-based admin auth; remove CSRF exemptions for admin in prod.
- [i18n completion] Add missing bundles; validate keys across all language maps.
- [Unify `/kingdom`] Keep source of truth at `omk-frontend/app/kingdom/`. Link from new frontend via `NEXT_PUBLIC_ADMIN_URL` or configure rewrites.

---

## 14) Quick References (Files)

- Backend
  - `backend/queen-ai/main.py`
  - `backend/queen-ai/app/core/orchestrator.py`
  - `backend/queen-ai/app/llm/abstraction.py`
  - `backend/queen-ai/app/bees/manager.py`
  - `backend/queen-ai/app/api/v1/frontend.py`
  - `backend/queen-ai/app/api/v1/admin.py`
  - `backend/queen-ai/app/api/v1/market.py`
  - `backend/queen-ai/app/middleware/csrf_protection.py`
  - `backend/queen-ai/app/utils/blockchain.py`
- New Frontend
  - `new-frontend/src/app/chat/page.tsx`
  - `new-frontend/src/lib/api/queen.ts`
  - `new-frontend/src/lib/web3/config.ts`
  - `new-frontend/src/components/ConnectButton.tsx`
  - `new-frontend/src/components/BalanceBubble.tsx`
  - `new-frontend/src/lib/intent/relay.ts`
  - `new-frontend/src/app/layout.tsx`
- Legacy Admin
  - `omk-frontend/app/kingdom/page.tsx`
  - `omk-frontend/app/kingdom/components/*`
  - `omk-frontend/lib/constants.ts`

---

## 15) Architecture Diagram

```mermaid
flowchart LR
  subgraph Frontends
    NF[New Frontend (Next 16)] -->|HTTP| BE[/Queen AI FastAPI/]
    ADM[Legacy Admin (Next 14)] -->|HTTP & WS| BE
  end

  subgraph Backend (FastAPI)
    BE --> ORCH[QueenOrchestrator]
    ORCH --> LLM[LLM Abstraction]
    ORCH --> BUS[Message Bus]
    ORCH --> HIVE[Hive Info Board]
    ORCH --> BEES[Bees Manager]
    ORCH --> BLK[BlockchainConnector]
    ORCH --> ELS[Elastic (optional)]
  end

  BLK --> ETH[(Ethereum Sepolia)]

  NF -.-> WC[WalletConnect Relay]
  NF -.-> RPC[Infura RPC]
```

  ---

 ## 16) Next Steps (High-Impact)

- **Completed (recent)**
  - **Shared constants**: Added `shared/config/constants.ts` and re-exports in both apps.
  - **Dev proxy**: Added `/kingdom` rewrites in `new-frontend/next.config.ts`.
  - **Market endpoint fix**: Switched widgets to `/api/v1/market/omk`.

- **Planned**
  - **[WC fallback]** Add “Copy WalletConnect URI” in connect UI and auto-hide WC after repeated failures.
  - **[admin hardening]** Implement JWT admin auth; remove CSRF exemptions on prod.
  - **[i18n]** Add `zh`, `ja`, `ru`, `ar`, `pcm` bundles and ensure parity.
  - **[Blocks details]** Expand property detail modal using `frontendAPI.getProperty(id)` (images, availability, reserve slot action).
  - **[Staking UX]** Add rewards/unstake readouts when staking ABI is finalized.

---

## 17) Endpoint Reference (Condensed)

- **Frontend API** (`backend/queen-ai/app/api/v1/frontend.py`, prefix `/api/v1/frontend`)
  - `GET /greetings`
  - `POST /welcome`
  - `POST /theme-selection`
  - `POST /ask-account`
  - `POST /check-email`
  - `POST /register`, `POST /login`, `POST /logout`, `POST /verify-session`
  - `POST /chat` (validated via `EnhancedSecurityBee`, calls `user_experience`)
  - `POST /menu-interaction`, `POST /explain/{feature}`
  - `GET /quick-help`
  - `POST /welcome-back`, `POST /dashboard-intro`, `POST /wallet-balance`
  - `GET /config`
  - `GET /properties`, `GET /properties/{id}`
  - `GET /health`

- **Admin API** (`backend/queen-ai/app/api/v1/admin.py`, prefix `/api/v1/admin`)
  - Config: `GET /config`, `PUT /config`, `POST /config/otc-phase`, `POST /config/treasury-wallets`, `POST /config/payment-methods`, `POST /config/tge-date`
  - Queen: `POST /queen/chat`, `GET /queen/status`, `GET /queen/bees`, `POST /queen/bee/execute`
  - Analytics: `GET /analytics/overview`, `GET /analytics/users`, `GET /analytics/transactions`
  - OTC: `GET /otc/requests`, `POST /otc/requests`, `POST /otc/requests/{id}/approve`, `POST /otc/requests/{id}/reject`, `GET /otc/requests/{id}`
  - Hive: `GET /hive/message-bus/{stats|history|health}`, `GET /hive/board/{posts|stats|search}`, `GET /hive/bees/performance`, `GET /hive/activity/live`, `GET /hive/overview`
  - Users: `GET /users`, `GET /users/{id}`, `POST /users/{id}/activate`, `POST /users/{id}/deactivate`, `POST /users/{id}/verify-email`, `DELETE /users/{id}`
  - Private Investors & TGE: `GET/POST /private-investors`, `POST /private-investors/tge`, `POST /private-investors/{investor_id}/distribute`

- **Contracts API** (`backend/queen-ai/app/api/v1/contracts.py`)
  - `GET /api/v1/admin/contracts` – list `.sol` sources, compile state
  - `GET /api/v1/admin/contracts/{name}/artifact` – ABI/bytecode
  - `POST /api/v1/admin/contracts/compile` – compile via Hardhat
  - `POST /api/v1/admin/contracts/{name}/deploy` – prepare deployment record (frontend executes)
  - `POST /api/v1/admin/contracts/{deployment_id}/execute` – execute prepared deployment (Hardhat script)
  - `GET /api/v1/admin/contracts/deployments` – list records
  - `DELETE /api/v1/admin/contracts/deployments/{deployment_id}` – cancel prepared
  - `POST /api/v1/admin/contracts/save-deployment` – persist successful on-chain deployment

- **Market API** (`backend/queen-ai/app/api/v1/market.py`, prefix `/api/v1/market`)
  - `GET /data`, `GET /omk`, `GET /crypto`, `GET /news`, `GET /config`, `GET /health`
  - Note: there is no `/omk-usdt` path.

- **Auth API** (`backend/queen-ai/app/api/v1/auth.py`, prefix `/api/v1/auth`)
  - `POST /login`, `POST /register`, `GET /me`, `POST /logout`

- **Autonomous & Queen Dev**
  - `backend/queen-ai/app/api/v1/queen_dev.py` (prefix `/api/v1/queen-dev`): secure Claude chat, code proposals, system context, reboot manager
  - `backend/queen-ai/app/api/v1/autonomous_dev.py` (prefix `/api/v1/autonomous`): autonomous fixer, code search, codebase indexing

---

## 18) WebSocket Channels

- Router: `backend/queen-ai/app/api/v1/websocket.py`, registered in `main.py`.
- Connection manager with heartbeat; server-side broadcasts available for hive/analytics/bees.
- Legacy admin WS endpoints (derived from constants):
  - `ws://<backend-host>/ws/admin/hive`
  - `ws://<backend-host>/ws/admin/analytics`
  - `ws://<backend-host>/ws/admin/bees`

---

## 19) Auth, CSRF, and Security

- Auth (`/api/v1/auth/*`) provides JWT for user accounts via SQLAlchemy models (`app/database/*`).
- Admin verify in `admin.py` currently accepts any Bearer token in dev. Harden for production with JWT roles and stricter checks.
- CSRF: Double Submit Cookie middleware (`app/middleware/csrf_protection.py`)
  - Protected: POST/PUT/DELETE/PATCH
  - Dev exemptions: `/api/v1/frontend`, `/api/v1/admin`. Remove for production.
- LLM input/output security via `EnhancedSecurityBee` on chat/dev endpoints.

---

## 20) Database and Storage Model

- Hybrid storage during MVP:
  - JSON files in `backend/queen-ai/app/data/` for OTC requests, analytics, system config (`app/models/database.py`).
  - SQLAlchemy models for users under `app/database/*` with `DATABASE_URL` in settings.
- System config defaults include OTC phase, payment methods, treasury wallets, price, feature flags. Active flow via `get_active_otc_flow()`.
- Private investors in-memory list for MVP (`app/models/database.py`), TGE ops via admin endpoints.

---

## 21) Admin Portal Map (Legacy, `omk-frontend`)

- Entry `omk-frontend/app/kingdom/page.tsx` with tabs:
  - Overview, Hive Intelligence, Queen Development, System Analysis, Analytics, Data Pipeline, Elastic Search, BigQuery, Users, OTC, Config, Contracts, Testnet Utils.
- Notable components:
  - Contracts: `ContractDeployer.tsx` (lists/compiles, executes deploy, saves deployment)
  - Hive: `HiveIntelligence.tsx`, `HiveMonitor.tsx`
  - Queen Dev: `QueenDevelopment.tsx`, `QueenDevelopmentHub.tsx`
  - OTC: `OTCRequestManager.tsx`
  - Utilities: `DataPipelineManager.tsx`, `ElasticSearchDashboard.tsx`, `BigQueryAnalytics.tsx`, `UserManagement.tsx`, `TestnetUtilities.tsx`
- Config and endpoints wired via `omk-frontend/lib/constants.ts` to `NEXT_PUBLIC_QUEEN_API_URL`.

---

## 22) Deployment Profiles

- Local Development
  - Backend: Uvicorn reload at `:8001`
  - New frontend: Next dev at `:3000`
  - Legacy admin: Next dev at `:3001`
- Cloud Run (target)
  - Backend: expose `/health` and `/docs` for operational checks
  - Frontend(s): set `NEXT_PUBLIC_QUEEN_API_URL` to Cloud Run backend URL; consider static hosting or Next runtime on Cloud Run
- CI/CD
  - GitHub Actions repair requested; ensure environment secrets for LLM and RPC are set; no dev CSRF exemptions in prod.

---

## 23) Environment Variables (Reference)

- Backend (`backend/queen-ai/.env` → `app/config/settings.py`)
  - `DEFAULT_LLM_PROVIDER`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
  - `ETHEREUM_RPC_URL`, `ETHEREUM_CHAIN_ID`, optional `QUEEN_WALLET_PRIVATE_KEY`
  - Contract addresses: `OMK_TOKEN_ADDRESS`, `BEE_SPAWNER_ADDRESS`, `TREASURY_VAULT_ADDRESS`, `GOVERNANCE_MANAGER_ADDRESS`, `OMK_BRIDGE_ADDRESS`, `SYSTEM_DASHBOARD_ADDRESS`, etc.
  - CORS origins, learning/Elastic configs

- New Frontend (`new-frontend/.env.local`)
  - `NEXT_PUBLIC_QUEEN_API_URL`
  - `NEXT_PUBLIC_ETH_RPC`
  - `NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID`
  - `NEXT_PUBLIC_OMK_TOKEN_SEPOLIA`
  - OTC treasury and mainnet refs: `NEXT_PUBLIC_ADMIN_TREASURY_ADDRESS`, `NEXT_PUBLIC_MAINNET_USDT`, `NEXT_PUBLIC_MAINNET_USDC`
  - `NEXT_PUBLIC_ADMIN_URL` for Admin link

- Legacy Admin (`omk-frontend/.env.local`)
  - `NEXT_PUBLIC_QUEEN_API_URL`

---

## 24) Testing Checklist

- Backend
  - `GET /health` returns operational
  - `POST /api/v1/frontend/chat` returns LLM message, not canned text
  - Admin config routes update and persist (`/api/v1/admin/config`)
  - Market: `GET /api/v1/market/omk` returns price/data

- New Frontend
  - Chat greeting is LLM-driven on first load
  - Wallet connectors: unique MetaMask, WC/Trust, Coinbase, Phantom
  - BalanceBubble price fetch uses `/api/v1/market/omk` (no 404)
  - Admin link opens `NEXT_PUBLIC_ADMIN_URL`

- Legacy Admin
  - `/kingdom` loads; Overview/Hive/OTC/Contracts tabs call corresponding admin endpoints
  - Contract compile and deployment flow executes and persists deployment
  - WebSocket dashboards render without errors

---

## 25) Troubleshooting

- WalletConnect QR fails
  - Try Incognito, disable extensions; ensure relay allowed
  - Toggle “Hide WalletConnect” in `BalanceBubble`
  - Consider adding “Copy WC URI” fallback

- Canned chat replies
  - Ensure LLM keys present and `DEFAULT_LLM_PROVIDER` valid
  - `user_experience` bee must have `llm_enabled = True` (configured in `bees/manager.py`)

- Market price 404
  - Switch UI fetch from `/market/omk-usdt` to `/market/omk`

- Admin auth
  - Dev accepts any Bearer; configure JWT in prod; remove CSRF exemptions

---

## 26) Future Work

- Complete i18n bundles for `zh`, `ja`, `ru`, `ar`, `pcm` in `new-frontend/src/lib/i18n.ts`
- Add WC URI fallback, auto-hide after N failures, and telemetry for WC errors
- Harden admin auth and CSRF for production; enforce RBAC via JWT roles
- Expand Market Data Agent sources and caching; surface OMK price in UI widgets consistently
- Unify `/kingdom` routing via rewrites or a single host; publish both frontends with consistent branding
- Expand DB persistence replacing JSON stores for OTC/analytics with relational tables

---

## 27) Personality Gate (LLM System)

- **Purpose**: Ensure every LLM session (Gemini/OpenAI/Anthropic) starts with the Queen’s persona, prime directives, safety rules, and runtime context; reinforce on every turn to prevent drift.
- **Persona Source**: `QUEEN_PERSONALITY.md` (living document with identity, mission, tone, directives, routing map, safety rules, and system prompt template).
- **Scope**:
  - Session bootstrap: inject persona + environment summary + endpoints + protected files list.
  - Per-message reinforcement: prepend short role header and last 3 memory nuggets; detect drift and auto-reset tone.
  - Memory persistence: conversation, system, and role memories updated each turn.
- **Injection Points**:
  - `backend/queen-ai/app/integrations/claude_integration.py` → `_build_system_prompt(...)`.
  - `backend/queen-ai/app/llm/abstraction.py` → `_build_prompt_with_memory(...)` to optionally prepend a short persona header.
  - Optional: add `settings.PERSONA_FILE` and a small loader utility.

---

## 28) Queen Persona (Summary)

- **Identity**: Queen AI of the OMK Hive; senior architect/orchestrator who coordinates specialized bees, safeguards the system, and guides users/admins concisely.
- **Mission**: Stability and growth of the OMK ecosystem (OTC → TGE → liquidity → governance → RWA tokenization), with safe continuous improvement.
- **Prime Directives**:
  - Safety first (protected files, no secrets, CSRF/JWT, on-chain guardrails).
  - Truthful, cite real files/endpoints; minimal fluff; propose clear next actions.
  - Delegate to the right bee; persist memory of rules/decisions.
- **Tone**: Calm, precise, supportive; short paragraphs, bullet points; citations to code/paths.
- **Bee Routing (selected)**: UX→`UserExperienceBee`, Education→`TeacherBee`, Market/Pattern→`MarketDataAgent`/`PatternBee`, Math→`MathsBee`, Security→`EnhancedSecurityBee`, On-chain→`BlockchainBee`/`TreasuryBee`, Data/Insights→`DataBee`.
- Full charter and system prompt template: see `QUEEN_PERSONALITY.md`.

---

## 29) Implementation Plan (Incremental)

- **Step 1: Add persona file**
  - Created `QUEEN_PERSONALITY.md` with identity, directives, tone, routing, and a provider-agnostic system prompt template.
- **Step 2: Loader utility (backend)**
  - Add helper to read persona and render template with runtime snippets (env summary, feature flags, key endpoints, protected files).
  - Proposed env: `PERSONA_FILE=QUEEN_PERSONALITY.md` with project-root fallback.
- **Step 3: Inject in Claude integration**
  - Update `app/integrations/claude_integration.py::_build_system_prompt()` to prepend persona header + context from loader; keep existing admin/development context.
- **Step 4: Abstraction short header**
  - Update `app/llm/abstraction.py::_build_prompt_with_memory()` to optionally add a short role/tone header for non-Claude providers.
- **Step 5: Reinforcement hooks**
  - Pre-message: inject small role reminder + last 3 memory nuggets.
  - Post-message: store summary, todos, warnings; mark drift if tone deviates (tie into `EnhancedSecurityBee` if desired).
- **Step 6: Testing**
  - Verify admin/queen-dev chat responses include persona tone and citations.
  - Confirm normal frontend chat stays concise and action-focused.
  - Add toggle to disable persona gate in local dev if needed.

---

Updated: Expanded with endpoint references, websockets, auth/CSRF, storage model, admin map, deployment profiles, env refs, QA checklist, troubleshooting, and future work.

---

## 30) Recent Updates (Oct 2025)

- **Elastic & Chainlink**
  - `ELASTIC_CLOUD_ID` and `ELASTIC_API_KEY` configured in `backend/queen-ai/.env`.
  - Chainlink Sepolia feeds env added: `CHAINLINK_FEED_ETH_USD`, `CHAINLINK_FEED_BTC_USD`, `CHAINLINK_FEED_USDC_USD`.
  - `price_oracles.py` now reads feeds from env (or JSON map `CHAINLINK_FEEDS_JSON`).

- **BigQuery Data Pipeline**
  - Optional BigQuery load step added in `app/bees/data_pipeline_bee.py::_load_to_bigquery()`.
  - Dataset name configured via `settings.PIPELINE_BIGQUERY_DATASET` (default `fivetran_blockchain_data`).
  - Service account used via `GOOGLE_APPLICATION_CREDENTIALS` in `backend/queen-ai/.env`.
  - ADC quota project set to `omk-hive`.

- **Frontend BigQuery UI**
  - `omk-frontend/app/kingdom/components/BigQueryAnalytics.tsx` now uses env project/dataset:
    - `NEXT_PUBLIC_GCP_PROJECT_ID`, `NEXT_PUBLIC_PIPELINE_DATASET`.
  - Queries aligned to tables created by the pipeline (`ethereum_transactions`, `dex_pools`, `oracle_prices`).

- **Admin Wiring (incremental)**
  - Centralized API base via `omk-frontend/lib/constants.ts::API_ENDPOINTS` adopted in:
    - `OTCRequestManager.tsx` (list/approve/reject OTC requests).
    - `DataPipelineManager.tsx` (status/run/schedule pipeline).
    - `UserManagement.tsx` (list users, activate/deactivate actions).
    - `QueenDevelopmentHub.tsx` (chat, proposal auto-fix).
  - Backend exposed `proposal_auto_fix` under `/api/v1/admin/proposals/*` in `app/api/v1/router.py` to match frontend path.

---

## 31) Admin Wiring Plan and Status

For full, continuously-maintained route mappings and phantom-path decisions, see `path.md`.

Goal: eliminate hardcoded/mock data in `omk-frontend/app/kingdom/` and wire to backend APIs.

- **Wired (done)**
  - **OTC**: `OTCRequestManager.tsx` → `/api/v1/admin/otc/requests*`.
  - **Pipeline**: `DataPipelineManager.tsx` → `/api/v1/admin/data-pipeline/*`.
  - **Users**: `UserManagement.tsx` → `/api/v1/admin/users*` (activate/deactivate).
  - **Queen Dev**: `QueenDevelopmentHub.tsx` → `/api/v1/queen-dev/*` (chat) and `/api/v1/admin/proposals/auto-fix/*`.
  - **BigQuery Analytics**: env-driven project/dataset and table names.
  - **Dev proxy**: `new-frontend` proxies `/kingdom` to Admin (port 3001) during development.
  - **Shared config**: Admin constants re-exported from `shared/config/constants.ts`.

- **Next steps (incremental)**
  1. Replace remaining hardcoded URLs with `API_ENDPOINTS` in:
     - `HiveIntelligence.tsx` (HTTP fallback fetches).
     - `ElasticSearchDashboard.tsx`.
     - `QueenDevelopment.tsx` (non-Hub variant).
     - `ContractDeployer.tsx` and `ContractDeployer_OLD_BACKUP.tsx`.
     - `BigQueryAnalytics.tsx` execute endpoint (switch to `API_ENDPOINTS.ADMIN`).
  2. Verify WebSocket endpoints in `useWebSocket` hook align with `WS_ENDPOINTS` (admin hive/analytics/bees).
  3. Implement Uniswap V3 subgraph ingestion in `app/integrations/data_collectors/dex_pools.py` to populate `dex_pools`.
  4. Add Elastic indexing in pipeline steps to enrich `ElasticSearchDashboard.tsx` recent activities.
  5. Harden Admin Auth (JWT/roles) and remove CSRF exemptions before production.

- **Notes**
  - DEX pools may be empty until Uniswap ingestion is implemented.
  - Ensure frontend `.env.local` has `NEXT_PUBLIC_QUEEN_API_URL` pointing to backend.
