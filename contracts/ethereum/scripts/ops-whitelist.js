const hre = require("hardhat");
require("dotenv").config();

async function main() {
  const PRIVATE_SALE = process.env.PRIVATE_SALE_ADDRESS || "0xc801977eA4c3dAA93ca18e00aB07625923714484";
  const INVESTOR = process.env.INITIAL_INVESTOR || "0x884F953A370D06E7f64A40D7814d58A49412124B";

  const [signer] = await hre.ethers.getSigners();
  console.log("Network:", hre.network.name);
  console.log("Signer:", signer.address);
  console.log("PrivateSale:", PRIVATE_SALE);
  console.log("Investor:", INVESTOR);

  const ps = await hre.ethers.getContractAt("PrivateSale", PRIVATE_SALE, signer);
  const tx = await ps.batchWhitelist([INVESTOR], true);
  console.log("batchWhitelist tx:", tx.hash);
  await tx.wait();
  const info = await ps.investments(INVESTOR);
  console.log("Whitelisted:", info.isWhitelisted);
}

main().catch((e) => { console.error(e); process.exit(1); });
