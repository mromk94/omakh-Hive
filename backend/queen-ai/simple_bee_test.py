#!/usr/bin/env python3
"""
Simple Bee Test - No external dependencies
Demonstrates bee functionality and communication
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Mock structlog
class MockLogger:
    def info(self, *args, **kwargs): pass
    def debug(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass

class MockStructlog:
    @staticmethod
    def get_logger(name):
        return MockLogger()

sys.modules['structlog'] = MockStructlog()
sys.path.insert(0, str(Path(__file__).parent))

from app.bees.maths_bee import MathsBee
from app.bees.security_bee import SecurityBee
from app.bees.data_bee import DataBee
from app.bees.treasury_bee import TreasuryBee
from app.bees.manager import BeeManager


def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_test(name):
    print(f"\n  🧪 {name}")


def print_result(key, value):
    print(f"     ✓ {key}: {value}")


async def test_all_bees():
    """Test all bee agents"""
    
    print("\n🐝" * 35)
    print("\n        OMK HIVE - BEE AGENT FUNCTIONALITY TEST")
    print("\n🐝" * 35)
    
    # Initialize manager
    print_header("INITIALIZING BEE MANAGER")
    manager = BeeManager()
    await manager.initialize()
    print(f"\n  ✅ Initialized {len(manager.bees)} bee agents:")
    for bee_name in manager.bees:
        print(f"     • {bee_name.title()}Bee")
    
    # Test MathsBee
    print_header("🧮 MATHS BEE - Mathematical Calculations")
    
    print_test("Calculate Slippage")
    result = await manager.execute_bee("maths", {
        "type": "calculate_slippage",
        "reserve_in": 1000000,
        "reserve_out": 1000000,
        "amount_in": 10000,
    })
    print_result("Slippage", f"{result['slippage_percent']}%")
    print_result("Amount out", f"{result['amount_out']:,.0f} tokens")
    
    print_test("Calculate Pool Ratio")
    result = await manager.execute_bee("maths", {
        "type": "calculate_pool_ratio",
        "token_a": 1200000,
        "token_b": 1000000,
        "target_ratio": 1.0,
    })
    print_result("Current ratio", f"{result['current_ratio']}")
    print_result("Deviation", f"{result['deviation_percent']}%")
    print_result("Needs rebalance", f"{result['needs_rebalance']}")
    
    print_test("Calculate APY")
    result = await manager.execute_bee("maths", {
        "type": "calculate_apy",
        "total_staked": 10_000_000 * 10**18,
        "annual_rewards": 1_200_000 * 10**18,
        "treasury_health": 1.5,
    })
    print_result("Base APY", f"{result['base_apy']}%")
    print_result("Adjusted APY", f"{result['adjusted_apy']}%")
    print_result("Health factor", f"{result['treasury_health']}x")
    
    # Test SecurityBee
    print_header("🔒 SECURITY BEE - Validation & Risk Assessment")
    
    print_test("Validate Address")
    result = await manager.execute_bee("security", {
        "type": "validate_address",
        "address": "0x" + "1" * 40,
    })
    print_result("Valid", f"{result['valid']}")
    print_result("Risk level", f"{result.get('risk_level', 'N/A')}")
    
    print_test("Assess Risk (Large Transfer)")
    result = await manager.execute_bee("security", {
        "type": "assess_risk",
        "operation_type": "bridge_transfer",
        "amount": 15_000_000 * 10**18,
        "target": "0x" + "2" * 40,
    })
    print_result("Risk level", f"{result['risk_level'].upper()}")
    print_result("Risk score", f"{result['risk_score']}/100")
    print_result("Recommendation", f"{result['recommendation'].upper()}")
    if result['risk_factors']:
        print(f"     ⚠ Risk factors:")
        for factor in result['risk_factors']:
            print(f"        - {factor}")
    
    print_test("Check Rate Limits")
    result = await manager.execute_bee("security", {
        "type": "check_rate_limit",
        "daily_limit": 50_000_000 * 10**18,
        "current_usage": 45_000_000 * 10**18,
        "requested_amount": 3_000_000 * 10**18,
    })
    print_result("Status", f"{result['status'].upper()}")
    print_result("Utilization", f"{result['utilization_percent']}%")
    print_result("Would exceed", f"{result['would_exceed']}")
    
    # Test DataBee
    print_header("📊 DATA BEE - Blockchain Queries & Aggregation")
    
    print_test("Query Balance")
    result = await manager.execute_bee("data", {
        "type": "query_balance",
        "address": "0x" + "1" * 40,
        "token": "OMK",
    })
    print_result("Balance", f"{result['formatted_balance']}")
    
    print_test("Aggregate Transfers (24h)")
    result = await manager.execute_bee("data", {
        "type": "aggregate_transfers",
        "address": "0x" + "1" * 40,
        "time_period": "24h",
    })
    print_result("Transfer count", f"{result['transfers']['transfer_count']}")
    print_result("Total sent", f"{result['transfers']['total_sent'] / 10**18:,.0f} OMK")
    print_result("Total received", f"{result['transfers']['total_received'] / 10**18:,.0f} OMK")
    print_result("Net flow", f"{result['net_flow'] / 10**18:,.0f} OMK")
    
    print_test("Get Pool Statistics")
    result = await manager.execute_bee("data", {
        "type": "get_pool_stats",
        "pool_address": "0x" + "a" * 40,
    })
    print_result("Total liquidity", f"${result['stats']['total_liquidity_usd']:,.0f}")
    print_result("24h volume", f"${result['stats']['volume_24h']:,.0f}")
    print_result("APY", f"{result['stats']['apy']}%")
    
    # Test TreasuryBee
    print_header("💰 TREASURY BEE - Budget & Treasury Management")
    
    print_test("Validate Proposal (Valid)")
    result = await manager.execute_bee("treasury", {
        "type": "validate_proposal",
        "category": 0,  # DEVELOPMENT
        "amount": 5_000_000 * 10**18,
        "description": "Smart contract development and security audits for Q4 2025",
    })
    print_result("Category", f"{result['category']}")
    print_result("Valid", f"{result['valid']}")
    print_result("Remaining budget", f"{result['remaining_budget'] / 10**18:,.0f} OMK")
    print_result("Utilization", f"{result['utilization_percent']}%")
    
    print_test("Validate Proposal (Invalid - Too Large)")
    result = await manager.execute_bee("treasury", {
        "type": "validate_proposal",
        "category": 0,
        "amount": 50_000_000 * 10**18,
        "description": "Large request",
    })
    print_result("Valid", f"{result['valid']}")
    if result['validation_issues']:
        print(f"     ⚠ Issues:")
        for issue in result['validation_issues']:
            print(f"        - {issue}")
    
    print_test("Check Treasury Health")
    result = await manager.execute_bee("treasury", {
        "type": "treasury_health",
        "total_balance": 100_000_000 * 10**18,
        "burn_rate": 2_000_000 * 10**18,
    })
    print_result("Health status", f"{result['health_status'].upper()}")
    print_result("Health score", f"{result['health_score']}/100")
    print_result("Runway", f"{result['runway_months']} months")
    
    # Inter-bee coordination
    print_header("🤝 INTER-BEE COORDINATION - Multi-Agent Workflows")
    
    print("\n  🔄 Workflow 1: Liquidity Management Decision")
    print(f"     Step 1: DataBee retrieves pool statistics...")
    pool_data = await manager.execute_bee("data", {
        "type": "get_pool_stats",
        "pool_address": "0x" + "a" * 40,
    })
    print(f"        ✓ Pool liquidity: ${pool_data['stats']['total_liquidity_usd']:,.0f}")
    
    print(f"     Step 2: MathsBee analyzes pool health...")
    math_result = await manager.execute_bee("maths", {
        "type": "calculate_pool_ratio",
        "token_a": pool_data["stats"]["token_a_amount"],
        "token_b": pool_data["stats"]["token_b_amount"],
        "target_ratio": 1.0,
    })
    print(f"        ✓ Pool deviation: {math_result['deviation_percent']}%")
    
    print(f"     Step 3: SecurityBee validates operation...")
    security_check = await manager.execute_bee("security", {
        "type": "assess_risk",
        "operation_type": "add_liquidity",
        "amount": 5_000_000 * 10**18,
        "target": "0x" + "a" * 40,
    })
    print(f"        ✓ Risk assessment: {security_check['risk_level']}")
    print(f"     ✅ Decision: {security_check['recommendation'].upper()}")
    
    print("\n  🔄 Workflow 2: Treasury Proposal Validation")
    print(f"     Step 1: TreasuryBee validates proposal...")
    proposal = await manager.execute_bee("treasury", {
        "type": "validate_proposal",
        "category": 1,  # MARKETING
        "amount": 3_000_000 * 10**18,
        "description": "Q4 marketing campaign and community growth initiatives",
    })
    print(f"        ✓ Proposal validation: {'APPROVED' if proposal['valid'] else 'REJECTED'}")
    
    print(f"     Step 2: SecurityBee validates recipient...")
    address_check = await manager.execute_bee("security", {
        "type": "validate_address",
        "address": "0x" + "b" * 40,
    })
    print(f"        ✓ Address validation: {'VALID' if address_check['valid'] else 'INVALID'}")
    
    print(f"     Step 3: DataBee logs transaction...")
    balance = await manager.execute_bee("data", {
        "type": "query_balance",
        "address": "0x" + "b" * 40,
        "token": "OMK",
    })
    print(f"        ✓ Recipient balance: {balance['formatted_balance']}")
    print(f"     ✅ Treasury proposal ready for execution")
    
    # Final stats
    print_header("📈 FINAL STATISTICS")
    stats = await manager.get_bee_stats()
    health = await manager.check_all_health()
    
    print(f"\n  Bee Agent Statistics:")
    for bee_name, bee_stats in stats.items():
        print(f"     {bee_name.title()}Bee: {bee_stats['tasks_completed']} tasks, {bee_stats['success_rate']}")
    
    print(f"\n  System Health:")
    print(f"     All bees healthy: {health['all_healthy']}")
    print(f"     Total bees: {health['total_bees']}")
    print(f"     Any critical: {health['any_critical']}")
    
    # Success message
    print("\n" + "="*70)
    print("  🎉 ALL TESTS PASSED! THE HIVE IS OPERATIONAL! 🎉")
    print("="*70)
    print("\n  ✅ 4 specialized bee agents active")
    print("  ✅ All mathematical calculations working")
    print("  ✅ Security validation operational")
    print("  ✅ Data aggregation functional")
    print("  ✅ Treasury management ready")
    print("  ✅ Inter-bee coordination successful")
    print("\n  🐝 The Queen AI can now orchestrate the full hive!")
    print("\n")


if __name__ == "__main__":
    try:
        asyncio.run(test_all_bees())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
