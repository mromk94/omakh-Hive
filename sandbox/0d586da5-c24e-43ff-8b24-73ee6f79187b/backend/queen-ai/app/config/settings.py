"""
Configuration Settings for Queen AI
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Database - MySQL (Cloud SQL compatible)
    DATABASE_URL: str = "mysql+pymysql://root:@localhost:3306/omk-hive1"
    
    # Redis (Use Memorystore in Google Cloud)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Message Bus
    MESSAGE_BUS_TYPE: str = "redis"  # or "kafka"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    # LLM Providers
    DEFAULT_LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROK_API_KEY: Optional[str] = None
    
    # Google Cloud (for Gemini via Vertex AI)
    GCP_PROJECT_ID: Optional[str] = None
    GCP_LOCATION: str = "us-central1"
    GCP_CREDENTIALS_PATH: Optional[str] = None
    
    # Blockchain - Ethereum (Use Infura/Alchemy in production)
    ETHEREUM_RPC_URL: str = "https://eth-mainnet.g.alchemy.com/v2/demo"
    ETHEREUM_CHAIN_ID: int = 1
    QUEEN_WALLET_PRIVATE_KEY: Optional[str] = None
    
    # Smart Contract Addresses (from PRIME2)
    OMK_TOKEN_ADDRESS: Optional[str] = None
    QUEEN_CONTROLLER_ADDRESS: Optional[str] = None
    BEE_SPAWNER_ADDRESS: Optional[str] = None
    ECOSYSTEM_MANAGER_ADDRESS: Optional[str] = None
    TREASURY_VAULT_ADDRESS: Optional[str] = None
    GOVERNANCE_MANAGER_ADDRESS: Optional[str] = None
    OMK_BRIDGE_ADDRESS: Optional[str] = None
    SYSTEM_DASHBOARD_ADDRESS: Optional[str] = None
    
    # Blockchain - Solana
    SOLANA_RPC_URL: str = "https://api.devnet.solana.com"
    SOLANA_BRIDGE_PROGRAM_ID: Optional[str] = None
    
    # Fetch.ai / ASI
    FETCH_NETWORK: str = "testnet"
    FETCH_MNEMONIC: Optional[str] = None
    ASI_ENABLED: bool = False
    
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    ADMIN_API_KEYS: List[str] = []
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    
    # CORS (Update with production URLs for cloud deployment)
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
        "https://*.run.app",  # Cloud Run
        "https://*.appspot.com",  # App Engine
    ]
    
    # Learning Function
    LEARNING_FUNCTION_ENABLED: bool = False  # Disabled by default (opt-in)
    LEARNING_STORAGE_TYPE: str = "bigquery"  # local, gcs, or bigquery
    LEARNING_STORAGE_PATH: str = "/tmp/learning"  # Use /tmp for cloud (ephemeral)
    LEARNING_STORAGE_BUCKET: Optional[str] = None
    LEARNING_BATCH_SIZE: int = 100  # Batch inserts for cost optimization
    LEARNING_RETENTION_DAYS: int = 365  # 1 year data retention
    
    # BigQuery (for learning function - follows google_cloud_strategy.md)
    BIGQUERY_DATASET: str = "omk_hive_learning"
    BIGQUERY_ENABLED: bool = False  # Requires GCP setup
    
    # Secret Manager (for production credentials)
    SECRET_MANAGER_ENABLED: bool = False
    SECRET_KEY: str = "development-secret-key-change-in-production"
    
    # Queen AI Behavior
    QUEEN_DECISION_INTERVAL: int = 300  # 5 minutes
    QUEEN_MONITORING_INTERVAL: int = 30  # 30 seconds
    QUEEN_MAX_DAILY_PROPOSALS: int = 100
    QUEEN_PROPOSAL_CONFIDENCE_THRESHOLD: float = 0.75
    
    # Bee Management
    BEE_HEALTH_CHECK_INTERVAL: int = 60  # 60 seconds
    BEE_MAX_TASK_TIMEOUT: int = 300  # 5 minutes
    BEE_RETRY_ATTEMPTS: int = 3
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from env

settings = Settings()
