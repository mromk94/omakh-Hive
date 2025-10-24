/**
 * Shared API and WebSocket endpoint constants for OMK apps
 */

declare const process: any;

export const QUEEN_API_URL =
  process.env.NEXT_PUBLIC_QUEEN_API_URL ||
  'https://omk-queen-ai-475745165557.us-central1.run.app';

export const QUEEN_WS_URL = QUEEN_API_URL
  .replace('https://', 'wss://')
  .replace('http://', 'ws://');

export const API_ENDPOINTS = {
  HEALTH: `${QUEEN_API_URL}/health`,
  FRONTEND: `${QUEEN_API_URL}/api/v1/frontend`,
  ADMIN: `${QUEEN_API_URL}/api/v1/admin`,
  AUTH: `${QUEEN_API_URL}/api/v1/auth`,
  MARKET: `${QUEEN_API_URL}/api/v1/market`,
  OTC: `${QUEEN_API_URL}/api/v1/otc`, // Note: not used by admin; prefer ADMIN/otc
  QUEEN_DEV: `${QUEEN_API_URL}/api/v1/queen-dev`,
  CLAUDE: `${QUEEN_API_URL}/api/v1/claude`, // Note: admin Claude endpoints live under ADMIN
  AUTONOMOUS: `${QUEEN_API_URL}/api/v1/autonomous`,
  CONTRACTS: `${QUEEN_API_URL}/api/v1/admin/contracts`,
} as const;

export const WS_ENDPOINTS = {
  ADMIN_HIVE: `${QUEEN_WS_URL}/ws/admin/hive`,
  ADMIN_ANALYTICS: `${QUEEN_WS_URL}/ws/admin/analytics`,
  ADMIN_BEES: `${QUEEN_WS_URL}/ws/admin/bees`,
} as const;
