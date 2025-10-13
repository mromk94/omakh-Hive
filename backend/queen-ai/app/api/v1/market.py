"""
Market Data API Endpoints

Real-time market data provided by MarketDataAgent
- Crypto prices (BTC, ETH, SOL)
- OMK token data (on-chain or OTC)
- Liquidity pools
- Crypto news
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/market", tags=["Market Data"])


@router.get("/data")
async def get_market_data(request: Request):
    """
    Get comprehensive market data
    
    Returns:
    - OMK token stats (price, market cap, supply)
    - Crypto market data (BTC, ETH, SOL prices)
    - Liquidity pool information
    - Latest crypto news
    - Data sources and last updated time
    """
    try:
        queen = request.app.state.queen
        agent = queen.market_data_agent
        
        data = await agent.get_comprehensive_data()
        
        return {
            "success": True,
            "data": data
        }
        
    except Exception as e:
        logger.error("Failed to get market data", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch market data"
        )


@router.get("/omk")
async def get_omk_data(request: Request):
    """
    Get OMK-specific market data
    
    Returns either:
    - On-chain data (if contract address set)
    - OTC data (calculated from Queen's bees)
    """
    try:
        queen = request.app.state.queen
        agent = queen.market_data_agent
        
        omk_data = await agent.fetch_omk_data()
        
        return {
            "success": True,
            "data": omk_data,
            "source": omk_data.get("data_source", "unknown")
        }
        
    except Exception as e:
        logger.error("Failed to get OMK data", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch OMK data"
        )


@router.get("/crypto")
async def get_crypto_data(request: Request):
    """
    Get general crypto market data
    
    Returns:
    - BTC, ETH, SOL prices and changes
    - Total market cap
    - 24h trading volume
    """
    try:
        queen = request.app.state.queen
        agent = queen.market_data_agent
        
        crypto_data = await agent.fetch_crypto_market_data()
        
        return {
            "success": True,
            "data": crypto_data
        }
        
    except Exception as e:
        logger.error("Failed to get crypto data", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch crypto data"
        )


@router.get("/news")
async def get_crypto_news(request: Request, limit: int = 10):
    """
    Get latest crypto news
    
    Query params:
    - limit: Number of news items (default 10, max 50)
    """
    try:
        if limit > 50:
            limit = 50
        
        queen = request.app.state.queen
        agent = queen.market_data_agent
        
        news = await agent.fetch_crypto_news()
        
        return {
            "success": True,
            "news": news[:limit],
            "count": len(news)
        }
        
    except Exception as e:
        logger.error("Failed to get crypto news", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch crypto news"
        )


@router.get("/config")
async def get_market_config(request: Request):
    """
    Get market data agent configuration
    
    Returns:
    - OMK contract address (if set)
    - OTC price settings
    - Data sources status
    - Cache settings
    """
    try:
        queen = request.app.state.queen
        agent = queen.market_data_agent
        
        config = agent.get_config()
        
        return {
            "success": True,
            "config": config
        }
        
    except Exception as e:
        logger.error("Failed to get market config", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch configuration"
        )


@router.get("/health")
async def market_health(request: Request):
    """Market data service health check"""
    try:
        queen = request.app.state.queen
        agent = queen.market_data_agent
        
        # Quick health check - just verify agent exists
        config = agent.get_config()
        
        return {
            "status": "healthy",
            "service": "Market Data Agent",
            "data_source": config.get("data_source"),
            "has_api_keys": {
                "coingecko": config.get("has_coingecko_key"),
                "cryptopanic": config.get("has_cryptopanic_key")
            }
        }
        
    except Exception as e:
        logger.error("Market health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e)
        }
