#!/usr/bin/env python3
"""
Check deployment readiness for OMK Hive platform
"""
import os
from dotenv import load_dotenv

load_dotenv('backend/queen-ai/.env')

print("=" * 70)
print("OMK HIVE - DEPLOYMENT READINESS CHECK")
print("=" * 70)

checks = []

# Elastic Search
print("\n🔍 ELASTIC SEARCH (AI-Powered Search & RAG)")
elastic_cloud_id = os.getenv('ELASTIC_CLOUD_ID')
elastic_api_key = os.getenv('ELASTIC_API_KEY')

if elastic_cloud_id and elastic_cloud_id != 'your_cloud_id_here':
    print("  ✅ ELASTIC_CLOUD_ID configured")
    checks.append(True)
else:
    print("  ❌ ELASTIC_CLOUD_ID not set")
    print("     Get from: https://cloud.elastic.co/")
    checks.append(False)

if elastic_api_key and elastic_api_key != 'your_elastic_api_key_here':
    print("  ✅ ELASTIC_API_KEY configured")
    checks.append(True)
else:
    print("  ❌ ELASTIC_API_KEY not set")
    checks.append(False)

# Fivetran & BigQuery
print("\n📊 DATA PIPELINES (Fivetran + BigQuery)")
fivetran_key = os.getenv('FIVETRAN_API_KEY')
bigquery_project = os.getenv('BIGQUERY_PROJECT_ID')

if fivetran_key and fivetran_key != 'your_fivetran_api_key_here':
    print("  ✅ FIVETRAN_API_KEY configured")
    checks.append(True)
else:
    print("  ❌ FIVETRAN_API_KEY not set")
    print("     Get from: https://fivetran.com/dashboard/account/api")
    checks.append(False)

if bigquery_project and bigquery_project != 'omk-hive-prod':
    print("  ✅ BIGQUERY_PROJECT_ID configured")
    checks.append(True)
else:
    print("  ⚠️  BIGQUERY_PROJECT_ID using default")
    checks.append(True)  # Not critical for testing

# Blockchain RPCs
print("\n⛓️  BLOCKCHAIN CONNECTIONS")
eth_rpc = os.getenv('ETHEREUM_RPC_URL')
sol_rpc = os.getenv('SOLANA_RPC_URL')

if eth_rpc and ('infura' in eth_rpc or 'alchemy' in eth_rpc):
    print("  ✅ ETHEREUM_RPC_URL configured")
    checks.append(True)
else:
    print("  ⚠️  ETHEREUM_RPC_URL not configured (needed for Fivetran)")
    print("     Get from: https://infura.io/ or https://alchemy.com/")
    checks.append(False)

if sol_rpc:
    print("  ✅ SOLANA_RPC_URL configured")
    checks.append(True)
else:
    print("  ⚠️  SOLANA_RPC_URL not configured")
    checks.append(False)

# Gemini (for embeddings)
print("\n🤖 GEMINI (for Vector Embeddings)")
gemini_key = os.getenv('GEMINI_API_KEY')

if gemini_key and len(gemini_key) > 10:
    print("  ✅ GEMINI_API_KEY configured")
    checks.append(True)
else:
    print("  ⚠️  GEMINI_API_KEY not set (optional for embeddings)")
    checks.append(True)  # Optional

# Summary
print("\n" + "=" * 70)
passed = sum(checks)
total = len(checks)
percentage = (passed / total) * 100

print(f"READINESS: {passed}/{total} checks passed ({percentage:.0f}%)")

if percentage == 100:
    print("\n🎉 READY FOR DEPLOYMENT!")
    print("\nNext steps:")
    print("  1. Run: cd backend/queen-ai && python3 initialize_elastic.py")
    print("  2. Deploy Fivetran connectors via web UI")
    print("  3. Start Queen AI: python3 main.py")
elif percentage >= 50:
    print("\n⚠️  PARTIALLY READY")
    print("\nComplete the ❌ items above, then re-run this check")
else:
    print("\n❌ NOT READY")
    print("\nFollow the deployment guide: DEPLOYMENT_GUIDE.md")

print("=" * 70)
