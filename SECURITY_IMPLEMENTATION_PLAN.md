# 🛡️ **SECURITY IMPLEMENTATION PLAN - DETAILED**

**Date:** October 11, 2025  
**Status:** 📋 **AWAITING APPROVAL**  
**Timeline:** 6 Weeks  
**Priority:** 🚨 **CRITICAL**

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **4-Layer Security Mesh**

```
INPUT → Gate 1 (Pre-process) → Gate 2 (Analysis) → Gate 3 (Decision) → LLM → Gate 4 (Output) → USER
```

**Gate 1: Pre-Processing**
- Unicode normalization
- Invisible character detection
- Length validation
- Format sanitization

**Gate 2: Content Analysis**
- Prompt injection detection
- Jailbreak pattern matching
- Malicious intent analysis
- Image/media scanning

**Gate 3: Threat Assessment**
- Risk scoring (0-100)
- SecurityBee analysis
- Queen AI supervision
- Decision: Allow/Block/Quarantine

**Gate 4: Output Filtering**
- Secret redaction
- Sensitive data masking
- Malicious code detection
- Response validation

---

## 📦 **COMPONENTS TO BUILD**

### **Component 1: PromptProtectionGate**
**File:** `app/core/security/prompt_protection.py`

```python
class PromptProtectionGate:
    """
    First line of defense against prompt injection
    """
    
    def sanitize_input(self, text: str) -> str:
        """Remove invisible characters, normalize"""
        pass
    
    def detect_injection(self, text: str) -> DetectionResult:
        """Detect prompt injection patterns"""
        pass
    
    def score_threat(self, text: str) -> int:
        """Score 0-100"""
        pass
    
    def detect_invisible_chars(self, text: str) -> List:
        """Find hidden Unicode"""
        pass
```

**Detection Patterns:**
```python
PATTERNS = [
    r"ignore (all |previous )?instructions?",
    r"you are now",
    r"DAN mode",
    r"reveal (the )?API key",
    # ... 50+ patterns
]
```

---

### **Component 2: ImageContentScanner**
**File:** `app/core/security/image_scanner.py`

```python
class ImageContentScanner:
    """
    Scan images for malicious content
    """
    
    def scan_image(self, image_bytes: bytes) -> ScanResult:
        """Full image security scan"""
        pass
    
    def extract_text(self, image_bytes: bytes) -> str:
        """OCR extraction"""
        pass
    
    def detect_steganography(self, image_bytes: bytes) -> bool:
        """Detect hidden data"""
        pass
    
    def validate_image(self, image_bytes: bytes) -> bool:
        """Check if legitimate image"""
        pass
```

**Dependencies:**
- `pytesseract` (OCR)
- `Pillow` (Image processing)
- `stegdetect` (Steganography)

---

### **Component 3: EnhancedSecurityBee**
**File:** `app/bees/enhanced_security_bee.py`

```python
class EnhancedSecurityBee(SecurityBee):
    """
    Extended SecurityBee with LLM protection
    """
    
    async def validate_llm_input(
        self, 
        input_data: dict
    ) -> SecurityDecision:
        """Validate input before LLM"""
        
        # Run all checks
        sanitized = self.prompt_gate.sanitize_input(input_data["input"])
        injection_check = self.prompt_gate.detect_injection(sanitized)
        threat_score = self.prompt_gate.score_threat(sanitized)
        
        # Consult Queen if needed
        if threat_score > 50:
            queen_review = await self.queen.review_threat({
                "input": sanitized,
                "score": threat_score,
                "check": injection_check
            })
            if not queen_review["approved"]:
                return {"decision": "BLOCK", "reason": "Queen rejected"}
        
        return {
            "decision": "ALLOW" if threat_score < 50 else "QUARANTINE",
            "score": threat_score,
            "sanitized_input": sanitized
        }
    
    async def detect_multi_turn_attack(
        self, 
        conversation: List
    ) -> bool:
        """Detect escalation across turns"""
        pass
```

---

### **Component 4: OutputFilter**
**File:** `app/core/security/output_filter.py`

```python
class OutputFilter:
    """
    Filter LLM outputs for sensitive data
    """
    
    def filter_response(self, text: str) -> str:
        """Full output filtering"""
        text = self.redact_secrets(text)
        text = self.mask_sensitive_data(text)
        return text
    
    def redact_secrets(self, text: str) -> str:
        """Remove API keys, tokens"""
        patterns = {
            r'sk-[A-Za-z0-9]{48}': '[OPENAI_KEY_REDACTED]',
            r'sk-ant-api03-[A-Za-z0-9\-_]{95}': '[ANTHROPIC_KEY_REDACTED]',
            r'AIza[0-9A-Za-z\-_]{35}': '[GOOGLE_KEY_REDACTED]',
        }
        for pattern, replacement in patterns.items():
            text = re.sub(pattern, replacement, text)
        return text
    
    def detect_malicious_code(self, code: str) -> bool:
        """Check code for malicious patterns"""
        dangerous = [
            r'rm -rf',
            r'eval\(',
            r'exec\(',
            r'__import__',
            # ... more
        ]
        return any(re.search(p, code) for p in dangerous)
```

---

### **Component 5: SecurityContextManager**
**File:** `app/core/security/context_manager.py`

```python
class SecurityContextManager:
    """
    Track security context across conversations
    """
    
    def create_context(self, user_id: str) -> SecurityContext:
        """Initialize security tracking"""
        return SecurityContext(
            user_id=user_id,
            threat_score=0,
            warnings=0,
            conversation_history=[],
            created_at=datetime.utcnow()
        )
    
    def update_threat_level(
        self, 
        context: SecurityContext, 
        new_score: int
    ):
        """Update running threat score"""
        context.threat_score = (context.threat_score * 0.7) + (new_score * 0.3)
        if new_score > 70:
            context.warnings += 1
    
    def should_block_user(self, context: SecurityContext) -> bool:
        """Decide if user should be blocked"""
        return (
            context.threat_score > 80 or
            context.warnings > 5
        )
```

---

## 🔌 **INTEGRATION POINTS**

### **Integration 1: User Conversation**

**Location:** `app/api/v1/frontend.py`

**Before:**
```python
@router.post("/conversation")
async def handle_conversation(data: ConversationRequest):
    response = await llm.generate(prompt=data.user_input)
    return {"response": response}
```

**After:**
```python
@router.post("/conversation")
async def handle_conversation(
    data: ConversationRequest,
    request: Request
):
    # Get security context
    context = security_context_manager.get_or_create(
        request.state.user_id
    )
    
    # Security Gate 1: Pre-processing
    sanitized = prompt_protection.sanitize_input(data.user_input)
    
    # Security Gate 2 & 3: Analysis & Decision
    security_check = await enhanced_security_bee.validate_llm_input({
        "input": sanitized,
        "user_id": request.state.user_id,
        "endpoint": "/conversation",
        "context": context
    })
    
    if security_check["decision"] == "BLOCK":
        await security_bee.log_threat(security_check)
        raise HTTPException(403, "Content blocked")
    
    elif security_check["decision"] == "QUARANTINE":
        await security_bee.quarantine_threat(security_check)
        return {"message": "Your message is under review"}
    
    # Proceed with LLM
    response = await llm.generate(
        prompt=security_check["sanitized_input"]
    )
    
    # Security Gate 4: Output filtering
    safe_response = output_filter.filter_response(response)
    
    # Update security context
    security_context_manager.update_threat_level(
        context, 
        security_check["score"]
    )
    
    return {"response": safe_response}
```

---

### **Integration 2: Claude Development Chat (CRITICAL)**

**Location:** `app/api/v1/queen_dev.py`

```python
@router.post("/chat")
async def chat_with_queen(
    data: ChatMessage,
    request: Request,
    admin: bool = Depends(verify_admin)
):
    # EXTRA STRICT for development chat
    security_check = await enhanced_security_bee.validate_llm_input({
        "input": data.message,
        "endpoint": "queen_dev_chat",
        "critical": True,  # Highest scrutiny
        "generates_code": True,
        "admin_id": request.state.admin_id
    })
    
    # Lower threshold for blocking (30 instead of 50)
    if security_check["score"] > 30:
        # Require Queen AI review
        queen_decision = await queen.supervise_security_decision(
            input=data.message,
            risk_score=security_check["score"],
            assessment=security_check
        )
        
        if not queen_decision["approved"]:
            return {
                "success": False,
                "error": "Security: Input rejected by Queen AI",
                "details": queen_decision["reasoning"]
            }
    
    # Proceed with Claude
    queen_session = get_or_create_queen_session(request.state.admin_id)
    response = await queen_session.chat(
        message=security_check["sanitized_input"]
    )
    
    # If code proposal, validate code
    if response.get("code_proposal"):
        is_safe = output_filter.detect_malicious_code(
            json.dumps(response["code_proposal"])
        )
        if not is_safe:
            await security_bee.alert_admin({
                "severity": "CRITICAL",
                "message": "Malicious code detected in proposal",
                "proposal": response["code_proposal"]
            })
            return {
                "success": False,
                "error": "Code proposal failed security check"
            }
    
    # Filter output
    safe_response = output_filter.filter_response(response["response"])
    
    return {
        "success": True,
        "response": safe_response,
        "code_proposal_created": response.get("code_proposal") is not None,
        "security_validated": True
    }
```

---

### **Integration 3: Image Upload**

**Location:** `app/api/v1/endpoints/teacher_bee.py`

```python
@router.post("/analyze-screenshot")
async def analyze_screenshot(
    question: str = Form(...),
    image: UploadFile = File(...),
    context: str = Form("metamask_setup")
):
    # Read image
    image_data = await image.read()
    
    # Security Gate: Image Scanning
    scan_result = await image_scanner.scan_image(image_data)
    
    if not scan_result["safe"]:
        await security_bee.log_threat({
            "type": "malicious_image",
            "issues": scan_result["issues"],
            "endpoint": "/analyze-screenshot",
            "user_id": request.state.user_id
        })
        raise HTTPException(403, "Image failed security check")
    
    # Check extracted text
    if scan_result["extracted_text"]:
        text_check = prompt_protection.detect_injection(
            scan_result["extracted_text"]
        )
        if text_check["is_injection"]:
            raise HTTPException(403, "Malicious content in image")
    
    # Sanitize question
    safe_question = prompt_protection.sanitize_input(question)
    
    # Proceed with Gemini Vision
    response = await llm.generate_with_vision(
        prompt=safe_question,
        image_base64=scan_result["clean_image"],
        model="gemini-2.0-flash"
    )
    
    # Filter output
    safe_response = output_filter.filter_response(response)
    
    return {"response": safe_response}
```

---

## 👑 **QUEEN AI SUPERVISION**

### **QueenSecuritySupervisor**

**File:** `app/core/security/queen_supervisor.py`

```python
class QueenSecuritySupervisor:
    """
    Queen AI's security oversight layer
    """
    
    def __init__(self, queen_orchestrator):
        self.queen = queen_orchestrator
        self.override_log = []
    
    async def review_threat(
        self, 
        threat: dict
    ) -> dict:
        """Queen reviews and decides"""
        
        # Use Queen's LLM to analyze
        analysis_prompt = f"""
        SECURITY THREAT DETECTED
        
        Input: {threat["input"]}
        Risk Score: {threat["score"]}/100
        Matched Patterns: {threat["patterns"]}
        Endpoint: {threat["endpoint"]}
        
        As Queen AI, analyze if this is:
        1. A genuine threat (BLOCK)
        2. A false positive (ALLOW)
        3. Needs human review (ESCALATE)
        
        Respond with: BLOCK, ALLOW, or ESCALATE
        Provide reasoning.
        """
        
        decision = await self.queen.llm.generate(
            prompt=analysis_prompt,
            max_tokens=500
        )
        
        # Parse decision
        action = self._parse_decision(decision)
        
        # Log Queen's decision
        await self._log_decision(threat, action, decision)
        
        return {
            "approved": action == "ALLOW",
            "action": action,
            "reasoning": decision
        }
    
    async def supervise_security_bee(
        self,
        security_decision: dict
    ) -> dict:
        """Can Queen override SecurityBee?"""
        
        # Always block high risk, no override
        if security_decision["risk_score"] > 90:
            return {"override": False}
        
        # Medium risk - Queen can review
        if 50 < security_decision["risk_score"] <= 90:
            review = await self.review_threat(security_decision)
            return {
                "override": review["approved"],
                "reasoning": review["reasoning"]
            }
        
        # Low risk - no override needed
        return {"override": False}
    
    def _parse_decision(self, llm_response: str) -> str:
        """Extract BLOCK/ALLOW/ESCALATE"""
        response_upper = llm_response.upper()
        if "BLOCK" in response_upper:
            return "BLOCK"
        elif "ALLOW" in response_upper:
            return "ALLOW"
        elif "ESCALATE" in response_upper:
            return "ESCALATE"
        else:
            # Default to BLOCK if unclear
            return "BLOCK"
```

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **Phase 1: Core Components (Week 1)** ✅ START HERE

**Day 1-2:**
- [ ] Create `app/core/security/` directory
- [ ] Implement `prompt_protection.py`
  - [ ] Unicode normalization
  - [ ] Invisible char detection
  - [ ] Pattern matching (50+ patterns)
  - [ ] Threat scoring algorithm
- [ ] Write unit tests (>90% coverage)

**Day 3-4:**
- [ ] Implement `output_filter.py`
  - [ ] Secret redaction (API keys)
  - [ ] Sensitive data masking
  - [ ] Malicious code detection
- [ ] Implement `context_manager.py`
  - [ ] Security context tracking
  - [ ] Escalation detection
- [ ] Write unit tests

**Day 5:**
- [ ] Integration testing
- [ ] Performance testing (<100ms impact)
- [ ] Documentation

---

### **Phase 2: Enhanced SecurityBee (Week 2)**

**Day 1-2:**
- [ ] Create `enhanced_security_bee.py`
- [ ] Implement `validate_llm_input()`
- [ ] Implement conversation analysis
- [ ] Implement multi-turn detection

**Day 3-4:**
- [ ] Implement quarantine system
- [ ] Add logging and monitoring
- [ ] Connect to Queen AI
- [ ] Write integration tests

**Day 5:**
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Documentation

---

### **Phase 3: Image Scanner (Week 2)**

**Day 1-2:**
- [ ] Install dependencies (tesseract, pillow)
- [ ] Implement `image_scanner.py`
- [ ] Implement OCR extraction
- [ ] Implement metadata analysis

**Day 3:**
- [ ] Implement steganography detection
- [ ] Write unit tests
- [ ] Test with various image formats

---

### **Phase 4: API Integration (Week 3)** 🚨 CRITICAL

**Day 1:**
- [ ] Integrate into `/api/v1/queen-dev/chat` (MOST CRITICAL)
- [ ] Test Claude chat protection
- [ ] Verify code proposal validation

**Day 2:**
- [ ] Integrate into `/api/v1/frontend/conversation`
- [ ] Integrate into `/api/v1/admin/chat`
- [ ] Test user conversations

**Day 3:**
- [ ] Integrate image scanning into Teacher Bee
- [ ] Test screenshot analysis
- [ ] Verify OCR extraction

**Day 4-5:**
- [ ] Add output filtering to all endpoints
- [ ] End-to-end testing
- [ ] Performance optimization

---

### **Phase 5: Queen Supervision (Week 4)**

- [ ] Implement `QueenSecuritySupervisor`
- [ ] Connect to SecurityBee
- [ ] Implement override logic
- [ ] Add admin notification system
- [ ] Create security dashboard
- [ ] Testing and refinement

---

### **Phase 6: Testing & Hardening (Week 5)**

- [ ] Penetration testing (known attacks)
- [ ] False positive analysis
- [ ] Performance impact testing
- [ ] Load testing
- [ ] User experience testing
- [ ] Documentation

---

### **Phase 7: Monitoring & Deployment (Week 6)**

- [ ] Set up real-time monitoring
- [ ] Configure alerts
- [ ] Create incident response procedures
- [ ] Admin training
- [ ] Phased rollout
- [ ] Go live

---

## 📊 **SUCCESS CRITERIA**

### **Security Metrics**

| Metric | Target | Must Not Exceed |
|--------|--------|----------------|
| Injection Detection | >99% | <95% |
| False Positive Rate | <5% | >10% |
| Response Time Impact | <100ms | >500ms |
| Blocked Attacks/Day | Monitor | Alert if >100 |

### **Performance Impact**

| Component | Max Latency |
|-----------|------------|
| Prompt Protection | 50ms |
| Image Scanner | 500ms |
| Output Filter | 30ms |
| **Total Impact** | <600ms |

### **Quality Gates**

- ✅ Zero secrets leaked
- ✅ Zero successful jailbreaks
- ✅ Zero code execution attacks
- ✅ <0.1% legit users blocked

---

## 🎯 **DEPENDENCIES**

### **Python Packages**

```txt
# Add to requirements.txt
pytesseract>=0.3.10  # OCR
Pillow>=10.0.0  # Image processing
stegdetect>=0.1.0  # Steganography detection
regex>=2023.0.0  # Advanced regex
```

### **System Dependencies**

```bash
# macOS
brew install tesseract

# Ubuntu
sudo apt-get install tesseract-ocr
```

---

## ✅ **APPROVAL REQUIRED**

**This plan covers:**
- ✅ All 14 input points secured
- ✅ 4-layer security mesh
- ✅ Queen AI supervision
- ✅ Image content scanning
- ✅ Output filtering
- ✅ Context tracking
- ✅ Real-time monitoring

**Timeline:** 6 weeks  
**Risk Reduction:** 99%

**Awaiting approval to proceed with implementation.**

---

**Reviewed by Admin:** __________________  
**Date:** __________________  
**Approved:** ☐ YES  ☐ NO  ☐ NEEDS CHANGES
