"""
Test Claude Development Chat - System Analysis Request
Tests the secured Claude endpoint and its analysis capabilities
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / "backend" / "queen-ai" / ".env"
load_dotenv(env_path)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "queen-ai"))

from app.integrations.claude_integration import ClaudeQueenIntegration
from app.bees.enhanced_security_bee import EnhancedSecurityBee


async def test_claude_system_analysis():
    """Test Claude's system analysis with security validation"""
    
    print("=" * 80)
    print("🧪 TESTING CLAUDE DEVELOPMENT CHAT - SYSTEM ANALYSIS")
    print("=" * 80)
    print()
    
    # Initialize components
    print("📦 Initializing security bee...")
    security_bee = EnhancedSecurityBee()
    
    print("📦 Initializing Claude integration...")
    claude = ClaudeQueenIntegration()
    
    # Test message
    test_message = """
    Analyze the OMK Hive backend system architecture with focus on:
    
    1. **Data Flow Efficiency**: How data flows from API endpoints → Bees → LLM providers
    2. **Information Flow**: Request/response patterns and potential bottlenecks
    3. **Security Integration**: Where the new security gates are integrated
    4. **Bee Coordination**: How the bee manager coordinates tasks
    5. **LLM Integration**: Multi-provider setup (Gemini, Claude, OpenAI)
    
    Provide a comprehensive technical analysis of the system's architecture,
    identifying strengths, potential bottlenecks, and efficiency recommendations.
    """
    
    print("\n📝 Test Message:")
    print("-" * 80)
    print(test_message.strip())
    print("-" * 80)
    print()
    
    # === SECURITY GATE 1-3: Input Validation ===
    print("🛡️  PHASE 1: Security Validation")
    print("-" * 80)
    
    security_check = await security_bee.execute({
        "type": "validate_llm_input",
        "input": test_message,
        "user_id": "test_admin",
        "endpoint": "queen_dev_chat",
        "critical": True,
        "generates_code": True
    })
    
    decision = security_check.get("decision")
    risk_score = security_check.get("risk_score", 0)
    
    print(f"Decision: {decision}")
    print(f"Risk Score: {risk_score}/100")
    print(f"Reasoning: {security_check.get('reasoning', 'N/A')}")
    
    if decision == "BLOCK":
        print("\n❌ Message BLOCKED by security")
        return
    elif decision == "QUARANTINE":
        print("\n⚠️  Message QUARANTINED for review")
        return
    
    print("\n✅ Security validation passed - proceeding to Claude")
    print()
    
    # === PHASE 2: Claude Analysis ===
    print("🤖 PHASE 2: Claude System Analysis")
    print("-" * 80)
    
    sanitized_message = security_check.get("sanitized_input")
    
    try:
        print("📡 Sending request to Claude API...")
        response = await claude.chat(
            message=sanitized_message,
            include_system_info=True
        )
        
        print("✅ Response received from Claude")
        print()
        
        # === PHASE 3: Output Filtering ===
        print("🛡️  PHASE 3: Output Filtering")
        print("-" * 80)
        
        output_check = await security_bee.execute({
            "type": "filter_llm_output",
            "output": response.get("response", ""),
            "mask_pii": False,
            "validate_code": True
        })
        
        filtered_response = output_check.get("filtered_output")
        warnings = output_check.get("warnings", [])
        
        if warnings:
            print(f"⚠️  Output warnings: {warnings}")
        else:
            print("✅ Output clean - no secrets or malicious patterns")
        
        print()
        
        # === DISPLAY RESULTS ===
        print("=" * 80)
        print("📊 CLAUDE'S SYSTEM ANALYSIS")
        print("=" * 80)
        print()
        print(filtered_response)
        print()
        print("=" * 80)
        print()
        
        # Save results
        print("💾 Saving analysis results...")
        output_file = Path(__file__).parent / "CLAUDE_SYSTEM_ANALYSIS.md"
        with open(output_file, "w") as f:
            f.write("# Claude System Analysis - OMK Hive Backend\n\n")
            f.write(f"**Date:** {response.get('timestamp', 'N/A')}\n")
            f.write(f"**Tokens Used:** {response.get('tokens_used', 'N/A')}\n")
            f.write(f"**Security Risk Score:** {risk_score}/100\n")
            f.write(f"**Security Decision:** {decision}\n\n")
            f.write("---\n\n")
            f.write("## Analysis\n\n")
            f.write(filtered_response)
            f.write("\n\n---\n\n")
            f.write("## Security Notes\n\n")
            f.write(f"- Input validated through 3-gate security mesh\n")
            f.write(f"- Risk score: {risk_score}/100 (threshold: 30 for critical endpoints)\n")
            f.write(f"- Output filtered for secrets and malicious patterns\n")
            if warnings:
                f.write(f"- Warnings: {', '.join(warnings)}\n")
        
        print(f"✅ Results saved to: {output_file}")
        print()
        
        # === TEST SUMMARY ===
        print("=" * 80)
        print("📋 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Security Validation: PASSED (risk: {risk_score}/100)")
        print(f"✅ Claude Integration: WORKING")
        print(f"✅ Output Filtering: PASSED")
        print(f"✅ Response Length: {len(filtered_response)} characters")
        print(f"✅ Tokens Used: {response.get('tokens_used', 'N/A')}")
        print()
        print("🎉 All systems operational!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during Claude communication: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print()
    asyncio.run(test_claude_system_analysis())
    print()
