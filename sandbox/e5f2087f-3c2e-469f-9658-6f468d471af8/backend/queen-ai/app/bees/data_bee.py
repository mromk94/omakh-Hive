"""
DataBee - Enterprise data operations with Elastic Search & BigQuery

Integrations:
- Elastic Search: Real-time bee activity queries, conversational search
- BigQuery: Historical blockchain data (transactions, DEX, oracles)
- Local cache: Performance optimization

Capabilities:
- Query blockchain data from BigQuery
- Search bee activities in Elastic
- Aggregate and analyze data
- Generate insights and reports
- RAG-powered conversational queries
"""
from typing import Dict, Any, List, Optional
import os
import structlog
from datetime import datetime, timedelta
from app.bees.base import BaseBee

try:
    from google.cloud import bigquery
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False

logger = structlog.get_logger(__name__)


class DataBee(BaseBee):
    """
    Enterprise Data Operations Bee
    
    Provides unified access to:
    1. Elastic Search - Real-time activity logs
    2. BigQuery - Historical blockchain data  
    3. Analytics - Aggregations and insights
    4. RAG - Conversational data queries
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id, name="DataBee")
        
        # Data source clients (set by BeeManager)
        self.elastic_client = None  # ElasticSearchIntegration
        self.bigquery_client = None  # BigQuery client
        
        # Configuration
        self.project_id = os.getenv('GCP_PROJECT_ID') or os.getenv('BIGQUERY_PROJECT_ID') or 'omk-hive-prod'
        self.dataset_id = os.getenv('BIGQUERY_DATASET', 'omk_hive_brain')
        
        # Cache for performance
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Initialize BigQuery if available
        if BIGQUERY_AVAILABLE:
            try:
                self.bigquery_client = bigquery.Client(project=self.project_id)
                logger.info("BigQuery client initialized", project=self.project_id)
            except Exception as e:
                logger.warning(f"BigQuery initialization failed: {e}")
                self.bigquery_client = None
    
    def set_elastic_client(self, elastic_client):
        """Set Elastic Search client (called by BeeManager)"""
        self.elastic_client = elastic_client
        logger.info("Elastic Search client connected to DataBee")
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data operation"""
        task_type = task_data.get("type")
        
        # Elastic Search operations
        if task_type == "search_activities":
            return await self._search_activities(task_data)
        elif task_type == "conversational_query":
            return await self._conversational_query(task_data)
        elif task_type == "get_bee_stats":
            return await self._get_bee_stats(task_data)
        
        # BigQuery operations
        elif task_type == "query_transactions":
            return await self._query_transactions(task_data)
        elif task_type == "query_dex_pools":
            return await self._query_dex_pools(task_data)
        elif task_type == "query_prices":
            return await self._query_prices(task_data)
        elif task_type == "get_blockchain_stats":
            return await self._get_blockchain_stats(task_data)
        
        # Analytics operations
        elif task_type == "aggregate_data":
            return await self._aggregate_data(task_data)
        elif task_type == "generate_insights":
            return await self._generate_insights(task_data)
        elif task_type == "create_report":
            return await self._create_report(task_data)
        
        # Legacy operations (backward compatibility)
        elif task_type == "query_balance":
            return await self._query_balance(task_data)
        elif task_type == "get_pool_stats":
            return await self._get_pool_stats(task_data)
        elif task_type == "aggregate_transfers":
            return await self._aggregate_transfers(task_data)
        elif task_type == "track_metrics":
            return await self._track_metrics(task_data)
        elif task_type == "generate_report":
            return await self._create_report(task_data)
        
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    # ========================================
    # ELASTIC SEARCH OPERATIONS
    # ========================================
    
    async def _search_activities(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Search bee activities in Elastic"""
        try:
            if not self.elastic_client:
                return {
                    "success": False,
                    "error": "Elastic Search not available"
                }
            
            query = data.get("query", "")
            bee_name = data.get("bee_name")  # Optional filter
            action = data.get("action")  # Optional filter
            limit = data.get("limit", 10)
            
            # Build filters
            filters = {}
            if bee_name:
                filters["bee_name"] = bee_name
            if action:
                filters["action"] = action
            
            # Search Elastic
            results = await self.elastic_client.hybrid_search(
                query=query,
                index="omk_hive_bee_activities",
                filters=filters,
                size=limit
            )
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Activity search failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _conversational_query(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """RAG-powered conversational query"""
        try:
            if not self.elastic_client:
                return {
                    "success": False,
                    "error": "Elastic Search not available"
                }
            
            question = data.get("question")
            context_size = data.get("context_size", 5)
            
            # Use Elastic's RAG feature
            result = await self.elastic_client.rag_query(
                question=question,
                context_size=context_size
            )
            
            return {
                "success": True,
                "question": question,
                "answer": result.get("answer"),
                "context": result.get("context"),
                "confidence": result.get("confidence"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Conversational query failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_bee_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics for bee activities"""
        try:
            if not self.elastic_client:
                return {"success": False, "error": "Elastic Search not available"}
            
            bee_name = data.get("bee_name")
            time_range = data.get("time_range", "24h")  # 24h, 7d, 30d
            
            # Query Elastic for activity stats
            query = f"bee_name:{bee_name}" if bee_name else "*"
            
            activities = await self.elastic_client.hybrid_search(
                query=query,
                index="omk_hive_bee_activities",
                size=1000
            )
            
            # Aggregate statistics
            total_activities = len(activities)
            successful = sum(1 for a in activities if a.get("success", True))
            failed = total_activities - successful
            
            # Group by action type
            action_counts = {}
            for activity in activities:
                action = activity.get("action", "unknown")
                action_counts[action] = action_counts.get(action, 0) + 1
            
            return {
                "success": True,
                "bee_name": bee_name or "all_bees",
                "time_range": time_range,
                "total_activities": total_activities,
                "successful": successful,
                "failed": failed,
                "success_rate": round((successful / total_activities * 100) if total_activities > 0 else 0, 2),
                "action_breakdown": action_counts,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Bee stats failed: {e}")
            return {"success": False, "error": str(e)}
    
    # ========================================
    # BIGQUERY OPERATIONS
    # ========================================
    
    async def _query_transactions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Query blockchain transactions from BigQuery"""
        try:
            if not self.bigquery_client:
                return {"success": False, "error": "BigQuery not available"}
            
            chain = data.get("chain", "ethereum")  # ethereum or solana
            limit = data.get("limit", 100)
            address = data.get("address")  # Optional filter
            
            # Build query
            table_name = f"{self.dataset_id}.{chain}_transactions"
            
            if address:
                query = f"""
                    SELECT *
                    FROM `{table_name}`
                    WHERE from_address = '{address}' OR to_address = '{address}'
                    ORDER BY block_timestamp DESC
                    LIMIT {limit}
                """
            else:
                query = f"""
                    SELECT *
                    FROM `{table_name}`
                    ORDER BY block_timestamp DESC
                    LIMIT {limit}
                """
            
            # Execute query
            query_job = self.bigquery_client.query(query)
            results = [dict(row) for row in query_job.result()]
            
            return {
                "success": True,
                "chain": chain,
                "transactions": results,
                "count": len(results),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Transaction query failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _query_dex_pools(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Query DEX pool data from BigQuery"""
        try:
            if not self.bigquery_client:
                return {"success": False, "error": "BigQuery not available"}
            
            dex = data.get("dex", "uniswap")  # uniswap, raydium
            limit = data.get("limit", 50)
            
            table_name = f"{self.dataset_id}.dex_pools"
            
            query = f"""
                SELECT *
                FROM `{table_name}`
                WHERE dex = '{dex}'
                ORDER BY timestamp DESC
                LIMIT {limit}
            """
            
            query_job = self.bigquery_client.query(query)
            results = [dict(row) for row in query_job.result()]
            
            return {
                "success": True,
                "dex": dex,
                "pools": results,
                "count": len(results),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"DEX pool query failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _query_prices(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Query price oracle data from BigQuery"""
        try:
            if not self.bigquery_client:
                return {"success": False, "error": "BigQuery not available"}
            
            pair = data.get("pair", "ETH/USD")  # e.g., ETH/USD, BTC/USD
            oracle = data.get("oracle", "chainlink")  # chainlink or pyth
            limit = data.get("limit", 100)
            
            table_name = f"{self.dataset_id}.{oracle}_prices"
            
            query = f"""
                SELECT *
                FROM `{table_name}`
                WHERE pair = '{pair}'
                ORDER BY timestamp DESC
                LIMIT {limit}
            """
            
            query_job = self.bigquery_client.query(query)
            results = [dict(row) for row in query_job.result()]
            
            # Calculate statistics
            if results:
                prices = [float(r.get('price', 0)) for r in results if 'price' in r]
                current_price = prices[0] if prices else None
                avg_price = sum(prices) / len(prices) if prices else None
                min_price = min(prices) if prices else None
                max_price = max(prices) if prices else None
            else:
                current_price = avg_price = min_price = max_price = None
            
            return {
                "success": True,
                "pair": pair,
                "oracle": oracle,
                "current_price": current_price,
                "avg_price": avg_price,
                "min_price": min_price,
                "max_price": max_price,
                "price_history": results[:10],  # Limit history in response
                "count": len(results),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Price query failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_blockchain_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive blockchain statistics from BigQuery"""
        try:
            if not self.bigquery_client:
                return {"success": False, "error": "BigQuery not available"}
            
            time_range = data.get("time_range", "24h")
            
            # Query transaction stats
            eth_query = f"""
                SELECT 
                    COUNT(*) as tx_count,
                    AVG(gas_price_gwei) as avg_gas,
                    SUM(value_eth) as total_volume
                FROM `{self.dataset_id}.ethereum_transactions`
                WHERE block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
            """
            
            eth_job = self.bigquery_client.query(eth_query)
            eth_stats = dict(next(eth_job.result(), {}))
            
            # Query DEX stats
            dex_query = f"""
                SELECT 
                    COUNT(DISTINCT pool_address) as pool_count,
                    SUM(CAST(total_liquidity_usd AS FLOAT64)) as total_tvl
                FROM `{self.dataset_id}.dex_pools`
            """
            
            dex_job = self.bigquery_client.query(dex_query)
            dex_stats = dict(next(dex_job.result(), {}))
            
            return {
                "success": True,
                "time_range": time_range,
                "ethereum": {
                    "transaction_count": int(eth_stats.get('tx_count', 0)),
                    "avg_gas_price": float(eth_stats.get('avg_gas', 0)),
                    "total_volume_eth": float(eth_stats.get('total_volume', 0))
                },
                "dex": {
                    "pool_count": int(dex_stats.get('pool_count', 0)),
                    "total_tvl_usd": float(dex_stats.get('total_tvl', 0))
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Blockchain stats failed: {e}")
            return {"success": False, "error": str(e)}
    
    # ========================================
    # ANALYTICS & REPORTING
    # ========================================
    
    async def _aggregate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate data across multiple sources"""
        try:
            metric = data.get("metric")  # tvl, volume, activity, etc.
            time_range = data.get("time_range", "24h")
            
            # Combine data from Elastic and BigQuery
            elastic_stats = await self._get_bee_stats({"time_range": time_range})
            blockchain_stats = await self._get_blockchain_stats({"time_range": time_range})
            
            aggregated = {
                "metric": metric,
                "time_range": time_range,
                "bee_activities": elastic_stats.get("total_activities", 0),
                "blockchain_transactions": blockchain_stats.get("ethereum", {}).get("transaction_count", 0),
                "total_tvl": blockchain_stats.get("dex", {}).get("total_tvl_usd", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "aggregated_data": aggregated
            }
            
        except Exception as e:
            logger.error(f"Data aggregation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered insights from data"""
        try:
            if not self.elastic_client:
                return {
                    "success": False,
                    "error": "Elastic Search required for insights"
                }
            
            topic = data.get("topic", "platform performance")
            
            # Use RAG to generate insights
            question = f"What are the key insights about {topic} based on recent data?"
            
            result = await self.elastic_client.rag_query(
                question=question,
                context_size=10
            )
            
            return {
                "success": True,
                "topic": topic,
                "insights": result.get("answer"),
                "data_sources": result.get("context"),
                "confidence": result.get("confidence"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive data report"""
        try:
            report_type = data.get("report_type", "daily")  # daily, weekly, monthly
            
            # Gather data from all sources
            bee_stats = await self._get_bee_stats({"time_range": "24h"})
            blockchain_stats = await self._get_blockchain_stats({"time_range": "24h"})
            
            # Get price data if available
            price_data = None
            if self.bigquery_client:
                price_data = await self._query_prices({"pair": "ETH/USD", "limit": 1})
            
            report = {
                "report_type": report_type,
                "generated_at": datetime.utcnow().isoformat(),
                "period": "24 hours",
                "summary": {
                    "total_bee_activities": bee_stats.get("total_activities", 0),
                    "bee_success_rate": bee_stats.get("success_rate", 0),
                    "blockchain_transactions": blockchain_stats.get("ethereum", {}).get("transaction_count", 0),
                    "total_tvl_usd": blockchain_stats.get("dex", {}).get("total_tvl_usd", 0),
                    "eth_price": price_data.get("current_price") if price_data else None
                },
                "detailed_sections": {
                    "bee_activities": bee_stats,
                    "blockchain": blockchain_stats,
                    "prices": price_data
                },
                "recommendations": self._generate_recommendations(bee_stats, blockchain_stats)
            }
            
            return {
                "success": True,
                "report": report
            }
            
        except Exception as e:
            logger.error(f"Report creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_recommendations(self, bee_stats: Dict, blockchain_stats: Dict) -> List[str]:
        """Generate actionable recommendations from data"""
        recommendations = []
        
        # Bee performance recommendations
        success_rate = bee_stats.get("success_rate", 100)
        if success_rate < 95:
            recommendations.append(f"⚠️ Bee success rate is {success_rate}% - investigate failed activities")
        else:
            recommendations.append(f"✅ Bee operations are healthy with {success_rate}% success rate")
        
        # Blockchain activity recommendations
        tx_count = blockchain_stats.get("ethereum", {}).get("transaction_count", 0)
        if tx_count > 1000:
            recommendations.append(f"📈 High blockchain activity detected ({tx_count} transactions) - monitor gas prices")
        
        # TVL recommendations
        tvl = blockchain_stats.get("dex", {}).get("total_tvl_usd", 0)
        if tvl > 1000000:
            recommendations.append(f"💰 Strong TVL of ${tvl:,.0f} - consider expanding liquidity pools")
        
        return recommendations
    
    # ========================================
    # LEGACY METHODS (Backward Compatibility)
    # ========================================
    
    async def _query_balance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy: Query balance"""
        address = data.get("address")
        
        if self.bigquery_client:
            # Query from BigQuery
            return await self._query_transactions({
                "address": address,
                "limit": 1
            })
        else:
            # Fallback to mock data
            return {
                "success": True,
                "address": address,
                "balance": 1000000 * 10**18,
                "note": "Mock data - BigQuery not available"
            }
    
    async def _get_pool_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy: Get pool stats"""
        pool_address = data.get("pool_address")
        
        if self.bigquery_client:
            # Query from BigQuery
            pools = await self._query_dex_pools({"limit": 10})
            # Find matching pool
            for pool in pools.get("pools", []):
                if pool.get("pool_address") == pool_address:
                    return {"success": True, "pool": pool}
            
            return {"success": False, "error": "Pool not found"}
        else:
            # Fallback to mock data
            return {
                "success": True,
                "pool_address": pool_address,
                "total_liquidity_usd": 5000000,
                "note": "Mock data - BigQuery not available"
            }
    
    async def _aggregate_transfers(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy: Aggregate transfers"""
        address = data.get("address")
        time_period = data.get("time_period", "24h")
        
        if self.bigquery_client:
            txs = await self._query_transactions({"address": address, "limit": 1000})
            transactions = txs.get("transactions", [])
            
            # Aggregate
            total_sent = sum(float(tx.get("value_eth", 0)) for tx in transactions if tx.get("from_address") == address)
            total_received = sum(float(tx.get("value_eth", 0)) for tx in transactions if tx.get("to_address") == address)
            
            return {
                "success": True,
                "address": address,
                "time_period": time_period,
                "total_sent": total_sent,
                "total_received": total_received,
                "transfer_count": len(transactions)
            }
        else:
            # Fallback mock
            return {
                "success": True,
                "address": address,
                "total_sent": 5000000,
                "total_received": 3000000,
                "note": "Mock data"
            }
    
    async def _track_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy: Track metrics"""
        metric_type = data.get("metric_type")
        
        # Use new aggregation
        return await self._aggregate_data({
            "metric": metric_type,
            "time_range": "24h"
        })
