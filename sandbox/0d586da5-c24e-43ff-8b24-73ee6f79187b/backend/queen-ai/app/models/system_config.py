"""
System Configuration Model
Manages global system settings including OTC phases
"""

from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class OTCPhase(str, Enum):
    """OTC Sale Phases"""
    PRIVATE_SALE = "private_sale"  # Pre-TGE - Manual approval required
    STANDARD = "standard"           # Post-TGE - Instant swaps via dispenser
    DISABLED = "disabled"           # OTC completely disabled

class SystemConfig(BaseModel):
    """Global system configuration"""
    
    # OTC Settings
    otc_phase: OTCPhase = OTCPhase.PRIVATE_SALE
    otc_enabled: bool = True
    
    # TGE Status
    tge_completed: bool = False
    tge_date: Optional[datetime] = None
    
    # OMK Token
    omk_price_usd: float = 0.10
    
    # Limits
    private_sale_min_usd: float = 10000.0  # $10k minimum for private sale
    standard_otc_min_usd: float = 100.0     # $100 minimum for standard OTC
    
    # Feature Flags
    allow_property_investment: bool = True
    allow_staking: bool = False
    allow_governance: bool = False
    
    # Maintenance
    maintenance_mode: bool = False
    maintenance_message: Optional[str] = None
    
    class Config:
        use_enum_values = True

# Global config instance (in production, load from database)
_config = SystemConfig()

def get_config() -> SystemConfig:
    """Get current system configuration"""
    return _config

def update_config(**kwargs) -> SystemConfig:
    """Update system configuration"""
    global _config
    for key, value in kwargs.items():
        if hasattr(_config, key):
            setattr(_config, key, value)
    return _config

def get_active_otc_flow() -> str:
    """Determine which OTC flow to show users"""
    config = get_config()
    
    if not config.otc_enabled:
        return "disabled"
    
    if config.otc_phase == OTCPhase.PRIVATE_SALE:
        return "private_sale"
    elif config.otc_phase == OTCPhase.STANDARD:
        return "standard_otc"
    else:
        return "disabled"
