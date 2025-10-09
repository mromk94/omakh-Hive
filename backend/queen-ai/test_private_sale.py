#!/usr/bin/env python3
"""
Test Private Sale Bee - Comprehensive testing of tiered token sale logic
"""
import asyncio
import sys
from pathlib import Path

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

from app.bees.private_sale_bee import PrivateSaleBee


class PrivateSaleTests:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.bee = None
    
    def print_header(self, title):
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def assert_equal(self, actual, expected, test_name):
        if actual == expected:
            self.passed += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            self.failed += 1
            print(f"  ❌ {test_name}")
            print(f"     Expected: {expected}")
            print(f"     Got: {actual}")
            return False
    
    def assert_true(self, condition, test_name):
        if condition:
            self.passed += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            self.failed += 1
            print(f"  ❌ {test_name}")
            return False
    
    async def test_tier_pricing_structure(self):
        """Test 1: Verify tier pricing structure"""
        self.print_header("TEST 1: Tier Pricing Structure")
        
        # Verify all 10 tiers are configured correctly
        self.assert_equal(len(self.bee.TIER_PRICES), 10, "10 tiers configured")
        
        # Verify tier 1 pricing
        tier1 = self.bee.TIER_PRICES[0]
        self.assert_equal(tier1["price"], 0.100, "Tier 1 price = $0.100")
        self.assert_equal(tier1["start"], 0, "Tier 1 starts at 0")
        self.assert_equal(tier1["end"], 10_000_000, "Tier 1 ends at 10M")
        
        # Verify tier 10 pricing
        tier10 = self.bee.TIER_PRICES[9]
        self.assert_equal(tier10["price"], 0.145, "Tier 10 price = $0.145")
        self.assert_equal(tier10["start"], 90_000_000, "Tier 10 starts at 90M")
        self.assert_equal(tier10["end"], 100_000_000, "Tier 10 ends at 100M")
        
        # Verify total allocation
        self.assert_equal(self.bee.TOTAL_ALLOCATION, 100_000_000, "Total allocation = 100M")
    
    async def test_single_tier_purchase(self):
        """Test 2: Calculate cost for single-tier purchase"""
        self.print_header("TEST 2: Single-Tier Purchase")
        
        # Purchase 5M tokens from tier 1
        result = await self.bee.execute({
            "type": "calculate_cost",
            "token_amount": 5_000_000
        })
        
        self.assert_true(result["success"], "Calculation succeeded")
        self.assert_equal(result["token_amount"], 5_000_000, "Token amount correct")
        self.assert_equal(result["total_cost_usd"], 500_000.00, "Cost = $500,000 (5M × $0.10)")
        self.assert_equal(result["average_price_per_token"], 0.100, "Avg price = $0.10")
        self.assert_equal(len(result["tier_breakdown"]), 1, "Single tier used")
    
    async def test_cross_tier_purchase(self):
        """Test 3: Calculate cost spanning multiple tiers"""
        self.print_header("TEST 3: Cross-Tier Purchase")
        
        # Purchase 15M tokens (spans tier 1 and 2)
        result = await self.bee.execute({
            "type": "calculate_cost",
            "token_amount": 15_000_000
        })
        
        self.assert_true(result["success"], "Calculation succeeded")
        self.assert_equal(result["token_amount"], 15_000_000, "Token amount correct")
        
        # Tier 1: 10M × $0.100 = $1,000,000
        # Tier 2:  5M × $0.105 = $525,000
        # Total: $1,525,000
        self.assert_equal(result["total_cost_usd"], 1_525_000.00, "Cost = $1,525,000")
        
        expected_avg = 1_525_000 / 15_000_000
        self.assert_equal(result["average_price_per_token"], round(expected_avg, 6), 
                         f"Avg price = ${expected_avg:.6f}")
        
        self.assert_equal(len(result["tier_breakdown"]), 2, "Two tiers used")
        
        # Verify tier breakdown
        tier1_breakdown = result["tier_breakdown"][0]
        self.assert_equal(tier1_breakdown["tokens"], 10_000_000, "10M from tier 1")
        self.assert_equal(tier1_breakdown["subtotal"], 1_000_000.00, "Tier 1 cost = $1M")
        
        tier2_breakdown = result["tier_breakdown"][1]
        self.assert_equal(tier2_breakdown["tokens"], 5_000_000, "5M from tier 2")
        self.assert_equal(tier2_breakdown["subtotal"], 525_000.00, "Tier 2 cost = $525K")
    
    async def test_full_100m_purchase(self):
        """Test 4: Calculate cost for all 100M tokens"""
        self.print_header("TEST 4: Full 100M Token Purchase")
        
        result = await self.bee.execute({
            "type": "calculate_cost",
            "token_amount": 100_000_000
        })
        
        self.assert_true(result["success"], "Calculation succeeded")
        self.assert_equal(result["total_cost_usd"], 12_250_000.00, 
                         "Total cost = $12,250,000")
        self.assert_equal(result["average_price_per_token"], 0.1225, 
                         "Weighted avg = $0.1225")
        self.assert_equal(len(result["tier_breakdown"]), 10, "All 10 tiers used")
    
    async def test_investor_whitelist(self):
        """Test 5: Investor whitelist management"""
        self.print_header("TEST 5: Investor Whitelist")
        
        investor_addr = "0x1234567890123456789012345678901234567890"
        
        # Check not whitelisted initially
        result = await self.bee.execute({
            "type": "validate_investor",
            "investor_address": investor_addr
        })
        
        self.assert_false(result["is_whitelisted"], "Not whitelisted initially")
        self.assert_false(result["can_purchase"], "Cannot purchase without KYC")
        
        # Add to whitelist (with Queen approval)
        result = await self.bee.execute({
            "type": "add_to_whitelist",
            "investor_address": investor_addr,
            "kyc_verified": True,
            "queen_approved": True
        })
        
        self.assert_true(result["success"], "Added to whitelist")
        
        # Verify now whitelisted
        result = await self.bee.execute({
            "type": "validate_investor",
            "investor_address": investor_addr
        })
        
        self.assert_true(result["is_whitelisted"], "Now whitelisted")
        self.assert_true(result["can_purchase"], "Can purchase after KYC")
    
    def assert_false(self, condition, test_name):
        """Helper for false assertions"""
        return self.assert_true(not condition, test_name)
    
    async def test_purchase_limits(self):
        """Test 6: Purchase limits and validations"""
        self.print_header("TEST 6: Purchase Limits")
        
        investor_addr = "0x" + "a" * 40
        
        # Add investor to whitelist
        await self.bee.execute({
            "type": "add_to_whitelist",
            "investor_address": investor_addr,
            "kyc_verified": True,
            "queen_approved": True
        })
        
        # Test minimum purchase
        result = await self.bee.execute({
            "type": "process_purchase",
            "investor_address": investor_addr,
            "token_amount": 5_000,  # Below 10K minimum
            "payment_amount_usd": 500
        })
        
        self.assert_false(result["success"], "Rejected below minimum")
        
        # Test Queen approval requirement (>1M tokens)
        result = await self.bee.execute({
            "type": "process_purchase",
            "investor_address": investor_addr,
            "token_amount": 2_000_000,  # Requires Queen approval
            "payment_amount_usd": 200_000
        })
        
        self.assert_true(result.get("requires_queen_approval"), "Large purchase needs Queen approval")
    
    async def test_successful_purchase(self):
        """Test 7: Complete successful purchase"""
        self.print_header("TEST 7: Successful Purchase")
        
        investor_addr = "0x" + "b" * 40
        
        # Add investor to whitelist
        await self.bee.execute({
            "type": "add_to_whitelist",
            "investor_address": investor_addr,
            "kyc_verified": True,
            "queen_approved": True
        })
        
        # Calculate cost for 500K tokens
        cost_calc = await self.bee.execute({
            "type": "calculate_cost",
            "token_amount": 500_000
        })
        
        required_payment = cost_calc["total_cost_usd"]
        
        # Execute purchase
        result = await self.bee.execute({
            "type": "process_purchase",
            "investor_address": investor_addr,
            "token_amount": 500_000,
            "payment_amount_usd": required_payment,
            "payment_tx_hash": "0xabcdef123"
        })
        
        self.assert_true(result["success"], "Purchase succeeded")
        self.assert_equal(result["purchase"]["token_amount"], 500_000, "Correct token amount")
        
        # Verify tokens sold updated
        self.assert_equal(self.bee.tokens_sold, 500_000, "Tokens sold updated")
        self.assert_equal(self.bee.total_raised, required_payment, "Total raised updated")
    
    async def test_current_tier_tracking(self):
        """Test 8: Current tier tracking"""
        self.print_header("TEST 8: Current Tier Tracking")
        
        # Initially at tier 1 with 500K sold from previous test
        result = await self.bee.execute({
            "type": "get_current_tier"
        })
        
        self.assert_equal(result["current_tier"]["tier"], 1, "Currently at tier 1")
        self.assert_equal(result["total_tokens_sold"], 500_000, "500K tokens sold")
    
    async def test_sales_statistics(self):
        """Test 9: Sales statistics reporting"""
        self.print_header("TEST 9: Sales Statistics")
        
        result = await self.bee.execute({
            "type": "get_sales_stats"
        })
        
        self.assert_true(result["success"], "Stats generated")
        self.assert_equal(result["overall_stats"]["total_tokens_sold"], 500_000, 
                         "500K tokens sold")
        self.assert_equal(result["overall_stats"]["tokens_remaining"], 99_500_000, 
                         "99.5M tokens remaining")
        
        # Check tier breakdown exists
        self.assert_equal(len(result["tier_breakdown"]), 10, "All 10 tiers in breakdown")
    
    async def test_purchase_simulation(self):
        """Test 10: Purchase simulation (no execution)"""
        self.print_header("TEST 10: Purchase Simulation")
        
        result = await self.bee.execute({
            "type": "simulate_purchase",
            "token_amount": 25_000_000
        })
        
        self.assert_true(result["success"], "Simulation succeeded")
        self.assert_true(result["simulation"], "Marked as simulation")
        
        # Verify tokens_sold NOT updated
        self.assert_equal(self.bee.tokens_sold, 500_000, "Tokens sold unchanged (still 500K)")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("\n" + "🐝" * 35)
        print("\n   PRIVATE SALE BEE - COMPREHENSIVE TEST SUITE")
        print("\n" + "🐝" * 35)
        
        # Initialize bee
        self.bee = PrivateSaleBee(bee_id=13)
        
        # Run tests in order
        await self.test_tier_pricing_structure()
        await self.test_single_tier_purchase()
        await self.test_cross_tier_purchase()
        await self.test_full_100m_purchase()
        await self.test_investor_whitelist()
        await self.test_purchase_limits()
        await self.test_successful_purchase()
        await self.test_current_tier_tracking()
        await self.test_sales_statistics()
        await self.test_purchase_simulation()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        
        success_rate = (self.passed / (self.passed + self.failed) * 100) if (self.passed + self.failed) > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 ALL TESTS PASSED! PrivateSaleBee is fully operational! 🐝")
        else:
            print(f"\n⚠️ {self.failed} test(s) failed - review implementation")


async def main():
    import sys
    sys.stdout.flush()
    print("Starting tests...", flush=True)
    tests = PrivateSaleTests()
    await tests.run_all_tests()
    print("Tests completed!", flush=True)
    sys.stdout.flush()
    return 0 if tests.failed == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
