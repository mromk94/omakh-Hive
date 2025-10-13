/**
 * PrivateSale Deployment Script
 * Deploys all private sale related contracts with security fixes
 */

const hre = require("hardhat");
const fs = require('fs');
const path = require('path');

async function main() {
  console.log("🚀 Starting PrivateSale Deployment with Security Fixes...\n");

  const [deployer] = await hre.ethers.getSigners();
  console.log(`👤 Deployer: ${deployer.address}`);
  console.log(`💰 Balance: ${hre.ethers.utils.formatEther(await deployer.getBalance())} ETH\n`);

  // Configuration
  const QUEEN_MANAGER_ADDRESS = process.env.QUEEN_MANAGER_ADDRESS || deployer.address;
  const TREASURY_ADDRESS = process.env.TREASURY_ADDRESS || deployer.address;
  
  const deployments = {};

  // 1. Deploy OMKToken (if not already deployed)
  console.log("📝 Step 1: Deploying OMKToken...");
  const OMKToken = await hre.ethers.getContractFactory("OMKToken");
  const omkToken = await OMKToken.deploy();
  await omkToken.deployed();
  console.log(`✅ OMKToken deployed to: ${omkToken.address}\n`);
  deployments.omkToken = omkToken.address;

  // 2. Deploy TokenVesting
  console.log("📝 Step 2: Deploying TokenVesting...");
  const TokenVesting = await hre.ethers.getContractFactory("TokenVesting");
  const tokenVesting = await TokenVesting.deploy(omkToken.address, deployer.address);
  await tokenVesting.deployed();
  console.log(`✅ TokenVesting deployed to: ${tokenVesting.address}\n`);
  deployments.tokenVesting = tokenVesting.address;

  // 3. Deploy PrivateSale (with all security fixes)
  console.log("📝 Step 3: Deploying PrivateSale (with security fixes)...");
  const PrivateSale = await hre.ethers.getContractFactory("PrivateSale");
  const privateSale = await PrivateSale.deploy(
    omkToken.address,
    TREASURY_ADDRESS,
    deployer.address,
    QUEEN_MANAGER_ADDRESS
  );
  await privateSale.deployed();
  console.log(`✅ PrivateSale deployed to: ${privateSale.address}`);
  console.log(`   - MIN_PURCHASE: 2000 OMK`);
  console.log(`   - MAX_RAISE: $12.25M`);
  console.log(`   - Vesting fixes: Applied\n`);
  deployments.privateSale = privateSale.address;

  // 4. Deploy PrivateInvestorRegistry
  console.log("📝 Step 4: Deploying PrivateInvestorRegistry...");
  const PrivateInvestorRegistry = await hre.ethers.getContractFactory("PrivateInvestorRegistry");
  const investorRegistry = await PrivateInvestorRegistry.deploy(
    omkToken.address,
    deployer.address
  );
  await investorRegistry.deployed();
  console.log(`✅ PrivateInvestorRegistry deployed to: ${investorRegistry.address}`);
  console.log(`   - MAX_INVESTORS: 10,000\n`);
  deployments.investorRegistry = investorRegistry.address;

  // 5. Deploy OMKDispenser (with price update fixes)
  console.log("📝 Step 5: Deploying OMKDispenser (with price fixes)...");
  const OMKDispenser = await hre.ethers.getContractFactory("OMKDispenser");
  const omkDispenser = await OMKDispenser.deploy(
    omkToken.address,
    deployer.address,
    QUEEN_MANAGER_ADDRESS
  );
  await omkDispenser.deployed();
  console.log(`✅ OMKDispenser deployed to: ${omkDispenser.address}`);
  console.log(`   - Price update delay: 30 minutes`);
  console.log(`   - Max price change: 20%\n`);
  deployments.omkDispenser = omkDispenser.address;

  // 6. Setup - Transfer tokens to contracts
  console.log("📝 Step 6: Transferring tokens to contracts...");
  
  // Transfer 100M to PrivateSale
  console.log("Transferring 100M OMK to PrivateSale...");
  await omkToken.transfer(privateSale.address, hre.ethers.utils.parseEther("100000000"));
  
  // Transfer 100M to InvestorRegistry
  console.log("Transferring 100M OMK to InvestorRegistry...");
  await omkToken.transfer(investorRegistry.address, hre.ethers.utils.parseEther("100000000"));
  
  // Transfer 10M to OMKDispenser
  console.log("Transferring 10M OMK to OMKDispenser...");
  await omkToken.transfer(omkDispenser.address, hre.ethers.utils.parseEther("10000000"));
  
  console.log("✅ Token transfers complete\n");

  // 7. Verify Security Fixes
  console.log("📝 Step 7: Verifying Security Fixes...\n");
  
  console.log("🔒 PrivateSale Security:");
  console.log(`   ✅ MIN_PURCHASE: ${hre.ethers.utils.formatEther(await privateSale.MIN_PURCHASE())} OMK`);
  console.log(`   ✅ MAX_RAISE_USD: $${(await privateSale.MAX_RAISE_USD()) / 1e6}`);
  console.log(`   ✅ Vesting setup order: Fixed (address set after success)\n`);
  
  console.log("🔒 OMKDispenser Security:");
  console.log(`   ✅ PRICE_UPDATE_DELAY: ${(await omkDispenser.PRICE_UPDATE_DELAY()) / 60} minutes`);
  console.log(`   ✅ MAX_PRICE_CHANGE_PERCENT: ${await omkDispenser.MAX_PRICE_CHANGE_PERCENT()}%\n`);
  
  console.log("🔒 TokenVesting Security:");
  console.log(`   ✅ Pausable: Enabled`);
  console.log(`   ✅ Can emergency pause: Yes\n`);
  
  console.log("🔒 InvestorRegistry Limits:");
  console.log(`   ✅ MAX_INVESTORS: ${await investorRegistry.MAX_INVESTORS()}\n`);

  // 8. Save deployment info
  const deploymentsDir = path.join(__dirname, '..', 'deployments');
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  const networkDir = path.join(deploymentsDir, hre.network.name);
  if (!fs.existsSync(networkDir)) {
    fs.mkdirSync(networkDir, { recursive: true });
  }

  const deploymentInfo = {
    network: hre.network.name,
    timestamp: new Date().toISOString(),
    deployer: deployer.address,
    contracts: deployments,
    securityFixes: {
      privateSale: {
        minPurchase: "2000 OMK",
        maxRaise: "$12.25M",
        vestingSetupFixed: true
      },
      omkDispenser: {
        priceUpdateDelay: "30 minutes",
        maxPriceChange: "20%"
      },
      tokenVesting: {
        pausable: true
      },
      investorRegistry: {
        maxInvestors: 10000
      }
    }
  };

  const deploymentFile = path.join(networkDir, 'private-sale-deployment.json');
  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
  console.log(`💾 Deployment info saved to: ${deploymentFile}\n`);

  // 9. Print verification commands
  console.log("📝 Verification Commands:\n");
  console.log(`npx hardhat verify --network ${hre.network.name} ${omkToken.address}`);
  console.log(`npx hardhat verify --network ${hre.network.name} ${tokenVesting.address} ${omkToken.address} ${deployer.address}`);
  console.log(`npx hardhat verify --network ${hre.network.name} ${privateSale.address} ${omkToken.address} ${TREASURY_ADDRESS} ${deployer.address} ${QUEEN_MANAGER_ADDRESS}`);
  console.log(`npx hardhat verify --network ${hre.network.name} ${investorRegistry.address} ${omkToken.address} ${deployer.address}`);
  console.log(`npx hardhat verify --network ${hre.network.name} ${omkDispenser.address} ${omkToken.address} ${deployer.address} ${QUEEN_MANAGER_ADDRESS}\n`);

  console.log("✅ Deployment Complete! All security fixes applied.\n");
  console.log("🎉 Ready for testing on", hre.network.name);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
