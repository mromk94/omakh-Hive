"""
Database Models - SQLAlchemy ORM Models

All entities for persistent storage in PostgreSQL.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    Text, JSON, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


# Enums
class ProposalStatus(str, enum.Enum):
    ACTIVE = "active"
    APPROVED = "approved_timelock"
    READY = "ready_to_execute"
    EXECUTED = "executed"
    FAILED_QUORUM = "failed_quorum"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ProposalType(str, enum.Enum):
    TREASURY_SPENDING = "treasury_spending"
    PARAMETER_CHANGE = "parameter_change"
    CONTRACT_UPGRADE = "contract_upgrade"
    EMERGENCY_ACTION = "emergency_action"
    ECOSYSTEM_GRANT = "ecosystem_grant"


class PurchaseStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


# Models

class GovernanceProposal(Base):
    """Governance DAO Proposals"""
    __tablename__ = "governance_proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, unique=True, index=True)
    proposer = Column(String(42), nullable=False, index=True)  # Ethereum address
    proposal_type = Column(SQLEnum(ProposalType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    actions = Column(JSON)  # List of actions to execute
    requirements = Column(JSON)  # Quorum, approval thresholds, etc.
    
    # Voting
    voting_start = Column(DateTime, nullable=False)
    voting_end = Column(DateTime, nullable=False)
    timelock_end = Column(DateTime, nullable=True)
    
    # Vote counts
    yes_votes = Column(Float, default=0)
    no_votes = Column(Float, default=0)
    abstain_votes = Column(Float, default=0)
    total_votes = Column(Float, default=0)
    
    # Status
    status = Column(SQLEnum(ProposalStatus), default=ProposalStatus.ACTIVE)
    executed_at = Column(DateTime, nullable=True)
    executed_by = Column(String(42), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    votes = relationship("Vote", back_populates="proposal", cascade="all, delete-orphan")


class Vote(Base):
    """Individual votes on proposals"""
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("governance_proposals.proposal_id"), nullable=False)
    voter = Column(String(42), nullable=False, index=True)  # Ethereum address
    vote = Column(String(10), nullable=False)  # "yes", "no", "abstain"
    voting_power = Column(Float, nullable=False)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    proposal = relationship("GovernanceProposal", back_populates="votes")


class PrivateSalePurchase(Base):
    """Private sale token purchases"""
    __tablename__ = "private_sale_purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    investor_address = Column(String(42), nullable=False, index=True)
    token_amount = Column(Float, nullable=False)
    payment_amount_usd = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)
    
    # Tier breakdown
    tier_breakdown = Column(JSON)  # List of {tier, tokens, cost}
    
    # Status
    status = Column(SQLEnum(PurchaseStatus), default=PurchaseStatus.PENDING)
    kyc_verified = Column(Boolean, default=False)
    whitelist_verified = Column(Boolean, default=False)
    
    # Transaction
    tx_hash = Column(String(66), nullable=True)
    blockchain = Column(String(20), default="ethereum")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    investor = relationship("Investor", back_populates="purchases")


class Investor(Base):
    """Investor information and KYC status"""
    __tablename__ = "investors"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(42), unique=True, nullable=False, index=True)
    
    # KYC
    kyc_status = Column(String(20), default="pending")  # pending, verified, rejected
    kyc_provider = Column(String(50), nullable=True)
    kyc_verified_at = Column(DateTime, nullable=True)
    
    # Whitelist
    is_whitelisted = Column(Boolean, default=False)
    whitelisted_at = Column(DateTime, nullable=True)
    whitelist_tier = Column(String(20), nullable=True)
    
    # Purchase limits
    max_purchase_usd = Column(Float, nullable=True)
    total_purchased_tokens = Column(Float, default=0)
    total_spent_usd = Column(Float, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    purchases = relationship("PrivateSalePurchase", back_populates="investor")


class HivePost(Base):
    """Hive Information Board posts"""
    __tablename__ = "hive_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    author = Column(String(50), nullable=False, index=True)  # Bee name
    category = Column(String(50), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(JSON, nullable=False)  # Flexible content structure
    tags = Column(JSON)  # List of tags
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Stats
    views = Column(Integer, default=0)
    references = Column(Integer, default=0)  # How many times referenced


class Message(Base):
    """Message Bus messages (for audit trail)"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String(50), nullable=False, index=True)
    recipient = Column(String(50), nullable=False, index=True)
    message_type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)
    priority = Column(Integer, default=0)
    
    # Status
    delivered = Column(Boolean, default=False)
    delivered_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class BeeMetrics(Base):
    """Bee performance metrics"""
    __tablename__ = "bee_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    bee_name = Column(String(50), nullable=False, index=True)
    
    # Performance
    task_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    total_response_time = Column(Float, default=0)  # milliseconds
    
    # Status
    status = Column(String(20), default="active")  # active, paused, error
    last_task_time = Column(DateTime, nullable=True)
    last_health_check = Column(DateTime, nullable=True)
    
    # Metadata
    date = Column(DateTime, nullable=False, index=True)  # Daily rollup
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LLMConversation(Base):
    """LLM conversation history"""
    __tablename__ = "llm_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), nullable=False, index=True)
    provider = Column(String(20), nullable=False)  # gemini, openai, anthropic
    model = Column(String(50), nullable=False)
    
    # Conversation
    role = Column(String(20), nullable=False)  # system, user, assistant
    content = Column(Text, nullable=False)
    
    # Metadata
    tokens_used = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class SystemEvent(Base):
    """System events for audit trail"""
    __tablename__ = "system_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_source = Column(String(50), nullable=False)  # queen, bee_name, api, etc.
    severity = Column(String(20), default="info")  # info, warning, error, critical
    
    # Event details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)  # Additional event data
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class StakingPosition(Base):
    """Staking positions"""
    __tablename__ = "staking_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    staker_address = Column(String(42), nullable=False, index=True)
    
    # Staking details
    staked_amount = Column(Float, nullable=False)
    lock_period_days = Column(Integer, nullable=False)  # 30, 90, 180, 365
    apy = Column(Float, nullable=False)
    
    # Dates
    started_at = Column(DateTime, nullable=False)
    unlock_at = Column(DateTime, nullable=False)
    
    # Rewards
    total_rewards = Column(Float, default=0)
    last_reward_claim = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(20), default="active")  # active, unlocked, withdrawn
    withdrawn_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TreasuryTransaction(Base):
    """Treasury transactions"""
    __tablename__ = "treasury_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(String(50), nullable=False)  # allocation, withdrawal, rebalance
    category = Column(String(50), nullable=False)  # development, marketing, etc.
    
    # Amount
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    
    # Details
    description = Column(Text, nullable=True)
    authorized_by = Column(String(50), nullable=True)
    proposal_id = Column(Integer, nullable=True)  # If from governance proposal
    
    # Blockchain
    tx_hash = Column(String(66), nullable=True)
    blockchain = Column(String(20), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
