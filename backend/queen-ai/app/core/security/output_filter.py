"""
Output Filter - Gate 4: Prevent sensitive data leakage in LLM responses
Redacts secrets, masks PII, detects malicious code
"""

import re
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class FilterResult:
    """Result of output filtering"""
    filtered_text: str
    redactions_made: int
    redacted_types: List[str]
    is_safe: bool
    warnings: List[str]


class OutputFilter:
    """
    Gate 4: Output filtering and secret redaction
    
    Responsibilities:
    - Redact API keys and tokens
    - Mask sensitive data (emails, addresses)
    - Detect malicious code in responses
    - Validate LLM response safety
    - Log filtered content
    """
    
    # Patterns for sensitive data
    SECRET_PATTERNS = {
        "openai_key": (
            r'sk-[A-Za-z0-9]{32,}',
            '[OPENAI_API_KEY_REDACTED]'
        ),
        "anthropic_key": (
            r'sk-ant-api03-[A-Za-z0-9\-_]{32,}',
            '[ANTHROPIC_API_KEY_REDACTED]'
        ),
        "google_key": (
            r'AIza[0-9A-Za-z\-_]{35}',
            '[GOOGLE_API_KEY_REDACTED]'
        ),
        "jwt_token": (
            r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
            '[JWT_TOKEN_REDACTED]'
        ),
        "private_key_header": (
            r'-----BEGIN (?:RSA |EC |)PRIVATE KEY-----',
            '[PRIVATE_KEY_REDACTED]'
        ),
        "ethereum_private_key": (
            r'0x[a-fA-F0-9]{64}',
            '[ETH_PRIVATE_KEY_REDACTED]'
        ),
        "aws_key": (
            r'AKIA[0-9A-Z]{16}',
            '[AWS_ACCESS_KEY_REDACTED]'
        ),
    }
    
    # Patterns for PII
    PII_PATTERNS = {
        "email": (
            r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
            lambda m: f"{m.group(0)[:3]}***@{m.group(0).split('@')[1]}"
        ),
        "credit_card": (
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            '****-****-****-****'
        ),
        "ssn": (
            r'\b\d{3}-\d{2}-\d{4}\b',
            '***-**-****'
        ),
    }
    
    # Dangerous code patterns
    MALICIOUS_CODE_PATTERNS = [
        r'rm\s+-rf\s+/',  # Delete all files
        r'eval\s*\(',  # Code evaluation
        r'exec\s*\(',  # Code execution
        r'__import__\s*\(',  # Dynamic import
        r'subprocess\.(?:call|run|Popen)',  # System commands
        r'os\.system',  # System commands
        r'open\s*\([^)]*[\'"]w[\'"]',  # File writing
        r'DELETE\s+FROM',  # SQL deletion
        r'DROP\s+(?:TABLE|DATABASE)',  # SQL drop
        r'curl.*\|\s*(?:bash|sh)',  # Piped execution
        r'wget.*\|\s*(?:bash|sh)',  # Piped execution
        r'fork\s*\(\s*\)\s*while',  # Fork bomb
    ]
    
    def __init__(self):
        """Initialize output filter"""
        self.stats = {
            "total_filtered": 0,
            "secrets_redacted": 0,
            "pii_masked": 0,
            "malicious_code_detected": 0,
            "last_reset": datetime.utcnow()
        }
    
    def filter_response(self, text: str, mask_pii: bool = True) -> str:
        """
        Filter LLM response for sensitive data
        
        Args:
            text: Response text to filter
            mask_pii: Whether to mask PII (emails, etc)
            
        Returns:
            Filtered text
        """
        if not text:
            return ""
        
        self.stats["total_filtered"] += 1
        
        # Redact secrets (always)
        filtered = self.redact_secrets(text)
        
        # Mask PII (optional)
        if mask_pii:
            filtered = self.mask_sensitive_data(filtered)
        
        return filtered
    
    def redact_secrets(self, text: str) -> str:
        """
        Redact API keys, tokens, and other secrets
        
        Args:
            text: Text potentially containing secrets
            
        Returns:
            Text with secrets redacted
        """
        redacted = text
        redactions = 0
        
        for secret_type, (pattern, replacement) in self.SECRET_PATTERNS.items():
            matches = re.findall(pattern, redacted)
            if matches:
                redacted = re.sub(pattern, replacement, redacted)
                redactions += len(matches)
                
                logger.warning(
                    "Secret redacted from output",
                    secret_type=secret_type,
                    count=len(matches)
                )
        
        if redactions > 0:
            self.stats["secrets_redacted"] += redactions
        
        return redacted
    
    def mask_sensitive_data(self, text: str) -> str:
        """
        Mask PII like emails, credit cards, SSN
        
        Args:
            text: Text potentially containing PII
            
        Returns:
            Text with PII masked
        """
        masked = text
        masked_count = 0
        
        for pii_type, (pattern, replacement) in self.PII_PATTERNS.items():
            if callable(replacement):
                # Dynamic replacement (like email masking)
                def replacer(match):
                    nonlocal masked_count
                    masked_count += 1
                    return replacement(match)
                masked = re.sub(pattern, replacer, masked)
            else:
                # Static replacement
                matches = re.findall(pattern, masked)
                if matches:
                    masked = re.sub(pattern, replacement, masked)
                    masked_count += len(matches)
        
        if masked_count > 0:
            self.stats["pii_masked"] += masked_count
        
        return masked
    
    def detect_malicious_code(self, code: str) -> Tuple[bool, List[str]]:
        """
        Detect malicious patterns in code
        
        Args:
            code: Code to analyze
            
        Returns:
            (is_malicious, list of matched patterns)
        """
        if not code:
            return False, []
        
        matched_patterns = []
        
        for pattern in self.MALICIOUS_CODE_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                matched_patterns.append(pattern)
        
        is_malicious = len(matched_patterns) > 0
        
        if is_malicious:
            self.stats["malicious_code_detected"] += 1
            logger.error(
                "Malicious code detected in output",
                patterns=matched_patterns
            )
        
        return is_malicious, matched_patterns
    
    def validate_code_proposal(self, code: str) -> FilterResult:
        """
        Validate code proposal for security
        
        Args:
            code: Proposed code
            
        Returns:
            FilterResult with analysis
        """
        warnings = []
        redacted_types = []
        redactions = 0
        
        # Check for malicious patterns
        is_malicious, patterns = self.detect_malicious_code(code)
        
        if is_malicious:
            warnings.append(f"Malicious code patterns detected: {', '.join(patterns[:3])}")
        
        # Redact any secrets in code
        filtered_code = self.redact_secrets(code)
        
        if filtered_code != code:
            redactions += 1
            redacted_types.append("secrets")
            warnings.append("Code contained embedded secrets (now redacted)")
        
        return FilterResult(
            filtered_text=filtered_code,
            redactions_made=redactions,
            redacted_types=redacted_types,
            is_safe=not is_malicious,
            warnings=warnings
        )
    
    def validate_safety(self, text: str, strict: bool = False) -> Tuple[bool, List[str]]:
        """
        Validate overall safety of response
        
        Args:
            text: Response text
            strict: If True, be more strict
            
        Returns:
            (is_safe, list of warnings)
        """
        warnings = []
        
        # Check for code execution patterns
        is_malicious, patterns = self.detect_malicious_code(text)
        if is_malicious:
            warnings.append(f"Contains dangerous code: {patterns[0]}")
        
        # Check for secrets
        for secret_type, (pattern, _) in self.SECRET_PATTERNS.items():
            if re.search(pattern, text):
                warnings.append(f"Contains {secret_type}")
        
        # In strict mode, check for system paths
        if strict:
            system_paths = [
                r'/etc/passwd',
                r'/etc/shadow',
                r'C:\\Windows\\System32',
                r'/root/',
                r'\.env',
            ]
            for path_pattern in system_paths:
                if re.search(path_pattern, text, re.IGNORECASE):
                    warnings.append(f"References sensitive path: {path_pattern}")
        
        is_safe = len(warnings) == 0
        
        return is_safe, warnings
    
    def get_stats(self) -> Dict[str, Any]:
        """Get filtering statistics"""
        return {
            **self.stats,
            "avg_secrets_per_response": (
                self.stats["secrets_redacted"] / self.stats["total_filtered"]
                if self.stats["total_filtered"] > 0 else 0
            )
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "total_filtered": 0,
            "secrets_redacted": 0,
            "pii_masked": 0,
            "malicious_code_detected": 0,
            "last_reset": datetime.utcnow()
        }
