"""
Ethereum Client - Complete Web3 Integration

Implements:
- Web3.py integration
- Wallet management
- Transaction signing and broadcasting
- Gas estimation and optimization
- Transaction monitoring and confirmation
- Nonce management
- Retry logic for failed transactions
- Blockchain event listener service
"""
import asyncio
from typing import Dict, Any, Optional, List
from decimal import Decimal
from web3 import Web3, AsyncWeb3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_typing import Address, HexStr
import structlog

from app.config.settings import settings

logger = structlog.get_logger(__name__)


class EthereumClient:
    """
    Complete Ethereum blockchain client
    
    Features:
    - Connection management (HTTP, WSS)
    - Transaction creation and signing
    - Gas optimization
    - Nonce management
    - Event monitoring
    - Retry logic
    """
    
    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url or settings.ETHEREUM_RPC_URL
        self.w3: Optional[AsyncWeb3] = None
        self.account: Optional[Account] = None
        self.initialized = False
        
        # Nonce tracking (prevents nonce conflicts)
        self.nonce_lock = asyncio.Lock()
        self.pending_nonce: Optional[int] = None
    
    async def initialize(self, private_key: Optional[str] = None):
        """
        Initialize Ethereum client
        
        Args:
            private_key: Optional private key for signing transactions
        """
        if not self.rpc_url:
            raise ValueError("Ethereum RPC URL not configured")
        
        try:
            # Create async Web3 instance
            self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(self.rpc_url))
            
            # Add POA middleware for testnets (Goerli, Sepolia)
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            # Test connection
            is_connected = await self.w3.is_connected()
            if not is_connected:
                raise ConnectionError(f"Could not connect to Ethereum node at {self.rpc_url}")
            
            # Get chain ID
            chain_id = await self.w3.eth.chain_id
            
            # Load account if private key provided
            if private_key:
                self.account = Account.from_key(private_key)
                logger.info(
                    "Ethereum client initialized with account",
                    address=self.account.address,
                    chain_id=chain_id
                )
            else:
                logger.info(
                    "Ethereum client initialized (read-only)",
                    chain_id=chain_id
                )
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize Ethereum client: {str(e)}")
            raise
    
    async def get_balance(self, address: str) -> Decimal:
        """
        Get ETH balance of address
        
        Args:
            address: Ethereum address
            
        Returns:
            Balance in ETH
        """
        if not self.initialized:
            raise RuntimeError("Client not initialized")
        
        wei_balance = await self.w3.eth.get_balance(address)
        eth_balance = Decimal(wei_balance) / Decimal(10 ** 18)
        
        return eth_balance
    
    async def get_next_nonce(self, address: str) -> int:
        """
        Get next nonce for address with lock to prevent conflicts
        
        Args:
            address: Ethereum address
            
        Returns:
            Next nonce to use
        """
        async with self.nonce_lock:
            # Get pending transaction count (includes pending txs)
            nonce = await self.w3.eth.get_transaction_count(address, 'pending')
            
            # Track highest pending nonce
            if self.pending_nonce is None or nonce > self.pending_nonce:
                self.pending_nonce = nonce
            else:
                # Use tracked nonce if higher (prevents conflicts)
                nonce = self.pending_nonce
            
            # Increment for next transaction
            self.pending_nonce = nonce + 1
            
            return nonce
    
    async def estimate_gas(
        self,
        transaction: Dict[str, Any],
        multiplier: float = 1.2
    ) -> int:
        """
        Estimate gas for transaction with safety multiplier
        
        Args:
            transaction: Transaction dict
            multiplier: Safety multiplier (default 1.2 = 20% buffer)
            
        Returns:
            Estimated gas limit
        """
        if not self.initialized:
            raise RuntimeError("Client not initialized")
        
        try:
            # Estimate gas
            estimated_gas = await self.w3.eth.estimate_gas(transaction)
            
            # Add safety buffer
            gas_limit = int(estimated_gas * multiplier)
            
            logger.debug(
                "Gas estimated",
                estimated=estimated_gas,
                with_buffer=gas_limit,
                multiplier=multiplier
            )
            
            return gas_limit
            
        except Exception as e:
            logger.error(f"Gas estimation failed: {str(e)}")
            # Return default gas limit as fallback
            return 21000  # Standard ETH transfer
    
    async def get_gas_price(self, priority: str = "normal") -> int:
        """
        Get current gas price with priority levels
        
        Args:
            priority: "low", "normal", or "high"
            
        Returns:
            Gas price in wei
        """
        if not self.initialized:
            raise RuntimeError("Client not initialized")
        
        # Get base gas price
        base_gas_price = await self.w3.eth.gas_price
        
        # Adjust based on priority
        multipliers = {
            "low": 0.8,
            "normal": 1.0,
            "high": 1.3
        }
        
        multiplier = multipliers.get(priority, 1.0)
        gas_price = int(base_gas_price * multiplier)
        
        logger.debug(
            "Gas price calculated",
            base=base_gas_price,
            priority=priority,
            final=gas_price
        )
        
        return gas_price
    
    async def send_transaction(
        self,
        to: str,
        value: int = 0,
        data: str = "0x",
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
        max_retries: int = 3
    ) -> HexStr:
        """
        Send transaction with automatic retry logic
        
        Args:
            to: Recipient address
            value: Amount in wei
            data: Transaction data (hex string)
            gas_limit: Optional gas limit
            gas_price: Optional gas price
            max_retries: Maximum retry attempts
            
        Returns:
            Transaction hash
        """
        if not self.initialized or not self.account:
            raise RuntimeError("Client not initialized with account")
        
        # Build transaction
        transaction = {
            'from': self.account.address,
            'to': to,
            'value': value,
            'data': data,
            'chainId': await self.w3.eth.chain_id,
        }
        
        # Get nonce
        transaction['nonce'] = await self.get_next_nonce(self.account.address)
        
        # Estimate gas if not provided
        if gas_limit is None:
            gas_limit = await self.estimate_gas(transaction)
        transaction['gas'] = gas_limit
        
        # Get gas price if not provided
        if gas_price is None:
            gas_price = await self.get_gas_price()
        transaction['gasPrice'] = gas_price
        
        # Retry loop
        for attempt in range(max_retries):
            try:
                # Sign transaction
                signed_txn = self.account.sign_transaction(transaction)
                
                # Send transaction
                tx_hash = await self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                
                logger.info(
                    "Transaction sent",
                    tx_hash=tx_hash.hex(),
                    to=to,
                    value=value,
                    nonce=transaction['nonce'],
                    attempt=attempt + 1
                )
                
                return tx_hash.hex()
                
            except Exception as e:
                logger.warning(
                    f"Transaction attempt {attempt + 1} failed: {str(e)}",
                    attempt=attempt + 1,
                    max_retries=max_retries
                )
                
                if attempt < max_retries - 1:
                    # Wait before retry
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    async def wait_for_transaction(
        self,
        tx_hash: str,
        timeout: int = 120,
        poll_interval: int = 2
    ) -> Dict[str, Any]:
        """
        Wait for transaction confirmation
        
        Args:
            tx_hash: Transaction hash
            timeout: Maximum wait time in seconds
            poll_interval: Polling interval in seconds
            
        Returns:
            Transaction receipt
        """
        if not self.initialized:
            raise RuntimeError("Client not initialized")
        
        logger.info(f"Waiting for transaction {tx_hash}...")
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                # Try to get receipt
                receipt = await self.w3.eth.get_transaction_receipt(tx_hash)
                
                if receipt:
                    # Transaction mined
                    status = "success" if receipt['status'] == 1 else "failed"
                    
                    logger.info(
                        "Transaction confirmed",
                        tx_hash=tx_hash,
                        status=status,
                        block=receipt['blockNumber'],
                        gas_used=receipt['gasUsed']
                    )
                    
                    return {
                        'tx_hash': tx_hash,
                        'status': status,
                        'block_number': receipt['blockNumber'],
                        'gas_used': receipt['gasUsed'],
                        'receipt': receipt
                    }
            
            except Exception:
                pass  # Transaction not mined yet
            
            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Transaction {tx_hash} not confirmed after {timeout}s")
            
            # Wait before next poll
            await asyncio.sleep(poll_interval)
    
    async def call_contract(
        self,
        contract_address: str,
        abi: List[Dict],
        function_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Call contract function (read-only)
        
        Args:
            contract_address: Contract address
            abi: Contract ABI
            function_name: Function to call
            *args: Function arguments
            **kwargs: Additional parameters
            
        Returns:
            Function result
        """
        if not self.initialized:
            raise RuntimeError("Client not initialized")
        
        # Create contract instance
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=abi
        )
        
        # Call function
        result = await contract.functions[function_name](*args).call(**kwargs)
        
        logger.debug(
            "Contract call",
            contract=contract_address,
            function=function_name,
            result=result
        )
        
        return result
    
    async def send_contract_transaction(
        self,
        contract_address: str,
        abi: List[Dict],
        function_name: str,
        *args,
        value: int = 0,
        **kwargs
    ) -> str:
        """
        Send contract transaction
        
        Args:
            contract_address: Contract address
            abi: Contract ABI
            function_name: Function to call
            *args: Function arguments
            value: ETH to send (wei)
            **kwargs: Additional parameters
            
        Returns:
            Transaction hash
        """
        if not self.initialized or not self.account:
            raise RuntimeError("Client not initialized with account")
        
        # Create contract instance
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=abi
        )
        
        # Build transaction data
        data = contract.encodeABI(fn_name=function_name, args=args)
        
        # Send transaction
        tx_hash = await self.send_transaction(
            to=contract_address,
            value=value,
            data=data,
            **kwargs
        )
        
        return tx_hash
    
    async def listen_for_events(
        self,
        contract_address: str,
        abi: List[Dict],
        event_name: str,
        from_block: int = None,
        callback: callable = None
    ):
        """
        Listen for contract events
        
        Args:
            contract_address: Contract address
            abi: Contract ABI
            event_name: Event to listen for
            from_block: Starting block (default: latest)
            callback: Async function to call on event
        """
        if not self.initialized:
            raise RuntimeError("Client not initialized")
        
        # Create contract instance
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=abi
        )
        
        # Get event filter
        event = contract.events[event_name]
        
        if from_block is None:
            from_block = await self.w3.eth.block_number
        
        logger.info(
            "Listening for events",
            contract=contract_address,
            event=event_name,
            from_block=from_block
        )
        
        # Poll for new events
        last_block = from_block
        
        while True:
            try:
                current_block = await self.w3.eth.block_number
                
                if current_block > last_block:
                    # Get events in new blocks
                    events = await event.get_logs(
                        fromBlock=last_block + 1,
                        toBlock=current_block
                    )
                    
                    for evt in events:
                        logger.info(
                            "Event detected",
                            event=event_name,
                            block=evt['blockNumber'],
                            tx_hash=evt['transactionHash'].hex()
                        )
                        
                        if callback:
                            await callback(evt)
                    
                    last_block = current_block
            
            except Exception as e:
                logger.error(f"Error listening for events: {str(e)}")
            
            # Poll interval
            await asyncio.sleep(2)
    
    async def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction details"""
        if not self.initialized:
            raise RuntimeError("Client not initialized")
        
        return await self.w3.eth.get_transaction(tx_hash)
    
    async def get_block(self, block_number: int) -> Dict[str, Any]:
        """Get block details"""
        if not self.initialized:
            raise RuntimeError("Client not initialized")
        
        return await self.w3.eth.get_block(block_number)
    
    async def shutdown(self):
        """Cleanup resources"""
        self.initialized = False
        logger.info("Ethereum client shutdown")


# Global instance
ethereum_client = EthereumClient()
