"""
Stake Bot Bee - Staking pool management

Manages staking pools and adjusts rewards in real time.
AI evaluates TVL (Total Value Locked) vs. yield ratio.
Automatically adjusts APY to maintain system sustainability.
"""
from typing import Dict, Any, List
import structlog
from app.bees.base import BaseBee

logger = structlog.get_logger(__name__)


class StakeBotBee(BaseBee):
    """
    Specialized bee for staking operations
    
    Responsibilities:
    - Manage staking pools
    - Adjust rewards in real-time
    - Evaluate TVL vs yield ratio
    - Automatically adjust APY for sustainability
    - Calculate lock period multipliers
    - Distribute daily rewards
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id, name="StakeBotBee")
        # Staking configuration
        self.base_apy_range = (8, 15)  # 8-15% base APY
        self.lock_multipliers = {
            7: 1.0,    # 7 days: 1.0x
            30: 1.1,   # 30 days: 1.1x
            90: 1.25,  # 90 days: 1.25x
            180: 1.5,  # 180 days: 1.5x
        }
        self.ecosystem_pool = 40_000_000 * 10**18  # 40M OMK for staking
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute staking task"""
        task_type = task_data.get("type")
        
        if task_type == "calculate_apy":
            return await self._calculate_apy(task_data)
        elif task_type == "calculate_rewards":
            return await self._calculate_rewards(task_data)
        elif task_type == "distribute_rewards":
            return await self._distribute_rewards(task_data)
        elif task_type == "evaluate_tvl":
            return await self._evaluate_tvl(task_data)
        elif task_type == "adjust_apy":
            return await self._adjust_apy(task_data)
        elif task_type == "process_stake":
            return await self._process_stake(task_data)
        elif task_type == "process_unstake":
            return await self._process_unstake(task_data)
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    async def _calculate_apy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal APY based on system conditions"""
        try:
            total_staked = data.get("total_staked")
            treasury_health = data.get("treasury_health", 1.0)
            market_conditions = data.get("market_conditions", "stable")
            protocol_revenue = data.get("protocol_revenue", 0)
            
            # Base APY calculation
            min_apy, max_apy = self.base_apy_range
            base_apy = min_apy + ((max_apy - min_apy) / 2)  # Start at middle
            
            # Adjust based on treasury health
            if treasury_health > 1.5:
                base_apy = min(max_apy, base_apy * 1.2)  # Increase APY if healthy
            elif treasury_health < 0.8:
                base_apy = max(min_apy, base_apy * 0.8)  # Decrease if unhealthy
            
            # Adjust based on market conditions
            market_multipliers = {
                "bull": 1.1,
                "stable": 1.0,
                "bear": 0.9,
            }
            base_apy *= market_multipliers.get(market_conditions, 1.0)
            
            # Adjust based on TVL ratio
            optimal_tvl = 50_000_000 * 10**18  # 50M OMK optimal
            tvl_ratio = total_staked / optimal_tvl if optimal_tvl > 0 else 0
            
            if tvl_ratio > 1.5:  # Too much staked
                base_apy *= 0.9  # Lower APY to discourage more staking
            elif tvl_ratio < 0.5:  # Too little staked
                base_apy *= 1.1  # Higher APY to encourage staking
            
            # Ensure within bounds
            final_apy = max(min_apy, min(max_apy, base_apy))
            
            # Calculate annual rewards needed
            annual_rewards = total_staked * (final_apy / 100)
            
            # Check sustainability
            sustainable = annual_rewards < (self.ecosystem_pool * 0.5)  # Use max 50% per year
            
            return {
                "success": True,
                "calculated_apy": round(final_apy, 2),
                "min_apy": min_apy,
                "max_apy": max_apy,
                "annual_rewards_needed": annual_rewards,
                "sustainable": sustainable,
                "treasury_health": treasury_health,
                "tvl_ratio": round(tvl_ratio, 2),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _calculate_rewards(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate staking rewards for a user"""
        try:
            staked_amount = data.get("staked_amount")
            lock_period_days = data.get("lock_period_days")
            current_apy = data.get("current_apy", 10.0)
            days_staked = data.get("days_staked", 1)
            
            # Get lock multiplier
            multiplier = self.lock_multipliers.get(lock_period_days, 1.0)
            
            # Calculate effective APY
            effective_apy = current_apy * multiplier
            
            # Calculate daily rewards
            daily_rewards = staked_amount * (effective_apy / 100 / 365)
            
            # Calculate total rewards
            total_rewards = daily_rewards * days_staked
            
            # Calculate yearly projection
            yearly_rewards = staked_amount * (effective_apy / 100)
            
            return {
                "success": True,
                "staked_amount": staked_amount,
                "lock_period_days": lock_period_days,
                "base_apy": current_apy,
                "lock_multiplier": multiplier,
                "effective_apy": round(effective_apy, 2),
                "daily_rewards": daily_rewards,
                "total_rewards": total_rewards,
                "yearly_projection": yearly_rewards,
                "days_staked": days_staked,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _distribute_rewards(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Distribute daily staking rewards"""
        try:
            total_staked = data.get("total_staked")
            current_apy = data.get("current_apy")
            stakers = data.get("stakers", [])  # List of {address, amount, lock_period}
            
            # Calculate total daily rewards
            daily_rate = current_apy / 100 / 365
            
            distributions = []
            total_distributed = 0
            
            for staker in stakers:
                amount = staker.get("amount")
                lock_period = staker.get("lock_period_days", 7)
                address = staker.get("address")
                
                # Apply multiplier
                multiplier = self.lock_multipliers.get(lock_period, 1.0)
                effective_rate = daily_rate * multiplier
                
                # Calculate reward
                reward = amount * effective_rate
                
                distributions.append({
                    "address": address,
                    "reward": reward,
                    "base_amount": amount,
                    "lock_period": lock_period,
                    "multiplier": multiplier,
                })
                
                total_distributed += reward
            
            return {
                "success": True,
                "distributions": distributions,
                "total_distributed": total_distributed,
                "total_stakers": len(stakers),
                "current_apy": current_apy,
                "timestamp": "2025-10-09T09:50:00Z",
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _evaluate_tvl(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate TVL vs yield ratio"""
        try:
            total_staked = data.get("total_staked")
            current_apy = data.get("current_apy")
            protocol_revenue = data.get("protocol_revenue", 0)
            
            # Calculate annual yield cost
            annual_yield_cost = total_staked * (current_apy / 100)
            
            # Calculate yield/revenue ratio
            if protocol_revenue > 0:
                yield_revenue_ratio = annual_yield_cost / protocol_revenue
            else:
                yield_revenue_ratio = float('inf')
            
            # Optimal TVL (50M OMK)
            optimal_tvl = 50_000_000 * 10**18
            tvl_utilization = (total_staked / optimal_tvl * 100) if optimal_tvl > 0 else 0
            
            # Determine health
            if yield_revenue_ratio > 2.0:
                health_status = "unsustainable"
                recommendation = "Reduce APY or increase revenue"
            elif yield_revenue_ratio > 1.0:
                health_status = "concerning"
                recommendation = "Monitor closely, consider APY adjustment"
            else:
                health_status = "healthy"
                recommendation = "Current levels sustainable"
            
            # TVL recommendation
            if tvl_utilization > 150:
                tvl_recommendation = "TVL too high, reduce incentives"
            elif tvl_utilization < 50:
                tvl_recommendation = "TVL too low, increase incentives"
            else:
                tvl_recommendation = "TVL in optimal range"
            
            return {
                "success": True,
                "total_staked": total_staked,
                "current_apy": current_apy,
                "annual_yield_cost": annual_yield_cost,
                "protocol_revenue": protocol_revenue,
                "yield_revenue_ratio": round(yield_revenue_ratio, 2) if yield_revenue_ratio != float('inf') else "N/A",
                "tvl_utilization_percent": round(tvl_utilization, 2),
                "health_status": health_status,
                "recommendation": recommendation,
                "tvl_recommendation": tvl_recommendation,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _adjust_apy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically adjust APY based on system state"""
        try:
            current_apy = data.get("current_apy")
            total_staked = data.get("total_staked")
            treasury_health = data.get("treasury_health")
            
            # Calculate new APY
            apy_result = await self._calculate_apy({
                "total_staked": total_staked,
                "treasury_health": treasury_health,
            })
            
            if not apy_result.get("success"):
                return apy_result
            
            new_apy = apy_result["calculated_apy"]
            change = new_apy - current_apy
            change_percent = (change / current_apy * 100) if current_apy > 0 else 0
            
            # Determine if adjustment needed
            should_adjust = abs(change_percent) > 5  # Only adjust if >5% change
            
            return {
                "success": True,
                "current_apy": current_apy,
                "recommended_apy": new_apy,
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "should_adjust": should_adjust,
                "sustainable": apy_result["sustainable"],
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_stake(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a new stake"""
        try:
            user_address = data.get("user_address")
            amount = data.get("amount")
            lock_period_days = data.get("lock_period_days", 7)
            
            # Validate lock period
            if lock_period_days not in self.lock_multipliers:
                return {
                    "success": False,
                    "error": f"Invalid lock period. Valid options: {list(self.lock_multipliers.keys())}"
                }
            
            # Get current APY
            current_apy = 10.0  # Mock - in production, query from contract
            
            # Calculate expected rewards
            rewards_calc = await self._calculate_rewards({
                "staked_amount": amount,
                "lock_period_days": lock_period_days,
                "current_apy": current_apy,
                "days_staked": lock_period_days,
            })
            
            return {
                "success": True,
                "user_address": user_address,
                "staked_amount": amount,
                "lock_period_days": lock_period_days,
                "lock_multiplier": self.lock_multipliers[lock_period_days],
                "effective_apy": rewards_calc["effective_apy"],
                "expected_rewards": rewards_calc["total_rewards"],
                "status": "active",
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_unstake(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an unstake request"""
        try:
            user_address = data.get("user_address")
            amount = data.get("amount")
            lock_end_date = data.get("lock_end_date")
            current_date = data.get("current_date")
            
            # Check if lock period ended
            lock_ended = current_date >= lock_end_date
            
            # Calculate early exit penalty if applicable
            penalty = 0
            if not lock_ended:
                penalty = amount * 0.05  # 5% penalty for early exit
            
            final_amount = amount - penalty
            
            return {
                "success": True,
                "user_address": user_address,
                "requested_amount": amount,
                "penalty": penalty,
                "final_amount": final_amount,
                "lock_ended": lock_ended,
                "status": "processed",
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
