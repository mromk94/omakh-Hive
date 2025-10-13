"""
Modern Solana RPC Client - Compatible with httpx>=0.28.1

This implementation uses httpx directly for RPC calls instead of the legacy
solana package, making it compatible with google-genai and other modern packages.

Implements:
- JSON-RPC 2.0 client for Solana
- Async/await support
- Transaction submission
- Account queries
- Token operations
- Full compatibility with solders types
"""
import asyncio
from typing import Dict, Any, Optional, List, Union
from decimal import Decimal
import structlog
import httpx
import base64
import json

logger = structlog.get_logger(__name__)

# Import solders for types (Rust-based, no dependency conflicts)
try:
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.transaction import Transaction
    from solders.system_program import transfer, TransferParams
    from solders.compute_budget import set_compute_unit_price, set_compute_unit_limit
    from solders.hash import Hash
    SOLDERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Solders not available: {e}. Install with: pip install solders>=0.20.0")
    SOLDERS_AVAILABLE = False
    Keypair = None
    Pubkey = None
    Transaction = None


class SolanaRPCClient:
    """
    Modern Solana RPC client using httpx directly
    Compatible with httpx>=0.28.1
    """
    
    def __init__(self, endpoint: str = "https://api.mainnet-beta.solana.com"):
        """Initialize Solana RPC client"""
        self.endpoint = endpoint
        self.client = httpx.AsyncClient(timeout=30.0)
        self._request_id = 0
        
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
        
    async def _call_rpc(self, method: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        Make a JSON-RPC 2.0 call to Solana
        
        Args:
            method: RPC method name
            params: Method parameters
            
        Returns:
            RPC response result
        """
        self._request_id += 1
        
        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or []
        }
        
        try:
            response = await self.client.post(self.endpoint, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            if "error" in data:
                logger.error(f"Solana RPC error: {data['error']}")
                raise Exception(f"RPC Error: {data['error']}")
                
            return data.get("result", {})
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Solana RPC: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling Solana RPC method {method}: {e}")
            raise
    
    async def get_balance(self, pubkey: Union[str, Pubkey]) -> int:
        """
        Get SOL balance for an account (in lamports)
        
        Args:
            pubkey: Account public key
            
        Returns:
            Balance in lamports (1 SOL = 1,000,000,000 lamports)
        """
        if isinstance(pubkey, Pubkey):
            pubkey = str(pubkey)
            
        result = await self._call_rpc("getBalance", [pubkey])
        return result.get("value", 0)
    
    async def get_account_info(self, pubkey: Union[str, Pubkey]) -> Optional[Dict[str, Any]]:
        """
        Get account information
        
        Args:
            pubkey: Account public key
            
        Returns:
            Account info dict or None if account doesn't exist
        """
        if isinstance(pubkey, Pubkey):
            pubkey = str(pubkey)
            
        result = await self._call_rpc("getAccountInfo", [
            pubkey,
            {"encoding": "jsonParsed"}
        ])
        
        return result.get("value")
    
    async def get_token_account_balance(self, pubkey: Union[str, Pubkey]) -> Dict[str, Any]:
        """
        Get token account balance
        
        Args:
            pubkey: Token account public key
            
        Returns:
            Token balance info with amount and decimals
        """
        if isinstance(pubkey, Pubkey):
            pubkey = str(pubkey)
            
        result = await self._call_rpc("getTokenAccountBalance", [pubkey])
        return result.get("value", {})
    
    async def get_token_accounts_by_owner(
        self,
        owner: Union[str, Pubkey],
        mint: Optional[Union[str, Pubkey]] = None,
        program_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all token accounts owned by an address
        
        Args:
            owner: Owner public key
            mint: Optional mint address to filter by
            program_id: Optional token program ID (defaults to SPL Token)
            
        Returns:
            List of token accounts
        """
        if isinstance(owner, Pubkey):
            owner = str(owner)
        if isinstance(mint, Pubkey):
            mint = str(mint)
            
        if mint:
            filter_param = {"mint": mint}
        elif program_id:
            filter_param = {"programId": program_id}
        else:
            filter_param = {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}
        
        result = await self._call_rpc("getTokenAccountsByOwner", [
            owner,
            filter_param,
            {"encoding": "jsonParsed"}
        ])
        
        return result.get("value", [])
    
    async def get_latest_blockhash(self) -> str:
        """
        Get the latest blockhash
        
        Returns:
            Latest blockhash as string
        """
        result = await self._call_rpc("getLatestBlockhash", [
            {"commitment": "finalized"}
        ])
        return result.get("value", {}).get("blockhash", "")
    
    async def send_transaction(
        self,
        transaction: Union[Transaction, str],
        skip_preflight: bool = False,
        max_retries: int = 3
    ) -> str:
        """
        Send a transaction to Solana
        
        Args:
            transaction: Signed transaction (Transaction object or base64 string)
            skip_preflight: Skip preflight transaction checks
            max_retries: Number of retry attempts
            
        Returns:
            Transaction signature
        """
        # Serialize transaction to base64
        if hasattr(transaction, 'serialize'):
            tx_bytes = transaction.serialize()
            tx_b64 = base64.b64encode(tx_bytes).decode('utf-8')
        else:
            tx_b64 = transaction
        
        result = await self._call_rpc("sendTransaction", [
            tx_b64,
            {
                "skipPreflight": skip_preflight,
                "maxRetries": max_retries,
                "encoding": "base64"
            }
        ])
        
        return result
    
    async def confirm_transaction(
        self,
        signature: str,
        commitment: str = "finalized"
    ) -> Dict[str, Any]:
        """
        Confirm a transaction
        
        Args:
            signature: Transaction signature
            commitment: Commitment level (finalized, confirmed, processed)
            
        Returns:
            Transaction status
        """
        result = await self._call_rpc("getSignatureStatuses", [[signature]])
        return result.get("value", [{}])[0]
    
    async def get_transaction(
        self,
        signature: str,
        max_supported_transaction_version: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Get transaction details
        
        Args:
            signature: Transaction signature
            max_supported_transaction_version: Max transaction version to support
            
        Returns:
            Transaction details or None
        """
        result = await self._call_rpc("getTransaction", [
            signature,
            {
                "encoding": "jsonParsed",
                "maxSupportedTransactionVersion": max_supported_transaction_version
            }
        ])
        
        return result
    
    async def get_slot(self) -> int:
        """Get current slot"""
        return await self._call_rpc("getSlot")
    
    async def get_block_height(self) -> int:
        """Get current block height"""
        return await self._call_rpc("getBlockHeight")
    
    async def get_version(self) -> Dict[str, Any]:
        """Get Solana version"""
        return await self._call_rpc("getVersion")
    
    async def is_connected(self) -> bool:
        """Check if connected to Solana RPC"""
        try:
            await self.get_version()
            return True
        except Exception:
            return False


# Compatibility wrapper for existing code
class AsyncClient(SolanaRPCClient):
    """
    Compatibility wrapper that mimics the old solana.rpc.async_api.AsyncClient
    """
    
    def __init__(self, endpoint: str = "https://api.mainnet-beta.solana.com", commitment: str = "confirmed"):
        super().__init__(endpoint)
        self.commitment = commitment
        logger.info(f"✅ Modern Solana RPC client initialized: {endpoint}")


# Export for compatibility
__all__ = [
    'SolanaRPCClient',
    'AsyncClient',
    'Keypair',
    'Pubkey',
    'Transaction',
    'SOLDERS_AVAILABLE'
]
