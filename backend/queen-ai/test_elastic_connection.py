#!/usr/bin/env python3
"""
Test Elastic Search connection
"""
import asyncio
import os
from dotenv import load_dotenv
from elasticsearch import AsyncElasticsearch

load_dotenv()

async def test_connection():
    """Test basic Elastic connection"""
    
    url = os.getenv('ELASTIC_CLOUD_ID')
    api_key = os.getenv('ELASTIC_API_KEY')
    
    print("=" * 60)
    print("ELASTIC CONNECTION TEST")
    print("=" * 60)
    print(f"\nURL: {url}")
    print(f"API Key: {api_key[:20]}...")
    
    # Try connecting
    print("\nAttempting connection...")
    
    es = AsyncElasticsearch(
        hosts=[url],
        api_key=api_key,
        verify_certs=True
    )
    
    try:
        # Test connection
        info = await es.info()
        print("\n✅ Connection successful!")
        print(f"\nCluster info:")
        print(f"  Name: {info.get('name')}")
        print(f"  Version: {info.get('version', {}).get('number')}")
        print(f"  Cluster: {info.get('cluster_name')}")
        
        # List existing indices
        indices = await es.cat.indices(format='json')
        print(f"\n Existing indices: {len(indices)}")
        for idx in indices[:5]:
            print(f"  - {idx.get('index')}")
        
        await es.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print(f"\nError type: {type(e).__name__}")
        print(f"\nThis might be a Serverless deployment.")
        print("Serverless requires different endpoint format.")
        print("\nPlease check your Elastic Cloud dashboard:")
        print("  1. Go to: https://cloud.elastic.co/deployments")
        print("  2. Click on your deployment")
        print("  3. Look for 'Elasticsearch endpoint'")
        print("  4. Copy the full endpoint URL")
        
        await es.close()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
