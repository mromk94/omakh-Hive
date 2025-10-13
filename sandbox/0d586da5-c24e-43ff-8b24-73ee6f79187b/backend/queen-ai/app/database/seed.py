"""
Database Seeding - Create initial admin and demo users
"""
from sqlalchemy.orm import Session
from .models import User, UserRole, SystemConfig
from .auth import get_password_hash
from datetime import datetime
import json

def seed_users(db: Session):
    """Create admin and demo users"""
    
    # Check if admin already exists
    admin = db.query(User).filter(User.email == "king@omakh.io").first()
    if not admin:
        # Note: Password is "Admin2025!!" (shorter for bcrypt 72-byte limit)
        admin = User(
            email="king@omakh.io",
            password_hash=get_password_hash("Admin2025!!"),
            full_name="King Admin",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            email_verified_at=datetime.utcnow(),
            omk_balance=0.0,
            total_invested_usd=0.0
        )
        db.add(admin)
        print("✅ Created admin user: king@omakh.io")
    else:
        print("ℹ️  Admin user already exists")
    
    # Create demo users
    demo_users = [
        {
            "email": "demo1@omakh.io",
            "full_name": "Demo User 1",
            "omk_balance": 50000.0,
            "total_invested_usd": 5000.0,
            "wallet_address": "0x1234567890123456789012345678901234567890"
        },
        {
            "email": "demo2@omakh.io",
            "full_name": "Demo User 2",
            "omk_balance": 100000.0,
            "total_invested_usd": 10000.0,
            "wallet_address": "0x0987654321098765432109876543210987654321"
        }
    ]
    
    for demo_data in demo_users:
        existing = db.query(User).filter(User.email == demo_data["email"]).first()
        if not existing:
            demo_user = User(
                email=demo_data["email"],
                password_hash=get_password_hash("demouser1234"),
                full_name=demo_data["full_name"],
                role=UserRole.USER,
                is_active=True,
                is_verified=True,
                email_verified_at=datetime.utcnow(),
                omk_balance=demo_data["omk_balance"],
                total_invested_usd=demo_data["total_invested_usd"],
                wallet_address=demo_data.get("wallet_address")
            )
            db.add(demo_user)
            print(f"✅ Created demo user: {demo_data['email']}")
        else:
            print(f"ℹ️  Demo user already exists: {demo_data['email']}")
    
    db.commit()
    print("✅ User seeding completed")

def seed_system_config(db: Session):
    """Create initial system configuration"""
    
    configs = [
        {
            "key": "otc_phase",
            "value": {"phase": "private_sale"},
            "description": "Current OTC phase: private_sale, standard, or disabled"
        },
        {
            "key": "treasury_wallets",
            "value": {
                "usdt": "",
                "usdc": "",
                "dai": "",
                "eth": ""
            },
            "description": "Treasury wallet addresses for OTC payments"
        },
        {
            "key": "payment_methods_enabled",
            "value": {
                "usdt": True,
                "usdc": True,
                "dai": True,
                "eth": False
            },
            "description": "Enabled payment methods for OTC"
        },
        {
            "key": "tge_date",
            "value": {"date": "2025-12-31T00:00:00Z"},
            "description": "Token Generation Event date"
        },
        {
            "key": "omk_price_usd",
            "value": {"price": 0.10},
            "description": "OMK token price in USD"
        },
        {
            "key": "feature_flags",
            "value": {
                "otc_enabled": True,
                "property_investment": True,
                "staking": False,
                "governance": False,
                "maintenance_mode": False
            },
            "description": "Feature flags for platform"
        }
    ]
    
    for config_data in configs:
        existing = db.query(SystemConfig).filter(SystemConfig.key == config_data["key"]).first()
        if not existing:
            config = SystemConfig(
                key=config_data["key"],
                value=config_data["value"],
                description=config_data["description"]
            )
            db.add(config)
            print(f"✅ Created config: {config_data['key']}")
        else:
            print(f"ℹ️  Config already exists: {config_data['key']}")
    
    db.commit()
    print("✅ System config seeding completed")

def seed_all(db: Session):
    """Run all seeding"""
    print("\n🌱 Starting database seeding...")
    seed_users(db)
    seed_system_config(db)
    print("\n✅ All seeding completed!\n")
