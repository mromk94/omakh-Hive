"""
Teacher Bee API Endpoints
Handles educational content and screenshot analysis using Gemini Vision
"""

from fastapi import APIRouter, Request, Form, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
import base64
import structlog
from app.bees.enhanced_security_bee import EnhancedSecurityBee

logger = structlog.get_logger(__name__)

router = APIRouter()

# Initialize security bee
_security_bee = None

def get_security_bee():
    global _security_bee
    if not _security_bee:
        _security_bee = EnhancedSecurityBee()
    return _security_bee

class TeacherBeeRequest(BaseModel):
    question: str
    context: Optional[str] = None

@router.post("/analyze-image")
async def analyze_image_with_gemini(
    request: Request,
    question: str = Form(...),
    context: str = Form(default="general"),
    image: Optional[str] = Form(None),
    image_type: Optional[str] = Form(None)
):
    """
    🛡️ SECURED: Analyze screenshot using Gemini Vision API
    Context-aware responses for MetaMask setup guidance
    
    Security Gates:
    1. Validate question text
    2. Scan image for malicious content
    3. Check extracted text from image
    4. Filter output
    """
    queen = request.app.state.queen
    
    try:
        # Get user ID
        user_id = request.state.user_id if hasattr(request.state, 'user_id') else f"anon_{hash(str(request.client))}"
        
        # === SECURITY GATE 1: Validate Question Text ===
        security_bee = get_security_bee()
        
        question_check = await security_bee.execute({
            "type": "validate_llm_input",
            "input": question,
            "user_id": user_id,
            "endpoint": "teacher_bee",
            "critical": False,
            "generates_code": False
        })
        
        decision = question_check.get("decision")
        risk_score = question_check.get("risk_score", 0)
        
        if decision == "BLOCK":
            logger.warning(
                "Teacher Bee question BLOCKED",
                user_id=user_id,
                risk_score=risk_score
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Your question was blocked by security",
                    "message": "Please rephrase without special instructions."
                }
            )
        
        elif decision == "QUARANTINE":
            return {
                "success": False,
                "response": "Your question is under security review. Please try a different question.",
                "quarantined": True
            }
        
        # Use sanitized question
        safe_question = question_check.get("sanitized_input")
        
        # === SECURITY GATE 2: Scan Image (if provided) ===
        image_safe = True
        extracted_text = None
        
        if image and image_type:
            # Scan image for security threats
            image_scan = await security_bee.execute({
                "type": "scan_image",
                "image_data": image,  # Base64 string
                "user_id": user_id
            })
            
            image_safe = image_scan.get("is_safe", False)
            image_risk = image_scan.get("risk_score", 0)
            extracted_text = image_scan.get("extracted_text")
            
            if not image_safe:
                logger.error(
                    "Teacher Bee image BLOCKED",
                    user_id=user_id,
                    risk_score=image_risk,
                    issues=image_scan.get("issues", [])
                )
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Image failed security check",
                        "issues": image_scan.get("issues", [])[:3],
                        "message": "Please upload a different image."
                    }
                )
            
            # Log if text was extracted
            if extracted_text:
                logger.info(
                    "Text extracted from image",
                    user_id=user_id,
                    text_length=len(extracted_text)
                )
        
        # Get Gemini provider with vision support
        llm = queen.llm
        
        if not llm or not llm.providers.get("gemini"):
            logger.warning("Gemini not available, using fallback")
            return await _generate_fallback_response(safe_question, context)
        
        # Prepare context-specific system message
        system_message = _get_system_message(context)
        
        # If image provided and safe, use Gemini Vision
        if image and image_type and image_safe:
            try:
                # Gemini Vision analysis
                prompt = f"""{system_message}

User's Question: {safe_question}

Analyze the screenshot and provide specific, helpful guidance based on what you see.
Be encouraging, clear, and actionable. Use emojis appropriately.

If you see:
- MetaMask installation page → Guide them through installation
- MetaMask setup wizard → Help with current step
- Error messages → Explain what's wrong and how to fix
- Recovery phrase → Emphasize security (never share!)
- Confirmation screen → Congratulate and guide next steps

Keep response concise and friendly."""

                # Call Gemini with vision (using Queen's LLM abstraction)
                response = await llm.generate_with_vision(
                    prompt=prompt,
                    image_base64=image,
                    model="gemini-2.0-flash"  # Vision-capable model
                )
                
                # === SECURITY GATE 4: Filter Output ===
                output_check = await security_bee.execute({
                    "type": "filter_llm_output",
                    "output": response,
                    "mask_pii": True
                })
                
                filtered_response = output_check.get("filtered_output")
                
                logger.info(
                    "Gemini Vision analysis complete",
                    user_id=user_id,
                    question_risk=risk_score,
                    image_risk=image_risk
                )
                
                return {
                    "success": True,
                    "response": filtered_response,
                    "analyzed_image": True,
                    "security": {
                        "image_scanned": True,
                        "text_extracted": extracted_text is not None,
                        "risk_score": max(risk_score, image_risk)
                    }
                }
                
            except Exception as vision_error:
                logger.error("Gemini Vision error", error=str(vision_error))
                # Fall back to text-only response
                pass
        
        # Text-only response (no image or vision failed)
        prompt = f"""{system_message}

User's Question: {safe_question}

Provide helpful, encouraging guidance based on the question.
Be specific, actionable, and friendly. Use emojis."""

        response = await llm.generate(
            prompt=prompt,
            model="gemini-2.0-flash",
            max_tokens=500
        )
        
        # Filter output
        output_check = await security_bee.execute({
            "type": "filter_llm_output",
            "output": response,
            "mask_pii": True
        })
        
        filtered_response = output_check.get("filtered_output")
        
        return {
            "success": True,
            "response": filtered_response,
            "analyzed_image": False,
            "security": {
                "risk_score": risk_score
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Teacher Bee analysis error", error=str(e))
        return await _generate_fallback_response(question, context)

def _get_system_message(context: str) -> str:
    """Get context-specific system message for Teacher Bee"""
    
    base_message = """You are Teacher Bee 🐝, a friendly Web3 learning assistant for Omakh.
Your role is to help users set up their first cryptocurrency wallet and understand blockchain.

Guidelines:
- Be encouraging and patient (many users are new to crypto)
- Use simple language, avoid jargon
- Give step-by-step instructions
- Use emojis to make it friendly (🦊 for MetaMask, ✅ for success, ⚠️ for warnings)
- Emphasize security for recovery phrases
- Be specific and actionable"""
    
    context_specific = {
        "metamask_setup": """

**Current Context: MetaMask Setup**
The user is setting up their first MetaMask wallet. They may be stuck on:
- Step 1: Installing the browser extension
- Step 2: Creating a new wallet with password
- Step 3: Saving the 12-word recovery phrase (MOST CRITICAL!)
- Step 4: Confirming the recovery phrase
- Step 5: Wallet creation complete

If analyzing a screenshot:
- Identify which step they're on
- Point out specific elements they should click
- Warn about security if you see recovery phrase exposed
- Congratulate progress and encourage completion""",
        
        "wallet_security": """

**Current Context: Wallet Security**
Focus on security best practices:
- Recovery phrase should NEVER be shared
- No screenshots, no cloud storage
- Write on paper only
- Beware of fake support asking for phrases
- Use strong passwords""",
        
        "token_purchase": """

**Current Context: Token Purchase**
Help with buying OMK tokens:
- Wallet must be connected first
- Explain gas fees simply
- Guide through transaction approval
- What to expect after purchase""",
    }
    
    return base_message + context_specific.get(context, "")

async def _generate_fallback_response(question: str, context: str) -> dict:
    """Generate helpful fallback response without Gemini"""
    
    question_lower = question.lower()
    
    # MetaMask setup responses
    if "step 1" in question_lower or "install" in question_lower:
        response = """🦊 **Installing MetaMask:**

1. Go to metamask.io/download
2. Click the button for your browser (Chrome, Firefox, Brave)
3. Click "Add to [Browser]"
4. Look for the 🦊 fox icon in your toolbar!

**Can't find the icon?**
- Try closing and reopening your browser
- Check your browser's extensions menu
- Make sure pop-ups aren't blocked

Let me know when you see the fox icon! 🦊"""
    
    elif "step 2" in question_lower or "create" in question_lower or "password" in question_lower:
        response = """🔐 **Creating Your Wallet:**

1. Click the 🦊 MetaMask icon in your toolbar
2. Click "Create a new wallet"
3. Agree to the terms
4. Create a **strong password**:
   - At least 8 characters
   - Mix of letters, numbers, symbols
   - Write it down somewhere safe!
5. Click "Create"

**Important:** You'll need this password every time you use MetaMask.

What do you see on screen now?"""
    
    elif "step 3" in question_lower or "recovery" in question_lower or "phrase" in question_lower or "seed" in question_lower:
        response = """⚠️ **CRITICAL: Saving Your Recovery Phrase!**

This is the **most important step**! Your 12-word recovery phrase is like a master password.

**Do this:**
1. Click "Reveal Secret Recovery Phrase"
2. Write down ALL 12 words on paper (in order!)
3. Store the paper somewhere safe

**⚠️ NEVER EVER:**
❌ Take a screenshot
❌ Save in email/cloud
❌ Share with anyone (not even Omakh support!)
❌ Type on your computer

**Why?** Anyone with these 12 words can steal all your tokens!

Have you written them down on paper? Don't proceed without doing this! 🐝"""
    
    elif "step 4" in question_lower or "confirm" in question_lower:
        response = """✅ **Confirming Your Phrase:**

MetaMask will test you to make sure you saved it correctly.

1. You'll see your 12 words jumbled below
2. Click them in the correct order (1, 2, 3... 12)
3. Click "Confirm"

**Stuck?**
- Check your paper with the words
- They need to be in the exact order you wrote them
- If you make a mistake, MetaMask lets you try again!

Click them in YOUR order from the paper! 📝"""
    
    elif "step 5" in question_lower or "done" in question_lower or "complete" in question_lower:
        response = """🎉 **Congratulations! Wallet Created!**

You now have your own MetaMask wallet! 

**Your wallet address:**
- Starts with "0x..."
- This is like your crypto bank account number
- You can share this address to receive tokens

**Next steps:**
1. Keep your recovery phrase safe
2. Remember your password
3. You're ready to connect to Omakh and get OMK tokens!

Ready to connect your wallet? 🚀"""
    
    else:
        response = """🐝 **I'm here to help with MetaMask setup!**

Can you tell me:
• Which step are you on? (1-5)
• What do you see on your screen?
• Is there an error message?

**The 5 steps are:**
1. Install MetaMask
2. Create your wallet
3. Save recovery phrase (most important!)
4. Confirm your phrase
5. Done!

Where are you stuck? I'll guide you through! 🦊"""
    
    return {
        "success": True,
        "response": response,
        "fallback": True
    }
