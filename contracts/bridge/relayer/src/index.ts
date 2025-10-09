import { ethers } from 'ethers';
import { Connection, PublicKey, Keypair } from '@solana/web3.js';
import { Program, AnchorProvider, Wallet } from '@project-serum/anchor';
import { BridgeRelayer } from './relayer';
import { config } from './config';

/**
 * OMK Bridge Relayer Service
 * 
 * Monitors both Ethereum and Solana chains for bridge events
 * and relays transactions between them.
 * 
 * Flow:
 * 1. User locks OMK on Ethereum
 * 2. Relayer detects lock event
 * 3. Relayer calls Solana program to mint wrapped OMK
 * 4. User burns wrapped OMK on Solana
 * 5. Relayer detects burn event
 * 6. Relayer validates with other relayers
 * 7. Relayer calls Ethereum bridge to release OMK
 */

async function main() {
    console.log('🌉 Starting OMK Bridge Relayer...\n');

    // Initialize Ethereum provider
    const ethProvider = new ethers.providers.JsonRpcProvider(config.ethereum.rpcUrl);
    const ethWallet = new ethers.Wallet(config.ethereum.privateKey, ethProvider);
    
    console.log(`✅ Ethereum connected: ${config.ethereum.network}`);
    console.log(`   Relayer address: ${ethWallet.address}\n`);

    // Initialize Solana connection
    const solConnection = new Connection(config.solana.rpcUrl, 'confirmed');
    const solWallet = Keypair.fromSecretKey(
        Buffer.from(config.solana.privateKey, 'base64')
    );
    
    console.log(`✅ Solana connected: ${config.solana.network}`);
    console.log(`   Relayer pubkey: ${solWallet.publicKey.toBase58()}\n`);

    // Initialize bridge relayer
    const relayer = new BridgeRelayer({
        ethProvider,
        ethWallet,
        ethBridgeAddress: config.ethereum.bridgeAddress,
        solConnection,
        solWallet,
        solBridgeProgramId: new PublicKey(config.solana.bridgeProgramId),
    });

    // Start monitoring
    await relayer.start();

    // Handle graceful shutdown
    process.on('SIGINT', async () => {
        console.log('\n\n⏹️  Shutting down relayer...');
        await relayer.stop();
        process.exit(0);
    });

    process.on('SIGTERM', async () => {
        console.log('\n\n⏹️  Shutting down relayer...');
        await relayer.stop();
        process.exit(0);
    });
}

main().catch((error) => {
    console.error('❌ Fatal error:', error);
    process.exit(1);
});
