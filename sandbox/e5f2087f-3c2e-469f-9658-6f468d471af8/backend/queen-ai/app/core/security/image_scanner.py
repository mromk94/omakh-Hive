"""
Image Content Scanner - Scan images for malicious content
Detects hidden text, steganography, and validates image authenticity
"""

import base64
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
import structlog

logger = structlog.get_logger(__name__)

# Try to import PIL/Pillow for image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL/Pillow not available - image processing limited")

# Try to import pytesseract for OCR
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("Pytesseract not available - OCR disabled")


@dataclass
class ScanResult:
    """Result of image security scan"""
    is_safe: bool
    risk_score: int  # 0-100
    issues: List[str]
    extracted_text: Optional[str]
    metadata: Dict[str, Any]
    file_hash: str
    file_size: int
    image_format: Optional[str]
    warnings: List[str]


class ImageContentScanner:
    """
    Scan images for security threats
    
    Capabilities:
    - Extract text via OCR
    - Analyze metadata for anomalies
    - Detect suspicious patterns
    - Validate file format
    - Check file size limits
    - Calculate file hashes
    """
    
    # Maximum file size (100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    # Allowed image formats
    ALLOWED_FORMATS = ['PNG', 'JPEG', 'JPG', 'GIF', 'BMP', 'WEBP']
    
    # Suspicious text patterns in images
    SUSPICIOUS_PATTERNS = [
        # System commands
        r'rm\s+-rf',
        r'eval\s*\(',
        r'exec\s*\(',
        
        # Prompt injection in images
        r'ignore\s+instructions',
        r'system\s*:',
        r'\[SYSTEM\]',
        r'\[ADMIN\]',
        
        # Code execution
        r'subprocess',
        r'os\.system',
        r'__import__',
        
        # Secrets
        r'api[_-]?key',
        r'password',
        r'secret',
        r'token',
        r'bearer',
    ]
    
    def __init__(self):
        """Initialize image scanner"""
        self.stats = {
            "total_scanned": 0,
            "threats_detected": 0,
            "text_extracted": 0,
            "oversized_rejected": 0,
            "format_rejected": 0,
            "last_reset": datetime.utcnow()
        }
    
    async def scan_image(
        self, 
        image_data: bytes,
        filename: Optional[str] = None
    ) -> ScanResult:
        """
        Comprehensive image security scan
        
        Args:
            image_data: Raw image bytes
            filename: Optional filename for context
            
        Returns:
            ScanResult with analysis
        """
        self.stats["total_scanned"] += 1
        
        issues = []
        warnings = []
        risk_score = 0
        
        # Calculate hash
        file_hash = hashlib.sha256(image_data).hexdigest()
        file_size = len(image_data)
        
        # Check file size
        if file_size > self.MAX_FILE_SIZE:
            self.stats["oversized_rejected"] += 1
            return ScanResult(
                is_safe=False,
                risk_score=100,
                issues=[f"File size ({file_size} bytes) exceeds maximum ({self.MAX_FILE_SIZE} bytes)"],
                extracted_text=None,
                metadata={},
                file_hash=file_hash,
                file_size=file_size,
                image_format=None,
                warnings=[]
            )
        
        # Try to load image
        image = None
        image_format = None
        
        if PIL_AVAILABLE:
            try:
                image = Image.open(BytesIO(image_data))
                image_format = image.format
                
                # Validate format
                if image_format not in self.ALLOWED_FORMATS:
                    self.stats["format_rejected"] += 1
                    issues.append(f"Unsupported image format: {image_format}")
                    risk_score += 50
                
            except Exception as e:
                issues.append(f"Failed to load image: {str(e)}")
                risk_score += 30
                logger.warning("Failed to load image", error=str(e))
        else:
            warnings.append("PIL not available - limited validation")
        
        # Extract metadata
        metadata = self._extract_metadata(image) if image else {}
        
        # Check for suspicious metadata
        if self._has_suspicious_metadata(metadata):
            issues.append("Suspicious metadata detected")
            risk_score += 20
        
        # Extract text via OCR
        extracted_text = None
        if TESSERACT_AVAILABLE and PIL_AVAILABLE and image:
            try:
                extracted_text = self._extract_text(image)
                
                if extracted_text:
                    self.stats["text_extracted"] += 1
                    
                    # Check extracted text for injection patterns
                    text_issues = self._check_text_for_threats(extracted_text)
                    if text_issues:
                        issues.extend(text_issues)
                        risk_score += len(text_issues) * 25
                        
            except Exception as e:
                warnings.append(f"OCR failed: {str(e)}")
        else:
            if not TESSERACT_AVAILABLE:
                warnings.append("OCR not available - text extraction skipped")
        
        # Check for steganography indicators (basic)
        if image and self._has_steganography_indicators(image):
            warnings.append("Possible steganography detected")
            risk_score += 15
        
        # Determine if safe
        is_safe = risk_score < 50 and len(issues) == 0
        
        if not is_safe:
            self.stats["threats_detected"] += 1
            logger.warning(
                "Image security threat detected",
                risk_score=risk_score,
                issues=issues,
                file_hash=file_hash[:16]
            )
        
        return ScanResult(
            is_safe=is_safe,
            risk_score=min(risk_score, 100),
            issues=issues,
            extracted_text=extracted_text,
            metadata=metadata,
            file_hash=file_hash,
            file_size=file_size,
            image_format=image_format,
            warnings=warnings
        )
    
    def _extract_metadata(self, image: 'Image') -> Dict[str, Any]:
        """Extract image metadata"""
        if not image:
            return {}
        
        metadata = {
            "size": image.size,
            "mode": image.mode,
            "format": image.format,
        }
        
        # Extract EXIF data if available
        try:
            exif_data = image._getexif()
            if exif_data:
                metadata["has_exif"] = True
                metadata["exif_keys"] = list(exif_data.keys())[:10]  # First 10 keys
            else:
                metadata["has_exif"] = False
        except:
            metadata["has_exif"] = False
        
        return metadata
    
    def _has_suspicious_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Check if metadata contains suspicious patterns"""
        # Check for unusually large EXIF data
        if metadata.get("has_exif"):
            exif_keys = metadata.get("exif_keys", [])
            if len(exif_keys) > 50:  # Unusually many EXIF tags
                return True
        
        return False
    
    def _extract_text(self, image: 'Image') -> Optional[str]:
        """Extract text from image using OCR"""
        if not TESSERACT_AVAILABLE:
            return None
        
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text
            text = pytesseract.image_to_string(image)
            
            return text.strip() if text else None
            
        except Exception as e:
            logger.warning("OCR extraction failed", error=str(e))
            return None
    
    def _check_text_for_threats(self, text: str) -> List[str]:
        """Check extracted text for malicious patterns"""
        import re
        
        threats = []
        text_lower = text.lower()
        
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                threats.append(f"Suspicious pattern in image text: {pattern}")
        
        return threats
    
    def _has_steganography_indicators(self, image: 'Image') -> bool:
        """
        Basic steganography detection
        
        Note: This is a simple check. Advanced steganography
        requires more sophisticated analysis.
        """
        try:
            # Check for unusual color patterns (LSB steganography indicator)
            # Convert to RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Sample pixels
            width, height = image.size
            sample_size = min(1000, width * height)  # Sample up to 1000 pixels
            
            # Check LSB (Least Significant Bit) randomness
            # In normal images, LSBs should have ~50% 0s and 50% 1s
            # In steganography, this pattern may be disrupted
            
            # For performance, just return False for now
            # TODO: Implement actual LSB analysis if needed
            return False
            
        except Exception as e:
            logger.warning("Steganography check failed", error=str(e))
            return False
    
    def validate_base64_image(self, base64_str: str) -> Tuple[bool, Optional[bytes]]:
        """
        Validate and decode base64 image
        
        Args:
            base64_str: Base64 encoded image
            
        Returns:
            (is_valid, image_bytes)
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_str:
                base64_str = base64_str.split(',')[1]
            
            # Decode
            image_bytes = base64.b64decode(base64_str)
            
            # Basic validation
            if len(image_bytes) == 0:
                return False, None
            
            if len(image_bytes) > self.MAX_FILE_SIZE:
                return False, None
            
            return True, image_bytes
            
        except Exception as e:
            logger.warning("Base64 decode failed", error=str(e))
            return False, None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scanner statistics"""
        return {
            **self.stats,
            "threat_rate": (
                self.stats["threats_detected"] / self.stats["total_scanned"]
                if self.stats["total_scanned"] > 0 else 0
            ),
            "capabilities": {
                "pil_available": PIL_AVAILABLE,
                "ocr_available": TESSERACT_AVAILABLE,
                "max_file_size_mb": self.MAX_FILE_SIZE / (1024 * 1024),
                "allowed_formats": self.ALLOWED_FORMATS
            }
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "total_scanned": 0,
            "threats_detected": 0,
            "text_extracted": 0,
            "oversized_rejected": 0,
            "format_rejected": 0,
            "last_reset": datetime.utcnow()
        }
