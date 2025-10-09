"""
Elastic Search Integration for Queen AI

Features:
- Hybrid search (vector + keyword)
- RAG (Retrieval Augmented Generation) with Gemini
- Bee activity logging
- Conversational interface
"""
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog

from elasticsearch import Elasticsearch, AsyncElasticsearch
from elasticsearch.helpers import async_bulk

logger = structlog.get_logger(__name__)


class ElasticSearchIntegration:
    """
    Elastic Search AI Platform integration
    
    Provides:
    - Hybrid search (semantic + keyword)
    - Vector embeddings via Gemini
    - RAG for Queen AI
    - Activity logging for all bees
    """
    
    def __init__(
        self,
        cloud_id: Optional[str] = None,
        api_key: Optional[str] = None,
        gemini_client = None
    ):
        """
        Initialize Elastic connection
        
        Args:
            cloud_id: Elastic Cloud ID
            api_key: Elastic API key
            gemini_client: Gemini client for embeddings
        """
        elastic_endpoint = cloud_id or os.getenv('ELASTIC_CLOUD_ID')
        self.api_key = api_key or os.getenv('ELASTIC_API_KEY')
        self.gemini = gemini_client
        
        # Initialize Elasticsearch client
        # Support both Cloud ID and direct URL
        if elastic_endpoint and elastic_endpoint.startswith('http'):
            # Direct URL
            self.es = AsyncElasticsearch(
                hosts=[elastic_endpoint],
                api_key=self.api_key,
                verify_certs=True
            )
        else:
            # Cloud ID
            self.es = AsyncElasticsearch(
                cloud_id=elastic_endpoint,
                api_key=self.api_key
            )
        
        # Index names
        self.bee_activities_index = "omk_hive_bee_activities"
        self.knowledge_base_index = "omk_hive_knowledge_base"
        self.transactions_index = "omk_hive_transactions"
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize indices and mappings"""
        try:
            # Create bee activities index
            await self._create_bee_activities_index()
            
            # Create knowledge base index
            await self._create_knowledge_base_index()
            
            # Create transactions index
            await self._create_transactions_index()
            
            self.initialized = True
            logger.info("Elastic Search initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Elastic Search: {str(e)}")
            raise
    
    async def _create_bee_activities_index(self):
        """Create index for bee activities with vector embeddings"""
        
        if await self.es.indices.exists(index=self.bee_activities_index):
            logger.info(f"Index {self.bee_activities_index} already exists")
            return
        
        mapping = {
            "mappings": {
                "properties": {
                    "bee_name": {"type": "keyword"},
                    "bee_id": {"type": "integer"},
                    "action": {"type": "text"},
                    "action_type": {"type": "keyword"},
                    "data": {"type": "object", "enabled": False},  # Store raw JSON
                    "result": {"type": "object", "enabled": False},
                    "success": {"type": "boolean"},
                    "error": {"type": "text"},
                    "timestamp": {"type": "date"},
                    "duration_ms": {"type": "float"},
                    
                    # Vector embedding for semantic search
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 768,  # Gemini embedding dimension
                        "index": True,
                        "similarity": "cosine"
                    },
                    
                    # Transaction specific fields
                    "tx_hash": {"type": "keyword"},
                    "chain": {"type": "keyword"},
                    "pool_address": {"type": "keyword"},
                    "token_address": {"type": "keyword"},
                    
                    # Tags for filtering
                    "tags": {"type": "keyword"}
                }
            }
        }
        
        await self.es.indices.create(index=self.bee_activities_index, body=mapping)
        logger.info(f"Created index: {self.bee_activities_index}")
    
    async def _create_knowledge_base_index(self):
        """Create index for Queen AI knowledge base"""
        
        if await self.es.indices.exists(index=self.knowledge_base_index):
            return
        
        mapping = {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "category": {"type": "keyword"},
                    "source": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 768,
                        "index": True,
                        "similarity": "cosine"
                    },
                    
                    "metadata": {"type": "object", "enabled": False}
                }
            }
        }
        
        await self.es.indices.create(index=self.knowledge_base_index, body=mapping)
        logger.info(f"Created index: {self.knowledge_base_index}")
    
    async def _create_transactions_index(self):
        """Create index for blockchain transactions"""
        
        if await self.es.indices.exists(index=self.transactions_index):
            return
        
        mapping = {
            "mappings": {
                "properties": {
                    "tx_hash": {"type": "keyword"},
                    "chain": {"type": "keyword"},
                    "from_address": {"type": "keyword"},
                    "to_address": {"type": "keyword"},
                    "value": {"type": "float"},
                    "gas_price": {"type": "float"},
                    "status": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "block_number": {"type": "long"},
                    
                    # For full-text search of transaction context
                    "description": {"type": "text"},
                    
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 768,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
        }
        
        await self.es.indices.create(index=self.transactions_index, body=mapping)
        logger.info(f"Created index: {self.transactions_index}")
    
    async def log_bee_activity(
        self,
        bee_name: str,
        action: str,
        data: Dict[str, Any],
        result: Optional[Dict] = None,
        success: bool = True,
        error: Optional[str] = None,
        duration_ms: Optional[float] = None,
        tags: Optional[List[str]] = None
    ):
        """
        Log bee activity to Elasticsearch
        
        Automatically generates vector embedding for semantic search
        """
        try:
            # Generate text for embedding
            text_for_embedding = f"{bee_name} {action} {str(data)}"
            
            # Get embedding from Gemini
            embedding = await self._get_embedding(text_for_embedding) if self.gemini else None
            
            # Extract relevant fields
            tx_hash = data.get('tx_hash') or data.get('signature')
            chain = data.get('chain')
            
            doc = {
                "bee_name": bee_name,
                "action": action,
                "action_type": data.get('type', 'unknown'),
                "data": data,
                "result": result,
                "success": success,
                "error": error,
                "timestamp": datetime.utcnow(),
                "duration_ms": duration_ms,
                "tx_hash": tx_hash,
                "chain": chain,
                "tags": tags or [],
                "embedding": embedding
            }
            
            await self.es.index(
                index=self.bee_activities_index,
                document=doc
            )
            
            logger.debug(f"Logged activity: {bee_name} - {action}")
        
        except Exception as e:
            logger.error(f"Failed to log bee activity: {str(e)}")
    
    async def hybrid_search(
        self,
        query: str,
        index: str = None,
        filters: Optional[Dict] = None,
        size: int = 10
    ) -> List[Dict]:
        """
        Hybrid search: Vector (semantic) + Keyword
        
        Args:
            query: Search query
            index: Index to search (defaults to bee_activities)
            filters: Additional filters (e.g., {"bee_name": "blockchain"})
            size: Number of results
            
        Returns:
            List of matching documents
        """
        if index is None:
            index = self.bee_activities_index
        
        # Get query embedding
        query_embedding = await self._get_embedding(query) if self.gemini else None
        
        # Build hybrid query
        must_clauses = []
        should_clauses = []
        
        # Keyword search
        should_clauses.append({
            "multi_match": {
                "query": query,
                "fields": ["action^2", "bee_name", "error"],
                "type": "best_fields"
            }
        })
        
        # Vector search (if embedding available)
        if query_embedding:
            should_clauses.append({
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": query_embedding}
                    }
                }
            })
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                must_clauses.append({"term": {field: value}})
        
        search_query = {
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "should": should_clauses,
                    "minimum_should_match": 1
                }
            },
            "size": size,
            "sort": ["_score", {"timestamp": "desc"}]
        }
        
        response = await self.es.search(
            index=index,
            body=search_query
        )
        
        results = []
        for hit in response['hits']['hits']:
            result = hit['_source']
            result['_score'] = hit['_score']
            results.append(result)
        
        return results
    
    async def rag_query(
        self,
        question: str,
        context_size: int = 5
    ) -> Dict[str, Any]:
        """
        RAG (Retrieval Augmented Generation) query
        
        1. Search Elastic for relevant context
        2. Pass context to Gemini
        3. Generate answer
        
        Args:
            question: User's question
            context_size: Number of context documents
            
        Returns:
            {
                "answer": str,
                "context": List[Dict],
                "sources": List[str]
            }
        """
        # Step 1: Search for relevant context
        context_docs = await self.hybrid_search(
            query=question,
            size=context_size
        )
        
        if not context_docs:
            return {
                "answer": "I don't have enough information to answer that question.",
                "context": [],
                "sources": []
            }
        
        # Step 2: Build context for Gemini
        context_text = "\n\n".join([
            f"[{doc['bee_name']}] {doc['action']}: {doc.get('result', '')}"
            for doc in context_docs
        ])
        
        # Step 3: Generate answer with Gemini
        if self.gemini:
            prompt = f"""Based on the following context from the OMK Hive system:

{context_text}

Question: {question}

Provide a clear, concise answer based only on the context provided. If you cannot answer from the context, say so."""
            
            # Use Gemini to generate answer
            answer = await self._generate_with_gemini(prompt)
        else:
            answer = f"Context found. Gemini not available for answer generation."
        
        return {
            "answer": answer,
            "context": context_docs,
            "sources": [doc.get('tx_hash', doc.get('bee_name', 'unknown')) for doc in context_docs]
        }
    
    async def conversational_search(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Conversational interface for Queen AI
        
        Examples:
        - "Show me all failed bridge transactions"
        - "Why did the last swap fail?"
        - "What's the average gas price today?"
        """
        # Use RAG to answer
        rag_result = await self.rag_query(query)
        
        # Format response conversationally
        response = f"{rag_result['answer']}\n\n"
        
        if rag_result['sources']:
            response += f"Sources: {', '.join(rag_result['sources'][:3])}"
        
        return response
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Get vector embedding from Gemini"""
        if not self.gemini:
            return None
        
        try:
            # Use Gemini's embedding API
            # This is a placeholder - actual implementation depends on Gemini SDK
            # embedding_result = await self.gemini.embed_content(text)
            # return embedding_result.embedding
            
            # For now, return None (will skip vector search)
            return None
        
        except Exception as e:
            logger.error(f"Failed to get embedding: {str(e)}")
            return None
    
    async def _generate_with_gemini(self, prompt: str) -> str:
        """Generate text with Gemini"""
        if not self.gemini:
            return "Gemini not available"
        
        try:
            # Placeholder for actual Gemini generation
            # response = await self.gemini.generate_content(prompt)
            # return response.text
            
            return "Answer would be generated by Gemini here."
        
        except Exception as e:
            logger.error(f"Failed to generate with Gemini: {str(e)}")
            return f"Error generating answer: {str(e)}"
    
    async def close(self):
        """Close Elasticsearch connection"""
        await self.es.close()


# Global instance
elastic_search = None
