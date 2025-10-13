"""
SecurityBee - Security validation and risk assessment
"""
from typing import Dict, Any
import structlog
from app.bees.base import BaseBee

logger = structlog.get_logger(__name__)


class SecurityBee(BaseBee):
    """
    Specialized bee for security operations
    
    Responsibilities:
    - Address validation
    - Transaction risk assessment
    - Signature verification
    - Blacklist checking
    - Rate limit validation
    - Anomaly detection
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id, name="SecurityBee")
        # Known blacklisted addresses (in production, from database)
        self.blacklist = set()
        # Suspicious patterns
        self.suspicious_patterns = []
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute security task"""
        task_type = task_data.get("type")
        
        if task_type == "validate_address":
            return await self._validate_address(task_data)
        elif task_type == "assess_risk":
            return await self._assess_risk(task_data)
        elif task_type == "check_rate_limit":
            return await self._check_rate_limit(task_data)
        elif task_type == "validate_transaction":
            return await self._validate_transaction(task_data)
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    async def _validate_address(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Ethereum address"""
        try:
            address = data.get("address", "")
            
            # Check if address is valid format
            if not address or not address.startswith("0x"):
                return {
                    "success": False,
                    "valid": False,
                    "reason": "Invalid address format"
                }
            
            # Check length (42 chars for 0x + 40 hex)
            if len(address) != 42:
                return {
                    "success": False,
                    "valid": False,
                    "reason": "Invalid address length"
                }
            
            # Check if blacklisted
            if address.lower() in self.blacklist:
                return {
                    "success": True,
                    "valid": False,
                    "reason": "Address is blacklisted",
                    "severity": "high"
                }
            
            return {
                "success": True,
                "valid": True,
                "address": address,
                "risk_level": "low"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _assess_risk(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk of an operation"""
        try:
            operation_type = data.get("operation_type")
            amount = data.get("amount", 0)
            target = data.get("target")
            
            risk_score = 0
            risk_factors = []
            
            # Check amount (large amounts = higher risk)
            if amount > 10_000_000 * 10**18:  # >10M tokens
                risk_score += 30
                risk_factors.append("Large amount (>10M tokens)")
            elif amount > 5_000_000 * 10**18:  # >5M tokens
                risk_score += 15
                risk_factors.append("Medium amount (>5M tokens)")
            
            # Check operation type
            high_risk_ops = ["bridge_transfer", "emergency_withdraw"]
            if operation_type in high_risk_ops:
                risk_score += 25
                risk_factors.append(f"High-risk operation: {operation_type}")
            
            # Check target (if provided)
            if target and target.lower() in self.blacklist:
                risk_score += 50
                risk_factors.append("Target address is blacklisted")
            
            # Determine risk level
            if risk_score >= 50:
                risk_level = "high"
                recommendation = "reject"
            elif risk_score >= 25:
                risk_level = "medium"
                recommendation = "review"
            else:
                risk_level = "low"
                recommendation = "approve"
            
            return {
                "success": True,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "recommendation": recommendation,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _check_rate_limit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if operation exceeds rate limits"""
        try:
            daily_limit = data.get("daily_limit", 50_000_000 * 10**18)
            current_usage = data.get("current_usage", 0)
            requested_amount = data.get("requested_amount", 0)
            
            remaining = daily_limit - current_usage
            would_exceed = (current_usage + requested_amount) > daily_limit
            
            utilization = (current_usage / daily_limit) * 100
            
            # Determine status
            if would_exceed:
                status = "exceeded"
                approved = False
            elif utilization > 80:
                status = "warning"
                approved = True
            else:
                status = "ok"
                approved = True
            
            return {
                "success": True,
                "approved": approved,
                "status": status,
                "daily_limit": daily_limit,
                "current_usage": current_usage,
                "remaining": remaining,
                "utilization_percent": round(utilization, 2),
                "would_exceed": would_exceed,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _validate_transaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive transaction validation"""
        try:
            # Validate address
            address_check = await self._validate_address({
                "address": data.get("to_address")
            })
            
            if not address_check.get("valid", False):
                return {
                    "success": True,
                    "valid": False,
                    "reason": address_check.get("reason", "Invalid address")
                }
            
            # Assess risk
            risk_check = await self._assess_risk({
                "operation_type": data.get("operation_type"),
                "amount": data.get("amount"),
                "target": data.get("to_address"),
            })
            
            # Check rate limits
            rate_check = await self._check_rate_limit({
                "daily_limit": data.get("daily_limit"),
                "current_usage": data.get("current_usage"),
                "requested_amount": data.get("amount"),
            })
            
            # Overall decision
            valid = (
                address_check.get("valid", False) and
                rate_check.get("approved", False) and
                risk_check.get("recommendation") != "reject"
            )
            
            return {
                "success": True,
                "valid": valid,
                "address_check": address_check,
                "risk_assessment": risk_check,
                "rate_limit_check": rate_check,
                "recommendation": risk_check.get("recommendation"),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
