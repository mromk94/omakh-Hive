"""
MathsBee - Mathematical calculations and pool analysis
"""
from typing import Dict, Any
import structlog
from app.bees.base import BaseBee

logger = structlog.get_logger(__name__)


class MathsBee(BaseBee):
    """
    Specialized bee for mathematical operations
    
    Responsibilities:
    - AMM pool calculations (x*y=k)
    - Slippage analysis
    - Rebalance amount calculations
    - APY calculations
    - Reward distributions
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id, name="MathsBee")
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mathematical task"""
        task_type = task_data.get("type")
        
        if task_type == "calculate_slippage":
            return await self._calculate_slippage(task_data)
        elif task_type == "calculate_pool_ratio":
            return await self._calculate_pool_ratio(task_data)
        elif task_type == "calculate_rebalance":
            return await self._calculate_rebalance(task_data)
        elif task_type == "calculate_apy":
            return await self._calculate_apy(task_data)
        elif task_type == "calculate_weighted_average_price":
            return await self._calculate_weighted_average_price(task_data)
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    async def _calculate_slippage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate slippage for a trade"""
        try:
            reserve_in = data.get("reserve_in", 0)
            reserve_out = data.get("reserve_out", 0)
            amount_in = data.get("amount_in", 0)
            
            if reserve_in == 0 or reserve_out == 0:
                return {"success": False, "error": "Invalid reserves"}
            
            # AMM formula: amount_out = (amount_in * reserve_out) / (reserve_in + amount_in)
            amount_out = (amount_in * reserve_out) / (reserve_in + amount_in)
            
            # Expected without slippage
            price = reserve_out / reserve_in
            expected_out = amount_in * price
            
            # Slippage percentage
            slippage = ((expected_out - amount_out) / expected_out) * 100
            
            return {
                "success": True,
                "amount_out": amount_out,
                "expected_out": expected_out,
                "slippage_percent": round(slippage, 4),
                "price_impact": round(slippage, 4),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _calculate_pool_ratio(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate pool ratio and health"""
        try:
            token_a_amount = data.get("token_a", 0)
            token_b_amount = data.get("token_b", 0)
            target_ratio = data.get("target_ratio", 1.0)
            
            if token_a_amount == 0 or token_b_amount == 0:
                return {"success": False, "error": "Invalid token amounts"}
            
            current_ratio = token_a_amount / token_b_amount
            deviation = abs(current_ratio - target_ratio) / target_ratio
            
            return {
                "success": True,
                "current_ratio": current_ratio,
                "target_ratio": target_ratio,
                "deviation_percent": round(deviation * 100, 2),
                "needs_rebalance": deviation > 0.1,  # >10% deviation
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _calculate_rebalance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate amount needed to rebalance pool"""
        try:
            token_a_amount = data.get("token_a", 0)
            token_b_amount = data.get("token_b", 0)
            target_ratio = data.get("target_ratio", 1.0)
            
            # Calculate how much to add/remove to reach target ratio
            # target_ratio = (token_a + delta) / token_b
            # delta = (target_ratio * token_b) - token_a
            
            target_token_a = target_ratio * token_b_amount
            delta = target_token_a - token_a_amount
            
            action = "add" if delta > 0 else "remove"
            amount = abs(delta)
            
            return {
                "success": True,
                "action": action,
                "amount": amount,
                "token": "token_a",
                "current_a": token_a_amount,
                "current_b": token_b_amount,
                "target_a": target_token_a,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _calculate_apy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate APY for staking"""
        try:
            total_staked = data.get("total_staked", 0)
            annual_rewards = data.get("annual_rewards", 0)
            treasury_health = data.get("treasury_health", 1.0)
            
            if total_staked == 0:
                return {"success": False, "error": "No tokens staked"}
            
            # Base APY
            base_apy = (annual_rewards / total_staked) * 100
            
            # Adjust based on treasury health
            if treasury_health > 1.5:
                adjusted_apy = min(base_apy * 1.2, 15.0)  # Max 15%
            elif treasury_health < 0.8:
                adjusted_apy = max(base_apy * 0.8, 8.0)   # Min 8%
            else:
                adjusted_apy = base_apy
            
            return {
                "success": True,
                "base_apy": round(base_apy, 2),
                "adjusted_apy": round(adjusted_apy, 2),
                "treasury_health": treasury_health,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _calculate_weighted_average_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate weighted average price from OTC requests
        Used by MarketDataAgent for OTC price calculation
        """
        try:
            requests = data.get("requests", [])
            
            if not requests:
                return {
                    "success": True,
                    "average_price": 0.10,  # Default
                    "total_requests": 0,
                    "total_volume": 0
                }
            
            total_value = 0
            total_allocation = 0
            
            for req in requests:
                try:
                    allocation = float(req.get("allocation", 0))
                    price = float(req.get("price_per_token", 0.10))
                    
                    if allocation > 0 and price > 0:
                        total_value += allocation * price
                        total_allocation += allocation
                except (ValueError, TypeError):
                    continue
            
            if total_allocation == 0:
                return {
                    "success": True,
                    "average_price": 0.10,
                    "total_requests": len(requests),
                    "total_volume": 0
                }
            
            average_price = total_value / total_allocation
            
            return {
                "success": True,
                "average_price": round(average_price, 4),
                "total_requests": len(requests),
                "total_allocation": total_allocation,
                "total_value": total_value,
                "min_price": min((float(r.get("price_per_token", 0.10)) for r in requests if r.get("allocation", 0) > 0), default=0.10),
                "max_price": max((float(r.get("price_per_token", 0.10)) for r in requests if r.get("allocation", 0) > 0), default=0.10)
            }
        except Exception as e:
            logger.error("Failed to calculate weighted average price", error=str(e))
            return {"success": False, "error": str(e)}
