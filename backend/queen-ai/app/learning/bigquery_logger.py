"""
BigQuery Logger - Store Training Data in Google BigQuery

Logs all interactions, decisions, and outcomes to BigQuery for future model training.
Follows google_cloud_strategy.md - uses BigQuery as data warehouse.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

try:
    from google.cloud import bigquery
    from google.api_core import retry
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    bigquery = None

from app.config.settings import settings

logger = structlog.get_logger(__name__)


class BigQueryLogger:
    """
    BigQuery data logger for learning function
    
    Tables:
    - llm_conversations: All LLM interactions
    - bee_decisions: Bee decision logs
    - user_interactions: User behavior
    - system_events: System-level events
    - pattern_data: Pattern recognition training data
    
    Features:
    - Async batch inserts (cost optimization)
    - Automatic schema creation
    - Partitioned tables (by date)
    - Data retention policies
    - Privacy-preserving (anonymized)
    """
    
    def __init__(self):
        self.client: Optional[bigquery.Client] = None
        self.dataset_id = "omk_hive_learning"
        self.initialized = False
        self.batch_buffer: List[Dict] = []
        self.batch_size = 100  # Insert in batches of 100
        
        if not BIGQUERY_AVAILABLE:
            logger.warning("⚠️  google-cloud-bigquery not installed. Install with: pip install google-cloud-bigquery")
    
    async def initialize(self):
        """Initialize BigQuery client and create datasets/tables"""
        if not BIGQUERY_AVAILABLE:
            logger.warning("BigQuery not available - learning function disabled")
            return
        
        try:
            # Create BigQuery client
            self.client = bigquery.Client(project=settings.GCP_PROJECT_ID)
            
            # Create dataset if not exists
            dataset_ref = self.client.dataset(self.dataset_id)
            
            try:
                self.client.get_dataset(dataset_ref)
                logger.info(f"Dataset {self.dataset_id} already exists")
            except Exception:
                # Create dataset
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = settings.GCP_LOCATION
                dataset.description = "OMK Hive Learning Function - Training Data"
                
                # Set data retention (7 days for free tier optimization)
                dataset.default_table_expiration_ms = 1000 * 60 * 60 * 24 * 365  # 1 year
                
                self.client.create_dataset(dataset)
                logger.info(f"Created dataset {self.dataset_id}")
            
            # Create tables
            await self._create_tables()
            
            self.initialized = True
            logger.info("✅ BigQuery Learning Function initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery: {str(e)}")
            self.initialized = False
    
    async def _create_tables(self):
        """Create all BigQuery tables with schemas"""
        
        # Table 1: LLM Conversations
        llm_schema = [
            bigquery.SchemaField("conversation_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("provider", "STRING", mode="REQUIRED"),  # gemini, openai, etc.
            bigquery.SchemaField("model", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("role", "STRING", mode="REQUIRED"),  # system, user, assistant
            bigquery.SchemaField("content", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("tokens_used", "INTEGER"),
            bigquery.SchemaField("cost_usd", "FLOAT"),
            bigquery.SchemaField("response_time_ms", "INTEGER"),
            bigquery.SchemaField("context_window", "INTEGER"),
            bigquery.SchemaField("temperature", "FLOAT"),
            bigquery.SchemaField("bee_source", "STRING"),  # Which bee initiated
            bigquery.SchemaField("success", "BOOLEAN"),
            bigquery.SchemaField("error_message", "STRING"),
        ]
        
        await self._create_table_if_not_exists(
            "llm_conversations",
            llm_schema,
            partition_field="timestamp",
            description="All LLM interactions for training data"
        )
        
        # Table 2: Bee Decisions
        decision_schema = [
            bigquery.SchemaField("decision_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("bee_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("decision_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("input_data", "JSON", mode="REQUIRED"),
            bigquery.SchemaField("output_decision", "JSON", mode="REQUIRED"),
            bigquery.SchemaField("confidence_score", "FLOAT"),
            bigquery.SchemaField("reasoning", "STRING"),
            bigquery.SchemaField("outcome", "STRING"),  # success, failure, pending
            bigquery.SchemaField("execution_time_ms", "INTEGER"),
            bigquery.SchemaField("llm_used", "BOOLEAN"),
            bigquery.SchemaField("override_by_human", "BOOLEAN"),
        ]
        
        await self._create_table_if_not_exists(
            "bee_decisions",
            decision_schema,
            partition_field="timestamp",
            description="All bee decision logs"
        )
        
        # Table 3: User Interactions
        interaction_schema = [
            bigquery.SchemaField("interaction_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("user_id_hash", "STRING", mode="REQUIRED"),  # Anonymized
            bigquery.SchemaField("interaction_type", "STRING"),  # query, transaction, vote, etc.
            bigquery.SchemaField("input_text", "STRING"),
            bigquery.SchemaField("response", "STRING"),
            bigquery.SchemaField("session_id", "STRING"),
            bigquery.SchemaField("response_time_ms", "INTEGER"),
            bigquery.SchemaField("user_satisfied", "BOOLEAN"),  # Feedback
            bigquery.SchemaField("error_occurred", "BOOLEAN"),
        ]
        
        await self._create_table_if_not_exists(
            "user_interactions",
            interaction_schema,
            partition_field="timestamp",
            description="User interaction patterns (anonymized)"
        )
        
        # Table 4: Pattern Data
        pattern_schema = [
            bigquery.SchemaField("pattern_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("pattern_type", "STRING"),  # price, volume, anomaly
            bigquery.SchemaField("detected_by", "STRING"),  # PatternBee
            bigquery.SchemaField("data_points", "JSON"),  # Time series data
            bigquery.SchemaField("pattern_label", "STRING"),  # uptrend, downtrend, etc.
            bigquery.SchemaField("confidence", "FLOAT"),
            bigquery.SchemaField("prediction", "STRING"),
            bigquery.SchemaField("actual_outcome", "STRING"),  # For model validation
            bigquery.SchemaField("accuracy", "FLOAT"),  # Was prediction correct?
        ]
        
        await self._create_table_if_not_exists(
            "pattern_data",
            pattern_schema,
            partition_field="timestamp",
            description="Pattern recognition training data"
        )
        
        # Table 5: System Events
        event_schema = [
            bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("source", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("severity", "STRING"),
            bigquery.SchemaField("event_data", "JSON"),
            bigquery.SchemaField("outcome", "STRING"),
        ]
        
        await self._create_table_if_not_exists(
            "system_events",
            event_schema,
            partition_field="timestamp",
            description="System-level events and actions"
        )
    
    async def _create_table_if_not_exists(
        self,
        table_name: str,
        schema: List[bigquery.SchemaField],
        partition_field: Optional[str] = None,
        description: str = ""
    ):
        """Create table if it doesn't exist"""
        if not self.client:
            return
        
        table_ref = self.client.dataset(self.dataset_id).table(table_name)
        
        try:
            self.client.get_table(table_ref)
            logger.info(f"Table {table_name} already exists")
        except Exception:
            # Create table
            table = bigquery.Table(table_ref, schema=schema)
            table.description = description
            
            # Add partitioning (cost optimization)
            if partition_field:
                table.time_partitioning = bigquery.TimePartitioning(
                    type_=bigquery.TimePartitioningType.DAY,
                    field=partition_field
                )
            
            # Add clustering (query optimization)
            if table_name == "llm_conversations":
                table.clustering_fields = ["provider", "bee_source"]
            elif table_name == "bee_decisions":
                table.clustering_fields = ["bee_name", "decision_type"]
            
            self.client.create_table(table)
            logger.info(f"Created table {table_name}")
    
    async def log_llm_conversation(
        self,
        conversation_id: str,
        provider: str,
        model: str,
        role: str,
        content: str,
        tokens_used: Optional[int] = None,
        cost_usd: Optional[float] = None,
        response_time_ms: Optional[int] = None,
        bee_source: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        **kwargs
    ):
        """Log LLM conversation to BigQuery"""
        if not self.initialized:
            return
        
        row = {
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "provider": provider,
            "model": model,
            "role": role,
            "content": content[:10000],  # Truncate very long content
            "tokens_used": tokens_used,
            "cost_usd": cost_usd,
            "response_time_ms": response_time_ms,
            "context_window": kwargs.get("context_window"),
            "temperature": kwargs.get("temperature"),
            "bee_source": bee_source,
            "success": success,
            "error_message": error_message,
        }
        
        await self._add_to_batch("llm_conversations", row)
    
    async def log_bee_decision(
        self,
        decision_id: str,
        bee_name: str,
        decision_type: str,
        input_data: Dict[str, Any],
        output_decision: Dict[str, Any],
        confidence_score: Optional[float] = None,
        reasoning: Optional[str] = None,
        outcome: str = "pending",
        execution_time_ms: Optional[int] = None,
        llm_used: bool = False,
        override_by_human: bool = False
    ):
        """Log bee decision to BigQuery"""
        if not self.initialized:
            return
        
        row = {
            "decision_id": decision_id,
            "timestamp": datetime.utcnow().isoformat(),
            "bee_name": bee_name,
            "decision_type": decision_type,
            "input_data": input_data,
            "output_decision": output_decision,
            "confidence_score": confidence_score,
            "reasoning": reasoning,
            "outcome": outcome,
            "execution_time_ms": execution_time_ms,
            "llm_used": llm_used,
            "override_by_human": override_by_human,
        }
        
        await self._add_to_batch("bee_decisions", row)
    
    async def log_user_interaction(
        self,
        interaction_id: str,
        user_id_hash: str,  # Already anonymized
        interaction_type: str,
        input_text: Optional[str] = None,
        response: Optional[str] = None,
        session_id: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        user_satisfied: Optional[bool] = None,
        error_occurred: bool = False
    ):
        """Log user interaction to BigQuery"""
        if not self.initialized:
            return
        
        row = {
            "interaction_id": interaction_id,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id_hash": user_id_hash,
            "interaction_type": interaction_type,
            "input_text": input_text[:5000] if input_text else None,
            "response": response[:5000] if response else None,
            "session_id": session_id,
            "response_time_ms": response_time_ms,
            "user_satisfied": user_satisfied,
            "error_occurred": error_occurred,
        }
        
        await self._add_to_batch("user_interactions", row)
    
    async def log_pattern_data(
        self,
        pattern_id: str,
        pattern_type: str,
        detected_by: str,
        data_points: Dict[str, Any],
        pattern_label: str,
        confidence: float,
        prediction: Optional[str] = None,
        actual_outcome: Optional[str] = None,
        accuracy: Optional[float] = None
    ):
        """Log pattern recognition data"""
        if not self.initialized:
            return
        
        row = {
            "pattern_id": pattern_id,
            "timestamp": datetime.utcnow().isoformat(),
            "pattern_type": pattern_type,
            "detected_by": detected_by,
            "data_points": data_points,
            "pattern_label": pattern_label,
            "confidence": confidence,
            "prediction": prediction,
            "actual_outcome": actual_outcome,
            "accuracy": accuracy,
        }
        
        await self._add_to_batch("pattern_data", row)
    
    async def _add_to_batch(self, table_name: str, row: Dict[str, Any]):
        """Add row to batch buffer and flush if needed"""
        self.batch_buffer.append({
            "table": table_name,
            "row": row
        })
        
        if len(self.batch_buffer) >= self.batch_size:
            await self.flush_batch()
    
    async def flush_batch(self):
        """Flush batch buffer to BigQuery"""
        if not self.batch_buffer or not self.client:
            return
        
        try:
            # Group by table
            tables: Dict[str, List[Dict]] = {}
            for item in self.batch_buffer:
                table_name = item["table"]
                if table_name not in tables:
                    tables[table_name] = []
                tables[table_name].append(item["row"])
            
            # Insert each table
            for table_name, rows in tables.items():
                table_ref = self.client.dataset(self.dataset_id).table(table_name)
                
                errors = self.client.insert_rows_json(
                    table_ref,
                    rows,
                    retry=retry.Retry(deadline=30)
                )
                
                if errors:
                    logger.error(f"BigQuery insert errors for {table_name}: {errors}")
                else:
                    logger.debug(f"Inserted {len(rows)} rows to {table_name}")
            
            # Clear buffer
            self.batch_buffer = []
            
        except Exception as e:
            logger.error(f"Failed to flush batch to BigQuery: {str(e)}")
    
    async def query_training_data(
        self,
        table_name: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Query training data from BigQuery
        
        Example:
            data = await logger.query_training_data(
                "llm_conversations",
                filters={"provider": "gemini", "success": True},
                limit=10000
            )
        """
        if not self.client:
            return []
        
        query = f"SELECT * FROM `{self.dataset_id}.{table_name}`"
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if isinstance(value, str):
                    conditions.append(f"{key} = '{value}'")
                else:
                    conditions.append(f"{key} = {value}")
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" LIMIT {limit}"
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"BigQuery query failed: {str(e)}")
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get learning function statistics"""
        if not self.client:
            return {}
        
        try:
            stats = {}
            
            for table_name in ["llm_conversations", "bee_decisions", "user_interactions", "pattern_data"]:
                query = f"""
                    SELECT 
                        COUNT(*) as total_rows,
                        MIN(timestamp) as earliest,
                        MAX(timestamp) as latest
                    FROM `{self.dataset_id}.{table_name}`
                """
                
                result = list(self.client.query(query).result())[0]
                stats[table_name] = {
                    "total_rows": result.total_rows,
                    "earliest": result.earliest,
                    "latest": result.latest
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {}
    
    async def shutdown(self):
        """Flush remaining data and cleanup"""
        await self.flush_batch()
        logger.info("BigQuery logger shutdown")


# Global instance
bigquery_logger = BigQueryLogger()
