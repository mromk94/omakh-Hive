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
  const admin = process.env.ADMIN_ADDRESS || '0xd4a3209ff4ADf36d6e43eeDC41A8C705e25708c1';
  const queen = process.env.QUEEN_ADDRESS || admin;
  if (!rpcUrl || !pk) throw new Error('SEPOLIA_RPC_URL and PRIVATE_KEY are required');

  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const wallet = new ethers.Wallet(pk, provider);

  const artifactPath = path.join(__dirname, '..', 'artifacts', 'src', 'core', 'LiquiditySentinel.sol', 'LiquiditySentinel.json');
  const artifact = JSON.parse(await readFile(artifactPath, 'utf8'));
  const { abi, bytecode } = artifact;

  console.log('Deploying LiquiditySentinel with wallet:', wallet.address);
  const factory = new ethers.ContractFactory(abi, bytecode, wallet);
  const contract = await factory.deploy(admin, queen);
  console.log('TX:', contract.deploymentTransaction()?.hash);
  const receipt = await contract.deploymentTransaction().wait(2);
  const address = await contract.getAddress();
  console.log('LiquiditySentinel deployed at:', address);
  console.log('Block:', receipt.blockNumber);
}

main().catch((e) => { console.error(e); process.exit(1); });
