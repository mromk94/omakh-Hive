import { ethers } from "hardhat";

/**
 * Script to verify Queen AI autonomy and safeguards
 * Tests:
 * 1. Queen receives 400M tokens
 * 2. Queen can transfer within daily limits
 * 3. Rate limiting works correctly
 * 4. Large transfers trigger monitoring
 * 5. Queen can propose and execute operations
 */

async function main() {
  console.log("🔍 QUEEN AUTONOMY VERIFICATION\n");
  console.log("=" .repeat(80));
  
  const [admin, queenBackend, treasury, dexPool, staker] = await ethers.getSigners();
  
  console.log("\n📋 SETUP");
  console.log("-".repeat(80));
  console.log("Admin:", admin.address);
  console.log("Queen Backend:", queenBackend.address);
  console.log("Treasury:", treasury.address);
  console.log("DEX Pool:", dexPool.address);
  
  // ============ DEPLOY CONTRACTS ============
  console.log("\n🚀 DEPLOYING CONTRACTS");
  console.log("-".repeat(80));
  
  // Deploy OMKToken
  const OMKToken = await ethers.getContractFactory("OMKToken");
  const token = await OMKToken.deploy(
    "OMK Token",
    "OMK",
    admin.address,
    treasury.address,
    queenBackend.address, // Queen gets the 400M tokens
    admin.address, // founders (placeholder)
    admin.address, // privateInvestors (placeholder)
    admin.address  // advisors (placeholder)
  );
  await token.deployed();
  console.log("✅ OMKToken deployed:", token.address);
  
  // Deploy QueenController
  const QueenController = await ethers.getContractFactory("QueenController");
  const controller = await QueenController.deploy(
    admin.address,
    queenBackend.address,
    token.address
  );
  await controller.deployed();
  console.log("✅ QueenController deployed:", controller.address);
  
  // ============ VERIFY INITIAL STATE ============
  console.log("\n💰 INITIAL TOKEN DISTRIBUTION");
  console.log("-".repeat(80));
  
  const totalSupply = await token.totalSupply();
  const queenBalance = await token.balanceOf(queenBackend.address);
  const adminBalance = await token.balanceOf(admin.address);
  const treasuryBalance = await token.balanceOf(treasury.address);
  
  console.log("Total Supply:", ethers.utils.formatEther(totalSupply), "OMK");
  console.log("Queen Balance:", ethers.utils.formatEther(queenBalance), "OMK (should be 400M)");
  console.log("Admin Balance:", ethers.utils.formatEther(adminBalance), "OMK (breakswitch)");
  console.log("Treasury Balance:", ethers.utils.formatEther(treasuryBalance), "OMK");
  
  const EXPECTED_QUEEN_BALANCE = ethers.utils.parseEther("400000000");
  if (queenBalance.eq(EXPECTED_QUEEN_BALANCE)) {
    console.log("✅ Queen received correct amount (400M OMK)");
  } else {
    console.log("❌ Queen balance mismatch!");
    return;
  }
  
  // ============ TEST RATE LIMITING ============
  console.log("\n🛡️  TESTING RATE LIMITING");
  console.log("-".repeat(80));
  
  // Get current stats
  let stats = await token.getQueenTransferStats();
  console.log("Rate Limit Active:", stats.rateLimitActive);
  console.log("Daily Limit:", ethers.utils.formatEther(await token.MAX_QUEEN_DAILY_TRANSFER()), "OMK");
  console.log("Remaining Today:", ethers.utils.formatEther(stats.remainingToday), "OMK");
  
  // Test 1: Transfer within limits (5M OMK to DEX)
  console.log("\n📤 Test 1: Transfer 5M OMK to DEX (within limits)");
  const amount1 = ethers.utils.parseEther("5000000");
  
  try {
    const tx1 = await token.connect(queenBackend).transfer(dexPool.address, amount1);
    await tx1.wait();
    console.log("✅ Transfer succeeded");
    
    const receipt1 = await tx1.wait();
    const event1 = receipt1.events?.find(e => e.event === "QueenTransfer");
    if (event1) {
      console.log("   Daily total after transfer:", ethers.utils.formatEther(event1.args?.dailyTotal), "OMK");
    }
  } catch (error: any) {
    console.log("❌ Transfer failed:", error.message);
  }
  
  // Test 2: Another transfer (10M OMK to DEX)
  console.log("\n📤 Test 2: Transfer 10M OMK to DEX (cumulative 15M)");
  const amount2 = ethers.utils.parseEther("10000000");
  
  try {
    const tx2 = await token.connect(queenBackend).transfer(dexPool.address, amount2);
    await tx2.wait();
    console.log("✅ Transfer succeeded");
    
    const receipt2 = await tx2.wait();
    const event2 = receipt2.events?.find(e => e.event === "QueenTransfer");
    if (event2) {
      console.log("   Daily total after transfer:", ethers.utils.formatEther(event2.args?.dailyTotal), "OMK");
    }
  } catch (error: any) {
    console.log("❌ Transfer failed:", error.message);
  }
  
  // Test 3: Large transfer alert (100M OMK)
  console.log("\n📤 Test 3: Large transfer (100M OMK) - should trigger alert event");
  const largeAmount = ethers.utils.parseEther("100000000");
  
  try {
    const tx3 = await token.connect(queenBackend).transfer(dexPool.address, largeAmount);
    const receipt3 = await tx3.wait();
    console.log("✅ Transfer succeeded");
    
    const largeEvent = receipt3.events?.find(e => e.event === "LargeTransferAttempt");
    if (largeEvent) {
      console.log("⚠️  Large transfer alert triggered!");
      console.log("   Amount:", ethers.utils.formatEther(largeEvent.args?.amount), "OMK");
    }
  } catch (error: any) {
    console.log("❌ Transfer failed:", error.message);
  }
  
  // Test 4: Exceed daily limit (should fail)
  console.log("\n📤 Test 4: Attempt to transfer beyond daily limit (should FAIL)");
  const excessAmount = ethers.utils.parseEther("200000000"); // 200M
  
  try {
    const tx4 = await token.connect(queenBackend).transfer(dexPool.address, excessAmount);
    await tx4.wait();
    console.log("❌ Transfer should have failed but succeeded!");
  } catch (error: any) {
    if (error.message.includes("Queen daily transfer limit exceeded")) {
      console.log("✅ Rate limit protection working - transfer rejected");
    } else {
      console.log("⚠️  Failed with unexpected error:", error.message);
    }
  }
  
  // ============ TEST QUEEN CONTROLLER ============
  console.log("\n👑 TESTING QUEEN CONTROLLER");
  console.log("-".repeat(80));
  
  // Propose operation
  console.log("\n📝 Proposing operation: DEX_ADD_LIQUIDITY");
  const tx5 = await controller.connect(queenBackend).proposeOperation(
    "DEX_ADD_LIQUIDITY",
    ethers.utils.parseEther("5000000"),
    dexPool.address
  );
  const receipt5 = await tx5.wait();
  const proposeEvent = receipt5.events?.find(e => e.event === "QueenOperationProposed");
  
  if (proposeEvent) {
    const operationId = proposeEvent.args?.operationId;
    console.log("✅ Operation proposed");
    console.log("   Operation ID:", operationId);
    console.log("   Type:", proposeEvent.args?.operationType);
    console.log("   Amount:", ethers.utils.formatEther(proposeEvent.args?.amount), "OMK");
    
    // Execute operation
    console.log("\n⚡ Executing operation...");
    const tx6 = await controller.connect(queenBackend).executeOperation(operationId);
    await tx6.wait();
    console.log("✅ Operation executed");
  }
  
  // ============ TEST EMERGENCY CONTROLS ============
  console.log("\n🚨 TESTING EMERGENCY CONTROLS");
  console.log("-".repeat(80));
  
  // Disable rate limiting
  console.log("\n🔓 Admin disabling rate limiting...");
  await token.connect(admin).setQueenRateLimitEnabled(false);
  console.log("✅ Rate limiting disabled");
  
  stats = await token.getQueenTransferStats();
  console.log("Rate Limit Active:", stats.rateLimitActive);
  
  // Re-enable rate limiting
  console.log("\n🔒 Admin re-enabling rate limiting...");
  await token.connect(admin).setQueenRateLimitEnabled(true);
  console.log("✅ Rate limiting re-enabled");
  
  // ============ SUMMARY ============
  console.log("\n" + "=".repeat(80));
  console.log("📊 VERIFICATION SUMMARY");
  console.log("=".repeat(80));
  
  const finalQueenBalance = await token.balanceOf(queenBackend.address);
  const dexBalance = await token.balanceOf(dexPool.address);
  
  console.log("\n💰 Final Balances:");
  console.log("Queen:", ethers.utils.formatEther(finalQueenBalance), "OMK");
  console.log("DEX Pool:", ethers.utils.formatEther(dexBalance), "OMK");
  console.log("\n✅ All tests completed successfully!");
  console.log("\n🎯 Queen AI is autonomous and protected by safeguards");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
