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
  const vesting = process.env.VESTING_MANAGER_ADDRESS || '0xeb8EE79C8c93052aF2e101dea8c9ABfcD9F1088b';
  const ecosystem = process.env.ECOSYSTEM_MANAGER_ADDRESS || '0xE30FBbb8a278d75846B485F6C15363b9c4953DC0';
  const treasury = process.env.TREASURY_VAULT_ADDRESS || '0x40Fc44E22c9E3B98be724d6E4a3e773702Ab302E';
  const privateSale = process.env.PRIVATE_SALE_ADDRESS || '0xc801977eA4c3dAA93ca18e00aB07625923714484';
  const queenController = process.env.QUEEN_CONTROLLER_ADDRESS || '0xf7435917202342A93A4bD52640CB0df19f0666bB';
  const liquidity = process.env.LIQUIDITY_SENTINEL_ADDRESS || '0x38fBbe174FaEaaa17aB9b53E8B64d96B297846f0';
  const governance = process.env.GOVERNANCE_MANAGER_ADDRESS || '0x69F0A899C1a3467305d80629017c4fA5AaaDA077';
  const emergency = process.env.EMERGENCY_SYSTEM_ADDRESS || '0x98624BAA37bD4e1f89D8cA9658622967639911A4';
  if (!rpcUrl || !pk) throw new Error('SEPOLIA_RPC_URL and PRIVATE_KEY are required');

  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const wallet = new ethers.Wallet(pk, provider);

  const artifactPath = path.join(__dirname, '..', 'artifacts', 'src', 'core', 'SystemDashboard.sol', 'SystemDashboard.json');
  const artifact = JSON.parse(await readFile(artifactPath, 'utf8'));
  const { abi, bytecode } = artifact;

  console.log('Deploying SystemDashboard with wallet:', wallet.address);
  const factory = new ethers.ContractFactory(abi, bytecode, wallet);
  const contract = await factory.deploy(
    omk,
    vesting,
    ecosystem,
    treasury,
    privateSale,
    queenController,
    liquidity,
    governance,
    emergency
  );
  console.log('TX:', contract.deploymentTransaction()?.hash);
  const receipt = await contract.deploymentTransaction().wait(2);
  const address = await contract.getAddress();
  console.log('SystemDashboard deployed at:', address);
  console.log('Block:', receipt.blockNumber);
}

main().catch((e) => { console.error(e); process.exit(1); });
