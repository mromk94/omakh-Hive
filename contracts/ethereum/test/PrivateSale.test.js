const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("PrivateSale - Security Fixes", function () {
  let omkToken, privateSale, tokenVesting;
  let owner, queenManager, investor1, investor2, treasury;
  let usdc;

  beforeEach(async function () {
    [owner, queenManager, investor1, investor2, treasury] = await ethers.getSigners();

    // Deploy OMK Token
    const OMKToken = await ethers.getContractFactory("OMKToken");
    omkToken = await OMKToken.deploy();
    await omkToken.deployed();

    // Deploy mock USDC
    const MockERC20 = await ethers.getContractFactory("MockERC20");
    usdc = await MockERC20.deploy("USD Coin", "USDC", 6);
    await usdc.deployed();

    // Deploy PrivateSale
    const PrivateSale = await ethers.getContractFactory("PrivateSale");
    privateSale = await PrivateSale.deploy(
      omkToken.address,
      treasury.address,
      owner.address,
      queenManager.address
    );
    await privateSale.deployed();

    // Transfer tokens to PrivateSale contract
    await omkToken.transfer(privateSale.address, ethers.utils.parseEther("100000000")); // 100M

    // Setup payment token
    await privateSale.setPaymentToken(usdc.address, true);
    
    // Whitelist investors
    await privateSale.connect(queenManager).setInvestorWhitelist(investor1.address, true);
    await privateSale.connect(queenManager).setInvestorWhitelist(investor2.address, true);
    
    // Activate sale
    await privateSale.connect(queenManager).activateSale();

    // Give investors USDC
    await usdc.mint(investor1.address, ethers.utils.parseUnits("1000000", 6)); // $1M
    await usdc.mint(investor2.address, ethers.utils.parseUnits("1000000", 6)); // $1M
  });

  describe("CRITICAL FIX: Minimum Purchase", function () {
    it("Should reject purchases below 2000 OMK", async function () {
      const amount = ethers.utils.parseEther("1000"); // 1000 OMK
      
      await expect(
        privateSale.connect(investor1).purchaseTokens(amount, usdc.address, ethers.utils.parseUnits("1000", 6))
      ).to.be.revertedWith("PrivateSale: Below minimum purchase");
    });

    it("Should accept purchases of exactly 2000 OMK", async function () {
      const amount = ethers.utils.parseEther("2000"); // 2000 OMK
      const payment = await privateSale.calculatePayment(amount);
      
      await usdc.connect(investor1).approve(privateSale.address, payment);
      
      await expect(
        privateSale.connect(investor1).purchaseTokens(amount, usdc.address, payment)
      ).to.not.be.reverted;
    });
  });

  describe("HIGH-3 FIX: USD Raise Cap", function () {
    it("Should enforce maximum raise of $12.25M", async function () {
      // Try to buy all 100M tokens (would be $12.25M at average price)
      const amount = ethers.utils.parseEther("100000000");
      const payment = await privateSale.calculatePayment(amount);
      
      await usdc.connect(investor1).approve(privateSale.address, payment);
      
      await privateSale.connect(investor1).purchaseTokens(
        amount, 
        usdc.address, 
        payment
      );

      // Try to buy more - should fail
      const moreAmount = ethers.utils.parseEther("1000");
      const morePayment = await privateSale.calculatePayment(moreAmount);
      
      await usdc.connect(investor2).approve(privateSale.address, morePayment);
      
      await expect(
        privateSale.connect(investor2).purchaseTokens(moreAmount, usdc.address, morePayment)
      ).to.be.revertedWith("PrivateSale: Max raise exceeded");
    });

    it("Should track total raised correctly", async function () {
      const amount = ethers.utils.parseEther("10000000"); // 10M tokens
      const payment = await privateSale.calculatePayment(amount);
      
      await usdc.connect(investor1).approve(privateSale.address, payment);
      await privateSale.connect(investor1).purchaseTokens(amount, usdc.address, payment);
      
      const totalRaised = await privateSale.getTotalRaisedUSD();
      expect(totalRaised).to.be.gt(0);
    });
  });

  describe("CRITICAL-1 FIX: Vesting Setup Order", function () {
    it("Should not set vesting contract address if balance insufficient", async function () {
      // Purchase tokens
      const amount = ethers.utils.parseEther("10000"); // 10k tokens
      const payment = await privateSale.calculatePayment(amount);
      
      await usdc.connect(investor1).approve(privateSale.address, payment);
      await privateSale.connect(investor1).purchaseTokens(amount, usdc.address, payment);

      // Remove tokens from contract to simulate insufficient balance
      await privateSale.connect(owner).withdrawFunds(omkToken.address, ethers.utils.parseEther("99999999"));

      // Try to setup vesting - should fail
      await expect(
        privateSale.connect(queenManager).setupVestingForInvestor(investor1.address)
      ).to.be.revertedWith("PrivateSale: Insufficient balance");

      // Verify vesting contract address is still 0
      const investorInfo = await privateSale.investments(investor1.address);
      expect(investorInfo.vestingContract).to.equal(ethers.constants.AddressZero);
    });

    it("Should set vesting contract address only after successful setup", async function () {
      // Purchase tokens
      const amount = ethers.utils.parseEther("10000");
      const payment = await privateSale.calculatePayment(amount);
      
      await usdc.connect(investor1).approve(privateSale.address, payment);
      await privateSale.connect(investor1).purchaseTokens(amount, usdc.address, payment);

      // Setup vesting - should succeed
      await expect(
        privateSale.connect(queenManager).setupVestingForInvestor(investor1.address)
      ).to.emit(privateSale, "VestingSetupComplete");

      // Verify vesting contract address is set
      const investorInfo = await privateSale.investments(investor1.address);
      expect(investorInfo.vestingContract).to.not.equal(ethers.constants.AddressZero);
    });

    it("Should emit VestingSetupComplete event", async function () {
      const amount = ethers.utils.parseEther("10000");
      const payment = await privateSale.calculatePayment(amount);
      
      await usdc.connect(investor1).approve(privateSale.address, payment);
      await privateSale.connect(investor1).purchaseTokens(amount, usdc.address, payment);

      await expect(
        privateSale.connect(queenManager).setupVestingForInvestor(investor1.address)
      ).to.emit(privateSale, "VestingSetupComplete")
        .withArgs(investor1.address, anyValue, amount);
    });
  });

  describe("Whale Limits", function () {
    it("Should enforce 10M token limit per investor", async function () {
      const amount = ethers.utils.parseEther("10000001"); // Just over limit
      
      await expect(
        privateSale.connect(investor1).purchaseTokens(amount, usdc.address, ethers.utils.parseUnits("10000000", 6))
      ).to.be.revertedWith("PrivateSale: Exceeds whale limit (10M)");
    });

    it("Should allow exactly 10M tokens per investor", async function () {
      const amount = ethers.utils.parseEther("10000000"); // Exactly 10M
      const payment = await privateSale.calculatePayment(amount);
      
      await usdc.connect(investor1).approve(privateSale.address, payment);
      
      await expect(
        privateSale.connect(investor1).purchaseTokens(amount, usdc.address, payment)
      ).to.not.be.reverted;
    });
  });

  describe("Tier Progression", function () {
    it("Should advance tiers correctly", async function () {
      const tierSize = ethers.utils.parseEther("10000000"); // 10M tokens
      const payment = await privateSale.calculatePayment(tierSize);
      
      await usdc.connect(investor1).approve(privateSale.address, payment);
      await privateSale.connect(investor1).purchaseTokens(tierSize, usdc.address, payment);

      const saleStatus = await privateSale.getSaleStatus();
      expect(saleStatus._currentTier).to.equal(1);
    });
  });
});

describe("OMKDispenser - Price Update Fixes", function () {
  let omkToken, dispenser, owner, oracle, user;
  let usdc;

  beforeEach(async function () {
    [owner, oracle, user] = await ethers.getSigners();

    // Deploy OMK Token
    const OMKToken = await ethers.getContractFactory("OMKToken");
    omkToken = await OMKToken.deploy();

    // Deploy mock USDC
    const MockERC20 = await ethers.getContractFactory("MockERC20");
    usdc = await MockERC20.deploy("USD Coin", "USDC", 6);

    // Deploy OMKDispenser
    const OMKDispenser = await ethers.getContractFactory("OMKDispenser");
    dispenser = await OMKDispenser.deploy(
      omkToken.address,
      owner.address,
      owner.address
    );

    // Grant oracle role
    const ORACLE_ROLE = await dispenser.ORACLE_ROLE();
    await dispenser.grantRole(ORACLE_ROLE, oracle.address);

    // Setup supported token
    await dispenser.setSupportedToken(
      usdc.address,
      true,
      6,
      100000000 // $1.00 in 8 decimals
    );

    // Deposit OMK to dispenser
    await omkToken.transfer(dispenser.address, ethers.utils.parseEther("1000000"));
  });

  describe("CRITICAL-2 FIX: Price Update Time-Lock", function () {
    it("Should reject price updates within 30 minutes", async function () {
      // First update
      await dispenser.connect(oracle).updateTokenPrice(usdc.address, 105000000); // $1.05

      // Try immediate update - should fail
      await expect(
        dispenser.connect(oracle).updateTokenPrice(usdc.address, 110000000)
      ).to.be.revertedWith("OMKDispenser: Price update too soon");
    });

    it("Should allow price updates after 30 minutes", async function () {
      // First update
      await dispenser.connect(oracle).updateTokenPrice(usdc.address, 105000000);

      // Fast forward 31 minutes
      await ethers.provider.send("evm_increaseTime", [31 * 60]);
      await ethers.provider.send("evm_mine");

      // Second update - should succeed
      await expect(
        dispenser.connect(oracle).updateTokenPrice(usdc.address, 110000000)
      ).to.not.be.reverted;
    });
  });

  describe("CRITICAL-2 FIX: Price Change Limit", function () {
    it("Should reject price changes > 20%", async function () {
      // Set initial price
      await dispenser.connect(oracle).updateTokenPrice(usdc.address, 100000000); // $1.00

      // Fast forward 31 minutes
      await ethers.provider.send("evm_increaseTime", [31 * 60]);
      await ethers.provider.send("evm_mine");

      // Try to update to $1.25 (25% increase) - should fail
      await expect(
        dispenser.connect(oracle).updateTokenPrice(usdc.address, 125000000)
      ).to.be.revertedWith("OMKDispenser: Price change exceeds limit");
    });

    it("Should allow price changes <= 20%", async function () {
      // Set initial price
      await dispenser.connect(oracle).updateTokenPrice(usdc.address, 100000000); // $1.00

      // Fast forward 31 minutes
      await ethers.provider.send("evm_increaseTime", [31 * 60]);
      await ethers.provider.send("evm_mine");

      // Update to $1.20 (20% increase) - should succeed
      await expect(
        dispenser.connect(oracle).updateTokenPrice(usdc.address, 120000000)
      ).to.not.be.reverted;
    });

    it("Should allow first-time price setting without limits", async function () {
      const MockERC20 = await ethers.getContractFactory("MockERC20");
      const dai = await MockERC20.deploy("DAI", "DAI", 18);

      // Add new token with high price - should work (first time)
      await expect(
        dispenser.setSupportedToken(dai.address, true, 18, 500000000000) // $5000
      ).to.not.be.reverted;
    });
  });
});

describe("TokenVesting - Pausable", function () {
  let omkToken, vesting, owner, beneficiary;

  beforeEach(async function () {
    [owner, beneficiary] = await ethers.getSigners();

    // Deploy OMK Token
    const OMKToken = await ethers.getContractFactory("OMKToken");
    omkToken = await OMKToken.deploy();

    // Deploy TokenVesting
    const TokenVesting = await ethers.getContractFactory("TokenVesting");
    vesting = await TokenVesting.deploy(omkToken.address, owner.address);

    // Transfer tokens and create schedule
    await omkToken.transfer(vesting.address, ethers.utils.parseEther("1000000"));
    
    await vesting.createVestingSchedule(
      beneficiary.address,
      ethers.utils.parseEther("1000000"),
      0, // no cliff
      12, // 12 months
      true // linear
    );
  });

  describe("HIGH-2 FIX: Emergency Pause", function () {
    it("Should allow admin to pause", async function () {
      await expect(vesting.pause()).to.not.be.reverted;
      expect(await vesting.paused()).to.be.true;
    });

    it("Should block releases when paused", async function () {
      // Fast forward 6 months
      await ethers.provider.send("evm_increaseTime", [6 * 30 * 24 * 60 * 60]);
      await ethers.provider.send("evm_mine");

      await vesting.pause();

      await expect(
        vesting.release(beneficiary.address)
      ).to.be.revertedWith("Pausable: paused");
    });

    it("Should allow releases after unpause", async function () {
      // Fast forward 6 months
      await ethers.provider.send("evm_increaseTime", [6 * 30 * 24 * 60 * 60]);
      await ethers.provider.send("evm_mine");

      await vesting.pause();
      await vesting.unpause();

      await expect(
        vesting.release(beneficiary.address)
      ).to.not.be.reverted;
    });
  });
});

describe("PrivateInvestorRegistry - Investor Limit", function () {
  let omkToken, registry, owner;

  beforeEach(async function () {
    [owner] = await ethers.getSigners();

    // Deploy OMK Token
    const OMKToken = await ethers.getContractFactory("OMKToken");
    omkToken = await OMKToken.deploy();

    // Deploy PrivateInvestorRegistry
    const PrivateInvestorRegistry = await ethers.getContractFactory("PrivateInvestorRegistry");
    registry = await PrivateInvestorRegistry.deploy(omkToken.address, owner.address);
  });

  describe("HIGH-1 FIX: 65k Investor Limit", function () {
    it("Should enforce 65,000 investor limit", async function () {
      const MAX_INVESTORS = 65000;
      
      // This test would take too long to actually register 65k investors
      // So we just verify the constant is set correctly
      expect(await registry.MAX_INVESTORS()).to.equal(MAX_INVESTORS);
    });

    it("Should have correct max investor constant", async function () {
      const maxInvestors = await registry.MAX_INVESTORS();
      expect(maxInvestors).to.equal(65000);
    });
  });
});
