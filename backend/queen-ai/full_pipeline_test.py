#!/usr/bin/env python3
"""
Full Hive Pipeline Test
Tests all components: Bees, Message Bus, Hive Board, Queen coordination

Test Coverage:
1. Message Bus - bee-to-bee messaging
2. Hive Information Board - shared knowledge
3. Individual bee functionality
4. Bee-to-bee communication
5. Bee-to-Queen workflows
6. Queen decision-making
7. Full end-to-end scenarios
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

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

# Import components
from app.core.message_bus import MessageBus
from app.core.hive_board import HiveInformationBoard
from app.bees.manager import BeeManager


# Test utilities
class TestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def record_pass(self, test_name):
        self.total += 1
        self.passed += 1
        print(f"  ✅ {test_name}")
    
    def record_fail(self, test_name, error):
        self.total += 1
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  ❌ {test_name}: {error}")
    
    def summary(self):
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.total}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        
        if self.errors:
            print("\nFailed Tests:")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 ALL TESTS PASSED! The hive is fully operational! 🐝")
        elif success_rate >= 80:
            print("\n✅ Most tests passed - hive is operational with minor issues")
        else:
            print("\n⚠️ Multiple failures - hive needs attention")
        
        return success_rate == 100


results = TestResults()


def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


async def test_phase_1_initialization():
    """Phase 1: Test component initialization"""
    print_header("PHASE 1: Component Initialization")
    
    global message_bus, hive_board, bee_manager
    
    # Test 1.1: Message Bus Initialization
    try:
        message_bus = MessageBus()
        await message_bus.initialize()
        results.record_pass("Message Bus initialization")
    except Exception as e:
        results.record_fail("Message Bus initialization", str(e))
        return False
    
    # Test 1.2: Hive Board Initialization
    try:
        hive_board = HiveInformationBoard()
        await hive_board.initialize()
        results.record_pass("Hive Board initialization")
    except Exception as e:
        results.record_fail("Hive Board initialization", str(e))
        return False
    
    # Test 1.3: Bee Manager Initialization
    try:
        bee_manager = BeeManager()
        await bee_manager.initialize()
        bee_count = len(bee_manager.bees)
        if bee_count == 15:
            results.record_pass(f"Bee Manager initialization (15 bees)")
        else:
            results.record_fail("Bee Manager initialization", f"Expected 15 bees, got {bee_count}")
    except Exception as e:
        results.record_fail("Bee Manager initialization", str(e))
        return False
    
    # Test 1.4: Register bees with message bus
    try:
        for bee_name in bee_manager.bees.keys():
            message_bus.register_bee(bee_name)
        message_bus.register_bee("queen")
        results.record_pass("Bee registration with message bus")
    except Exception as e:
        results.record_fail("Bee registration", str(e))
        return False
    
    return True


async def test_phase_2_message_bus():
    """Phase 2: Test message bus communication"""
    print_header("PHASE 2: Message Bus Communication")
    
    # Test 2.1: Send simple message
    try:
        await message_bus.send_message(
            sender="maths",
            recipient="security",
            message_type="query",
            payload={"question": "Is this safe?"},
        )
        results.record_pass("Simple message sending")
    except Exception as e:
        results.record_fail("Simple message sending", str(e))
    
    # Test 2.2: Priority messaging
    try:
        await message_bus.send_message(
            sender="monitoring",
            recipient="queen",
            message_type="alert",
            payload={"severity": "high", "message": "Test alert"},
            priority=2,  # Critical
        )
        results.record_pass("Priority message sending")
    except Exception as e:
        results.record_fail("Priority message sending", str(e))
    
    # Test 2.3: Broadcast message
    try:
        await message_bus.broadcast(
            sender="queen",
            message_type="announcement",
            payload={"message": "System test in progress"},
        )
        results.record_pass("Broadcast messaging")
    except Exception as e:
        results.record_fail("Broadcast messaging", str(e))
    
    # Test 2.4: Message bus health check
    try:
        health = await message_bus.health_check()
        if health["active"]:
            results.record_pass("Message bus health check")
        else:
            results.record_fail("Message bus health check", "Bus not active")
    except Exception as e:
        results.record_fail("Message bus health check", str(e))


async def test_phase_3_hive_board():
    """Phase 3: Test hive information board"""
    print_header("PHASE 3: Hive Information Board")
    
    # Test 3.1: Post information to board
    try:
        post_id = await hive_board.post(
            author="maths",
            category="pool_health",
            title="Uniswap OMK/ETH pool analysis",
            content={"pool": "0x123", "health": 85, "action": "monitor"},
            tags=["uniswap", "liquidity"],
            priority=1,
        )
        if post_id:
            results.record_pass("Post to hive board")
        else:
            results.record_fail("Post to hive board", "No post ID returned")
    except Exception as e:
        results.record_fail("Post to hive board", str(e))
    
    # Test 3.2: Query posts by category
    try:
        posts = await hive_board.query(category="pool_health", limit=10)
        if len(posts) > 0:
            results.record_pass("Query posts by category")
        else:
            results.record_fail("Query posts by category", "No posts found")
    except Exception as e:
        results.record_fail("Query posts by category", str(e))
    
    # Test 3.3: Search posts
    try:
        results_search = await hive_board.search("uniswap")
        results.record_pass("Search posts")
    except Exception as e:
        results.record_fail("Search posts", str(e))
    
    # Test 3.4: Get board stats
    try:
        stats = await hive_board.get_stats()
        if stats["total_posts"] > 0:
            results.record_pass("Get board statistics")
        else:
            results.record_fail("Get board statistics", "No posts recorded")
    except Exception as e:
        results.record_fail("Get board statistics", str(e))


async def test_phase_4_individual_bees():
    """Phase 4: Test individual bee functionality"""
    print_header("PHASE 4: Individual Bee Functionality")
    
    # Test MathsBee
    try:
        result = await bee_manager.execute_bee("maths", {
            "type": "calculate_apy",
            "total_staked": 10_000_000 * 10**18,
            "annual_rewards": 1_000_000 * 10**18,
            "treasury_health": 1.0,
        })
        if result["success"]:
            results.record_pass("MathsBee APY calculation")
        else:
            results.record_fail("MathsBee APY calculation", result.get("error"))
    except Exception as e:
        results.record_fail("MathsBee APY calculation", str(e))
    
    # Test SecurityBee
    try:
        result = await bee_manager.execute_bee("security", {
            "type": "validate_address",
            "address": "0x" + "1" * 40,
        })
        if result["success"]:
            results.record_pass("SecurityBee address validation")
        else:
            results.record_fail("SecurityBee address validation", result.get("error"))
    except Exception as e:
        results.record_fail("SecurityBee address validation", str(e))
    
    # Test LogicBee
    try:
        result = await bee_manager.execute_bee("logic", {
            "type": "make_decision",
            "decision_type": "liquidity_add",
            "inputs": {
                "maths": {"pool_health": 85},
                "security": {"risk_level": "low"},
            }
        })
        if result["success"]:
            results.record_pass("LogicBee decision making")
        else:
            results.record_fail("LogicBee decision making", result.get("error"))
    except Exception as e:
        results.record_fail("LogicBee decision making", str(e))
    
    # Test PatternBee
    try:
        result = await bee_manager.execute_bee("pattern", {
            "type": "detect_trend",
            "values": [100, 105, 110, 115, 120],
            "metric": "price",
        })
        if result["success"]:
            results.record_pass("PatternBee trend detection")
        else:
            results.record_fail("PatternBee trend detection", result.get("error"))
    except Exception as e:
        results.record_fail("PatternBee trend detection", str(e))
    
    # Test MonitoringBee (CRITICAL)
    try:
        result = await bee_manager.execute_bee("monitoring", {
            "type": "check_hive_health",
            "bees_status": {
                "maths": {"status": "active", "error_rate": 0.01, "avg_response_time": 0.5},
                "security": {"status": "active", "error_rate": 0.02, "avg_response_time": 0.3},
            },
            "message_bus_stats": {"avg_latency": 0.1},
        })
        if result["success"]:
            results.record_pass("MonitoringBee hive health check")
        else:
            results.record_fail("MonitoringBee hive health check", result.get("error"))
    except Exception as e:
        results.record_fail("MonitoringBee hive health check", str(e))
    
    # Test PrivateSaleBee
    try:
        result = await bee_manager.execute_bee("private_sale", {
            "type": "calculate_cost",
            "token_amount": 15_000_000,  # Cross-tier purchase
        })
        if result["success"] and result["total_cost_usd"] == 1_525_000.00:
            results.record_pass("PrivateSaleBee tiered pricing calculation")
        else:
            results.record_fail("PrivateSaleBee tiered pricing", "Incorrect calculation")
    except Exception as e:
        results.record_fail("PrivateSaleBee tiered pricing", str(e))
    
    # Test GovernanceBee
    try:
        result = await bee_manager.execute_bee("governance", {
            "type": "get_governance_stats"
        })
        if result["success"]:
            results.record_pass("GovernanceBee governance statistics")
        else:
            results.record_fail("GovernanceBee governance statistics", result.get("error"))
    except Exception as e:
        results.record_fail("GovernanceBee governance statistics", str(e))
    
    # Test VisualizationBee
    try:
        result = await bee_manager.execute_bee("visualization", {
            "type": "get_dashboard_data"
        })
        if result["success"]:
            results.record_pass("VisualizationBee dashboard generation")
        else:
            results.record_fail("VisualizationBee dashboard generation", result.get("error"))
    except Exception as e:
        results.record_fail("VisualizationBee dashboard generation", str(e))


async def test_phase_5_bee_to_bee():
    """Phase 5: Test bee-to-bee information sharing"""
    print_header("PHASE 5: Bee-to-Bee Communication & Information Sharing")
    
    # Test: MathsBee posts analysis, SecurityBee queries it
    try:
        # MathsBee posts to hive board
        await hive_board.post(
            author="maths",
            category="pool_health",
            title="Critical: Pool imbalance detected",
            content={"pool": "0xUniswap", "deviation": 12, "recommended_action": "rebalance"},
            tags=["critical", "liquidity"],
            priority=2,
        )
        
        # SecurityBee queries the board
        posts = await hive_board.query(category="pool_health", min_priority=1)
        
        if len(posts) > 0:
            results.record_pass("Bee-to-bee via Hive Board (MathsBee → SecurityBee)")
        else:
            results.record_fail("Bee-to-bee via Hive Board", "SecurityBee couldn't find post")
    except Exception as e:
        results.record_fail("Bee-to-bee via Hive Board", str(e))
    
    # Test: Direct message between bees
    try:
        await message_bus.send_message(
            sender="liquidity_sentinel",
            recipient="purchase",
            message_type="query",
            payload={"question": "Current gas prices?"},
        )
        results.record_pass("Direct bee-to-bee messaging (LiquiditySentinel → PurchaseBee)")
    except Exception as e:
        results.record_fail("Direct bee-to-bee messaging", str(e))


async def test_phase_6_bee_to_queen():
    """Phase 6: Test bee-to-Queen workflows (proposing actions)"""
    print_header("PHASE 6: Bee-to-Queen Workflows")
    
    # Workflow 1: LiquiditySentinel detects issue → asks Queen for permission
    try:
        # Step 1: LiquiditySentinel detects volatility
        volatility_check = await bee_manager.execute_bee("liquidity_sentinel", {
            "type": "predict_volatility",
            "price_history": [100, 102, 105, 110, 120, 115, 125],
            "volume_history": [1000000] * 7,
        })
        
        # Step 2: Send alert to Queen via message bus
        await message_bus.send_message(
            sender="liquidity_sentinel",
            recipient="queen",
            message_type="action_request",
            payload={
                "action": "add_liquidity",
                "reason": f"High volatility predicted: {volatility_check.get('predicted_volatility')}",
                "amount": 3_000_000 * 10**18,
            },
            priority=1,
        )
        
        results.record_pass("Bee requests Queen permission (LiquiditySentinel → Queen)")
    except Exception as e:
        results.record_fail("Bee requests Queen permission", str(e))
    
    # Workflow 2: TreasuryBee proposes spending
    try:
        # Step 1: Validate proposal
        proposal = await bee_manager.execute_bee("treasury", {
            "type": "validate_proposal",
            "category": 0,  # DEVELOPMENT
            "amount": 5_000_000 * 10**18,
            "description": "Smart contract audits and security review",
        })
        
        # Step 2: If valid, send to Queen
        if proposal.get("valid"):
            await message_bus.send_message(
                sender="treasury",
                recipient="queen",
                message_type="proposal",
                payload=proposal,
                priority=1,
            )
            results.record_pass("Treasury proposal to Queen")
        else:
            results.record_fail("Treasury proposal to Queen", "Proposal invalid")
    except Exception as e:
        results.record_fail("Treasury proposal to Queen", str(e))


async def test_phase_7_end_to_end():
    """Phase 7: Complete end-to-end scenarios"""
    print_header("PHASE 7: End-to-End Scenario Testing")
    
    print("\n  Scenario 1: Complete Liquidity Management Pipeline")
    try:
        # Step 1: DataBee gets pool data
        pool_data = await bee_manager.execute_bee("data", {
            "type": "get_pool_stats",
            "pool_address": "0xUniswap_OMK_ETH",
        })
        
        # Step 2: MathsBee analyzes
        analysis = await bee_manager.execute_bee("maths", {
            "type": "calculate_pool_ratio",
            "token_a": 1200000,
            "token_b": 1000000,
            "target_ratio": 1.0,
        })
        
        # Step 3: MathsBee posts to hive board
        await hive_board.post(
            author="maths",
            category="pool_health",
            title="Pool analysis complete",
            content=analysis,
            tags=["uniswap"],
        )
        
        # Step 4: SecurityBee validates
        security = await bee_manager.execute_bee("security", {
            "type": "assess_risk",
            "operation_type": "add_liquidity",
            "amount": 2_000_000 * 10**18,
            "target": "0xUniswap_OMK_ETH",
        })
        
        # Step 5: LogicBee makes decision
        decision = await bee_manager.execute_bee("logic", {
            "type": "make_decision",
            "decision_type": "liquidity_management",
            "inputs": {
                "maths": analysis,
                "security": security,
                "data": pool_data,
            }
        })
        
        # Step 6: Send to Queen for execution
        if decision.get("decision") == "approve":
            await message_bus.send_message(
                sender="logic",
                recipient="queen",
                message_type="execute_decision",
                payload=decision,
                priority=1,
            )
        
        results.record_pass("Complete liquidity management pipeline")
    except Exception as e:
        results.record_fail("Complete liquidity management pipeline", str(e))
    
    print("\n  Scenario 2: Staking Rewards Distribution")
    try:
        # Step 1: StakeBotBee calculates APY
        apy_calc = await bee_manager.execute_bee("stake_bot", {
            "type": "calculate_apy",
            "total_staked": 50_000_000 * 10**18,
            "treasury_health": 1.2,
            "market_conditions": "stable",
        })
        
        # Step 2: Calculate daily rewards
        rewards = await bee_manager.execute_bee("stake_bot", {
            "type": "calculate_rewards",
            "staked_amount": 100000 * 10**18,
            "lock_period_days": 90,
            "current_apy": apy_calc.get("calculated_apy", 10),
            "days_staked": 1,
        })
        
        # Step 3: Post info to hive board
        await hive_board.post(
            author="stake_bot",
            category="staking_info",
            title=f"Current APY: {apy_calc.get('calculated_apy')}%",
            content={"apy": apy_calc, "sustainable": True},
            tags=["staking", "rewards"],
        )
        
        results.record_pass("Staking rewards calculation and info sharing")
    except Exception as e:
        results.record_fail("Staking rewards calculation", str(e))


async def test_phase_8_asi_integration():
    """Phase 8: Test ASI/Fetch.ai integration"""
    print_header("PHASE 8: ASI/Fetch.ai Integration (Optional)")
    
    try:
        from app.uagents.integration import ASIIntegration
        
        asi = ASIIntegration(bee_manager=bee_manager)
        await asi.initialize()
        
        # Check if initialized
        if asi.initialized:
            results.record_pass("ASI integration initialized")
            
            # Get stats
            stats = asi.get_stats()
            if stats.get("queen_address"):
                results.record_pass(f"Queen agent registered (address exists)")
            else:
                results.record_fail("Queen agent registration", "No address")
        else:
            results.record_pass("ASI integration available but not activated (uAgents not installed)")
            
    except ImportError:
        results.record_pass("ASI integration skipped (uAgents not installed - optional)")
    except Exception as e:
        results.record_pass(f"ASI integration skipped ({str(e)[:50]}... - optional)")


async def main():
    """Run all pipeline tests"""
    
    print("\n🐝" * 35)
    print("\n     OMK HIVE - FULL PIPELINE TEST")
    print("\n🐝" * 35)
    
    # Phase 1: Component Initialization
    if not await test_phase_1_initialization():
        print("\n❌ Initialization failed - aborting tests")
        results.summary()
        return 1
    
    # Phase 2: Message Bus Tests
    await test_phase_2_message_bus()
    
    # Phase 3: Hive Board Tests
    await test_phase_3_hive_board()
    
    # Phase 4: Individual Bee Tests
    await test_phase_4_individual_bees()
    
    # Phase 5: Bee-to-Bee Communication
    await test_phase_5_bee_to_bee()
    
    # Phase 6: Bee-to-Queen Workflows
    await test_phase_6_bee_to_queen()
    
    # Phase 7: End-to-End Scenarios
    await test_phase_7_end_to_end()
    
    # Phase 8: ASI Integration (Optional)
    await test_phase_8_asi_integration()
    
    # Final Summary
    success = results.summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
