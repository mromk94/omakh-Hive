import { HardhatUserConfig } from "hardhat/types";
import "@nomiclabs/hardhat-ethers";
import "@nomiclabs/hardhat-etherscan";
import "hardhat-gas-reporter";
import "solidity-coverage";
import "hardhat-deploy";
import "hardhat-contract-sizer";
import "hardhat-abi-exporter";
import "@openzeppelin/hardhat-upgrades";
import "@typechain/hardhat";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

// Extend the HardhatUserConfig type to include namedAccounts
declare module "hardhat/types/config" {
  interface HardhatUserConfig {
    namedAccounts?: {
      [name: string]: string | number | { [network: string]: null | number | string };
    };
  }
}

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
      viaIR: true,
    },
  },
  gasReporter: {
    enabled: process.env.REPORT_GAS === "true",
    currency: "USD",
    coinmarketcap: process.env.COINMARKETCAP_API_KEY,
    token: "ETH",
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY,
  },
  paths: {
    sources: "./src",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  },
  mocha: {
    timeout: 40000,
  },
  namedAccounts: {
    deployer: {
      default: 0,
    },
    approver1: {
      default: 1,
    },
    approver2: {
      default: 2,
    },
    approver3: {
      default: 3,
    },
  },
  // @ts-ignore - Hardhat plugin types are not properly recognized
  contractSizer: {
    alphaSort: true,
    disambiguatePaths: false,
    runOnCompile: true,
    strict: true,
  },
  // @ts-ignore - Hardhat plugin types are not properly recognized
  abiExporter: {
    path: "./abis",
    runOnCompile: true,
    clear: true,
    flat: false, // Changed to false to avoid TreasuryVault naming conflict
    only: [],
    spacing: 2,
    pretty: false,
  },
};

export default config;