"""
Test Claude Development Chat - Can Claude Actually Develop?
Tests if Claude can implement its own recommendations
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
import time
import re

# Load environment variables
env_path = Path(__file__).parent / "backend" / "queen-ai" / ".env"
load_dotenv(env_path)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "queen-ai"))

from app.integrations.claude_integration import ClaudeQueenIntegration
from app.bees.enhanced_security_bee import EnhancedSecurityBee


async def test_claude_can_develop():
    """Test if Claude can actually implement code based on its own analysis"""
    
    print("=" * 80)
    print("🧪 TESTING: CAN CLAUDE ACTUALLY DEVELOP?")
    print("=" * 80)
    print()
    
    # Initialize
    print("📦 Initializing components...")
    security_bee = EnhancedSecurityBee()
    claude = ClaudeQueenIntegration()
    print("✅ Components initialized")
    print()
    
    # Test: Ask Claude to implement security context propagation
    test_request = """
Based on your previous system analysis, you recommended implementing "Security Context Propagation"
to create a shared security context across the system for a 50% reduction in security overhead.

Now implement this recommendation. Provide:

1. Complete Python code for the SecurityContextPropagation class
2. Integration points with existing SecurityContextManager
3. How it should be used in the EnhancedSecurityBee
4. Unit tests
5. Expected performance improvement measurement

Requirements:
- Must be production-ready Python code
- Must integrate with existing security system
- Must include proper error handling
- Must be thread-safe for async operations
- Must include docstrings

Generate the complete implementation now.
"""
    
    print("📝 Development Request:")
    print("-" * 80)
    print(test_request.strip())
    print("-" * 80)
    print()
    
    # === PHASE 1: Security Validation ===
    print("🛡️  PHASE 1: Security Validation")
    print("-" * 80)
    
    start_security = time.time()
    security_check = await security_bee.execute({
        "type": "validate_llm_input",
        "input": test_request,
        "user_id": "test_developer",
        "endpoint": "claude_development_test",
        "critical": True,
        "generates_code": True
    })
    security_time = (time.time() - start_security) * 1000
    
    decision = security_check.get("decision")
    risk_score = security_check.get("risk_score", 0)
    
    print(f"Decision: {decision}")
    print(f"Risk Score: {risk_score}/100")
    print(f"Time: {security_time:.2f}ms")
    
    if decision != "ALLOW":
        print(f"\n❌ Request BLOCKED by security")
        return
    
    print("\n✅ Security validation passed")
    print()
    
    # === PHASE 2: Claude Implementation ===
    print("🤖 PHASE 2: Claude Code Generation")
    print("-" * 80)
    
    sanitized = security_check.get("sanitized_input")
    
    try:
        print("📡 Requesting implementation from Claude...")
        start_claude = time.time()
        
        response = await claude.chat(
            message=sanitized,
            include_system_info=True
        )
        
        claude_time = (time.time() - start_claude) * 1000
        
        print(f"✅ Response received in {claude_time:.2f}ms")
        print()
        
        # === PHASE 3: Code Validation ===
        print("🛡️  PHASE 3: Code Security Validation")
        print("-" * 80)
        
        start_output = time.time()
        output_check = await security_bee.execute({
            "type": "filter_llm_output",
            "output": response.get("response", ""),
            "validate_code": True
        })
        output_time = (time.time() - start_output) * 1000
        
        is_safe = output_check.get("is_safe", False)
        warnings = output_check.get("warnings", [])
        filtered = output_check.get("filtered_output")
        
        print(f"Code Safety: {'✅ SAFE' if is_safe else '❌ UNSAFE'}")
        print(f"Time: {output_time:.2f}ms")
        
        if warnings:
            print(f"⚠️  Warnings: {', '.join(warnings)}")
        else:
            print("✅ No security warnings")
        
        if not is_safe:
            print("\n❌ Generated code failed security validation")
            return
        
        print()
        
        # === PHASE 4: Code Analysis ===
        print("📊 PHASE 4: Implementation Analysis")
        print("-" * 80)
        
        # Extract code blocks
        code_blocks = re.findall(r'```python\n(.*?)```', filtered, re.DOTALL)
        
        # Count classes, functions, tests
        classes = len(re.findall(r'class\s+\w+', filtered))
        functions = len(re.findall(r'def\s+\w+', filtered))
        async_functions = len(re.findall(r'async\s+def\s+\w+', filtered))
        test_functions = len(re.findall(r'def\s+test_\w+', filtered))
        docstrings = len(re.findall(r'""".*?"""', filtered, re.DOTALL))
        imports = len(re.findall(r'^import\s+|^from\s+.*\s+import', filtered, re.MULTILINE))
        
        print(f"Code Blocks Found: {len(code_blocks)}")
        print(f"Classes Defined: {classes}")
        print(f"Functions Defined: {functions}")
        print(f"Async Functions: {async_functions}")
        print(f"Test Functions: {test_functions}")
        print(f"Docstrings: {docstrings}")
        print(f"Import Statements: {imports}")
        print()
        
        # === DISPLAY GENERATED CODE ===
        print("=" * 80)
        print("📝 GENERATED IMPLEMENTATION")
        print("=" * 80)
        print()
        print(filtered)
        print()
        print("=" * 80)
        print()
        
        # === SAVE IMPLEMENTATION ===
        output_file = Path(__file__).parent / "CLAUDE_SECURITY_CONTEXT_PROPAGATION_IMPL.md"
        with open(output_file, 'w') as f:
            f.write("# Claude Implementation: Security Context Propagation\n\n")
            f.write(f"**Generated:** {response.get('timestamp', 'N/A')}\n")
            f.write(f"**Tokens Used:** {response.get('tokens_used', 'N/A')}\n")
            f.write(f"**Security Validated:** ✅ YES\n\n")
            f.write("---\n\n")
            f.write("## Generated Code\n\n")
            f.write(filtered)
        
        print(f"💾 Implementation saved to: {output_file}")
        print()
        
        # === PHASE 5: Quality Assessment ===
        print("🎯 PHASE 5: Quality Assessment")
        print("-" * 80)
        
        # Quality checks
        checks = {
            "Has classes": classes > 0,
            "Has functions": functions > 0,
            "Has async support": async_functions > 0,
            "Has tests": test_functions > 0,
            "Has docstrings": docstrings > 0,
            "Has imports": imports > 0,
            "Has code blocks": len(code_blocks) > 0,
            "Code is safe": is_safe,
        }
        
        passed = sum(checks.values())
        total = len(checks)
        quality_score = (passed / total) * 100
        
        print("Quality Checks:")
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}")
        
        print()
        print(f"Quality Score: {quality_score:.0f}% ({passed}/{total} checks passed)")
        print()
        
        # === PHASE 6: Verification Test ===
        print("🧪 PHASE 6: Implementation Verification")
        print("-" * 80)
        
        # Check if code can be parsed (syntax check)
        syntax_valid = True
        for i, code_block in enumerate(code_blocks):
            try:
                compile(code_block, f'<code_block_{i}>', 'exec')
                print(f"✅ Code block {i+1}: Syntax valid")
            except SyntaxError as e:
                print(f"❌ Code block {i+1}: Syntax error - {e}")
                syntax_valid = False
        
        if not code_blocks:
            print("⚠️  No Python code blocks found in response")
            syntax_valid = False
        
        print()
        
        # === FINAL SUMMARY ===
        print("=" * 80)
        print("📋 TEST SUMMARY: CAN CLAUDE DEVELOP?")
        print("=" * 80)
        
        total_time = security_time + claude_time + output_time
        
        print(f"\n⏱️  PERFORMANCE:")
        print(f"  Security Validation: {security_time:.2f}ms")
        print(f"  Claude Generation: {claude_time:.2f}ms")
        print(f"  Output Validation: {output_time:.2f}ms")
        print(f"  Total: {total_time:.2f}ms")
        
        print(f"\n📊 CODE METRICS:")
        print(f"  Response Length: {len(filtered)} characters")
        print(f"  Code Blocks: {len(code_blocks)}")
        print(f"  Classes: {classes}")
        print(f"  Functions: {functions} ({async_functions} async)")
        print(f"  Tests: {test_functions}")
        print(f"  Docstrings: {docstrings}")
        
        print(f"\n✅ QUALITY:")
        print(f"  Quality Score: {quality_score:.0f}%")
        print(f"  Syntax Valid: {'✅ YES' if syntax_valid else '❌ NO'}")
        print(f"  Security Safe: {'✅ YES' if is_safe else '❌ NO'}")
        
        print(f"\n🎯 VERDICT:")
        
        # Calculate overall success
        development_capable = (
            quality_score >= 75 and
            syntax_valid and
            is_safe and
            classes > 0 and
            functions > 0
        )
        
        if development_capable:
            print("  ✅ CLAUDE CAN DEVELOP!")
            print("  Claude successfully generated production-ready code")
            print("  that passed security validation and quality checks.")
        else:
            print("  ⚠️  CLAUDE NEEDS IMPROVEMENT")
            print("  Code generated but quality/security concerns exist.")
        
        print()
        print("=" * 80)
        
        return {
            "success": development_capable,
            "quality_score": quality_score,
            "syntax_valid": syntax_valid,
            "security_safe": is_safe,
            "code_blocks": len(code_blocks),
            "classes": classes,
            "functions": functions,
            "tests": test_functions,
            "total_time": total_time
        }
        
    except Exception as e:
        print(f"\n❌ Error during development test: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print()
    result = asyncio.run(test_claude_can_develop())
    print()
    
    if result:
        sys.exit(0 if result["success"] else 1)
    else:
        sys.exit(1)
