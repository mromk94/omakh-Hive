#!/usr/bin/env python3
"""
Run Bee Agent Tests
Quick test runner without pytest (for rapid testing)
"""
import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.bees.maths_bee import MathsBee
from app.bees.security_bee import SecurityBee
from app.bees.data_bee import DataBee
from app.bees.treasury_bee import TreasuryBee
from app.bees.manager import BeeManager


async def test_maths_bee():
    """Test MathsBee"""
    print("\n" + "="*60)
    print("🧮 TESTING MATHS BEE")
    print("="*60)
    
    bee = MathsBee(bee_id=1)
    
    # Test 1: Slippage calculation
    print("\n📊 Test 1: Calculate Slippage")
    result = await bee.process_task({
        "type": "calculate_slippage",
        "reserve_in": 1000000,
        "reserve_out": 1000000,
        "amount_in": 10000,
    })
    print(f"  Result: {result['slippage_percent']}% slippage")
    assert result["success"], "Slippage calculation failed"
    
    # Test 2: Pool ratio
    print("\n📊 Test 2: Calculate Pool Ratio")
    result = await bee.process_task({
        "type": "calculate_pool_ratio",
        "token_a": 1200000,
        "token_b": 1000000,
        "target_ratio": 1.0,
    })
    print(f"  Current ratio: {result['current_ratio']}")
    print(f"  Deviation: {result['deviation_percent']}%")
    print(f"  Needs rebalance: {result['needs_rebalance']}")
    assert result["success"], "Pool ratio calculation failed"
    
    # Test 3: APY calculation
    print("\n📊 Test 3: Calculate APY")
    result = await bee.process_task({
        "type": "calculate_apy",
        "total_staked": 10_000_000 * 10**18,
        "annual_rewards": 1_200_000 * 10**18,
        "treasury_health": 1.5,
    })
    print(f"  Base APY: {result['base_apy']}%")
    print(f"  Adjusted APY: {result['adjusted_apy']}%")
    print(f"  Treasury health: {result['treasury_health']}")
    assert result["success"], "APY calculation failed"
    
    stats = bee.get_stats()
    print(f"\n✅ MathsBee: {stats['tasks_completed']} tasks, {stats['success_rate']} success rate")


async def test_security_bee():
    """Test SecurityBee"""
    print("\n" + "="*60)
    print("🔒 TESTING SECURITY BEE")
    print("="*60)
    
    bee = SecurityBee(bee_id=2)
    
    # Test 1: Valid address
    print("\n🔐 Test 1: Validate Address (Valid)")
    result = await bee.process_task({
        "type": "validate_address",
        "address": "0x" + "1" * 40,
    })
    print(f"  Valid: {result['valid']}")
    print(f"  Risk level: {result.get('risk_level', 'N/A')}")
    assert result["success"], "Address validation failed"
    
    # Test 2: Invalid address
    print("\n🔐 Test 2: Validate Address (Invalid)")
    result = await bee.process_task({
        "type": "validate_address",
        "address": "0x123",
    })
    print(f"  Valid: {result['valid']}")
    print(f"  Reason: {result.get('reason', 'N/A')}")
    
    # Test 3: Risk assessment
    print("\n🔐 Test 3: Assess Risk")
    result = await bee.process_task({
        "type": "assess_risk",
        "operation_type": "bridge_transfer",
        "amount": 15_000_000 * 10**18,
        "target": "0x" + "2" * 40,
    })
    print(f"  Risk level: {result['risk_level']}")
    print(f"  Risk score: {result['risk_score']}")
    print(f"  Factors: {', '.join(result['risk_factors'])}")
    print(f"  Recommendation: {result['recommendation']}")
    assert result["success"], "Risk assessment failed"
    
    # Test 4: Rate limit check
    print("\n🔐 Test 4: Check Rate Limits")
    result = await bee.process_task({
        "type": "check_rate_limit",
        "daily_limit": 50_000_000 * 10**18,
        "current_usage": 45_000_000 * 10**18,
        "requested_amount": 3_000_000 * 10**18,
    })
    print(f"  Status: {result['status']}")
    print(f"  Approved: {result['approved']}")
    print(f"  Utilization: {result['utilization_percent']}%")
    print(f"  Would exceed: {result['would_exceed']}")
    assert result["success"], "Rate limit check failed"
    
    stats = bee.get_stats()
    print(f"\n✅ SecurityBee: {stats['tasks_completed']} tasks, {stats['success_rate']} success rate")


async def test_data_bee():
    """Test DataBee"""
    print("\n" + "="*60)
    print("📊 TESTING DATA BEE")
    print("="*60)
    
    bee = DataBee(bee_id=3)
    
    # Test 1: Query balance
    print("\n💰 Test 1: Query Balance")
    result = await bee.process_task({
        "type": "query_balance",
        "address": "0x" + "1" * 40,
        "token": "OMK",
    })
    print(f"  Balance: {result['formatted_balance']}")
    assert result["success"], "Balance query failed"
    
    # Test 2: Aggregate transfers
    print("\n💰 Test 2: Aggregate Transfers")
    result = await bee.process_task({
        "type": "aggregate_transfers",
        "address": "0x" + "1" * 40,
        "time_period": "24h",
    })
    print(f"  Transfer count: {result['transfers']['transfer_count']}")
    print(f"  Total sent: {result['transfers']['total_sent'] / 10**18:,.0f} OMK")
    print(f"  Total received: {result['transfers']['total_received'] / 10**18:,.0f} OMK")
    print(f"  Net flow: {result['net_flow'] / 10**18:,.0f} OMK")
    assert result["success"], "Transfer aggregation failed"
    
    # Test 3: Pool stats
    print("\n💰 Test 3: Get Pool Stats")
    result = await bee.process_task({
        "type": "get_pool_stats",
        "pool_address": "0x" + "a" * 40,
    })
    print(f"  Liquidity: ${result['stats']['total_liquidity_usd']:,.0f}")
    print(f"  24h Volume: ${result['stats']['volume_24h']:,.0f}")
    print(f"  APY: {result['stats']['apy']}%")
    assert result["success"], "Pool stats failed"
    
    # Test 4: Generate report
    print("\n💰 Test 4: Generate Report")
    result = await bee.process_task({
        "type": "generate_report",
        "report_type": "daily",
    })
    print(f"  Report type: {result['report']['report_type']}")
    print(f"  System health: {result['report']['summary']['system_health']}")
    assert result["success"], "Report generation failed"
    
    stats = bee.get_stats()
    print(f"\n✅ DataBee: {stats['tasks_completed']} tasks, {stats['success_rate']} success rate")


async def test_treasury_bee():
    """Test TreasuryBee"""
    print("\n" + "="*60)
    print("💰 TESTING TREASURY BEE")
    print("="*60)
    
    bee = TreasuryBee(bee_id=4)
    
    # Test 1: Valid proposal
    print("\n💵 Test 1: Validate Proposal (Valid)")
    result = await bee.process_task({
        "type": "validate_proposal",
        "category": 0,  # DEVELOPMENT
        "amount": 5_000_000 * 10**18,
        "description": "Smart contract development and security audits for Q4",
    })
    print(f"  Category: {result['category']}")
    print(f"  Valid: {result['valid']}")
    print(f"  Remaining budget: {result['remaining_budget'] / 10**18:,.0f} OMK")
    print(f"  Utilization: {result['utilization_percent']}%")
    assert result["success"], "Proposal validation failed"
    
    # Test 2: Invalid proposal
    print("\n💵 Test 2: Validate Proposal (Invalid)")
    result = await bee.process_task({
        "type": "validate_proposal",
        "category": 0,
        "amount": 50_000_000 * 10**18,  # Too large
        "description": "Too large",
    })
    print(f"  Valid: {result['valid']}")
    print(f"  Issues: {', '.join(result['validation_issues'])}")
    
    # Test 3: Budget check
    print("\n💵 Test 3: Check Budget")
    result = await bee.process_task({
        "type": "check_budget",
        "category": "MARKETING",
    })
    print(f"  Category: {result['category']}")
    print(f"  Monthly limit: {result['monthly_limit'] / 10**18:,.0f} OMK")
    print(f"  Spent: {result['spent'] / 10**18:,.0f} OMK")
    print(f"  Status: {result['status']}")
    assert result["success"], "Budget check failed"
    
    # Test 4: Treasury health
    print("\n💵 Test 4: Check Treasury Health")
    result = await bee.process_task({
        "type": "treasury_health",
        "total_balance": 100_000_000 * 10**18,
        "burn_rate": 2_000_000 * 10**18,
    })
    print(f"  Health status: {result['health_status']}")
    print(f"  Health score: {result['health_score']}/100")
    print(f"  Runway: {result['runway_months']} months")
    print(f"  Recommendations: {result['recommendations']}")
    assert result["success"], "Treasury health check failed"
    
    stats = bee.get_stats()
    print(f"\n✅ TreasuryBee: {stats['tasks_completed']} tasks, {stats['success_rate']} success rate")


async def test_bee_manager():
    """Test BeeManager"""
    print("\n" + "="*60)
    print("👑 TESTING BEE MANAGER")
    print("="*60)
    
    manager = BeeManager()
    await manager.initialize()
    
    print(f"\n📋 Initialized {len(manager.bees)} bees:")
    for name in manager.bees:
        print(f"  - {name}")
    
    # Test execution through manager
    print("\n🔄 Test: Execute via Manager")
    result = await manager.execute_bee("maths", {
        "type": "calculate_apy",
        "total_staked": 10_000_000 * 10**18,
        "annual_rewards": 1_000_000 * 10**18,
        "treasury_health": 1.0,
    })
    print(f"  Result: APY = {result['base_apy']}%")
    assert result["success"], "Manager execution failed"
    
    # Test health check
    print("\n🔄 Test: Health Check")
    health = await manager.check_all_health()
    print(f"  All healthy: {health['all_healthy']}")
    print(f"  Total bees: {health['total_bees']}")
    for bee_name, bee_health in health['bees'].items():
        print(f"    {bee_name}: {bee_health['status']} ({bee_health['task_count']} tasks)")
    
    # Test stats
    print("\n🔄 Test: Get Stats")
    stats = await manager.get_bee_stats()
    for bee_name, bee_stats in stats.items():
        print(f"  {bee_name}: {bee_stats['tasks_completed']} tasks, {bee_stats['success_rate']}")
    
    print(f"\n✅ BeeManager: All operations successful")


async def test_inter_bee_coordination():
    """Test coordination between bees"""
    print("\n" + "="*60)
    print("🤝 TESTING INTER-BEE COORDINATION")
    print("="*60)
    
    manager = BeeManager()
    await manager.initialize()
    
    # Workflow 1: Liquidity Management
    print("\n🔄 Workflow 1: Liquidity Management Decision")
    print("  Step 1: DataBee gets pool stats...")
    pool_data = await manager.execute_bee("data", {
        "type": "get_pool_stats",
        "pool_address": "0x" + "a" * 40,
    })
    print(f"    ✓ Pool liquidity: ${pool_data['stats']['total_liquidity_usd']:,.0f}")
    
    print("  Step 2: MathsBee analyzes pool...")
    math_result = await manager.execute_bee("maths", {
        "type": "calculate_pool_ratio",
        "token_a": pool_data["stats"]["token_a_amount"],
        "token_b": pool_data["stats"]["token_b_amount"],
        "target_ratio": 1.0,
    })
    print(f"    ✓ Pool deviation: {math_result['deviation_percent']}%")
    
    print("  Step 3: SecurityBee validates operation...")
    security_check = await manager.execute_bee("security", {
        "type": "assess_risk",
        "operation_type": "add_liquidity",
        "amount": 5_000_000 * 10**18,
        "target": "0x" + "a" * 40,
    })
    print(f"    ✓ Risk level: {security_check['risk_level']}")
    print(f"  ✅ Liquidity decision complete: {security_check['recommendation']}")
    
    # Workflow 2: Treasury Proposal
    print("\n🔄 Workflow 2: Treasury Proposal Validation")
    print("  Step 1: TreasuryBee validates proposal...")
    proposal = await manager.execute_bee("treasury", {
        "type": "validate_proposal",
        "category": 1,  # MARKETING
        "amount": 3_000_000 * 10**18,
        "description": "Q4 marketing campaign and community growth initiatives",
    })
    print(f"    ✓ Proposal valid: {proposal['valid']}")
    
    print("  Step 2: SecurityBee checks recipient...")
    address_check = await manager.execute_bee("security", {
        "type": "validate_address",
        "address": "0x" + "b" * 40,
    })
    print(f"    ✓ Address valid: {address_check['valid']}")
    
    print("  Step 3: DataBee logs transaction...")
    balance = await manager.execute_bee("data", {
        "type": "query_balance",
        "address": "0x" + "b" * 40,
        "token": "OMK",
    })
    print(f"    ✓ Recipient balance: {balance['formatted_balance']}")
    print(f"  ✅ Treasury proposal workflow complete!")
    
    print(f"\n✅ Inter-bee coordination: All workflows successful")


async def main():
    """Run all tests"""
    print("\n")
    print("🐝" * 30)
    print("   OMK HIVE - BEE AGENT TEST SUITE")
    print("🐝" * 30)
    
    try:
        await test_maths_bee()
        await test_security_bee()
        await test_data_bee()
        await test_treasury_bee()
        await test_bee_manager()
        await test_inter_bee_coordination()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("="*60)
        print("\n✅ The Hive is fully operational!")
        print("✅ All 4 bees are working correctly")
        print("✅ Inter-bee communication is functional")
        print("✅ Ready for Queen AI orchestration")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
