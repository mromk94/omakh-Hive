"""
Authentication API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import timedelta, datetime
from typing import Optional

from app.database.connection import get_db
from app.database.models import User, UserRole
from app.database.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
import structlog

router = APIRouter()
logger = structlog.get_logger()

# ==================== REQUEST/RESPONSE MODELS ====================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    wallet_address: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    wallet_address: Optional[str]
    role: str
    omk_balance: float
    total_invested_usd: float
    is_active: bool
    is_verified: bool
    created_at: datetime

# ==================== ENDPOINTS ====================

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password
    Returns JWT access token
    """
    user = authenticate_user(db, request.email, request.password)
    
    if not user:
        logger.warning("Failed login attempt", email=request.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    logger.info("User logged in", user_id=user.id, email=user.email, role=user.role.value)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "wallet_address": user.wallet_address,
            "role": user.role.value,
            "omk_balance": user.omk_balance,
            "total_invested_usd": user.total_invested_usd,
            "is_active": user.is_active,
            "is_verified": user.is_verified
        }
    }

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register new user account
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        full_name=request.full_name,
        wallet_address=request.wallet_address,
        role=UserRole.USER,
        is_active=True,
        is_verified=False,
        omk_balance=0.0,
        total_invested_usd=0.0
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email, "role": new_user.role.value},
        expires_delta=access_token_expires
    )
    
    logger.info("New user registered", user_id=new_user.id, email=new_user.email)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "wallet_address": new_user.wallet_address,
            "role": new_user.role.value,
            "omk_balance": new_user.omk_balance,
            "total_invested_usd": new_user.total_invested_usd,
            "is_active": new_user.is_active,
            "is_verified": new_user.is_verified
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current logged in user information
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "wallet_address": current_user.wallet_address,
        "role": current_user.role.value,
        "omk_balance": current_user.omk_balance,
        "total_invested_usd": current_user.total_invested_usd,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at
    }

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user
    (JWT tokens are stateless, so this is mainly for client-side cleanup)
    """
    logger.info("User logged out", user_id=current_user.id, email=current_user.email)
    return {"message": "Successfully logged out"}
