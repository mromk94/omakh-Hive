import { HardhatUserConfig } from "hardhat/types";
import "@nomicfoundation/hardhat-ethers";
import "@nomicfoundation/hardhat-verify";
// Temporarily disabled plugins for Hardhat v3 migration
// import "hardhat-gas-reporter";
// import "solidity-coverage";
// import "hardhat-contract-sizer";
// import "hardhat-abi-exporter";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();


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
  networks: {
    localhost: {
      type: "http",
      url: "http://127.0.0.1:8545",
      chainId: 31337,
    },
    sepolia: {
      type: "http",
      url: process.env.SEPOLIA_RPC_URL || "https://ethereum-sepolia.publicnode.com",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 11155111,
    },
    mainnet: {
      type: "http",
      url: process.env.MAINNET_RPC_URL || "https://ethereum.publicnode.com",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 1,
    },
  },
  // gasReporter: {
  //   enabled: process.env.REPORT_GAS === "true",
  //   currency: "USD",
  //   coinmarketcap: process.env.COINMARKETCAP_API_KEY,
  //   token: "ETH",
  // },
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
  // contractSizer and abiExporter temporarily disabled for v3 upgrade
};

export default config;