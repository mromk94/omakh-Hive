"""
Test Suite for Bee Agents
Tests individual bee functionality and inter-bee communication
"""
import pytest
import asyncio
from app.bees.maths_bee import MathsBee
from app.bees.security_bee import SecurityBee
from app.bees.data_bee import DataBee
from app.bees.treasury_bee import TreasuryBee
from app.bees.manager import BeeManager


class TestMathsBee:
    """Test MathsBee calculations"""
    
    @pytest.mark.asyncio
    async def test_calculate_slippage(self):
        """Test slippage calculation"""
        bee = MathsBee(bee_id=1)
        
        result = await bee.process_task({
            "type": "calculate_slippage",
            "reserve_in": 1000000,
            "reserve_out": 1000000,
            "amount_in": 10000,
        })
        
        assert result["success"] is True
        assert "slippage_percent" in result
        assert result["slippage_percent"] > 0  # Should have some slippage
        print(f"✅ Slippage calculation: {result['slippage_percent']}%")
    
    @pytest.mark.asyncio
    async def test_calculate_pool_ratio(self):
        """Test pool ratio calculation"""
        bee = MathsBee(bee_id=1)
        
        result = await bee.process_task({
            "type": "calculate_pool_ratio",
            "token_a": 1000000,
            "token_b": 1000000,
            "target_ratio": 1.0,
        })
        
        assert result["success"] is True
        assert result["current_ratio"] == 1.0
        assert result["needs_rebalance"] is False
        print(f"✅ Pool ratio: {result['current_ratio']}, Deviation: {result['deviation_percent']}%")
    
    @pytest.mark.asyncio
    async def test_calculate_apy(self):
        """Test APY calculation"""
        bee = MathsBee(bee_id=1)
        
        result = await bee.process_task({
            "type": "calculate_apy",
            "total_staked": 10_000_000 * 10**18,
            "annual_rewards": 1_000_000 * 10**18,
            "treasury_health": 1.2,
        })
        
        assert result["success"] is True
        assert "base_apy" in result
        assert "adjusted_apy" in result
        print(f"✅ APY calculation: Base={result['base_apy']}%, Adjusted={result['adjusted_apy']}%")


class TestSecurityBee:
    """Test SecurityBee validation"""
    
    @pytest.mark.asyncio
    async def test_validate_address(self):
        """Test address validation"""
        bee = SecurityBee(bee_id=2)
        
        # Valid address
        result = await bee.process_task({
            "type": "validate_address",
            "address": "0x" + "1" * 40,
        })
        
        assert result["success"] is True
        assert result["valid"] is True
        print(f"✅ Valid address: {result['address']}")
        
        # Invalid address
        result = await bee.process_task({
            "type": "validate_address",
            "address": "0x123",  # Too short
        })
        
        assert result["success"] is False
        assert result["valid"] is False
        print(f"✅ Invalid address rejected: {result['reason']}")
    
    @pytest.mark.asyncio
    async def test_risk_assessment(self):
        """Test risk assessment"""
        bee = SecurityBee(bee_id=2)
        
        # Low risk operation
        result = await bee.process_task({
            "type": "assess_risk",
            "operation_type": "staking",
            "amount": 1_000_000 * 10**18,
            "target": "0x" + "1" * 40,
        })
        
        assert result["success"] is True
        assert result["risk_level"] == "low"
        print(f"✅ Risk assessment: {result['risk_level']} (score: {result['risk_score']})")
        
        # High risk operation
        result = await bee.process_task({
            "type": "assess_risk",
            "operation_type": "bridge_transfer",
            "amount": 15_000_000 * 10**18,  # Large amount
            "target": "0x" + "2" * 40,
        })
        
        assert result["success"] is True
        assert result["risk_level"] in ["medium", "high"]
        print(f"✅ High-risk operation detected: {result['risk_level']}, Factors: {result['risk_factors']}")
    
    @pytest.mark.asyncio
    async def test_rate_limit_check(self):
        """Test rate limit validation"""
        bee = SecurityBee(bee_id=2)
        
        result = await bee.process_task({
            "type": "check_rate_limit",
            "daily_limit": 50_000_000 * 10**18,
            "current_usage": 40_000_000 * 10**18,
            "requested_amount": 5_000_000 * 10**18,
        })
        
        assert result["success"] is True
        assert result["approved"] is True
        assert result["status"] == "warning"  # 90% utilization
        print(f"✅ Rate limit check: {result['status']}, Utilization: {result['utilization_percent']}%")


class TestDataBee:
    """Test DataBee queries"""
    
    @pytest.mark.asyncio
    async def test_query_balance(self):
        """Test balance query"""
        bee = DataBee(bee_id=3)
        
        result = await bee.process_task({
            "type": "query_balance",
            "address": "0x" + "1" * 40,
            "token": "OMK",
        })
        
        assert result["success"] is True
        assert "balance" in result
        assert "formatted_balance" in result
        print(f"✅ Balance query: {result['formatted_balance']}")
    
    @pytest.mark.asyncio
    async def test_aggregate_transfers(self):
        """Test transfer aggregation"""
        bee = DataBee(bee_id=3)
        
        result = await bee.process_task({
            "type": "aggregate_transfers",
            "address": "0x" + "1" * 40,
            "time_period": "24h",
        })
        
        assert result["success"] is True
        assert "transfers" in result
        assert result["transfers"]["transfer_count"] > 0
        print(f"✅ Transfers: {result['transfers']['transfer_count']} in 24h")
    
    @pytest.mark.asyncio
    async def test_generate_report(self):
        """Test report generation"""
        bee = DataBee(bee_id=3)
        
        result = await bee.process_task({
            "type": "generate_report",
            "report_type": "daily",
        })
        
        assert result["success"] is True
        assert "report" in result
        assert "summary" in result["report"]
        print(f"✅ Report generated: {result['report']['summary']}")


class TestTreasuryBee:
    """Test TreasuryBee operations"""
    
    @pytest.mark.asyncio
    async def test_validate_proposal(self):
        """Test proposal validation"""
        bee = TreasuryBee(bee_id=4)
        
        # Valid proposal
        result = await bee.process_task({
            "type": "validate_proposal",
            "category": 0,  # DEVELOPMENT
            "amount": 5_000_000 * 10**18,
            "description": "Funding for smart contract development and audits",
        })
        
        assert result["success"] is True
        assert result["valid"] is True
        print(f"✅ Proposal validated: {result['category']}, Remaining: {result['remaining_budget'] / 10**18:.0f} OMK")
        
        # Invalid proposal (too large)
        result = await bee.process_task({
            "type": "validate_proposal",
            "category": 0,
            "amount": 50_000_000 * 10**18,  # Exceeds limit
            "description": "Large development request",
        })
        
        assert result["success"] is True
        assert result["valid"] is False
        assert len(result["validation_issues"]) > 0
        print(f"✅ Invalid proposal rejected: {result['validation_issues']}")
    
    @pytest.mark.asyncio
    async def test_treasury_health(self):
        """Test treasury health check"""
        bee = TreasuryBee(bee_id=4)
        
        result = await bee.process_task({
            "type": "treasury_health",
            "total_balance": 100_000_000 * 10**18,
            "burn_rate": 2_000_000 * 10**18,
        })
        
        assert result["success"] is True
        assert "health_score" in result
        assert "runway_months" in result
        print(f"✅ Treasury health: {result['health_status']}, Runway: {result['runway_months']} months")
    
    @pytest.mark.asyncio
    async def test_budget_check(self):
        """Test budget checking"""
        bee = TreasuryBee(bee_id=4)
        
        result = await bee.process_task({
            "type": "check_budget",
            "category": "MARKETING",
        })
        
        assert result["success"] is True
        assert result["status"] == "healthy"
        print(f"✅ Budget check: {result['category']}, Utilization: {result['utilization_percent']}%")


class TestBeeManager:
    """Test BeeManager coordination"""
    
    @pytest.mark.asyncio
    async def test_manager_initialization(self):
        """Test manager initializes all bees"""
        manager = BeeManager()
        await manager.initialize()
        
        assert manager.initialized is True
        assert len(manager.bees) == 4  # 4 bees
        assert "maths" in manager.bees
        assert "security" in manager.bees
        assert "data" in manager.bees
        assert "treasury" in manager.bees
        print(f"✅ Manager initialized with {len(manager.bees)} bees")
    
    @pytest.mark.asyncio
    async def test_execute_bee(self):
        """Test executing specific bee"""
        manager = BeeManager()
        await manager.initialize()
        
        result = await manager.execute_bee("maths", {
            "type": "calculate_apy",
            "total_staked": 10_000_000 * 10**18,
            "annual_rewards": 1_000_000 * 10**18,
            "treasury_health": 1.0,
        })
        
        assert result["success"] is True
        assert "base_apy" in result
        print(f"✅ Executed MathsBee via manager: APY={result['base_apy']}%")
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check for all bees"""
        manager = BeeManager()
        await manager.initialize()
        
        # Execute some tasks first
        await manager.execute_bee("maths", {
            "type": "calculate_apy",
            "total_staked": 10_000_000 * 10**18,
            "annual_rewards": 1_000_000 * 10**18,
            "treasury_health": 1.0,
        })
        
        health = await manager.check_all_health()
        
        assert health["all_healthy"] is True
        assert health["total_bees"] == 4
        print(f"✅ Health check: All bees healthy ({health['total_bees']} bees)")


class TestInterBeeCoordination:
    """Test coordination between multiple bees"""
    
    @pytest.mark.asyncio
    async def test_liquidity_decision_workflow(self):
        """Test complete liquidity management workflow using multiple bees"""
        manager = BeeManager()
        await manager.initialize()
        
        print("\n🔄 Testing Liquidity Management Workflow:")
        
        # Step 1: DataBee gets pool stats
        pool_data = await manager.execute_bee("data", {
            "type": "get_pool_stats",
            "pool_address": "0x" + "a" * 40,
        })
        assert pool_data["success"] is True
        print(f"  1️⃣ DataBee: Pool stats retrieved - Liquidity: ${pool_data['stats']['total_liquidity_usd']:,.0f}")
        
        # Step 2: MathsBee analyzes if rebalance needed
        math_result = await manager.execute_bee("maths", {
            "type": "calculate_pool_ratio",
            "token_a": pool_data["stats"]["token_a_amount"],
            "token_b": pool_data["stats"]["token_b_amount"],
            "target_ratio": 1.0,
        })
        assert math_result["success"] is True
        print(f"  2️⃣ MathsBee: Pool ratio analyzed - Deviation: {math_result['deviation_percent']}%")
        
        # Step 3: SecurityBee validates the operation
        security_check = await manager.execute_bee("security", {
            "type": "assess_risk",
            "operation_type": "add_liquidity",
            "amount": 5_000_000 * 10**18,
            "target": "0x" + "a" * 40,
        })
        assert security_check["success"] is True
        print(f"  3️⃣ SecurityBee: Risk assessed - Level: {security_check['risk_level']}, Recommendation: {security_check['recommendation']}")
        
        print(f"✅ Workflow complete: All bees coordinated successfully!")
    
    @pytest.mark.asyncio
    async def test_treasury_proposal_workflow(self):
        """Test complete treasury proposal workflow"""
        manager = BeeManager()
        await manager.initialize()
        
        print("\n🔄 Testing Treasury Proposal Workflow:")
        
        # Step 1: TreasuryBee validates proposal
        proposal_check = await manager.execute_bee("treasury", {
            "type": "validate_proposal",
            "category": 0,  # DEVELOPMENT
            "amount": 5_000_000 * 10**18,
            "description": "Smart contract audit and development",
        })
        assert proposal_check["success"] is True
        print(f"  1️⃣ TreasuryBee: Proposal validated - {proposal_check['category']}, Valid: {proposal_check['valid']}")
        
        # Step 2: SecurityBee checks address
        address_check = await manager.execute_bee("security", {
            "type": "validate_address",
            "address": "0x" + "b" * 40,
        })
        assert address_check["success"] is True
        print(f"  2️⃣ SecurityBee: Recipient validated - Valid: {address_check['valid']}")
        
        # Step 3: DataBee logs the proposal
        data_log = await manager.execute_bee("data", {
            "type": "query_balance",
            "address": "0x" + "b" * 40,
            "token": "OMK",
        })
        assert data_log["success"] is True
        print(f"  3️⃣ DataBee: Recipient balance checked - {data_log['formatted_balance']}")
        
        print(f"✅ Treasury workflow complete: Proposal ready for execution!")
    
    @pytest.mark.asyncio
    async def test_multi_bee_execution(self):
        """Test executing multiple bees simultaneously"""
        manager = BeeManager()
        await manager.initialize()
        
        print("\n🔄 Testing Multi-Bee Parallel Execution:")
        
        # Execute multiple bees in parallel
        results = await manager.execute_multi(
            ["maths", "security", "data"],
            {
                "type": "calculate_apy",  # This will work for maths, fail for others
                "total_staked": 10_000_000 * 10**18,
                "annual_rewards": 1_000_000 * 10**18,
                "treasury_health": 1.0,
            }
        )
        
        assert len(results) == 3
        assert results[0]["success"] is True  # MathsBee should succeed
        print(f"  ✅ MathsBee: Succeeded")
        print(f"  ⚠️  SecurityBee: {results[1].get('error', 'Unknown task type')}")
        print(f"  ⚠️  DataBee: {results[2].get('error', 'Unknown task type')}")
        
        print(f"✅ Multi-bee execution complete!")


# Run tests if executed directly
if __name__ == "__main__":
    import sys
    
    print("🐝 OMK HIVE - BEE AGENT TEST SUITE 🐝\n")
    print("=" * 60)
    
    # Run all tests
    pytest.main([__file__, "-v", "-s"])
