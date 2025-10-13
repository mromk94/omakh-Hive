"""
Database Models and Storage Layer
Simple JSON file storage for now, can migrate to PostgreSQL later
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Data files
USERS_FILE = DATA_DIR / "users.json"
OTC_REQUESTS_FILE = DATA_DIR / "otc_requests.json"
ANALYTICS_FILE = DATA_DIR / "analytics.json"
SYSTEM_CONFIG_FILE = DATA_DIR / "system_config.json"

def load_json(file_path: Path, default: Any = None) -> Any:
    """Load JSON file"""
    if not file_path.exists():
        return default if default is not None else []
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return default if default is not None else []

def save_json(file_path: Path, data: Any):
    """Save JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving {file_path}: {e}")

# ==================== USERS ====================

def get_all_users() -> List[Dict]:
    """Get all users"""
    return load_json(USERS_FILE, [])

def get_user_by_id(user_id: int):
    """Get user by ID"""
    from app.database.connection import SessionLocal
    from app.database.models import User
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        return {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role.value,
            'wallet_address': user.wallet_address,
            'omk_balance': float(user.omk_balance),
            'total_invested_usd': float(user.total_invested_usd),
            'is_active': user.is_active,
            'is_verified': user.is_verified,
            'email_verified_at': user.email_verified_at.isoformat() if user.email_verified_at else None,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    finally:
        db.close()

def get_user_by_email(email: str):
    """Get user by email"""
    users = get_all_users()
    return next((u for u in users if u['email'] == email), None)

def update_user(user_id: int, data: dict):
    """Update user data"""
    from app.database.connection import SessionLocal
    from app.database.models import User
    from datetime import datetime
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Update fields
        for key, value in data.items():
            if hasattr(user, key):
                if key == 'email_verified_at' and isinstance(value, str):
                    setattr(user, key, datetime.fromisoformat(value))
                else:
                    setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        
        return {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role.value,
            'is_active': user.is_active,
            'is_verified': user.is_verified
        }
    finally:
        db.close()

def create_user(user_data: Dict) -> Dict:
    """Create new user"""
    users = get_all_users()
    
    user = {
        'id': len(users) + 1,
        'created_at': datetime.now().isoformat(),
        **user_data
    }
    
    users.append(user)
    save_json(USERS_FILE, users)
    return user

# ==================== OTC REQUESTS ====================

def get_all_otc_requests(status: Optional[str] = None) -> List[Dict]:
    """Get all OTC requests, optionally filtered by status"""
    requests = load_json(OTC_REQUESTS_FILE, [])
    
    if status:
        requests = [r for r in requests if r.get('status') == status]
    
    return requests

def get_otc_request_by_id(request_id: str) -> Optional[Dict]:
    """Get OTC request by ID"""
    requests = get_all_otc_requests()
    return next((r for r in requests if r['id'] == request_id), None)

def create_otc_request(request_data: Dict) -> Dict:
    """Create new OTC request"""
    requests = get_all_otc_requests()
    
    request = {
        'id': f"OTC-{str(len(requests) + 1).zfill(3)}",
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        **request_data
    }
    
    requests.append(request)
    save_json(OTC_REQUESTS_FILE, requests)
    return request

def update_otc_request(request_id: str, updates: Dict) -> Optional[Dict]:
    """Update OTC request"""
    requests = get_all_otc_requests()
    
    for i, request in enumerate(requests):
        if request['id'] == request_id:
            requests[i].update(updates)
            requests[i]['updated_at'] = datetime.now().isoformat()
            save_json(OTC_REQUESTS_FILE, requests)
            return requests[i]
    
    return None

def approve_otc_request(request_id: str, approved_by: str) -> Optional[Dict]:
    """Approve OTC request"""
    return update_otc_request(request_id, {
        'status': 'approved',
        'approved_by': approved_by,
        'approved_at': datetime.now().isoformat()
    })

def reject_otc_request(request_id: str, reason: str, rejected_by: str) -> Optional[Dict]:
    """Reject OTC request"""
    return update_otc_request(request_id, {
        'status': 'rejected',
        'rejection_reason': reason,
        'rejected_by': rejected_by,
        'rejected_at': datetime.now().isoformat()
    })

# ==================== ANALYTICS ====================

def get_analytics() -> Dict:
    """Get analytics data"""
    analytics = load_json(ANALYTICS_FILE, {
        'total_users': 0,
        'active_users_24h': 0,
        'total_omk_distributed': 0,
        'total_revenue_usd': 0,
        'transactions': [],
        'user_signups': []
    })
    
    # Calculate real stats from users and OTC requests
    users = get_all_users()
    otc_requests = get_all_otc_requests()
    
    analytics['total_users'] = len(users)
    analytics['pending_otc_requests'] = len([r for r in otc_requests if r['status'] == 'pending'])
    
    # Calculate revenue from approved OTC requests
    approved_requests = [r for r in otc_requests if r['status'] == 'approved']
    analytics['total_revenue_usd'] = sum(float(r.get('amount_usd', 0)) for r in approved_requests)
    analytics['total_omk_distributed'] = sum(float(r.get('allocation', 0)) for r in approved_requests)
    
    return analytics

def update_analytics(data: Dict):
    """Update analytics data"""
    analytics = get_analytics()
    analytics.update(data)
    save_json(ANALYTICS_FILE, analytics)

def log_transaction(tx_data: dict):
    """Log transaction for analytics"""
    analytics = get_analytics()
    
    tx = {
        'timestamp': datetime.now().isoformat(),
        **tx_data
    }
    
    if 'transactions' not in analytics:
        analytics['transactions'] = []
    
    analytics['transactions'].append(tx)
    save_json(ANALYTICS_FILE, analytics)

def log_user_signup(user_data: Dict):
    """Log a user signup"""
    analytics = get_analytics()
    
    signup = {
        'timestamp': datetime.now().isoformat(),
        **user_data
    }
    
    if 'user_signups' not in analytics:
        analytics['user_signups'] = []
    
    analytics['user_signups'].append(signup)
    analytics['total_users'] = analytics.get('total_users', 0) + 1
    save_json(ANALYTICS_FILE, analytics)

# ==================== SYSTEM CONFIG ====================

def get_system_config() -> Dict:
    """Get system configuration"""
    default_config = {
        'otc_phase': 'private_sale',
        'treasury_wallets': {
            'usdt': '',
            'usdc': '',
            'dai': '',
            'eth': ''
        },
        'payment_methods_enabled': {
            'usdt': True,
            'usdc': True,
            'dai': True,
            'eth': False
        },
        'otc_enabled': True,
        'tge_completed': False,
        'tge_date': '2025-12-31T00:00:00Z',  # Configurable TGE date
        'omk_price_usd': 0.10,
        'private_sale_min_usd': 10000.0,
        'standard_otc_min_usd': 100.0,
        'allow_property_investment': True,
        'allow_staking': False,
        'allow_governance': False,
        'maintenance_mode': False,
        'maintenance_message': None,
        'updated_at': datetime.now().isoformat()
    }
    
    config = load_json(SYSTEM_CONFIG_FILE, default_config)
    return config

def update_system_config(updates: Dict) -> Dict:
    """Update system configuration"""
    config = get_system_config()
    config.update(updates)
    config['updated_at'] = datetime.now().isoformat()
    save_json(SYSTEM_CONFIG_FILE, config)
    return config

def get_active_otc_flow() -> str:
    """Get active OTC flow based on config"""
    config = get_system_config()
    
    if not config.get('otc_enabled'):
        return 'disabled'
    
    phase = config.get('otc_phase', 'private_sale')
    
    if phase == 'private_sale':
        return 'private_sale'
    elif phase == 'standard':
        return 'standard_otc'
    else:
        return 'disabled'

# Initialize files if they don't exist
def initialize_database():
    """Initialize database files"""
    if not USERS_FILE.exists():
        save_json(USERS_FILE, [])
    
    if not OTC_REQUESTS_FILE.exists():
        save_json(OTC_REQUESTS_FILE, [])
    
    if not ANALYTICS_FILE.exists():
        save_json(ANALYTICS_FILE, {
            'total_users': 0,
            'active_users_24h': 0,
            'total_omk_distributed': 0,
            'total_revenue_usd': 0,
            'transactions': [],
            'user_signups': []
        })
    
    if not SYSTEM_CONFIG_FILE.exists():
        get_system_config()  # This will create with defaults

# Initialize on import
initialize_database()

# ==================== PRIVATE INVESTORS ====================

# In-memory storage for private investors (can move to DB table later)
_private_investors = []

def get_all_private_investors() -> List[Dict]:
    """Get all private investors"""
    return _private_investors

def create_private_investor(data: Dict) -> Dict:
    """Create new private investor"""
    # Check if investor_id already exists
    if any(inv['investor_id'] == data['investor_id'] for inv in _private_investors):
        raise ValueError(f"Investor {data['investor_id']} already exists")
    
    investor = {
        **data,
        'id': len(_private_investors) + 1
    }
    _private_investors.append(investor)
    return investor

def get_private_investor(investor_id: str) -> Optional[Dict]:
    """Get private investor by ID"""
    return next((inv for inv in _private_investors if inv['investor_id'] == investor_id), None)

def update_private_investor(investor_id: str, data: Dict) -> Optional[Dict]:
    """Update private investor"""
    for inv in _private_investors:
        if inv['investor_id'] == investor_id:
            inv.update(data)
            return inv
    return None
