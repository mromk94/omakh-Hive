import { loadFixture, time } from "@nomicfoundation/hardhat-network-helpers";
import { expect } from "chai";
import { ethers } from "hardhat";

describe("OMKToken", function () {
  // We define a fixture to reuse the same setup in every test.
  // We use loadFixture to run this setup once, snapshot that state,
  // and reset Hardhat Network to that snapshot in every test.
  async function deployTokenFixture() {
    // Get the ContractFactory and Signers here.
    const [owner, minter, pauser, otherAccount] = await ethers.getSigners();

    // Deploy the contract
    const OMKToken = await ethers.getContractFactory("OMKToken");
    const token = await OMKToken.deploy("OMK Token", "OMK", owner.address);

    // Grant MINTER_ROLE and PAUSER_ROLE to the respective accounts
    await token.connect(owner).grantRole(await token.MINTER_ROLE(), minter.address);
    await token.connect(owner).grantRole(await token.PAUSER_ROLE(), pauser.address);

    return { token, owner, minter, pauser, otherAccount };
  }

  describe("Deployment", function () {
    it("Should set the right name and symbol", async function () {
      const { token } = await loadFixture(deployTokenFixture);
      expect(await token.name()).to.equal("OMK Token");
      expect(await token.symbol()).to.equal("OMK");
    });

    it("Should grant DEFAULT_ADMIN_ROLE to the deployer", async function () {
      const { token, owner } = await loadFixture(deployTokenFixture);
      expect(await token.hasRole(await token.DEFAULT_ADMIN_ROLE(), owner.address)).to.be.true;
    });
  });

  describe("Minting", function () {
    it("Should allow minter to mint tokens", async function () {
      const { token, minter, otherAccount } = await loadFixture(deployTokenFixture);
      const amount = ethers.parseEther("1000");
      
      await expect(token.connect(minter).mint(otherAccount.address, amount))
        .to.emit(token, "TokensMinted")
        .withArgs(otherAccount.address, amount);
      
      expect(await token.balanceOf(otherAccount.address)).to.equal(amount);
    });

    it("Should not allow non-minters to mint tokens", async function () {
      const { token, otherAccount } = await loadFixture(deployTokenFixture);
      const amount = ethers.parseEther("1000");
      
      await expect(
        token.connect(otherAccount).mint(otherAccount.address, amount)
      ).to.be.revertedWithCustomError(token, "AccessControlUnauthorizedAccount");
    });

    it("Should not allow minting beyond max supply", async function () {
      const { token, minter, otherAccount } = await loadFixture(deployTokenFixture);
      const maxSupply = await token.MAX_SUPPLY();
      const amount = maxSupply + BigInt(1);
      
      await expect(
        token.connect(minter).mint(otherAccount.address, amount)
      ).to.be.revertedWith("OMKToken: max supply exceeded");
    });
  });

  describe("Pausing", function () {
    it("Should allow pauser to pause and unpause", async function () {
      const { token, pauser } = await loadFixture(deployTokenFixture);
      
      await token.connect(pauser).pause();
      expect(await token.paused()).to.be.true;
      
      await token.connect(pauser).unpause();
      expect(await token.paused()).to.be.false;
    });

    it("Should not allow non-pausers to pause", async function () {
      const { token, otherAccount } = await loadFixture(deployTokenFixture);
      
      await expect(
        token.connect(otherAccount).pause()
      ).to.be.revertedWithCustomError(token, "AccessControlUnauthorizedAccount");
    });

    it("Should not allow transfers when paused", async function () {
      const { token, minter, owner, otherAccount, pauser } = await loadFixture(deployTokenFixture);
      const amount = ethers.parseEther("1000");
      
      // Mint some tokens first
      await token.connect(minter).mint(owner.address, amount);
      
      // Pause the contract
      await token.connect(pauser).pause();
      
      // Try to transfer - check for the correct error message
      await expect(
        token.connect(owner).transfer(otherAccount.address, amount)
      ).to.be.revertedWithCustomError(token, "EnforcedPause");
    });
  });

  describe("Queen Controller", function () {
    it("Should allow admin to set queen controller", async function () {
      const { token, owner, otherAccount } = await loadFixture(deployTokenFixture);
      
      await expect(token.connect(owner).setQueenController(otherAccount.address))
        .to.emit(token, "QueenControllerUpdated")
        .withArgs(ethers.ZeroAddress, otherAccount.address);
      
      expect(await token.queenController()).to.equal(otherAccount.address);
      expect(await token.hasRole(await token.QUEEN_ROLE(), otherAccount.address)).to.be.true;
    });

    it("Should not allow non-admins to set queen controller", async function () {
      const { token, otherAccount } = await loadFixture(deployTokenFixture);
      
      await expect(
        token.connect(otherAccount).setQueenController(otherAccount.address)
      ).to.be.revertedWithCustomError(token, "AccessControlUnauthorizedAccount");
    });
  });

  describe("Transfer Logging", function () {
    it("Should log transfers when learning observer is set", async function () {
      const { token, minter, owner, otherAccount } = await loadFixture(deployTokenFixture);
      const amount = ethers.parseEther("1000");
      
      // Mint some tokens first
      await token.connect(minter).mint(owner.address, amount);
      
      // Set learning observer
      const observer = ethers.Wallet.createRandom().address;
      await token.connect(owner).setLearningObserver(observer);
      
      // Make a transfer
      const tx = await token.connect(owner).transfer(otherAccount.address, amount);
      const receipt = await tx.wait();
      
      // Check for TransferLogged event
      const transferLoggedEvent = receipt?.logs?.find(
        (log) => log.topics[0] === token.interface.getEvent("TransferLogged").topicHash
      );
      
      expect(transferLoggedEvent).to.not.be.undefined;
      
      if (transferLoggedEvent) {
        const decoded = token.interface.decodeEventLog(
          "TransferLogged",
          transferLoggedEvent.data,
          transferLoggedEvent.topics
        );
        
        expect(decoded.from).to.equal(owner.address);
        expect(decoded.to).to.equal(otherAccount.address);
        expect(decoded.amount).to.equal(amount);
      }
    });
  });
});
