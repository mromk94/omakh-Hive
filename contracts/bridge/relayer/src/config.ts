import * as dotenv from 'dotenv';

dotenv.config();

export const config = {
    ethereum: {
        network: process.env.ETH_NETWORK || 'sepolia',
        rpcUrl: process.env.ETH_RPC_URL || 'https://sepolia.infura.io/v3/YOUR_INFURA_KEY',
        bridgeAddress: process.env.ETH_BRIDGE_ADDRESS || '0x...',
        privateKey: process.env.ETH_PRIVATE_KEY || '',
    },
    solana: {
        network: process.env.SOL_NETWORK || 'devnet',
        rpcUrl: process.env.SOL_RPC_URL || 'https://api.devnet.solana.com',
        bridgeProgramId: process.env.SOL_BRIDGE_PROGRAM_ID || '',
        privateKey: process.env.SOL_PRIVATE_KEY || '', // Base64 encoded keypair
    },
    relayer: {
        pollIntervalMs: parseInt(process.env.POLL_INTERVAL_MS || '5000'),
        maxRetries: parseInt(process.env.MAX_RETRIES || '3'),
        retryDelayMs: parseInt(process.env.RETRY_DELAY_MS || '10000'),
    },
};

// Validation
if (!config.ethereum.privateKey) {
    throw new Error('ETH_PRIVATE_KEY not set');
}

if (!config.solana.privateKey) {
    throw new Error('SOL_PRIVATE_KEY not set');
}

console.log('⚙️  Configuration loaded:');
console.log(`   Ethereum Network: ${config.ethereum.network}`);
console.log(`   Solana Network: ${config.solana.network}`);
console.log(`   Poll Interval: ${config.relayer.pollIntervalMs}ms\n`);
