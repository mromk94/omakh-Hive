import 'dotenv/config';
import path from 'path';
import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { ethers } from 'ethers';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  const rpcUrl = process.env.SEPOLIA_RPC_URL;
  const pk = process.env.PRIVATE_KEY;
  const omk = process.env.OMK_TOKEN || '0x9654B4F2AC47BF46884d69BcCC636ef5A9c48632';
  const admin = process.env.ADMIN_ADDRESS || '0xd4a3209ff4ADf36d6e43eeDC41A8C705e25708c1';
  const queen = process.env.QUEEN_ADDRESS || admin;
  const treasury = process.env.TREASURY_VAULT_ADDRESS || '0x40Fc44E22c9E3B98be724d6E4a3e773702Ab302E';
  const liquidity = process.env.LIQUIDITY_SENTINEL_ADDRESS || '0x38fBbe174FaEaaa17aB9b53E8B64d96B297846f0';
  if (!rpcUrl || !pk) throw new Error('SEPOLIA_RPC_URL and PRIVATE_KEY are required');

  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const wallet = new ethers.Wallet(pk, provider);

  const artifactPath = path.join(__dirname, '..', 'artifacts', 'src', 'core', 'QueenController.sol', 'QueenController.json');
  const artifact = JSON.parse(await readFile(artifactPath, 'utf8'));
  const { abi, bytecode } = artifact;

  console.log('Deploying QueenController with wallet:', wallet.address);
  const factory = new ethers.ContractFactory(abi, bytecode, wallet);
  const contract = await factory.deploy(admin, queen, omk);
  console.log('TX:', contract.deploymentTransaction()?.hash);
  await contract.deploymentTransaction().wait(2);
  const address = await contract.getAddress();
  console.log('QueenController deployed at:', address);

  // Wire treasury and liquidity addresses
  const qc = new ethers.Contract(address, abi, wallet);
  let tx = await qc.setTreasuryVault(treasury);
  await tx.wait();
  console.log('setTreasuryVault ok');
  tx = await qc.setLiquiditySentinel(liquidity);
  await tx.wait();
  console.log('setLiquiditySentinel ok');
}

main().catch((e) => { console.error(e); process.exit(1); });
