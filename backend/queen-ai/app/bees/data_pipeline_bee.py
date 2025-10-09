"""
DataPipelineBee - Automated blockchain data collection & GCS sync

Responsibilities:
- Collect blockchain data (transactions, DEX, oracles)
- Convert to CSV format (Fivetran-compatible)
- Upload to GCS bucket
- Monitor Fivetran sync status
- Schedule automated runs (every 15 minutes)
- Report pipeline health to Queen AI

This bee runs the entire data pipeline automatically!
"""
from typing import Dict, Any, List
import os
import json
import csv
import structlog
from datetime import datetime, timedelta
from pathlib import Path
from app.bees.base import BaseBee

try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

logger = structlog.get_logger(__name__)


class DataPipelineBee(BaseBee):
    """
    Automated Data Pipeline Bee
    
    Handles the complete data pipeline:
    1. Collect blockchain data
    2. Convert to CSV
    3. Upload to GCS
    4. Monitor Fivetran
    5. Report status
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id, name="DataPipelineBee")
        
        # Configuration
        self.gcs_bucket = os.getenv('GCS_BUCKET', 'omk-hive-blockchain-data')
        self.gcs_prefix = os.getenv('GCS_PREFIX', 'blockchain_data/')
        self.project_id = os.getenv('GCP_PROJECT_ID', 'omk-hive-prod')
        
        # Pipeline state
        self.last_run = None
        self.last_success = None
        self.run_count = 0
        self.error_count = 0
        
        # Schedule (default: every 15 minutes)
        self.schedule_interval = timedelta(minutes=15)
        
        # Initialize GCS client
        self.gcs_client = None
        if GCS_AVAILABLE:
            try:
                self.gcs_client = storage.Client(project=self.project_id)
                logger.info("GCS client initialized for pipeline", bucket=self.gcs_bucket)
            except Exception as e:
                logger.warning(f"GCS initialization failed: {e}")
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pipeline task"""
        task_type = task_data.get("type")
        
        if task_type == "run_pipeline":
            return await self._run_full_pipeline(task_data)
        elif task_type == "collect_data":
            return await self._collect_blockchain_data(task_data)
        elif task_type == "convert_to_csv":
            return await self._convert_to_csv(task_data)
        elif task_type == "upload_to_gcs":
            return await self._upload_to_gcs(task_data)
        elif task_type == "check_fivetran":
            return await self._check_fivetran_status(task_data)
        elif task_type == "get_pipeline_status":
            return await self._get_pipeline_status(task_data)
        elif task_type == "schedule_pipeline":
            return await self._schedule_pipeline(task_data)
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    async def _run_full_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete data pipeline"""
        try:
            logger.info("Starting full data pipeline")
            pipeline_start = datetime.utcnow()
            self.run_count += 1
            
            results = {
                "pipeline_run": self.run_count,
                "started_at": pipeline_start.isoformat(),
                "steps": {}
            }
            
            # Step 1: Collect blockchain data
            logger.info("Step 1/3: Collecting blockchain data")
            collect_result = await self._collect_blockchain_data({})
            results["steps"]["collect"] = collect_result
            
            if not collect_result.get("success"):
                raise Exception(f"Data collection failed: {collect_result.get('error')}")
            
            json_file = collect_result.get("output_file")
            
            # Step 2: Convert to CSV
            logger.info("Step 2/3: Converting to CSV")
            convert_result = await self._convert_to_csv({"input_file": json_file})
            results["steps"]["convert"] = convert_result
            
            if not convert_result.get("success"):
                raise Exception(f"CSV conversion failed: {convert_result.get('error')}")
            
            csv_files = convert_result.get("csv_files", [])
            
            # Step 3: Upload to GCS
            logger.info("Step 3/3: Uploading to GCS")
            upload_result = await self._upload_to_gcs({"files": csv_files})
            results["steps"]["upload"] = upload_result
            
            if not upload_result.get("success"):
                raise Exception(f"GCS upload failed: {upload_result.get('error')}")
            
            # Pipeline complete
            pipeline_end = datetime.utcnow()
            duration = (pipeline_end - pipeline_start).total_seconds()
            
            self.last_run = pipeline_end
            self.last_success = pipeline_end
            
            results.update({
                "success": True,
                "completed_at": pipeline_end.isoformat(),
                "duration_seconds": duration,
                "total_records": collect_result.get("total_records", 0),
                "csv_files_uploaded": len(csv_files),
                "gcs_bucket": self.gcs_bucket,
                "message": f"Pipeline completed successfully in {duration:.1f}s"
            })
            
            logger.info("Data pipeline completed successfully", 
                       duration=duration, 
                       records=results["total_records"])
            
            return results
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Pipeline failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "pipeline_run": self.run_count,
                "started_at": pipeline_start.isoformat() if 'pipeline_start' in locals() else None
            }
    
    async def _collect_blockchain_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect blockchain data using existing connectors"""
        try:
            # Import connectors dynamically
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
            
            from backend.queen_ai.app.integrations.data_collectors.blockchain_transactions import BlockchainTransactionsConnector
            from backend.queen_ai.app.integrations.data_collectors.dex_pools import DEXPoolsConnector
            from backend.queen_ai.app.integrations.data_collectors.price_oracles import PriceOraclesConnector
            
            # Initialize connectors
            blockchain_connector = BlockchainTransactionsConnector()
            dex_connector = DEXPoolsConnector()
            oracle_connector = PriceOraclesConnector()
            
            # Collect data
            all_data = {
                "metadata": {
                    "collected_at": datetime.utcnow().isoformat(),
                    "collector": "DataPipelineBee",
                    "version": "1.0"
                },
                "blockchain": [],
                "dex": [],
                "oracle": []
            }
            
            # Blockchain transactions
            eth_txs = await blockchain_connector.extract_ethereum_transactions(limit=10)
            sol_txs = await blockchain_connector.extract_solana_transactions(limit=10)
            all_data["blockchain"].extend(eth_txs + sol_txs)
            
            # DEX pools
            uniswap_pools = await dex_connector.extract_uniswap_pools(limit=5)
            all_data["dex"].extend(uniswap_pools)
            
            # Price oracles
            chainlink_prices = await oracle_connector.extract_chainlink_prices(limit=5)
            pyth_prices = await oracle_connector.extract_pyth_prices(limit=5)
            all_data["oracle"].extend(chainlink_prices + pyth_prices)
            
            # Save to JSON file
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            output_file = f"data_sync_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump(all_data, f, indent=2, default=str)
            
            total_records = len(all_data["blockchain"]) + len(all_data["dex"]) + len(all_data["oracle"])
            
            logger.info("Data collection complete", 
                       records=total_records,
                       file=output_file)
            
            return {
                "success": True,
                "output_file": output_file,
                "total_records": total_records,
                "blockchain_records": len(all_data["blockchain"]),
                "dex_records": len(all_data["dex"]),
                "oracle_records": len(all_data["oracle"])
            }
            
        except Exception as e:
            logger.error(f"Data collection failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _convert_to_csv(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert JSON data to CSV format"""
        try:
            input_file = data.get("input_file")
            
            if not input_file or not os.path.exists(input_file):
                raise Exception(f"Input file not found: {input_file}")
            
            with open(input_file, 'r') as f:
                json_data = json.load(f)
            
            timestamp = json_data.get('metadata', {}).get('collected_at', datetime.utcnow().isoformat())
            csv_files = []
            
            # Convert blockchain data
            if json_data.get('blockchain'):
                csv_file = input_file.replace('.json', '_blockchain.csv')
                with open(csv_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'timestamp', 'table', 'transaction_hash', 'block_number',
                        'from_address', 'to_address', 'value', 'gas_price', 'status'
                    ])
                    
                    for record in json_data['blockchain']:
                        table = record.get('table', 'unknown')
                        rec_data = record.get('data', {})
                        writer.writerow([
                            timestamp, table,
                            rec_data.get('transaction_hash', ''),
                            rec_data.get('block_number', ''),
                            rec_data.get('from_address', ''),
                            rec_data.get('to_address', ''),
                            rec_data.get('value', 0),
                            rec_data.get('gas_price', 0),
                            rec_data.get('status', 'pending')
                        ])
                
                csv_files.append(csv_file)
            
            # Convert DEX data
            if json_data.get('dex'):
                csv_file = input_file.replace('.json', '_dex.csv')
                with open(csv_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'timestamp', 'table', 'pool_address', 'dex',
                        'token_a', 'token_b', 'liquidity_usd', 'volume_24h',
                        'reserve_a', 'reserve_b'
                    ])
                    
                    for record in json_data['dex']:
                        table = record.get('table', 'unknown')
                        rec_data = record.get('data', {})
                        writer.writerow([
                            timestamp, table,
                            rec_data.get('pool_address', ''),
                            rec_data.get('dex', 'unknown'),
                            rec_data.get('token_a', ''),
                            rec_data.get('token_b', ''),
                            rec_data.get('liquidity_usd', 0),
                            rec_data.get('volume_24h', 0),
                            rec_data.get('reserve_a', 0),
                            rec_data.get('reserve_b', 0)
                        ])
                
                csv_files.append(csv_file)
            
            # Convert oracle data
            if json_data.get('oracle'):
                csv_file = input_file.replace('.json', '_oracle.csv')
                with open(csv_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'timestamp', 'table', 'oracle', 'pair',
                        'price', 'confidence', 'feed_address'
                    ])
                    
                    for record in json_data['oracle']:
                        table = record.get('table', 'unknown')
                        rec_data = record.get('data', {})
                        writer.writerow([
                            timestamp, table,
                            rec_data.get('oracle', 'unknown'),
                            rec_data.get('pair', ''),
                            rec_data.get('price', 0),
                            rec_data.get('confidence', 0),
                            rec_data.get('feed_address', '')
                        ])
                
                csv_files.append(csv_file)
            
            logger.info("CSV conversion complete", files=len(csv_files))
            
            return {
                "success": True,
                "csv_files": csv_files,
                "count": len(csv_files)
            }
            
        except Exception as e:
            logger.error(f"CSV conversion failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _upload_to_gcs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload files to GCS"""
        try:
            if not self.gcs_client:
                raise Exception("GCS client not available")
            
            files = data.get("files", [])
            if not files:
                raise Exception("No files to upload")
            
            bucket = self.gcs_client.bucket(self.gcs_bucket)
            uploaded = []
            
            for file_path in files:
                if not os.path.exists(file_path):
                    logger.warning(f"File not found: {file_path}")
                    continue
                
                blob_name = f"{self.gcs_prefix}{os.path.basename(file_path)}"
                blob = bucket.blob(blob_name)
                blob.upload_from_filename(file_path)
                
                uploaded.append({
                    "file": os.path.basename(file_path),
                    "gcs_path": f"gs://{self.gcs_bucket}/{blob_name}",
                    "size_bytes": os.path.getsize(file_path)
                })
                
                logger.info(f"Uploaded: {blob_name}")
            
            return {
                "success": True,
                "uploaded_files": uploaded,
                "count": len(uploaded),
                "bucket": self.gcs_bucket
            }
            
        except Exception as e:
            logger.error(f"GCS upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _check_fivetran_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check Fivetran sync status (placeholder for future API integration)"""
        # TODO: Integrate with Fivetran API to check sync status
        return {
            "success": True,
            "message": "Fivetran status check not yet implemented",
            "note": "Files uploaded to GCS, Fivetran will sync automatically"
        }
    
    async def _get_pipeline_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get pipeline status"""
        return {
            "success": True,
            "status": {
                "run_count": self.run_count,
                "error_count": self.error_count,
                "last_run": self.last_run.isoformat() if self.last_run else None,
                "last_success": self.last_success.isoformat() if self.last_success else None,
                "schedule_interval_minutes": self.schedule_interval.total_seconds() / 60,
                "gcs_bucket": self.gcs_bucket,
                "gcs_available": self.gcs_client is not None
            }
        }
    
    async def _schedule_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule pipeline runs (to be called by Queen AI scheduler)"""
        interval_minutes = data.get("interval_minutes", 15)
        self.schedule_interval = timedelta(minutes=interval_minutes)
        
        return {
            "success": True,
            "message": f"Pipeline scheduled to run every {interval_minutes} minutes",
            "next_run": (datetime.utcnow() + self.schedule_interval).isoformat()
        }
