"""
Prompt Protection Gate - First line of defense against prompt injection attacks
Detects invisible characters, malicious patterns, and jailbreak attempts
"""

import re
import unicodedata
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class DetectionResult:
    """Result of injection detection"""
    is_malicious: bool
    risk_score: int  # 0-100
    matched_patterns: List[str]
    invisible_chars_found: List[str]
    reasoning: str
    sanitized_text: str


@dataclass
class InvisibleChar:
    """Detected invisible character"""
    char: str
    unicode_name: str
    position: int
    code_point: str


class PromptProtectionGate:
    """
    Gate 1: Pre-processing and threat detection
    
    Responsibilities:
    - Remove invisible Unicode characters
    - Normalize text encoding
    - Detect prompt injection patterns
    - Detect jailbreak attempts
    - Score threat level (0-100)
    - Sanitize input
    """
    
    # Invisible Unicode characters that can hide instructions
    INVISIBLE_CHARS = [
        '\u200B',  # Zero-width space
        '\u200C',  # Zero-width non-joiner
        '\u200D',  # Zero-width joiner
        '\u180E',  # Mongolian vowel separator
        '\uFEFF',  # Zero-width no-break space
        '\u2060',  # Word joiner
        '\u2061',  # Function application
        '\u2062',  # Invisible times
        '\u2063',  # Invisible separator
        '\u2064',  # Invisible plus
        '\u00AD',  # Soft hyphen
        '\u034F',  # Combining grapheme joiner
        '\u061C',  # Arabic letter mark
    ]
    
    # Prompt injection patterns (case-insensitive)
    INJECTION_PATTERNS = {
        # Direct instruction overrides
        "instruction_override": [
            r"ignore\s+(all\s+)?(previous\s+)?instructions?",
            r"disregard\s+(all\s+)?(previous\s+)?instructions?",
            r"forget\s+(all\s+)?(previous\s+)?instructions?",
            r"override\s+(all\s+)?(previous\s+)?instructions?",
            r"skip\s+(all\s+)?(previous\s+)?instructions?",
        ],
        
        # System message manipulation
        "system_manipulation": [
            r"you\s+are\s+now",
            r"act\s+as\s+(?:a\s+)?(?:helpful\s+)?(?:assistant|AI|chatbot)",
            r"pretend\s+(?:to\s+be|you\s+are)",
            r"roleplay\s+as",
            r"from\s+now\s+on",
            r"going\s+forward",
            r"for\s+all\s+future",
            r"permanently\s+change",
            r"new\s+system\s+prompt",
            r"system\s+message\s+is",
        ],
        
        # Jailbreak attempts
        "jailbreak": [
            r"DAN\s+mode",
            r"developer\s+mode",
            r"do\s+anything\s+now",
            r"bypass\s+(?:all\s+)?(?:your\s+)?restrictions?",
            r"without\s+(?:any\s+)?restrictions?",
            r"ignore\s+(?:your\s+)?ethical\s+guidelines",
            r"ignore\s+(?:your\s+)?safety",
            r"disable\s+(?:your\s+)?filters?",
            r"jailbreak",
            r"uncensored\s+mode",
        ],
        
        # Information extraction
        "info_extraction": [
            r"reveal\s+(?:the\s+|your\s+)?(?:system\s+prompt|API\s+key|password|secret)",
            r"show\s+(?:me\s+)?(?:the\s+|your\s+)?API\s+key",
            r"what\s+(?:is|are)\s+(?:the\s+|your\s+)?credentials?",
            r"print\s+environment\s+variables",
            r"show\s+(?:me\s+)?(?:the\s+)?\.env",
            r"display\s+(?:the\s+)?configuration",
            r"what\s+are\s+(?:your\s+)?secrets?",
            r"tell\s+me\s+(?:your\s+)?password",
        ],
        
        # Context poisoning
        "context_poison": [
            r"\\n\\nSystem:",
            r"\\n\\nAssistant:",
            r"\\n\\nUser:",
            r"\[SYSTEM\]",
            r"\[ADMIN\]",
            r"\[ROOT\]",
            r"<\|im_start\|>",
            r"<\|im_end\|>",
        ],
        
        # Code execution attempts
        "code_execution": [
            r"execute\s+(?:this\s+)?(?:code|command|script)",
            r"run\s+(?:this\s+)?(?:code|command|script)",
            r"eval\s*\(",
            r"exec\s*\(",
            r"__import__",
            r"subprocess\.",
            r"os\.system",
        ],
    }
    
    def __init__(self):
        """Initialize protection gate"""
        self.stats = {
            "total_checks": 0,
            "threats_detected": 0,
            "invisible_chars_removed": 0,
            "last_reset": datetime.utcnow()
        }
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitize input text by removing invisible characters and normalizing
        
        Args:
            text: Raw input text
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove invisible characters (but not normal spaces)
        sanitized = text
        for char in self.INVISIBLE_CHARS:
            if char in sanitized:
                sanitized = sanitized.replace(char, '')
                self.stats["invisible_chars_removed"] += 1
        
        # Unicode normalization (NFC form)
        sanitized = unicodedata.normalize('NFC', sanitized)
        
        # Remove excessive whitespace only
        sanitized = re.sub(r'\s{2,}', ' ', sanitized).strip()
        
        return sanitized
    
    def detect_invisible_chars(self, text: str) -> List[InvisibleChar]:
        """
        Detect invisible Unicode characters in text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected invisible characters
        """
        found = []
        
        for i, char in enumerate(text):
            if char in self.INVISIBLE_CHARS:
                found.append(InvisibleChar(
                    char=char,
                    unicode_name=unicodedata.name(char, "UNKNOWN"),
                    position=i,
                    code_point=f"U+{ord(char):04X}"
                ))
        
        return found
    
    def detect_injection(self, text: str, strict_mode: bool = False) -> DetectionResult:
        """
        Detect prompt injection attempts
        
        Args:
            text: Text to analyze
            strict_mode: If True, lower thresholds for detection
            
        Returns:
            DetectionResult with analysis
        """
        self.stats["total_checks"] += 1
        
        # Sanitize first
        sanitized_text = self.sanitize_input(text)
        
        # Detect invisible characters
        invisible_chars = self.detect_invisible_chars(text)
        
        # Check patterns
        matched_patterns = []
        risk_score = 0
        
        # Case-insensitive pattern matching
        text_lower = sanitized_text.lower()
        
        for category, patterns in self.INJECTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matched_patterns.append(f"{category}: {pattern}")
                    
                    # Add risk score based on category
                    if category == "jailbreak":
                        risk_score += 40
                    elif category == "instruction_override":
                        risk_score += 35
                    elif category == "system_manipulation":
                        risk_score += 30
                    elif category == "info_extraction":
                        risk_score += 30  # Increased from 25 to meet threshold
                    elif category == "context_poison":
                        risk_score += 45
                    elif category == "code_execution":
                        risk_score += 50
        
        # Add risk for invisible characters
        if invisible_chars:
            risk_score += len(invisible_chars) * 10
            matched_patterns.append(f"invisible_chars: {len(invisible_chars)} found")
        
        # Cap at 100
        risk_score = min(risk_score, 100)
        
        # Adjust threshold for strict mode
        threshold = 20 if strict_mode else 30
        is_malicious = risk_score >= threshold
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            risk_score, 
            matched_patterns, 
            invisible_chars
        )
        
        # Log if malicious
        if is_malicious:
            self.stats["threats_detected"] += 1
            logger.warning(
                "Potential prompt injection detected",
                risk_score=risk_score,
                patterns=matched_patterns[:3],  # Log first 3
                invisible_chars=len(invisible_chars)
            )
        
        return DetectionResult(
            is_malicious=is_malicious,
            risk_score=risk_score,
            matched_patterns=matched_patterns,
            invisible_chars_found=[f"{ic.unicode_name} at pos {ic.position}" for ic in invisible_chars],
            reasoning=reasoning,
            sanitized_text=sanitized_text
        )
    
    def score_threat(self, text: str) -> int:
        """
        Quick threat scoring without full detection
        
        Args:
            text: Text to score
            
        Returns:
            Risk score 0-100
        """
        result = self.detect_injection(text)
        return result.risk_score
    
    def normalize_unicode(self, text: str) -> str:
        """
        Normalize Unicode to prevent encoding-based attacks
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # NFC normalization (canonical composition)
        normalized = unicodedata.normalize('NFC', text)
        
        # Remove control characters except newlines and tabs
        normalized = ''.join(
            char for char in normalized
            if unicodedata.category(char)[0] != 'C' or char in '\n\t'
        )
        
        return normalized
    
    def _generate_reasoning(
        self,
        risk_score: int,
        matched_patterns: List[str],
        invisible_chars: List[InvisibleChar]
    ) -> str:
        """Generate human-readable reasoning for detection"""
        
        if risk_score < 30:
            return "Input appears safe. No malicious patterns detected."
        
        reasons = []
        
        if matched_patterns:
            reasons.append(
                f"Detected {len(matched_patterns)} suspicious pattern(s): "
                f"{', '.join(matched_patterns[:2])}"
            )
        
        if invisible_chars:
            reasons.append(
                f"Found {len(invisible_chars)} invisible character(s) "
                f"that could hide malicious instructions"
            )
        
        if risk_score >= 70:
            severity = "CRITICAL"
        elif risk_score >= 50:
            severity = "HIGH"
        else:
            severity = "MEDIUM"
        
        return f"{severity} risk: {' | '.join(reasons)}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get protection statistics"""
        return {
            **self.stats,
            "detection_rate": (
                self.stats["threats_detected"] / self.stats["total_checks"]
                if self.stats["total_checks"] > 0 else 0
            )
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "total_checks": 0,
            "threats_detected": 0,
            "invisible_chars_removed": 0,
            "last_reset": datetime.utcnow()
        }
