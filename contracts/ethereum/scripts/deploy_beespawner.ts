import hre from "hardhat";

async function main() {
  const admin = process.env.ADMIN_ADDRESS || "0xd4a3209ff4ADf36d6e43eeDC41A8C705e25708c1";
  const queen = process.env.QUEEN_ADDRESS || admin;

  console.log("Deploying BeeSpawner...");
  console.log("Network:", hre.network.name);
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deployer:", deployer.address);

  const Factory = await hre.ethers.getContractFactory("BeeSpawner");
  const contract = await Factory.deploy(admin, queen);
  console.log("TX:", contract.deploymentTransaction()?.hash);
  await contract.waitForDeployment();
  const addr = await contract.getAddress();
  console.log("BeeSpawner deployed at:", addr);
}

main().then(() => process.exit(0)).catch((err) => { console.error(err); process.exit(1); });
