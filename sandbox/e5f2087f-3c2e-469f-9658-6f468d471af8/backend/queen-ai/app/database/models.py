"""
Database Models using SQLAlchemy ORM
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, Enum, JSON
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .connection import Base

# ==================== ENUMS ====================

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class OTCStatus(str, enum.Enum):
    PENDING = "pending"
    PAYMENT_RECEIVED = "payment_received"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

class PaymentToken(str, enum.Enum):
    USDT = "USDT"
    USDC = "USDC"
    DAI = "DAI"
    ETH = "ETH"

# ==================== MODELS ====================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    wallet_address = Column(String(42), index=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    
    # Profile
    phone = Column(String(50))
    country = Column(String(100))
    kyc_verified = Column(Boolean, default=False)
    kyc_submitted_at = Column(DateTime)
    kyc_verified_at = Column(DateTime)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime)
    
    # Portfolio
    omk_balance = Column(Float, default=0.0)
    total_invested_usd = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)

class OTCRequest(Base):
    __tablename__ = "otc_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True)
    
    # Contact info
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    wallet_address = Column(String(42), nullable=False)
    
    # Purchase details
    omk_amount = Column(Float, nullable=False)
    price_per_token = Column(Float, default=0.10)
    total_usd = Column(Float, nullable=False)
    
    # Payment details
    payment_token = Column(Enum(PaymentToken), default=PaymentToken.USDT)
    tx_hash = Column(String(66))
    payment_screenshot = Column(Text)
    treasury_wallet = Column(String(42))
    
    # Status
    status = Column(Enum(OTCStatus), default=OTCStatus.PENDING, nullable=False)
    requires_approval = Column(Boolean, default=False)
    payment_verified = Column(Boolean, default=False)
    
    # Admin actions
    approved_by = Column(Integer)
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    admin_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, index=True, nullable=False)
    value = Column(JSON, nullable=False)
    description = Column(Text)
    updated_by = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    tx_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True)
    
    # Transaction details
    type = Column(String(50), nullable=False)  # otc_purchase, swap, stake, etc.
    amount_omk = Column(Float)
    amount_usd = Column(Float)
    token = Column(String(20))
    
    # Blockchain
    tx_hash = Column(String(66))
    block_number = Column(Integer)
    gas_used = Column(Float)
    
    # Status
    status = Column(String(50), default="pending")
    
    # Extra data (renamed from metadata to avoid SQLAlchemy conflict)
    extra_data = Column(JSON)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class QueenAILog(Base):
    __tablename__ = "queen_ai_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_id = Column(String(100), index=True)
    
    # Message
    role = Column(String(20), nullable=False)  # user, ai, system
    message = Column(Text, nullable=False)
    
    # Context
    action_taken = Column(String(100))
    context_data = Column(JSON)  # Renamed from metadata
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Property details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    property_type = Column(String(50))
    
    # Investment details
    total_value_usd = Column(Float, nullable=False)
    token_price = Column(Float, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    tokens_sold = Column(Integer, default=0)
    min_investment_tokens = Column(Integer, default=1)
    
    # Returns
    expected_annual_return = Column(Float)
    rental_yield = Column(Float)
    occupancy_rate = Column(Float)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_funded = Column(Boolean, default=False)
    funded_at = Column(DateTime)
    
    # Media
    images = Column(JSON)
    documents = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class PropertyInvestment(Base):
    __tablename__ = "property_investments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    property_id = Column(Integer, index=True, nullable=False)
    
    # Investment
    tokens_purchased = Column(Integer, nullable=False)
    price_per_token = Column(Float, nullable=False)
    total_invested_usd = Column(Float, nullable=False)
    
    # Returns
    total_earned_usd = Column(Float, default=0.0)
    last_payout_at = Column(DateTime)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), index=True, nullable=False)
    user_id = Column(Integer, index=True)
    
    # Event data
    event_data = Column(JSON)
    page = Column(String(255))
    referrer = Column(String(500))
    
    # User agent
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
