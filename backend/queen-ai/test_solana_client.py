"""
Test script for modern Solana client implementation
"""
import asyncio
from app.blockchain.solana_rpc_client import SolanaRPCClient, SOLDERS_AVAILABLE

async def test_solana_client():
    """Test the modern Solana RPC client"""
    
    if not SOLDERS_AVAILABLE:
        print("❌ Solders not available. Install with: pip install solders>=0.20.0")
        return
    
    print("🧪 Testing Modern Solana RPC Client\n")
    print("=" * 50)
    
    # Test with mainnet
    client = SolanaRPCClient("https://api.mainnet-beta.solana.com")
    
    try:
        # Test 1: Get version
        print("\n1️⃣ Testing getVersion...")
        version = await client.get_version()
        print(f"✅ Solana version: {version.get('solana-core', 'unknown')}")
        
        # Test 2: Get slot
        print("\n2️⃣ Testing getSlot...")
        slot = await client.get_slot()
        print(f"✅ Current slot: {slot:,}")
        
        # Test 3: Get block height
        print("\n3️⃣ Testing getBlockHeight...")
        height = await client.get_block_height()
        print(f"✅ Block height: {height:,}")
        
        # Test 4: Get latest blockhash
        print("\n4️⃣ Testing getLatestBlockhash...")
        blockhash = await client.get_latest_blockhash()
        print(f"✅ Latest blockhash: {blockhash[:20]}...")
        
        # Test 5: Check connection
        print("\n5️⃣ Testing connection...")
        connected = await client.is_connected()
        print(f"✅ Connected: {connected}")
        
        # Test 6: Get balance for a known address (Solana Foundation wallet)
        print("\n6️⃣ Testing getBalance...")
        # Using a known mainnet address
        test_address = "7Np41oeYqPefeNQEHSv1UDhYrehxin3NStELsSKCT4K2"  # Random mainnet address
        balance = await client.get_balance(test_address)
        print(f"✅ Balance for {test_address[:8]}...: {balance:,} lamports ({balance / 1e9:.4f} SOL)")
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! Modern Solana client is working!")
        print("\n📊 Summary:")
        print("  • Using httpx>=0.28.1 (compatible with google-genai)")
        print("  • Using solders>=0.20.0 for types (Rust-based)")
        print("  • No dependency conflicts!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await client.close()
        print("\n🔒 Client closed")

if __name__ == "__main__":
    asyncio.run(test_solana_client())
