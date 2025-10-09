#!/usr/bin/env python3
"""
Upload collected data to GCS for Fivetran ingestion
"""
import os
import sys
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv('backend/queen-ai/.env')

GCS_BUCKET = "omk-hive-blockchain-data"

def upload_file(file_path):
    """Upload file to GCS bucket"""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"📤 Uploading {file_path} to gs://{GCS_BUCKET}/")
    
    try:
        # Initialize GCS client
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET)
        
        # Upload file
        blob_name = f"blockchain_data/{os.path.basename(file_path)}"
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        
        print(f"✅ Uploaded to: gs://{GCS_BUCKET}/{blob_name}")
        print(f"✅ Fivetran will sync this to BigQuery automatically")
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        print("\nMake sure you're authenticated:")
        print("  gcloud auth application-default login")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 upload_to_gcs.py <data_file.json>")
        print("\nOr upload all sync files:")
        print("  python3 upload_to_gcs.py data_sync_*.json")
        sys.exit(1)
    
    for file_path in sys.argv[1:]:
        upload_file(file_path)
