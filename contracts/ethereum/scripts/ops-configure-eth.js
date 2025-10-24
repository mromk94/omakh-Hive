import { ethers } from "ethers";
import dotenv from "dotenv";

dotenv.config();

async function main() {
  const DISPENSER = process.env.OMK_DISPENSER_ADDRESS || "0x6165050d8F9a09498D5A36Ea58BBcc9c0039889D";
  const ETH_PRICE_USD = process.env.ETH_PRICE_USD || "2500"; // dollars
  const RPC = process.env.SEPOLIA_RPC_URL || "https://ethereum-sepolia.publicnode.com";
  const PK = process.env.PRIVATE_KEY;

  if (!PK) {
    throw new Error("Missing PRIVATE_KEY in env");
  }

  console.log("RPC:", RPC);
  console.log("OMKDispenser:", DISPENSER);

  const provider = new ethers.JsonRpcProvider(RPC);
  const wallet = new ethers.Wallet(PK, provider);
  console.log("Signer:", wallet.address);

  // Minimal ABI
  const ABI = [
    "function setSupportedToken(address token, bool supported, uint256 decimals, uint256 priceUSD) external",
    "function supportedTokens(address) view returns (bool)",
    "function tokenDecimals(address) view returns (uint256)",
    "function tokenPricesUSD(address) view returns (uint256)"
  ];

  // price with 8 decimals
  const price8 = BigInt(Math.floor(Number(ETH_PRICE_USD) * 1e8));
  const dispenser = new ethers.Contract(DISPENSER, ABI, wallet);

  const tx = await dispenser.setSupportedToken("0x0000000000000000000000000000000000000000", true, 18, price8);
  console.log("setSupportedToken(ETH) tx:", tx.hash);
  await tx.wait();
  console.log("✅ ETH configured in OMKDispenser (supported=true, decimals=18, priceUSD8=", price8.toString(), ")");

  const supported = await dispenser.supportedTokens("0x0000000000000000000000000000000000000000");
  const dec = await dispenser.tokenDecimals("0x0000000000000000000000000000000000000000");
  const price = await dispenser.tokenPricesUSD("0x0000000000000000000000000000000000000000");
  console.log("ETH supported:", supported, "decimals:", dec.toString(), "priceUSD8:", price.toString());
}

main().catch((e) => { console.error(e); process.exit(1); });
