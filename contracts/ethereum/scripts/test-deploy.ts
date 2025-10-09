import { ethers } from "hardhat";

async function main() {
  console.log("Starting deployment test...");
  
  const [deployer, founders, privateInvestors, advisors, treasury, queenAI] = await ethers.getSigners();
  
  console.log("Deploying OMKToken...");
  console.log("Deployer:", deployer.address);
  console.log("Founders:", founders.address);
  console.log("Private Investors:", privateInvestors.address);
  console.log("Advisors:", advisors.address);
  console.log("Treasury:", treasury.address);
  
  const OMKToken = await ethers.getContractFactory("OMKToken");
  
  try {
    const token = await OMKToken.deploy(
      "OMK Token",
      "OMK",
      deployer.address,
      treasury.address,
      founders.address,
      privateInvestors.address,
      advisors.address
    );
    
    await token.deployed();
    
    console.log("✅ OMKToken deployed successfully to:", token.address);
    console.log("Total supply:", ethers.utils.formatEther(await token.totalSupply()));
    
    // Check balances
    console.log("\nBalances:");
    console.log("Deployer:", ethers.utils.formatEther(await token.balanceOf(deployer.address)));
    console.log("Treasury:", ethers.utils.formatEther(await token.balanceOf(treasury.address)));
    console.log("Contract:", ethers.utils.formatEther(await token.balanceOf(token.address)));
    
  } catch (error: any) {
    console.error("❌ Deployment failed:");
    console.error(error.message);
    if (error.error) {
      console.error("Error details:", error.error);
    }
    throw error;
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
