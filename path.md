# OMK System Path Map (Larry State)

This document inventories frontend-referenced routes, their backend implementations, and flags any phantom paths. It also maps components to endpoints and records decisions to create/keep/deprecate paths.

Date: 2025-10-24

---

## Methodology (Larry State)

- Read complete files before editing; traced full flow: Frontend constants → Components → Backend routers → Includes.
- Verified existence by grepping router files and opening sources in `backend/queen-ai/app/api/v1/`.
- Mapped each component call to exact backend handler and noted file:line ownership.
- Flagged phantom constants and proposed deprecations vs. create/keep decisions.
- Kept changes minimal and incremental; deferred runtime smoke tests to follow once backend is running.

---

## API Bases

- Backend base URL: `NEXT_PUBLIC_QUEEN_API_URL` (see `omk-frontend/.env.local` and `new-frontend/.env.local`)
- Shared constants: `shared/config/constants.ts` re-exported by:
  - `omk-frontend/lib/constants.ts`
  - `new-frontend/src/lib/constants.ts`
  - `API_ENDPOINTS.HEALTH = /health`
  - `API_ENDPOINTS.FRONTEND = /api/v1/frontend`
  - `API_ENDPOINTS.ADMIN = /api/v1/admin`
  - `API_ENDPOINTS.AUTH = /api/v1/auth`
  - `API_ENDPOINTS.MARKET = /api/v1/market`
  - `API_ENDPOINTS.OTC = /api/v1/otc`  ← see Phantom Paths
  - `API_ENDPOINTS.QUEEN_DEV = /api/v1/queen-dev`
  - `API_ENDPOINTS.CLAUDE = /api/v1/claude` ← see Phantom Paths
  - `API_ENDPOINTS.AUTONOMOUS = /api/v1/autonomous`
  - `API_ENDPOINTS.CONTRACTS = /api/v1/admin/contracts`
  - WebSockets: `WS_ENDPOINTS.ADMIN_HIVE|ADMIN_ANALYTICS|ADMIN_BEES = /ws/admin/*`

---

## Endpoint Inventory and Status

- Admin Analytics
  - GET `/api/v1/admin/analytics/overview` → `backend/queen-ai/app/api/v1/admin.py` ✔ exists
  - GET `/api/v1/admin/analytics/users` → `admin.py` ✔ exists
  - GET `/api/v1/admin/analytics/transactions` → `admin.py` ✔ exists

- Admin OTC
  - GET `/api/v1/admin/otc/requests` → `admin.py` ✔ exists
  - POST `/api/v1/admin/otc/requests/{id}/approve` → `admin.py` ✔ exists
  - POST `/api/v1/admin/otc/requests/{id}/reject` → `admin.py` ✔ exists

- Admin Data Pipeline
  - GET `/api/v1/admin/data-pipeline/status` → `admin.py` ✔ exists
  - POST `/api/v1/admin/data-pipeline/run` → `admin.py` ✔ exists
  - POST `/api/v1/admin/data-pipeline/schedule` → `admin.py` ✔ exists

- Admin Users
  - GET `/api/v1/admin/users` → `admin.py` ✔ exists
  - POST `/api/v1/admin/users/{id}/activate` → `admin.py` ✔ exists
  - POST `/api/v1/admin/users/{id}/deactivate` → `admin.py` ✔ exists

- Admin Hive Intelligence
  - GET `/api/v1/admin/hive/overview` → `admin.py` ✔ exists
  - GET `/api/v1/admin/hive/message-bus/stats` → `admin.py` ✔ exists
  - GET `/api/v1/admin/hive/board/stats` → `admin.py` ✔ exists
  - GET `/api/v1/admin/hive/bees/performance` → `admin.py` ✔ exists
  - GET `/api/v1/admin/hive/activity/live` → `admin.py` ✔ exists
  - WS `/ws/admin/hive` → `backend/queen-ai/app/api/v1/websocket.py` ✔ exists

- Admin Elastic
  - GET `/api/v1/admin/elastic/recent` → `admin.py` ✔ exists
  - POST `/api/v1/admin/elastic/search` → `admin.py` ✔ exists
  - POST `/api/v1/admin/elastic/rag` → `admin.py` ✔ exists

- Admin BigQuery
  - POST `/api/v1/admin/bigquery/query` → `admin.py` ✔ exists

- Queen Development
  - POST `/api/v1/queen-dev/chat` → `backend/queen-ai/app/api/v1/queen_dev.py` ✔ exists
  - POST `/api/v1/queen-dev/analyze-system` → `queen_dev.py` ✔ exists
  - GET `/api/v1/queen-dev/conversation-history` → `queen_dev.py` ✔ exists
  - GET `/api/v1/queen-dev/proposals` → `queen_dev.py` ✔ exists
  - POST `/api/v1/queen-dev/proposals/{id}/(deploy-sandbox|run-tests|approve|reject|apply|rollback)` → `queen_dev.py` ✔ exists
  - POST `/api/v1/admin/proposals/auto-fix/{id}` → `proposal_auto_fix.py` (included via prefix) ✔ exists

- Autonomous Development
  - Base: `/api/v1/autonomous` (prefix from `autonomous_dev.py` + main include) ✔ exists
  - POST `/api/v1/autonomous/fix-bug` → `autonomous_dev.py` ✔ exists
  - GET `/api/v1/autonomous/fixes` → `autonomous_dev.py` ✔ exists
  - GET `/api/v1/autonomous/fixes/{fix_id}` → `autonomous_dev.py` ✔ exists
  - POST `/api/v1/autonomous/fixes/{fix_id}/approve` → `autonomous_dev.py` ✔ exists
  - POST `/api/v1/autonomous/fixes/{fix_id}/reject` → `autonomous_dev.py` ✔ exists
  - POST `/api/v1/autonomous/index-codebase` → `autonomous_dev.py` ✔ exists
  - POST `/api/v1/autonomous/analyze-bug` → `autonomous_dev.py` ✔ exists
  - POST `/api/v1/autonomous/search-code` → `autonomous_dev.py` ✔ exists
  - GET `/api/v1/autonomous/status` → `autonomous_dev.py` ✔ exists

- Contracts
  - Base: `/api/v1/admin/contracts` (prefix via `contracts.py` + main include) ✔ exists
  - GET `/admin/contracts` → list ✔
  - GET `/admin/contracts/{name}/artifact` ✔
  - POST `/admin/contracts/compile` ✔
  - POST `/admin/contracts/{name}/deploy` ✔
  - POST `/admin/contracts/{deployment_id}/execute` ✔
  - GET `/admin/contracts/deployments` ✔
  - POST `/admin/contracts/batch-deploy` ✔
  - DELETE `/admin/contracts/deployments/{deployment_id}` ✔

- Auth / Market / Frontend
  - `/api/v1/auth/*` → `app/api/v1/auth.py` (included in `main.py`) ✔ present (not audited fully here)
  - `/api/v1/market/*` → `app/api/v1/market.py` ✔ present (not audited fully here)
  - `/api/v1/frontend/*` → `app/api/v1/frontend.py` ✔ present (not audited fully here)

---

## Frontend Component → Endpoint Map

- `UserManagement.tsx` → `/api/v1/admin/users*`
- `OTCRequestManager.tsx` → `/api/v1/admin/otc/requests*`
- `DataPipelineManager.tsx` → `/api/v1/admin/data-pipeline/*`
- `EnhancedAnalytics.tsx` → `/api/v1/admin/analytics/*`
- `HiveIntelligence.tsx` → HTTP fallback `/api/v1/admin/hive/*`, WS `/ws/admin/hive`
- `ElasticSearchDashboard.tsx` → `/api/v1/admin/elastic/*`
- `BigQueryAnalytics.tsx` → `POST /api/v1/admin/bigquery/query`
- `QueenDevelopmentHub.tsx` → `/api/v1/queen-dev/*`, `/api/v1/admin/proposals/auto-fix/{id}`
- `QueenDevelopment.tsx` → `/api/v1/queen-dev/*`
- `ContractDeployer.tsx` → `/api/v1/admin/contracts*`
- `AutonomousFixer.tsx` → `/api/v1/autonomous/*`
- `WidgetRenderer.tsx::UtilitiesWidget` → `GET ${API_ENDPOINTS.HEALTH}`, `GET ${API_ENDPOINTS.FRONTEND}/config`

New Frontend (site)
- `PriceTicker.tsx`, `BalanceBubble.tsx`, `WidgetRenderer.tsx` → `GET ${API_ENDPOINTS.MARKET}/omk`
- `lib/api/queen.ts::frontendAPI.chat(text)` → `POST ${API_ENDPOINTS.FRONTEND}/chat`
- `lib/api/queen.ts::queenAPI.submitOtc(...)` → `POST ${API_ENDPOINTS.FRONTEND}/otc-request` (Phase 2: ensure backend route)
- `lib/api/queen.ts::frontendAPI.getProperties()` → `GET ${API_ENDPOINTS.FRONTEND}/properties`
- `lib/api/queen.ts::frontendAPI.getProperty(id)` → `GET ${API_ENDPOINTS.FRONTEND}/properties/{id}`
- `lib/api/queen.ts::frontendAPI.getPublicConfig()` → `GET ${API_ENDPOINTS.FRONTEND}/config`
- Header/Modal wiring: `components/layout/AppHeader.tsx` + `components/widgets/WidgetHost.tsx` used in `app/page.tsx`, `app/invest/page.tsx`, `app/governance/page.tsx`, `app/portfolio/page.tsx`

## Recent Changes (Oct 2025):
- New Frontend now uses `API_ENDPOINTS.MARKET/omk` for price/info in `BalanceBubble.tsx`, `PriceTicker.tsx`, `WidgetRenderer.tsx`.
- Admin `AutonomousFixer.tsx` uses `API_ENDPOINTS.AUTONOMOUS` (removed hardcoded base).
- Dev proxy active: `new-frontend/next.config.ts` rewrites `/kingdom/*` → Admin on `:3001`.
- New widget: `utilities` (menu + chat intent) for health/config and env addresses. `PriceTicker.tsx` menu includes Utilities with i18n key `menu_utilities`.
- `QuickActions` component added to `app/page.tsx` and `app/invest/page.tsx` to open `private_sale`, `stake`, and `blocks` widgets.
- Added `UtilitiesWidget` route, menu label, intent mapping, and API helper additions.

---

## Phantom Paths and Decisions

- `API_ENDPOINTS.OTC = /api/v1/otc` → Phantom for admin portal
  - Decision: DEPRECATE in admin context. Use `/api/v1/admin/otc` everywhere.

- `API_ENDPOINTS.CLAUDE = /api/v1/claude` → Phantom (backend mounts Claude analysis under `/api/v1/admin`)
  - Decision: DEPRECATE this constant. If needed, add `API_ENDPOINTS.ADMIN_CLAUDE = /api/v1/admin` subpaths, or call existing admin endpoints directly.

- `router.py` include for `proposal_auto_fix` (added) may duplicate main inclusion
  - Reality: `main.py` already includes `proposal_auto_fix` under `/api/v1/admin/proposals`.
  - Decision: KEEP as harmless; primary inclusion is in `main.py`.

- Any hardcoded `http://localhost:8001` in admin components
  - Decision: REMOVE/REPLACE with `API_ENDPOINTS` (done for targeted files; run a final grep before release).

---

## Testing Status (static verification)

- Verified existence in source files (`admin.py`, `queen_dev.py`, `proposal_auto_fix.py`, `autonomous_dev.py`, `contracts.py`, `websocket.py`).
- Frontend wiring updated to call these paths via `API_ENDPOINTS`.
- Runtime tests pending: manual smoke across `/kingdom` tabs recommended after backend is running.

## Evidence References

- `backend/queen-ai/app/api/v1/admin.py` – analytics, users, otc, pipeline, hive, elastic, bigquery.
- `backend/queen-ai/app/api/v1/queen_dev.py` – queen-dev chat, proposals, actions.
- `backend/queen-ai/app/api/v1/proposal_auto_fix.py` – auto-fix route; included under `/api/v1/admin/proposals`.
- `backend/queen-ai/app/api/v1/autonomous_dev.py` – `/api/v1/autonomous/*` endpoints for autonomous fixing.
- `backend/queen-ai/app/api/v1/contracts.py` – contracts admin endpoints.
- `backend/queen-ai/app/api/v1/websocket.py` – `/ws/admin/*` real-time channels.
- `omk-frontend/lib/constants.ts` – `API_ENDPOINTS`, `WS_ENDPOINTS` definitions.

---

## Next Steps

1. Remove or repoint phantom constants in `omk-frontend/lib/constants.ts`:
   - Remove `CLAUDE`, `OTC` or document they are not used by admin.
2. Final grep for any leftover hardcoded base URLs in `/omk-frontend/app/kingdom/components/`.
3. Add small docs note in `blueprint.md` linking to this file for route matrix.
