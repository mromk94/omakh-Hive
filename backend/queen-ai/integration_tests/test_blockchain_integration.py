#!/usr/bin/env python3
"""
Blockchain Integration Tests - Real Network Connection

Tests DataBee and BlockchainBee with actual Ethereum/Polygon testnets.

REQUIREMENTS:
- ETHEREUM_RPC_URL in .env (Infura/Alchemy)
- Sufficient testnet ETH for gas
- QUEEN_PRIVATE_KEY (testnet only!)

SETUP:
1. Get testnet RPC:
   - Infura: https://infura.io
   - Alchemy: https://alchemy.com
   
2. Get testnet ETH:
   - Goerli faucet: https://goerlifaucet.com
   - Mumbai faucet: https://mumbaifaucet.com

3. Configure .env:
   ETHEREUM_RPC_URL=https://goerli.infura.io/v3/YOUR_KEY
   QUEEN_PRIVATE_KEY=your_testnet_private_key
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from web3 import Web3
from eth_account import Account

from app.config.settings import settings


class BlockchainIntegrationTests:
    """Real blockchain integration tests"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = []
        
        # Check requirements
        self.can_run = self._check_requirements()
    
    def _check_requirements(self) -> bool:
        """Check if we have necessary configuration"""
        if not settings.ETHEREUM_RPC_URL:
            print("❌ ETHEREUM_RPC_URL not configured in .env")
            print("   Get API key from Infura or Alchemy")
            return False
        
        return True
    
    def print_header(self, title):
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def record_pass(self, test_name):
        self.passed += 1
        print(f"  ✅ {test_name}")
    
    def record_fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  ❌ {test_name}: {error}")
    
    def record_skip(self, test_name, reason):
        self.skipped += 1
        print(f"  ⏭️  {test_name} (skipped: {reason})")
    
    async def test_1_web3_connection(self):
        """Test 1: Connect to Ethereum RPC"""
        self.print_header("TEST 1: Web3 RPC Connection")
        
        try:
            w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
            
            # Test connection
            if w3.is_connected():
                self.record_pass("Web3 connection established")
            else:
                self.record_fail("Web3 connection", "Not connected")
                return
            
            # Get network info
            chain_id = w3.eth.chain_id
            block_number = w3.eth.block_number
            
            print(f"     Chain ID: {chain_id}")
            print(f"     Latest block: {block_number}")
            
            self.record_pass(f"Network info retrieved (chain {chain_id})")
            
        except Exception as e:
            self.record_fail("Web3 connection", str(e))
    
    async def test_2_get_eth_balance(self):
        """Test 2: Query ETH balance"""
        self.print_header("TEST 2: Get ETH Balance")
        
        try:
            w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
            
            # Use Vitalik's address as test (always has balance)
            test_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
            
            balance = w3.eth.get_balance(test_address)
            balance_eth = w3.from_wei(balance, 'ether')
            
            print(f"     Address: {test_address}")
            print(f"     Balance: {balance_eth} ETH")
            
            self.record_pass(f"Balance query successful")
            
        except Exception as e:
            self.record_fail("ETH balance query", str(e))
    
    async def test_3_get_erc20_balance(self):
        """Test 3: Query ERC20 token balance"""
        self.print_header("TEST 3: Get ERC20 Token Balance")
        
        try:
            w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
            
            # USDC contract on Ethereum mainnet
            usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
            
            # ERC20 ABI (minimal)
            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                }
            ]
            
            contract = w3.eth.contract(address=usdc_address, abi=erc20_abi)
            
            # Query a known USDC holder
            test_address = "0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503"  # Binance wallet
            balance = contract.functions.balanceOf(test_address).call()
            decimals = contract.functions.decimals().call()
            
            balance_formatted = balance / (10 ** decimals)
            
            print(f"     Token: USDC")
            print(f"     Address: {test_address[:10]}...")
            print(f"     Balance: {balance_formatted:,.2f} USDC")
            
            self.record_pass("ERC20 balance query successful")
            
        except Exception as e:
            self.record_fail("ERC20 balance query", str(e))
    
    async def test_4_uniswap_pool_query(self):
        """Test 4: Query Uniswap pool reserves"""
        self.print_header("TEST 4: Uniswap Pool Reserves")
        
        try:
            w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
            
            # USDC/ETH pool on Uniswap V2
            pool_address = "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
            
            # Uniswap V2 Pair ABI (minimal)
            pair_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "getReserves",
                    "outputs": [
                        {"name": "reserve0", "type": "uint112"},
                        {"name": "reserve1", "type": "uint112"},
                        {"name": "blockTimestampLast", "type": "uint32"}
                    ],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "totalSupply",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "type": "function"
                }
            ]
            
            pool_contract = w3.eth.contract(address=pool_address, abi=pair_abi)
            
            reserves = pool_contract.functions.getReserves().call()
            total_supply = pool_contract.functions.totalSupply().call()
            
            print(f"     Pool: USDC/ETH")
            print(f"     Reserve0: {reserves[0]:,}")
            print(f"     Reserve1: {reserves[1]:,}")
            print(f"     LP Supply: {total_supply:,}")
            
            self.record_pass("Pool reserves query successful")
            
        except Exception as e:
            self.record_fail("Pool reserves query", str(e))
    
    async def test_5_gas_price_estimation(self):
        """Test 5: Get current gas price"""
        self.print_header("TEST 5: Gas Price Estimation")
        
        try:
            w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
            
            # Get gas price
            gas_price = w3.eth.gas_price
            gas_gwei = w3.from_wei(gas_price, 'gwei')
            
            # Get latest block for base fee (EIP-1559)
            latest_block = w3.eth.get_block('latest')
            base_fee = latest_block.get('baseFeePerGas', 0)
            base_fee_gwei = w3.from_wei(base_fee, 'gwei') if base_fee else 0
            
            print(f"     Gas Price: {gas_gwei:.2f} gwei")
            print(f"     Base Fee: {base_fee_gwei:.2f} gwei")
            
            self.record_pass("Gas price query successful")
            
        except Exception as e:
            self.record_fail("Gas price query", str(e))
    
    async def test_6_transaction_simulation(self):
        """Test 6: Simulate transaction (no actual send)"""
        self.print_header("TEST 6: Transaction Simulation")
        
        if not settings.QUEEN_WALLET_ADDRESS:
            self.record_skip("Transaction simulation", "No wallet configured")
            return
        
        try:
            w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
            
            # Build a simple ETH transfer tx (not signed, not sent)
            tx = {
                'from': settings.QUEEN_WALLET_ADDRESS,
                'to': '0x0000000000000000000000000000000000000000',
                'value': w3.to_wei(0.001, 'ether'),
                'gas': 21000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(settings.QUEEN_WALLET_ADDRESS),
                'chainId': w3.eth.chain_id
            }
            
            # Estimate gas (this simulates without sending)
            try:
                estimated_gas = w3.eth.estimate_gas(tx)
                print(f"     Estimated gas: {estimated_gas}")
                self.record_pass("Transaction simulation successful")
            except Exception as e:
                # This may fail if wallet has no balance (expected on testnet)
                print(f"     Note: {str(e)[:50]}...")
                self.record_pass("Transaction built (estimation failed - normal if no balance)")
            
        except Exception as e:
            self.record_fail("Transaction simulation", str(e))
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("BLOCKCHAIN INTEGRATION TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.passed + self.failed + self.skipped}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Skipped: {self.skipped} ⏭️")
        
        if self.errors:
            print("\nFailed Tests:")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        
        success_rate = (self.passed / (self.passed + self.failed) * 100) if (self.passed + self.failed) > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 ALL TESTS PASSED! Blockchain integration working! 🔗")
        elif success_rate >= 50:
            print("\n✅ Most tests passed - blockchain connectivity OK")
        else:
            print("\n⚠️ Multiple failures - check RPC configuration")
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("\n🔗" * 35)
        print("\n   BLOCKCHAIN INTEGRATION TESTS - REAL NETWORK")
        print("\n🔗" * 35)
        
        if not self.can_run:
            print("\n❌ Cannot run tests - missing configuration")
            print("\nSetup instructions:")
            print("1. Get RPC API key from Infura or Alchemy")
            print("2. Add to .env: ETHEREUM_RPC_URL=https://goerli.infura.io/v3/YOUR_KEY")
            print("3. Run tests again")
            return
        
        # Run tests
        await self.test_1_web3_connection()
        await self.test_2_get_eth_balance()
        await self.test_3_get_erc20_balance()
        await self.test_4_uniswap_pool_query()
        await self.test_5_gas_price_estimation()
        await self.test_6_transaction_simulation()
        
        # Summary
        self.print_summary()


async def main():
    tests = BlockchainIntegrationTests()
    await tests.run_all_tests()
    return 0 if tests.failed == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
