"""
Liquidity Sentinel Bee - Price Control Department

Off-chain orchestrator using AI to monitor price movements and LP ratios.
Predicts volatility and calls for top-ups or buybacks.
Integrates Pattern Recognition Bee's models for predictive market balancing.
"""
from typing import Dict, Any, List
import structlog
from app.bees.base import BaseBee

logger = structlog.get_logger(__name__)


class LiquiditySentinelBee(BaseBee):
    """
    Specialized bee for liquidity monitoring and price control
    
    Responsibilities:
    - Monitor price movements across all pools
    - Track LP ratios and pool health
    - Predict volatility using AI models
    - Call for liquidity top-ups or buybacks
    - Coordinate with Pattern Recognition Bee
    - Alert Queen of critical price events
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id, name="LiquiditySentinelBee")
        # Monitoring thresholds
        self.price_deviation_threshold = 0.05  # 5%
        self.volatility_high_threshold = 0.15  # 15%
        self.pool_health_critical = 30  # Below 30 is critical
        self.pool_health_warning = 50   # Below 50 is warning
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sentinel task"""
        task_type = task_data.get("type")
        
        if task_type == "monitor_price":
            return await self._monitor_price(task_data)
        elif task_type == "check_pool_health":
            return await self._check_pool_health(task_data)
        elif task_type == "predict_volatility":
            return await self._predict_volatility(task_data)
        elif task_type == "recommend_action":
            return await self._recommend_action(task_data)
        elif task_type == "calculate_buyback":
            return await self._calculate_buyback(task_data)
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    async def _monitor_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor price movements"""
        try:
            current_price = data.get("current_price")
            expected_price = data.get("expected_price")
            pool_address = data.get("pool_address")
            
            # Calculate deviation
            deviation = abs((current_price - expected_price) / expected_price)
            deviation_percent = deviation * 100
            
            # Determine severity
            if deviation > self.price_deviation_threshold * 2:  # >10%
                severity = "critical"
                action_needed = True
            elif deviation > self.price_deviation_threshold:  # >5%
                severity = "warning"
                action_needed = True
            else:
                severity = "normal"
                action_needed = False
            
            # Generate alert if needed
            alert = None
            if action_needed:
                alert = {
                    "type": "price_deviation",
                    "severity": severity,
                    "message": f"Price deviation of {deviation_percent:.2f}% detected",
                    "recommended_action": "add_liquidity" if current_price > expected_price else "remove_liquidity",
                }
            
            return {
                "success": True,
                "current_price": current_price,
                "expected_price": expected_price,
                "deviation_percent": round(deviation_percent, 2),
                "severity": severity,
                "action_needed": action_needed,
                "alert": alert,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _check_pool_health(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check liquidity pool health"""
        try:
            token_a_amount = data.get("token_a_amount")
            token_b_amount = data.get("token_b_amount")
            target_ratio = data.get("target_ratio", 1.0)
            volume_24h = data.get("volume_24h", 0)
            
            # Calculate current ratio
            current_ratio = token_a_amount / token_b_amount if token_b_amount > 0 else 0
            ratio_deviation = abs(current_ratio - target_ratio) / target_ratio
            
            # Calculate liquidity depth score (0-100)
            total_liquidity = token_a_amount + token_b_amount
            depth_score = min(100, (total_liquidity / 1_000_000) * 10)  # 10M = 100 score
            
            # Calculate volume/liquidity ratio
            vol_liq_ratio = volume_24h / total_liquidity if total_liquidity > 0 else 0
            
            # Calculate overall health score
            health_score = 100
            
            # Penalize for ratio deviation
            health_score -= min(30, ratio_deviation * 100)
            
            # Penalize for low liquidity
            if depth_score < 50:
                health_score -= (50 - depth_score) * 0.5
            
            # Penalize for high volume/liquidity (slippage risk)
            if vol_liq_ratio > 0.5:
                health_score -= min(20, (vol_liq_ratio - 0.5) * 40)
            
            health_score = max(0, health_score)
            
            # Determine status
            if health_score < self.pool_health_critical:
                status = "critical"
            elif health_score < self.pool_health_warning:
                status = "warning"
            else:
                status = "healthy"
            
            # Generate recommendations
            recommendations = []
            if ratio_deviation > 0.1:
                recommendations.append("Rebalance pool to target ratio")
            if depth_score < 50:
                recommendations.append("Add more liquidity to improve depth")
            if vol_liq_ratio > 0.5:
                recommendations.append("High volume/liquidity ratio - monitor for slippage")
            
            return {
                "success": True,
                "health_score": round(health_score, 2),
                "status": status,
                "current_ratio": round(current_ratio, 4),
                "target_ratio": target_ratio,
                "ratio_deviation_percent": round(ratio_deviation * 100, 2),
                "depth_score": round(depth_score, 2),
                "volume_liquidity_ratio": round(vol_liq_ratio, 4),
                "recommendations": recommendations,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _predict_volatility(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict future volatility"""
        try:
            price_history = data.get("price_history", [])
            volume_history = data.get("volume_history", [])
            
            if len(price_history) < 10:
                return {
                    "success": False,
                    "error": "Insufficient price history for volatility prediction"
                }
            
            # Calculate historical volatility
            returns = []
            for i in range(1, len(price_history)):
                ret = (price_history[i] - price_history[i-1]) / price_history[i-1]
                returns.append(ret)
            
            # Calculate standard deviation of returns
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            volatility = variance ** 0.5
            
            # Annualized volatility (assuming daily data)
            annualized_volatility = volatility * (365 ** 0.5)
            
            # Predict future volatility (simplified - in production use ML)
            # Use recent trend
            recent_volatility = (sum(abs(r) for r in returns[-5:]) / 5) * (365 ** 0.5)
            predicted_volatility = (annualized_volatility * 0.7) + (recent_volatility * 0.3)
            
            # Classify volatility level
            if predicted_volatility > self.volatility_high_threshold:
                level = "high"
                risk_score = min(100, predicted_volatility / self.volatility_high_threshold * 60)
            elif predicted_volatility > self.volatility_high_threshold / 2:
                level = "moderate"
                risk_score = 40
            else:
                level = "low"
                risk_score = 20
            
            # Generate recommendations
            recommendations = []
            if level == "high":
                recommendations.append("Increase liquidity buffer")
                recommendations.append("Tighten price monitoring")
                recommendations.append("Consider hedging strategies")
            elif level == "moderate":
                recommendations.append("Monitor closely for changes")
            
            return {
                "success": True,
                "predicted_volatility": round(predicted_volatility, 4),
                "current_volatility": round(annualized_volatility, 4),
                "volatility_level": level,
                "risk_score": round(risk_score, 2),
                "recommendations": recommendations,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _recommend_action(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend liquidity action based on analysis"""
        try:
            pool_health = data.get("pool_health", {})
            price_analysis = data.get("price_analysis", {})
            volatility_prediction = data.get("volatility_prediction", {})
            
            health_score = pool_health.get("health_score", 100)
            price_deviation = price_analysis.get("deviation_percent", 0)
            volatility_level = volatility_prediction.get("volatility_level", "low")
            
            actions = []
            priority = "normal"
            
            # Critical health - immediate action
            if health_score < self.pool_health_critical:
                actions.append({
                    "action": "add_liquidity",
                    "amount": "5M OMK (critical)",
                    "reason": "Pool health critical",
                    "urgency": "immediate",
                })
                priority = "critical"
            
            # High price deviation
            elif price_deviation > 10:
                actions.append({
                    "action": "rebalance_pool",
                    "amount": "2M OMK",
                    "reason": f"Price deviation {price_deviation}%",
                    "urgency": "high",
                })
                priority = "high"
            
            # High volatility predicted
            elif volatility_level == "high":
                actions.append({
                    "action": "increase_buffer",
                    "amount": "3M OMK",
                    "reason": "High volatility predicted",
                    "urgency": "medium",
                })
                priority = "medium"
            
            # Moderate health - preventive action
            elif health_score < self.pool_health_warning:
                actions.append({
                    "action": "add_liquidity",
                    "amount": "1M OMK (preventive)",
                    "reason": "Pool health below optimal",
                    "urgency": "low",
                })
                priority = "low"
            
            # All good
            else:
                actions.append({
                    "action": "monitor",
                    "amount": "0",
                    "reason": "Pool healthy",
                    "urgency": "none",
                })
            
            return {
                "success": True,
                "recommended_actions": actions,
                "priority": priority,
                "health_score": health_score,
                "requires_queen_approval": priority in ["critical", "high"],
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _calculate_buyback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal buyback amount"""
        try:
            current_price = data.get("current_price")
            target_price = data.get("target_price")
            pool_liquidity = data.get("pool_liquidity")
            treasury_balance = data.get("treasury_balance")
            
            # Calculate price gap
            price_gap = (target_price - current_price) / current_price
            
            if price_gap <= 0:
                return {
                    "success": True,
                    "buyback_needed": False,
                    "reason": "Price at or above target",
                }
            
            # Estimate buyback amount needed
            # Simplified formula (in production, use AMM math)
            estimated_buyback = pool_liquidity * price_gap * 0.5
            
            # Cap at 5% of treasury
            max_buyback = treasury_balance * 0.05
            recommended_buyback = min(estimated_buyback, max_buyback)
            
            # Calculate expected price impact
            price_impact = (recommended_buyback / pool_liquidity) * 100
            
            return {
                "success": True,
                "buyback_needed": True,
                "recommended_amount": recommended_buyback,
                "max_amount": max_buyback,
                "estimated_price_impact": round(price_impact, 2),
                "current_price": current_price,
                "target_price": target_price,
                "price_gap_percent": round(price_gap * 100, 2),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
