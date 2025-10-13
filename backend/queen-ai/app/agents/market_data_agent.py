"""
Market Data Agent - Autonomous Data Collector

Fetches real-time market data from multiple sources:
- Crypto prices (BTC, ETH, SOL, etc.) from CoinGecko
- OMK token data (on-chain when available, OTC fallback)
- Crypto news and trends
- Market sentiment

Coordinates with Queen's bees for OTC data calculation.
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import structlog
from decimal import Decimal

logger = structlog.get_logger(__name__)


class MarketDataAgent:
    """
    Autonomous agent for comprehensive market data management
    
    Data Sources:
    - CoinGecko API: Crypto prices and market data
    - CryptoPanic API: Crypto news
    - Blockchain RPC: On-chain OMK data (when contract exists)
    - Queen's Bees: OTC data calculation
    """
    
    def __init__(self, queen_instance):
        self.queen = queen_instance
        
        # API Configuration
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.cryptopanic_base = "https://cryptopanic.com/api/v1"
        
        # API Keys (from environment)
        import os
        self.coingecko_api_key = os.getenv("COINGECKO_API_KEY", "")
        self.cryptopanic_api_key = os.getenv("CRYPTOPANIC_API_KEY", "")
        
        # OMK Token Configuration (set by admin)
        self.omk_contract_address: Optional[str] = None
        self.omk_chain: str = "ethereum"  # ethereum or solana
        self.omk_otc_price: float = 0.10  # Default OTC price, admin can override
        
        # Cache
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: int = 30  # 30 seconds cache
        
        logger.info("MarketDataAgent initialized", 
                   has_coingecko_key=bool(self.coingecko_api_key),
                   has_cryptopanic_key=bool(self.cryptopanic_api_key))
    
    async def get_comprehensive_data(self) -> Dict[str, Any]:
        """
        Get all market data in one call
        Returns comprehensive data for frontend display
        """
        try:
            # Check cache
            cache_key = "comprehensive_data"
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if (datetime.now() - cached_time).seconds < self.cache_ttl:
                    logger.debug("Returning cached comprehensive data")
                    return cached_data
            
            # Fetch all data in parallel
            crypto_data, omk_data, news_data = await asyncio.gather(
                self.fetch_crypto_market_data(),
                self.fetch_omk_data(),
                self.fetch_crypto_news(),
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(crypto_data, Exception):
                logger.error("Failed to fetch crypto data", error=str(crypto_data))
                crypto_data = self._get_fallback_crypto_data()
            
            if isinstance(omk_data, Exception):
                logger.error("Failed to fetch OMK data", error=str(omk_data))
                omk_data = self._get_fallback_omk_data()
            
            if isinstance(news_data, Exception):
                logger.error("Failed to fetch news", error=str(news_data))
                news_data = []
            
            # Combine all data
            comprehensive_data = {
                "omk": omk_data,
                "liquidity": self._calculate_liquidity(omk_data),
                "crypto": crypto_data,
                "news": news_data[:5],  # Top 5 news items
                "last_updated": datetime.now().isoformat(),
                "data_sources": {
                    "omk": "on-chain" if self.omk_contract_address else "otc",
                    "crypto": "coingecko",
                    "news": "cryptopanic"
                }
            }
            
            # Cache result
            self.cache[cache_key] = (comprehensive_data, datetime.now())
            
            return comprehensive_data
            
        except Exception as e:
            logger.error("Failed to get comprehensive data", error=str(e))
            return self._get_complete_fallback_data()
    
    async def fetch_crypto_market_data(self) -> Dict[str, Any]:
        """
        Fetch crypto market data from CoinGecko
        Returns BTC, ETH, SOL prices and global market stats
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Fetch multiple coins at once
                coins_url = f"{self.coingecko_base}/simple/price"
                params = {
                    "ids": "bitcoin,ethereum,solana",
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_market_cap": "true",
                    "include_24hr_vol": "true"
                }
                
                if self.coingecko_api_key:
                    params["x_cg_pro_api_key"] = self.coingecko_api_key
                
                async with session.get(coins_url, params=params) as resp:
                    if resp.status != 200:
                        logger.warning(f"CoinGecko API returned {resp.status}")
                        return self._get_fallback_crypto_data()
                    
                    data = await resp.json()
                
                # Fetch global market data
                global_url = f"{self.coingecko_base}/global"
                async with session.get(global_url) as resp:
                    if resp.status == 200:
                        global_data = await resp.json()
                        total_market_cap = global_data['data']['total_market_cap']['usd']
                        total_volume = global_data['data']['total_volume']['usd']
                    else:
                        total_market_cap = 1750000000000  # Fallback
                        total_volume = 85000000000
                
                return {
                    "btc": {
                        "price": data.get('bitcoin', {}).get('usd', 43250),
                        "change24h": data.get('bitcoin', {}).get('usd_24h_change', 2.14),
                        "market_cap": data.get('bitcoin', {}).get('usd_market_cap', 850000000000),
                        "volume24h": data.get('bitcoin', {}).get('usd_24h_vol', 25000000000)
                    },
                    "eth": {
                        "price": data.get('ethereum', {}).get('usd', 2485),
                        "change24h": data.get('ethereum', {}).get('usd_24h_change', 1.85),
                        "market_cap": data.get('ethereum', {}).get('usd_market_cap', 300000000000),
                        "volume24h": data.get('ethereum', {}).get('usd_24h_vol', 15000000000)
                    },
                    "sol": {
                        "price": data.get('solana', {}).get('usd', 98),
                        "change24h": data.get('solana', {}).get('usd_24h_change', -0.92),
                        "market_cap": data.get('solana', {}).get('usd_market_cap', 45000000000),
                        "volume24h": data.get('solana', {}).get('usd_24h_vol', 2000000000)
                    },
                    "totalMarketCap": total_market_cap,
                    "total24hVolume": total_volume
                }
                
        except Exception as e:
            logger.error("Failed to fetch crypto data from CoinGecko", error=str(e))
            return self._get_fallback_crypto_data()
    
    async def fetch_omk_data(self) -> Dict[str, Any]:
        """
        Fetch OMK token data
        - If contract address set: fetch on-chain data
        - Else: calculate from OTC data via Queen's bees
        """
        if self.omk_contract_address:
            return await self._fetch_onchain_omk_data()
        else:
            return await self._fetch_otc_omk_data()
    
    async def _fetch_onchain_omk_data(self) -> Dict[str, Any]:
        """
        Fetch OMK data from blockchain when contract exists
        """
        try:
            # Get blockchain bee for on-chain queries
            blockchain_bee = self.queen.bee_manager.get_bee("blockchain")
            
            if not blockchain_bee:
                logger.warning("BlockchainBee not available, falling back to OTC data")
                return await self._fetch_otc_omk_data()
            
            # Query contract for token data
            contract_data = await self.queen.bee_manager.execute_bee("blockchain", {
                "type": "get_token_info",
                "contract_address": self.omk_contract_address,
                "chain": self.omk_chain
            })
            
            if not contract_data.get("success"):
                logger.warning("Failed to fetch on-chain data, falling back to OTC")
                return await self._fetch_otc_omk_data()
            
            # Get price from DEX (Uniswap/Raydium)
            price_data = await self.queen.bee_manager.execute_bee("blockchain", {
                "type": "get_dex_price",
                "token_address": self.omk_contract_address,
                "chain": self.omk_chain
            })
            
            price = price_data.get("price", 0.10)
            total_supply = contract_data.get("total_supply", 1000000000)
            circulating = contract_data.get("circulating_supply", 500000000)
            
            return {
                "price": price,
                "marketCap": circulating * price,
                "circulation": circulating,
                "totalSupply": total_supply,
                "volume24h": price_data.get("volume_24h", 2500000),
                "priceChange24h": price_data.get("price_change_24h", 0.0025),
                "priceChangePercent": price_data.get("price_change_percent", 2.56),
                "data_source": "on-chain",
                "contract_address": self.omk_contract_address,
                "chain": self.omk_chain
            }
            
        except Exception as e:
            logger.error("Failed to fetch on-chain OMK data", error=str(e))
            return await self._fetch_otc_omk_data()
    
    async def _fetch_otc_omk_data(self) -> Dict[str, Any]:
        """
        Calculate OMK data from OTC information via Queen's bees
        Coordinates with: TreasuryBee, PrivateSaleBee, MathsBee
        """
        try:
            # 1. Get OTC treasury balance
            treasury_result = await self.queen.bee_manager.execute_bee("treasury", {
                "type": "get_otc_balance"
            })
            otc_treasury_balance = treasury_result.get("balance", 0) if treasury_result.get("success") else 0
            
            # 2. Get all OTC requests to calculate allocated supply
            otc_result = await self.queen.bee_manager.execute_bee("private_sale", {
                "type": "get_all_requests"
            })
            
            if otc_result.get("success"):
                otc_requests = otc_result.get("requests", [])
                
                # Calculate total allocated
                total_allocated = sum(
                    float(req.get("allocation", 0)) 
                    for req in otc_requests 
                    if req.get("status") in ["approved", "pending"]
                )
            else:
                otc_requests = []
                total_allocated = 0
            
            # 3. Calculate weighted average price using MathsBee
            if len(otc_requests) > 0:
                price_result = await self.queen.bee_manager.execute_bee("maths", {
                    "type": "calculate_weighted_average_price",
                    "requests": otc_requests
                })
                calculated_price = price_result.get("average_price", 0.10) if price_result.get("success") else 0.10
            else:
                calculated_price = 0.10
            
            # 4. Admin OTC price takes precedence
            final_price = self.omk_otc_price if self.omk_otc_price > 0 else calculated_price
            
            # 5. Calculate metrics
            available_supply = otc_treasury_balance - total_allocated
            total_supply = 1000000000  # 1B OMK total
            market_cap = total_allocated * final_price
            
            # Mock volume and price change for OTC
            volume_24h = total_allocated * final_price * 0.05  # 5% of market cap
            
            return {
                "price": final_price,
                "marketCap": market_cap,
                "circulation": total_allocated,
                "totalSupply": total_supply,
                "volume24h": volume_24h,
                "priceChange24h": 0.0025,  # Mock for OTC
                "priceChangePercent": 2.56,  # Mock for OTC
                "data_source": "otc",
                "price_source": "admin_set" if self.omk_otc_price > 0 else "calculated",
                "treasury_balance": otc_treasury_balance,
                "available_supply": available_supply,
                "allocated_supply": total_allocated,
                "total_requests": len(otc_requests)
            }
            
        except Exception as e:
            logger.error("Failed to fetch OTC OMK data", error=str(e))
            return self._get_fallback_omk_data()
    
    async def fetch_crypto_news(self) -> List[Dict[str, Any]]:
        """
        Fetch latest crypto news from CryptoPanic
        """
        try:
            if not self.cryptopanic_api_key:
                logger.info("No CryptoPanic API key, returning empty news")
                return []
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.cryptopanic_base}/posts/"
                params = {
                    "auth_token": self.cryptopanic_api_key,
                    "kind": "news",
                    "filter": "hot",
                    "currencies": "BTC,ETH,SOL"
                }
                
                async with session.get(url, params=params) as resp:
                    if resp.status != 200:
                        logger.warning(f"CryptoPanic API returned {resp.status}")
                        return []
                    
                    data = await resp.json()
                    results = data.get("results", [])
                    
                    # Format news items
                    news = []
                    for item in results[:10]:  # Top 10
                        news.append({
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "source": item.get("source", {}).get("title", ""),
                            "published_at": item.get("published_at", ""),
                            "currencies": [c.get("code") for c in item.get("currencies", [])],
                            "sentiment": item.get("votes", {}).get("positive", 0) - item.get("votes", {}).get("negative", 0)
                        })
                    
                    return news
                    
        except Exception as e:
            logger.error("Failed to fetch crypto news", error=str(e))
            return []
    
    def _calculate_liquidity(self, omk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate liquidity pool data"""
        price = omk_data.get("price", 0.10)
        
        # If on-chain, these would come from DEX pools
        # For now, mock based on market cap
        market_cap = omk_data.get("marketCap", 50000000)
        
        eth_omk = market_cap * 0.025  # 2.5% in ETH/OMK pool
        usdt_omk = market_cap * 0.035  # 3.5% in USDT/OMK pool
        
        return {
            "eth_omk": eth_omk,
            "usdt_omk": usdt_omk,
            "total": eth_omk + usdt_omk
        }
    
    # Configuration methods (called by admin)
    
    def set_omk_contract(self, address: str, chain: str = "ethereum"):
        """Admin sets OMK contract address - switches to on-chain mode"""
        self.omk_contract_address = address
        self.omk_chain = chain
        self.cache.clear()  # Clear cache to fetch new data
        logger.info("OMK contract address set", address=address, chain=chain)
    
    def set_otc_price(self, price: float):
        """Admin sets OTC price - takes precedence"""
        self.omk_otc_price = price
        self.cache.clear()
        logger.info("OMK OTC price set", price=price)
    
    def get_config(self) -> Dict[str, Any]:
        """Get current agent configuration"""
        return {
            "omk_contract_address": self.omk_contract_address,
            "omk_chain": self.omk_chain,
            "omk_otc_price": self.omk_otc_price,
            "data_source": "on-chain" if self.omk_contract_address else "otc",
            "has_coingecko_key": bool(self.coingecko_api_key),
            "has_cryptopanic_key": bool(self.cryptopanic_api_key),
            "cache_ttl": self.cache_ttl
        }
    
    # Fallback data methods
    
    def _get_fallback_crypto_data(self) -> Dict[str, Any]:
        """Fallback crypto data when API fails"""
        return {
            "btc": {"price": 43250.18, "change24h": 2.14, "market_cap": 850000000000, "volume24h": 25000000000},
            "eth": {"price": 2485.32, "change24h": 1.85, "market_cap": 300000000000, "volume24h": 15000000000},
            "sol": {"price": 98.47, "change24h": -0.92, "market_cap": 45000000000, "volume24h": 2000000000},
            "totalMarketCap": 1750000000000,
            "total24hVolume": 85000000000
        }
    
    def _get_fallback_omk_data(self) -> Dict[str, Any]:
        """Fallback OMK data"""
        return {
            "price": 0.10,
            "marketCap": 50000000,
            "circulation": 500000000,
            "totalSupply": 1000000000,
            "volume24h": 2500000,
            "priceChange24h": 0.0025,
            "priceChangePercent": 2.56,
            "data_source": "fallback"
        }
    
    def _get_complete_fallback_data(self) -> Dict[str, Any]:
        """Complete fallback when everything fails"""
        return {
            "omk": self._get_fallback_omk_data(),
            "liquidity": {"eth_omk": 1250000, "usdt_omk": 1750000, "total": 3000000},
            "crypto": self._get_fallback_crypto_data(),
            "news": [],
            "last_updated": datetime.now().isoformat(),
            "data_sources": {"omk": "fallback", "crypto": "fallback", "news": "unavailable"}
        }
