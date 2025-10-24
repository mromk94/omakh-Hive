const hre = require("hardhat");
require("dotenv").config();

async function main() {
  const STABLECOIN = process.env.STABLECOIN_ADDRESS || "0x8b81ffe0ad7bca69f05b18a603f4352d22cfa8b2";
  const PRIVATE_SALE = process.env.PRIVATE_SALE_ADDRESS || "0xc801977eA4c3dAA93ca18e00aB07625923714484";
  const DISPENSER = process.env.OMK_DISPENSER_ADDRESS || "0x6165050d8F9a09498D5A36Ea58BBcc9c0039889D";

  console.log("Network:", hre.network.name);
  console.log("Stablecoin:", STABLECOIN);
  console.log("PrivateSale:", PRIVATE_SALE);
  console.log("OMKDispenser:", DISPENSER, "\n");

  const [signer] = await hre.ethers.getSigners();
  console.log("Signer:", signer.address);

  // 1) Accept stablecoin in PrivateSale
  const ps = await hre.ethers.getContractAt("PrivateSale", PRIVATE_SALE, signer);
  let tx = await ps.setPaymentToken(STABLECOIN, true);
  console.log("setPaymentToken tx:", tx.hash);
  await tx.wait();
  console.log("✅ Payment token accepted in PrivateSale");

  // 2) Configure stablecoin in OMKDispenser (6 decimals, price $1.00 with 8 decimals)
  const dispenser = await hre.ethers.getContractAt("OMKDispenser", DISPENSER, signer);
  tx = await dispenser.setSupportedToken(STABLECOIN, true, 6, 100000000);
  console.log("setSupportedToken tx:", tx.hash);
  await tx.wait();
  console.log("✅ Stablecoin configured in OMKDispenser");

  // 3) Activate the sale
  tx = await ps.activateSale();
  console.log("activateSale tx:", tx.hash);
  await tx.wait();
  console.log("✅ PrivateSale activated\n");

  // Verify state
  const accepted = await ps.acceptedPaymentTokens(STABLECOIN);
  console.log("PrivateSale.acceptedPaymentTokens:", accepted);
  const supported = await dispenser.supportedTokens(STABLECOIN);
  const dec = await dispenser.tokenDecimals(STABLECOIN);
  const price = await dispenser.tokenPricesUSD(STABLECOIN);
  console.log("OMKDispenser.supported:", supported, "decimals:", dec.toString(), "priceUSD:", price.toString());
}

main().catch((e) => { console.error(e); process.exit(1); });
