"""
Private Sale Bee - Handles private investor token sales with tiered pricing

Manages the private sale of OMK tokens with exact tiered pricing structure.
Works with Queen for approval and security validation.
"""
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime, timedelta

from app.bees.base import BaseBee

logger = structlog.get_logger(__name__)


class PrivateSaleBee(BaseBee):
    """
    Private Sale Management Bee
    
    Responsibilities:
    - Calculate token prices based on tiered structure
    - Process private investor purchases
    - Track sales across all tiers
    - Validate investor eligibility
    - Generate sales reports
    - Work with Queen for approval on large purchases
    
    Exact Pricing Structure (10 tiers, 10M tokens each):
    - Tier 1:  0-10M   @ $0.100 = $1,000,000
    - Tier 2:  10-20M  @ $0.105 = $1,050,000
    - Tier 3:  20-30M  @ $0.110 = $1,100,000
    - Tier 4:  30-40M  @ $0.115 = $1,150,000
    - Tier 5:  40-50M  @ $0.120 = $1,200,000
    - Tier 6:  50-60M  @ $0.125 = $1,250,000
    - Tier 7:  60-70M  @ $0.130 = $1,300,000
    - Tier 8:  70-80M  @ $0.135 = $1,350,000
    - Tier 9:  80-90M  @ $0.140 = $1,400,000
    - Tier 10: 90-100M @ $0.145 = $1,450,000
    
    Total if 100M sold: $12,250,000
    Weighted average: $0.1225 / OMK
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(
            bee_id=bee_id or 13,
            name="private_sale"
        )
        
        # Exact tiered pricing structure
        self.TIER_PRICES = [
            {"tier": 1, "start": 0, "end": 10_000_000, "price": 0.100},
            {"tier": 2, "start": 10_000_000, "end": 20_000_000, "price": 0.105},
            {"tier": 3, "start": 20_000_000, "end": 30_000_000, "price": 0.110},
            {"tier": 4, "start": 30_000_000, "end": 40_000_000, "price": 0.115},
            {"tier": 5, "start": 40_000_000, "end": 50_000_000, "price": 0.120},
            {"tier": 6, "start": 50_000_000, "end": 60_000_000, "price": 0.125},
            {"tier": 7, "start": 60_000_000, "end": 70_000_000, "price": 0.130},
            {"tier": 8, "start": 70_000_000, "end": 80_000_000, "price": 0.135},
            {"tier": 9, "start": 80_000_000, "end": 90_000_000, "price": 0.140},
            {"tier": 10, "start": 90_000_000, "end": 100_000_000, "price": 0.145},
        ]
        
        self.TOTAL_ALLOCATION = 100_000_000  # 100M tokens
        self.TIER_SIZE = 10_000_000  # 10M tokens per tier
        
        # Track sales (in production, this would be from database/blockchain)
        self.tokens_sold = 0
        self.total_raised = 0.0
        self.purchases = []
        self.investor_whitelist = set()  # KYC approved addresses
        
        # Security settings
        self.MIN_PURCHASE = 10_000  # Minimum 10K tokens
        self.MAX_PURCHASE_PER_INVESTOR = 5_000_000  # Max 5M tokens per investor
        self.QUEEN_APPROVAL_THRESHOLD = 1_000_000  # Purchases > 1M tokens need Queen approval
        
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute private sale task
        
        Tasks:
        - calculate_purchase: Calculate cost for token purchase
        - process_purchase: Process an investor purchase
        - get_current_tier: Get current tier info
        - add_to_whitelist: Add investor to KYC whitelist
        - get_sales_report: Generate sales report
        - get_all_requests: Get all OTC requests (for MarketDataAgent)
        """
        task_type = task_data.get("type")
        
        if task_type == "calculate_purchase":
            return await self._calculate_purchase(task_data)
        elif task_type == "process_purchase":
            return await self._process_purchase(task_data)
        elif task_type == "get_current_tier":
            return await self._get_current_tier(task_data)
        elif task_type == "add_to_whitelist":
            return await self._add_to_whitelist(task_data)
        elif task_type == "get_sales_report":
            return await self._get_sales_report(task_data)
        elif task_type == "get_all_requests":
            return await self._get_all_requests(task_data)
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    async def _get_all_requests(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get all OTC requests
        Used by MarketDataAgent for calculating OTC metrics
        """
        try:
            # In production, this would query the database
            # For now, load from JSON file if it exists
            import json
            import os
            
            db_path = "data/otc_requests.json"
            requests = []
            
            if os.path.exists(db_path):
                try:
                    with open(db_path, 'r') as f:
                        requests = json.load(f)
                except Exception as e:
                    logger.warning("Failed to load OTC requests", error=str(e))
            
            # Also include in-memory purchases
            for purchase in self.purchases:
                requests.append({
                    "allocation": purchase.get("tokens", 0),
                    "price_per_token": purchase.get("price_per_token", 0.10),
                    "amount_usd": purchase.get("total_cost", 0),
                    "status": "approved",
                    "timestamp": purchase.get("timestamp", datetime.now().isoformat())
                })
            
            logger.info("OTC requests retrieved", count=len(requests))
            
            return {
                "success": True,
                "requests": requests,
                "count": len(requests)
            }
        except Exception as e:
            logger.error("Failed to get all OTC requests", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _calculate_cost(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate exact USD cost for purchasing tokens across tiers
        
        Handles cross-tier purchases (e.g., 15M tokens spans tiers 1 and 2)
        """
        token_amount = data.get("token_amount", 0)
        
        if token_amount <= 0:
            return {"success": False, "error": "Invalid token amount"}
        
        if token_amount > (self.TOTAL_ALLOCATION - self.tokens_sold):
            return {
                "success": False,
                "error": f"Insufficient tokens available. Only {self.TOTAL_ALLOCATION - self.tokens_sold:,} tokens remaining"
            }
        
        # Calculate cost across tiers
        total_cost = 0.0
        tokens_remaining = token_amount
        current_position = self.tokens_sold
        tier_breakdown = []
        
        for tier_info in self.TIER_PRICES:
            if tokens_remaining <= 0:
                break
            
            # Skip tiers already sold out
            if current_position >= tier_info["end"]:
                continue
            
            # Calculate tokens available in this tier
            tier_start = max(current_position, tier_info["start"])
            tier_available = tier_info["end"] - tier_start
            
            # Tokens to buy from this tier
            tokens_from_tier = min(tokens_remaining, tier_available)
            
            # Cost from this tier
            tier_cost = tokens_from_tier * tier_info["price"]
            total_cost += tier_cost
            
            tier_breakdown.append({
                "tier": tier_info["tier"],
                "tokens": tokens_from_tier,
                "price_per_token": tier_info["price"],
                "subtotal": round(tier_cost, 2)
            })
            
            tokens_remaining -= tokens_from_tier
            current_position += tokens_from_tier
        
        avg_price = total_cost / token_amount if token_amount > 0 else 0
        
        return {
            "success": True,
            "token_amount": token_amount,
            "total_cost_usd": round(total_cost, 2),
            "average_price_per_token": round(avg_price, 6),
            "tier_breakdown": tier_breakdown,
            "tokens_sold_before": self.tokens_sold,
            "tokens_sold_after": self.tokens_sold + token_amount
        }
    
    async def _process_purchase(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process actual investor purchase
        
        Validates investor, calculates cost, checks limits, 
        requests Queen approval if needed, and executes purchase
        """
        investor_address = data.get("investor_address")
        token_amount = data.get("token_amount", 0)
        payment_amount_usd = data.get("payment_amount_usd", 0)
        payment_tx_hash = data.get("payment_tx_hash")
        
        # Validation 1: Investor whitelist
        if investor_address not in self.investor_whitelist:
            return {
                "success": False,
                "error": "Investor not whitelisted. Complete KYC first.",
                "requires_kyc": True
            }
        
        # Validation 2: Purchase limits
        if token_amount < self.MIN_PURCHASE:
            return {
                "success": False,
                "error": f"Minimum purchase is {self.MIN_PURCHASE:,} tokens"
            }
        
        # Check investor's previous purchases
        investor_total = sum(
            p["token_amount"] 
            for p in self.purchases 
            if p["investor_address"] == investor_address
        )
        
        if investor_total + token_amount > self.MAX_PURCHASE_PER_INVESTOR:
            return {
                "success": False,
                "error": f"Maximum {self.MAX_PURCHASE_PER_INVESTOR:,} tokens per investor. You have {investor_total:,} already."
            }
        
        # Calculate exact cost
        cost_calc = await self._calculate_cost({"token_amount": token_amount})
        if not cost_calc["success"]:
            return cost_calc
        
        required_payment = cost_calc["total_cost_usd"]
        
        # Validation 3: Payment amount
        if abs(payment_amount_usd - required_payment) > 0.01:  # Allow 1 cent tolerance
            return {
                "success": False,
                "error": f"Payment amount mismatch. Required: ${required_payment:.2f}, Received: ${payment_amount_usd:.2f}"
            }
        
        # Validation 4: Queen approval for large purchases
        needs_queen_approval = token_amount >= self.QUEEN_APPROVAL_THRESHOLD
        
        if needs_queen_approval:
            return {
                "success": False,
                "requires_queen_approval": True,
                "purchase_details": {
                    "investor_address": investor_address,
                    "token_amount": token_amount,
                    "payment_amount_usd": required_payment,
                    "tier_breakdown": cost_calc["tier_breakdown"]
                },
                "message": f"Purchase of {token_amount:,} tokens requires Queen approval. Please wait for authorization."
            }
        
        # Execute purchase
        purchase_record = {
            "purchase_id": len(self.purchases) + 1,
            "investor_address": investor_address,
            "token_amount": token_amount,
            "payment_amount_usd": required_payment,
            "payment_tx_hash": payment_tx_hash,
            "tier_breakdown": cost_calc["tier_breakdown"],
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        
        self.purchases.append(purchase_record)
        self.tokens_sold += token_amount
        self.total_raised += required_payment
        
        logger.info(
            f"Purchase completed",
            investor=investor_address,
            tokens=token_amount,
            cost=required_payment
        )
        
        return {
            "success": True,
            "message": "Purchase completed successfully",
            "purchase": purchase_record,
            "tokens_remaining": self.TOTAL_ALLOCATION - self.tokens_sold,
            "total_raised": round(self.total_raised, 2)
        }
    
    async def _get_current_tier(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get current tier information"""
        current_tier_info = None
        
        for tier in self.TIER_PRICES:
            if self.tokens_sold < tier["end"]:
                tokens_sold_in_tier = max(0, self.tokens_sold - tier["start"])
                tokens_remaining_in_tier = tier["end"] - tier["start"] - tokens_sold_in_tier
                
                current_tier_info = {
                    "tier": tier["tier"],
                    "price_per_token": tier["price"],
                    "tokens_sold_in_tier": tokens_sold_in_tier,
                    "tokens_remaining_in_tier": tokens_remaining_in_tier,
                    "tier_capacity": self.TIER_SIZE,
                    "progress_percentage": round((tokens_sold_in_tier / self.TIER_SIZE) * 100, 2)
                }
                break
        
        if not current_tier_info:
            current_tier_info = {
                "tier": "SOLD OUT",
                "message": "All 100M tokens have been sold"
            }
        
        return {
            "success": True,
            "current_tier": current_tier_info,
            "total_tokens_sold": self.tokens_sold,
            "total_tokens_available": self.TOTAL_ALLOCATION,
            "sale_progress_percentage": round((self.tokens_sold / self.TOTAL_ALLOCATION) * 100, 2)
        }
    
    async def _get_remaining_tokens(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed breakdown of remaining tokens at each tier"""
        remaining_by_tier = []
        
        for tier in self.TIER_PRICES:
            tokens_sold_in_tier = max(0, min(
                self.tokens_sold - tier["start"],
                tier["end"] - tier["start"]
            ))
            tokens_remaining = (tier["end"] - tier["start"]) - tokens_sold_in_tier
            
            remaining_by_tier.append({
                "tier": tier["tier"],
                "price_per_token": tier["price"],
                "tokens_remaining": tokens_remaining,
                "status": "available" if tokens_remaining > 0 else "sold_out"
            })
        
        return {
            "success": True,
            "remaining_by_tier": remaining_by_tier,
            "total_remaining": self.TOTAL_ALLOCATION - self.tokens_sold
        }
    
    async def _validate_investor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if investor is eligible (whitelisted)"""
        investor_address = data.get("investor_address")
        
        is_whitelisted = investor_address in self.investor_whitelist
        
        # Get investor purchase history
        investor_purchases = [
            p for p in self.purchases 
            if p["investor_address"] == investor_address
        ]
        
        investor_total_tokens = sum(p["token_amount"] for p in investor_purchases)
        investor_total_spent = sum(p["payment_amount_usd"] for p in investor_purchases)
        
        remaining_allocation = self.MAX_PURCHASE_PER_INVESTOR - investor_total_tokens
        
        return {
            "success": True,
            "investor_address": investor_address,
            "is_whitelisted": is_whitelisted,
            "kyc_status": "approved" if is_whitelisted else "pending",
            "purchase_history": {
                "total_purchases": len(investor_purchases),
                "total_tokens": investor_total_tokens,
                "total_spent_usd": round(investor_total_spent, 2),
                "remaining_allocation": remaining_allocation
            },
            "can_purchase": is_whitelisted and remaining_allocation > 0
        }
    
    async def _add_to_whitelist(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add investor to KYC whitelist (requires Queen approval)
        """
        investor_address = data.get("investor_address")
        kyc_verified = data.get("kyc_verified", False)
        queen_approved = data.get("queen_approved", False)
        
        if not kyc_verified:
            return {
                "success": False,
                "error": "KYC verification required"
            }
        
        if not queen_approved:
            return {
                "success": False,
                "requires_queen_approval": True,
                "message": "KYC whitelist addition requires Queen approval"
            }
        
        self.investor_whitelist.add(investor_address)
        
        logger.info(f"Investor added to whitelist", investor=investor_address)
        
        return {
            "success": True,
            "message": "Investor added to whitelist",
            "investor_address": investor_address,
            "total_whitelisted": len(self.investor_whitelist)
        }
    
    async def _get_sales_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive sales statistics"""
        
        # Calculate weighted average price
        weighted_avg_price = (self.total_raised / self.tokens_sold) if self.tokens_sold > 0 else 0
        
        # Tier-by-tier sales
        tier_sales = []
        for tier in self.TIER_PRICES:
            tokens_sold_in_tier = max(0, min(
                self.tokens_sold - tier["start"],
                tier["end"] - tier["start"]
            ))
            revenue_from_tier = tokens_sold_in_tier * tier["price"]
            
            tier_sales.append({
                "tier": tier["tier"],
                "price": tier["price"],
                "tokens_sold": tokens_sold_in_tier,
                "revenue_usd": round(revenue_from_tier, 2),
                "status": "sold_out" if tokens_sold_in_tier >= self.TIER_SIZE else "active"
            })
        
        # Investor statistics
        unique_investors = len(set(p["investor_address"] for p in self.purchases))
        
        return {
            "success": True,
            "overall_stats": {
                "total_tokens_sold": self.tokens_sold,
                "total_tokens_available": self.TOTAL_ALLOCATION,
                "tokens_remaining": self.TOTAL_ALLOCATION - self.tokens_sold,
                "total_raised_usd": round(self.total_raised, 2),
                "target_raise_usd": 12_250_000,
                "progress_percentage": round((self.tokens_sold / self.TOTAL_ALLOCATION) * 100, 2),
                "weighted_avg_price": round(weighted_avg_price, 6),
                "target_avg_price": 0.1225
            },
            "tier_breakdown": tier_sales,
            "investor_stats": {
                "total_investors": unique_investors,
                "total_purchases": len(self.purchases),
                "whitelisted_investors": len(self.investor_whitelist),
                "avg_purchase_size": round(self.tokens_sold / len(self.purchases), 0) if self.purchases else 0
            }
        }
    
    async def _simulate_purchase(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate a purchase without executing it
        Useful for UI previews and investor planning
        """
        token_amount = data.get("token_amount", 0)
        
        # Calculate cost
        cost_calc = await self._calculate_cost({"token_amount": token_amount})
        
        if not cost_calc["success"]:
            return cost_calc
        
        # Add simulation metadata
        cost_calc["simulation"] = True
        cost_calc["note"] = "This is a simulation. No purchase was executed."
        
        # Add requirements checklist
        cost_calc["requirements"] = {
            "minimum_purchase": self.MIN_PURCHASE,
            "maximum_purchase": self.MAX_PURCHASE_PER_INVESTOR,
            "queen_approval_needed": token_amount >= self.QUEEN_APPROVAL_THRESHOLD,
            "kyc_required": True
        }
        
        return cost_calc
