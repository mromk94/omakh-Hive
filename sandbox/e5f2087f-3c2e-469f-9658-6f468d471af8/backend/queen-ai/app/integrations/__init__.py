"""
Integration modules for external services

- Elastic Search (AI-powered search & RAG)
- BigQuery (Analytics via Fivetran)
"""
from app.integrations.elastic_search import ElasticSearchIntegration

__all__ = ['ElasticSearchIntegration']
