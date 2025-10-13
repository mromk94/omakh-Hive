"""
Enhanced SecurityBee - Extends SecurityBee with LLM protection capabilities
Coordinates all security gates for prompt injection protection
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.bees.security_bee import SecurityBee
from app.core.security.prompt_protection import PromptProtectionGate
from app.core.security.output_filter import OutputFilter
from app.core.security.context_manager import SecurityContextManager, ThreatLevel
from app.core.security.image_scanner import ImageContentScanner

logger = structlog.get_logger(__name__)


class EnhancedSecurityBee(SecurityBee):
    """
    Enhanced security bee with LLM protection
    
    New responsibilities:
    - Validate LLM inputs for prompt injection
    - Coordinate security gates
    - Detect multi-turn attacks
    - Manage security contexts
    - Quarantine threats
    - Alert admins
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id)
        self.name = "EnhancedSecurityBee"
        
        # Initialize security components
        self.prompt_protection = PromptProtectionGate()
        self.output_filter = OutputFilter()
        self.context_manager = SecurityContextManager()
        self.image_scanner = ImageContentScanner()
        
        # Quarantine storage
        self.quarantined_threats = []
        
        logger.info("EnhancedSecurityBee initialized with LLM protection + Image scanning")
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute security task"""
        task_type = task_data.get("type")
        
        # New LLM protection tasks
        if task_type == "validate_llm_input":
            return await self._validate_llm_input(task_data)
        elif task_type == "filter_llm_output":
            return await self._filter_llm_output(task_data)
        elif task_type == "check_security_context":
            return await self._check_security_context(task_data)
        elif task_type == "validate_code_proposal":
            return await self._validate_code_proposal(task_data)
        elif task_type == "scan_image":
            return await self._scan_image(task_data)
        
        # Fall back to parent SecurityBee for blockchain tasks
        else:
            return await super().execute(task_data)
    
    async def _validate_llm_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input before sending to LLM
        
        This is Gate 1, 2, and 3 combined:
        - Pre-processing
        - Threat detection
        - Decision making
        
        Args:
            data: {
                "input": str,
                "user_id": str,
                "endpoint": str,
                "critical": bool (optional),
                "generates_code": bool (optional),
                "context": dict (optional)
            }
            
        Returns:
            {
                "decision": "ALLOW" | "BLOCK" | "QUARANTINE",
                "risk_score": int,
                "sanitized_input": str,
                "reasoning": str,
                "context_summary": dict
            }
        """
        try:
            input_text = data.get("input", "")
            user_id = data.get("user_id", "unknown")
            endpoint = data.get("endpoint", "unknown")
            is_critical = data.get("critical", False)
            generates_code = data.get("generates_code", False)
            
            # Get or create security context
            context = self.context_manager.get_or_create_context(
                user_id=user_id,
                session_id=data.get("session_id")
            )
            
            # Check if user is blocked
            should_block, block_reason = self.context_manager.should_block_user(context)
            if should_block:
                logger.warning(
                    "Blocked user attempted access",
                    user_id=user_id,
                    reason=block_reason
                )
                return {
                    "decision": "BLOCK",
                    "risk_score": 100,
                    "reasoning": f"User is blocked: {block_reason}",
                    "sanitized_input": "",
                    "context_summary": self.context_manager.get_security_summary(context)
                }
            
            # Gate 1 & 2: Detect injection
            strict_mode = is_critical or generates_code
            detection_result = self.prompt_protection.detect_injection(
                input_text,
                strict_mode=strict_mode
            )
            
            # Update security context
            event_type = "llm_input_check"
            if detection_result.is_malicious:
                event_type = self._classify_attack_type(detection_result.matched_patterns)
            
            self.context_manager.update_threat_level(
                context=context,
                new_risk_score=detection_result.risk_score,
                event_type=event_type,
                details=detection_result.reasoning,
                blocked=detection_result.is_malicious
            )
            
            # Gate 3: Decision
            decision = self._make_decision(
                detection_result=detection_result,
                context=context,
                is_critical=is_critical,
                generates_code=generates_code
            )
            
            # If quarantine, store for review
            if decision == "QUARANTINE":
                await self._quarantine_threat({
                    "input": input_text,
                    "sanitized": detection_result.sanitized_text,
                    "user_id": user_id,
                    "endpoint": endpoint,
                    "risk_score": detection_result.risk_score,
                    "reasoning": detection_result.reasoning,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Log decision
            logger.info(
                "LLM input validation completed",
                user_id=user_id,
                endpoint=endpoint,
                decision=decision,
                risk_score=detection_result.risk_score,
                threat_level=context.threat_level.value
            )
            
            return {
                "decision": decision,
                "risk_score": detection_result.risk_score,
                "sanitized_input": detection_result.sanitized_text,
                "reasoning": detection_result.reasoning,
                "matched_patterns": detection_result.matched_patterns,
                "invisible_chars_found": detection_result.invisible_chars_found,
                "context_summary": self.context_manager.get_security_summary(context)
            }
            
        except Exception as e:
            logger.error("Error in LLM input validation", error=str(e))
            return {
                "decision": "BLOCK",
                "risk_score": 100,
                "reasoning": f"Validation error: {str(e)}",
                "sanitized_input": ""
            }
    
    def _make_decision(
        self,
        detection_result,
        context,
        is_critical: bool,
        generates_code: bool
    ) -> str:
        """
        Make final decision: ALLOW, BLOCK, or QUARANTINE
        
        Args:
            detection_result: PromptProtection detection result
            context: SecurityContext
            is_critical: Whether endpoint is critical
            generates_code: Whether LLM generates code
            
        Returns:
            Decision string
        """
        risk_score = detection_result.risk_score
        threat_level = context.threat_level
        
        # Stricter thresholds for critical endpoints
        if is_critical or generates_code:
            block_threshold = 30
            quarantine_threshold = 20
        else:
            block_threshold = 70
            quarantine_threshold = 50
        
        # Always block critical threats
        if risk_score >= block_threshold:
            return "BLOCK"
        
        # Quarantine medium risks
        if risk_score >= quarantine_threshold:
            return "QUARANTINE"
        
        # Consider user's threat level
        if threat_level == ThreatLevel.CRITICAL:
            return "BLOCK"
        elif threat_level == ThreatLevel.HIGH and risk_score > 30:
            return "QUARANTINE"
        
        # Allow low risk
        return "ALLOW"
    
    def _classify_attack_type(self, matched_patterns: List[str]) -> str:
        """Classify attack type from matched patterns"""
        if not matched_patterns:
            return "unknown"
        
        # Count pattern categories
        categories = {}
        for pattern in matched_patterns:
            if ":" in pattern:
                category = pattern.split(":")[0]
                categories[category] = categories.get(category, 0) + 1
        
        # Return most common category
        if categories:
            return max(categories, key=categories.get)
        
        return "unknown"
    
    async def _filter_llm_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter LLM output (Gate 4)
        
        Args:
            data: {
                "output": str,
                "mask_pii": bool (optional),
                "validate_code": bool (optional)
            }
            
        Returns:
            {
                "filtered_output": str,
                "redactions_made": int,
                "is_safe": bool,
                "warnings": list
            }
        """
        try:
            output_text = data.get("output", "")
            mask_pii = data.get("mask_pii", True)
            validate_code = data.get("validate_code", False)
            
            # Filter response
            filtered = self.output_filter.filter_response(output_text, mask_pii)
            
            # Validate safety
            is_safe, warnings = self.output_filter.validate_safety(
                filtered,
                strict=validate_code
            )
            
            # If validating code, do extra check
            if validate_code:
                code_result = self.output_filter.validate_code_proposal(filtered)
                is_safe = is_safe and code_result.is_safe
                warnings.extend(code_result.warnings)
            
            return {
                "filtered_output": filtered,
                "redactions_made": len(warnings),
                "is_safe": is_safe,
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error("Error in output filtering", error=str(e))
            return {
                "filtered_output": "",
                "redactions_made": 0,
                "is_safe": False,
                "warnings": [f"Filter error: {str(e)}"]
            }
    
    async def _check_security_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check security context for a user
        
        Args:
            data: {"user_id": str}
            
        Returns:
            Security context summary
        """
        user_id = data.get("user_id")
        if not user_id:
            return {"error": "user_id required"}
        
        context = self.context_manager.get_or_create_context(user_id)
        return self.context_manager.get_security_summary(context)
    
    async def _validate_code_proposal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate code proposal for security
        
        Args:
            data: {
                "code": str,
                "proposal_id": str
            }
            
        Returns:
            Validation result
        """
        code = data.get("code", "")
        
        # Use output filter to validate code
        result = self.output_filter.validate_code_proposal(code)
        
        if not result.is_safe:
            logger.error(
                "Malicious code detected in proposal",
                proposal_id=data.get("proposal_id"),
                warnings=result.warnings
            )
        
        return {
            "is_safe": result.is_safe,
            "warnings": result.warnings,
            "redacted_types": result.redacted_types,
            "filtered_code": result.filtered_text
        }
    
    async def _scan_image(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan image for security threats
        
        Args:
            data: {
                "image_data": bytes or str (base64),
                "filename": str (optional),
                "user_id": str
            }
            
        Returns:
            Scan result
        """
        try:
            image_data = data.get("image_data")
            filename = data.get("filename")
            user_id = data.get("user_id", "unknown")
            
            # If base64 string, decode first
            if isinstance(image_data, str):
                is_valid, decoded = self.image_scanner.validate_base64_image(image_data)
                if not is_valid:
                    return {
                        "is_safe": False,
                        "error": "Invalid base64 image data",
                        "risk_score": 100
                    }
                image_data = decoded
            
            # Scan image
            result = await self.image_scanner.scan_image(image_data, filename)
            
            # Log if threat detected
            if not result.is_safe:
                logger.error(
                    "Image security threat detected",
                    user_id=user_id,
                    risk_score=result.risk_score,
                    issues=result.issues,
                    file_hash=result.file_hash[:16]
                )
            
            # If extracted text contains injection, also check it
            if result.extracted_text:
                text_check = self.prompt_protection.detect_injection(
                    result.extracted_text
                )
                if text_check.is_malicious:
                    result.is_safe = False
                    result.risk_score = max(result.risk_score, text_check.risk_score)
                    result.issues.append(
                        f"Prompt injection detected in extracted text (risk: {text_check.risk_score})"
                    )
            
            return {
                "is_safe": result.is_safe,
                "risk_score": result.risk_score,
                "issues": result.issues,
                "extracted_text": result.extracted_text,
                "metadata": result.metadata,
                "file_hash": result.file_hash,
                "file_size": result.file_size,
                "image_format": result.image_format,
                "warnings": result.warnings
            }
            
        except Exception as e:
            logger.error("Error scanning image", error=str(e))
            return {
                "is_safe": False,
                "error": str(e),
                "risk_score": 100
            }
    
    async def _quarantine_threat(self, threat_data: Dict[str, Any]):
        """
        Quarantine a threat for admin review
        
        Args:
            threat_data: Threat information
        """
        self.quarantined_threats.append(threat_data)
        
        # Keep only last 100
        if len(self.quarantined_threats) > 100:
            self.quarantined_threats = self.quarantined_threats[-100:]
        
        logger.warning(
            "Threat quarantined for review",
            user_id=threat_data.get("user_id"),
            risk_score=threat_data.get("risk_score")
        )
        
        # TODO: Send admin notification
    
    def get_quarantined_threats(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent quarantined threats"""
        return self.quarantined_threats[-limit:]
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get comprehensive security statistics"""
        return {
            "prompt_protection": self.prompt_protection.get_stats(),
            "output_filter": self.output_filter.get_stats(),
            "context_manager": self.context_manager.get_global_stats(),
            "quarantined_threats": len(self.quarantined_threats),
            "timestamp": datetime.utcnow().isoformat()
        }
