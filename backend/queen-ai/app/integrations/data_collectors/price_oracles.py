"""
Price Oracles Data Collector for Fivetran
Collects price feed data from Chainlink, Pyth, etc.
"""
from typing import Dict, List, Any
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class PriceOraclesConnector:
    """
    Collects price oracle data for Fivetran
    
    Data Sources:
    - Chainlink price feeds
    - Pyth Network
    - API3
    """
    
    def __init__(self):
        self.tracked_feeds = []
    
    async def collect_chainlink_prices(self) -> List[Dict]:
        """
        Collect Chainlink price feed data
        
        Returns:
            List of price feed dictionaries
        """
        try:
            from web3 import Web3
            from app.config.settings import settings
            
            if not settings.ETHEREUM_RPC_URL:
                logger.warning("Ethereum RPC URL not configured")
                return []
            
            w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
            
            if not w3.is_connected():
                logger.error("Failed to connect to Ethereum RPC")
                return []
            
            # Chainlink price feed addresses (Ethereum Mainnet)
            PRICE_FEEDS = {
                'ETH/USD': '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419',
                'BTC/USD': '0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c',
                'USDC/USD': '0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6'
            }
            
            # Chainlink Aggregator ABI (minimal)
            AGGREGATOR_ABI = [
                {
                    "inputs": [],
                    "name": "latestRoundData",
                    "outputs": [
                        {"name": "roundId", "type": "uint80"},
                        {"name": "answer", "type": "int256"},
                        {"name": "startedAt", "type": "uint256"},
                        {"name": "updatedAt", "type": "uint256"},
                        {"name": "answeredInRound", "type": "uint80"}
                    ],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]
            
            prices = []
            
            for pair_name, feed_address in PRICE_FEEDS.items():
                try:
                    contract = w3.eth.contract(
                        address=Web3.to_checksum_address(feed_address),
                        abi=AGGREGATOR_ABI
                    )
                    
                    # Get latest price
                    round_data = contract.functions.latestRoundData().call()
                    decimals = contract.functions.decimals().call()
                    
                    price = round_data[1] / (10 ** decimals)
                    
                    prices.append({
                        'pair': pair_name,
                        'oracle': 'chainlink',
                        'feed_address': feed_address,
                        'price': float(price),
                        'updated_at': datetime.fromtimestamp(round_data[3]).isoformat(),
                        'round_id': round_data[0],
                        'collected_at': datetime.utcnow().isoformat()
                    })
                
                except Exception as e:
                    logger.error(f"Failed to get {pair_name} price: {str(e)}")
                    continue
            
            logger.info(f"Collected {len(prices)} Chainlink prices")
            return prices
        
        except Exception as e:
            logger.error(f"Failed to collect Chainlink prices: {str(e)}")
            return []
    
    async def collect_pyth_prices(self) -> List[Dict]:
        """
        Collect Pyth Network price feed data
        
        Returns:
            List of price feed dictionaries
        """
        try:
            import aiohttp
            
            # Pyth API endpoint
            url = "https://hermes.pyth.network/api/latest_price_feeds"
            
            params = {
                'ids[]': [
                    '0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace',  # ETH/USD
                    '0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43',  # BTC/USD
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        prices = []
                        for feed in data:
                            price_data = feed.get('price', {})
                            prices.append({
                                'pair': feed.get('id'),
                                'oracle': 'pyth',
                                'price': float(price_data.get('price', 0)) / (10 ** abs(price_data.get('expo', 0))),
                                'confidence': float(price_data.get('conf', 0)),
                                'updated_at': datetime.fromtimestamp(price_data.get('publish_time', 0)).isoformat(),
                                'collected_at': datetime.utcnow().isoformat()
                            })
                        
                        logger.info(f"Collected {len(prices)} Pyth prices")
                        return prices
                    else:
                        logger.error(f"Pyth API returned {response.status}")
                        return []
        
        except Exception as e:
            logger.error(f"Failed to collect Pyth prices: {str(e)}")
            return []
    
    async def collect_all(self) -> Dict[str, List[Dict]]:
        """
        Collect prices from all oracles
        
        Returns:
            Dictionary with oracle names as keys and price lists as values
        """
        import asyncio
        
        chainlink_prices, pyth_prices = await asyncio.gather(
            self.collect_chainlink_prices(),
            self.collect_pyth_prices(),
            return_exceptions=True
        )
        
        return {
            'chainlink': chainlink_prices if not isinstance(chainlink_prices, Exception) else [],
            'pyth': pyth_prices if not isinstance(pyth_prices, Exception) else []
        }
