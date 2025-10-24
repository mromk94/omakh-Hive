import { ethers } from "ethers";
import dotenv from "dotenv";

dotenv.config();

async function main() {
  const SALE = process.env.PRIVATE_SALE_ADDRESS || "0xc801977eA4c3dAA93ca18e00aB07625923714484";
  const USDT = process.env.USDT_ADDRESS || process.env.NEXT_PUBLIC_USDT_ADDRESS || "0x8b81ffe0ad7bca69f05b18a603f4352d22cfa8b2";
  const USDC = process.env.USDC_ADDRESS || process.env.NEXT_PUBLIC_USDC_ADDRESS || "0x8b81ffe0ad7bca69f05b18a603f4352d22cfa8b2";
  const RPC = process.env.SEPOLIA_RPC_URL || "https://ethereum-sepolia.publicnode.com";
  const PK = process.env.PRIVATE_KEY;

  if (!PK) throw new Error("Missing PRIVATE_KEY in env");

  const provider = new ethers.JsonRpcProvider(RPC);
  const wallet = new ethers.Wallet(PK, provider);
  console.log("Signer:", wallet.address);
  console.log("PrivateSale:", SALE);
  console.log("USDT:", USDT);
  console.log("USDC:", USDC);

  const ABI = [
    "function setPaymentToken(address token, bool accepted) external",
    "function acceptedPaymentTokens(address) view returns (bool)"
  ];

  const sale = new ethers.Contract(SALE, ABI, wallet);

  for (const token of [USDT, USDC]) {
    console.log(`Setting acceptedPaymentToken(${token}) = true ...`);
    const tx = await sale.setPaymentToken(token, true);
    console.log("tx:", tx.hash);
    await tx.wait();
    const ok = await sale.acceptedPaymentTokens(token);
    console.log("accepted:", ok);
  }

  console.log("✅ Payment tokens accepted in PrivateSale");
}

main().catch((e) => { console.error(e); process.exit(1); });
