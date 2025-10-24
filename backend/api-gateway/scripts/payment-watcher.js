/*
  Payment Watcher for Sepolia Private Sale
  - Listens for ERC20 Transfer events to the Treasury for the configured stablecoin
  - Optional TX hash verification utility

  Env required (backend/api-gateway/.env):
  - SEPOLIA_RPC_URL=... (HTTP) or SEPOLIA_WSS_URL=... (WebSocket preferred)
  - STABLECOIN_ADDRESS=0x8b81ffe0ad7bca69f05b18a603f4352d22cfa8b2
  - TREASURY_ADDRESS=0xd4a3209ff4ADf36d6e43eeDC41A8C705e25708c1
*/

const { ethers } = require("ethers");
require("dotenv").config();

const STABLE = (process.env.STABLECOIN_ADDRESS || "").toLowerCase();
const TREASURY = (process.env.TREASURY_ADDRESS || "").toLowerCase();
const WSS = process.env.SEPOLIA_WSS_URL;
const HTTP = process.env.SEPOLIA_RPC_URL;

if (!STABLE || !TREASURY) {
  console.error("Missing STABLECOIN_ADDRESS or TREASURY_ADDRESS in env");
  process.exit(1);
}

const provider = WSS
  ? new ethers.WebSocketProvider(WSS)
  : new ethers.JsonRpcProvider(HTTP);

const ERC20_ABI = [
  "event Transfer(address indexed from, address indexed to, uint256 value)",
  "function decimals() view returns (uint8)",
  "function symbol() view returns (string)",
];

const token = new ethers.Contract(STABLE, ERC20_ABI, provider);

async function main() {
  const [dec, sym] = await Promise.all([
    token.decimals().catch(() => 6),
    token.symbol().catch(() => "USDX"),
  ]);
  console.log(`Listening for ${sym} (decimals=${dec}) transfers to Treasury ${TREASURY} on Sepolia...`);

  token.on("Transfer", async (from, to, value, evt) => {
    try {
      if ((to || "").toLowerCase() !== TREASURY) return;
      const human = Number(value) / 10 ** dec;
      console.log(
        JSON.stringify(
          {
            type: "stablecoin_inflow",
            token: STABLE,
            symbol: sym,
            to: to,
            from: from,
            amount: human,
            txHash: evt.log.transactionHash,
            blockNumber: evt.log.blockNumber,
            timestamp: Date.now(),
          },
          null,
          2
        )
      );
    } catch (e) {
      console.error("Watcher error:", e);
    }
  });
}

// Optional: verify a specific tx hash passed as CLI arg
async function verifyTxHash(txHash) {
  const tx = await provider.getTransaction(txHash);
  if (!tx) {
    console.error("TX not found");
    process.exit(1);
  }
  const rcpt = await provider.getTransactionReceipt(txHash);
  const iface = new ethers.Interface(ERC20_ABI);
  let matched = [];
  for (const log of rcpt.logs || []) {
    if ((log.address || "").toLowerCase() !== STABLE) continue;
    try {
      const parsed = iface.parseLog({ topics: log.topics, data: log.data });
      if (parsed?.name === "Transfer") {
        const { from, to, value } = parsed.args;
        if ((to || "").toLowerCase() === TREASURY) {
          matched.push({ from, to, value: value.toString() });
        }
      }
    } catch (_) {}
  }
  console.log(JSON.stringify({ txHash, transfersToTreasury: matched }, null, 2));
}

const arg = process.argv[2];
if (arg && arg.startsWith("0x") && arg.length > 40) {
  verifyTxHash(arg).then(() => process.exit(0));
} else {
  main();
}
