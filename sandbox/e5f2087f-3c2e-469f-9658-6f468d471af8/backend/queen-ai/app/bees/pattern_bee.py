"""
PatternBee - Pattern recognition and trend analysis
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import structlog
from app.bees.base import BaseBee

logger = structlog.get_logger(__name__)


class PatternBee(BaseBee):
    """
    Specialized bee for pattern recognition
    
    Responsibilities:
    - Trend detection (price, volume, liquidity)
    - Anomaly detection
    - Seasonal pattern recognition
    - Historical pattern matching
    - Predictive analytics
    - Market cycle identification
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id, name="PatternBee")
        # Pattern database (in production, from ML models/database)
        self.known_patterns = {}
        self.anomaly_threshold = 2.5  # Standard deviations
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pattern task"""
        task_type = task_data.get("type")
        
        if task_type == "detect_trend":
            return await self._detect_trend(task_data)
        elif task_type == "detect_anomaly":
            return await self._detect_anomaly(task_data)
        elif task_type == "match_pattern":
            return await self._match_pattern(task_data)
        elif task_type == "predict_next":
            return await self._predict_next(task_data)
        elif task_type == "identify_cycle":
            return await self._identify_cycle(task_data)
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    async def _detect_trend(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect trend in time series data"""
        try:
            values = data.get("values", [])
            metric_name = data.get("metric", "unknown")
            
            if len(values) < 3:
                return {
                    "success": False,
                    "error": "Not enough data points (minimum 3)"
                }
            
            # Calculate trend
            increases = 0
            decreases = 0
            
            for i in range(1, len(values)):
                if values[i] > values[i-1]:
                    increases += 1
                elif values[i] < values[i-1]:
                    decreases += 1
            
            total_comparisons = len(values) - 1
            increase_rate = increases / total_comparisons
            
            # Determine trend
            if increase_rate >= 0.7:
                trend = "strong_up"
            elif increase_rate >= 0.55:
                trend = "up"
            elif increase_rate <= 0.3:
                trend = "strong_down"
            elif increase_rate <= 0.45:
                trend = "down"
            else:
                trend = "stable"
            
            # Calculate trend strength
            trend_strength = abs(increase_rate - 0.5) * 200  # 0-100
            
            # Calculate rate of change
            first_value = values[0]
            last_value = values[-1]
            rate_of_change = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
            
            return {
                "success": True,
                "metric": metric_name,
                "trend": trend,
                "trend_strength": round(trend_strength, 2),
                "rate_of_change_percent": round(rate_of_change, 2),
                "data_points": len(values),
                "first_value": first_value,
                "last_value": last_value,
                "confidence": "high" if trend_strength > 60 else "medium" if trend_strength > 30 else "low",
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _detect_anomaly(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in data"""
        try:
            values = data.get("values", [])
            current_value = data.get("current_value")
            metric_name = data.get("metric", "unknown")
            
            if len(values) < 5:
                return {
                    "success": False,
                    "error": "Not enough historical data (minimum 5)"
                }
            
            # Calculate mean and standard deviation
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            
            # Check if current value is anomalous
            if std_dev > 0:
                z_score = abs((current_value - mean) / std_dev)
                is_anomaly = z_score > self.anomaly_threshold
            else:
                z_score = 0
                is_anomaly = False
            
            # Determine severity
            if z_score > 3.5:
                severity = "critical"
            elif z_score > 2.5:
                severity = "high"
            elif z_score > 1.5:
                severity = "medium"
            else:
                severity = "low"
            
            return {
                "success": True,
                "metric": metric_name,
                "is_anomaly": is_anomaly,
                "severity": severity,
                "current_value": current_value,
                "mean": round(mean, 2),
                "std_dev": round(std_dev, 2),
                "z_score": round(z_score, 2),
                "threshold": self.anomaly_threshold,
                "deviation_percent": round(((current_value - mean) / mean * 100), 2) if mean != 0 else 0,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _match_pattern(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Match current pattern against known patterns"""
        try:
            current_pattern = data.get("pattern", [])
            pattern_type = data.get("pattern_type", "price")
            
            if len(current_pattern) < 5:
                return {
                    "success": False,
                    "error": "Not enough data for pattern matching"
                }
            
            # Known patterns (simplified)
            known_patterns = {
                "bull_flag": {
                    "description": "Bullish continuation pattern",
                    "signal": "buy",
                    "confidence": 0.7,
                },
                "bear_flag": {
                    "description": "Bearish continuation pattern",
                    "signal": "sell",
                    "confidence": 0.7,
                },
                "double_bottom": {
                    "description": "Bullish reversal pattern",
                    "signal": "buy",
                    "confidence": 0.8,
                },
                "double_top": {
                    "description": "Bearish reversal pattern",
                    "signal": "sell",
                    "confidence": 0.8,
                },
            }
            
            # Simplified pattern matching (in production, would use ML)
            # For now, return a mock match based on trend
            trend_result = await self._detect_trend({"values": current_pattern})
            
            if trend_result.get("trend") in ["strong_up", "up"]:
                matched_pattern = "bull_flag"
            elif trend_result.get("trend") in ["strong_down", "down"]:
                matched_pattern = "bear_flag"
            else:
                matched_pattern = None
            
            if matched_pattern:
                pattern_info = known_patterns[matched_pattern]
                return {
                    "success": True,
                    "matched_pattern": matched_pattern,
                    "description": pattern_info["description"],
                    "signal": pattern_info["signal"],
                    "confidence": pattern_info["confidence"],
                    "trend": trend_result.get("trend"),
                }
            else:
                return {
                    "success": True,
                    "matched_pattern": None,
                    "signal": "hold",
                    "confidence": 0.0,
                    "message": "No clear pattern detected",
                }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _predict_next(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict next value based on pattern"""
        try:
            values = data.get("values", [])
            metric_name = data.get("metric", "unknown")
            
            if len(values) < 3:
                return {
                    "success": False,
                    "error": "Not enough data for prediction"
                }
            
            # Simple moving average prediction
            window_size = min(5, len(values))
            recent_values = values[-window_size:]
            prediction = sum(recent_values) / len(recent_values)
            
            # Get trend
            trend_result = await self._detect_trend({"values": values})
            trend = trend_result.get("trend", "stable")
            
            # Adjust prediction based on trend
            if trend == "strong_up":
                prediction *= 1.05  # 5% increase
            elif trend == "up":
                prediction *= 1.02  # 2% increase
            elif trend == "strong_down":
                prediction *= 0.95  # 5% decrease
            elif trend == "down":
                prediction *= 0.98  # 2% decrease
            
            # Calculate confidence
            variance = sum((x - prediction) ** 2 for x in recent_values) / len(recent_values)
            std_dev = variance ** 0.5
            
            # Lower std_dev = higher confidence
            if std_dev < prediction * 0.05:  # < 5% variance
                confidence = "high"
            elif std_dev < prediction * 0.15:  # < 15% variance
                confidence = "medium"
            else:
                confidence = "low"
            
            return {
                "success": True,
                "metric": metric_name,
                "predicted_value": round(prediction, 2),
                "trend": trend,
                "confidence": confidence,
                "std_dev": round(std_dev, 2),
                "current_value": values[-1],
                "change_from_current": round(((prediction - values[-1]) / values[-1] * 100), 2) if values[-1] != 0 else 0,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _identify_cycle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify market cycle phase"""
        try:
            price_data = data.get("price_history", [])
            volume_data = data.get("volume_history", [])
            
            if len(price_data) < 10:
                return {
                    "success": False,
                    "error": "Not enough data for cycle identification"
                }
            
            # Get trend
            price_trend = await self._detect_trend({"values": price_data})
            
            # Simplified cycle identification
            trend = price_trend.get("trend")
            rate_of_change = price_trend.get("rate_of_change_percent", 0)
            
            # Identify phase
            if trend in ["strong_up"] and rate_of_change > 20:
                phase = "euphoria"
            elif trend in ["up"] and rate_of_change > 5:
                phase = "accumulation"
            elif trend in ["strong_down"] and rate_of_change < -20:
                phase = "panic"
            elif trend in ["down"] and rate_of_change < -5:
                phase = "distribution"
            else:
                phase = "consolidation"
            
            # Recommendation based on phase
            recommendations = {
                "euphoria": "Consider taking profits, market may be overheated",
                "accumulation": "Good time for long-term positions",
                "panic": "Opportunity for value buyers, but risky",
                "distribution": "Be cautious, trend may reverse",
                "consolidation": "Wait for clearer signals",
            }
            
            return {
                "success": True,
                "cycle_phase": phase,
                "price_trend": trend,
                "rate_of_change": rate_of_change,
                "recommendation": recommendations.get(phase, "Monitor closely"),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
