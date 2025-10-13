"""
Purchase Bee - User swap facilitation and order routing

Facilitates user swaps and orders across both internal and external DEXs.
Tracks gas usage, slippage, and transaction health.
Prioritizes routes that minimize fees and maximize liquidity balance.
"""
from typing import Dict, Any, List, Optional
import structlog
from app.bees.base import BaseBee

logger = structlog.get_logger(__name__)


class PurchaseBee(BaseBee):
    """
    Specialized bee for purchase/swap operations
    
    Responsibilities:
    - Facilitate user swaps and orders
    - Route optimization (internal vs external DEXs)
    - Gas usage tracking and optimization
    - Slippage monitoring and protection
    - Transaction health monitoring
    - Multi-DEX route comparison
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id, name="PurchaseBee")
        # DEX registry
        self.dexes = {
            "omk_internal": {"fee": 0.003, "liquidity_score": 85},
            "uniswap_v3": {"fee": 0.003, "liquidity_score": 95},
            "sushiswap": {"fee": 0.0025, "liquidity_score": 75},
            "pancakeswap": {"fee": 0.0025, "liquidity_score": 80},
        }
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute purchase task"""
        task_type = task_data.get("type")
        
        if task_type == "execute_swap":
            return await self._execute_swap(task_data)
        elif task_type == "find_best_route":
            return await self._find_best_route(task_data)
        elif task_type == "estimate_swap":
            return await self._estimate_swap(task_data)
        elif task_type == "track_order":
            return await self._track_order(task_data)
        elif task_type == "optimize_gas":
            return await self._optimize_gas(task_data)
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    async def _execute_swap(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a token swap"""
        try:
            token_in = data.get("token_in")
            token_out = data.get("token_out")
            amount_in = data.get("amount_in")
            max_slippage = data.get("max_slippage", 0.01)  # 1% default
            user_address = data.get("user_address")
            
            # Find best route
            route_result = await self._find_best_route({
                "token_in": token_in,
                "token_out": token_out,
                "amount_in": amount_in,
                "max_slippage": max_slippage,
            })
            
            if not route_result.get("success"):
                return route_result
            
            best_route = route_result["best_route"]
            
            # Execute swap (in production, would call DEX contract)
            amount_out = best_route["estimated_output"]
            actual_slippage = best_route["slippage"]
            
            # Mock transaction execution
            tx_hash = "0x" + "swap" + "abc123" * 8
            
            logger.info(
                "Swap executed",
                token_in=token_in,
                token_out=token_out,
                amount_in=amount_in,
                amount_out=amount_out,
                dex=best_route["dex"],
                user=user_address
            )
            
            return {
                "success": True,
                "tx_hash": tx_hash,
                "token_in": token_in,
                "token_out": token_out,
                "amount_in": amount_in,
                "amount_out": amount_out,
                "dex_used": best_route["dex"],
                "slippage": actual_slippage,
                "gas_used": best_route["estimated_gas"],
                "total_fee": best_route["total_fee"],
                "route": best_route["path"],
                "status": "confirmed",
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _find_best_route(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Find optimal swap route across DEXs"""
        try:
            token_in = data.get("token_in")
            token_out = data.get("token_out")
            amount_in = data.get("amount_in")
            max_slippage = data.get("max_slippage", 0.01)
            
            routes = []
            
            # Evaluate each DEX
            for dex_name, dex_info in self.dexes.items():
                # Mock route calculation (in production, query actual DEX)
                estimated_output = amount_in * 0.997  # After fees
                slippage = 0.005  # 0.5% mock slippage
                gas_cost = 150000 if "uniswap" in dex_name else 120000
                
                # Calculate total cost
                fee = amount_in * dex_info["fee"]
                total_fee = fee + (gas_cost * 30 * 10**9 / 10**18)  # Gas in ETH
                
                # Calculate net output
                net_output = estimated_output - total_fee
                
                # Check if within slippage tolerance
                if slippage <= max_slippage:
                    routes.append({
                        "dex": dex_name,
                        "path": [token_in, token_out],
                        "estimated_output": estimated_output,
                        "net_output": net_output,
                        "slippage": slippage,
                        "fee_percent": dex_info["fee"] * 100,
                        "total_fee": total_fee,
                        "estimated_gas": gas_cost,
                        "liquidity_score": dex_info["liquidity_score"],
                    })
            
            if not routes:
                return {
                    "success": False,
                    "error": "No routes found within slippage tolerance"
                }
            
            # Sort by net output (best first)
            routes.sort(key=lambda x: x["net_output"], reverse=True)
            best_route = routes[0]
            
            return {
                "success": True,
                "best_route": best_route,
                "all_routes": routes,
                "routes_evaluated": len(routes),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _estimate_swap(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate swap output and costs"""
        try:
            token_in = data.get("token_in")
            token_out = data.get("token_out")
            amount_in = data.get("amount_in")
            
            # Find best route
            route_result = await self._find_best_route({
                "token_in": token_in,
                "token_out": token_out,
                "amount_in": amount_in,
            })
            
            if not route_result.get("success"):
                return route_result
            
            best_route = route_result["best_route"]
            
            return {
                "success": True,
                "estimated_output": best_route["estimated_output"],
                "net_output": best_route["net_output"],
                "estimated_slippage": best_route["slippage"],
                "fee": best_route["total_fee"],
                "gas_estimate": best_route["estimated_gas"],
                "recommended_dex": best_route["dex"],
                "price_impact": best_route["slippage"] * 100,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _track_order(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Track order status"""
        try:
            tx_hash = data.get("tx_hash")
            
            # Mock order tracking (in production, query blockchain)
            status = "confirmed"
            confirmations = 12
            
            return {
                "success": True,
                "tx_hash": tx_hash,
                "status": status,
                "confirmations": confirmations,
                "health": "healthy",
                "timestamp": "2025-10-09T09:50:00Z",
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _optimize_gas(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize gas usage for swap"""
        try:
            swap_type = data.get("swap_type", "standard")
            urgency = data.get("urgency", "normal")
            
            # Base gas estimates
            gas_estimates = {
                "standard": 120000,
                "with_permit": 150000,
                "multi_hop": 200000,
            }
            
            base_gas = gas_estimates.get(swap_type, 120000)
            
            # Gas price multipliers based on urgency
            multipliers = {
                "low": 0.8,
                "normal": 1.0,
                "high": 1.3,
                "urgent": 1.6,
            }
            
            multiplier = multipliers.get(urgency, 1.0)
            base_price = 30 * 10**9  # 30 gwei
            optimized_price = int(base_price * multiplier)
            
            total_cost = base_gas * optimized_price
            
            return {
                "success": True,
                "swap_type": swap_type,
                "urgency": urgency,
                "estimated_gas": base_gas,
                "gas_price_gwei": optimized_price / 10**9,
                "total_cost_wei": total_cost,
                "total_cost_eth": total_cost / 10**18,
                "estimated_time": self._estimate_time(urgency),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _estimate_time(self, urgency: str) -> str:
        """Estimate confirmation time"""
        times = {
            "low": "5-10 minutes",
            "normal": "1-3 minutes",
            "high": "30-60 seconds",
            "urgent": "15-30 seconds",
        }
        return times.get(urgency, "1-3 minutes")
