/**
 * Deploy BeeSpawner to selected network (CommonJS for ESM repo)
 */
const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying BeeSpawner...");
  console.log("Network:", hre.network.name);

  const [deployer] = await hre.ethers.getSigners();
  console.log("Deployer:", deployer.address);
  console.log("Balance:", hre.ethers.utils.formatEther(await deployer.getBalance()), "ETH");

  const admin = process.env.ADMIN_ADDRESS || deployer.address;
  const queen = process.env.QUEEN_ADDRESS || admin;
  console.log("Admin:", admin);
  console.log("Queen:", queen);

  const Factory = await hre.ethers.getContractFactory("BeeSpawner");
  const contract = await Factory.deploy(admin, queen);
  console.log("TX:", contract.deploymentTransaction()?.hash);
  await contract.waitForDeployment();
  const address = await contract.getAddress();
  console.log("✅ BeeSpawner deployed at:", address);
}

main()
  .then(() => process.exit(0))
  .catch((err) => { console.error(err); process.exit(1); });
