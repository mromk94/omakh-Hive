#!/usr/bin/env python3
"""
Test DataPipelineBee - Automated blockchain data pipeline
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.bees.data_pipeline_bee import DataPipelineBee
import structlog

# Configure logging
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)

async def test_pipeline():
    """Test the automated data pipeline"""
    
    print("=" * 70)
    print("TESTING DATAPIPELINEBEE - AUTOMATED DATA PIPELINE")
    print("=" * 70)
    
    # Initialize bee
    bee = DataPipelineBee()
    print(f"\n✅ DataPipelineBee initialized")
    print(f"   GCS Bucket: {bee.gcs_bucket}")
    print(f"   Schedule: Every {bee.schedule_interval.total_seconds() / 60} minutes")
    
    # Test 1: Get pipeline status
    print("\n" + "=" * 70)
    print("TEST 1: Get Pipeline Status")
    print("=" * 70)
    
    status = await bee.execute({"type": "get_pipeline_status"})
    print(f"\n✅ Status: {status}")
    
    # Test 2: Run full pipeline
    print("\n" + "=" * 70)
    print("TEST 2: Run Full Pipeline")
    print("=" * 70)
    print("\nThis will:")
    print("  1. Collect blockchain data")
    print("  2. Convert to CSV format")
    print("  3. Upload to GCS")
    print("\nStarting pipeline...")
    
    result = await bee.execute({"type": "run_pipeline"})
    
    if result.get("success"):
        print(f"\n✅ PIPELINE SUCCESS!")
        print(f"   Duration: {result.get('duration_seconds'):.1f}s")
        print(f"   Total Records: {result.get('total_records')}")
        print(f"   CSV Files: {result.get('csv_files_uploaded')}")
        print(f"   GCS Bucket: {result.get('gcs_bucket')}")
        
        print(f"\n📊 Pipeline Steps:")
        for step_name, step_result in result.get("steps", {}).items():
            status = "✅" if step_result.get("success") else "❌"
            print(f"   {status} {step_name}: {step_result}")
    else:
        print(f"\n❌ PIPELINE FAILED!")
        print(f"   Error: {result.get('error')}")
    
    # Test 3: Schedule pipeline
    print("\n" + "=" * 70)
    print("TEST 3: Schedule Pipeline (Every 15 Minutes)")
    print("=" * 70)
    
    schedule_result = await bee.execute({
        "type": "schedule_pipeline",
        "interval_minutes": 15
    })
    
    print(f"\n✅ Schedule Result: {schedule_result}")
    
    # Final status
    print("\n" + "=" * 70)
    print("FINAL PIPELINE STATUS")
    print("=" * 70)
    
    final_status = await bee.execute({"type": "get_pipeline_status"})
    status_data = final_status.get("status", {})
    
    print(f"\n📊 Pipeline Statistics:")
    print(f"   Run Count: {status_data.get('run_count')}")
    print(f"   Error Count: {status_data.get('error_count')}")
    print(f"   Last Run: {status_data.get('last_run')}")
    print(f"   Last Success: {status_data.get('last_success')}")
    print(f"   Schedule: Every {status_data.get('schedule_interval_minutes')} minutes")
    
    print("\n" + "=" * 70)
    print("✅ DATAPIPELINEBEE TEST COMPLETE")
    print("=" * 70)
    
    print("\n💡 Next Steps:")
    print("   1. Fivetran will automatically sync CSV files to BigQuery")
    print("   2. DataBee can now query real blockchain data")
    print("   3. Schedule DataPipelineBee to run every 15 minutes")

if __name__ == "__main__":
    # Add missing import
    import logging
    asyncio.run(test_pipeline())
