"""
LogicBee - Decision making and consensus building
"""
from typing import Dict, Any, List
import structlog
from app.bees.base import BaseBee

logger = structlog.get_logger(__name__)


class LogicBee(BaseBee):
    """
    Specialized bee for decision making
    
    Responsibilities:
    - Aggregate inputs from multiple bees
    - Build consensus on decisions
    - Apply decision rules and policies
    - Risk-reward analysis
    - Multi-criteria decision making
    - Conflict resolution between bees
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id, name="LogicBee")
        # Decision policies
        self.policies = {
            "min_consensus_score": 70,  # 70% consensus required
            "max_risk_score": 60,        # Maximum acceptable risk
            "min_benefit_score": 40,     # Minimum benefit required
        }
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute logic task"""
        task_type = task_data.get("type")
        
        if task_type == "make_decision":
            return await self._make_decision(task_data)
        elif task_type == "build_consensus":
            return await self._build_consensus(task_data)
        elif task_type == "resolve_conflict":
            return await self._resolve_conflict(task_data)
        elif task_type == "analyze_tradeoffs":
            return await self._analyze_tradeoffs(task_data)
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    async def _make_decision(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a decision based on multiple inputs"""
        try:
            decision_type = data.get("decision_type")
            inputs = data.get("inputs", {})
            
            # Extract key factors
            maths_input = inputs.get("maths", {})
            security_input = inputs.get("security", {})
            data_input = inputs.get("data", {})
            treasury_input = inputs.get("treasury", {})
            pattern_input = inputs.get("pattern", {})
            
            # Calculate decision score
            score = 0
            max_score = 0
            factors = []
            
            # Maths analysis (weight: 25%)
            if maths_input:
                math_score = self._score_maths_input(maths_input)
                score += math_score * 0.25
                max_score += 100 * 0.25
                factors.append(f"Maths: {math_score}/100")
            
            # Security analysis (weight: 30%)
            if security_input:
                security_score = self._score_security_input(security_input)
                score += security_score * 0.30
                max_score += 100 * 0.30
                factors.append(f"Security: {security_score}/100")
            
            # Data analysis (weight: 15%)
            if data_input:
                data_score = self._score_data_input(data_input)
                score += data_score * 0.15
                max_score += 100 * 0.15
                factors.append(f"Data: {data_score}/100")
            
            # Treasury health (weight: 20%)
            if treasury_input:
                treasury_score = self._score_treasury_input(treasury_input)
                score += treasury_score * 0.20
                max_score += 100 * 0.20
                factors.append(f"Treasury: {treasury_score}/100")
            
            # Pattern analysis (weight: 10%)
            if pattern_input:
                pattern_score = self._score_pattern_input(pattern_input)
                score += pattern_score * 0.10
                max_score += 100 * 0.10
                factors.append(f"Pattern: {pattern_score}/100")
            
            # Normalize score
            final_score = (score / max_score * 100) if max_score > 0 else 0
            
            # Make decision
            if final_score >= self.policies["min_consensus_score"]:
                decision = "approve"
                confidence = "high" if final_score >= 85 else "medium"
            elif final_score >= 50:
                decision = "review"
                confidence = "low"
            else:
                decision = "reject"
                confidence = "high"
            
            return {
                "success": True,
                "decision": decision,
                "confidence": confidence,
                "score": round(final_score, 2),
                "factors": factors,
                "reasoning": self._generate_reasoning(decision, final_score, factors),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _build_consensus(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build consensus from multiple bee inputs"""
        try:
            bee_votes = data.get("votes", [])
            
            # Count votes
            vote_counts = {"approve": 0, "reject": 0, "abstain": 0}
            total_weight = 0
            
            for vote in bee_votes:
                bee_name = vote.get("bee")
                vote_value = vote.get("vote")
                weight = vote.get("weight", 1.0)
                
                if vote_value in vote_counts:
                    vote_counts[vote_value] += weight
                total_weight += weight
            
            # Calculate consensus
            if total_weight == 0:
                return {
                    "success": False,
                    "error": "No votes received"
                }
            
            approve_percent = (vote_counts["approve"] / total_weight) * 100
            reject_percent = (vote_counts["reject"] / total_weight) * 100
            
            # Determine consensus
            if approve_percent >= self.policies["min_consensus_score"]:
                consensus = "approve"
                strength = "strong"
            elif reject_percent >= self.policies["min_consensus_score"]:
                consensus = "reject"
                strength = "strong"
            elif approve_percent > reject_percent:
                consensus = "approve"
                strength = "weak"
            else:
                consensus = "reject"
                strength = "weak"
            
            return {
                "success": True,
                "consensus": consensus,
                "strength": strength,
                "approve_percent": round(approve_percent, 2),
                "reject_percent": round(reject_percent, 2),
                "abstain_percent": round((vote_counts["abstain"] / total_weight) * 100, 2),
                "total_votes": len(bee_votes),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _resolve_conflict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflicts between bee recommendations"""
        try:
            conflicts = data.get("conflicts", [])
            
            # Prioritize by bee expertise
            bee_priorities = {
                "security": 10,      # Highest priority
                "treasury": 8,
                "maths": 7,
                "blockchain": 6,
                "pattern": 5,
                "data": 4,
                "monitoring": 9,     # High for health issues
            }
            
            resolution = None
            highest_priority = -1
            
            for conflict in conflicts:
                bee_name = conflict.get("bee")
                recommendation = conflict.get("recommendation")
                priority = bee_priorities.get(bee_name, 0)
                
                if priority > highest_priority:
                    highest_priority = priority
                    resolution = {
                        "bee": bee_name,
                        "recommendation": recommendation,
                        "priority": priority,
                    }
            
            return {
                "success": True,
                "resolution": resolution,
                "reasoning": f"{resolution['bee']} has highest priority for this decision",
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _analyze_tradeoffs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risk-reward tradeoffs"""
        try:
            options = data.get("options", [])
            
            analyzed_options = []
            
            for option in options:
                name = option.get("name")
                risk = option.get("risk", 50)        # 0-100
                reward = option.get("reward", 50)    # 0-100
                cost = option.get("cost", 0)
                
                # Calculate risk-reward ratio
                if risk > 0:
                    ratio = reward / risk
                else:
                    ratio = float('inf') if reward > 0 else 0
                
                # Calculate net benefit
                net_benefit = reward - risk - (cost / 1000000)  # Normalize cost
                
                analyzed_options.append({
                    "name": name,
                    "risk": risk,
                    "reward": reward,
                    "cost": cost,
                    "risk_reward_ratio": round(ratio, 2),
                    "net_benefit": round(net_benefit, 2),
                    "recommended": net_benefit > 0 and risk < self.policies["max_risk_score"],
                })
            
            # Sort by net benefit
            analyzed_options.sort(key=lambda x: x["net_benefit"], reverse=True)
            
            return {
                "success": True,
                "options": analyzed_options,
                "best_option": analyzed_options[0] if analyzed_options else None,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _score_maths_input(self, maths_input: Dict[str, Any]) -> float:
        """Score mathematical analysis (0-100)"""
        score = 50  # Base score
        
        # Reward good pool health
        if "pool_health" in maths_input:
            health = maths_input["pool_health"]
            score += (health - 50) * 0.5  # +/- 25 points
        
        # Reward low slippage
        if "slippage" in maths_input:
            slippage = maths_input["slippage"]
            score += max(0, (5 - slippage) * 5)  # Up to +25 for low slippage
        
        return max(0, min(100, score))
    
    def _score_security_input(self, security_input: Dict[str, Any]) -> float:
        """Score security analysis (0-100)"""
        score = 100  # Start high
        
        # Penalize high risk
        if "risk_level" in security_input:
            risk_map = {"low": 0, "medium": -20, "high": -50, "critical": -80}
            score += risk_map.get(security_input["risk_level"], -30)
        
        # Penalize if would exceed limits
        if security_input.get("would_exceed_limits", False):
            score -= 30
        
        return max(0, min(100, score))
    
    def _score_data_input(self, data_input: Dict[str, Any]) -> float:
        """Score data analysis (0-100)"""
        score = 50  # Base score
        
        # Reward good historical performance
        if "success_rate" in data_input:
            rate = data_input["success_rate"]
            score += (rate - 50) * 0.5
        
        return max(0, min(100, score))
    
    def _score_treasury_input(self, treasury_input: Dict[str, Any]) -> float:
        """Score treasury health (0-100)"""
        score = 50  # Base score
        
        # Reward good health
        if "health_score" in treasury_input:
            health = treasury_input["health_score"]
            score += (health - 50) * 0.5
        
        # Penalize low runway
        if "runway_months" in treasury_input:
            runway = treasury_input["runway_months"]
            if runway < 6:
                score -= 30
            elif runway < 12:
                score -= 15
        
        return max(0, min(100, score))
    
    def _score_pattern_input(self, pattern_input: Dict[str, Any]) -> float:
        """Score pattern analysis (0-100)"""
        score = 50  # Base score
        
        # Reward positive trends
        if "trend" in pattern_input:
            trend_map = {"strong_up": 25, "up": 15, "stable": 0, "down": -15, "strong_down": -25}
            score += trend_map.get(pattern_input["trend"], 0)
        
        return max(0, min(100, score))
    
    def _generate_reasoning(self, decision: str, score: float, factors: List[str]) -> str:
        """Generate human-readable reasoning"""
        if decision == "approve":
            return f"Decision APPROVED with score {score:.1f}/100. All factors aligned: {', '.join(factors)}"
        elif decision == "reject":
            return f"Decision REJECTED with score {score:.1f}/100. Insufficient support: {', '.join(factors)}"
        else:
            return f"Decision requires REVIEW with score {score:.1f}/100. Mixed signals: {', '.join(factors)}"
