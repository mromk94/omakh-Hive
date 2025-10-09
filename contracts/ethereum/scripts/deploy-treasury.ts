import { ethers, upgrades } from "hardhat";
import { HardhatRuntimeEnvironment } from "hardhat/types";
import { DeployFunction } from "hardhat-deploy/types";

const func: DeployFunction = async function (hre: HardhatRuntimeEnvironment) {
  const { deployments, getNamedAccounts } = hre;
  const { deploy } = deployments;
  const { deployer } = await getNamedAccounts();

  console.log("Deploying TreasuryVault...");
  
  // Get signers for approvers (using the first 3 accounts after deployer)
  const signers = await ethers.getSigners();
  const approvers = [
    signers[1].address, // approver1
    signers[2].address, // approver2
    signers[3].address  // approver3
  ];
  
  // Deploy TreasuryVault
  const TreasuryVault = await ethers.getContractFactory("TreasuryVault");
  const treasury = await upgrades.deployProxy(
    TreasuryVault,
    [
      deployer,      // admin
      approvers,     // initial approvers
      deployer       // emergency admin (same as deployer for testing)
    ],
    { initializer: 'initialize' }
  );
  
  await treasury.waitForDeployment();
  
  console.log(`TreasuryVault deployed to: ${await treasury.getAddress()}`);
  console.log("Approvers:", approvers);
  console.log(`Required approvals: ${await treasury.requiredApprovals()}`);
  console.log(`Withdrawal delay: ${await treasury.withdrawalDelay()} seconds`);
};

export default func;
func.tags = ["TreasuryVault"];
