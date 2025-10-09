#!/usr/bin/env python3
"""
Environment Setup Script

Helps configure .env file with API keys and settings.
"""
import os
from pathlib import Path


def setup_env():
    """Interactive .env file setup"""
    env_path = Path(__file__).parent / ".env"
    env_example_path = Path(__file__).parent / ".env.example"
    
    print("=" * 70)
    print("  OMK HIVE - ENVIRONMENT SETUP")
    print("=" * 70)
    print()
    
    # Check if .env exists
    if env_path.exists():
        print(f"⚠️  .env file already exists at: {env_path}")
        response = input("Do you want to update it? (y/n): ").lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📝 Let's configure your environment variables...\n")
    
    # Read current .env if it exists
    current_env = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    current_env[key] = value
    
    # Configuration sections
    config = {}
    
    # 1. Environment
    print("1️⃣  ENVIRONMENT SETTINGS")
    print("-" * 70)
    environment = input(f"Environment (development/staging/production) [{current_env.get('ENVIRONMENT', 'development')}]: ") or current_env.get('ENVIRONMENT', 'development')
    config['ENVIRONMENT'] = environment
    config['DEBUG'] = 'true' if environment == 'development' else 'false'
    config['LOG_LEVEL'] = 'DEBUG' if environment == 'development' else 'INFO'
    print()
    
    # 2. LLM Provider (CRITICAL)
    print("2️⃣  LLM PROVIDER (REQUIRED)")
    print("-" * 70)
    print("At least ONE LLM provider is required for the system to work.")
    print("Recommended: Gemini (free tier: 15 req/min, 1500 req/day)")
    print()
    
    print("Choose your default LLM provider:")
    print("  1. Gemini (Google AI) - RECOMMENDED")
    print("  2. OpenAI (GPT-4/GPT-3.5)")
    print("  3. Anthropic (Claude 3.5)")
    print("  4. Grok (X AI)")
    
    provider_choice = input(f"Enter choice [1-4, default 1]: ") or "1"
    provider_map = {
        "1": "gemini",
        "2": "openai",
        "3": "anthropic",
        "4": "grok"
    }
    config['DEFAULT_LLM_PROVIDER'] = provider_map.get(provider_choice, "gemini")
    print()
    
    # 3. API Keys
    print("3️⃣  API KEYS")
    print("-" * 70)
    print("⚠️  WARNING: Never commit real API keys to git!")
    print()
    
    # Gemini
    print("GEMINI API KEY:")
    print("  Get it at: https://makersuite.google.com/app/apikey")
    print("  Free tier: 15 requests/min, 1500 requests/day")
    gemini_key = input(f"Enter Gemini API key [{current_env.get('GEMINI_API_KEY', '')}]: ") or current_env.get('GEMINI_API_KEY', '')
    config['GEMINI_API_KEY'] = gemini_key
    print()
    
    # OpenAI
    print("OPENAI API KEY (optional):")
    print("  Get it at: https://platform.openai.com/api-keys")
    openai_key = input(f"Enter OpenAI API key [{current_env.get('OPENAI_API_KEY', '')}]: ") or current_env.get('OPENAI_API_KEY', '')
    config['OPENAI_API_KEY'] = openai_key
    print()
    
    # Anthropic
    print("ANTHROPIC API KEY (optional):")
    print("  Get it at: https://console.anthropic.com/settings/keys")
    anthropic_key = input(f"Enter Anthropic API key [{current_env.get('ANTHROPIC_API_KEY', '')}]: ") or current_env.get('ANTHROPIC_API_KEY', '')
    config['ANTHROPIC_API_KEY'] = anthropic_key
    print()
    
    # 4. Database
    print("4️⃣  DATABASE")
    print("-" * 70)
    use_postgres = input("Use PostgreSQL? (y/n, default n - will use in-memory): ").lower() == 'y'
    
    if use_postgres:
        db_user = input("PostgreSQL user [omk_user]: ") or "omk_user"
        db_pass = input("PostgreSQL password [omk_password]: ") or "omk_password"
        db_host = input("PostgreSQL host [localhost]: ") or "localhost"
        db_port = input("PostgreSQL port [5432]: ") or "5432"
        db_name = input("PostgreSQL database [omk_hive]: ") or "omk_hive"
        
        config['DATABASE_URL'] = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    else:
        config['DATABASE_URL'] = "sqlite:///./omk_hive.db"
    print()
    
    # 5. Redis
    print("5️⃣  REDIS")
    print("-" * 70)
    use_redis = input("Use Redis? (y/n, default n - will use in-memory): ").lower() == 'y'
    
    if use_redis:
        redis_host = input("Redis host [localhost]: ") or "localhost"
        redis_port = input("Redis port [6379]: ") or "6379"
        redis_db = input("Redis database [0]: ") or "0"
        
        config['REDIS_URL'] = f"redis://{redis_host}:{redis_port}/{redis_db}"
        config['MESSAGE_BUS_TYPE'] = "redis"
    else:
        config['REDIS_URL'] = ""
        config['MESSAGE_BUS_TYPE'] = "memory"
    print()
    
    # 6. Blockchain (optional)
    print("6️⃣  BLOCKCHAIN (Optional)")
    print("-" * 70)
    configure_blockchain = input("Configure blockchain RPC URLs? (y/n, default n): ").lower() == 'y'
    
    if configure_blockchain:
        eth_rpc = input("Ethereum RPC URL: ") or ""
        config['ETHEREUM_RPC_URL'] = eth_rpc
        
        solana_rpc = input("Solana RPC URL [https://api.mainnet-beta.solana.com]: ") or "https://api.mainnet-beta.solana.com"
        config['SOLANA_RPC_URL'] = solana_rpc
    else:
        config['ETHEREUM_RPC_URL'] = ""
        config['SOLANA_RPC_URL'] = ""
    print()
    
    # 7. Google Cloud (optional)
    print("7️⃣  GOOGLE CLOUD PLATFORM (Optional)")
    print("-" * 70)
    configure_gcp = input("Configure GCP? (y/n, default n): ").lower() == 'y'
    
    if configure_gcp:
        gcp_project = input("GCP Project ID: ") or ""
        config['GCP_PROJECT_ID'] = gcp_project
        
        gcp_location = input("GCP Location [us-central1]: ") or "us-central1"
        config['GCP_LOCATION'] = gcp_location
        
        gcp_creds = input("Path to service account JSON: ") or ""
        config['GOOGLE_APPLICATION_CREDENTIALS'] = gcp_creds
        
        config['BIGQUERY_ENABLED'] = 'true'
        config['BIGQUERY_DATASET'] = 'omk_hive_learning'
        config['LEARNING_FUNCTION_ENABLED'] = 'true'
    else:
        config['GCP_PROJECT_ID'] = ""
        config['GCP_LOCATION'] = "us-central1"
        config['GOOGLE_APPLICATION_CREDENTIALS'] = ""
        config['BIGQUERY_ENABLED'] = 'false'
        config['BIGQUERY_DATASET'] = "omk_hive_learning"
        config['LEARNING_FUNCTION_ENABLED'] = 'false'
    print()
    
    # Add defaults for other settings
    config['LEARNING_BATCH_SIZE'] = '100'
    config['LEARNING_RETENTION_DAYS'] = '365'
    config['SECRET_MANAGER_ENABLED'] = 'false'
    config['FETCH_NETWORK'] = 'testnet'
    config['FETCH_MNEMONIC'] = ''
    config['API_KEY_HEADER'] = 'X-API-Key'
    config['ADMIN_API_KEYS'] = ''
    config['CORS_ORIGINS'] = 'http://localhost:3000,http://localhost:3001'
    config['QUEEN_CONTROLLER_ADDRESS'] = ''
    
    # Write .env file
    print("\n" + "=" * 70)
    print("📝 WRITING .env FILE...")
    print("=" * 70)
    
    with open(env_path, 'w') as f:
        f.write("# OMK HIVE - Environment Configuration\n")
        f.write("# AUTO-GENERATED - DO NOT COMMIT TO GIT\n")
        f.write(f"# Generated: {os.popen('date').read().strip()}\n\n")
        
        f.write("# Application\n")
        f.write(f"ENVIRONMENT={config['ENVIRONMENT']}\n")
        f.write(f"DEBUG={config['DEBUG']}\n")
        f.write(f"LOG_LEVEL={config['LOG_LEVEL']}\n\n")
        
        f.write("# LLM Providers\n")
        f.write(f"DEFAULT_LLM_PROVIDER={config['DEFAULT_LLM_PROVIDER']}\n")
        f.write(f"GEMINI_API_KEY={config['GEMINI_API_KEY']}\n")
        f.write(f"OPENAI_API_KEY={config['OPENAI_API_KEY']}\n")
        f.write(f"ANTHROPIC_API_KEY={config['ANTHROPIC_API_KEY']}\n\n")
        
        f.write("# Database\n")
        f.write(f"DATABASE_URL={config['DATABASE_URL']}\n\n")
        
        f.write("# Redis\n")
        f.write(f"REDIS_URL={config['REDIS_URL']}\n")
        f.write(f"MESSAGE_BUS_TYPE={config['MESSAGE_BUS_TYPE']}\n\n")
        
        f.write("# Blockchain\n")
        f.write(f"ETHEREUM_RPC_URL={config['ETHEREUM_RPC_URL']}\n")
        f.write(f"SOLANA_RPC_URL={config['SOLANA_RPC_URL']}\n")
        f.write(f"QUEEN_CONTROLLER_ADDRESS={config['QUEEN_CONTROLLER_ADDRESS']}\n\n")
        
        f.write("# Google Cloud Platform\n")
        f.write(f"GCP_PROJECT_ID={config['GCP_PROJECT_ID']}\n")
        f.write(f"GCP_LOCATION={config['GCP_LOCATION']}\n")
        f.write(f"GOOGLE_APPLICATION_CREDENTIALS={config['GOOGLE_APPLICATION_CREDENTIALS']}\n")
        f.write(f"BIGQUERY_ENABLED={config['BIGQUERY_ENABLED']}\n")
        f.write(f"BIGQUERY_DATASET={config['BIGQUERY_DATASET']}\n\n")
        
        f.write("# Learning Function\n")
        f.write(f"LEARNING_FUNCTION_ENABLED={config['LEARNING_FUNCTION_ENABLED']}\n")
        f.write(f"LEARNING_BATCH_SIZE={config['LEARNING_BATCH_SIZE']}\n")
        f.write(f"LEARNING_RETENTION_DAYS={config['LEARNING_RETENTION_DAYS']}\n\n")
        
        f.write("# Security\n")
        f.write(f"SECRET_MANAGER_ENABLED={config['SECRET_MANAGER_ENABLED']}\n")
        f.write(f"API_KEY_HEADER={config['API_KEY_HEADER']}\n")
        f.write(f"ADMIN_API_KEYS={config['ADMIN_API_KEYS']}\n\n")
        
        f.write("# CORS\n")
        f.write(f"CORS_ORIGINS={config['CORS_ORIGINS']}\n\n")
        
        f.write("# Fetch.ai / ASI\n")
        f.write(f"FETCH_NETWORK={config['FETCH_NETWORK']}\n")
        f.write(f"FETCH_MNEMONIC={config['FETCH_MNEMONIC']}\n")
    
    print(f"\n✅ .env file created successfully at: {env_path}")
    print()
    
    # Validation
    print("=" * 70)
    print("🔍 VALIDATION")
    print("=" * 70)
    
    warnings = []
    errors = []
    
    # Check for LLM API key
    if config['DEFAULT_LLM_PROVIDER'] == 'gemini' and not config['GEMINI_API_KEY']:
        errors.append("❌ GEMINI_API_KEY is required (you selected Gemini as default)")
    elif config['DEFAULT_LLM_PROVIDER'] == 'openai' and not config['OPENAI_API_KEY']:
        errors.append("❌ OPENAI_API_KEY is required (you selected OpenAI as default)")
    elif config['DEFAULT_LLM_PROVIDER'] == 'anthropic' and not config['ANTHROPIC_API_KEY']:
        errors.append("❌ ANTHROPIC_API_KEY is required (you selected Anthropic as default)")
    
    if not config['GEMINI_API_KEY'] and not config['OPENAI_API_KEY'] and not config['ANTHROPIC_API_KEY']:
        errors.append("❌ At least ONE LLM API key is required!")
    
    # Warnings
    if config['MESSAGE_BUS_TYPE'] == 'memory':
        warnings.append("⚠️  Using in-memory message bus (won't persist across restarts)")
    
    if 'sqlite' in config['DATABASE_URL']:
        warnings.append("⚠️  Using SQLite (not recommended for production)")
    
    if errors:
        print("\n🚨 ERRORS (MUST FIX):")
        for error in errors:
            print(f"  {error}")
        print("\n❌ Configuration is incomplete. Please update .env file manually.")
        print(f"   Location: {env_path}")
        return False
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
    
    print("\n✅ Configuration is valid!")
    print()
    
    # Next steps
    print("=" * 70)
    print("🚀 NEXT STEPS")
    print("=" * 70)
    print()
    print("1. Get your Gemini API key:")
    print("   https://makersuite.google.com/app/apikey")
    print()
    print("2. Update .env file with your API key:")
    print(f"   nano {env_path}")
    print()
    print("3. Test the configuration:")
    print("   python3 manage.py health")
    print()
    print("4. Start the system:")
    print("   python3 manage.py start")
    print()
    
    return True


if __name__ == "__main__":
    try:
        setup_env()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Error during setup: {str(e)}")
        import traceback
        traceback.print_exc()
