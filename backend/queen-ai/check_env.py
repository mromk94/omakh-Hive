#!/usr/bin/env python3
"""
Environment Configuration Checker

Validates .env file without exposing sensitive values.
"""
import os
from pathlib import Path
from dotenv import load_dotenv


def check_env():
    """Check .env configuration"""
    env_path = Path(__file__).parent / ".env"
    
    print("=" * 70)
    print("  OMK HIVE - ENVIRONMENT CONFIGURATION CHECK")
    print("=" * 70)
    print()
    
    # Check if .env exists
    if not env_path.exists():
        print("❌ .env file not found!")
        print(f"   Expected location: {env_path}")
        print()
        print("To create .env file:")
        print("  1. Run: python3 setup_env.py")
        print("  2. OR copy: cp .env.example .env")
        print("  3. Then edit .env with your API keys")
        return False
    
    print(f"✅ .env file found at: {env_path}")
    print(f"   Size: {env_path.stat().st_size} bytes")
    print()
    
    # Load environment variables
    load_dotenv(env_path)
    
    # Check critical variables
    print("🔍 CHECKING CONFIGURATION...")
    print("=" * 70)
    print()
    
    issues = []
    warnings = []
    success = []
    
    # 1. Environment
    environment = os.getenv("ENVIRONMENT", "")
    if environment:
        success.append(f"✅ ENVIRONMENT: {environment}")
    else:
        warnings.append("⚠️  ENVIRONMENT not set (defaulting to 'development')")
    
    # 2. LLM Provider (CRITICAL)
    default_llm = os.getenv("DEFAULT_LLM_PROVIDER", "")
    if default_llm:
        success.append(f"✅ DEFAULT_LLM_PROVIDER: {default_llm}")
    else:
        issues.append("❌ DEFAULT_LLM_PROVIDER not set!")
    
    # 3. LLM API Keys (AT LEAST ONE REQUIRED)
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    grok_key = os.getenv("GROK_API_KEY", "")
    
    llm_keys_found = []
    
    if gemini_key:
        masked = gemini_key[:8] + "..." + gemini_key[-4:] if len(gemini_key) > 12 else "***"
        llm_keys_found.append("Gemini")
        success.append(f"✅ GEMINI_API_KEY: {masked}")
    else:
        warnings.append("⚠️  GEMINI_API_KEY not set")
    
    if openai_key:
        masked = openai_key[:8] + "..." + openai_key[-4:] if len(openai_key) > 12 else "***"
        llm_keys_found.append("OpenAI")
        success.append(f"✅ OPENAI_API_KEY: {masked}")
    else:
        warnings.append("⚠️  OPENAI_API_KEY not set")
    
    if anthropic_key:
        masked = anthropic_key[:8] + "..." + anthropic_key[-4:] if len(anthropic_key) > 12 else "***"
        llm_keys_found.append("Anthropic")
        success.append(f"✅ ANTHROPIC_API_KEY: {masked}")
    else:
        warnings.append("⚠️  ANTHROPIC_API_KEY not set")
    
    if not llm_keys_found:
        issues.append("❌ NO LLM API KEYS FOUND! At least ONE is required!")
        issues.append("   Get Gemini API key (free): https://makersuite.google.com/app/apikey")
    
    # Check if default provider has key
    if default_llm == "gemini" and not gemini_key:
        issues.append(f"❌ DEFAULT_LLM_PROVIDER is 'gemini' but GEMINI_API_KEY is not set!")
    elif default_llm == "openai" and not openai_key:
        issues.append(f"❌ DEFAULT_LLM_PROVIDER is 'openai' but OPENAI_API_KEY is not set!")
    elif default_llm == "anthropic" and not anthropic_key:
        issues.append(f"❌ DEFAULT_LLM_PROVIDER is 'anthropic' but ANTHROPIC_API_KEY is not set!")
    
    # 4. Database
    db_url = os.getenv("DATABASE_URL", "")
    if db_url:
        # Mask password
        if "@" in db_url:
            parts = db_url.split("@")
            masked_db = parts[0].split(":")[0] + ":***@" + parts[1]
        else:
            masked_db = db_url
        success.append(f"✅ DATABASE_URL: {masked_db}")
    else:
        warnings.append("⚠️  DATABASE_URL not set (will use in-memory)")
    
    # 5. Redis
    redis_url = os.getenv("REDIS_URL", "")
    message_bus_type = os.getenv("MESSAGE_BUS_TYPE", "memory")
    
    if redis_url:
        success.append(f"✅ REDIS_URL: {redis_url}")
        success.append(f"✅ MESSAGE_BUS_TYPE: {message_bus_type}")
    else:
        warnings.append(f"⚠️  REDIS_URL not set (using MESSAGE_BUS_TYPE={message_bus_type})")
    
    # 6. Blockchain (optional)
    eth_rpc = os.getenv("ETHEREUM_RPC_URL", "")
    if eth_rpc:
        success.append(f"✅ ETHEREUM_RPC_URL: {eth_rpc[:30]}...")
    
    # 7. GCP (optional)
    gcp_project = os.getenv("GCP_PROJECT_ID", "")
    if gcp_project:
        success.append(f"✅ GCP_PROJECT_ID: {gcp_project}")
    
    # Print results
    if success:
        print("✅ CONFIGURED:")
        for item in success:
            print(f"   {item}")
        print()
    
    if warnings:
        print("⚠️  WARNINGS:")
        for item in warnings:
            print(f"   {item}")
        print()
    
    if issues:
        print("❌ CRITICAL ISSUES:")
        for item in issues:
            print(f"   {item}")
        print()
    
    # Summary
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print()
    
    if llm_keys_found:
        print(f"✅ LLM Providers Configured: {', '.join(llm_keys_found)}")
    else:
        print("❌ NO LLM Providers Configured!")
    
    print(f"   Default Provider: {default_llm or 'NOT SET'}")
    print()
    
    if issues:
        print("❌ CONFIGURATION INVALID - SYSTEM WILL NOT WORK!")
        print()
        print("🔧 TO FIX:")
        print("   1. Get a Gemini API key (free):")
        print("      https://makersuite.google.com/app/apikey")
        print()
        print("   2. Edit your .env file:")
        print(f"      nano {env_path}")
        print()
        print("   3. Add the line:")
        print("      GEMINI_API_KEY=your_actual_api_key_here")
        print()
        print("   4. Or run the setup script:")
        print("      python3 setup_env.py")
        print()
        return False
    
    elif warnings:
        print("⚠️  CONFIGURATION VALID BUT HAS WARNINGS")
        print("   System will work but some features may be limited.")
        print()
        return True
    
    else:
        print("✅ CONFIGURATION IS PERFECT!")
        print()
        return True


if __name__ == "__main__":
    try:
        valid = check_env()
        
        if valid:
            print("=" * 70)
            print("🚀 READY TO START")
            print("=" * 70)
            print()
            print("Start the system with:")
            print("  python3 manage.py start")
            print()
            print("Or test individual components:")
            print("  python3 manage.py health")
            print()
    
    except Exception as e:
        print(f"\n❌ Error checking environment: {str(e)}")
        import traceback
        traceback.print_exc()
