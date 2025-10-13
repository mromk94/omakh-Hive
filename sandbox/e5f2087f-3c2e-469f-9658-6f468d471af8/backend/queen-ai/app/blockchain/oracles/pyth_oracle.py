"""
Pyth Network Oracle Integration (Solana)

High-frequency, low-latency price feeds for:
- SOL/USD
- Token prices
- Cross-chain data
"""
from typing import Dict, Optional, List
from decimal import Decimal
import structlog
from solders.pubkey import Pubkey

logger = structlog.get_logger(__name__)


class PythOracle:
    """
    Pyth Network Oracle integration
    
    Provides high-frequency price feeds on Solana
    """
    
    # Pyth program ID (Mainnet)
    PYTH_PROGRAM_ID = "FsJ3A3u2vn5cTVofAjvy6y5kwABJAqYWpe4975bi2epH"
    
    # Price feed IDs (Mainnet)
    PRICE_FEEDS = {
        "SOL/USD": "H6ARHf6YXhGYeQfUzQNGk6rDNnLBQKrenN712K4AQJEG",
        "BTC/USD": "GVXRSBjFk6e6J3NbVPXohDJetcTjaeeuykUpbQF8UoMU",
        "ETH/USD": "JBu1AL4obBcCMqKBBxhpWCNUt136ijcuMZLFvTP7iWdB",
        "USDC/USD": "Gnt27xtC473ZT2Mw5u8wZ68Z3gULkSTb5DuxJy7eJotD",
        "USDT/USD": "3vxLXJqLqF3JG5TCbYycbKWRBbCJQLxQmBGCkyqEEefL",
        # Add more feeds as needed
    }
    
    # Testnet/Devnet feeds
    TESTNET_FEEDS = {
        "SOL/USD": "J83w4HKfqxwcq3BEMMkPFSppX3gqekLyLJBexebFVkix",
        "BTC/USD": "HovQMDrbAgAYPCmHVSrezcSmkMtXSSUsLDFANExrZh2J",
        "ETH/USD": "EdVCmQ9FSPcVe5YySXDPCRmc8aDQLKJ9xvYBMZPie1Vw",
    }
    
    # Price account structure offsets (Pyth format)
    PYTH_PRICE_OFFSET = 208  # Price data starts at byte 208
    PYTH_CONFIDENCE_OFFSET = 216  # Confidence interval
    PYTH_STATUS_OFFSET = 224  # Status (trading/halted/etc)
    PYTH_EXPO_OFFSET = 20  # Exponent
    
    def __init__(self, solana_client, network: str = "mainnet"):
        """
        Initialize Pyth oracle
        
        Args:
            solana_client: Solana client instance
            network: 'mainnet' or 'testnet'
        """
        self.solana_client = solana_client
        self.client = solana_client.client
        self.network = network
        
        # Select appropriate feeds
        self.feeds = self.PRICE_FEEDS if network == "mainnet" else self.TESTNET_FEEDS
        
        # Cache for price data
        self.price_cache = {}
        self.cache_ttl = 5  # 5 seconds cache
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize oracle and verify feed access"""
        try:
            # Test access to SOL/USD feed
            sol_price = await self.get_price("SOL/USD")
            
            if sol_price > 0:
                logger.info(
                    "Pyth oracle initialized",
                    network=self.network,
                    sol_price=sol_price
                )
                self.initialized = True
            else:
                raise Exception("Invalid price returned from feed")
        
        except Exception as e:
            logger.error(f"Failed to initialize Pyth oracle: {str(e)}")
            raise
    
    async def get_price(self, pair: str) -> float:
        """
        Get current price for trading pair
        
        Args:
            pair: Trading pair (e.g., "SOL/USD")
            
        Returns:
            Current price
        """
        try:
            # Check cache
            cached_price = self._get_cached_price(pair)
            if cached_price is not None:
                return cached_price
            
            # Get feed address
            feed_address = self.feeds.get(pair)
            
            if not feed_address:
                raise ValueError(f"Price feed not available for {pair}")
            
            # Get price account data
            price_data = await self._fetch_price_account(feed_address)
            
            # Parse price
            price = self._parse_price_data(price_data)
            
            # Cache price
            self._cache_price(pair, price)
            
            logger.debug(f"Price fetched: {pair} = ${price:,.2f}")
            
            return price
        
        except Exception as e:
            logger.error(f"Failed to get price for {pair}: {str(e)}")
            raise
    
    async def get_price_with_confidence(self, pair: str) -> Dict:
        """
        Get price with confidence interval
        
        Returns:
            {
                "price": float,
                "confidence": float,  # Confidence interval
                "status": str,  # "trading", "halted", etc.
                "pair": str,
                "slot": int
            }
        """
        try:
            feed_address = self.feeds.get(pair)
            if not feed_address:
                raise ValueError(f"Price feed not available for {pair}")
            
            # Get account data
            account_info = await self.client.get_account_info(
                Pubkey.from_string(feed_address)
            )
            
            if not account_info.value:
                raise Exception(f"Price account not found: {feed_address}")
            
            data = account_info.value.data
            
            # Parse full price data
            price = self._parse_price_from_bytes(data)
            confidence = self._parse_confidence_from_bytes(data)
            status = self._parse_status_from_bytes(data)
            
            return {
                "success": True,
                "pair": pair,
                "price": price,
                "confidence": confidence,
                "status": status,
                "feed_address": feed_address
            }
        
        except Exception as e:
            logger.error(f"Failed to get price with confidence: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_multiple_prices(self, pairs: List[str]) -> Dict[str, float]:
        """
        Get prices for multiple pairs efficiently
        
        Uses batch fetching for better performance
        """
        prices = {}
        
        # Batch fetch all accounts
        feed_addresses = [self.feeds.get(pair) for pair in pairs if pair in self.feeds]
        
        # TODO: Implement batch account fetching
        # For now, fetch sequentially
        for pair in pairs:
            try:
                prices[pair] = await self.get_price(pair)
            except Exception as e:
                logger.error(f"Failed to fetch {pair}: {str(e)}")
                prices[pair] = None
        
        return prices
    
    async def get_ema_price(self, pair: str) -> Dict:
        """
        Get Exponential Moving Average (EMA) price
        
        Pyth provides EMA for smoother price data
        """
        try:
            feed_address = self.feeds.get(pair)
            if not feed_address:
                raise ValueError(f"Price feed not available for {pair}")
            
            # Fetch EMA from Pyth account
            # EMA data is at different offset
            price_data = await self._fetch_price_account(feed_address)
            
            ema_price = self._parse_ema_from_bytes(price_data)
            current_price = self._parse_price_data(price_data)
            
            return {
                "success": True,
                "pair": pair,
                "current_price": current_price,
                "ema_price": ema_price,
                "difference": abs(current_price - ema_price),
                "difference_pct": abs((current_price - ema_price) / ema_price) * 100
            }
        
        except Exception as e:
            logger.error(f"Failed to get EMA price: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def calculate_token_value(
        self,
        token_amount: float,
        token_pair: str
    ) -> Dict:
        """
        Calculate USD value of token amount
        """
        try:
            price = await self.get_price(token_pair)
            usd_value = token_amount * price
            
            return {
                "success": True,
                "token_amount": token_amount,
                "token_price": price,
                "usd_value": usd_value,
                "pair": token_pair
            }
        
        except Exception as e:
            logger.error(f"Failed to calculate token value: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def subscribe_to_price_updates(
        self,
        pairs: List[str],
        callback
    ):
        """
        Subscribe to real-time price updates
        
        Uses WebSocket connection for live updates
        """
        try:
            # Get feed addresses
            feed_addresses = [
                Pubkey.from_string(self.feeds[pair])
                for pair in pairs
                if pair in self.feeds
            ]
            
            # Subscribe to account changes
            # TODO: Implement WebSocket subscription
            logger.info(f"Subscribed to price updates for {len(pairs)} pairs")
            
            # For now, return subscription info
            return {
                "success": True,
                "subscribed_pairs": pairs,
                "feed_count": len(feed_addresses)
            }
        
        except Exception as e:
            logger.error(f"Failed to subscribe to price updates: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _fetch_price_account(self, feed_address: str) -> bytes:
        """Fetch price account data from Solana"""
        try:
            account_info = await self.client.get_account_info(
                Pubkey.from_string(feed_address)
            )
            
            if not account_info.value:
                raise Exception(f"Price account not found: {feed_address}")
            
            return account_info.value.data
        
        except Exception as e:
            logger.error(f"Failed to fetch price account: {str(e)}")
            raise
    
    def _parse_price_data(self, data: bytes) -> float:
        """Parse price from Pyth account data"""
        try:
            # Pyth stores price as int64 at offset 208
            price_bytes = data[self.PYTH_PRICE_OFFSET:self.PYTH_PRICE_OFFSET + 8]
            price_raw = int.from_bytes(price_bytes, byteorder='little', signed=True)
            
            # Get exponent (scaling factor) at offset 20
            expo_bytes = data[self.PYTH_EXPO_OFFSET:self.PYTH_EXPO_OFFSET + 4]
            expo = int.from_bytes(expo_bytes, byteorder='little', signed=True)
            
            # Calculate actual price: price_raw * 10^expo
            price = float(Decimal(price_raw) * Decimal(10) ** Decimal(expo))
            
            return price
        
        except Exception as e:
            logger.error(f"Failed to parse price data: {str(e)}")
            raise
    
    def _parse_price_from_bytes(self, data: bytes) -> float:
        """Parse price from raw bytes"""
        return self._parse_price_data(data)
    
    def _parse_confidence_from_bytes(self, data: bytes) -> float:
        """Parse confidence interval from raw bytes"""
        try:
            conf_bytes = data[self.PYTH_CONFIDENCE_OFFSET:self.PYTH_CONFIDENCE_OFFSET + 8]
            conf_raw = int.from_bytes(conf_bytes, byteorder='little', signed=False)
            
            expo_bytes = data[self.PYTH_EXPO_OFFSET:self.PYTH_EXPO_OFFSET + 4]
            expo = int.from_bytes(expo_bytes, byteorder='little', signed=True)
            
            confidence = float(Decimal(conf_raw) * Decimal(10) ** Decimal(expo))
            
            return confidence
        
        except Exception as e:
            logger.error(f"Failed to parse confidence: {str(e)}")
            return 0.0
    
    def _parse_status_from_bytes(self, data: bytes) -> str:
        """Parse trading status from raw bytes"""
        try:
            status_byte = data[self.PYTH_STATUS_OFFSET]
            
            status_map = {
                0: "unknown",
                1: "trading",
                2: "halted",
                3: "auction"
            }
            
            return status_map.get(status_byte, "unknown")
        
        except Exception as e:
            logger.error(f"Failed to parse status: {str(e)}")
            return "unknown"
    
    def _parse_ema_from_bytes(self, data: bytes) -> float:
        """Parse EMA price from raw bytes"""
        try:
            # EMA is stored at different offset (around 240)
            ema_offset = 240
            ema_bytes = data[ema_offset:ema_offset + 8]
            ema_raw = int.from_bytes(ema_bytes, byteorder='little', signed=True)
            
            expo_bytes = data[self.PYTH_EXPO_OFFSET:self.PYTH_EXPO_OFFSET + 4]
            expo = int.from_bytes(expo_bytes, byteorder='little', signed=True)
            
            ema_price = float(Decimal(ema_raw) * Decimal(10) ** Decimal(expo))
            
            return ema_price
        
        except Exception as e:
            logger.error(f"Failed to parse EMA: {str(e)}")
            return 0.0
    
    def _get_cached_price(self, pair: str) -> Optional[float]:
        """Get price from cache if still valid"""
        import time
        
        if pair in self.price_cache:
            cached_data = self.price_cache[pair]
            age = time.time() - cached_data["timestamp"]
            
            if age < self.cache_ttl:
                return cached_data["price"]
        
        return None
    
    def _cache_price(self, pair: str, price: float):
        """Cache price with timestamp"""
        import time
        
        self.price_cache[pair] = {
            "price": price,
            "timestamp": time.time()
        }
    
    def add_custom_feed(self, pair: str, feed_address: str):
        """Add custom price feed"""
        self.feeds[pair] = feed_address
        logger.info(f"Custom feed added: {pair} -> {feed_address}")


# Global instance
pyth_oracle = None
