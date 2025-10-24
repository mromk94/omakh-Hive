import 'dotenv/config';
import { readFile } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { ethers } from 'ethers';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  const rpcUrl = process.env.SEPOLIA_RPC_URL;
  const pk = process.env.PRIVATE_KEY;
  const omk = process.env.OMK_TOKEN || '0x9654B4F2AC47BF46884d69BcCC636ef5A9c48632';
  const admin = process.env.ADMIN_ADDRESS || '0xd4a3209ff4ADf36d6e43eeDC41A8C705e25708c1';
  const founders = process.env.FOUNDERS_WALLET || admin; // testnet: use admin as founders
  const advisorsManager = process.env.ADVISORS_MANAGER_ADDRESS || '0x026d1f8D1eB8094432daD9dd9d92B233f1CfEAF7';
  const ecosystemManager = process.env.ECOSYSTEM_MANAGER_ADDRESS || '0xE30FBbb8a278d75846B485F6C15363b9c4953DC0';
  if (!rpcUrl || !pk) throw new Error('SEPOLIA_RPC_URL and PRIVATE_KEY are required');

  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const wallet = new ethers.Wallet(pk, provider);

  const artifactPath = path.join(__dirname, '..', 'artifacts', 'src', 'core', 'VestingManager.sol', 'VestingManager.json');
  const artifact = JSON.parse(await readFile(artifactPath, 'utf8'));
  const { abi, bytecode } = artifact;

  console.log('Deploying VestingManager with wallet:', wallet.address);
  const factory = new ethers.ContractFactory(abi, bytecode, wallet);
  const contract = await factory.deploy(omk, admin, founders, advisorsManager, ecosystemManager);
  console.log('TX:', contract.deploymentTransaction()?.hash);
  const receipt = await contract.deploymentTransaction().wait(2);
  const address = await contract.getAddress();
  console.log('VestingManager deployed at:', address);
  console.log('Block:', receipt.blockNumber);
}

main().catch((e) => { console.error(e); process.exit(1); });
