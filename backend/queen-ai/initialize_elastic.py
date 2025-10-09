#!/usr/bin/env python3
"""
Initialize Elastic Search for OMK Hive
Run this after setting ELASTIC_CLOUD_ID and ELASTIC_API_KEY in .env
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def main():
    """Initialize Elastic Search indices"""
    
    print("=" * 60)
    print("ELASTIC SEARCH INITIALIZATION")
    print("=" * 60)
    
    # Check environment variables
    cloud_id = os.getenv('ELASTIC_CLOUD_ID')
    api_key = os.getenv('ELASTIC_API_KEY')
    
    if not cloud_id or not api_key:
        print("\n❌ Missing Elastic credentials!")
        print("\nPlease set in .env:")
        print("  ELASTIC_CLOUD_ID=your_cloud_id")
        print("  ELASTIC_API_KEY=your_api_key")
        print("\nGet credentials from: https://cloud.elastic.co/")
        sys.exit(1)
    
    print(f"\n✅ Credentials found")
    print(f"  Cloud ID: {cloud_id[:20]}...")
    print(f"  API Key: {api_key[:10]}...")
    
    try:
        # Import Elastic integration
        from app.integrations.elastic_search import ElasticSearchIntegration
        
        print("\n✅ Creating Elastic Search connection...")
        elastic = ElasticSearchIntegration(
            cloud_id=cloud_id,
            api_key=api_key
        )
        
        print("\n✅ Initializing indices...")
        await elastic.initialize()
        
        print("\n🎉 Elastic Search initialized successfully!")
        print("\nCreated indices:")
        print(f"  • {elastic.bee_activities_index}")
        print(f"  • {elastic.knowledge_base_index}")
        print(f"  • {elastic.transactions_index}")
        
        print("\n✅ Testing connection...")
        # Test a simple log
        await elastic.log_bee_activity(
            bee_name="System",
            action="Elastic initialization test",
            data={"status": "success"},
            success=True,
            tags=["initialization", "test"]
        )
        
        print("\n✅ Test log written successfully!")
        
        print("\n" + "=" * 60)
        print("ELASTIC SEARCH READY!")
        print("=" * 60)
        print("\nYou can now:")
        print("  1. Start Queen AI: python3 main.py")
        print("  2. All bee activities will be logged to Elastic")
        print("  3. Use conversational search for insights")
        
        await elastic.close()
        
    except ImportError as e:
        print(f"\n❌ Import error: {str(e)}")
        print("\nMake sure elasticsearch is installed:")
        print("  pip install elasticsearch==8.11.0")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Initialization failed: {str(e)}")
        print("\nPlease check:")
        print("  1. Elastic Cloud deployment is running")
        print("  2. Credentials are correct")
        print("  3. Network connection is active")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
