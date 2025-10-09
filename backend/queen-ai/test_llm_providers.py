#!/usr/bin/env python3
"""
LLM Provider Test

Tests which LLM providers are working with your current API keys.
"""
import asyncio
import os
from dotenv import load_dotenv


async def test_llm_providers():
    """Test all configured LLM providers"""
    load_dotenv()
    
    print("=" * 70)
    print("  LLM PROVIDER CONNECTION TEST")
    print("=" * 70)
    print()
    
    results = {}
    
    # Test Gemini
    print("1️⃣  Testing Gemini...")
    print("-" * 70)
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    
    if not gemini_key or gemini_key.startswith("your_"):
        print("❌ GEMINI_API_KEY is a placeholder or not set")
        print("   Current value starts with: 'your_'")
        print("   Get a real API key at: https://makersuite.google.com/app/apikey")
        results['gemini'] = False
    else:
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=gemini_key)
            
            # Try different model names (API versions change)
            model_names = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-pro-latest']
            
            for model_name in model_names:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = await asyncio.to_thread(
                        model.generate_content,
                        "Say 'Hello from Gemini!' in exactly 3 words"
                    )
                    
                    print(f"✅ Gemini is working!")
                    print(f"   Model: {model_name}")
                    print(f"   Response: {response.text}")
                    results['gemini'] = True
                    break
                except Exception as e:
                    if "not found" in str(e):
                        continue  # Try next model
                    else:
                        raise  # Other error, re-raise
            
            if not results.get('gemini'):
                raise Exception("No Gemini models available")
            
        except Exception as e:
            print(f"❌ Gemini failed: {str(e)}")
            if "API_KEY_INVALID" in str(e) or "API key not valid" in str(e):
                print("   → Your GEMINI_API_KEY is invalid")
                print("   → Get a valid key at: https://makersuite.google.com/app/apikey")
            results['gemini'] = False
    
    print()
    
    # Test OpenAI
    print("2️⃣  Testing OpenAI...")
    print("-" * 70)
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    if not openai_key or openai_key.startswith("your_"):
        print("❌ OPENAI_API_KEY is a placeholder or not set")
        results['openai'] = False
    else:
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=openai_key)
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'Hello from OpenAI!' in exactly 3 words"}],
                max_tokens=10
            )
            
            print(f"✅ OpenAI is working!")
            print(f"   Response: {response.choices[0].message.content}")
            results['openai'] = True
            
        except Exception as e:
            print(f"❌ OpenAI failed: {str(e)}")
            if "Incorrect API key" in str(e) or "invalid_api_key" in str(e):
                print("   → Your OPENAI_API_KEY is invalid")
                print("   → Get a valid key at: https://platform.openai.com/api-keys")
            results['openai'] = False
    
    print()
    
    # Test Anthropic
    print("3️⃣  Testing Anthropic...")
    print("-" * 70)
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    if not anthropic_key or anthropic_key.startswith("your_"):
        print("❌ ANTHROPIC_API_KEY is a placeholder or not set")
        results['anthropic'] = False
    else:
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(api_key=anthropic_key)
            
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "Say 'Hello from Claude!' in exactly 3 words"}]
            )
            
            print(f"✅ Anthropic is working!")
            print(f"   Response: {response.content[0].text}")
            results['anthropic'] = True
            
        except Exception as e:
            print(f"❌ Anthropic failed: {str(e)}")
            if "invalid_api_key" in str(e) or "authentication" in str(e).lower():
                print("   → Your ANTHROPIC_API_KEY is invalid")
                print("   → Get a valid key at: https://console.anthropic.com/settings/keys")
            results['anthropic'] = False
    
    print()
    
    # Summary
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print()
    
    working_providers = [name for name, status in results.items() if status]
    failed_providers = [name for name, status in results.items() if not status]
    
    if working_providers:
        print(f"✅ Working Providers: {', '.join(working_providers).upper()}")
    else:
        print("❌ NO WORKING PROVIDERS!")
    
    if failed_providers:
        print(f"❌ Failed Providers: {', '.join(failed_providers).upper()}")
    
    print()
    
    # Check default provider
    default_llm = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
    print(f"Default Provider: {default_llm.upper()}")
    
    if default_llm in results and results[default_llm]:
        print(f"✅ Your default provider ({default_llm}) is working!")
    else:
        print(f"❌ Your default provider ({default_llm}) is NOT working!")
        
        if working_providers:
            print(f"\n💡 RECOMMENDATION:")
            print(f"   Change DEFAULT_LLM_PROVIDER to: {working_providers[0]}")
            print(f"   Edit your .env file and set:")
            print(f"   DEFAULT_LLM_PROVIDER={working_providers[0]}")
    
    print()
    
    # Instructions
    if not working_providers:
        print("=" * 70)
        print("🔧 HOW TO FIX")
        print("=" * 70)
        print()
        print("You need at least ONE valid LLM API key.")
        print()
        print("EASIEST OPTION - Gemini (Free):")
        print("  1. Go to: https://makersuite.google.com/app/apikey")
        print("  2. Click 'Create API Key'")
        print("  3. Copy the key")
        print("  4. Edit .env file:")
        print("     nano .env")
        print("  5. Replace the line:")
        print("     GEMINI_API_KEY=your_gemini_api_key")
        print("     with:")
        print("     GEMINI_API_KEY=<paste_your_actual_key_here>")
        print("  6. Save and re-run this test")
        print()
    
    return working_providers


if __name__ == "__main__":
    try:
        working = asyncio.run(test_llm_providers())
        
        if working:
            print("=" * 70)
            print("✅ SYSTEM CAN START")
            print("=" * 70)
            print()
            print("You can now start the OMK Hive:")
            print("  python3 manage.py start")
            print()
        else:
            print("=" * 70)
            print("❌ SYSTEM CANNOT START")
            print("=" * 70)
            print()
            print("Fix the API keys first, then try again.")
            print()
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
