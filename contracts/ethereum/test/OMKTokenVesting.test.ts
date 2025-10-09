import { loadFixture, time } from "@nomicfoundation/hardhat-network-helpers";
import { expect } from "chai";
import { ethers } from "hardhat";

describe("OMKToken with Vesting", function () {
  // 1 year in seconds
  const ONE_YEAR = 365 * 24 * 60 * 60;
  const ONE_MONTH = 30 * 24 * 60 * 60;

  // Token distribution constants
  const TOTAL_SUPPLY = ethers.utils.parseEther("1000000000"); // 1B tokens
  const FOUNDERS_AMOUNT = ethers.utils.parseEther("250000000"); // 25%
  const PRIVATE_INVESTORS_AMOUNT = ethers.utils.parseEther("100000000"); // 10%
  const ECOSYSTEM_AMOUNT = ethers.utils.parseEther("100000000"); // 10%
  const ADVISORS_AMOUNT = ethers.utils.parseEther("20000000"); // 2%
  const BREAKSWITCH_AMOUNT = ethers.utils.parseEther("10000000"); // 1%
  const TREASURY_AMOUNT = ethers.utils.parseEther("120000000"); // 12%
  const PUBLIC_ACQUISITION_AMOUNT = ethers.utils.parseEther("400000000"); // 40%

  async function deployTokenFixture() {
    const [
      deployer, // admin
      founders,
      privateInvestors,
      advisors,
      treasury,
      queenAI,
      otherAccount
    ] = await ethers.getSigners();

    // Deploy the token contract
    const OMKToken = await ethers.getContractFactory("OMKToken");
    const token = await OMKToken.deploy(
      "OMK Token",
      "OMK",
      deployer.address, // admin
      treasury.address, // treasury
      queenAI.address, // queen AI
      founders.address, // founders
      privateInvestors.address, // private investors
      advisors.address // advisors
    );

    return {
      token,
      deployer,
      founders,
      privateInvestors,
      advisors,
      treasury,
      queenAI,
      otherAccount,
    };
  }

  describe("Deployment and Initial Distribution", function () {
    it("Should deploy with correct initial supply", async function () {
      const { token } = await loadFixture(deployTokenFixture);
      expect(await token.totalSupply()).to.equal(TOTAL_SUPPLY);
    });

    it("Should distribute initial allocations correctly", async function () {
      const { token, deployer, treasury, queenAI } = await loadFixture(deployTokenFixture);
      
      // Check breakswitch amount (1%) was sent to deployer
      expect(await token.balanceOf(deployer.address)).to.equal(BREAKSWITCH_AMOUNT);
      
      // Check treasury amount (12%) was sent to treasury
      expect(await token.balanceOf(treasury.address)).to.equal(TREASURY_AMOUNT);
      
      // Check public acquisition amount (40%) was sent to Queen AI
      expect(await token.balanceOf(queenAI.address)).to.equal(PUBLIC_ACQUISITION_AMOUNT);
      
      // Check contract balance (remaining tokens)
      const contractBalance = await token.balanceOf(token.address);
      const expectedContractBalance = TOTAL_SUPPLY.sub(BREAKSWITCH_AMOUNT).sub(TREASURY_AMOUNT).sub(PUBLIC_ACQUISITION_AMOUNT);
      expect(contractBalance).to.equal(expectedContractBalance);
    });
  });

  describe("Vesting Schedules", function () {
    it("Should set up founders vesting schedule (25% at 12m, then 36m linear)", async function () {
      const { token, founders, deployer } = await loadFixture(deployTokenFixture);
      
      // Check initial vesting schedule
      const foundersVesting = await token.foundersVesting();
      expect(foundersVesting).to.not.equal(ethers.constants.AddressZero);
      
      // Check initial balance is zero (tokens are locked)
      expect(await token.balanceOf(founders.address)).to.equal(0);
      
      // Try to release before cliff (should not release anything)
      await token.connect(founders).releaseVestedTokens(founders.address);
      
      // Fast forward to cliff (12 months)
      await time.increase(ONE_YEAR);
      
      // Should be able to release 25% at cliff
      await token.connect(founders).releaseVestedTokens(founders.address);
      
      // Check balance after cliff release
      expect(await token.balanceOf(founders.address)).to.equal(FOUNDERS_AMOUNT.div(4));
      
      // Fast forward to end of vesting (36 more months)
      await time.increase(3 * ONE_YEAR);
      
      // Release remaining tokens
      await token.connect(founders).releaseVestedTokens(founders.address);
      
      // Should have all tokens now
      expect(await token.balanceOf(founders.address)).to.equal(FOUNDERS_AMOUNT);
    });

    it("Should set up private investors vesting schedule (25% at 12m, then 18m linear)", async function () {
      const { token, privateInvestors } = await loadFixture(deployTokenFixture);
      
      // Fast forward to cliff (12 months)
      await time.increase(ONE_YEAR);
      
      // Release cliff amount (25%)
      await token.connect(privateInvestors).releaseVestedTokens(privateInvestors.address);
      
      // Check balance after cliff release
      const cliffAmount = PRIVATE_INVESTORS_AMOUNT.div(4);
      expect(await token.balanceOf(privateInvestors.address)).to.equal(cliffAmount);
      
      // Fast forward to middle of vesting (9 months after cliff)
      await time.increase(9 * ONE_MONTH);
      
      // Release vested amount (should be 50% of remaining 75% = 37.5% total)
      await token.connect(privateInvestors).releaseVestedTokens(privateInvestors.address);
      const balance = await token.balanceOf(privateInvestors.address);
      const expected = PRIVATE_INVESTORS_AMOUNT.mul(5).div(8); // 25% + (75% * 0.5) = 62.5%
      const tolerance = PRIVATE_INVESTORS_AMOUNT.div(100); // 1% tolerance for rounding
      expect(balance).to.be.gte(expected.sub(tolerance)).and.lte(expected.add(tolerance));
    });

    it("Should set up advisors vesting schedule (18m linear)", async function () {
      const { token, advisors } = await loadFixture(deployTokenFixture);
      
      // Fast forward to 6 months
      await time.increase(6 * ONE_MONTH);
      
      // Release vested amount (should be ~33.33%)
      await token.connect(advisors).releaseVestedTokens(advisors.address);
      
      const balance = await token.balanceOf(advisors.address);
      const expectedAmount = ADVISORS_AMOUNT.mul(6).div(18);
      const tolerance = ADVISORS_AMOUNT.div(100); // 1% tolerance for rounding
      expect(balance).to.be.gte(expectedAmount.sub(tolerance)).and.lte(expectedAmount.add(tolerance));
      
      // Fast forward to end of vesting (12 more months)
      await time.increase(12 * ONE_MONTH);
      
      // Release remaining tokens
      await token.connect(advisors).releaseVestedTokens(advisors.address);
      
      // Should have all tokens now
      expect(await token.balanceOf(advisors.address)).to.equal(ADVISORS_AMOUNT);
    });
  });

  describe("Ecosystem Tokens", function () {
    it("Should allow Queen to release ecosystem tokens", async function () {
      const { token, queenAI, otherAccount } = await loadFixture(deployTokenFixture);
      
      // Fast forward 6 months
      await time.increase(6 * ONE_MONTH);
      
      // Check available amount (should be ~16.67% after 6 months of 36 month vesting)
      const availableAmount = await token.getAvailableEcosystemTokens();
      const expectedAmount = ECOSYSTEM_AMOUNT.mul(6).div(36);
      const tolerance = ECOSYSTEM_AMOUNT.div(1000); // 0.1% tolerance
      expect(availableAmount).to.be.gte(expectedAmount.sub(tolerance)).and.lte(expectedAmount.add(tolerance));
      
      // Release some tokens
      const releaseAmount = availableAmount.div(2);
      await token.connect(queenAI).releaseEcosystemTokens(otherAccount.address, releaseAmount);
      
      // Check balance
      expect(await token.balanceOf(otherAccount.address)).to.equal(releaseAmount);
    });
    
    it("Should not allow non-Queen to release ecosystem tokens", async function () {
      const { token, otherAccount } = await loadFixture(deployTokenFixture);
      
      await expect(
        token.connect(otherAccount).releaseEcosystemTokens(otherAccount.address, 1000)
      ).to.be.reverted;
    });
  });

  describe("Public Acquisition Tokens", function () {
    it("Should have transferred public acquisition tokens to Queen AI", async function () {
      const { token, queenAI } = await loadFixture(deployTokenFixture);
      
      // Queen AI should have the full public acquisition amount immediately
      expect(await token.balanceOf(queenAI.address)).to.equal(PUBLIC_ACQUISITION_AMOUNT);
    });
    
    it("Should allow Queen AI to transfer public acquisition tokens", async function () {
      const { token, queenAI, otherAccount } = await loadFixture(deployTokenFixture);
      const transferAmount = ethers.utils.parseEther("1000000");
      
      // Queen AI can transfer tokens immediately
      await token.connect(queenAI).transfer(otherAccount.address, transferAmount);
      
      // Check balance
      expect(await token.balanceOf(otherAccount.address)).to.equal(transferAmount);
      expect(await token.balanceOf(queenAI.address)).to.equal(PUBLIC_ACQUISITION_AMOUNT.sub(transferAmount));
    });
  });
});
