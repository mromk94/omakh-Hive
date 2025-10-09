"""
Uniswap V2/V3 Router Integration

Supports:
- Token swaps
- Liquidity provision/removal
- Price quotes
- Path finding
- Slippage protection
"""
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from web3 import Web3
import structlog

logger = structlog.get_logger(__name__)


# Uniswap V2 Router ABI (key functions)
UNISWAP_V2_ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForTokens",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokens",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForETH",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"}
        ],
        "name": "getAmountsOut",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "tokenA", "type": "address"},
            {"internalType": "address", "name": "tokenB", "type": "address"},
            {"internalType": "uint256", "name": "amountADesired", "type": "uint256"},
            {"internalType": "uint256", "name": "amountBDesired", "type": "uint256"},
            {"internalType": "uint256", "name": "amountAMin", "type": "uint256"},
            {"internalType": "uint256", "name": "amountBMin", "type": "uint256"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "addLiquidity",
        "outputs": [
            {"internalType": "uint256", "name": "amountA", "type": "uint256"},
            {"internalType": "uint256", "name": "amountB", "type": "uint256"},
            {"internalType": "uint256", "name": "liquidity", "type": "uint256"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "tokenA", "type": "address"},
            {"internalType": "address", "name": "tokenB", "type": "address"},
            {"internalType": "uint256", "name": "liquidity", "type": "uint256"},
            {"internalType": "uint256", "name": "amountAMin", "type": "uint256"},
            {"internalType": "uint256", "name": "amountBMin", "type": "uint256"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "removeLiquidity",
        "outputs": [
            {"internalType": "uint256", "name": "amountA", "type": "uint256"},
            {"internalType": "uint256", "name": "amountB", "type": "uint256"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]


# ERC20 ABI (for token approvals)
ERC20_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "address", "name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]


class UniswapRouter:
    """
    Uniswap V2 Router integration
    
    Handles token swaps, liquidity operations, and price quotes
    """
    
    # Mainnet addresses
    UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    UNISWAP_V2_FACTORY = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    
    def __init__(self, eth_client):
        """
        Initialize Uniswap router
        
        Args:
            eth_client: Ethereum client instance
        """
        self.eth_client = eth_client
        self.w3 = eth_client.w3
        
        # Initialize router contract
        self.router = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.UNISWAP_V2_ROUTER),
            abi=UNISWAP_V2_ROUTER_ABI
        )
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize router"""
        try:
            # Verify router is accessible
            code = await self.w3.eth.get_code(self.UNISWAP_V2_ROUTER)
            if code == b'' or code == b'0x':
                raise Exception("Uniswap router not found at address")
            
            self.initialized = True
            logger.info("Uniswap router initialized", router=self.UNISWAP_V2_ROUTER)
        
        except Exception as e:
            logger.error(f"Failed to initialize Uniswap router: {str(e)}")
            raise
    
    async def get_quote(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        path: Optional[List[str]] = None
    ) -> Dict:
        """
        Get quote for token swap
        
        Args:
            token_in: Input token address
            token_out: Output token address
            amount_in: Amount of input token (in wei)
            path: Custom path (optional, will auto-find if not provided)
            
        Returns:
            Quote with expected output amount
        """
        try:
            # Build path if not provided
            if not path:
                path = await self._find_best_path(token_in, token_out)
            
            # Convert to checksum addresses
            path = [Web3.to_checksum_address(addr) for addr in path]
            
            # Get amounts out
            amounts = await self.router.functions.getAmountsOut(
                amount_in,
                path
            ).call()
            
            amount_out = amounts[-1]
            
            # Calculate price impact and slippage
            price_impact = self._calculate_price_impact(amounts, path)
            
            return {
                "success": True,
                "amount_in": amount_in,
                "amount_out": amount_out,
                "path": path,
                "price_impact": price_impact,
                "exchange_rate": float(Decimal(amount_out) / Decimal(amount_in))
            }
        
        except Exception as e:
            logger.error(f"Failed to get quote: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def swap_tokens(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        min_amount_out: int,
        recipient: str,
        deadline: Optional[int] = None,
        path: Optional[List[str]] = None,
        gas_priority: str = "normal"
    ) -> str:
        """
        Execute token swap
        
        Args:
            token_in: Input token address (use WETH for ETH)
            token_out: Output token address
            amount_in: Amount to swap (in wei)
            min_amount_out: Minimum acceptable output (slippage protection)
            recipient: Address to receive tokens
            deadline: Transaction deadline (timestamp)
            path: Custom swap path
            gas_priority: Gas priority level
            
        Returns:
            Transaction hash
        """
        try:
            # Build path
            if not path:
                path = await self._find_best_path(token_in, token_out)
            
            path = [Web3.to_checksum_address(addr) for addr in path]
            
            # Set deadline (default 20 minutes)
            if not deadline:
                deadline = await self.w3.eth.get_block('latest')['timestamp'] + 1200
            
            # Check if input is ETH
            is_eth_input = token_in.lower() == "eth" or token_in == self.WETH_ADDRESS
            is_eth_output = token_out.lower() == "eth" or token_out == self.WETH_ADDRESS
            
            # Approve token if not ETH
            if not is_eth_input:
                await self._approve_token(token_in, amount_in)
            
            # Build transaction
            if is_eth_input and not is_eth_output:
                # ETH -> Token
                tx = await self.router.functions.swapExactETHForTokens(
                    min_amount_out,
                    path,
                    Web3.to_checksum_address(recipient),
                    deadline
                ).build_transaction({
                    'value': amount_in,
                    'from': self.eth_client.default_account
                })
            
            elif not is_eth_input and is_eth_output:
                # Token -> ETH
                tx = await self.router.functions.swapExactTokensForETH(
                    amount_in,
                    min_amount_out,
                    path,
                    Web3.to_checksum_address(recipient),
                    deadline
                ).build_transaction({
                    'from': self.eth_client.default_account
                })
            
            else:
                # Token -> Token
                tx = await self.router.functions.swapExactTokensForTokens(
                    amount_in,
                    min_amount_out,
                    path,
                    Web3.to_checksum_address(recipient),
                    deadline
                ).build_transaction({
                    'from': self.eth_client.default_account
                })
            
            # Execute transaction
            tx_hash = await self.eth_client.send_transaction(tx, gas_priority=gas_priority)
            
            logger.info(
                "Uniswap swap executed",
                token_in=token_in,
                token_out=token_out,
                amount_in=amount_in,
                tx_hash=tx_hash
            )
            
            return tx_hash
        
        except Exception as e:
            logger.error(f"Swap failed: {str(e)}")
            raise
    
    async def add_liquidity(
        self,
        token_a: str,
        token_b: str,
        amount_a: int,
        amount_b: int,
        amount_a_min: int,
        amount_b_min: int,
        recipient: str,
        deadline: Optional[int] = None,
        gas_priority: str = "normal"
    ) -> Tuple[str, Dict]:
        """
        Add liquidity to Uniswap pool
        
        Returns:
            (tx_hash, liquidity_info)
        """
        try:
            # Approve both tokens
            await self._approve_token(token_a, amount_a)
            await self._approve_token(token_b, amount_b)
            
            # Set deadline
            if not deadline:
                deadline = await self.w3.eth.get_block('latest')['timestamp'] + 1200
            
            # Build transaction
            tx = await self.router.functions.addLiquidity(
                Web3.to_checksum_address(token_a),
                Web3.to_checksum_address(token_b),
                amount_a,
                amount_b,
                amount_a_min,
                amount_b_min,
                Web3.to_checksum_address(recipient),
                deadline
            ).build_transaction({
                'from': self.eth_client.default_account
            })
            
            # Execute
            tx_hash = await self.eth_client.send_transaction(tx, gas_priority=gas_priority)
            
            # Get receipt to extract liquidity amount
            receipt = await self.eth_client.get_transaction_receipt(tx_hash)
            
            logger.info("Liquidity added", token_a=token_a, token_b=token_b, tx_hash=tx_hash)
            
            return tx_hash, {
                "token_a": token_a,
                "token_b": token_b,
                "amount_a": amount_a,
                "amount_b": amount_b
            }
        
        except Exception as e:
            logger.error(f"Add liquidity failed: {str(e)}")
            raise
    
    async def remove_liquidity(
        self,
        token_a: str,
        token_b: str,
        liquidity: int,
        amount_a_min: int,
        amount_b_min: int,
        recipient: str,
        deadline: Optional[int] = None,
        gas_priority: str = "normal"
    ) -> Tuple[str, Dict]:
        """
        Remove liquidity from Uniswap pool
        
        Returns:
            (tx_hash, amounts_removed)
        """
        try:
            # Set deadline
            if not deadline:
                deadline = await self.w3.eth.get_block('latest')['timestamp'] + 1200
            
            # Build transaction
            tx = await self.router.functions.removeLiquidity(
                Web3.to_checksum_address(token_a),
                Web3.to_checksum_address(token_b),
                liquidity,
                amount_a_min,
                amount_b_min,
                Web3.to_checksum_address(recipient),
                deadline
            ).build_transaction({
                'from': self.eth_client.default_account
            })
            
            # Execute
            tx_hash = await self.eth_client.send_transaction(tx, gas_priority=gas_priority)
            
            logger.info("Liquidity removed", token_a=token_a, token_b=token_b, tx_hash=tx_hash)
            
            return tx_hash, {
                "token_a": token_a,
                "token_b": token_b,
                "liquidity_removed": liquidity
            }
        
        except Exception as e:
            logger.error(f"Remove liquidity failed: {str(e)}")
            raise
    
    async def _approve_token(self, token_address: str, amount: int):
        """Approve token spending for Uniswap router"""
        try:
            token = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=ERC20_ABI
            )
            
            # Check current allowance
            allowance = await token.functions.allowance(
                self.eth_client.default_account,
                self.UNISWAP_V2_ROUTER
            ).call()
            
            # Approve if needed
            if allowance < amount:
                # Approve max amount
                max_approval = 2**256 - 1
                
                tx = await token.functions.approve(
                    self.UNISWAP_V2_ROUTER,
                    max_approval
                ).build_transaction({
                    'from': self.eth_client.default_account
                })
                
                tx_hash = await self.eth_client.send_transaction(tx)
                
                logger.info("Token approved", token=token_address, tx_hash=tx_hash)
        
        except Exception as e:
            logger.error(f"Token approval failed: {str(e)}")
            raise
    
    async def _find_best_path(self, token_in: str, token_out: str) -> List[str]:
        """
        Find best swap path
        
        For now, uses direct path or WETH intermediary
        Future: Implement multi-hop path finding
        """
        token_in = token_in.lower()
        token_out = token_out.lower()
        
        # Direct path
        if token_in == self.WETH_ADDRESS.lower() or token_out == self.WETH_ADDRESS.lower():
            return [token_in, token_out]
        
        # Path through WETH
        return [token_in, self.WETH_ADDRESS, token_out]
    
    def _calculate_price_impact(self, amounts: List[int], path: List[str]) -> float:
        """
        Calculate price impact of trade
        
        Simple estimation based on amount ratios
        """
        if len(amounts) < 2:
            return 0.0
        
        # Price impact = (expected_price - actual_price) / expected_price
        # Simplified calculation
        return 0.0  # TODO: Implement proper price impact calculation


# Global instance
uniswap_router = None
