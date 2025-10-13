"""
TreasuryBee - Treasury management and budget tracking
"""
from typing import Dict, Any, List
import structlog
from datetime import datetime
from app.bees.base import BaseBee

logger = structlog.get_logger(__name__)


class TreasuryBee(BaseBee):
    """
    Specialized bee for treasury operations
    
    Responsibilities:
    - Budget tracking by category
    - Spending proposal validation
    - Treasury health monitoring
    - Fund allocation recommendations
    - Monthly spending reports
    """
    
    # Treasury categories (from TreasuryVault.sol)
    CATEGORIES = {
        0: "DEVELOPMENT",
        1: "MARKETING",
        2: "OPERATIONS",
        3: "INVESTMENTS",
        4: "EMERGENCY",
        5: "GOVERNANCE",
    }
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id, name="TreasuryBee")
        # Monthly limits per category (100M total / 6 categories)
        self.monthly_limits = {
            "DEVELOPMENT": 20_000_000 * 10**18,    # 20M
            "MARKETING": 15_000_000 * 10**18,      # 15M
            "OPERATIONS": 15_000_000 * 10**18,     # 15M
            "INVESTMENTS": 25_000_000 * 10**18,    # 25M
            "EMERGENCY": 15_000_000 * 10**18,      # 15M
            "GOVERNANCE": 10_000_000 * 10**18,     # 10M
        }
        # Track spending (in production, from blockchain)
        self.monthly_spending = {cat: 0 for cat in self.monthly_limits}
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute treasury task"""
        task_type = task_data.get("type")
        
        if task_type == "validate_proposal":
            return await self._validate_proposal(task_data)
        elif task_type == "check_budget":
            return await self._check_budget(task_data)
        elif task_type == "treasury_health":
            return await self._check_treasury_health(task_data)
        elif task_type == "recommend_allocation":
            return await self._recommend_allocation(task_data)
        elif task_type == "generate_report":
            return await self._generate_spending_report(task_data)
        elif task_type == "get_otc_balance":
            return await self._get_otc_balance(task_data)
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    async def _validate_proposal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a treasury spending proposal"""
        try:
            category_id = data.get("category")
            amount = data.get("amount", 0)
            description = data.get("description", "")
            
            # Get category name
            category_name = self.CATEGORIES.get(category_id, "UNKNOWN")
            
            if category_name == "UNKNOWN":
                return {
                    "success": False,
                    "valid": False,
                    "reason": f"Invalid category: {category_id}"
                }
            
            # Check monthly limit
            limit = self.monthly_limits.get(category_name, 0)
            current_spending = self.monthly_spending.get(category_name, 0)
            remaining = limit - current_spending
            
            would_exceed = (current_spending + amount) > limit
            
            # Validation rules
            validation_issues = []
            
            if amount <= 0:
                validation_issues.append("Amount must be positive")
            
            if would_exceed:
                validation_issues.append(
                    f"Would exceed monthly limit ({remaining / 10**18:.0f} OMK remaining)"
                )
            
            if not description or len(description) < 10:
                validation_issues.append("Description too short (min 10 chars)")
            
            # Emergency category requires special justification
            if category_name == "EMERGENCY" and "emergency" not in description.lower():
                validation_issues.append("Emergency category requires emergency justification")
            
            valid = len(validation_issues) == 0
            
            return {
                "success": True,
                "valid": valid,
                "category": category_name,
                "amount": amount,
                "monthly_limit": limit,
                "current_spending": current_spending,
                "remaining_budget": remaining,
                "utilization_percent": (current_spending / limit * 100) if limit > 0 else 0,
                "validation_issues": validation_issues,
                "recommendation": "approve" if valid else "reject",
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _check_budget(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check budget status for a category"""
        try:
            category_name = data.get("category", "DEVELOPMENT")
            
            if category_name not in self.monthly_limits:
                return {
                    "success": False,
                    "error": f"Unknown category: {category_name}"
                }
            
            limit = self.monthly_limits[category_name]
            spent = self.monthly_spending[category_name]
            remaining = limit - spent
            utilization = (spent / limit * 100) if limit > 0 else 0
            
            # Determine status
            if utilization >= 90:
                status = "critical"
            elif utilization >= 70:
                status = "warning"
            else:
                status = "healthy"
            
            return {
                "success": True,
                "category": category_name,
                "monthly_limit": limit,
                "spent": spent,
                "remaining": remaining,
                "utilization_percent": round(utilization, 2),
                "status": status,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _check_treasury_health(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check overall treasury health"""
        try:
            total_balance = data.get("total_balance", 100_000_000 * 10**18)
            burn_rate = data.get("burn_rate", 1_000_000 * 10**18)  # per month
            
            # Calculate runway (months of operation)
            runway_months = total_balance / burn_rate if burn_rate > 0 else float('inf')
            
            # Calculate total spending vs limits
            total_limit = sum(self.monthly_limits.values())
            total_spent = sum(self.monthly_spending.values())
            overall_utilization = (total_spent / total_limit * 100) if total_limit > 0 else 0
            
            # Health score (0-100)
            health_score = 100
            
            # Deduct for low runway
            if runway_months < 6:
                health_score -= 30
            elif runway_months < 12:
                health_score -= 15
            
            # Deduct for high utilization
            if overall_utilization > 80:
                health_score -= 20
            elif overall_utilization > 60:
                health_score -= 10
            
            # Determine health status
            if health_score >= 80:
                health_status = "excellent"
            elif health_score >= 60:
                health_status = "good"
            elif health_score >= 40:
                health_status = "fair"
            else:
                health_status = "poor"
            
            return {
                "success": True,
                "health_score": max(0, health_score),
                "health_status": health_status,
                "total_balance": total_balance,
                "burn_rate_monthly": burn_rate,
                "runway_months": round(runway_months, 1),
                "overall_utilization": round(overall_utilization, 2),
                "recommendations": self._get_health_recommendations(health_score, runway_months),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_health_recommendations(self, health_score: int, runway_months: float) -> List[str]:
        """Generate health recommendations"""
        recommendations = []
        
        if health_score < 60:
            recommendations.append("Consider reducing monthly spending")
        
        if runway_months < 12:
            recommendations.append("Low runway - prioritize revenue generation")
        
        if runway_months < 6:
            recommendations.append("URGENT: Treasury approaching critical levels")
        
        return recommendations if recommendations else ["Treasury health is good"]
    
    async def _recommend_allocation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend budget allocation based on priorities"""
        try:
            available_funds = data.get("available_funds", 100_000_000 * 10**18)
            priorities = data.get("priorities", ["DEVELOPMENT", "MARKETING"])
            
            # Allocate based on priorities and limits
            allocations = {}
            remaining = available_funds
            
            # First pass: allocate to priorities
            for priority in priorities:
                if priority in self.monthly_limits and remaining > 0:
                    limit = self.monthly_limits[priority]
                    allocation = min(limit, remaining)
                    allocations[priority] = allocation
                    remaining -= allocation
            
            # Second pass: distribute remaining to other categories
            other_categories = [cat for cat in self.monthly_limits if cat not in priorities]
            if remaining > 0 and other_categories:
                per_category = remaining // len(other_categories)
                for category in other_categories:
                    allocations[category] = per_category
                    remaining -= per_category
            
            return {
                "success": True,
                "total_allocated": available_funds - remaining,
                "remaining": remaining,
                "allocations": allocations,
                "allocation_percent": {
                    cat: round((amt / available_funds * 100), 2) 
                    for cat, amt in allocations.items()
                },
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_spending_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate monthly spending report"""
        try:
            # Aggregate all category spending
            category_reports = {}
            total_spent = 0
            total_limit = 0
            
            for category, limit in self.monthly_limits.items():
                spent = self.monthly_spending.get(category, 0)
                total_spent += spent
                total_limit += limit
                
                category_reports[category] = {
                    "spent": spent,
                    "limit": limit,
                    "remaining": limit - spent,
                    "utilization": round((spent / limit * 100), 2) if limit > 0 else 0,
                }
            
            return {
                "success": True,
                "report_date": datetime.utcnow().isoformat(),
                "total_spent": total_spent,
                "total_limit": total_limit,
                "overall_utilization": round((total_spent / total_limit * 100), 2) if total_limit > 0 else 0,
                "categories": category_reports,
                "top_spending_category": max(
                    category_reports.items(),
                    key=lambda x: x[1]["spent"]
                )[0] if category_reports else None,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_otc_balance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get OTC treasury balance
        Used by MarketDataAgent for OTC supply calculations
        """
        try:
            # In production, this would query blockchain
            # For now, return initial OTC allocation
            # Total supply = 1B, OTC allocation = 50% = 500M OMK
            otc_treasury_balance = 500000000  # 500M OMK
            
            logger.info("OTC treasury balance queried", balance=otc_treasury_balance)
            
            return {
                "success": True,
                "balance": otc_treasury_balance,
                "total_supply": 1000000000,  # 1B OMK
                "otc_percentage": 50.0,
                "note": "This is initial allocation. In production, query blockchain."
            }
        except Exception as e:
            logger.error("Failed to get OTC balance", error=str(e))
            return {"success": False, "error": str(e)}
