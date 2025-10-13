"""
Chainlink Price Oracle Integration (Ethereum)

Provides reliable price feeds for:
- ETH/USD
- Token prices
- Gas prices
- Market data
"""
from typing import Dict, Optional
from decimal import Decimal
from web3 import Web3
import structlog

logger = structlog.get_logger(__name__)


# Chainlink Aggregator ABI
CHAINLINK_AGGREGATOR_ABI = [
    {
        "inputs": [],
        "name": "latestRoundData",
        "outputs": [
            {"internalType": "uint80", "name": "roundId", "type": "uint80"},
            {"internalType": "int256", "name": "answer", "type": "int256"},
            {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
            {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
            {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "description",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    }
]


class ChainlinkOracle:
    """
    Chainlink Price Oracle integration
    
    Provides reliable, decentralized price feeds
    """
    
    # Mainnet price feed addresses
    PRICE_FEEDS = {
        "ETH/USD": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",
        "BTC/USD": "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c",
        "LINK/USD": "0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c",
        "USDC/USD": "0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6",
        "DAI/USD": "0xAed0c38402a5d19df6E4c03F4E2DceD6e29c1ee9",
        "USDT/USD": "0x3E7d1eAB13ad0104d2750B8863b489D65364e32D",
        # Add more feeds as needed
    }
    
    # Testnet (Sepolia) feeds for testing
    TESTNET_FEEDS = {
        "ETH/USD": "0x694AA1769357215DE4FAC081bf1f309aDC325306",
        "BTC/USD": "0x1b44F3514812d835EB1BDB0acB33d3fA3351Ee43",
        "LINK/USD": "0xc59E3633BAAC79493d908e63626716e204A45EdF",
    }
    
    def __init__(self, eth_client, network: str = "mainnet"):
        """
        Initialize Chainlink oracle
        
        Args:
            eth_client: Ethereum client instance
            network: 'mainnet' or 'testnet'
        """
        self.eth_client = eth_client
        self.w3 = eth_client.w3
        self.network = network
        
        # Select appropriate feeds
        self.feeds = self.PRICE_FEEDS if network == "mainnet" else self.TESTNET_FEEDS
        
        # Cache for feed contracts
        self.feed_contracts = {}
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize oracle and verify feed access"""
        try:
            # Test access to ETH/USD feed
            eth_price = await self.get_price("ETH/USD")
            
            if eth_price > 0:
                logger.info(
                    "Chainlink oracle initialized",
                    network=self.network,
                    eth_price=eth_price
                )
                self.initialized = True
            else:
                raise Exception("Invalid price returned from feed")
        
        except Exception as e:
            logger.error(f"Failed to initialize Chainlink oracle: {str(e)}")
            raise
    
    async def get_price(self, pair: str) -> float:
        """
        Get current price for trading pair
        
        Args:
            pair: Trading pair (e.g., "ETH/USD")
            
        Returns:
            Current price
        """
        try:
            # Get feed address
            feed_address = self.feeds.get(pair)
            
            if not feed_address:
                raise ValueError(f"Price feed not available for {pair}")
            
            # Get or create feed contract
            feed_contract = await self._get_feed_contract(feed_address)
            
            # Get latest price data
            round_data = await feed_contract.functions.latestRoundData().call()
            
            answer = round_data[1]  # Price
            updated_at = round_data[3]  # Timestamp
            
            # Get decimals
            decimals = await feed_contract.functions.decimals().call()
            
            # Convert to human-readable price
            price = float(Decimal(answer) / Decimal(10 ** decimals))
            
            # Verify price is fresh (not stale)
            import time
            current_time = int(time.time())
            age = current_time - updated_at
            
            if age > 3600:  # 1 hour staleness threshold
                logger.warning(
                    f"Stale price data for {pair}",
                    age_seconds=age,
                    price=price
                )
            
            logger.debug(f"Price fetched: {pair} = ${price:,.2f}")
            
            return price
        
        except Exception as e:
            logger.error(f"Failed to get price for {pair}: {str(e)}")
            raise
    
    async def get_price_with_metadata(self, pair: str) -> Dict:
        """
        Get price with additional metadata
        
        Returns:
            {
                "price": float,
                "pair": str,
                "updated_at": int,
                "round_id": int,
                "decimals": int,
                "description": str
            }
        """
        try:
            feed_address = self.feeds.get(pair)
            if not feed_address:
                raise ValueError(f"Price feed not available for {pair}")
            
            feed_contract = await self._get_feed_contract(feed_address)
            
            # Get all data
            round_data = await feed_contract.functions.latestRoundData().call()
            decimals = await feed_contract.functions.decimals().call()
            description = await feed_contract.functions.description().call()
            
            round_id = round_data[0]
            answer = round_data[1]
            updated_at = round_data[3]
            
            price = float(Decimal(answer) / Decimal(10 ** decimals))
            
            return {
                "success": True,
                "pair": pair,
                "price": price,
                "updated_at": updated_at,
                "round_id": round_id,
                "decimals": decimals,
                "description": description,
                "feed_address": feed_address
            }
        
        except Exception as e:
            logger.error(f"Failed to get price metadata: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_multiple_prices(self, pairs: list) -> Dict[str, float]:
        """
        Get prices for multiple pairs efficiently
        
        Args:
            pairs: List of trading pairs
            
        Returns:
            Dictionary mapping pairs to prices
        """
        prices = {}
        
        for pair in pairs:
            try:
                prices[pair] = await self.get_price(pair)
            except Exception as e:
                logger.error(f"Failed to fetch {pair}: {str(e)}")
                prices[pair] = None
        
        return prices
    
    async def calculate_token_value(
        self,
        token_amount: float,
        token_pair: str
    ) -> Dict:
        """
        Calculate USD value of token amount
        
        Args:
            token_amount: Amount of tokens
            token_pair: Price pair (e.g., "ETH/USD")
            
        Returns:
            {
                "token_amount": float,
                "token_price": float,
                "usd_value": float,
                "pair": str
            }
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
    
    async def get_historical_price(
        self,
        pair: str,
        round_id: int
    ) -> Optional[float]:
        """
        Get historical price from specific round
        
        Args:
            pair: Trading pair
            round_id: Chainlink round ID
            
        Returns:
            Historical price
        """
        try:
            feed_address = self.feeds.get(pair)
            if not feed_address:
                raise ValueError(f"Price feed not available for {pair}")
            
            feed_contract = await self._get_feed_contract(feed_address)
            
            # Get round data
            round_data = await feed_contract.functions.getRoundData(round_id).call()
            
            answer = round_data[1]
            decimals = await feed_contract.functions.decimals().call()
            
            price = float(Decimal(answer) / Decimal(10 ** decimals))
            
            return price
        
        except Exception as e:
            logger.error(f"Failed to get historical price: {str(e)}")
            return None
    
    async def _get_feed_contract(self, feed_address: str):
        """Get or create feed contract instance"""
        if feed_address not in self.feed_contracts:
            self.feed_contracts[feed_address] = self.w3.eth.contract(
                address=Web3.to_checksum_address(feed_address),
                abi=CHAINLINK_AGGREGATOR_ABI
            )
        
        return self.feed_contracts[feed_address]
    
    def add_custom_feed(self, pair: str, feed_address: str):
        """
        Add custom price feed
        
        Useful for adding token-specific feeds
        """
        self.feeds[pair] = feed_address
        logger.info(f"Custom feed added: {pair} -> {feed_address}")


# Global instance
chainlink_oracle = None
