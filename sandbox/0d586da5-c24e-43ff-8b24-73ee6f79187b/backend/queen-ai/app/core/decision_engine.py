"""
Decision Engine - Autonomous decision-making for Queen AI

Makes real-time decisions about:
- Liquidity management (DEX operations)
- Staking rewards distribution
- Airdrops and campaigns
- Treasury allocations
- Cross-chain operations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.config.settings import settings

logger = structlog.get_logger(__name__)


class DecisionEngine:
    """
    Autonomous decision-making engine
    
    Analyzes system state and market conditions to make
    operational decisions within Queen's authority:
    
    1. DEX Liquidity Management
    2. Staking Rewards (40M OMK ecosystem pool)
    3. Airdrops & Campaigns (25M OMK ecosystem pool)
    4. Cross-chain bridge operations
    5. Treasury proposals
    """
    
    def __init__(self, llm=None):
        self.llm = llm  # LLM abstraction for AI-driven decisions
        self.pending_decisions: List[Dict[str, Any]] = []
    
    async def get_pending(self) -> List[Dict[str, Any]]:
        """Get pending decisions that need to be executed"""
        return self.pending_decisions.copy()
    
    async def analyze_liquidity_needs(
        self,
        pool_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze if DEX pools need liquidity adjustment
        
        Queen's Responsibilities (from QUEEN_AUTONOMY_ARCHITECTURE):
        - Add/remove liquidity from AMM pools
        - Rebalance pools to maintain optimal ratios
        - Slippage management
        - Max 50M OMK per day (5% rate limit)
        
        Returns decision or None
        """
        try:
            # Extract pool metrics
            current_ratio = pool_data.get("ratio", 0)
            optimal_ratio = pool_data.get("optimal_ratio", 1.0)
            slippage = pool_data.get("slippage", 0)
            volume_24h = pool_data.get("volume_24h", 0)
            
            # Decision criteria
            ratio_deviation = abs(current_ratio - optimal_ratio) / optimal_ratio
            high_slippage = slippage > 0.02  # >2% slippage
            low_liquidity = pool_data.get("liquidity_usd", 0) < 100000  # <$100K
            
            # Determine if action needed
            if ratio_deviation > 0.1:  # >10% deviation
                action = "rebalance"
                amount = self._calculate_rebalance_amount(pool_data)
            elif high_slippage or low_liquidity:
                action = "add_liquidity"
                amount = self._calculate_liquidity_addition(pool_data, volume_24h)
            else:
                return None  # No action needed
            
            # Create decision
            decision = {
                "type": "liquidity_management",
                "action": action,
                "pool": pool_data.get("address"),
                "amount": amount,
                "reason": f"Ratio deviation: {ratio_deviation:.2%}, Slippage: {slippage:.2%}",
                "confidence": 0.85,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            logger.info("Liquidity decision generated", 
                       action=action, 
                       amount=amount,
                       pool=pool_data.get("name"))
            
            return decision
            
        except Exception as e:
            logger.error("Failed to analyze liquidity needs", error=str(e))
            return None
    
    async def calculate_staking_rewards(
        self,
        staking_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate daily staking rewards distribution
        
        From ECOSYSTEM_PROGRAMS.md:
        - 40M OMK allocated for staking rewards (40% of ecosystem)
        - APY: 8-15% (Queen adjusts based on treasury health)
        - Lock period multipliers: 7d(1.0x), 30d(1.1x), 90d(1.25x), 180d(1.5x)
        - Daily distribution
        
        Returns reward distribution plan
        """
        try:
            total_staked = staking_data.get("total_staked", 0)
            treasury_health = staking_data.get("treasury_health", 1.0)
            
            # Calculate dynamic APY based on treasury health
            base_apy = 0.10  # 10% base
            if treasury_health > 1.5:
                base_apy = 0.15  # 15% if treasury very healthy
            elif treasury_health < 0.8:
                base_apy = 0.08  # 8% if treasury stressed
            
            # Calculate daily rewards
            daily_rate = base_apy / 365
            daily_rewards = int(total_staked * daily_rate)
            
            # Apply lock period multipliers
            stakers = staking_data.get("stakers", [])
            distributions = []
            
            for staker in stakers:
                stake_amount = staker.get("amount", 0)
                lock_days = staker.get("lock_days", 7)
                
                # Multiplier based on lock period
                if lock_days >= 180:
                    multiplier = 1.5
                elif lock_days >= 90:
                    multiplier = 1.25
                elif lock_days >= 30:
                    multiplier = 1.1
                else:
                    multiplier = 1.0
                
                reward = int(stake_amount * daily_rate * multiplier)
                distributions.append({
                    "address": staker.get("address"),
                    "amount": reward,
                    "stake_amount": stake_amount,
                    "lock_days": lock_days,
                    "multiplier": multiplier,
                })
            
            decision = {
                "type": "staking_rewards",
                "total_amount": sum(d["amount"] for d in distributions),
                "distributions": distributions,
                "apy": base_apy,
                "reason": f"Daily rewards for {len(stakers)} stakers",
                "confidence": 0.95,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            logger.info("Staking rewards calculated",
                       total_rewards=decision["total_amount"],
                       stakers=len(stakers),
                       apy=base_apy)
            
            return decision
            
        except Exception as e:
            logger.error("Failed to calculate staking rewards", error=str(e))
            return None
    
    async def evaluate_airdrop_campaign(
        self,
        campaign_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate and approve airdrop campaigns
        
        From ECOSYSTEM_PROGRAMS.md:
        - 25M OMK for airdrops & campaigns (25% of ecosystem)
        - Types: New user welcome, trading competitions, referrals, social engagement
        - Queen verifies budget and approves execution
        
        Returns campaign approval decision
        """
        try:
            campaign_type = campaign_data.get("type")
            total_cost = campaign_data.get("total_cost", 0)
            recipients = campaign_data.get("recipients", [])
            
            # Budget limits per campaign type (from ECOSYSTEM_PROGRAMS.md)
            budget_limits = {
                "new_user_welcome": 5_000_000,    # 5M OMK
                "trading_competition": 8_000_000,  # 8M OMK
                "referral_program": 5_000_000,     # 5M OMK
                "social_engagement": 4_000_000,    # 4M OMK
                "special_events": 3_000_000,       # 3M OMK
            }
            
            limit = budget_limits.get(campaign_type, 1_000_000)
            
            # Check if within budget
            if total_cost > limit:
                logger.warning("Campaign exceeds budget",
                             type=campaign_type,
                             cost=total_cost,
                             limit=limit)
                return None
            
            # Verify recipients are eligible
            # (In production, would check KYC, activity requirements, etc.)
            
            decision = {
                "type": "airdrop_campaign",
                "campaign_type": campaign_type,
                "total_amount": total_cost,
                "recipient_count": len(recipients),
                "recipients": recipients,
                "reason": f"Campaign approved within budget: {total_cost}/{limit}",
                "confidence": 0.90,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            logger.info("Airdrop campaign approved",
                       type=campaign_type,
                       cost=total_cost,
                       recipients=len(recipients))
            
            return decision
            
        except Exception as e:
            logger.error("Failed to evaluate airdrop campaign", error=str(e))
            return None
    
    async def evaluate_bridge_operation(
        self,
        bridge_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate cross-chain bridge operations
        
        From OMKBridge.sol:
        - Rate limiting: 10M OMK/day max
        - Multi-sig validation required
        - Queen can propose changes (admin approves)
        
        Returns bridge operation decision
        """
        try:
            operation = bridge_data.get("operation")  # lock, release, adjust_rate
            amount = bridge_data.get("amount", 0)
            target_chain = bridge_data.get("target_chain", "solana")
            
            # Check rate limits
            daily_limit = 10_000_000 * 10**18  # 10M OMK
            today_bridged = bridge_data.get("today_bridged", 0)
            
            if today_bridged + amount > daily_limit:
                logger.warning("Bridge operation exceeds daily limit",
                             amount=amount,
                             today=today_bridged,
                             limit=daily_limit)
                return None
            
            decision = {
                "type": "bridge_operation",
                "operation": operation,
                "amount": amount,
                "target_chain": target_chain,
                "reason": f"Bridge {operation} within daily limit",
                "confidence": 0.85,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            logger.info("Bridge operation approved",
                       operation=operation,
                       amount=amount,
                       chain=target_chain)
            
            return decision
            
        except Exception as e:
            logger.error("Failed to evaluate bridge operation", error=str(e))
            return None
    
    def _calculate_rebalance_amount(self, pool_data: Dict[str, Any]) -> int:
        """Calculate amount needed to rebalance pool"""
        # Simplified calculation - in production would use AMM math
        current_omk = pool_data.get("omk_amount", 0)
        target_omk = pool_data.get("target_omk_amount", current_omk)
        return abs(target_omk - current_omk)
    
    def _calculate_liquidity_addition(
        self,
        pool_data: Dict[str, Any],
        volume_24h: float
    ) -> int:
        """Calculate amount to add for liquidity"""
        # Rule: Add 2% of 24h volume or min 100K OMK
        volume_based = int(volume_24h * 0.02)
        return max(volume_based, 100_000 * 10**18)
